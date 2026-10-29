"""Geometry on a downscaled frame, perspective warp from untouched source pixels."""
from dataclasses import dataclass, field
import math
import re

import cv2
import numpy as np

from .config import Config


def order_quad(points):
    """Clockwise cyclic order, starting with the upper short edge (no sum/diff ties)."""
    p = np.asarray(points, np.float32).reshape(4, 2)
    if not np.isfinite(p).all() or len(np.unique(p, axis=0)) != 4:
        raise ValueError("Four different finite corners required")
    center = p.mean(axis=0)
    p = p[np.argsort(np.arctan2(p[:, 1] - center[1], p[:, 0] - center[0]))]
    if not cv2.isContourConvex(p) or abs(cv2.contourArea(p)) < 25:
        raise ValueError("Corners must form a convex quadrilateral")
    lengths = np.linalg.norm(np.roll(p, -1, axis=0) - p, axis=1)
    pair = 0 if lengths[0] + lengths[2] < lengths[1] + lengths[3] else 1
    start = min((pair, pair + 2), key=lambda i: tuple(((p[i] + p[(i + 1) % 4]) / 2)[::-1]))
    return np.roll(p, -start, axis=0)


def quad_ratio(p):
    d = np.linalg.norm(np.roll(p, -1, axis=0) - p, axis=1)
    return float((d[0] + d[2]) / (d[1] + d[3])), d


def corner_motion(a, b):
    """Compare cyclic shifts, including canonical edge changes near 90 degrees."""
    return min(float(np.max(np.linalg.norm(a - np.roll(b, k, axis=0), axis=1))) for k in range(4))


@dataclass
class QRResult:
    status: str = "UNREADABLE"
    book_id: str | None = None
    payloads: list = field(default_factory=list)
    points: list = field(default_factory=list)
    attempts: int = 0


def parse_payload(text):
    if re.fullmatch(r"PBL5-B[0-9]{2,6}", text):
        return "VALID_FORMAT", text
    if re.fullmatch(r"LIB1:[A-Za-z0-9][A-Za-z0-9_-]{0,63}", text):
        return "VALID_FORMAT", text.split(":", 1)[1]
    return ("INVALID_FORMAT" if text.startswith(("PBL5-", "LIB1:")) else "INVALID_NAMESPACE"), None


class QRReader:
    def __init__(self):
        self.detector = cv2.QRCodeDetector()

    def read(self, crop):
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        variants = (gray, cv2.createCLAHE(2.0, (8, 8)).apply(gray))
        last = QRResult()
        for attempt, image in enumerate(variants, 1):
            try:
                _, texts, points, _ = self.detector.detectAndDecodeMulti(image)
                count = 0 if points is None else len(points)
                if count > 1:
                    return QRResult("AMBIGUOUS", payloads=list(texts), points=points.tolist(), attempts=attempt)
                if not any(texts):
                    text, single_points, _ = self.detector.detectAndDecode(image)
                    if text:
                        texts = (text,)
                        points = single_points
                decoded = [s for s in texts if s]
                if decoded:
                    status, book_id = parse_payload(decoded[0])
                    return QRResult(status, book_id, decoded,
                                    [] if points is None else points.tolist(), attempt)
                last.attempts = attempt
            except (cv2.error, UnicodeDecodeError):
                last = QRResult("DECODE_ERROR", attempts=attempt)
        return last


@dataclass
class Result:
    status: str
    corners: np.ndarray | None = None
    crop: np.ndarray | None = None
    mask: np.ndarray | None = None
    qr: QRResult = field(default_factory=QRResult)
    metrics: dict = field(default_factory=dict)
    issues: list = field(default_factory=list)
    stable_count: int = 0
    method: str = "auto"
    rotation: int = 0
    orientation_basis: str = "geometry_only"


class CoverVision:
    def __init__(self, config: Config):
        self.config = config
        self.background = None
        self.previous = None
        self.stable = 0
        self.reader = QRReader()
        self.manual_points = None

    def reset_tracking(self):
        self.previous = None
        self.stable = 0

    def small_frame(self, frame):
        scale = min(1.0, self.config.processing_width / frame.shape[1])
        small = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        return small, np.array([frame.shape[1] / small.shape[1], frame.shape[0] / small.shape[0]], np.float32)

    def calibrate(self, frame):
        small, _ = self.small_frame(frame)
        self.background = cv2.cvtColor(cv2.GaussianBlur(small, (7, 7), 0), cv2.COLOR_BGR2LAB).astype(np.float32)
        self.reset_tracking()

    def detect(self, frame):
        small, scale = self.small_frame(frame)
        h, w = small.shape[:2]
        smooth = cv2.GaussianBlur(small, (5, 5), 0)
        lab = cv2.cvtColor(smooth, cv2.COLOR_BGR2LAB).astype(np.float32)
        if self.background is not None and self.background.shape == lab.shape:
            bg = self.background
        else:
            border = np.concatenate((lab[:8].reshape(-1, 3), lab[-8:].reshape(-1, 3),
                                     lab[:, :8].reshape(-1, 3), lab[:, -8:].reshape(-1, 3)))
            bg = np.median(border, axis=0)
        delta = lab - bg
        distance = np.sqrt(0.45 * delta[:, :, 0] ** 2 + delta[:, :, 1] ** 2 + delta[:, :, 2] ** 2)
        mask = np.uint8(distance > self.config.background_tolerance) * 255
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        edges = cv2.Canny(cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY), 45, 130)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        candidates = []
        for source, binary in (("background", mask), ("edges", edges)):
            contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:35]:
                area = cv2.contourArea(contour)
                if not self.config.min_area_fraction <= area / (w * h) <= self.config.max_area_fraction:
                    continue
                perimeter = cv2.arcLength(contour, True)
                for epsilon in (0.015, 0.025, 0.04):
                    approx = cv2.approxPolyDP(contour, epsilon * perimeter, True)
                    if len(approx) != 4 or not cv2.isContourConvex(approx):
                        continue
                    p = order_quad(approx)
                    ratio, _ = quad_ratio(p)
                    relative_error = abs(ratio / (105 / 148) - 1)
                    coverage = area / max(1, cv2.contourArea(p))
                    if relative_error > self.config.aspect_tolerance or not 0.80 <= coverage <= 1.15:
                        continue
                    score = area * (1 - relative_error * 0.5)
                    candidates.append((score, p, source))
                    break
        if not candidates:
            return None, mask, "auto"
        candidates.sort(key=lambda c: c[0], reverse=True)
        best = candidates[0]
        for other in candidates[1:]:
            overlap, _ = cv2.intersectConvexConvex(best[1], other[1])
            smaller = min(cv2.contourArea(best[1]), cv2.contourArea(other[1]))
            if overlap / max(smaller, 1) < 0.20 and other[0] > best[0] * 0.45:
                return None, mask, "multiple"
        return best[1] * scale, mask, best[2]

    def process(self, frame, decode=True, flip=False):
        if frame is None or frame.size == 0 or frame.ndim != 3 or min(frame.shape[:2]) < 32:
            self.reset_tracking()
            return Result("EMPTY_FRAME")
        points, mask, method = self.detect(frame) if self.manual_points is None else (
            order_quad(self.manual_points), None, "manual")
        if points is None:
            self.reset_tracking()
            return Result("MULTIPLE_COVERS" if method == "multiple" else "NO_COVER", mask=mask)
        h, w = frame.shape[:2]
        margin = max(4, min(h, w) * 0.008)
        if np.any(points[:, 0] < margin) or np.any(points[:, 0] >= w - margin) or \
                np.any(points[:, 1] < margin) or np.any(points[:, 1] >= h - margin):
            self.reset_tracking()
            return Result("TOUCHING_FRAME", points, mask=mask, method=method)
        ratio, lengths = quad_ratio(points)
        angle = math.degrees(math.atan2(float(points[1, 1] - points[0, 1]),
                                        float(points[1, 0] - points[0, 0])))
        ow, oh = self.config.output_width, self.config.output_height
        target = np.float32([[0, 0], [ow - 1, 0], [ow - 1, oh - 1], [0, oh - 1]])
        transform = cv2.getPerspectiveTransform(points.astype(np.float32), target)
        crop = cv2.warpPerspective(frame, transform, (ow, oh), flags=cv2.INTER_LINEAR)
        native_width = max(16, min(ow, int(min(lengths[0], lengths[2]))))
        native = cv2.resize(crop, (native_width, round(native_width * oh / ow)), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(native, cv2.COLOR_BGR2GRAY)
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        brightness = float(gray.mean())
        issues = []
        if min(lengths[0], lengths[2]) < self.config.min_source_short_edge:
            issues.append("TOO_SMALL")
        if sharpness < self.config.min_sharpness:
            issues.append("BLURRY")
        if not self.config.min_brightness <= brightness <= self.config.max_brightness:
            issues.append("BAD_LIGHT")
        if abs(ratio / (105 / 148) - 1) > self.config.aspect_tolerance:
            issues.append("BAD_ASPECT")
        if self.previous is not None and corner_motion(points, self.previous) <= self.config.stable_motion_pixels:
            self.stable += 1
        else:
            self.stable = 1
        self.previous = points.copy()
        qr = self.reader.read(crop) if decode else QRResult("PENDING")
        rotation, basis = 0, "geometry_only"
        if self.config.orient_by_qr and qr.status == "VALID_FORMAT" and qr.points:
            qp = np.array(qr.points).reshape(-1, 4, 2)[0]
            direction = qp[1] - qp[0]
            if abs(direction[0]) > abs(direction[1]):
                basis = "qr_assumed_aligned_with_cover"
                if direction[0] < 0:
                    rotation = 180
        if flip:
            rotation = (rotation + 180) % 360
            basis += "+manual_flip"
        if rotation:
            crop = cv2.rotate(crop, cv2.ROTATE_180)
            qr.points = (np.array([ow - 1, oh - 1]) - np.array(qr.points)).tolist() if qr.points else []
        status = "QUALITY_WARNING" if issues else (
            "MOVING" if self.stable < self.config.stable_frames else (
                "READY" if qr.status == "VALID_FORMAT" else "QR_" + qr.status))
        return Result(status, points, crop, mask, qr,
                      {"center_px": points.mean(axis=0).tolist(), "angle_deg": angle,
                       "aspect_ratio": ratio, "area_px": float(cv2.contourArea(points)),
                       "sharpness": sharpness, "brightness": brightness,
                       "source_short_edge_px": float(min(lengths[0], lengths[2])),
                       "homography_before_rotation": transform.tolist()},
                      issues, self.stable, method, rotation, basis)
