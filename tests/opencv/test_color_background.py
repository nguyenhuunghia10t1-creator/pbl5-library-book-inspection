"""Synthetic color/background regression, not evidence of real-world accuracy."""
import unittest
import cv2
import numpy as np

from vision.opencv.config import Config, load_config
from vision.opencv.pipeline import CoverVision, order_quad, corner_motion
from vision.opencv.quality import assess_quality
from .color_fixtures import color_scene, matrix_cases


class ColorGeometryTests(unittest.TestCase):
    def assert_outer(self, result, expected, label):
        self.assertIsNotNone(result.corners, (label, result.status, result.method))
        self.assertIsNotNone(result.crop, (label, result.status))
        self.assertLess(corner_motion(result.corners, order_quad(expected)), 10, (label, result.corners, expected))
        self.assertEqual(result.crop.shape, (888, 630, 3))

    def test_color_background_matrix_automatic_and_calibrated(self):
        for label, options in matrix_cases():
            image, expected, bg = color_scene(**options)
            for calibrated in (False, True):
                with self.subTest(case=label, calibrated=calibrated):
                    vision = CoverVision(Config(processing_width=640, stable_frames=1))
                    if calibrated:
                        vision.calibrate(bg)
                    self.assert_outer(vision.process(image, decode=False), expected, (label, calibrated))

    def test_rectified_crop_against_ground_truth_warp(self):
        for options in ({}, {"color": (25, 30, 35), "perspective": True}, {"angle": 27}):
            with self.subTest(options=options):
                image, expected, _ = color_scene(**options)
                result = CoverVision(Config(stable_frames=1)).process(image, decode=False)
                self.assert_outer(result, expected, options)
                target = np.float32([[0, 0], [629, 0], [629, 887], [0, 887]])
                reference = cv2.warpPerspective(image, cv2.getPerspectiveTransform(order_quad(expected), target), (630, 888))
                # Compare printed content, excluding the warp boundary; catches a wrong crop extent.
                error = np.abs(result.crop[45:-45, 32:-32].astype(float) - reference[45:-45, 32:-32].astype(float)).mean()
                self.assertLess(error, 10, ("mean BGR pixel error", error))

    def test_inset_printed_border_is_not_outer_paper(self):
        image, expected, _ = color_scene(details=False, print_border=True)
        result = CoverVision(Config(stable_frames=1)).process(image, decode=False)
        self.assert_outer(result, expected, "inset border")

    def test_empty_background_without_calibration(self):
        for pattern in ("plain", "texture", "seams", "checker", "gradient"):
            with self.subTest(pattern=pattern):
                _, _, bg = color_scene(pattern=pattern, bg_color=(180, 190, 200))
                result = CoverVision(Config(processing_width=640)).process(bg, decode=False)
                self.assertEqual(result.status, "NO_COVER")
                self.assertIsNone(result.crop)

    def test_recalibrate_after_background_change(self):
        image, expected, bg = color_scene(pattern="texture", bg_color=(120, 140, 160))
        _, _, previous_bg = color_scene(bg_color=(240, 240, 240))
        vision = CoverVision(Config(processing_width=640, stable_frames=1))
        vision.calibrate(previous_bg)
        vision.process(image, decode=False)
        vision.calibrate(bg)
        self.assertIsNone(vision.previous)
        self.assertEqual(vision.stable, 0)
        self.assertEqual(vision.process(bg, decode=False).status, "NO_COVER")
        self.assert_outer(vision.process(image, decode=False), expected, "new background")

    def test_empty_background_after_b_and_exposure_shift(self):
        for pattern in ("plain", "texture", "seams", "checker", "gradient"):
            with self.subTest(pattern=pattern):
                _, _, bg = color_scene(pattern=pattern, bg_color=(180, 190, 200))
                vision = CoverVision(Config(processing_width=640))
                vision.calibrate(bg)
                shifted = np.uint8(np.clip(bg.astype(np.int16) + 12, 0, 255))
                self.assertEqual(vision.process(shifted, decode=False).status, "NO_COVER")

    def test_book_after_b_with_common_light_change(self):
        image, expected, bg = color_scene(pattern="texture", bg_color=(150, 170, 190))
        vision = CoverVision(Config(processing_width=640, stable_frames=1))
        vision.calibrate(bg)
        shifted = np.uint8(np.clip(image.astype(np.int16) - 15, 0, 255))
        self.assert_outer(vision.process(shifted, decode=False), expected, "exposure shift")

    def test_removal_does_not_keep_last_corners(self):
        image, expected, bg = color_scene()
        vision = CoverVision(Config(stable_frames=1))
        vision.process(image, decode=False)
        removed = vision.process(bg, decode=False)
        self.assertEqual(removed.status, "NO_COVER")
        self.assertIsNone(removed.crop)
        self.assertIsNone(vision.previous)
        self.assertEqual(vision.stable, 0)

    def test_no_observable_boundary_fails_safely(self):
        image, _, bg = color_scene(color=(240, 240, 240), bg_color=(240, 240, 240), details=False, print_border=False)
        for calibrated in (False, True):
            with self.subTest(calibrated=calibrated):
                vision = CoverVision(Config())
                if calibrated:
                    vision.calibrate(bg)
                result = vision.process(image, decode=False)
                self.assertEqual(result.status, "NO_COVER")
                self.assertIsNone(result.crop)

    def test_invisible_paper_boundary_does_not_use_printed_frame(self):
        image, _, bg = color_scene(color=(240, 240, 240), bg_color=(240, 240, 240))
        for calibrated in (False, True):
            with self.subTest(calibrated=calibrated):
                vision = CoverVision(Config(stable_frames=1))
                if calibrated:
                    vision.calibrate(bg)
                result = vision.process(image, decode=False)
                self.assertEqual(result.status, "NO_COVER")
                self.assertIsNone(result.crop)

    def test_bright_and_dark_covers_keep_qr_contract(self):
        for color in ((250, 250, 250), (25, 30, 35)):
            with self.subTest(color=color):
                image, expected, _ = color_scene(color=color)
                result = CoverVision(Config(stable_frames=1)).process(image)
                self.assert_outer(result, expected, "QR compatibility")
                self.assertEqual(result.qr.book_id, "PBL5-B04")
                self.assertEqual(result.status, "READY", result.issues)

    def test_legacy_config_and_new_threshold_validation(self):
        self.assertEqual(load_config().output_width, 630)
        for options in ({"edge_min_threshold": 0}, {"edge_noise_factor": float("nan")},
                        {"min_side_support": 1.2}, {"geometry_ring_pixels": True},
                        {"geometry_ring_pixels": 0}, {"max_clipped_fraction": 1},
                        {"min_detail_contrast": -1}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                Config(**options).validate()


class CoverQualityTests(unittest.TestCase):
    def test_plain_bright_is_unverified_focus_not_blur_or_bad_light(self):
        metrics, issues = assess_quality(np.full((400, 280), 250, np.uint8), Config())
        self.assertFalse(metrics["focus_measurable"])
        self.assertIn("FOCUS_UNVERIFIED", issues)
        self.assertNotIn("BLURRY", issues)
        self.assertNotIn("BAD_LIGHT", issues)
        self.assertTrue(metrics["brightness_outside_legacy_range"])

    def test_high_brightness_with_sharp_detail_is_not_blocked_by_mean(self):
        gray = np.full((400, 280), 250, np.uint8)
        cv2.putText(gray, "A6", (50, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.0, 40, 2)
        metrics, issues = assess_quality(gray, Config())
        self.assertGreater(metrics["brightness"], 235)
        self.assertTrue(metrics["focus_measurable"])
        self.assertNotIn("BLURRY", issues)
        self.assertNotIn("BAD_LIGHT", issues)

    def test_blurred_print_is_still_blocked(self):
        image, _, _ = color_scene()
        image = cv2.GaussianBlur(image, (35, 35), 10)
        result = CoverVision(Config(stable_frames=1)).process(image, decode=False)
        self.assertIn("BLURRY", result.issues)
        self.assertNotEqual(result.status, "READY")

    def test_blank_clipped_white_and_black_keep_quality_warning(self):
        for value in (0, 255):
            with self.subTest(value=value):
                metrics, issues = assess_quality(np.full((400, 280), value, np.uint8), Config())
                self.assertIn("BAD_LIGHT", issues)
                self.assertIn("FOCUS_UNVERIFIED", issues)
                self.assertGreaterEqual(max(metrics["clipped_high_fraction"], metrics["clipped_low_fraction"]), 0.98)

    def test_plain_cover_has_geometry_but_not_ready(self):
        image, expected, _ = color_scene(details=False, print_border=False)
        result = CoverVision(Config(stable_frames=1)).process(image, decode=False)
        self.assertIsNotNone(result.crop)
        self.assertLess(corner_motion(result.corners, order_quad(expected)), 10)
        self.assertEqual(result.status, "QUALITY_WARNING")
        self.assertIn("FOCUS_UNVERIFIED", result.issues)


if __name__ == "__main__":
    unittest.main()
