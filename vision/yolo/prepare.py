"""Immutable-source five-class conversion and reviewed, group-separated splits."""
import argparse
import ast
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import random
import shutil
import zipfile
from . import CLASSES


ORIGINAL_CLASSES = ("Barcode", "Notch", "Ripped", "Spot", "Tag", "Wornout")
REVIEW_FIELDS = ("image_id", "group_id", "label_review", "negative_review")


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    if source == output or (source in output.parents and output.relative_to(source).parts[0] != "data"):
        raise ValueError("Output must be a separate local data directory")
    if output.exists():
        raise ValueError("Output already exists; use a new version, never overwrite reviewed data")
    config = (source / "data.yaml").read_text(encoding="utf-8-sig")
    source_names = next((line.split(":", 1)[1].strip() for line in config.splitlines() if line.startswith("names:")), "[]")
    if tuple(ast.literal_eval(source_names)) != ORIGINAL_CLASSES:
        raise ValueError("Unexpected source class definition")
    rows, stats, source_splits = [], Counter(), {}
    # Validate everything before writing anything.
    for split in ("train", "valid", "test"):
        if not all((source / split / kind).is_dir() for kind in ("images", "labels")):
            raise ValueError(f"Missing source split directories: {split}")
        images = sorted((source / split / "images").glob("*"))
        image_stems = [p.stem for p in images if p.suffix.lower() in (".jpg", ".jpeg", ".png")]
        if len(set(image_stems)) != len(image_stems):
            raise ValueError(f"Duplicate image stems in {split}")
        if set(image_stems) != {p.stem for p in (source / split / "labels").glob("*.txt")}:
            raise ValueError(f"Missing or orphan label in {split}")
        source_splits[split] = {"images": 0, "classes_after_conversion": Counter()}
        for image in images:
            if image.suffix.lower() not in (".jpg", ".jpeg", ".png"):
                continue
            label = source / split / "labels" / (image.stem + ".txt")
            lines = []
            for number, line in enumerate(label.read_text(encoding="utf-8-sig").splitlines(), 1):
                if not line.strip():
                    continue
                fields = line.split()
                if len(fields) != 5:
                    raise ValueError(f"Invalid label {label.name}:{number}")
                old = int(fields[0])
                coordinates = list(map(float, fields[1:]))
                if old not in range(6) or not all(0 <= v <= 1 for v in coordinates) or min(coordinates[2:]) <= 0:
                    raise ValueError(f"Invalid label coordinates {label.name}:{number}")
                if old == 4:
                    stats["removed_Tag"] += 1
                    continue
                new = 4 if old == 5 else old
                lines.append(str(new) + " " + " ".join(fields[1:]))
                stats[CLASSES[new]] += 1
                source_splits[split]["classes_after_conversion"][CLASSES[new]] += 1
            source_splits[split]["images"] += 1
            image_id = f"{split}__{image.stem}"
            no_damage = not any(int(line.split()[0]) != 0 for line in lines)
            rows.append({"image_id": image_id, "image_file": image_id + image.suffix.lower(),
                         "source_image": image.relative_to(source).as_posix(),
                         "source_label": label.relative_to(source).as_posix(),
                         "image_sha256": sha256(image), "source_label_sha256": sha256(label),
                         "labels": lines, "negative_candidate": no_damage})
    if not rows:
        raise ValueError("No source images")
    output.mkdir(parents=True)
    (output / "images").mkdir()
    (output / "labels").mkdir()
    for row in rows:
        shutil.copyfile(source / row["source_image"], output / "images" / row["image_file"])
        (output / "labels" / (row["image_id"] + ".txt")).write_text("\n".join(row["labels"]) + ("\n" if row["labels"] else ""), encoding="utf-8")
    review = output / "review.csv"
    with review.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=REVIEW_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({"image_id": row["image_id"], "group_id": "",
                             "label_review": "pending", "negative_review": "pending" if row["negative_candidate"] else "not_needed"})
    identity = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    archives = list(source.glob("Damaged Books*.zip"))
    manifest = {"schema_version": 1, "dataset_version": "damaged-books-v1-five-" + identity[:12],
                "classes": list(CLASSES), "license": "CC BY 4.0",
                "source": "https://universe.roboflow.com/atcom21-gmail-com/damaged-books/dataset/1",
                "archive_sha256": sha256(archives[0]) if len(archives) == 1 else None,
                "archive_file": archives[0].name if len(archives) == 1 else None,
                "source_metadata_sha256": {name: sha256(source / name) for name in
                    ("data.yaml", "README.dataset.txt", "README.roboflow.txt") if (source / name).exists()},
                "source_splits": source_splits,
                "id_mapping": {"0": 0, "1": 1, "2": 2, "3": 3, "4": None, "5": 4},
                "statistics": {"images": len(rows), "boxes": sum(len(r["labels"]) for r in rows),
                               "empty_labels": sum(not r["labels"] for r in rows),
                               "negative_candidates": sum(r["negative_candidate"] for r in rows), **stats},
                "split_ready": False, "records": rows}
    write_json(output / "manifest.json", manifest)
    for name in ("README.dataset.txt", "README.roboflow.txt"):
        if (source / name).exists():
            shutil.copyfile(source / name, output / name)
    return manifest


def reviewed_split(prepared, destination):
    prepared, destination = Path(prepared), Path(destination)
    if destination.exists():
        raise ValueError("Split output already exists; use a new version")
    manifest = json.loads((prepared / "manifest.json").read_text(encoding="utf-8"))
    with (prepared / "review.csv").open(encoding="utf-8-sig", newline="") as stream:
        reviews = list(csv.DictReader(stream))
    by_id = {r["image_id"]: r for r in manifest["records"]}
    if len(reviews) != len(by_id) or {r["image_id"] for r in reviews} != set(by_id):
        raise ValueError("Review must contain each image exactly once")
    groups, quarantined = defaultdict(list), []
    for review in reviews:
        row = by_id[review["image_id"]]
        if review["label_review"] not in ("approved", "pending", "rejected"):
            raise ValueError("Invalid label_review")
        if review["negative_review"] not in ("approved", "pending", "rejected", "not_needed"):
            raise ValueError("Invalid negative_review")
        accepted = review["label_review"] == "approved" and review["group_id"].strip()
        if row["negative_candidate"]:
            accepted = accepted and review["negative_review"] == "approved"
        if accepted:
            groups[review["group_id"].strip()].append(row)
        else:
            quarantined.append(row["image_id"])
    if len(groups) < 3:
        raise ValueError("Need reviewed book groups before splitting; unresolved images remain quarantined")
    # Reject changed images/labels and exact duplicates assigned to different groups.
    hash_groups = {}
    for group, records in groups.items():
        for row in records:
            if sha256(prepared / "images" / row["image_file"]) != row["image_sha256"]:
                raise ValueError("Prepared image checksum mismatch")
            expected = "\n".join(row["labels"]) + ("\n" if row["labels"] else "")
            if (prepared / "labels" / (row["image_id"] + ".txt")).read_text() != expected:
                raise ValueError("Prepared labels changed; create a new dataset version")
            previous = hash_groups.setdefault(row["image_sha256"], group)
            if previous != group:
                raise ValueError("Identical images assigned to different groups")
    rng = random.Random(42)
    total = sum(map(len, groups.values()))
    target = {"train": .70, "val": .15, "test": .15}
    best = None
    for _ in range(2000):
        keys = list(groups)
        rng.shuffle(keys)
        assignment = {name: [] for name in target}
        for group in keys:
            part = min(target, key=lambda name: (sum(len(groups[g]) for g in assignment[name]) / max(1, total)) / target[name])
            assignment[part].append(group)
        covers = {}
        for part, ids in assignment.items():
            covers[part] = {int(line.split()[0]) for g in ids for r in groups[g] for line in r["labels"]}
        if any(covers[part] != set(range(5)) for part in target):
            continue
        score = sum(abs(sum(len(groups[g]) for g in assignment[part]) / total - target[part]) for part in target)
        if best is None or score < best[0]:
            best = score, assignment
    if best is None:
        raise ValueError("Cannot cover all five classes in train/val/test by reviewed groups; add/review data")
    destination.mkdir(parents=True)
    assigned = {}
    for part, ids in best[1].items():
        for kind in ("images", "labels"):
            (destination / part / kind).mkdir(parents=True)
        assigned[part] = []
        for group in ids:
            for row in groups[group]:
                shutil.copyfile(prepared / "images" / row["image_file"], destination / part / "images" / row["image_file"])
                shutil.copyfile(prepared / "labels" / (row["image_id"] + ".txt"), destination / part / "labels" / (row["image_id"] + ".txt"))
                assigned[part].append({"image_id": row["image_id"], "group_id": group})
    yaml = "path: .\ntrain: train/images\nval: val/images\ntest: test/images\nnc: 5\nnames: " + json.dumps(list(CLASSES)) + "\n"
    (destination / "data.yaml").write_text(yaml, encoding="utf-8")
    split_identity = hashlib.sha256(json.dumps(assigned, sort_keys=True).encode()).hexdigest()[:12]
    file_hashes = {}
    for file in destination.rglob("*"):
        if file.is_file():
            file_hashes[file.relative_to(destination).as_posix()] = sha256(file)
    report = {"schema_version": 1, "classes": list(CLASSES), "dataset_version": manifest["dataset_version"] + "-" + split_identity,
              "split_ready": True, "seed": 42, "license": manifest["license"], "source": manifest["source"],
              "assignment": assigned, "quarantined": quarantined,
              "counts": {part: len(records) for part, records in assigned.items()},
              "class_counts": {part: dict(Counter(CLASSES[int(line.split()[0])] for group in ids
                   for row in groups[group] for line in row["labels"])) for part, ids in best[1].items()},
              "review_csv_sha256": sha256(prepared / "review.csv"),
              "file_sha256": file_hashes,
              "source_archive_sha256": manifest["archive_sha256"]}
    write_json(destination / "split_manifest.json", report)
    archive = shutil.make_archive(str(destination), "zip", destination)
    return report, archive


def audit(source, prepared):
    """Read back every converted record and compare it with the immutable source."""
    source, prepared = Path(source), Path(prepared)
    manifest = json.loads((prepared / "manifest.json").read_text(encoding="utf-8"))
    if manifest["classes"] != list(CLASSES):
        raise ValueError("Unexpected prepared class order")
    records = manifest["records"]
    if len({row["image_id"] for row in records}) != len(records):
        raise ValueError("Duplicate manifest records")
    if {p.name for p in (prepared / "images").iterdir()} != {r["image_file"] for r in records}:
        raise ValueError("Prepared image inventory mismatch")
    if {p.name for p in (prepared / "labels").iterdir()} != {r["image_id"] + ".txt" for r in records}:
        raise ValueError("Prepared label inventory mismatch")
    counts = Counter()
    for row in manifest["records"]:
        image = source / row["source_image"]
        label = source / row["source_label"]
        if sha256(image) != row["image_sha256"] or sha256(label) != row["source_label_sha256"]:
            raise ValueError(f"Source changed: {row['image_id']}")
        if sha256(prepared / "images" / row["image_file"]) != row["image_sha256"]:
            raise ValueError(f"Converted image changed: {row['image_id']}")
        expected = []
        for line in label.read_text(encoding="utf-8-sig").splitlines():
            fields = line.split()
            if fields and fields[0] != "4":
                fields[0] = "4" if fields[0] == "5" else fields[0]
                expected.append(" ".join(fields))
        actual = (prepared / "labels" / (row["image_id"] + ".txt")).read_text().splitlines()
        if actual != expected or actual != row["labels"]:
            raise ValueError(f"Converted labels mismatch: {row['image_id']}")
        counts.update(CLASSES[int(line.split()[0])] for line in actual)
    for name, digest in manifest.get("source_metadata_sha256", {}).items():
        if sha256(source / name) != digest:
            raise ValueError(f"Source metadata changed: {name}")
    archive_match = None
    if manifest.get("archive_file"):
        archive = source / manifest["archive_file"]
        if sha256(archive) != manifest["archive_sha256"]:
            raise ValueError("Source archive changed")
        with zipfile.ZipFile(archive) as package:
            for row in manifest["records"]:
                for name, digest in ((row["source_image"], row["image_sha256"]),
                                     (row["source_label"], row["source_label_sha256"])):
                    if hashlib.sha256(package.read(name)).hexdigest() != digest:
                        raise ValueError(f"Extracted source differs from ZIP: {name}")
        archive_match = True
    empty = sum(not r["labels"] for r in records)
    negative = sum(not any(int(line.split()[0]) != 0 for line in r["labels"]) for r in records)
    statistics = manifest["statistics"]
    if (statistics["images"], statistics["boxes"], statistics["empty_labels"], statistics["negative_candidates"]) != (len(records), sum(counts.values()), empty, negative):
        raise ValueError("Manifest statistics mismatch")
    return {"status": "PASS", "images": len(records), "class_counts": dict(counts),
            "empty_labels": empty, "negative_candidates": negative,
            "boxes": sum(counts.values()), "source_matches_zip": archive_match,
            "dataset_version": manifest["dataset_version"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    convert = sub.add_parser("convert")
    convert.add_argument("--source", required=True)
    convert.add_argument("--output", required=True)
    split = sub.add_parser("split")
    split.add_argument("--prepared", required=True)
    split.add_argument("--output", required=True)
    verify = sub.add_parser("audit")
    verify.add_argument("--source", required=True)
    verify.add_argument("--prepared", required=True)
    args = parser.parse_args(argv)
    if args.command == "convert":
        result = prepare(args.source, args.output)
    elif args.command == "split":
        result = reviewed_split(args.prepared, args.output)[0]
    else:
        result = audit(args.source, args.prepared)
    print(json.dumps({k: v for k, v in result.items() if k not in ("records", "assignment", "quarantined")}, indent=2))


if __name__ == "__main__":
    main()
