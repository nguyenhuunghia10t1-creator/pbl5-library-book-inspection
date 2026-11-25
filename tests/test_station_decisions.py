import importlib.util
from pathlib import Path
import tempfile
import unittest

import numpy as np
from unittest.mock import patch
from types import SimpleNamespace

from vision.yolo.station import Reading


@unittest.skipUnless(importlib.util.find_spec("serial"), "Requires station runtime")
class DecisionTests(unittest.TestCase):
    def setUp(self):
        from software.inspection.runtime import Runtime

        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.rt = Runtime(False, Path(self.temp.name))
        self.addCleanup(self.rt.store.db.close)
        self.rt.vision.classifier = SimpleNamespace(
            checksum="fixture", size=448, mapping={"good": "OK", "bad": "NG"}
        )
        self.rt.vision.background = np.zeros((20, 30, 3), dtype=np.uint8)

    def test_manual_stop_during_network_roundtrip_does_not_count(self):
        rt = self.rt
        rt.key = "boot-3"
        rt.store.begin(rt.key)
        rt.candidate = Reading("bad", 0.99, "NG", "", b"jpg", b"raw", "fixture")
        rt.pending = "NG"
        rt.observe(
            dict(boot="boot", job=3, completed=2, phase="OFF", reason="MANUAL_OFF")
        )
        counts, jobs = rt.store.summary()
        self.assertEqual(counts["total"], 0)
        self.assertEqual(jobs[0]["status"], "UNCONFIRMED")

    def test_counts_an_accepted_decision_once(self):
        rt = self.rt
        rt.key = "boot-8"
        rt.store.begin(rt.key)
        rt.candidate = Reading("good", 0.98, "OK", "", b"jpg", b"raw", "fixture")
        rt.pending = "OK"
        board = dict(boot="boot", job=8, completed=7, phase="RELEASE", reason="")
        rt.observe(board)
        self.assertEqual(rt.store.summary()[0]["ok"], 0)
        board["ack"] = "OK"
        rt.observe(board)
        rt.observe(board)
        self.assertEqual(rt.store.summary()[0]["ok"], 1)
        rt.observe(dict(board, completed=8, phase="RUN"))
        self.assertEqual(rt.store.summary()[1][0]["status"], "COMPLETE")

    def test_only_matching_capture_starts_yolo_and_replays_do_not_repeat_it(self):
        rt = self.rt
        board = dict(boot="boot", job=4, completed=3, phase="WAIT_AI", reason="")
        with patch("asyncio.create_task") as task:
            rt.observe(board)
            rt.observe(dict(board, capture_id="boot-3"))
            task.assert_not_called()
            board["capture_id"] = "boot-4"
            rt.observe(board)
            rt.observe(board)
            task.assert_called_once()
            task.call_args.args[0].close()
            rt.end_job("UNCONFIRMED", "LINK_LOST")
            rt.observe(board)
            self.assertEqual(rt.pending, "HOLD")
            task.assert_called_once()

    def test_thresholds_reject_leaked_books_and_false_ok(self):
        rt = self.rt
        provenance = rt.vision.provenance_key()
        for split in ("cal", "test"):
            for label, truth in (("bad", "NG"), ("good", "OK")):
                r = Reading(label, 0.98, "HOLD", "", b"x", b"x", "fixture")
                rt.store.sample(split + label, truth, split, r, provenance)
        profile = rt.calibrate_thresholds()
        self.assertEqual(profile["thresholds"], {"OK": 0.85, "NG": 0.85})
        with self.assertRaises(ValueError):
            rt.store.sample("calgood", "OK", "test", r)
        wrong = Reading("good", 0.99, "OK", "", b"x", b"x", "fixture")
        rt.store.sample("bad-passed", "NG", "test", wrong, provenance)
        with self.assertRaisesRegex(ValueError, "bad-passed"):
            rt.calibrate_thresholds()
        self.assertIsNone(rt.vision.thresholds)
