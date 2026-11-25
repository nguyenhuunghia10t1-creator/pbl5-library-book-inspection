import asyncio
from io import BytesIO
from pathlib import Path
import tempfile
import threading
import time
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import cv2
import numpy as np
from PIL import Image

from software.inspection.runtime import Runtime
from software.inspection.file_simulation import FileClassifier, Photo, decode_photo
from vision.yolo.station import square_cover


def status(phase="WAIT_AI", boot="boot", job=1, **extra):
    return {
        "boot": boot, "job": job, "completed": 0, "phase": phase,
        "capture_id": f"{boot}-{job}" if phase == "WAIT_AI" else None,
        "ir": True, "reason": "", **extra,
    }


class RuntimeModeTests(unittest.IsolatedAsyncioTestCase):
    def runtime(self, **mode):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        rt = Runtime(folder=Path(tmp.name), **mode)
        self.addCleanup(rt.store.db.close)
        return rt

    def test_manual_decision_requires_active_identity_and_matching_ack(self):
        rt = self.runtime(manual=True)
        self.assertIsNone(rt.vision)
        self.assertTrue((rt.folder / "hardware-manual.sqlite3").is_file())
        self.assertEqual(rt.health(), "")
        rt.link_error = ""
        rt.board = status()
        rt.observe(rt.board)
        self.assertIsNone(rt.status()["manual_decision"])
        self.assertGreater(rt.status()["manual_remaining_s"], 0)
        with self.assertRaises(ValueError):
            rt.manual_decision("oldboot-1", "OK")
        rt.manual_decision("boot-1", "NG")
        queued = {"key": "boot-1", "verdict": "NG", "state": "queued"}
        self.assertEqual(rt.status()["manual_decision"], queued)
        with self.assertRaises(ValueError):
            rt.manual_decision("boot-1", "OK")
        rt.observe(status("PUSH", ack="OK"))
        self.assertEqual(rt.status()["manual_decision"], queued)
        self.assertEqual(rt.store.summary()[0]["total"], 0)
        rt.observe(status("PUSH", ack="NG"))
        self.assertEqual(rt.status()["manual_decision"], dict(queued, state="acknowledged"))
        counts, rows = rt.store.summary()
        self.assertEqual(counts["ng"], 1)
        self.assertIsNone(rows[0]["confidence"])
        rt.observe(status("RUN", completed=1))
        self.assertIsNone(rt.status()["manual_decision"])

    async def test_manual_deadline_sends_hold_without_pausing_heartbeat(self):
        rt = self.runtime(manual=True)
        seen = []
        capture = status()

        class Controller:
            async def exchange(self, boot, ready, job, verdict):
                seen.append((boot, ready, job, verdict))
                if verdict == "HOLD":
                    return status("FAULT", ack="HOLD", reason="INSPECTION_HOLD")
                return capture

            async def close(self):
                pass

        rt.ctrl = Controller()
        rt.cfg["heartbeat_s"] = 0.01
        rt.start()
        try:
            for _ in range(100):
                if len(seen) >= 3:
                    break
                await asyncio.sleep(0.01)
            self.assertTrue(all(ready and verdict == "WAIT" for _, ready, _, verdict in seen))
            rt.manual_deadline = time.monotonic() - 1
            with self.assertRaises(ValueError):
                rt.manual_decision("boot-1", "OK")
            for _ in range(100):
                if rt.last_stop:
                    break
                await asyncio.sleep(0.01)
            self.assertIn(("boot", True, 1, "HOLD"), seen)
            self.assertEqual(rt.store.summary()[1][0]["status"], "HOLD")
            self.assertTrue(rt.last_stop_path.is_file())
        finally:
            await rt.stop()

    async def test_image_preview_inference_and_explicit_source_switch(self):
        rt = self.runtime(simulation=True)
        data = BytesIO()
        pixels = np.indices((256, 256)).sum(axis=0) % 2 * 255
        Image.fromarray(pixels.astype("uint8")).save(data, "PNG")
        self.assertIsNone(rt.vision)
        with self.assertRaises(ValueError):
            await rt.sim_image(b"invalid")
        with patch("vision.yolo.station.Classifier") as model:
            predict = Mock(return_value=("bad", 0.99))
            model.return_value = SimpleNamespace(
                size=32, mapping={"bad": "NG"}, checksum="fixture",
                predict=predict,
            )
            await rt.sim_image(data.getvalue())
            model.assert_called_once()
            predict.assert_not_called()
            self.assertTrue(rt.status()["simulation_image"])
            self.assertTrue(rt.simulation_preview.startswith(b"\xff\xd8"))
            rt.observe(status())
            await rt.inspection
            predict.assert_called_once()
            original = cv2.imdecode(np.frombuffer(data.getvalue(), dtype=np.uint8), cv2.IMREAD_COLOR)
            np.testing.assert_array_equal(predict.call_args.args[0], square_cover(original, 32))
            self.assertEqual(rt.pending, "NG")
            rt.observe(status("PUSH", ack="NG"))
        self.assertEqual(rt.store.summary()[0]["ng"], 1)
        rt.sim_event("OK")
        self.assertFalse(rt.status()["simulation_image"])

    async def test_file_inference_error_holds_instead_of_using_manual_choice(self):
        rt = self.runtime(simulation=True)
        rt.sim_event("OK")
        rt.simulation_photo = Photo(None, b"test")
        with patch.object(rt.file_classifier, "inspect", side_effect=ValueError("bad model")):
            rt.observe(status())
            await rt.inspection
        self.assertEqual(rt.pending, "HOLD")
        rt.observe(status("FAULT", ack="HOLD", reason="INSPECTION_HOLD"))
        counts, rows = rt.store.summary()
        self.assertEqual(counts["total"], 0)
        self.assertEqual(rows[0]["status"], "HOLD")
        self.assertEqual(rows[0]["reason"], "bad model")

    async def test_preview_endpoint_returns_only_the_selected_active_version(self):
        import httpx
        from software.web.app import create_app

        rt = self.runtime(simulation=True)
        app = create_app(simulation=True)
        app.state.runtime = rt
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url="http://testserver") as client:
            versions = []
            with patch.object(rt.file_classifier, "prepare"):
                for gray in (80, 200):
                    photo = cv2.imencode(".png", np.full((200, 200, 3), gray, dtype=np.uint8))[1].tobytes()
                    result = await client.post("/api/sim/image", content=photo, headers={"Content-Type": "image/png"})
                    result.raise_for_status()
                    version = result.json()["simulation_image_version"]
                    self.assertEqual(version, (await client.get("/api/status")).json()["simulation_image_version"])
                    preview = await client.get("/api/sim/image", params={"version": version})
                    self.assertEqual(preview.content, rt.simulation_preview)
                    self.assertTrue(preview.content.startswith(b"\xff\xd8"))
                    versions.append(version)
            self.assertNotEqual(*versions)
            self.assertEqual((await client.get("/api/sim/image", params={"version": versions[0]})).status_code, 204)
            self.assertTrue((await client.post("/api/sim/NG")).is_success)
            self.assertIsNone((await client.get("/api/status")).json()["simulation_image_version"])
            self.assertEqual((await client.get("/api/sim/image", params={"version": versions[1]})).status_code, 204)

    async def test_simulated_insert_locks_source_even_before_heartbeat_observes_it(self):
        rt = self.runtime(simulation=True)
        rt.simulation_photo = Photo(None, b"first photo")
        rt.ctrl.enter("RUN")
        rt.sim_event("insert")
        self.assertFalse(rt.board)
        with self.assertRaisesRegex(ValueError, "current simulated capture"):
            rt.sim_event("OK")
        with self.assertRaisesRegex(ValueError, "current simulated capture"):
            await rt.sim_image(b"another photo")
        self.assertEqual(rt.simulation_preview, b"first photo")

    async def test_upload_started_before_insert_cannot_replace_active_photo(self):
        rt = self.runtime(simulation=True)
        rt.simulation_photo = Photo(None, b"first photo")
        rt.ctrl.enter("RUN")
        started = threading.Event()
        resume = threading.Event()

        def decode(_):
            started.set()
            resume.wait(timeout=2)
            return Photo(None, b"second photo")

        with patch("software.inspection.runtime.decode_photo", side_effect=decode):
            upload = asyncio.create_task(rt.sim_image(b"new upload"))
            try:
                self.assertTrue(await asyncio.to_thread(started.wait, 1))
                rt.sim_event("insert")
            finally:
                resume.set()
            with self.assertRaisesRegex(ValueError, "current simulated capture"):
                await upload
        self.assertEqual(rt.simulation_preview, b"first photo")

    async def test_file_prediction_timeout_is_retained_after_hold_ack(self):
        rt = self.runtime(simulation=True)
        rt.simulation_photo = Photo(None, b"photo")
        rt.cfg["inspection_s"] = 0.01
        with patch.object(rt.file_classifier, "inspect", side_effect=lambda _: time.sleep(0.05)):
            rt.observe(status())
            await rt.inspection
        self.assertEqual(rt.pending, "HOLD")
        rt.board = status("FAULT", ack="HOLD", reason="INSPECTION_HOLD")
        rt.observe(rt.board)
        observed = rt.status()
        self.assertTrue(observed["idle"])
        self.assertEqual(observed["jobs"][0]["reason"], "Image prediction timed out.")
        self.assertEqual(observed["last_stop"]["reason"], "INSPECTION_HOLD")

    def test_quality_failure_holds_even_with_strict_ng(self):
        rt = self.runtime(simulation=True)
        classifier = FileClassifier(dict(rt.cfg, uncertain_policy="strict_ng"))
        classifier.classifier = Mock()
        cases = (
            (np.zeros((8, 400, 3), np.uint8), "too small"),
            (np.zeros((400, 400, 3), np.uint8), "brightness"),
            (np.full((400, 400, 3), 128, np.uint8), "blurred or blank"),
        )
        for pixels, message in cases:
            result = classifier.inspect(Photo(pixels, b"preview"))
            self.assertEqual(result.verdict, "HOLD")
            self.assertIn(message, result.reason)
        classifier.classifier.predict.assert_not_called()

    def test_jpeg_pixels_match_direct_decode(self):
        source = np.random.default_rng(123).integers(0, 256, (300, 400, 3), dtype=np.uint8)
        ok, encoded = cv2.imencode(".jpg", source)
        self.assertTrue(ok)
        np.testing.assert_array_equal(
            decode_photo(encoded.tobytes()).frame,
            cv2.imdecode(encoded, cv2.IMREAD_COLOR),
        )
