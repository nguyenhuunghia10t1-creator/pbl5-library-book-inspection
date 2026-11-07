"""Geometry on a downscaled frame, perspective warp from untouched source pixels."""
from dataclasses import dataclass, field
import math
import re

import cv2
import numpy as np

from .config import Config
from .geometry import order_quad, quad_ratio, corner_motion, prepare_lab, detect_cover
from .quality import assess_quality


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
        self.detection_metrics = {}

    def reset_tracking(self):
        self.previous = None
        self.stable = 0

    def small_frame(self, frame):
        scale = min(1.0, self.config.processing_width / frame.shape[1])
        small = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        return small, np.array([frame.shape[1] / small.shape[1], frame.shape[0] / small.shape[0]], np.float32)

    def calibrate(self, frame):
        small, _ = self.small_frame(frame)
        self.background = prepare_lab(small)
        self.reset_tracking()

    def detect(self, frame):
        small, scale = self.small_frame(frame)
        previous = None if self.previous is None else self.previous / scale
        points, mask, method, self.detection_metrics = detect_cover(small, self.background, previous, self.config)
        return (None if points is None else points * scale), mask, method

    def process(self, frame, decode=True, flip=False):
        if frame is None or frame.size == 0 or frame.ndim != 3 or min(frame.shape[:2]) < 32:
            self.reset_tracking()
            return Result("EMPTY_FRAME")
        self.detection_metrics = {}
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
        quality, issues = assess_quality(gray, self.config)
        if min(lengths[0], lengths[2]) < self.config.min_source_short_edge:
            issues.append("TOO_SMALL")
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
                       **quality, **self.detection_metrics,
                       "source_short_edge_px": float(min(lengths[0], lengths[2])),
                       "homography_before_rotation": transform.tolist()},
                      issues, self.stable, method, rotation, basis)
