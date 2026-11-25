"""Guard source integrity and uncertainty semantics of the proposal-only review."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import cv2
import numpy as np

SPEC = importlib.util.spec_from_file_location(
    "review20", Path(__file__).resolve().parents[1] / "scripts/build_damaged_books_review20.py")
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


class ProposalSafetyTests(unittest.TestCase):
    def test_independent_damage_can_overlap_barcode(self):
        boxes = [[0, .5, .5, .5, .5], [3, .5, .5, .05, .05]]
        actions = [{"action": "keep", "source_lines": [n], "reason": "Two separate visible phenomena"}
                   for n in (1, 2)]
        proposed, _ = review.apply_proposals(boxes, actions, (640, 640))
        self.assertEqual([r["box"] for r in proposed], boxes)

    def test_unknown_rip_is_preserved_and_flagged(self):
        box = [2, .5, .5, .2, .2]
        proposed, changes = review.apply_proposals([box], [{"action": "needs_review", "source_lines": [1],
                                                        "reason": "Cannot separate rip from surface wear"}], (640, 640))
        self.assertEqual(proposed[0]["box"], box)
        self.assertTrue(proposed[0]["review_required"])
        self.assertEqual(changes[0]["before"], changes[0]["after"])

    def test_no_silent_drop_or_double_consumption(self):
        boxes = [[4, .5, .5, .1, .1]]
        with self.assertRaises(ValueError):
            review.apply_proposals(boxes, [], (640, 640))
        action = {"action": "delete", "source_lines": [1], "reason": "Printed artwork"}
        with self.assertRaises(ValueError):
            review.apply_proposals(boxes, [action, action], (640, 640))

    def test_new_barcode_and_bad_coordinates(self):
        action = {"action": "add", "source_lines": [], "class_id": 0,
                  "xyxy_px": [10, 20, 80, 60], "reason": "Visible barcode omitted in empty label"}
        proposed, _ = review.apply_proposals([], [action], (100, 100))
        self.assertEqual(proposed[0]["box"], [0, .45, .4, .7, .4])
        action["xyxy_px"] = [10, 20, 101, 60]
        with self.assertRaises(ValueError):
            review.apply_proposals([], [action], (100, 100))

    def test_all_merged_boxes_are_traceable(self):
        originals = [[4, .25, .5, .1, .1], [4, .35, .5, .1, .1]]
        action = {"action": "merge", "source_lines": [1, 2], "class_id": 4,
                  "xyxy_px": [20, 45, 40, 55], "reason": "One continuous worn edge"}
        proposed, changes = review.apply_proposals(originals, [action], (100, 100))
        self.assertEqual(changes[0]["before"], originals)
        self.assertEqual(proposed[0]["source_lines"], [1, 2])


class SourceGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        manifest = {"classes": review.CLASSES, "dataset_version": "fixture", "assignment": {"train": [], "val": []}}
        records = []
        for n in range(20):
            split = "val" if n < 12 else "train"
            ident = f"fixture_{n}"
            for folder in ("images", "labels"):
                (self.root / split / folder).mkdir(parents=True, exist_ok=True)
            ip, lp = self.root / split / "images" / f"{ident}.jpg", self.root / split / "labels" / f"{ident}.txt"
            cv2.imwrite(str(ip), np.full((4, 4, 3), 140, np.uint8))
            lp.write_text("", encoding="utf-8")
            manifest["assignment"][split].append({"image_id": ident, "group_id": f"group_{n}"})
            records.append({"split": split, "image_id": ident, "group_id": f"group_{n}",
                            "image_size": [4, 4], "image_sha256": review.sha256(ip), "label_sha256": review.sha256(lp),
                            "expected_class_counts": [0] * 5, "observation": "Viewed original image",
                            "actions": [], "questions": []})
        # No test folder exists: a valid build must never attempt to open it.
        (self.root / "split_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        self.decisions = {"classes": review.CLASSES, "dataset_version": "fixture",
                          "manifest_sha256": review.sha256(self.root / "split_manifest.json"), "records": records}

    def test_empty_unknown_is_not_clean_and_sources_unchanged(self):
        self.decisions["records"][0]["questions"] = [{"priority": "route", "question": "Rip or cover flap?",
                                                      "reason": "Empty label does not establish a negative"}]
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        report = review.build_report(self.root, self.decisions)
        self.assertEqual(report["records"][0]["status"], "needs_review")
        self.assertFalse(report["records"][0]["fully_approved"])
        self.assertFalse(report["test_opened"])
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_stale_source_hash_and_duplicate_ids_are_rejected(self):
        stale = copy.deepcopy(self.decisions)
        stale["records"][0]["label_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Label changed"):
            review.build_report(self.root, stale)
        duplicate = copy.deepcopy(self.decisions)
        duplicate["records"][1]["image_id"] = duplicate["records"][0]["image_id"]
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            review.build_report(self.root, duplicate)


if __name__ == "__main__":
    unittest.main()
