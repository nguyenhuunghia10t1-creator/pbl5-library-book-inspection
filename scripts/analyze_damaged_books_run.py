"""Audit exported YOLO artifacts and train/val labels without loading a model.

Requires numpy, opencv-python and PyYAML (use the separate AI environment).
All extracted artifacts and detailed output must be in a Git-ignored directory.
Test images/labels are never opened. Existing outputs are verified, not replaced.
"""

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import stat
import subprocess
import zipfile

import cv2
import numpy as np
import yaml


CLASSES = ["Barcode", "Notch", "Ripped", "Spot", "Wornout"]
ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def write_once(path, content):
    payload = content.encode("utf-8")
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError(f"Refusing to overwrite changed output: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(payload)


def json_text(value):
    return json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n"


def extract_verified(archive, destination):
    inventory = []
    with zipfile.ZipFile(archive) as zipped:
        for entry in zipped.infolist():
            target = (destination / entry.filename).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise ValueError(f"Unsafe ZIP path: {entry.filename}")
            if stat.S_ISLNK(entry.external_attr >> 16):
                raise ValueError(f"Symlink in ZIP: {entry.filename}")
            if entry.is_dir():
                continue
            payload = zipped.read(entry)  # Checks ZIP CRC before writing.
            digest = hashlib.sha256(payload).hexdigest()
            if target.exists():
                if sha(target) != digest:
                    raise ValueError(f"Existing extracted file differs: {target}")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as handle:
                    handle.write(payload)
            inventory.append({"path": entry.filename, "bytes": len(payload), "sha256": digest})
    return inventory


def quantiles(values):
    if not values:
        return None
    return dict(zip(["min", "p05", "p25", "p50", "p75", "p95", "max"],
                    map(float, np.quantile(values, [0, .05, .25, .5, .75, .95, 1]))))


def phash(gray):
    small = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA)
    low = cv2.dct(small.astype(np.float32))[:8, :8].flatten()[1:]
    return low > np.median(low)


def box_iou(a, b):
    def corners(row):
        _, x, y, w, h = row
        return x-w/2, y-h/2, x+w/2, y+h/2
    ax, ay, ar, ab = corners(a)
    bx, by, br, bb = corners(b)
    intersection = max(0, min(ar, br)-max(ax, bx))*max(0, min(ab, bb)-max(ay, by))
    union = a[3]*a[4]+b[3]*b[4]-intersection
    return intersection/union if union > 0 else 0


def audit_dataset(dataset, manifest, imgsz):
    stats, images, anomalies, file_hashes = {}, {}, [], {}
    for split in ("train", "val"):
        split_images = sorted((dataset / split / "images").glob("*"))
        split_labels = sorted((dataset / split / "labels").glob("*.txt"))
        expected = {r["image_id"] for r in manifest["assignment"][split]}
        assert {p.stem for p in split_images} == expected, f"{split}: manifest image mismatch"
        assert {p.stem for p in split_labels} == expected, f"{split}: label mismatch"
        boxes = {name: [] for name in CLASSES}
        image_counts = dict.fromkeys(CLASSES, 0)
        group_sets = {name: set() for name in CLASSES}
        groups = {r["image_id"]: r["group_id"] for r in manifest["assignment"][split]}
        empty, no_damage, shapes = [], [], set()
        images[split] = []
        for image_path in split_images:
            label_path = dataset / split / "labels" / (image_path.stem + ".txt")
            for path in (image_path, label_path):
                rel = path.relative_to(dataset).as_posix()
                file_hashes[rel] = sha(path)
                assert file_hashes[rel] == manifest["file_sha256"][rel], f"Hash mismatch: {rel}"
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Cannot decode {image_path}")
            height, width = image.shape[:2]
            shapes.add((width, height))
            gain = imgsz / max(width, height)
            images[split].append({"id": image_path.stem, "sha256": sha(image_path),
                                  "pixels_sha256": hashlib.sha256(image.tobytes()).hexdigest(),
                                  "phash": phash(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))})
            rows, seen = [], set()
            text = label_path.read_text(encoding="utf-8").strip()
            if not text:
                empty.append(image_path.stem)
            for number, line in enumerate(text.splitlines(), 1):
                values = list(map(float, line.split()))
                location = {"split": split, "image": image_path.stem, "line": number}
                if len(values) != 5 or not all(math.isfinite(v) for v in values):
                    anomalies.append({**location, "kind": "malformed"})
                    continue
                cls, x, y, w, h = values
                if cls != int(cls) or not 0 <= cls < len(CLASSES):
                    anomalies.append({**location, "kind": "class_id"})
                    continue
                if w <= 0 or h <= 0 or min(x-w/2, y-h/2) < -1e-6 or max(x+w/2, y+h/2) > 1+1e-6:
                    anomalies.append({**location, "kind": "geometry", "values": values})
                if w*h <= 1e-6 or w*width*gain*h*height*gain < 1:
                    anomalies.append({**location, "kind": "near_zero_area", "values": values})
                if tuple(values) in seen:
                    anomalies.append({**location, "kind": "duplicate_row"})
                for previous in rows:
                    overlap = box_iou(values, previous)
                    if overlap >= .9 and tuple(values) != tuple(previous):
                        anomalies.append({**location, "kind": "high_iou", "iou": overlap,
                                          "class_pair": [int(cls), int(previous[0])]})
                seen.add(tuple(values))
                rows.append(values)
                boxes[CLASSES[int(cls)]].append({"w_norm": w, "h_norm": h, "area_norm": w*h,
                    "w_px": w*width*gain, "h_px": h*height*gain,
                    "short_px": min(w*width*gain, h*height*gain),
                    "area_px": w*width*gain*h*height*gain})
            present = {int(row[0]) for row in rows}
            if not present.intersection({1, 2, 3, 4}):
                no_damage.append(image_path.stem)
            for cls in present:
                image_counts[CLASSES[cls]] += 1
                group_sets[CLASSES[cls]].add(groups[image_path.stem])
        per_class = {}
        for name, rows in boxes.items():
            per_class[name] = {"images": image_counts[name], "groups": len(group_sets[name]),
                "instances": len(rows), "quantiles": {key: quantiles([r[key] for r in rows])
                    for key in ("w_norm", "h_norm", "area_norm", "w_px", "h_px", "short_px", "area_px")},
                "short_lt_8px": sum(r["short_px"] < 8 for r in rows),
                "short_lt_16px": sum(r["short_px"] < 16 for r in rows),
                "area_lt_32_squared_px": sum(r["area_px"] < 32**2 for r in rows)}
        stats[split] = {"images": len(split_images), "groups": len(set(groups.values())),
                        "image_shapes": sorted(shapes), "empty_labels": empty,
                        "no_damage_labels": no_damage, "per_class": per_class}
    pairs = []
    exact, pixels = [], []
    for train in images["train"]:
        for val in images["val"]:
            pair = {"train": train["id"], "val": val["id"]}
            if train["sha256"] == val["sha256"]:
                exact.append(pair)
            if train["pixels_sha256"] == val["pixels_sha256"]:
                pixels.append(pair)
            distance = int(np.count_nonzero(train["phash"] != val["phash"]))
            if distance <= 8:
                pairs.append({**pair, "phash_hamming_63": distance})
    train_groups = {r["group_id"] for r in manifest["assignment"]["train"]}
    val_groups = {r["group_id"] for r in manifest["assignment"]["val"]}
    leakage = {"group_overlap": sorted(train_groups & val_groups), "byte_duplicates": exact,
               "decoded_pixel_duplicates": pixels, "phash_candidates_le_8": pairs,
               "pairs_checked": len(images["train"])*len(images["val"]),
               "limitation": "pHash screens similar views only; no proof against different views of the same book"}
    return {"splits": stats, "anomalies": anomalies, "leakage": leakage,
            "train_val_file_hashes": file_hashes}


def curve_summary(path):
    rows = [{k.strip(): float(v) for k, v in r.items()} for r in csv.DictReader(io.StringIO(path.read_text()))]
    nonfinite = {key: [int(r["epoch"]) for r in rows if not math.isfinite(r[key])]
                 for key in rows[0] if any(not math.isfinite(r[key]) for r in rows)}
    windows = {}
    for lo, hi in ((1, 10), (11, 20), (41, 50), (61, 70), (71, 80), (81, 90), (91, 100)):
        sample = [r for r in rows if lo <= r["epoch"] <= hi]
        windows[f"{lo}-{hi}"] = {key: float(np.mean(finite)) if finite else None
            for key in rows[0] if key != "epoch"
            for finite in [[r[key] for r in sample if math.isfinite(r[key])]]}
    return {"epochs": len(rows), "nonfinite_epochs": nonfinite, "window_means": windows,
            "best_ap50_epoch": int(max(rows, key=lambda r: r["metrics/mAP50(B)"])["epoch"]),
            "best_ap50_95_epoch": int(max(rows, key=lambda r: r["metrics/mAP50-95(B)"])["epoch"]),
            "last_epoch": rows[-1]}


def tables_markdown(result):
    lines = ["# YOLO11n run 1: computed tables", "",
             "Generated by `scripts/analyze_damaged_books_run.py`; train/val only.", "",
             f"Artifacts SHA256: `{result['archive_sha256']}`.", "",
             "## Validation metrics", "", "P, R and AP values are percentages.", "",
             "| Class | P | R | AP50 | AP50-95 | Images | Instances | Groups |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for row in result["per_class_table"]:
        values = [row["class"]] + [f"{row[k]*100:.3f}" for k in
                  ("precision", "recall", "ap50", "ap50_95")]
        values += [str(row[k]) for k in ("images", "instances", "groups")]
        lines.append("| " + " | ".join(values) + " |")
    lines += ["", "## Dataset counts", "",
              "Empty = zero labels; no damage = zero class 1-4 labels (may contain Barcode).", "",
              "| Split | Images | Groups | Empty | No damage |",
              "|---|---:|---:|---:|---:|"]
    splits = result["dataset"]["splits"]
    for split, data in splits.items():
        lines.append(f"| {split} | {data['images']} | {data['groups']} | {len(data['empty_labels'])} | {len(data['no_damage_labels'])} |")
    lines += ["", "| Split | Class | Images | Groups | Boxes | Short <8px | Short <16px | Area <1024px2 |",
              "|---|---|---:|---:|---:|---:|---:|---:|"]
    for split, data in splits.items():
        for name, row in data["per_class"].items():
            values = [split, name] + [str(row[k]) for k in ("images", "groups", "instances",
                      "short_lt_8px", "short_lt_16px", "area_lt_32_squared_px")]
            lines.append("| " + " | ".join(values) + " |")
    for keys, title in [(("w_norm", "h_norm", "area_norm"), "Normalized box size"),
                        (("w_px", "h_px", "short_px", "area_px"), "Box size after letterbox at imgsz=640")]:
        lines += ["", "## " + title, "", "Each cell = P05 / P50 / P95. Width and height medians are independent.", "",
                  "| Split | Class | " + " | ".join(keys) + " |", "|---|---|" + "---:|"*len(keys)]
        for split, data in splits.items():
            for name, row in data["per_class"].items():
                values = [split, name] + [" / ".join(f"{row['quantiles'][key][p]:.5f}" for p in
                         ("p05", "p50", "p95")) for key in keys]
                lines.append("| " + " | ".join(values) + " |")
    lines += ["", "## Epoch window means", "", "AP values are percentages; loss excludes nonfinite values.", "",
              "| Epochs | AP50 | AP50-95 | Train box | Val box | Train cls | Val cls | Train dfl | Val dfl |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for window, row in result["curves"]["window_means"].items():
        values = [window] + [f"{row[k]*100:.3f}" for k in ("metrics/mAP50(B)", "metrics/mAP50-95(B)")]
        values += [f"{row[k]:.4f}" if row[k] is not None else "N/A" for k in
                   ("train/box_loss", "val/box_loss", "train/cls_loss", "val/cls_loss", "train/dfl_loss", "val/dfl_loss")]
        lines.append("| " + " | ".join(values) + " |")
    lines += ["", "Epochs 1-10 contain only ONE finite validation-loss sample (epoch 9).",
              "Local analysis.json includes all quantiles, anomalies, hashes and leakage-screen details.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tables", type=Path, help="Optional small Markdown table file in docs (never overwrite)")
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / "data" / "local"):
        parser.error("--output must be inside this repository's data/local")
    subprocess.run(["git", "-c", f"safe.directory={ROOT.as_posix()}", "check-ignore", "-v",
                    output.as_posix()], cwd=ROOT, check=True)
    archive_hash = sha(args.archive)
    artifacts = output / "artifacts"
    inventory = extract_verified(args.archive, artifacts)
    read_json = lambda name: json.loads((artifacts / name).read_text(encoding="utf-8"))
    config = yaml.safe_load((artifacts / "train/args.yaml").read_text())
    manifest = read_json("split_manifest.json")
    dataset_manifest = json.loads((args.dataset / "split_manifest.json").read_text())
    assert dataset_manifest == manifest, "Local and exported split manifests differ"
    dataset_yaml = yaml.safe_load((args.dataset / "data.yaml").read_text())
    train_yaml = yaml.safe_load((artifacts / "train-val.yaml").read_text())
    assert dataset_yaml["names"] == train_yaml["names"] == manifest["classes"] == CLASSES
    assert dataset_yaml["nc"] == train_yaml["nc"] == 5
    assert dataset_yaml["train"] == train_yaml["train"] == "train/images"
    assert dataset_yaml["val"] == train_yaml["val"] == "val/images"
    assert sha(args.dataset / "data.yaml") == manifest["file_sha256"]["data.yaml"]
    metadata = read_json("model-metadata.json")
    assert metadata["classes"] == CLASSES, "Model metadata class order mismatch"
    assert metadata["dataset_version"] == manifest["dataset_version"], "Dataset version mismatch"
    assert sha(artifacts / "train/weights/best.pt") == metadata["weights_sha256"]
    audit = audit_dataset(args.dataset, manifest, int(config["imgsz"]))
    metrics = read_json("validation-metrics.json")
    assert metrics["split"] == "val"
    table = [{"class": name, **metrics["per_class"][name],
              **{k: audit["splits"]["val"]["per_class"][name][k]
                 for k in ("images", "instances", "groups")}} for name in CLASSES]
    result = {"archive_sha256": archive_hash, "inventory": inventory,
              "environment": read_json("environment.json"), "config": config,
              "initial_weights": read_json("initial-weights.json"),
              "training_status": read_json("training-status.json"),
              "model_metadata": metadata, "validation_metrics": metrics,
              "per_class_table": table, "curves": curve_summary(artifacts / "train/results.csv"),
              "dataset": audit, "scope": "offline artifacts and train/val only; no inference or test evaluation"}
    assert sha(args.archive) == archive_hash, "Archive changed during audit"
    for rel, digest in audit["train_val_file_hashes"].items():
        assert sha(args.dataset / rel) == digest, f"Dataset changed during audit: {rel}"
    write_once(output / "analysis.json", json_text(result))
    write_once(output / "inventory.txt", "\n".join(f"{i['path']} ({i['bytes']} bytes)" for i in inventory)+"\n")
    write_once(output / "tables.md", tables_markdown(result))
    if args.tables:
        if not args.tables.resolve().is_relative_to(ROOT / "docs") or args.tables.suffix != ".md":
            parser.error("--tables must be a Markdown file in this repository's docs")
        write_once(args.tables, tables_markdown(result))
    print(json_text({"archive_sha256": archive_hash, "extracted_files": len(inventory),
                     "per_class": table, "curves": result["curves"],
                     "anomalies": audit["anomalies"], "leakage": audit["leakage"]}))


if __name__ == "__main__":
    main()
