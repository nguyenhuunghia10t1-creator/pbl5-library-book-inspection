import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

from software.inspection.runtime import Runtime
from vision.yolo.station import Reading


class StationSettingsTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        folder = self.enterContext(tempfile.TemporaryDirectory())
        self.rt = Runtime(folder=Path(folder))
        self.addCleanup(self.rt.store.db.close)
        self.vision = self.rt.vision
        self.model = SimpleNamespace(checksum="model-a", size=448, mapping={"good": "OK", "bad": "NG"})
        self.vision.classifier = self.model
        self.vision.background = np.zeros((40, 60, 3), dtype=np.uint8)

    async def test_direct_save_and_reset_preserve_calibrated_profile(self):
        folder = self.rt.folder
        profile = folder / "thresholds.json"
        profile.write_bytes(b'{"sentinel":true}')
        direct = Runtime(folder=folder, direct=True)
        self.addCleanup(direct.store.db.close)
        await direct.update_settings({"stabilize_s": 0.6})
        self.assertEqual(direct.cfg["stabilize_s"], 0.6)
        await direct.update_settings({}, reset=True)
        self.assertEqual(profile.read_bytes(), b'{"sentinel":true}')
        self.assertFalse((folder / "vision-settings.json").exists())
        self.assertEqual(direct.cfg["stabilize_s"], self.rt.cfg["stabilize_s"])

    def samples(self, provenance):
        for split in ("cal", "test"):
            for label, truth in (("good", "OK"), ("bad", "NG")):
                reading = Reading(label, 0.98, "HOLD", "", b"jpg", b"raw", self.model.checksum)
                self.rt.store.sample(split + label, truth, split, reading, provenance)

    async def validate(self, label="bad", confidence=0.97):
        reference = {"book": "IMG_7", "truth": "NG", "label": label, "confidence": confidence}
        with patch("software.inspection.reference.inspect_reference", return_value=reference):
            return await self.rt.validate_known_books()

    async def test_idle_only_and_settings_persist_without_collector_changes(self):
        before = self.rt.settings_status()
        for changes in ({"inspection_s": 9}, {"stable_frames": 2.5}, {"min_brightness": 240},
                        {"frozen_s": 0.2, "frame_age_s": 0.8}, {"min_confidence": {"OK": True}}):
            with self.assertRaises(ValueError):
                await self.rt.update_settings(changes)
        self.assertEqual(self.rt.settings_status(), before)
        self.rt.board = {"phase": "RUN"}
        with self.assertRaises(ValueError):
            await self.rt.update_settings({"min_brightness": 44})
        self.rt.board = {}
        current = await self.rt.update_settings({"min_brightness": 44, "min_confidence": {"NG": 0.92}})
        self.assertEqual(current["values"]["min_brightness"], 44)
        self.assertEqual(current["values"]["min_confidence"]["OK"], before["values"]["min_confidence"]["OK"])
        self.assertEqual(self.vision.geometry.min_brightness, 44)
        restarted = Runtime(folder=self.rt.folder)
        self.addCleanup(restarted.store.db.close)
        self.assertEqual(restarted.settings_status()["values"], current["values"])
        reset = await restarted.update_settings({}, reset=True)
        self.assertEqual(reset["values"], before["defaults"])

    async def test_legacy_and_changed_samples_cannot_arm(self):
        self.samples(None)
        with self.assertRaisesRegex(ValueError, "calibration sample"):
            self.rt.calibrate_thresholds()
        self.samples(self.vision.provenance_key())
        await self.validate()
        self.assertTrue(self.rt.settings_status()["calibration"]["valid"])
        await self.rt.update_settings({"min_sharpness": 75})
        self.assertIsNone(self.vision.thresholds)
        with self.assertRaisesRegex(ValueError, "calibration sample"):
            self.rt.calibrate_thresholds()

    async def test_strict_policy_reports_false_ng_with_representative_coverage(self):
        await self.rt.update_settings({"uncertain_policy": "strict_ng"})
        provenance = self.vision.provenance_key()
        self.samples(provenance)
        ambiguous = Reading("good", 0.71, "HOLD", "", b"jpg", b"raw", self.model.checksum)
        self.rt.store.sample("known-good", "OK", "test", ambiguous, provenance)
        profile = await self.validate()
        self.assertEqual(profile["test"], {"OK": 1, "NG": 2, "HOLD": 0, "wrong_ok": 0, "wrong_ng": 1})
        self.assertTrue(self.rt.settings_status()["calibration"]["valid"])

    async def test_strict_policy_rejects_missing_true_ok_coverage(self):
        await self.rt.update_settings({"uncertain_policy": "strict_ng"})
        provenance = self.vision.provenance_key()
        self.samples(provenance)
        with self.rt.store.db:
            self.rt.store.db.execute("DELETE FROM samples WHERE book='testgood'")
        ambiguous = Reading("good", 0.71, "HOLD", "", b"jpg", b"raw", self.model.checksum)
        self.rt.store.sample("known-good", "OK", "test", ambiguous, provenance)
        with self.assertRaisesRegex(ValueError, "known-good"):
            self.rt.calibrate_thresholds()
        failure = self.rt.settings_status()["calibration"]["error"]
        self.assertEqual((failure["truth"], failure["label"], failure["decision"]), ("OK", "good", "NG"))
        self.assertEqual((failure["confidence"], failure["threshold"]), (0.71, 0.85))
        self.assertFalse(self.rt.settings_status()["calibration"]["valid"])

    async def test_saved_profile_requires_exact_provenance(self):
        import cv2

        self.samples(self.vision.provenance_key())
        await self.validate()
        cv2.imwrite(str(self.vision.background_path), self.vision.background)
        path = self.rt.folder / "thresholds.json"
        profile = json.loads(path.read_text(encoding="utf8"))
        with patch("vision.yolo.station.Classifier", return_value=self.model):
            self.vision.thresholds = None
            self.vision._load_station_profile()
            self.assertIsNotNone(self.vision.thresholds)
            self.vision.thresholds = None
            profile.pop("provenance")
            path.write_text(json.dumps(profile), encoding="utf8")
            self.vision._load_station_profile()
            self.assertIsNone(self.vision.thresholds)

    async def test_reference_false_ok_blocks_activation(self):
        self.samples(self.vision.provenance_key())
        with self.assertRaisesRegex(ValueError, "IMG_7"):
            await self.validate("good", 0.98)
        self.assertIsNone(self.vision.thresholds)
        self.assertFalse((self.rt.folder / "thresholds.json").exists())
        error = self.rt.settings_status()["calibration"]["error"]
        self.assertEqual((error["book"], error["truth"], error["decision"]), ("IMG_7", "NG", "OK"))
        for action in ("Manual Mechanics", "compatible classifier", "independent known books", "low-confidence"):
            self.assertIn(action, error["remedy"])

    async def test_threshold_endpoint_returns_the_failed_book_and_remedy_together(self):
        import httpx
        from software.web.app import create_app

        app = create_app()
        app.state.runtime = self.rt
        self.samples(self.vision.provenance_key())
        reference = {"book": "IMG_7", "truth": "NG", "label": "good", "confidence": 0.999}
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://testserver") as client:
            with patch("software.inspection.reference.inspect_reference", return_value=reference):
                response = await client.post("/api/thresholds")
            self.assertEqual(response.status_code, 409)
            detail = response.json()["detail"]
            self.assertEqual((detail["book"], detail["decision"], detail["truth"]), ("IMG_7", "OK", "NG"))
            self.assertIn("Manual Mechanics", detail["remedy"])
            self.assertEqual(detail, (await client.get("/api/settings")).json()["calibration"]["error"])
            self.assertIsNone(self.rt.vision.thresholds)

    async def test_simulation_edits_are_isolated_from_production(self):
        sim = Runtime(simulation=True, folder=self.rt.folder)
        self.addCleanup(sim.store.db.close)
        await sim.update_settings({"uncertain_policy": "strict_ng"})
        self.assertEqual(sim.cfg["uncertain_policy"], "strict_ng")
        self.assertEqual(self.rt.cfg["uncertain_policy"], "hold")
        self.assertTrue((sim.folder / "simulation-vision-settings.json").exists())
        self.assertFalse((sim.folder / "vision-settings.json").exists())

    async def test_missing_resources_leave_automatic_mode_disarmed_and_settings_editable(self):
        path = self.rt.folder / "thresholds.json"
        path.write_text("{}", encoding="utf8")
        self.vision.thresholds = {"OK": 0.9, "NG": 0.9}
        self.vision.classifier = None
        with self.assertRaisesRegex(ValueError, "missing or invalid"):
            await self.rt.validate_known_books()
        self.assertFalse(path.exists())
        self.assertFalse(self.rt.settings_status()["calibration"]["valid"])
        self.assertTrue(self.vision.reason())
        self.assertIn("Manual Mechanics", self.rt.settings_status()["calibration"]["error"]["remedy"])
        result = await self.rt.update_settings({"min_brightness": 44})
        self.assertEqual(result["values"]["min_brightness"], 44)
        self.assertFalse(result["calibration"]["valid"])
