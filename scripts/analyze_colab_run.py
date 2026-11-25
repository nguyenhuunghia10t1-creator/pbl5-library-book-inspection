"""Reproducible analysis of Colab YOLO11n training artifacts and Damaged Books split statistics."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import struct
from typing import Any

try:
    import cv2  # type: ignore
except ImportError:
    cv2 = None


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACTS = (
    ROOT
    / "data"
    / "local"
    / "damaged_books_v1"
    / "colab-results"
    / "20261111T132200647414Z-artifacts"
)
DEFAULT_SPLIT_ROOT = ROOT / "data" / "local" / "damaged_books_v1" / "split-reviewed-v1"
EXPECTED_CLASSES = ["Barcode", "Notch", "Ripped", "Spot", "Wornout"]
AUDIT_20_CANDIDATES = [
    ("val", "train__IMG_1174_jpg.rf.150e452512bc5b0270247d17e32764e1"),
    ("val", "train__IMG_1359_jpg.rf.21b7d1f92a68815a84681fa4f0b82e2b"),
    ("val", "train__IMG_1446_jpg.rf.7c5e4f5a6a8d4afd8fdf84d098dea71e"),
    ("val", "train__IMG_1201_jpg.rf.222bf0fbb2b3e9da5bb50d95b71416d7"),
    ("val", "train__IMG_1129_jpg.rf.2c673a20905717fed0cf55f4c14fd371"),
    ("val", "train__IMG_1736_jpg.rf.d422877808581b2810764b2ba6d0053e"),
    ("val", "train__IMG_1330_jpg.rf.56bd3678a78279742ce541f7530b0c16"),
    ("val", "test__IMG_7_jpg.rf.b0eda460f02c08b90d5530fafd1d8fe0"),
    ("val", "train__IMG_1316_jpg.rf.faff4976751925a381bcd15b93a6342c"),
    ("val", "train__IMG_128_jpg.rf.e8f2e585c235d04383d46d45089b203e"),
    ("val", "train__IMG_1666_jpg.rf.870f66f26b2a08772ee56261e4fd2b8f"),
    ("val", "train__IMG_1122_jpg.rf.1d6cdbb6339ffde5cd835aeffca1ff07"),
    ("train", "train__IMG_1654_jpg.rf.44c01b9543050b1d6f37194005a3743d"),
    ("train", "train__IMG_1081_jpg.rf.f8a5c130159a65ab4198e96038593125"),
    ("train", "train__IMG_1118_jpg.rf.c43d7c0edde6436aa66e3e1c21d27414"),
    ("train", "train__IMG_1102_jpg.rf.b19e8d2ce131dbfe3f424409da4ea7e6"),
    ("train", "train__IMG_1474_jpg.rf.d0452b6eee2b416445b3dbb131c22be6"),
    ("train", "train__IMG_1634_jpg.rf.2089ffa600282ed7ddfa0de71454a74b"),
    ("train", "train__IMG_204_jpg.rf.2876d2153d9ae9fd2ab452f9f8941fa1"),
    ("train", "train__IMG_1078_jpg.rf.ad6d792160e893cba0b959eddb89616f"),
]


def sha256_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return round(ordered[0], 6)
    idx = (p / 100.0) * (len(ordered) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    frac = idx - lo
    return round(ordered[lo] + frac * (ordered[hi] - ordered[lo]), 6)


def summary_stats(values: list[float], digits: int = 4) -> dict[str, float]:
    if not values:
        return {}
    return {
        "min": round(percentile(values, 0), digits),
        "p10": round(percentile(values, 10), digits),
        "p25": round(percentile(values, 25), digits),
        "p50": round(percentile(values, 50), digits),
        "p75": round(percentile(values, 75), digits),
        "p90": round(percentile(values, 90), digits),
        "max": round(percentile(values, 100), digits),
        "mean": round(sum(values) / len(values), digits),
    }


def read_jpeg_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if len(data) < 4 or data[0:2] != b"\xff\xd8":
        raise ValueError(f"Unsupported JPEG file: {path}")
    pos = 2
    sof_markers = {
        0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
        0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
    }
    while pos < len(data):
        while pos < len(data) and data[pos] == 0xFF:
            pos += 1
        if pos >= len(data):
            break
        marker = data[pos]
        pos += 1
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            continue
        if pos + 2 > len(data):
            break
        segment_len = struct.unpack(">H", data[pos:pos + 2])[0]
        if marker in sof_markers:
            height, width = struct.unpack(">HH", data[pos + 3:pos + 7])
            return width, height
        pos += segment_len
    raise ValueError(f"Could not parse JPEG dimensions: {path}")


def compute_dhash(path: Path) -> int | None:
    if cv2 is None:
        return None
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    resized = cv2.resize(img, (9, 8), interpolation=cv2.INTER_AREA)
    value = 0
    bit = 0
    for y in range(8):
        for x in range(8):
            if int(resized[y, x]) > int(resized[y, x + 1]):
                value |= 1 << bit
            bit += 1
    return value


def hamming_distance(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {}
    current_list_key: str | None = None
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- ") and current_list_key is not None:
            result.setdefault(current_list_key, []).append(line[2:].strip().strip("\"'"))
            continue
        current_list_key = None
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        if not val:
            current_list_key = key
            result[key] = []
        elif val.startswith("[") and val.endswith("]"):
            items = [item.strip().strip("\"'") for item in val[1:-1].split(",") if item.strip()]
            result[key] = items
        elif val.lower() in ("true", "false"):
            result[key] = val.lower() == "true"
        elif val.lower() in ("null", "none"):
            result[key] = None
        else:
            try:
                result[key] = int(val)
            except ValueError:
                try:
                    result[key] = float(val)
                except ValueError:
                    result[key] = val.strip("\"'")
    return result


def analyze_training_artifacts(artifacts_dir: Path) -> dict[str, Any]:
    env = json.loads((artifacts_dir / "environment.json").read_text(encoding="utf-8"))
    init_weights = json.loads((artifacts_dir / "initial-weights.json").read_text(encoding="utf-8"))
    metadata = json.loads((artifacts_dir / "model-metadata.json").read_text(encoding="utf-8"))
    req_cfg = json.loads((artifacts_dir / "requested-config.json").read_text(encoding="utf-8"))
    train_status = json.loads((artifacts_dir / "training-status.json").read_text(encoding="utf-8"))
    val_metrics = json.loads((artifacts_dir / "validation-metrics.json").read_text(encoding="utf-8"))
    args_yaml = parse_simple_yaml(artifacts_dir / "train" / "args.yaml")

    frozen_pkgs: dict[str, str] = {}
    for line in (artifacts_dir / "requirements-frozen.txt").read_text(encoding="utf-8").splitlines():
        if "==" in line:
            pkg, ver = line.split("==", 1)
            frozen_pkgs[pkg.strip().lower()] = ver.strip()

    rows: list[dict[str, Any]] = []
    with (artifacts_dir / "train" / "results.csv").open("r", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        for row in reader:
            parsed: dict[str, Any] = {}
            for k, v in row.items():
                k_clean = k.strip()
                v_clean = (v or "").strip()
                if k_clean == "epoch":
                    parsed[k_clean] = int(v_clean)
                else:
                    parsed[k_clean] = float(v_clean)
            rows.append(parsed)

    nan_val_epochs = [
        r["epoch"]
        for r in rows
        if math.isnan(r["val/box_loss"]) or math.isnan(r["val/cls_loss"]) or math.isnan(r["val/dfl_loss"])
    ]
    finite_val_rows = [r for r in rows if r["epoch"] not in nan_val_epochs]
    peak_map50_row = max(rows, key=lambda r: r["metrics/mAP50(B)"])
    peak_map50_95_row = max(rows, key=lambda r: r["metrics/mAP50-95(B)"])
    min_val_box_row = min(finite_val_rows, key=lambda r: r["val/box_loss"])
    min_val_cls_row = min(finite_val_rows, key=lambda r: r["val/cls_loss"])
    max_val_cls_row = max(finite_val_rows, key=lambda r: r["val/cls_loss"])
    max_recall_row = max(rows, key=lambda r: r["metrics/recall(B)"])

    return {
        "environment": env,
        "key_frozen_packages": {
            k: frozen_pkgs.get(k)
            for k in (
                "ultralytics",
                "torch",
                "torchvision",
                "opencv-python",
                "numpy",
                "pillow",
                "scipy",
                "matplotlib",
                "pyyaml",
            )
        },
        "initial_weights": init_weights,
        "model_metadata": metadata,
        "requested_config": req_cfg,
        "training_status": train_status,
        "effective_args": {
            k: args_yaml.get(k)
            for k in (
                "model", "epochs", "patience", "batch", "imgsz", "seed", "deterministic",
                "optimizer", "lr0", "lrf", "cos_lr", "momentum", "weight_decay",
                "warmup_epochs", "warmup_momentum", "warmup_bias_lr", "amp",
                "box", "cls", "dfl", "mosaic", "close_mosaic", "mixup", "cutmix",
                "copy_paste", "auto_augment", "erasing", "hsv_h", "hsv_s", "hsv_v",
                "degrees", "translate", "scale", "shear", "perspective", "flipud", "fliplr",
                "rect", "single_cls", "freeze", "dropout", "multi_scale", "conf", "iou", "max_det",
            )
        },
        "missing_or_unrecorded_in_artifacts": [
            "experiment-summary.csv, team_member, experiment (run created before team-preset metadata update)",
            "Per-epoch per-class AP/Precision/Recall (results.csv only logs macro averages across 5 classes)",
            "Raw PR/F1 curve coordinate arrays per class (saved only as PNG plots; thresholds=null)",
        ],
        "validation_metrics": val_metrics,
        "epoch_curve_summary": {
            "total_epochs_run": len(rows),
            "total_time_seconds": round(rows[-1]["time"], 2),
            "nan_val_loss_epochs": nan_val_epochs,
            "epoch_9_val_cls_loss_spike": round(max_val_cls_row["val/cls_loss"], 3),
            "peak_mAP50": {
                "epoch": peak_map50_row["epoch"],
                "mAP50": round(peak_map50_row["metrics/mAP50(B)"], 5),
                "mAP50_95": round(peak_map50_row["metrics/mAP50-95(B)"], 5),
                "precision": round(peak_map50_row["metrics/precision(B)"], 5),
                "recall": round(peak_map50_row["metrics/recall(B)"], 5),
            },
            "peak_mAP50_95_fitness_best_pt": {
                "epoch": peak_map50_95_row["epoch"],
                "mAP50": round(peak_map50_95_row["metrics/mAP50(B)"], 5),
                "mAP50_95": round(peak_map50_95_row["metrics/mAP50-95(B)"], 5),
                "precision": round(peak_map50_95_row["metrics/precision(B)"], 5),
                "recall": round(peak_map50_95_row["metrics/recall(B)"], 5),
            },
            "peak_recall": {
                "epoch": max_recall_row["epoch"],
                "recall": round(max_recall_row["metrics/recall(B)"], 5),
                "precision": round(max_recall_row["metrics/precision(B)"], 5),
            },
            "min_val_box_loss": {
                "epoch": min_val_box_row["epoch"],
                "val_box_loss": round(min_val_box_row["val/box_loss"], 5),
            },
            "min_val_cls_loss": {
                "epoch": min_val_cls_row["epoch"],
                "val_cls_loss": round(min_val_cls_row["val/cls_loss"], 5),
            },
            "epoch_100_final": {
                "train_box_loss": round(rows[-1]["train/box_loss"], 5),
                "train_cls_loss": round(rows[-1]["train/cls_loss"], 5),
                "train_dfl_loss": round(rows[-1]["train/dfl_loss"], 5),
                "val_box_loss": round(rows[-1]["val/box_loss"], 5),
                "val_cls_loss": round(rows[-1]["val/cls_loss"], 5),
                "val_dfl_loss": round(rows[-1]["val/dfl_loss"], 5),
                "mAP50": round(rows[-1]["metrics/mAP50(B)"], 5),
                "mAP50_95": round(rows[-1]["metrics/mAP50-95(B)"], 5),
            },
        },
    }


def analyze_dataset_split(split_root: Path, imgsz: int = 640) -> dict[str, Any]:
    data_yaml = parse_simple_yaml(split_root / "data.yaml")
    manifest = json.loads((split_root / "split_manifest.json").read_text(encoding="utf-8"))
    yaml_names = data_yaml.get("names", [])
    classes_match = (
        data_yaml.get("nc") == 5
        and yaml_names == EXPECTED_CLASSES
        and manifest.get("classes") == EXPECTED_CLASSES
    )

    group_lookup: dict[str, str] = {}
    for part in ("train", "val", "test"):
        for rec in manifest["assignment"][part]:
            group_lookup[rec["image_id"]] = rec["group_id"]

    split_reports: dict[str, Any] = {}
    image_meta_by_split: dict[str, list[dict[str, Any]]] = {"train": [], "val": []}

    for split in ("train", "val"):
        img_dir = split_root / split / "images"
        lbl_dir = split_root / split / "labels"
        images = sorted(img_dir.iterdir(), key=lambda p: p.name)
        labels = sorted(lbl_dir.iterdir(), key=lambda p: p.name)

        size_counter: Counter[str] = Counter()
        for img_path in images:
            w, h = read_jpeg_size(img_path)
            size_counter[f"{w}x{h}"] += 1
            image_meta_by_split[split].append(
                {
                    "id": img_path.stem,
                    "group_id": group_lookup.get(img_path.stem, ""),
                    "sha256": sha256_file(img_path),
                    "dhash": compute_dhash(img_path),
                    "width": w,
                    "height": h,
                }
            )

        empty_labels: list[str] = []
        barcode_only_images: list[str] = []
        class_img_counts = {name: 0 for name in EXPECTED_CLASSES}
        class_inst_counts = {name: 0 for name in EXPECTED_CLASSES}
        boxes_by_class: dict[str, list[dict[str, float]]] = {name: [] for name in EXPECTED_CLASSES}

        coco_small = {name: 0 for name in EXPECTED_CLASSES}
        coco_medium = {name: 0 for name in EXPECTED_CLASSES}
        coco_large = {name: 0 for name in EXPECTED_CLASSES}

        out_of_bounds: list[str] = []
        invalid_class_ids: list[str] = []
        tiny_boxes: list[dict[str, Any]] = []
        extreme_aspect_boxes: list[dict[str, Any]] = []
        duplicate_boxes: list[dict[str, Any]] = []
        high_overlap_pairs: list[dict[str, Any]] = []

        group_box_counts: Counter[str] = Counter()
        group_img_counts: Counter[str] = Counter()

        for lbl_path in labels:
            image_id = lbl_path.stem
            gid = group_lookup.get(image_id, "")
            group_img_counts[gid] += 1
            raw_lines = [ln.strip() for ln in lbl_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
            if not raw_lines:
                empty_labels.append(image_id)
                continue

            present_classes: set[int] = set()
            img_boxes: list[dict[str, Any]] = []
            for line_idx, line in enumerate(raw_lines):
                parts = line.split()
                c_raw = float(parts[0])
                x, y, w, h = (float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4]))
                if not c_raw.is_integer() or not (0 <= int(c_raw) < 5):
                    invalid_class_ids.append(f"{lbl_path.name}:{line_idx} ({parts[0]})")
                    continue
                c = int(c_raw)
                cname = EXPECTED_CLASSES[c]
                present_classes.add(c)
                class_inst_counts[cname] += 1
                group_box_counts[gid] += 1

                area = w * h
                px_w = w * imgsz
                px_h = h * imgsz
                px_area = px_w * px_h
                px_side = math.sqrt(px_area)
                aspect = max(w / h, h / w) if (w > 0 and h > 0) else 999999.0

                if px_area < 32.0 * 32.0:
                    coco_small[cname] += 1
                elif px_area < 96.0 * 96.0:
                    coco_medium[cname] += 1
                else:
                    coco_large[cname] += 1

                x1, y1, x2, y2 = x - w / 2.0, y - h / 2.0, x + w / 2.0, y + h / 2.0
                if x1 < -1e-6 or y1 < -1e-6 or x2 > 1.000001 or y2 > 1.000001 or w <= 0 or h <= 0:
                    out_of_bounds.append(f"{image_id}:{line_idx}")
                if px_area < 16.0 or px_w < 4.0 or px_h < 4.0:
                    tiny_boxes.append(
                        {"image_id": image_id, "line": line_idx, "class": cname, "px_w": px_w, "px_h": px_h}
                    )
                if aspect > 10.0:
                    extreme_aspect_boxes.append(
                        {
                            "image_id": image_id,
                            "line": line_idx,
                            "class": cname,
                            "px_w": round(px_w, 1),
                            "px_h": round(px_h, 1),
                            "aspect": round(aspect, 2),
                        }
                    )

                box_rec = {
                    "line": line_idx,
                    "c": c,
                    "cname": cname,
                    "w": w,
                    "h": h,
                    "area": area,
                    "px_w": px_w,
                    "px_h": px_h,
                    "px_area": px_area,
                    "px_side": px_side,
                    "aspect": aspect,
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                }
                boxes_by_class[cname].append(box_rec)
                img_boxes.append(box_rec)

            for c in present_classes:
                class_img_counts[EXPECTED_CLASSES[c]] += 1
            if not any(c > 0 for c in present_classes):
                barcode_only_images.append(image_id)

            for i in range(len(img_boxes)):
                for j in range(i + 1, len(img_boxes)):
                    b1, b2 = img_boxes[i], img_boxes[j]
                    ix1, iy1 = max(b1["x1"], b2["x1"]), max(b1["y1"], b2["y1"])
                    ix2, iy2 = min(b1["x2"], b2["x2"]), min(b1["y2"], b2["y2"])
                    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
                    inter = iw * ih
                    if inter <= 0:
                        continue
                    union = b1["area"] + b2["area"] - inter
                    iou = inter / union if union > 0 else 0.0
                    ioa = inter / min(b1["area"], b2["area"])
                    if iou >= 0.95 and b1["c"] == b2["c"]:
                        duplicate_boxes.append(
                            {"image_id": image_id, "class": b1["cname"], "l1": b1["line"], "l2": b2["line"], "iou": round(iou, 4)}
                        )
                    elif iou >= 0.25 or ioa >= 0.50:
                        high_overlap_pairs.append(
                            {
                                "image_id": image_id,
                                "l1": b1["line"],
                                "c1": b1["cname"],
                                "l2": b2["line"],
                                "c2": b2["cname"],
                                "iou": round(iou, 4),
                                "ioa": round(ioa, 4),
                            }
                        )

        box_stats_per_class: dict[str, Any] = {}
        for cname in EXPECTED_CLASSES:
            blist = boxes_by_class[cname]
            box_stats_per_class[cname] = {
                "count": len(blist),
                "norm_w": summary_stats([b["w"] for b in blist], 4),
                "norm_h": summary_stats([b["h"] for b in blist], 4),
                "norm_area": summary_stats([b["area"] for b in blist], 6),
                "px_w": summary_stats([b["px_w"] for b in blist], 1),
                "px_h": summary_stats([b["px_h"] for b in blist], 1),
                "px_area": summary_stats([b["px_area"] for b in blist], 1),
                "px_sqrt_area": summary_stats([b["px_side"] for b in blist], 1),
                "aspect_ratio": summary_stats([b["aspect"] for b in blist], 2),
                "coco_scale_counts": {
                    "small_lt_32x32": coco_small[cname],
                    "medium_32_to_96": coco_medium[cname],
                    "large_ge_96x96": coco_large[cname],
                    "small_pct": round(100.0 * coco_small[cname] / len(blist), 2) if blist else 0.0,
                },
            }

        top_groups = [
            {"group_id": gid, "images": group_img_counts[gid], "boxes": boxes_cnt}
            for gid, boxes_cnt in group_box_counts.most_common(5)
        ]
        top3 = top_groups[:3]
        total_inst = sum(class_inst_counts.values())
        extreme_by_class = Counter(b["class"] for b in extreme_aspect_boxes)

        split_reports[split] = {
            "images": len(images),
            "groups": len(set(group_img_counts)),
            "image_resolutions": dict(size_counter),
            "empty_label_images_count": len(empty_labels),
            "empty_label_images": empty_labels,
            "barcode_only_images_count": len(barcode_only_images),
            "barcode_only_images": barcode_only_images,
            "defect_free_images_total": len(empty_labels) + len(barcode_only_images),
            "class_image_counts": class_img_counts,
            "class_instance_counts": class_inst_counts,
            "total_instances": total_inst,
            "top_groups_by_boxes": top_groups,
            "top_3_groups_concentration": {
                "groups": [g["group_id"] for g in top3],
                "images": sum(g["images"] for g in top3),
                "total_split_images": len(images),
                "boxes": sum(g["boxes"] for g in top3),
                "total_split_boxes": total_inst,
                "box_share_pct": round(100.0 * sum(g["boxes"] for g in top3) / total_inst, 2) if total_inst else 0.0,
            },
            "box_stats": box_stats_per_class,
            "anomalies": {
                "invalid_class_id_count": len(invalid_class_ids),
                "out_of_bounds_count": len(out_of_bounds),
                "tiny_area_lt_16px2_or_4px_count": len(tiny_boxes),
                "extreme_aspect_gt_10_count": len(extreme_aspect_boxes),
                "extreme_aspect_gt_10_by_class": {
                    cname: extreme_by_class.get(cname, 0) for cname in EXPECTED_CLASSES
                },
                "exact_duplicate_boxes_iou_ge_095_count": len(duplicate_boxes),
                "high_overlap_iou_ge_025_or_ioa_ge_050_count": len(high_overlap_pairs),
                "high_overlap_pairs": high_overlap_pairs,
                "extreme_aspect_samples": extreme_aspect_boxes[:12],
            },
        }

    train_groups = {m["group_id"] for m in image_meta_by_split["train"]}
    val_groups = {m["group_id"] for m in image_meta_by_split["val"]}
    train_shas = {m["sha256"] for m in image_meta_by_split["train"]}
    val_shas = {m["sha256"] for m in image_meta_by_split["val"]}

    near_duplicates: list[dict[str, Any]] = []
    for t_meta in image_meta_by_split["train"]:
        for v_meta in image_meta_by_split["val"]:
            if t_meta["dhash"] is not None and v_meta["dhash"] is not None:
                dist = hamming_distance(t_meta["dhash"], v_meta["dhash"])
                if dist <= 10:
                    near_duplicates.append(
                        {
                            "train_id": t_meta["id"],
                            "train_group": t_meta["group_id"],
                            "val_id": v_meta["id"],
                            "val_group": v_meta["group_id"],
                            "dhash_hamming": dist,
                        }
                    )
    near_duplicates.sort(key=lambda item: item["dhash_hamming"])

    manifest_split_lookup: dict[tuple[str, str], str] = {}
    for split_name in ("train", "val"):
        for rec in manifest["assignment"][split_name]:
            manifest_split_lookup[(split_name, rec["image_id"])] = rec["group_id"]

    audit_20_records: list[dict[str, Any]] = []
    for idx, (split_name, image_id) in enumerate(AUDIT_20_CANDIDATES, 1):
        if (split_name, image_id) not in manifest_split_lookup:
            raise ValueError(f"Audit candidate not in {split_name} manifest: {image_id}")
        gid = manifest_split_lookup[(split_name, image_id)]
        img_rel = f"{split_name}/images/{image_id}.jpg"
        lbl_rel = f"{split_name}/labels/{image_id}.txt"
        img_path = split_root / img_rel
        lbl_path = split_root / lbl_rel
        if not img_path.exists() or not lbl_path.exists():
            raise FileNotFoundError(f"Missing audit file: {img_rel} or {lbl_rel}")
        raw_lines = [ln.strip() for ln in lbl_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        counts = Counter(EXPECTED_CLASSES[int(float(ln.split()[0]))] for ln in raw_lines)
        audit_20_records.append(
            {
                "index": idx,
                "split": split_name,
                "image_id": image_id,
                "group_id": gid,
                "image_path": img_rel,
                "label_path": lbl_rel,
                "total_boxes": len(raw_lines),
                "class_counts": {cname: counts.get(cname, 0) for cname in EXPECTED_CLASSES},
            }
        )

    return {
        "data_yaml": data_yaml,
        "class_ids_match_data_yaml_and_manifest": classes_match,
        "splits": split_reports,
        "cross_split_train_val": {
            "group_overlap_count": len(train_groups & val_groups),
            "exact_sha256_overlap_count": len(train_shas & val_shas),
            "dhash_enabled": cv2 is not None,
            "opencv_version": getattr(cv2, "__version__", None) if cv2 is not None else None,
            "near_duplicate_dhash_le_10_count": len(near_duplicates),
            "near_duplicate_dhash_le_10": near_duplicates,
        },
        "audit_20_manifest_verified": audit_20_records,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, default=DEFAULT_ARTIFACTS, help="Extracted Colab artifacts directory")
    parser.add_argument("--split-root", type=Path, default=DEFAULT_SPLIT_ROOT, help="Reviewed dataset split root")
    parser.add_argument("--output-json", type=Path, default=None, help="Optional path to save JSON report")
    args = parser.parse_args(argv)

    report = {
        "training_analysis": analyze_training_artifacts(args.artifacts.resolve()),
        "dataset_analysis": analyze_dataset_split(args.split_root.resolve()),
    }
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text, encoding="utf-8")
        print(f"Saved JSON analysis to: {args.output_json}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
