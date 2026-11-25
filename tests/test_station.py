"""Offline tests. Simulated frames/actions never count as physical evidence."""

import asyncio
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from software.controller.simulator import Simulator
from software.inspection.store import Store
from vision.yolo.station import Reading


class PersistenceTests(unittest.TestCase):
    def test_dedup_restart_and_shift(self):
        with TemporaryDirectory() as folder:
            store = Store(Path(folder), "simulation")
            self.assertTrue(store.begin("boot-1"))
            self.assertFalse(store.begin("boot-1"))
            result = Reading("ảnh lỗi", 0.97, "NG", "", b"crop", b"raw", "fake")
            self.assertTrue(store.decision("boot-1", result))
            self.assertFalse(store.decision("boot-1", result))
            store.db.close()
            store = Store(Path(folder), "simulation")
            counts, recent = store.summary()
            self.assertEqual((counts["ng"], recent[0]["status"]), (1, "UNCONFIRMED"))
            store.shift()
            self.assertEqual(store.summary()[0]["total"], 0)
            self.assertEqual(len(store.summary()[1]), 0)
            store.db.close()

    def test_cycle_fault_retains_ai_reason_and_pinned_job(self):
        with TemporaryDirectory() as directory:
            store = Store(Path(directory), "hardware")
            try:
                store.begin("boot-1", "calibrated")
                reading = Reading("good", 0.6, "NG", "Below threshold", b"img", b"raw", "model", 15)
                store.decision("boot-1", reading)
                store.finish("boot-1", "FAULT", "NG_NOT_CLEAR")
                for job in range(2, 11):
                    store.begin(f"boot-{job}", "direct")
                counts, recent = store.summary()
                self.assertEqual(counts["ng"], 1)
                self.assertNotIn("boot-1", [row["id"] for row in recent])
                first = store.job("boot-1")
                self.assertEqual((first["reason"], first["stop_reason"]), ("Below threshold", "NG_NOT_CLEAR"))
                self.assertEqual((first["policy"], first["inference_ms"], first["has_image"]), ("calibrated", 15, 1))
                self.assertTrue(first["created"].endswith("Z"))
            finally:
                store.db.close()


class SimTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.s = Simulator()
        self.s.clear_since -= 1
        await self.s.exchange("-")
        await self.s.exchange(self.s.boot, True)
        self.s.event("button")
        self.s.event("insert")

    async def cmd(self, value="WAIT", job=1):
        return await self.s.exchange(self.s.boot, True, job, value)

    async def test_ok_releases_occluded_ir_once(self):
        self.assertEqual((await self.cmd("OK"))["phase"], "RELEASE")
        self.s.event("insert")
        self.assertEqual((await self.cmd("NG"))["job"], 1)
        self.s.event("remove")
        self.s.clear_since -= 0.2
        self.assertEqual((await self.cmd())["completed"], 1)

    async def test_ng_and_duplicate(self):
        self.assertEqual((await self.cmd("NG"))["phase"], "PUSH")
        self.s.since -= 1
        self.assertEqual((await self.cmd("NG"))["phase"], "RETRACT")
        self.s.since -= 1
        self.assertEqual((await self.cmd())["phase"], "SETTLE")
        self.s.since -= 2
        self.assertEqual((await self.cmd())["reason"], "NG_NOT_CLEAR")

    async def test_stale_and_off(self):
        self.assertEqual((await self.cmd("NG", 2))["phase"], "WAIT_AI")
        self.s.event("button")
        self.assertEqual((await self.cmd("NG"))["phase"], "OFF")

    async def test_watchdog(self):
        self.s.beat -= 2
        self.assertEqual((await self.cmd("NG"))["phase"], "FAULT")

    async def test_start_reports_occupied_ir_and_retries_after_clear(self):
        self.s.event("button")
        stopped_at = self.s.since
        for _ in range(2):
            with self.assertRaisesRegex(ValueError, "^CLEAR_STATION$"):
                self.s.event("button")
            state = await self.cmd()
            self.assertEqual((state["phase"], state["reason"], state["pwm"]), ("OFF", "CLEAR_STATION", 0))
            self.assertEqual(self.s.since, stopped_at)

        self.s.event("remove")
        self.s.clear_since -= 0.2
        self.s.event("button")
        state = await self.cmd()
        self.assertEqual((state["phase"], state["reason"], state["job"]), ("RUN", "", 1))


@unittest.skipUnless(
    importlib.util.find_spec("fastapi")
    and importlib.util.find_spec("httpx"),
    "Requires station runtime and httpx",
)
class HmiTests(unittest.TestCase):
    def test_connect_uses_explicit_port_or_auto_detection(self):
        from unittest.mock import AsyncMock, patch
        from fastapi.testclient import TestClient
        from software.web.app import create_app

        with (
            patch("software.web.app.Runtime") as runtime_class,
            TestClient(create_app()) as client,
        ):
            rt = runtime_class.return_value
            rt.stop = AsyncMock()
            rt.connect_serial = AsyncMock()
            self.assertIn("Kết nối USB", client.get("/").text)
            self.assertTrue(client.post("/api/connect", json={"port": "com5"}).is_success)
            rt.connect_serial.assert_awaited_once_with("COM5")
            rt.connect_serial.reset_mock()
            self.assertTrue(client.post("/api/connect", json={}).is_success)
            rt.connect_serial.assert_awaited_once_with("")
            rt.connect_serial.reset_mock()
            self.assertEqual(client.post("/api/connect", json={"port": "192.168.1.5"}).status_code, 422)
            rt.connect_serial.assert_not_awaited()

    def test_camera_mode_runs_without_controller_or_store(self):
        from unittest.mock import patch
        from fastapi.testclient import TestClient
        from software.web.app import create_app

        with (
            patch("software.web.app.Runtime", side_effect=AssertionError("controller")),
            patch("vision.yolo.station.StationVision") as vision_class,
            TestClient(create_app(camera_test=True)) as client,
        ):
            vision = vision_class.return_value
            vision.camera_status.return_value = ""
            vision.classifier.checksum = "test-weights"
            vision.classify_snapshot.return_value = ("NG", "not_ok_nhe", 0.75, b"frame")
            self.assertIn("Chụp và nhận diện", client.get("/").text)
            self.assertEqual(client.get("/api/status").json()["mode"], "camera-test")
            sample = client.post("/api/capture").json()
            self.assertEqual((sample["label"], sample["model_sha256"]), ("not_ok_nhe", "test-weights"))
            self.assertEqual((sample["prediction"], sample["confidence"]), ("NG", 0.75))
            self.assertEqual(sample["image"], "data:image/jpeg;base64,ZnJhbWU=")
            self.assertEqual(client.post("/api/connect").status_code, 404)
            vision.classify_snapshot.side_effect = ValueError("Chờ hình mới từ DroidCam")
            self.assertEqual(client.post("/api/capture").status_code, 409)
        vision.close.assert_called_once()

    def test_serves_hmi_and_simulates_a_book(self):
        import time
        from fastapi.testclient import TestClient
        from software.web.app import create_app

        with (
            TemporaryDirectory() as folder,
            TestClient(create_app(True, Path(folder))) as client,
        ):
            self.assertIn("Trạm kiểm tra sách", client.get("/").text)
            self.assertEqual(client.get("/api/status").json()["mode"], "simulation")

            def wait(test):
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline:
                    state = client.get("/api/status").json()
                    if test(state):
                        return state
                    time.sleep(0.06)
                self.fail(str(state))

            wait(lambda s: s["board"].get("phase") == "OFF" and client.app.state.runtime.ctrl.ready)
            self.assertTrue(client.post("/api/sim/insert").is_success)
            denied = client.post("/api/sim/button")
            self.assertEqual((denied.status_code, denied.json()), (409, {"detail": "CLEAR_STATION"}))
            wait(lambda s: s["board"].get("reason") == "CLEAR_STATION")
            self.assertTrue(client.post("/api/sim/remove").is_success)
            time.sleep(0.2)
            for action in ("button", "insert"):
                self.assertTrue(client.post("/api/sim/" + action).is_success)
            wait(lambda s: s["board"].get("phase") == "RELEASE")
            client.post("/api/sim/remove")
            result = wait(lambda s: s["jobs"] and s["jobs"][0]["status"] == "COMPLETE")
            self.assertEqual(result["counts"], {"ok": 1, "ng": 0, "total": 1})
            client.post("/api/sim/camera")
            wait(lambda s: s["board"].get("phase") == "FAULT")
            client.post("/api/sim/camera")
            client.post("/api/sim/ai")
            wait(lambda s: "AI" in s["health"])
            client.post("/api/sim/wifi")
            wait(lambda s: bool(s["link_error"]))
            client.post("/api/sim/wifi")
            wait(lambda s: s["board"].get("phase") == "FAULT")
