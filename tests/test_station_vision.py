"""Exercise the station gate with synthetic covers, without opening camera or loading weights."""

import json
import threading
import time
import unittest
from unittest.mock import Mock

import numpy as np

from tests.opencv.test_cover_capture import scene
from vision.opencv.camera import Frame
from vision.yolo.station import ROOT, StationVision


class VisionGateTests(unittest.TestCase):
    def setUp(self):
        cfg = json.loads((ROOT / "configs/station.json").read_text(encoding="utf8"))
        cfg.update(inspection_s=1.3, stabilize_s=0.05)
        self.v = StationVision(cfg)
        self.img, _ = scene()
        self.v.background = np.broadcast_to(self.img[0, 0], self.img.shape).copy()
        self.v.geometry.stable_frames = 2
        self.v.classifier = Mock(size=448, checksum="fixture", mapping={"good": "OK"})
        self.v.thresholds = {"OK": 0.9, "NG": 0.9}

    def inspect(self, image, *, direct=False):
        stop = threading.Event()

        def feed():
            seq = 0
            while not stop.is_set():
                now = time.monotonic()
                with self.v.frame_lock:
                    self.v.latest = Frame(image, "test", now, seq, "fake-camera")
                    self.v.changed_at = now
                seq += 1
                stop.wait(0.04)

        worker = threading.Thread(target=feed)
        worker.start()
        try:
            return self.v.inspect(time.monotonic(), threading.Event(), direct=direct)
        finally:
            stop.set()
            worker.join()

    def test_stable_cover_once_and_below_threshold_holds(self):
        self.v.classifier.predict.return_value = ("good", 0.72)
        r = self.inspect(self.img)
        self.assertEqual((r.verdict, r.label), ("HOLD", "good"))
        self.assertTrue(r.image and r.raw)
        self.v.classifier.predict.assert_called_once()
        self.assertEqual(
            self.v.classifier.predict.call_args.args[0].shape, (448, 448, 3)
        )

    def test_empty_belt_never_classified(self):
        with self.assertRaises(ValueError):
            self.inspect(self.v.background)
        self.v.classifier.predict.assert_not_called()

    def test_manual_snapshot_uses_current_frame_without_station_calibration(self):
        self.v.background = self.v.thresholds = None
        now = time.monotonic()
        self.v.latest = Frame(self.img, "test", now, 1, "manual")
        self.v.changed_at = now
        self.v.classifier.predict.return_value = ("good", 0.64)
        verdict, label, confidence, photo = self.v.classify_snapshot()
        self.assertEqual((verdict, label, confidence), ("OK", "good", 0.64))
        self.assertTrue(photo.startswith(b"\xff\xd8"))
        self.v.changed_at -= 15
        with self.assertRaisesRegex(ValueError, "frozen"):
            self.v.classify_snapshot()
        self.v.classifier.predict.assert_called_once()

    def test_direct_routing_uses_both_top_labels_on_full_frames(self):
        self.v.background = self.v.thresholds = None
        self.v.direct_routing = True
        self.v.classifier.mapping = {"good": "OK", "bad": "NG"}
        for label, route in self.v.classifier.mapping.items():
            self.v.classifier.predict.reset_mock()
            self.v.classifier.predict.return_value = (label, 0.55)
            reading = self.inspect(self.img, direct=True)
            self.assertEqual((reading.verdict, reading.confidence), (route, 0.55))
            self.assertEqual(self.v.reason(), "")
            self.v.classifier.predict.assert_called_once()
        self.v.changed_at -= 15
        self.assertIn("frozen", self.v.reason())
        with self.assertRaisesRegex(ValueError, "frozen"):
            self.v.inspect(time.monotonic(), threading.Event(), direct=True)

    def test_frozen_and_stale_frames(self):
        now = time.monotonic()
        self.v.latest = Frame(self.img, "test", now, 8, "camera")
        self.v.changed_at = now - 10
        self.assertIn("frozen", self.v.camera_status())
        self.v.latest.monotonic = now - 10
        self.v.changed_at = now
        self.assertNotEqual(self.v.camera_status(), "")

    def test_strict_ng_requires_valid_image_and_calibration(self):
        self.v.cfg["uncertain_policy"] = "strict_ng"
        self.v.classifier.predict.return_value = ("good", 0.72)
        self.assertEqual(self.inspect(self.img).verdict, "NG")
        issue = self.v.diagnostics_status()["inspection"]
        self.assertEqual((issue["code"], issue["measured"], issue["limit"]), ("LOW_CONFIDENCE", 0.72, 0.9))
        self.v.thresholds = None
        self.assertEqual(self.inspect(self.img).verdict, "HOLD")
        self.v.classifier.predict.reset_mock()
        with self.assertRaises(ValueError):
            self.inspect(self.v.background)
        self.v.classifier.predict.assert_not_called()
