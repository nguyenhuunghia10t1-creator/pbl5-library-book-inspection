"""Synthetic UI/worker regressions; no camera, display or hardware acceptance."""
from contextlib import ExitStack
from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import cv2
import numpy as np

from software.desktop import cover_capture_app as app
from software.desktop.analysis_worker import AnalysisRequest, AnalysisWorker, SnapshotProcessor
from vision.opencv.camera import Frame
from vision.opencv.config import Config
from vision.opencv.dataset import read_image
from vision.opencv.pipeline import Result, QRResult


def request(sequence=1, revision=0):
    packet = Frame(np.full((64, 64, 3), sequence, np.uint8), "synthetic UTC", time.monotonic(), sequence, "fixture")
    return AnalysisRequest(packet, {"marker": sequence}, Config(stable_frames=1), revision)


def ready(req):
    return Result("READY", corners=np.float32([[2, 2], [61, 2], [61, 61], [2, 61]]),
                  crop=req.packet.image.copy(), qr=QRResult("VALID_FORMAT", f"PBL5-B{req.packet.sequence:02d}"))


def await_completion(worker):
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        value = worker.poll()
        if value is not None:
            return value
        threading.Event().wait(0.001)
    raise AssertionError("Analysis completion did not arrive")


class WorkerTests(unittest.TestCase):
    def test_busy_worker_has_no_frame_backlog(self):
        entered, release = threading.Event(), threading.Event()
        seen = []
        def process(req):
            seen.append(req.packet.sequence)
            entered.set()
            release.wait(3)
            return ready(req)
        worker = AnalysisWorker(process)
        try:
            self.assertTrue(worker.submit(request(1)))
            self.assertTrue(entered.wait(1))
            for seq in range(2, 20):
                self.assertFalse(worker.submit(request(seq)))
            release.set()
            self.assertEqual(await_completion(worker).request.packet.sequence, 1)
            self.assertTrue(worker.submit(request(20)))
            self.assertEqual(await_completion(worker).request.packet.sequence, 20)
            self.assertEqual(seen, [1, 20])
        finally:
            release.set()
            worker.close()
            worker.thread.join(1)

    def test_worker_exception_is_reported_and_next_request_recovers(self):
        def process(req):
            if req.packet.sequence == 1:
                raise RuntimeError("synthetic QR failure")
            return ready(req)
        worker = AnalysisWorker(process)
        try:
            worker.submit(request())
            failed = await_completion(worker)
            self.assertIsNone(failed.result)
            self.assertIn("synthetic QR failure", failed.error)
            self.assertTrue(worker.submit(request(2)))
            self.assertEqual(await_completion(worker).result.status, "READY")
        finally:
            worker.close()

    def test_close_does_not_wait_for_blocked_native_decode(self):
        entered, release = threading.Event(), threading.Event()
        def process(req):
            entered.set()
            release.wait(3)
            return ready(req)
        worker = AnalysisWorker(process)
        worker.submit(request())
        self.assertTrue(entered.wait(1))
        try:
            worker.close()
            self.assertFalse(release.is_set())
            self.assertTrue(worker.thread.is_alive())
            self.assertFalse(worker.submit(request(2)))
        finally:
            release.set()
            worker.thread.join(1)
        self.assertIsNone(worker.poll())

    def test_processor_owns_state_and_resets_on_revision_or_session(self):
        from tests.opencv.test_cover_capture import scene
        image, _ = scene()
        processor = SnapshotProcessor()
        first = replace(request(), packet=replace(request().packet, image=image), config=Config(stable_frames=2))
        self.assertEqual(processor(first).stable_count, 1)
        self.assertEqual(processor(replace(first, packet=replace(first.packet, sequence=2))).stable_count, 2)
        self.assertEqual(processor(replace(first, revision=1)).stable_count, 1)
        self.assertEqual(processor(replace(first, packet=replace(first.packet, camera_session_id="new"))).stable_count, 1)


class UIHarness:
    def __init__(self, folder, process, keys, camera_transform=None):
        self.folder = Path(folder)
        self.process, self.keys, self.transform = process, keys, camera_transform
        self.rendered, self.requests, self.workers = [], [], []
        self.iterations, self.released, self.mouse = 0, False, None
        self.config = Config(output_dir=folder, stable_frames=1, qr_interval_seconds=0.001)

    def capture(self):
        self.iterations += 1
        packet = Frame(np.full((64, 64, 3), self.iterations % 255, np.uint8),
                       datetime.now(timezone.utc).isoformat(), time.monotonic(), self.iterations, "fixture")
        if self.transform:
            packet = self.transform(packet)
        return packet, "LIVE" if packet else "DISCONNECTED", {"marker": self.iterations}

    def release(self):
        self.released = True

    def render(self, packet, result, *args, **kwargs):
        self.rendered.append((packet, result, kwargs.get("analysis_packet")))
        return np.zeros((2, 2, 3), np.uint8), (0, 0, 64, 64)

    def worker(self):
        def process(req):
            self.requests.append(req)
            return self.process(req)
        worker = AnalysisWorker(process)
        self.workers.append(worker)
        return worker

    def wait_key(self, delay):
        if self.iterations > 2000:
            raise AssertionError("UI did not reach the expected state")
        # Yield so this synthetic camera does not starve the real worker thread.
        threading.Event().wait(0.001)
        return self.keys(self)

    def metadata(self):
        return list((self.folder / "captures").glob("*/metadata.json"))

    def run(self, window_open=lambda: 1):
        with ExitStack() as stack:
            targets = {"load_config": lambda _: self.config, "CameraAdapter": lambda _: self,
                       "AnalysisWorker": self.worker, "render": self.render}
            for name, value in targets.items():
                stack.enter_context(patch.object(app, name, value))
            stack.enter_context(patch.object(self, "start", create=True, return_value=self))
            for name in ("namedWindow", "imshow", "destroyAllWindows"):
                stack.enter_context(patch.object(cv2, name))
            stack.enter_context(patch.object(cv2, "setMouseCallback", side_effect=lambda window, callback: setattr(self, "mouse", callback)))
            stack.enter_context(patch.object(cv2, "getWindowProperty", side_effect=lambda *a: window_open()))
            stack.enter_context(patch.object(cv2, "waitKey", side_effect=self.wait_key))
            return app.main(["--source-kind", "synthetic"])


class AsyncUITests(unittest.TestCase):
    def test_preview_advances_and_q_responds_while_qr_blocked(self):
        entered, release = threading.Event(), threading.Event()
        def process(req):
            entered.set()
            release.wait(3)
            return ready(req)
        def keys(ui):
            self.assertTrue(entered.wait(1))
            return ord("q") if ui.iterations >= 5 else -1
        with tempfile.TemporaryDirectory() as folder:
            ui = UIHarness(folder, process, keys)
            try:
                self.assertEqual(ui.run(), 0)
                self.assertFalse(release.is_set())
                self.assertEqual([p.sequence for p, _, _ in ui.rendered], [1, 2, 3, 4, 5])
                self.assertTrue(ui.released)
            finally:
                release.set()
                for worker in ui.workers:
                    worker.thread.join(1)

    def test_window_close_responds_while_qr_blocked(self):
        entered, release = threading.Event(), threading.Event()
        def process(req):
            entered.set()
            release.wait(3)
            return ready(req)
        with tempfile.TemporaryDirectory() as folder:
            ui = UIHarness(folder, process, lambda _: -1)
            try:
                self.assertEqual(ui.run(lambda: 0 if entered.is_set() and ui.iterations >= 3 else 1), 0)
                self.assertFalse(release.is_set())
                self.assertTrue(ui.released)
            finally:
                release.set()
                for worker in ui.workers:
                    worker.thread.join(1)

    def test_save_waits_for_new_frame_and_keeps_raw_qr_properties_together(self):
        entered, release = threading.Event(), threading.Event()
        def process(req):
            if req.packet.sequence == 1:
                entered.set()
                release.wait(3)
            return ready(req)
        def keys(ui):
            if ui.iterations == 1:
                self.assertTrue(entered.wait(1))
                return ord("s")
            if ui.iterations >= 4:
                release.set()
            return ord("q") if ui.metadata() else -1
        with tempfile.TemporaryDirectory() as folder:
            ui = UIHarness(folder, process, keys)
            try:
                self.assertEqual(ui.run(), 0)
            finally:
                release.set()
            paths = ui.metadata()
            self.assertEqual(len(paths), 1)
            record = json.loads(paths[0].read_text(encoding="utf-8"))
            seq = record["capture_seq"]
            self.assertGreater(seq, 1)
            self.assertEqual(record["copy_id"], f"PBL5-B{seq:02d}")
            self.assertEqual(record["camera"]["marker"], seq)
            self.assertTrue(np.all(read_image(paths[0].parent / "raw.png") == seq % 255))
            self.assertTrue(np.all(read_image(paths[0].parent / "cover.png") == seq % 255))
            self.assertFalse(record["manual_frozen_snapshot"])

    def test_no_pre_keypress_frame_is_saved_when_camera_repeats_it(self):
        frame = request().packet
        def keys(ui):
            return ord("s") if ui.iterations == 1 else ord("q") if ui.iterations >= 6 else -1
        with tempfile.TemporaryDirectory() as folder:
            ui = UIHarness(folder, ready, keys, camera_transform=lambda _: frame)
            self.assertEqual(ui.run(), 0)
            self.assertEqual(ui.metadata(), [])

    def test_disconnect_drops_inflight_result_and_pending_save(self):
        entered, release = threading.Event(), threading.Event()
        def process(req):
            entered.set()
            release.wait(3)
            return ready(req)
        def keys(ui):
            if ui.iterations == 1:
                self.assertTrue(entered.wait(1))
                return ord("s")
            release.set()
            return ord("q") if ui.iterations >= 8 else -1
        with tempfile.TemporaryDirectory() as folder:
            ui = UIHarness(folder, process, keys, camera_transform=lambda p: p if p.sequence == 1 else None)
            try:
                self.assertEqual(ui.run(), 0)
            finally:
                release.set()
            self.assertEqual(ui.metadata(), [])
            self.assertTrue(all(p is None and a is None and r.status == "WAITING_FOR_FRESH_FRAME"
                                for p, r, a in ui.rendered[1:]))

    def test_reconnect_rejects_old_camera_session(self):
        entered, release = threading.Event(), threading.Event()
        def process(req):
            if req.packet.camera_session_id == "old":
                entered.set()
                release.wait(3)
            return ready(req)
        def keys(ui):
            if ui.iterations == 1:
                self.assertTrue(entered.wait(1))
            if ui.iterations >= 3:
                release.set()
            return ord("q") if any(a and a.camera_session_id == "new" for _, _, a in ui.rendered) else -1
        def transform(p):
            return replace(p, camera_session_id="old" if p.sequence < 3 else "new")
        with tempfile.TemporaryDirectory() as folder:
            ui = UIHarness(folder, process, keys, transform)
            try:
                self.assertEqual(ui.run(), 0)
            finally:
                release.set()
            self.assertTrue(all(a is None or a.camera_session_id == p.camera_session_id for p, _, a in ui.rendered))

    def test_flip_discards_completion_from_previous_settings(self):
        entered, release = threading.Event(), threading.Event()
        def process(req):
            if not req.flip:
                entered.set()
                release.wait(3)
            return ready(req)
        def keys(ui):
            if ui.iterations == 1:
                self.assertTrue(entered.wait(1))
                return ord("r")
            release.set()
            return ord("q") if any(a for _, _, a in ui.rendered) else -1
        with tempfile.TemporaryDirectory() as folder:
            ui = UIHarness(folder, process, keys)
            try:
                self.assertEqual(ui.run(), 0)
            finally:
                release.set()
            accepted = [a.sequence for _, _, a in ui.rendered if a]
            self.assertNotIn(1, accepted)
            self.assertTrue(any(req.flip for req in ui.requests))

    def test_processing_error_is_visible_and_next_frame_recovers(self):
        def process(req):
            if req.packet.sequence == 1:
                raise RuntimeError("synthetic decode failure")
            return ready(req)
        def keys(ui):
            return ord("q") if any(a for _, _, a in ui.rendered) else -1
        with tempfile.TemporaryDirectory() as folder:
            ui = UIHarness(folder, process, keys)
            self.assertEqual(ui.run(), 0)
            self.assertIn("PROCESSING_ERROR", [r.status for _, r, _ in ui.rendered])
            self.assertTrue(ui.released)

    def test_expired_result_is_not_saved_and_retries_new_frame(self):
        stale = []
        def process(req):
            if req.save_request and not stale:
                stale.append(req.packet.sequence)
                req.packet.monotonic -= 10  # Simulate a completion delayed beyond frame-age limit.
            return ready(req)
        def keys(ui):
            if ui.iterations == 1:
                return ord("s")
            return ord("q") if ui.metadata() else -1
        with tempfile.TemporaryDirectory() as folder:
            ui = UIHarness(folder, process, keys)
            self.assertEqual(ui.run(), 0)
            self.assertEqual(len(stale), 1)
            record = json.loads(ui.metadata()[0].read_text(encoding="utf-8"))
            self.assertGreater(record["capture_seq"], stale[0])

    def test_manual_freeze_save_uses_frozen_frame_not_live_camera(self):
        def keys(ui):
            if ui.iterations == 1:
                return ord("m")
            if ui.iterations == 2:
                for x, y in ((2, 2), (61, 2), (61, 61), (2, 61)):
                    ui.mouse(cv2.EVENT_LBUTTONDOWN, x, y, 0, None)
            if ui.rendered[-1][2] is not None and not ui.metadata():
                return ord("s")
            return ord("q") if ui.metadata() else -1
        with tempfile.TemporaryDirectory() as folder:
            ui = UIHarness(folder, ready, keys)
            self.assertEqual(ui.run(), 0)
            record = json.loads(ui.metadata()[0].read_text(encoding="utf-8"))
            self.assertEqual(record["capture_seq"], 1)
            self.assertEqual(record["camera"]["marker"], 1)
            self.assertTrue(record["manual_frozen_snapshot"])
            self.assertTrue(any(req.manual_points is not None for req in ui.requests))

    def test_background_and_config_changes_reject_old_work_before_save(self):
        entered, release = threading.Event(), threading.Event()
        def process(req):
            if req.revision == 1:
                entered.set()
                release.wait(3)
            return ready(req)
        def keys(ui):
            if ui.iterations == 1:
                self.assertTrue(entered.wait(1))
                return ord("b")
            if ui.iterations == 2:
                return ord("]")
            if ui.iterations == 3:
                return ord("s")
            release.set()
            return ord("q") if ui.metadata() else -1
        with tempfile.TemporaryDirectory() as folder:
            ui = UIHarness(folder, process, keys)
            try:
                self.assertEqual(ui.run(), 0)
            finally:
                release.set()
            record = json.loads(ui.metadata()[0].read_text(encoding="utf-8"))
            self.assertGreater(record["capture_seq"], 3)
            self.assertEqual(record["config_at_capture"]["background_tolerance"], 24)
            self.assertEqual(ui.requests[0].config.background_tolerance, 22)
            background = read_image(Path(folder) / record["background_reference"])
            self.assertTrue(np.all(background == 1))

    def test_review_key_saves_new_frame_as_review(self):
        def process(req):
            result = ready(req)
            result.status = "QUALITY_WARNING"
            result.issues = ["SYNTHETIC_WARNING"]
            return result
        def keys(ui):
            return ord("d") if ui.iterations == 1 else ord("q") if ui.metadata() else -1
        with tempfile.TemporaryDirectory() as folder:
            ui = UIHarness(folder, process, keys)
            self.assertEqual(ui.run(), 0)
            record = json.loads(ui.metadata()[0].read_text(encoding="utf-8"))
            self.assertGreater(record["capture_seq"], 1)
            self.assertEqual(record["collection_status"], "review")
            self.assertEqual(record["vision_status"], "QUALITY_WARNING")

    def test_render_keeps_live_and_annotated_source_separate(self):
        old, new = request(1).packet, request(2).packet
        result = ready(request(1))
        marked = np.full_like(old.image, 99)
        for live in (old, new):
            with self.subTest(live_sequence=live.sequence), \
                    patch.object(app, "annotate", return_value=marked) as annotate, \
                    patch.object(app, "fit_image", wraps=app.fit_image) as fit:
                app.render(live, result, "LIVE", "", {}, analysis_packet=old)
                annotate.assert_called_once()
                self.assertIs(annotate.call_args.args[0], old.image)
                self.assertIs(fit.call_args_list[0].args[1], live.image)
                rendered_analysis = [call for call in fit.call_args_list if call.args[1] is marked]
                self.assertEqual(len(rendered_analysis), 1)
                live_box, analyzed_box = fit.call_args_list[0].args[2], rendered_analysis[0].args[2]
                self.assertLessEqual(live_box[0] + live_box[2], analyzed_box[0])

    def test_live_without_analysis_has_no_geometry_overlay(self):
        live = request().packet
        with patch.object(app, "annotate", wraps=app.annotate) as annotate, \
                patch.object(app, "fit_image", wraps=app.fit_image) as fit:
            app.render(live, Result("WAITING_FOR_ANALYSIS"), "LIVE", "", {})
            annotate.assert_not_called()
            self.assertIs(fit.call_args_list[0].args[1], live.image)

    def test_frozen_manual_selection_keeps_large_source_view(self):
        packet = request().packet
        _, placement = app.render(packet, Result("PICK_4_OUTER_CORNERS"), "LIVE", "", {},
                                  manual_points=[[10, 10]], frozen=True)
        self.assertGreater(placement[2], 420)

    def test_calibration_is_rejected_when_recent_analysis_sees_book_qr(self):
        attempted = []
        def keys(ui):
            if attempted:
                return ord("q")
            if ui.rendered[-1][2] is not None:
                attempted.append(True)
                return ord("b")
            return -1
        with tempfile.TemporaryDirectory() as folder:
            ui = UIHarness(folder, ready, keys)
            self.assertEqual(ui.run(), 0)
            self.assertEqual(attempted, [True])
            self.assertEqual(list(Path(folder).glob("sessions/*/background_*.png")), [])

    def test_held_calibration_key_does_not_relearn_background_each_frame(self):
        def keys(ui):
            return ord("b") if ui.iterations <= 10 else ord("q")
        with tempfile.TemporaryDirectory() as folder:
            ui = UIHarness(folder, lambda req: Result("NO_COVER"), keys)
            self.assertEqual(ui.run(), 0)
            self.assertEqual(len(list(Path(folder).glob("sessions/*/background_*.png"))), 1)


if __name__ == "__main__":
    unittest.main()
