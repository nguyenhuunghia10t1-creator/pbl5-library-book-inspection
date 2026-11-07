"""Unicode display regressions; capture status/schema are not translated in data."""
import ctypes
from ctypes import wintypes
import sys
import unittest
from unittest.mock import patch

import numpy as np

from software.desktop import cover_capture_app as app
from software.desktop.ui_text import draw_text, _mask, ascii_fallback
from vision.opencv.pipeline import Result, QRResult
from vision.opencv.dataset import annotate


class VietnameseDisplayTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "win32", "Native Unicode renderer requires Windows GDI")
    def test_accents_are_real_glyphs_and_gdi_handles_are_released(self):
        accented = _mask("Độ sáng, ổn định, ảnh bìa", 18)
        plain = _mask("Do sang, on dinh, anh bia", 18)
        self.assertTrue(np.any(accented))
        self.assertFalse(accented.shape == plain.shape and np.array_equal(accented, plain))
        kernel = ctypes.WinDLL("kernel32")
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        user = ctypes.WinDLL("user32")
        user.GetGuiResources.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        user.GetGuiResources.restype = wintypes.DWORD
        handle = kernel.GetCurrentProcess()
        before = user.GetGuiResources(handle, 0)
        for i in range(300):
            _mask(f"Khung hình có dấu #{i}", 14)
        after = user.GetGuiResources(handle, 0)
        self.assertLessEqual(after, before + 2, "Per-label drawing must not leak GDI handles")
        self.assertLessEqual(_mask.cache_info().currsize, 256)

    def test_long_text_and_negative_coordinates_stay_inside_canvas(self):
        canvas = np.full((40, 160, 3), 25, np.uint8)
        draw_text(canvas, "Tiếng Việt có dấu " * 20, (-20, 23), .55)
        self.assertEqual(canvas.shape, (40, 160, 3))
        self.assertTrue(np.any(canvas != 25))
        unchanged = canvas.copy()
        draw_text(canvas, "", (0, 0))
        np.testing.assert_array_equal(canvas, unchanged)

    def test_screen_translates_qr_and_quality_without_mutating_result(self):
        result = Result("QUALITY_WARNING", qr=QRResult("INVALID_FORMAT"),
                        issues=["FOCUS_UNVERIFIED"])
        labels = []
        with patch.object(app, "text", side_effect=lambda canvas, value, *args: labels.append(str(value))):
            app.render(None, result, "STARTING_CAMERA", "", {})
        joined = " ".join(labels)
        self.assertIn("Sai định dạng mã", joined)
        self.assertIn("Chưa đủ chi tiết để xác minh độ nét", joined)
        self.assertNotIn("QUALITY_WARNING", joined)
        self.assertEqual(result.status, "QUALITY_WARNING")
        self.assertEqual(result.qr.status, "INVALID_FORMAT")
        self.assertEqual(result.issues, ["FOCUS_UNVERIFIED"])

    def test_saved_debug_annotation_keeps_technical_label_by_default(self):
        frame = np.zeros((80, 200, 3), np.uint8)
        result = Result("READY")
        self.assertTrue(np.any(annotate(frame, result)))
        self.assertFalse(np.any(annotate(frame, result, show_status=False)))
        self.assertFalse(np.any(frame))

    def test_non_windows_fallback_is_readable_vietnamese_without_accents(self):
        self.assertEqual(ascii_fallback("Độ sáng và độ nét"), "Do sang va do net")
        with patch("software.desktop.ui_text.sys.platform", "linux"), patch("software.desktop.ui_text.cv2.putText") as put:
            draw_text(np.zeros((30, 200, 3), np.uint8), "Độ sáng", (0, 20))
        self.assertEqual(put.call_args.args[1], "Do sang")


if __name__ == "__main__":
    unittest.main()
