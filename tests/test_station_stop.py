import asyncio
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import patch

import numpy as np

from software.inspection.file_simulation import Photo
from software.inspection.runtime import MANUAL_DECISION_S, Runtime


def board(phase, *, job=1, reason="", ack=None):
    return dict(boot="boot", job=job, phase=phase, ir=True, completed=0, reason=reason,
                ack=ack, capture_id=f"boot-{job}" if phase == "WAIT_AI" else None)


class StopDiagnosticTests(unittest.IsolatedAsyncioTestCase):
    def station(self, **mode):
        directory = self.enterContext(TemporaryDirectory())
        rt = Runtime(folder=Path(directory), **mode)
        self.addCleanup(rt.store.db.close)
        return rt

    async def test_file_hold_keeps_measured_light_after_ack_until_an_actual_stop(self):
        rt = self.station(simulation=True)
        rt.simulation_photo = Photo(np.zeros((400, 400, 3), np.uint8), b"preview")
        rt.observe(board("WAIT_AI"))
        await rt.inspection
        # Serial status and a command acknowledgement may arrive on different polls.
        rt.observe(board("WAIT_AI", ack="HOLD"))
        self.assertIsNone(rt.candidate)
        rt.observe(board("FAULT", reason="INSPECTION_HOLD"))
        snapshot = rt.last_stop
        self.assertEqual(snapshot["reason"], "INSPECTION_HOLD")
        self.assertEqual(snapshot["job_id"], "boot-1")
        issue = snapshot["diagnostic"]
        self.assertEqual((issue["code"], issue["measured"], issue["limit"]),
                         ("BAD_LIGHT", 0, [rt.cfg["min_brightness"], rt.cfg["max_brightness"]]))
        for denied in ("CLEAR_STATION", "RETURN_WAIT", "PC_NOT_READY"):
            rt.observe(board("OFF", reason=denied))
        self.assertEqual(json.loads(rt.last_stop_path.read_text(encoding="utf8")), snapshot)
        rt.observe(board("FAULT", job=2, reason="INSPECTION_HOLD"))
        self.assertIsNone(rt.last_stop["diagnostic"])

    def test_board_stops_exclude_old_camera_and_inspection_evidence(self):
        rt = self.station()
        rt.vision.last_inspection_issue = {"code": "LOW_CONFIDENCE"}
        rt.vision.last_camera_issue = {"code": "FRAME_STALE"}
        current = {"code": "FRAME_FROZEN", "message": "Frozen", "measured": 3, "limit": 2}
        for reason in ("RELEASE_JAM", "LINK_LOST", "MANUAL_OFF"):
            rt.record_stop("FAULT", reason, "boot-1", current)
            self.assertEqual(rt.last_stop["reason"], reason)
            self.assertIsNone(rt.last_stop["diagnostic"])
        rt.record_stop("FAULT", "PC_NOT_READY", "boot-1", current)
        self.assertEqual(rt.last_stop["diagnostic"], current)

    def test_denied_restart_during_fault_keeps_the_incident_until_a_new_stop(self):
        rt = self.station(simulation=True)
        rt.observe(board("RELEASE"))
        rt.observe(board("FAULT", reason="RELEASE_JAM"))
        jam = rt.last_stop
        current = dict(code="FRAME_FROZEN", message="Frozen", limit=1.5, measured=2.1)
        rt.observe(board("FAULT", reason="PC_NOT_READY"), current)
        self.assertEqual(rt.board["reason"], "PC_NOT_READY")
        self.assertEqual(rt.last_stop, jam)
        rt.observe(board("RUN"))
        rt.observe(board("FAULT", reason="PC_NOT_READY"), current)
        self.assertEqual(rt.last_stop["reason"], "PC_NOT_READY")
        self.assertEqual(rt.last_stop["diagnostic"], current)
        rt.observe(board("FAULT", job=2, reason="PC_NOT_READY"))
        self.assertEqual(rt.last_stop["job_id"], "boot-2")
        self.assertIsNone(rt.last_stop["diagnostic"])

    async def test_file_timeout_and_manual_timeout_report_measured_duration_and_limit(self):
        rt = self.station(simulation=True)
        rt.cfg["inspection_s"] = 0.01
        rt.simulation_photo = Photo(None, b"preview")
        with patch.object(rt.file_classifier, "inspect", side_effect=lambda _: time.sleep(0.05)):
            rt.observe(board("WAIT_AI"))
            await rt.inspection
        rt.observe(board("FAULT", reason="INSPECTION_HOLD", ack="HOLD"))
        issue = rt.last_stop["diagnostic"]
        self.assertEqual((issue["code"], issue["limit"]), ("INSPECTION_EXPIRED", 0.01))
        # A Windows monotonic clock tick can exceed this deliberately tiny test budget.
        self.assertGreaterEqual(issue["measured"], 0)

        manual = self.station(manual=True)
        manual.cfg["heartbeat_s"] = 0.001
        stopped = asyncio.Event()

        class Board:
            async def exchange(self, boot, ready, job, verdict):
                if verdict == "HOLD":
                    stopped.set()
                    return board("FAULT", reason="INSPECTION_HOLD", ack="HOLD")
                return board("WAIT_AI")

            async def close(self):
                pass

        manual.ctrl = Board()
        manual.board = board("WAIT_AI")
        manual.observe(manual.board)
        manual.manual_deadline = time.monotonic() - 0.1
        task = asyncio.create_task(manual.run())
        try:
            await asyncio.wait_for(stopped.wait(), 2)
            issue = manual.last_stop["diagnostic"]
            self.assertEqual((issue["code"], issue["limit"]), ("MANUAL_TIMEOUT", MANUAL_DECISION_S))
            self.assertGreaterEqual(issue["measured"], issue["limit"])
        finally:
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
