"""Synthetic fixtures exercise software only; never evidence of real camera accuracy."""
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

import cv2
import numpy as np

from vision.opencv.camera import CameraAdapter, Frame, wait_for_frame
from vision.opencv.config import Config, load_config
from vision.opencv.dataset import DatasetWriter, read_image, rebuild_manifest
from vision.opencv.pipeline import CoverVision, QRReader, corner_motion, order_quad, parse_payload
from software.desktop.cover_capture_app import main


def qr_image(payload="PBL5-B04", size=154):
    qr = cv2.QRCodeEncoder_create().encode(payload)
    qr = cv2.copyMakeBorder(qr, 4, 4, 4, 4, cv2.BORDER_CONSTANT, value=255)
    return cv2.cvtColor(cv2.resize(qr, (size, size), interpolation=cv2.INTER_NEAREST), cv2.COLOR_GRAY2BGR)


def cover(two_qr=False, color=(235, 240, 245)):
    image = np.full((592, 420, 3), color, np.uint8)
    cv2.rectangle(image, (14, 14), (405, 577), (45, 65, 110), 3)
    cv2.putText(image, "PBL5", (45, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (50, 45, 80), 4)
    cv2.putText(image, "BOOK 04", (45, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.15, (50, 45, 80), 2)
    for y in range(210, 370, 22):
        cv2.line(image, (45, y), (360, y), (80, 120, 170), 2)
    image[406:560, 234:388] = qr_image()
    if two_qr:
        image[406:560, 32:186] = qr_image("PBL5-B05")
    return image


def scene(angle=0, perspective=False, two_qr=False, color=(235, 240, 245)):
    background = np.full((900, 1200, 3), (165, 155, 140), np.uint8)
    src = np.float32([[0, 0], [419, 0], [419, 591], [0, 591]])
    if perspective:
        dst = np.float32([[382, 144], [795, 179], [830, 742], [350, 720]])
    else:
        dst = cv2.boxPoints(((600, 450), (420, 592), angle)).astype(np.float32)
        # Explicit source corner mapping, including 180/270 deg rotations.
        theta = np.deg2rad(angle)
        rotation = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
        dst = ((src - [209.5, 295.5]) @ rotation.T + [600, 450]).astype(np.float32)
    transform = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(cover(two_qr, color), transform, (1200, 900))
    mask = cv2.warpPerspective(np.full((592, 420), 255, np.uint8), transform, (1200, 900))
    background[mask > 0] = warped[mask > 0]
    return background, dst


class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.config = Config(stable_frames=2)

    def test_rotation_and_qr(self):
        for angle in (0, 25, 45, 90, 135, 180, 225, 270):
            with self.subTest(angle=angle):
                image, expected = scene(angle)
                vision = CoverVision(self.config)
                result = vision.process(image)
                result = vision.process(image)
                self.assertEqual(result.status, "READY", (angle, result.status, result.issues))
                self.assertEqual(result.qr.book_id, "PBL5-B04")
                self.assertEqual(result.crop.shape, (888, 630, 3))
                self.assertLess(corner_motion(result.corners, order_quad(expected)), 10)
                self.assertLess(float(result.crop[70:200].mean()), 250)
                self.assertEqual(QRReader().read(result.crop).book_id, "PBL5-B04")
                qr_center = np.array(result.qr.points).reshape(-1, 2).mean(axis=0)
                self.assertGreater(qr_center[0], 315)
                self.assertGreater(qr_center[1], 444)

    def test_perspective(self):
        image, corners = scene(perspective=True)
        result = CoverVision(self.config).process(image)
        self.assertIsNotNone(result.crop)
        self.assertLess(corner_motion(result.corners, order_quad(corners)), 10)
        self.assertEqual(result.qr.book_id, "PBL5-B04")

    def test_blank_and_empty(self):
        vision = CoverVision(self.config)
        self.assertEqual(vision.process(None).status, "EMPTY_FRAME")
        self.assertEqual(vision.process(np.full((720, 1280, 3), 150, np.uint8)).status, "NO_COVER")

    def test_ambiguous_qr(self):
        image, _ = scene(two_qr=True)
        result = CoverVision(self.config).process(image)
        self.assertEqual(result.qr.status, "AMBIGUOUS")
        self.assertIsNone(result.qr.book_id)

    def test_blur_and_movement(self):
        image, _ = scene()
        vision = CoverVision(self.config)
        self.assertEqual(vision.process(image).status, "MOVING")
        self.assertEqual(vision.process(image).status, "READY")
        moved = cv2.warpAffine(image, np.float32([[1, 0, 30], [0, 1, 0]]), (1200, 900), borderValue=(165, 155, 140))
        self.assertEqual(vision.process(moved).stable_count, 1)
        blurred = cv2.GaussianBlur(image, (35, 35), 10)
        result = vision.process(blurred)
        self.assertIn("BLURRY", result.issues)

    def test_clipped_cover_is_not_accepted(self):
        image, _ = scene()
        image = cv2.warpAffine(image, np.float32([[1, 0, -400], [0, 1, 0]]), (1200, 900), borderValue=(165, 155, 140))
        result = CoverVision(self.config).process(image)
        self.assertNotEqual(result.status, "READY")
        self.assertTrue(result.crop is None or result.issues)

    def test_two_covers(self):
        bg = np.full((900, 1500, 3), (165, 155, 140), np.uint8)
        bg[154:746, 100:520] = cover()
        bg[154:746, 850:1270] = cover()
        self.assertEqual(CoverVision(self.config).process(bg).status, "MULTIPLE_COVERS")

    def test_calibrated_dark_cover(self):
        image, _ = scene(color=(55, 65, 80))
        vision = CoverVision(self.config)
        vision.calibrate(np.full_like(image, (165, 155, 140)))
        result = vision.process(image)
        self.assertIsNotNone(result.crop)
        self.assertEqual(result.qr.book_id, "PBL5-B04")

    def test_manual_bad_points(self):
        for points in ([[1, 1]] * 4, [[0, 0], [10, 0], [20, 0], [30, 0]]):
            with self.assertRaises(ValueError):
                order_quad(points)


class QRTests(unittest.TestCase):
    def test_formats(self):
        for payload, status, book_id in [
            ("PBL5-B04", "VALID_FORMAT", "PBL5-B04"),
            ("PBL5-B123", "VALID_FORMAT", "PBL5-B123"),
            ("LIB1:B000123", "VALID_FORMAT", "B000123"),
            ("PBL5-../x", "INVALID_FORMAT", None),
            ("LIB1:", "INVALID_FORMAT", None),
            ("OTHER:B04", "INVALID_NAMESPACE", None),
        ]:
            self.assertEqual(parse_payload(payload), (status, book_id))

    def test_no_qr(self):
        self.assertEqual(QRReader().read(np.full((400, 300, 3), 180, np.uint8)).status, "UNREADABLE")


class StorageTests(unittest.TestCase):
    def test_roundtrip_unique_and_manifest(self):
        with tempfile.TemporaryDirectory() as folder:
            config = Config(output_dir=str(Path(folder) / "thu anh bia"), stable_frames=1)
            image, _ = scene()
            result = CoverVision(config).process(image)
            packet = Frame(image, datetime.now(timezone.utc).isoformat(), time.monotonic(), 1, "fake-camera")
            writer = DatasetWriter(config, "synthetic", "unit test")
            first = writer.save(packet, result, {})
            with self.assertRaisesRegex(ValueError, "already saved"):
                writer.save(packet, result, {})
            second = writer.save(replace(packet, sequence=2), result, {})
            self.assertNotEqual(first, second)
            np.testing.assert_array_equal(read_image(first / "raw.png"), image)
            self.assertEqual(read_image(first / "cover.png").shape, (888, 630, 3))
            record = json.loads((first / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(record["source_kind"], "synthetic")
            self.assertIsNone(record["ai_quality"])
            self.assertEqual(record["identity_status"], "NOT_CHECKED")
            self.assertEqual(record["sha256"]["raw"], hashlib.sha256((first / "raw.png").read_bytes()).hexdigest())
            self.assertEqual(rebuild_manifest(config.output_dir), 2)

    def test_reject_stale_and_nonready(self):
        with tempfile.TemporaryDirectory() as folder:
            config = Config(output_dir=folder)
            image, _ = scene()
            result = CoverVision(config).process(image)
            packet = Frame(image, "2026-01-01T00:00:00+00:00", 0, 1, "fake")
            writer = DatasetWriter(config, "synthetic")
            with self.assertRaisesRegex(ValueError, "Not READY"):
                writer.save(packet, result, {})
            with self.assertRaisesRegex(ValueError, "Stale"):
                writer.save(packet, result, {}, review=True, frame_age_seconds=10)
            saved = writer.save(packet, result, {}, review=True)
            self.assertEqual(json.loads((saved / "metadata.json").read_text())["collection_status"], "review")

    def test_failed_write_has_no_completed_bundle(self):
        with tempfile.TemporaryDirectory() as folder:
            config = Config(output_dir=folder, stable_frames=1)
            image, _ = scene()
            result = CoverVision(config).process(image)
            writer = DatasetWriter(config, "synthetic")
            with patch("vision.opencv.dataset.write_image", side_effect=OSError("disk full")):
                with self.assertRaisesRegex(OSError, "disk full"):
                    writer.save(Frame(image, "UTC", 0, 1, "fake"), result, {})
            self.assertEqual(list((Path(folder) / "captures").iterdir()), [])

    def test_manifest_failure_retains_bundle_and_can_rebuild(self):
        with tempfile.TemporaryDirectory() as folder:
            config = Config(output_dir=folder, stable_frames=1)
            image, _ = scene()
            writer = DatasetWriter(config, "synthetic")
            (Path(folder) / "manifest.jsonl").mkdir()
            saved = writer.save(Frame(image, "UTC", 0, 1, "fake"), CoverVision(config).process(image), {})
            self.assertTrue((saved / "metadata.json").is_file())
            self.assertIn("manifest append failed", writer.manifest_warning)


class FakeCapture:
    def __init__(self, fail=False):
        self.fail, self.released, self.seq = fail, False, 0
    def open(self, *args):
        return True
    def set(self, *args):
        return True
    def get(self, *args):
        return 30
    def read(self):
        time.sleep(0.01)
        self.seq += 1
        return (False, None) if self.fail else (True, np.full((32, 32, 3), self.seq % 255, np.uint8))
    def release(self):
        self.released = True


class CameraTests(unittest.TestCase):
    def test_sequence_and_release(self):
        fake = FakeCapture()
        camera = CameraAdapter(Config(backend="dshow"), factory=lambda: fake).start()
        try:
            first, _ = wait_for_frame(camera, 1)
            time.sleep(0.04)
            second, status, _ = camera.capture()
            self.assertEqual(status, "LIVE")
            self.assertGreater(second.sequence, first.sequence)
            self.assertGreater(second.monotonic, first.monotonic)
        finally:
            camera.release()
        self.assertTrue(fake.released)
        self.assertIsNone(camera.capture()[0])

    def test_read_failure_clears_packet(self):
        fake = FakeCapture(fail=True)
        camera = CameraAdapter(Config(backend="dshow"), factory=lambda: fake).start()
        try:
            with self.assertRaises(RuntimeError):
                wait_for_frame(camera, 0.15)
            self.assertIsNone(camera.capture()[0])
        finally:
            camera.release()
        self.assertTrue(fake.released)


class ConfigTests(unittest.TestCase):
    def test_defaults_and_invalid(self):
        self.assertEqual(load_config().output_width, 630)
        for config in (Config(camera_index=-1), Config(stable_frames=0), Config(min_sharpness=float("nan")),
                       Config(output_height=630), Config(background_tolerance=0), Config(width=True)):
            with self.assertRaises(ValueError):
                config.validate()


class AppTests(unittest.TestCase):
    def test_save_uses_frame_after_keypress(self):
        image, _ = scene()

        class FakeCamera:
            def __init__(self):
                self.sequence = 0
                self.released = False
            def start(self):
                return self
            def capture(self):
                self.sequence += 1
                return Frame(image, datetime.now(timezone.utc).isoformat(), time.monotonic(),
                             self.sequence, "synthetic-ui-camera"), "LIVE", {"camera_index": 0}
            def release(self):
                self.released = True

        with tempfile.TemporaryDirectory() as folder:
            config = Config(output_dir=folder, stable_frames=1)
            fake = FakeCamera()
            with patch("software.desktop.cover_capture_app.load_config", return_value=config), \
                 patch("software.desktop.cover_capture_app.CameraAdapter", return_value=fake), \
                 patch("cv2.namedWindow"), patch("cv2.setMouseCallback"), \
                 patch("cv2.imshow"), patch("cv2.destroyAllWindows"), \
                 patch("cv2.getWindowProperty", return_value=1), \
                 patch("cv2.waitKey", side_effect=[ord("s"), ord("q")]):
                self.assertEqual(main(["--source-kind", "synthetic"]), 0)
            metadata = list((Path(folder) / "captures").glob("*/metadata.json"))
            self.assertEqual(len(metadata), 1)
            record = json.loads(metadata[0].read_text(encoding="utf-8"))
            self.assertEqual(record["capture_seq"], 2)
            self.assertEqual(record["source_kind"], "synthetic")
            self.assertTrue(fake.released)


if __name__ == "__main__":
    unittest.main()
