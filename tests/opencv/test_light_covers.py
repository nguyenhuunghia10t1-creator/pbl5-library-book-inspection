"""Synthetic low-contrast covers; no camera or defect-accuracy evidence."""
import unittest

import cv2
import numpy as np

from vision.opencv.config import Config
from vision.opencv.pipeline import CoverVision, corner_motion, order_quad
from tests.opencv.test_cover_capture import qr_image


PALE_COLORS = {"yellow": (225, 242, 242), "blue": (247, 237, 231),
               "white": (246, 246, 246), "equal_gray": (244, 232, 237)}


def light_scene(color, angle=0, perspective=False, printed=False, noise=0):
    background = np.full((600, 800, 3), 235, np.uint8)
    sheet = np.full((338, 240, 3), color, np.uint8)
    if printed:
        cv2.putText(sheet, "BOOK", (25, 55), cv2.FONT_HERSHEY_SIMPLEX, 1, (35, 35, 35), 2)
        sheet[226:314, 128:216] = qr_image(size=88)
    source = np.float32([[0, 0], [239, 0], [239, 337], [0, 337]])
    if perspective:
        corners = np.float32([[285, 115], [520, 130], [535, 474], [266, 460]])
    else:
        theta = np.deg2rad(angle)
        rotation = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
        corners = ((source - [119.5, 168.5]) @ rotation.T + [400, 300]).astype(np.float32)
    transform = cv2.getPerspectiveTransform(source, corners)
    # Replicate the sheet edge so interpolation cannot invent a black outline.
    warped = cv2.warpPerspective(sheet, transform, (800, 600), borderMode=cv2.BORDER_REPLICATE)
    mask = cv2.warpPerspective(np.full(sheet.shape[:2], 255, np.uint8), transform, (800, 600))
    frame = background.copy()
    frame[mask > 127] = warped[mask > 127]
    if noise:
        frame = np.clip(frame.astype(np.float32) + np.random.default_rng(42).normal(
            0, noise, frame.shape), 0, 255).astype(np.uint8)
    return frame, corners, background


class LightCoverTests(unittest.TestCase):
    def setUp(self):
        self.config = Config(stable_frames=1)

    def assert_outer_cover(self, frame, expected, vision=None):
        vision = vision or CoverVision(self.config)
        before = frame.copy()
        points, _, _ = vision.detect(frame)
        self.assertIsNotNone(points, "A faint outer boundary must not require a dark printed border")
        self.assertLess(corner_motion(order_quad(points), order_quad(expected)), 7)
        np.testing.assert_array_equal(frame, before, "Detection must preserve source pixels")
        return vision

    def test_pale_colors_without_calibration(self):
        for name, color in PALE_COLORS.items():
            for angle in (0, 27, 90):
                with self.subTest(color=name, angle=angle):
                    frame, corners, _ = light_scene(color, angle)
                    self.assert_outer_cover(frame, corners)

    def test_pale_colors_with_calibrated_background(self):
        for name, color in PALE_COLORS.items():
            with self.subTest(color=name):
                frame, corners, empty = light_scene(color, perspective=True)
                vision = CoverVision(self.config)
                vision.calibrate(empty)
                self.assert_outer_cover(frame, corners, vision)

    def test_equal_gray_chromatic_boundary(self):
        color = PALE_COLORS["equal_gray"]
        gray = int(cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_BGR2GRAY)[0, 0])
        self.assertLessEqual(abs(gray - 235), 1)
        frame, corners, _ = light_scene(color, perspective=True)
        self.assert_outer_cover(frame, corners)

    def test_text_and_qr_do_not_replace_outer_corners(self):
        for name in ("yellow", "blue", "white"):
            with self.subTest(color=name):
                frame, corners, _ = light_scene(PALE_COLORS[name], perspective=True, printed=True)
                vision = self.assert_outer_cover(frame, corners)
                result = vision.process(frame)
                self.assertIsNotNone(result.crop)
                self.assertEqual(result.crop.shape, (888, 630, 3))
                self.assertEqual(result.qr.book_id, "PBL5-B04")

    def test_small_sensor_noise_and_global_exposure_change(self):
        for name in ("yellow", "blue"):
            for gain in (0.8, 1.0):
                with self.subTest(color=name, gain=gain):
                    frame, corners, _ = light_scene(PALE_COLORS[name], angle=18, noise=1.2)
                    frame = np.clip(frame.astype(np.float32) * gain, 0, 255).astype(np.uint8)
                    self.assert_outer_cover(frame, corners)

    def test_dark_cover_still_detected(self):
        frame, corners, _ = light_scene((40, 55, 75), angle=27)
        self.assert_outer_cover(frame, corners)

    def test_light_cover_on_textured_background_with_and_without_calibration(self):
        y, x = np.indices((600, 800))
        grain = 234 + 3 * np.sin(x / 5) + 2 * np.sin(y / 13)
        background = np.repeat(grain[:, :, None], 3, axis=2).astype(np.uint8)
        for calibrated in (False, True):
            with self.subTest(calibrated=calibrated):
                frame, corners, _ = light_scene(PALE_COLORS["blue"], angle=18)
                inside = np.zeros(frame.shape[:2], np.uint8)
                cv2.fillConvexPoly(inside, corners.astype(np.int32), 255)
                textured = background.copy()
                textured[inside > 0] = frame[inside > 0]
                vision = CoverVision(self.config)
                if calibrated:
                    vision.calibrate(background)
                self.assert_outer_cover(textured, corners, vision)

    def test_empty_bright_and_noisy_backgrounds_do_not_make_a_cover(self):
        random = np.random.default_rng(7)
        for level in (40, 180, 235, 252):
            with self.subTest(level=level):
                blank = np.clip(level + random.normal(0, 2, (600, 800, 3)), 0, 255).astype(np.uint8)
                self.assertEqual(CoverVision(self.config).process(blank, decode=False).status, "NO_COVER")
        ramp = np.broadcast_to(np.linspace(180, 250, 800)[None, :, None], (600, 800, 3)).astype(np.uint8)
        self.assertEqual(CoverVision(self.config).process(ramp, decode=False).status, "NO_COVER")

    def test_stronger_sensor_noise_is_not_a_cover(self):
        frame = np.clip(235 + np.random.default_rng(9).normal(0, 10, (600, 800, 3)),
                        0, 255).astype(np.uint8)
        self.assertEqual(CoverVision(self.config).process(frame, decode=False).status, "NO_COVER")

    def test_nonrectangular_pale_objects_are_not_covers(self):
        for shape in ("ellipse", "triangle"):
            with self.subTest(shape=shape):
                frame = np.full((600, 800, 3), 235, np.uint8)
                if shape == "ellipse":
                    cv2.ellipse(frame, (400, 300), (120, 169), 0, 0, 360, PALE_COLORS["blue"], -1)
                else:
                    cv2.fillConvexPoly(frame, np.int32([[400, 100], [240, 469], [560, 469]]),
                                       PALE_COLORS["yellow"])
                self.assertEqual(CoverVision(self.config).process(frame, decode=False).status, "NO_COVER")

    def test_faint_cover_without_qr_is_not_ready(self):
        frame, _, _ = light_scene(PALE_COLORS["blue"])
        result = CoverVision(self.config).process(frame)
        self.assertIsNotNone(result.crop)
        self.assertNotEqual(result.status, "READY")
        self.assertIsNone(result.qr.book_id)

    def test_brightness_gate_remains_in_effect(self):
        frame, _, _ = light_scene((252, 252, 252))
        result = CoverVision(self.config).process(frame, decode=False)
        self.assertIsNotNone(result.crop)
        self.assertIn("BAD_LIGHT", result.issues)
        self.assertNotEqual(result.status, "READY")

    def test_two_faint_covers_remain_ambiguous(self):
        frame = np.full((600, 1100, 3), 235, np.uint8)
        frame[130:468, 100:340] = PALE_COLORS["yellow"]
        frame[130:468, 750:990] = PALE_COLORS["blue"]
        self.assertEqual(CoverVision(self.config).process(frame, decode=False).status, "MULTIPLE_COVERS")

    def test_clipped_faint_cover_is_not_accepted(self):
        frame, _, _ = light_scene(PALE_COLORS["blue"])
        shifted = cv2.warpAffine(frame, np.float32([[1, 0, -310], [0, 1, 0]]), (800, 600),
                                 borderMode=cv2.BORDER_REPLICATE)
        result = CoverVision(self.config).process(shifted, decode=False)
        self.assertIsNone(result.crop)
        self.assertIn(result.status, ("NO_COVER", "TOUCHING_FRAME"))


if __name__ == "__main__":
    unittest.main()
