"""Synthetic temporary bundles test integrity only, never camera or AI accuracy."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid

import numpy as np

from vision.opencv import audit as audit_module
from vision.opencv.audit import audit_collection
from vision.opencv.camera import Frame
from vision.opencv.config import Config
from vision.opencv.dataset import DatasetWriter
from vision.opencv.pipeline import QRResult, Result


ROOT = Path(__file__).resolve().parents[2]


class CaptureAuditTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name)
        self.root = self.parent / "thu anh bia"
        self.records = {}
        self.sequence = 0

    def writer(self, source="synthetic"):
        config = Config(output_dir=str(self.root), output_width=105, output_height=148)
        # real/imported below exercise the enum using fake bytes, not hardware evidence.
        return DatasetWriter(config, source, "synthetic fixture testing declared provenance")

    def capture(self, writer=None, copy_id="PBL5-B04", review=False, background=False):
        writer = writer or self.writer()
        self.sequence += 1
        raw = np.arange(32 * 24 * 3, dtype=np.uint8).reshape(32, 24, 3)
        crop = np.full((148, 105, 3), self.sequence, np.uint8)
        qr = QRResult("VALID_FORMAT", copy_id, [copy_id]) if copy_id else QRResult()
        result = Result("READY" if copy_id else "QR_UNREADABLE",
                        np.float32([[1, 1], [22, 1], [22, 30], [1, 30]]), crop, qr=qr)
        packet = Frame(raw, datetime.now(timezone.utc).isoformat(), 0.0, self.sequence,
                       "synthetic-camera-" + writer.session_id)
        reference = writer.save_background(raw) if background else None
        folder = writer.save(packet, result, {}, review=review, background_path=reference)
        record = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))
        self.records[record["image_id"]] = record
        return record

    def rewrite(self, record):
        (self.root / "captures" / record["image_id"] / "metadata.json").write_text(
            json.dumps(record, ensure_ascii=False), encoding="utf-8")
        self.records[record["image_id"]] = record
        self.index()

    def index(self, records=None):
        entries = records if records is not None else self.records.values()
        (self.root / "manifest.jsonl").write_text(
            "".join(json.dumps(record) + "\n" for record in entries), encoding="utf-8")

    def audit(self):
        return audit_collection(self.root)

    def assert_issue(self, code, report=None):
        report = self.audit() if report is None else report
        self.assertFalse(report["ok"], report)
        self.assertIn(code, [issue["code"] for issue in report["issues"]], report)
        return report

    def snapshot(self):
        return {str(path.relative_to(self.root)): (path.read_bytes(), path.stat().st_mtime_ns)
                for path in self.root.rglob("*") if path.is_file()}

    def test_writer_bundles_and_valid_only_statistics(self):
        real = self.writer("real")
        self.capture(real)
        self.capture(real, review=True)
        self.capture(self.writer("imported"), copy_id="B000123")
        self.capture(copy_id=None, review=True, background=True)
        before = self.snapshot()
        report = self.audit()
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["summary"], {"captures": 4, "valid_bundles": 4, "invalid_bundles": 0,
                                            "pending_entries": 0, "errors": 0, "warnings": 0})
        self.assertEqual(report["by_source_kind"], {"real": 2, "imported": 1, "synthetic": 1})
        self.assertEqual(report["by_collection_status"], {"accepted": 2, "review": 2})
        books = {entry["copy_id"]: entry for entry in report["by_copy_id"]}
        self.assertEqual(books["PBL5-B04"], {"copy_id": "PBL5-B04", "captures": 2, "accepted": 1, "review": 1})
        self.assertEqual(books[None]["review"], 1)
        self.assertEqual(report["statistics_scope"], "valid_bundles_only")
        self.assertEqual(before, self.snapshot(), "Audit must not write input files or timestamps")

    def test_hash_mismatch_excluded_from_statistics_without_repair(self):
        record = self.capture()
        raw = self.root / record["files"]["raw"]
        raw.write_bytes(raw.read_bytes() + b"synthetic corruption")
        before = self.snapshot()
        report = self.assert_issue("HASH_MISMATCH")
        self.assertEqual(report["summary"]["invalid_bundles"], 1)
        self.assertEqual(report["by_collection_status"]["accepted"], 0)
        self.assertEqual(report["by_copy_id"], [])
        self.assertEqual(before, self.snapshot())

    def test_every_missing_image_is_reported(self):
        record = self.capture()
        for kind in ("raw", "cover", "debug"):
            with self.subTest(kind=kind):
                path = self.root / record["files"][kind]
                saved = path.read_bytes()
                path.unlink()
                self.assert_issue("IMAGE_UNAVAILABLE")
                path.write_bytes(saved)

    def test_invalid_json_metadata_and_nonfinite_values(self):
        record = self.capture()
        path = self.root / "captures" / record["image_id"] / "metadata.json"
        for text in ("{broken", "[]", '{"image_id":"one","image_id":"two"}', '{"metric":NaN}'):
            with self.subTest(text=text):
                path.write_text(text, encoding="utf-8")
                self.assert_issue("INVALID_JSON")

    def test_missing_metadata_does_not_count_as_valid(self):
        record = self.capture()
        (self.root / "captures" / record["image_id"] / "metadata.json").unlink()
        report = self.assert_issue("INVALID_JSON")
        self.assertEqual(report["summary"]["valid_bundles"], 0)

    def test_schema_and_provenance_validation(self):
        original = self.capture()
        cases = [
            ("schema_version", True, "INVALID_SCHEMA"),
            ("source_kind", "unknown", "INVALID_SOURCE"),
            ("source_kind", {}, "INVALID_SOURCE"),
            ("collection_status", "PASS", "INVALID_COLLECTION_STATUS"),
            ("capture_seq", 0, "INVALID_FRAME_REFERENCE"),
            ("capture_seq", True, "INVALID_FRAME_REFERENCE"),
            ("camera_session_id", "", "INVALID_FRAME_REFERENCE"),
            ("timestamp_utc", "2026-11-07T09:00:00", "INVALID_TIMESTAMP"),
            ("saved_utc", "bad date", "INVALID_TIMESTAMP"),
            ("copy_id", 123, "INVALID_COPY_ID"),
            ("session_id", "../outside", "INVALID_SESSION_ID"),
            ("image_id", str(uuid.uuid4()), "INVALID_IMAGE_ID"),
        ]
        path = self.root / "captures" / original["image_id"] / "metadata.json"
        for field, value, code in cases:
            with self.subTest(field=field, value=value):
                record = deepcopy(original)
                record[field] = value
                path.write_text(json.dumps(record), encoding="utf-8")
                self.index([record])
                report = self.assert_issue(code)
                self.assertEqual(report["summary"]["valid_bundles"], 0)

    def test_qr_and_accepted_status_are_consistent(self):
        original = self.capture()
        for changes, code in [
            ({"qr": {"status": "VALID_FORMAT", "book_id": "different"}}, "QR_ID_MISMATCH"),
            ({"vision_status": "MOVING"}, "INVALID_ACCEPTED"),
            ({"qr": {"status": "UNREADABLE", "book_id": original["copy_id"]}}, "INVALID_ACCEPTED"),
            ({"qr": None}, "QR_ID_MISMATCH"),
            ({"qr": {"book_id": original["copy_id"]}}, "QR_ID_MISMATCH"),
        ]:
            with self.subTest(changes=changes):
                record = dict(original, **changes)
                self.rewrite(record)
                self.assert_issue(code)

    def test_manifest_missing_and_recoverable_without_changing_bundle(self):
        record = self.capture()
        (self.root / "manifest.jsonl").unlink()
        report = self.assert_issue("MANIFEST_UNAVAILABLE")
        self.assertEqual(report["summary"]["valid_bundles"], 1)
        self.assertTrue((self.root / record["files"]["raw"]).is_file())
        self.assertFalse((self.root / "manifest.jsonl").exists())

    def test_manifest_missing_duplicate_orphan_and_changed_records(self):
        original = self.capture()
        orphan = dict(original, image_id=str(uuid.uuid4()))
        changed = dict(original, source_kind="imported")
        for records, code in [
            ([], "MISSING_MANIFEST_RECORD"),
            ([original, original], "DUPLICATE_MANIFEST_ID"),
            ([original, orphan], "ORPHAN_MANIFEST_RECORD"),
            ([changed], "MANIFEST_MISMATCH"),
            ([dict(original, image_id=[])], "INVALID_MANIFEST_ID"),
        ]:
            with self.subTest(code=code):
                self.index(records)
                self.assert_issue(code)

    def test_manifest_invalid_json_object_and_encoding(self):
        self.capture()
        path = self.root / "manifest.jsonl"
        for content in (b"{broken\n", b"[]\n", b'{"image_id":NaN}\n', b"\xff\xfe\xfa"):
            with self.subTest(content=content):
                path.write_bytes(content)
                report = self.audit()
                self.assertFalse(report["ok"])
                self.assertTrue(any(issue["code"] in ("INVALID_MANIFEST_RECORD", "MANIFEST_UNAVAILABLE")
                                    for issue in report["issues"]))

    def test_session_missing_malformed_or_mismatched_for_all_captures(self):
        writer = self.writer()
        self.capture(writer)
        self.capture(writer)
        path = writer.session_dir / "session.json"
        original = json.loads(path.read_text(encoding="utf-8"))
        for changes in ({"source_kind": "real"}, {"session_id": str(uuid.uuid4())},
                        {"created_utc": "not a timestamp"}):
            with self.subTest(changes=changes):
                path.write_text(json.dumps(dict(original, **changes)), encoding="utf-8")
                self.assertEqual(self.audit()["summary"]["valid_bundles"], 0)
        path.write_text("{broken", encoding="utf-8")
        self.assert_issue("SESSION_UNAVAILABLE")
        path.unlink()
        self.assertEqual(self.assert_issue("SESSION_UNAVAILABLE")["summary"]["valid_bundles"], 0)

    def test_duplicate_frame_reference_fails_even_when_manifest_matches(self):
        writer = self.writer()
        first = self.capture(writer)
        second = self.capture(writer)
        second["capture_seq"] = first["capture_seq"]
        self.rewrite(second)
        self.assert_issue("DUPLICATE_FRAME")

    def test_metadata_paths_cannot_read_outside_own_bundle(self):
        original = self.capture()
        sentinel = self.parent / "outside.png"
        sentinel.write_bytes(b"outside collection must not be read")
        for path in ("../../outside.png", str(sentinel), "captures/other/raw.png",
                     original["files"]["raw"].replace("/", "\\")):
            with self.subTest(path=path):
                record = deepcopy(original)
                record["files"]["raw"] = path
                self.rewrite(record)
                with patch("vision.opencv.audit._sha256", wraps=audit_module._sha256) as read_hash:
                    self.assert_issue("INVALID_IMAGE_PATH")
                    self.assertNotIn(sentinel, [call.args[0] for call in read_hash.call_args_list])
                self.assertEqual(sentinel.read_bytes(), b"outside collection must not be read")

    def test_hash_map_must_be_complete_and_well_formed(self):
        original = self.capture()
        for hashes in (None, {}, {"raw": "not hex", "cover": "f" * 64, "debug": "f" * 64}):
            with self.subTest(hashes=hashes):
                self.rewrite(dict(original, sha256=hashes))
                report = self.audit()
                self.assertFalse(report["ok"])
                self.assertEqual(report["summary"]["valid_bundles"], 0)

    def test_file_map_must_be_complete_without_extra_entries(self):
        original = self.capture()
        for files in (None, {}, dict(original["files"], extra="outside.png")):
            with self.subTest(files=files):
                self.rewrite(dict(original, files=files))
                self.assertEqual(self.assert_issue("INVALID_FILES")["summary"]["valid_bundles"], 0)

    def test_utf8_bom_is_supported_without_rewriting_files(self):
        record = self.capture()
        for path in (self.root / "manifest.jsonl",
                     self.root / "captures" / record["image_id"] / "metadata.json",
                     self.root / "sessions" / record["session_id"] / "session.json"):
            path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8-sig")
        before = self.snapshot()
        self.assertTrue(self.audit()["ok"])
        self.assertEqual(before, self.snapshot())

    def test_missing_and_outside_session_backgrounds(self):
        original = self.capture(background=True)
        for reference, code in [
            ("../../outside.png", "INVALID_BACKGROUND_PATH"),
            ("sessions/" + str(uuid.uuid4()) + "/background_000000000000.png", "INVALID_BACKGROUND_PATH"),
            ("sessions/" + original["session_id"] + "/background_000000000000.png", "BACKGROUND_UNAVAILABLE"),
        ]:
            with self.subTest(reference=reference):
                self.rewrite(dict(original, background_reference=reference))
                self.assert_issue(code)

    def test_pending_staging_is_reported_without_becoming_a_completed_capture(self):
        self.capture()
        staging = self.root / "captures" / (".pending_" + str(uuid.uuid4()))
        staging.mkdir()
        (staging / "raw.png").write_bytes(b"partial synthetic write")
        before = self.snapshot()
        report = self.audit()
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["summary"]["captures"], 1)
        self.assertEqual(report["summary"]["pending_entries"], 1)
        self.assertEqual(report["summary"]["warnings"], 1)
        self.assertEqual(before, self.snapshot())

    def test_no_data_and_missing_collection_fail_without_creating_files(self):
        self.assert_issue("COLLECTION_UNAVAILABLE")
        self.assertFalse(self.root.exists())
        (self.root / "captures").mkdir(parents=True)
        self.index([])
        self.assert_issue("NO_CAPTURES")

    def test_linked_images_and_metadata_are_not_opened(self):
        record = self.capture()
        from vision.opencv.audit import _is_link
        for relative in (record["files"]["raw"], f"captures/{record['image_id']}/metadata.json",
                         f"sessions/{record['session_id']}/session.json", "manifest.jsonl",
                         "captures", f"captures/{record['image_id']}",
                         "sessions", f"sessions/{record['session_id']}"):
            target = self.root / relative
            with self.subTest(relative=relative), patch(
                    "vision.opencv.audit._is_link", side_effect=lambda p: p == target or _is_link(p)):
                self.assert_issue("LINK_NOT_ALLOWED")

    def test_cli_json_and_text_from_other_directory_and_exit_status(self):
        self.capture()
        script = str(ROOT / "scripts/audit_captures.py")
        before = self.snapshot()
        for flags in (["--json"], []):
            result = subprocess.run([sys.executable, script, str(self.root), *flags],
                                    cwd=self.parent, text=True, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            if flags:
                self.assertTrue(json.loads(result.stdout)["ok"])
            else:
                self.assertIn("PBL5-B04", result.stdout)
                self.assertIn("synthetic=1", result.stdout)
        self.assertEqual(before, self.snapshot())
        (self.root / "manifest.jsonl").unlink()
        failed = subprocess.run([sys.executable, script, str(self.root), "--json"],
                                cwd=self.parent, text=True, capture_output=True, timeout=20)
        self.assertEqual(failed.returncode, 1)
        self.assertFalse(json.loads(failed.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
