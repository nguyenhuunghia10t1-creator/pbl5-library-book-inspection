"""Vietnamese UI text with native Windows Unicode rasterization, no extra dependency."""
import ctypes
from ctypes import wintypes
from functools import lru_cache
import sys
import unicodedata

import cv2
import numpy as np


def ascii_fallback(value):
    return "".join(c for c in unicodedata.normalize("NFD", value.replace("đ", "d").replace("Đ", "D"))
                   if unicodedata.category(c) != "Mn").encode("ascii", "replace").decode("ascii")


@lru_cache(maxsize=1)
def _gdi():
    g = ctypes.WinDLL("gdi32", use_last_error=True)
    signatures = {
        "CreateCompatibleDC": ([wintypes.HDC], wintypes.HDC),
        "DeleteDC": ([wintypes.HDC], wintypes.BOOL),
        "SelectObject": ([wintypes.HDC, wintypes.HANDLE], wintypes.HANDLE),
        "DeleteObject": ([wintypes.HANDLE], wintypes.BOOL),
        "CreateFontIndirectW": ([ctypes.c_void_p], wintypes.HANDLE),
        "GetTextExtentPoint32W": ([wintypes.HDC, wintypes.LPCWSTR, ctypes.c_int, ctypes.c_void_p], wintypes.BOOL),
        "CreateDIBSection": ([wintypes.HDC, ctypes.c_void_p, wintypes.UINT, ctypes.POINTER(ctypes.c_void_p), wintypes.HANDLE, wintypes.DWORD], wintypes.HANDLE),
        "SetTextColor": ([wintypes.HDC, wintypes.DWORD], wintypes.DWORD),
        "SetBkMode": ([wintypes.HDC, ctypes.c_int], ctypes.c_int),
        "TextOutW": ([wintypes.HDC, ctypes.c_int, ctypes.c_int, wintypes.LPCWSTR, ctypes.c_int], wintypes.BOOL),
        "GdiFlush": ([], wintypes.BOOL),
    }
    for name, (args, result) in signatures.items():
        function = getattr(g, name)
        function.argtypes, function.restype = args, result
    return g


class _Font(ctypes.Structure):
    _fields_ = [(name, wintypes.LONG) for name in ("height", "width", "escapement", "orientation", "weight")] + [
        (name, wintypes.BYTE) for name in ("italic", "underline", "strikeout", "charset", "out_precision", "clip_precision", "quality", "pitch")
    ] + [("face", wintypes.WCHAR * 32)]


class _BitmapInfo(ctypes.Structure):
    _fields_ = [("size", wintypes.DWORD), ("width", wintypes.LONG), ("height", wintypes.LONG),
                ("planes", wintypes.WORD), ("bits", wintypes.WORD), ("compression", wintypes.DWORD),
                ("image_size", wintypes.DWORD), ("xppm", wintypes.LONG), ("yppm", wintypes.LONG),
                ("used", wintypes.DWORD), ("important", wintypes.DWORD)]


@lru_cache(maxsize=256)
def _mask(value, pixels):
    """Return an antialiased mask; restore selected objects before freeing every handle."""
    g = _gdi()
    dc = g.CreateCompatibleDC(None)
    if not dc:
        raise ctypes.WinError(ctypes.get_last_error())
    font = bitmap = old_font = old_bitmap = None
    try:
        spec = _Font(height=-pixels, weight=400, charset=1, quality=4, face="Segoe UI")
        font = g.CreateFontIndirectW(ctypes.byref(spec))
        if not font:
            raise ctypes.WinError(ctypes.get_last_error())
        old_font = g.SelectObject(dc, font)
        extent = wintypes.SIZE()
        if not g.GetTextExtentPoint32W(dc, value, len(value), ctypes.byref(extent)):
            raise ctypes.WinError(ctypes.get_last_error())
        width, height = max(1, extent.cx + 4), max(1, extent.cy + 4)
        info = _BitmapInfo(size=ctypes.sizeof(_BitmapInfo), width=width, height=-height, planes=1, bits=32)
        address = ctypes.c_void_p()
        bitmap = g.CreateDIBSection(dc, ctypes.byref(info), 0, ctypes.byref(address), None, 0)
        if not bitmap or not address.value:
            raise ctypes.WinError(ctypes.get_last_error())
        old_bitmap = g.SelectObject(dc, bitmap)
        ctypes.memset(address, 0, width * height * 4)
        g.SetBkMode(dc, 1)  # TRANSPARENT, white text on the zeroed DIB.
        g.SetTextColor(dc, 0xFFFFFF)
        if not g.TextOutW(dc, 2, 2, value, len(value)):
            raise ctypes.WinError(ctypes.get_last_error())
        g.GdiFlush()
        data = (ctypes.c_ubyte * (width * height * 4)).from_address(address.value)
        return np.ctypeslib.as_array(data).reshape(height, width, 4)[:, :, 0].copy()
    finally:
        if old_bitmap:
            g.SelectObject(dc, old_bitmap)
        if old_font:
            g.SelectObject(dc, old_font)
        if bitmap:
            g.DeleteObject(bitmap)
        if font:
            g.DeleteObject(font)
        g.DeleteDC(dc)


def draw_text(canvas, value, pos, size=0.55, color=(210, 220, 230)):
    value = str(value)
    if not value:
        return
    x, baseline = pos
    if sys.platform != "win32":
        # The capture app targets Windows. Keep headless/non-Windows tools usable.
        cv2.putText(canvas, ascii_fallback(value), pos, cv2.FONT_HERSHEY_SIMPLEX, size, color, 1, cv2.LINE_AA)
        return
    pixels = max(10, round(30 * size))
    mask = _mask(value, pixels)
    available = max(0, canvas.shape[1] - x - 12)
    if mask.shape[1] > available:
        low, high = 0, len(value)
        while low < high:
            mid = (low + high + 1) // 2
            if _mask(value[:mid] + "…", pixels).shape[1] <= available:
                low = mid
            else:
                high = mid - 1
        mask = _mask(value[:low] + "…", pixels)
    top = baseline - mask.shape[0] + 4
    left, right = max(0, x), min(canvas.shape[1], x + mask.shape[1])
    upper, lower = max(0, top), min(canvas.shape[0], top + mask.shape[0])
    if right <= left or lower <= upper:
        return
    alpha = mask[upper-top:lower-top, left-x:right-x, None].astype(np.float32) / 255
    region = canvas[upper:lower, left:right]
    region[:] = (region * (1-alpha) + np.array(color, np.float32) * alpha).astype(np.uint8)
