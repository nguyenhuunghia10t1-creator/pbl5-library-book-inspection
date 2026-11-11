"""Dataset conversion, immutable-source checks and reviewed group splits."""
import csv
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

import cv2
import numpy as np

from vision.yolo import CLASSES
from vision.yolo.prepare import REVIEW_FIELDS, audit, prepare, reviewed_split, sha256
from vision.yolo.review import create_review


class DatasetTests(unittest.TestCase):
    def fixture(self, root, total=12):
        (root / "data.yaml").write_text("names: ['Barcode', 'Notch', 'Ripped', 'Spot', 'Tag', 'Wornout']")
        for part in ("train", "valid", "test"):
            for kind in ("images", "labels"):
                (root / part / kind).mkdir(parents=True)
        for n in range(total):
            cv2.imwrite(str(root / "train/images" / f"book{n}.png"), np.full((32, 32, 3), n * 7, np.uint8))
            (root / "train/labels" / f"book{n}.txt").write_text("\n".join(f"{c} .5 .5 .2 .2" for c in range(6)) + "\n")

    def approve(self, prepared, omit=()):
        manifest = json.loads((prepared / "manifest.json").read_text())
        with (prepared / "review.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=REVIEW_FIELDS)
            writer.writeheader()
            for i, row in enumerate(manifest["records"]):
                writer.writerow(dict(image_id=row["image_id"], group_id="book" + str(i // 2),
                    label_review="pending" if i in omit else "approved",
                    negative_review="pending" if row["negative_candidate"] else "not_needed"))

    def test_remap_preserves_coordinates_source_images_labels_and_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            archive = root / "Damaged Books.v1i.yolov11.zip"
            with zipfile.ZipFile(archive, "w") as package:
                for file in root.rglob("*"):
                    if file.is_file() and file != archive:
                        package.write(file, file.relative_to(root).as_posix())
            before = {p.relative_to(root): sha256(p) for p in root.rglob("*") if p.is_file()}
            output = root / "data/prepared"
            manifest = prepare(root, output)
            lines = (output / "labels/train__book0.txt").read_text().splitlines()
            self.assertEqual(lines, [f"{i} .5 .5 .2 .2" for i in range(5)])
            self.assertEqual(manifest["statistics"]["boxes"], 60)
            self.assertEqual(manifest["statistics"]["removed_Tag"], 12)
            self.assertEqual({p: sha256(root / p) for p in before}, before)
            self.assertTrue(audit(root, output)["source_matches_zip"])
            with self.assertRaises(ValueError):
                prepare(root, output)

    def test_empty_labels_and_barcode_only_are_pending_negative_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            (root / "train/labels/book0.txt").write_text("4 .5 .5 .2 .2\n")
            (root / "train/labels/book1.txt").write_text("0 .5 .5 .2 .2\n")
            prepared = root / "data/prepared"
            manifest = prepare(root, prepared)
            self.assertEqual(manifest["statistics"]["empty_labels"], 1)
            self.assertEqual(manifest["statistics"]["negative_candidates"], 2)
            self.assertEqual((prepared / "labels/train__book0.txt").read_bytes(), b"")
            with (prepared / "review.csv").open() as stream:
                rows = {r["image_id"]: r for r in csv.DictReader(stream)}
            self.assertEqual(rows["train__book0"]["negative_review"], "pending")
            with self.assertRaisesRegex(ValueError, "reviewed book groups"):
                reviewed_split(prepared, root / "data/split")
            self.assertFalse((root / "data/split").exists())

    def test_reviewed_groups_are_disjoint_deterministic_and_all_classes_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            prepared = root / "data/prepared"
            prepare(root, prepared)
            self.approve(prepared)
            a, archive = reviewed_split(prepared, root / "data/a")
            b, _ = reviewed_split(prepared, root / "data/b")
            self.assertEqual(a["assignment"], b["assignment"])
            self.assertEqual(a["seed"], 42)
            self.assertTrue(Path(archive).exists())
            groups = [{r["group_id"] for r in a["assignment"][part]} for part in ("train", "val", "test")]
            self.assertFalse(groups[0] & groups[1] or groups[0] & groups[2] or groups[1] & groups[2])
            for part, ratio in (("train", .70), ("val", .15), ("test", .15)):
                self.assertEqual(set(a["class_counts"][part]), set(CLASSES))
                self.assertLess(abs(a["counts"][part] / 12 - ratio), .1)
            for name, digest in a["file_sha256"].items():
                self.assertEqual(sha256(root / "data/a" / name), digest)

    def test_pending_and_unapproved_negatives_are_quarantined(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            (root / "train/labels/book0.txt").write_text("0 .5 .5 .2 .2\n")
            prepared = root / "data/prepared"
            prepare(root, prepared)
            self.approve(prepared, omit=(3,))
            report, _ = reviewed_split(prepared, root / "data/split")
            self.assertIn("train__book0", report["quarantined"])
            ids = {r["image_id"] for records in report["assignment"].values() for r in records}
            self.assertFalse(ids & set(report["quarantined"]))
            self.assertEqual(len(ids) + len(report["quarantined"]), 12)

    def test_impossible_five_class_coverage_is_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            for label in (root / "train/labels").glob("*.txt"):
                label.write_text("1 .5 .5 .2 .2\n")
            prepared = root / "data/prepared"
            prepare(root, prepared)
            self.approve(prepared)
            with self.assertRaisesRegex(ValueError, "all five classes"):
                reviewed_split(prepared, root / "data/split")
            self.assertFalse((root / "data/split").exists())

    def test_exact_duplicates_in_different_groups_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            (root / "train/images/book2.png").write_bytes((root / "train/images/book0.png").read_bytes())
            prepared = root / "data/prepared"
            prepare(root, prepared)
            self.approve(prepared)
            with self.assertRaisesRegex(ValueError, "Identical images"):
                reviewed_split(prepared, root / "data/split")

    def test_changed_source_or_converted_data_fails_audit(self):
        for kind in ("source", "image", "label"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.fixture(root)
                prepared = root / "data/prepared"
                prepare(root, prepared)
                target = {"source": root / "train/labels/book0.txt", "image": prepared / "images/train__book0.png",
                          "label": prepared / "labels/train__book0.txt"}[kind]
                target.write_bytes(b"changed")
                with self.assertRaises(ValueError):
                    audit(root, prepared)

    def test_missing_or_orphan_labels_and_invalid_coordinates_fail_without_output(self):
        for content in (None, "7 .5 .5 .2 .2", "1 nan .5 .2 .2", "1 .5 .5 0 .2"):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.fixture(root)
                label = root / "train/labels/book0.txt"
                if content is None:
                    label.unlink()
                else:
                    label.write_text(content)
                with self.assertRaises(ValueError):
                    prepare(root, root / "data/prepared")
                self.assertFalse((root / "data/prepared").exists())

    def test_review_page_loads_saved_groups_without_auto_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            prepared = root / "data/prepared"
            prepare(root, prepared)
            page = create_review(prepared)
            html = page.read_text(encoding="utf-8")
            rows = json.loads(html.split("const rows=", 1)[1].split(";const cards=", 1)[0])
            self.assertEqual(len(rows), 12)
            self.assertTrue(all(r["review"]["label_review"] == "pending" for r in rows))
            self.assertIn("parseCSV", html)
            self.assertIn("Tải review.csv", html)


if __name__ == "__main__":
    unittest.main()
