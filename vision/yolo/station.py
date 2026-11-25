"""Inspect one fresh, stable cover per request. A pilot can run without an ESP32."""

from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import threading
import time
import zlib

import cv2
import numpy as np

from software.inspection.settings import decide_prediction, station_defaults
from vision.opencv.camera import CameraAdapter
from vision.opencv.config import ROOT, load_config
from vision.opencv.pipeline import CoverVision

DATA = ROOT / "data/local/station"


@dataclass
class Reading:
    label: str
    confidence: float
    verdict: str
    reason: str
    image: bytes
    raw: bytes
    model_hash: str
    inference_ms: float | None = None


def jpeg(frame):
    ok, data = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
    if not ok:
        raise ValueError("JPEG_ENCODE")
    return data.tobytes()


def square_cover(crop, size):
    """Preserve the edges and aspect ratio through the classifier's square transform."""
    height, width = crop.shape[:2]
    side = max(height, width)
    canvas = np.full((side, side, 3), 114, dtype=np.uint8)
    y, x = (side - height) // 2, (side - width) // 2
    canvas[y : y + height, x : x + width] = crop
    return cv2.resize(canvas, (size, size), interpolation=cv2.INTER_AREA)


class Classifier:
    def __init__(self, cfg):
        for key in ("YOLO_CONFIG_DIR", "MPLCONFIGDIR", "TORCH_HOME"):
            os.environ.setdefault(key, str(DATA / "runtime" / key.lower()))
        os.environ["YOLO_OFFLINE"] = "true"
        os.environ["YOLO_AUTOINSTALL"] = "false"
        from ultralytics import YOLO
        import torch

        torch.set_num_threads(4)
        path = Path(os.environ.get("PBL5_MODEL", str(ROOT / cfg["model"])))
        with path.open("rb") as stream:
            self.checksum = hashlib.file_digest(stream, "sha256").hexdigest()
        self.model = YOLO(str(path))
        self.mapping = cfg["classes"]
        if (
            self.model.task != "classify"
            or len(self.model.names) != len(self.mapping)
            or set(self.model.names.values()) != set(self.mapping)
            or set(self.mapping.values()) != {"OK", "NG"}
        ):
            raise ValueError("MODEL_CLASS_MAPPING")
        self.size = cfg["image_size"]

    def predict(self, image):
        probs = self.model.predict(image, device="cpu", imgsz=self.size, verbose=False)[
            0
        ].probs
        if probs is None:
            raise ValueError("MODEL_NO_PROBABILITIES")
        label = self.model.names[probs.top1]
        confidence = float(probs.top1conf)
        if not math.isfinite(confidence) or not 0 <= confidence <= 1:
            raise ValueError("MODEL_BAD_PROBABILITY")
        return label, confidence


class StationVision:
    def __init__(self, cfg, *, camera_test=False):
        self.cfg = cfg
        self.camera_test = camera_test
        self.direct_routing = False
        self.folder = DATA
        self.settings_error = ""
        self.last_inspection_issue = None
        self.last_camera_issue = None
        self.classifier = self.camera = self.background = self.thresholds = None
        self.error = ""
        self.latest = None
        self.live_jpg = b""
        self.changed_at = 0.0
        self.frame_lock = threading.Lock()
        self.work = threading.Lock()
        self.closed = threading.Event()
        self.worker = threading.Thread(
            target=self._run, daemon=True, name="station-vision"
        )
        self.geometry = load_config()
        self.geometry.backend = "msmf"
        self.geometry.width, self.geometry.height = 640, 480

    def start(self):
        self.worker.start()

    def apply_settings(self, values):
        self.cfg.update(values)
        for field, value in values.items():
            if hasattr(self.geometry, field):
                setattr(self.geometry, field, value)

    def provenance(self):
        if not self.classifier or self.background is None:
            return None
        geometry = self.geometry.to_dict()
        for key in ("camera_index", "output_dir", "qr_interval_seconds", "orient_by_qr"):
            geometry.pop(key)
        return {
            "schema": 1,
            "sha256": self.classifier.checksum,
            "classes": self.classifier.mapping,
            "image_size": self.classifier.size,
            "geometry": geometry,
            "background": hashlib.sha256(self.background.tobytes()).hexdigest(),
            "background_shape": list(self.background.shape),
            "camera_name": self.cfg["camera_name"],
            "settings": station_defaults(self.cfg, self.geometry),
        }

    def provenance_key(self):
        provenance = self.provenance()
        if provenance is None:
            return None
        encoded = json.dumps(provenance, sort_keys=True, separators=(",", ":")).encode("utf8")
        return hashlib.sha256(encoded).hexdigest()

    @property
    def background_path(self):
        name = self.cfg["camera_name"]
        if name == "DroidCam Video":
            return self.folder / "empty.png"
        camera_id = hashlib.sha256(name.encode("utf8")).hexdigest()[:16]
        return self.folder / f"empty-{camera_id}.png"

    def _load_station_profile(self):
        from software.inspection.reference import REFERENCE_PATH, REFERENCE_SHA256

        self.thresholds = None
        self.classifier = Classifier(self.cfg)
        bg = self.background_path
        self.background = cv2.imread(str(bg)) if bg.is_file() else None
        calibration = self.folder / "thresholds.json"
        if not calibration.is_file() or self.settings_error:
            return
        try:
            profile = json.loads(calibration.read_text(encoding="utf8"))
            values = profile.get("thresholds")
            reference = profile.get("reference")
            if not (
                self.background is not None
                and profile.get("provenance") == self.provenance()
                and isinstance(reference, dict)
                and reference.get("sha256") == REFERENCE_SHA256
                and reference.get("book") == "IMG_7"
                and reference.get("truth") == "NG"
                and isinstance(values, dict)
                and set(values) == {"OK", "NG"}
                and all(type(values[k]) in (int, float)
                        and self.cfg["min_confidence"][k] <= values[k] <= 1 for k in values)
            ):
                return
            confidence = reference.get("confidence")
            if type(confidence) not in (int, float) or not 0 <= confidence <= 1:
                return
            route = self.classifier.mapping[reference["label"]]
            decision = decide_prediction(route, confidence, values, self.cfg["uncertain_policy"])
            if (
                decision in ("HOLD", "NG")
                and decision == reference.get("decision")
                and hashlib.sha256(REFERENCE_PATH.read_bytes()).hexdigest() == REFERENCE_SHA256
            ):
                self.thresholds = values
        except (OSError, ValueError, AttributeError, KeyError, TypeError):
            pass

    def _run(self):
        try:
            from cv2_enumerate_cameras import enumerate_cameras

            if not self.camera_test:
                self._load_station_profile()
            while not self.closed.is_set():
                devices = [
                    d
                    for d in enumerate_cameras(cv2.CAP_MSMF)
                    if d.name == self.cfg["camera_name"]
                ]
                if len(devices) != 1:
                    self.error = (
                        "Không tìm được duy nhất camera " + self.cfg["camera_name"]
                    )
                    self.closed.wait(2)
                    continue
                self.geometry.camera_index = devices[0].index
                self.camera = CameraAdapter(self.geometry).start()
                self._read_camera()
                self.camera.release()
                self.camera = None
                self.closed.wait(1)
        except Exception as exc:
            self.error = str(exc)
        finally:
            if self.camera:
                self.camera.release()
            with self.frame_lock:
                self.latest = None

    def _read_camera(self):
        previous, previous_key = None, None
        changed = 0.0
        while not self.closed.wait(1 / 60):
            packet, status, _ = self.camera.capture()
            if packet is None:
                with self.frame_lock:
                    self.latest = None
                self.error = status
                if not self.camera.thread.is_alive():
                    return
                continue
            key = (packet.camera_session_id, packet.sequence)
            if key == previous_key:
                continue
            previous_key = key
            fingerprint = zlib.crc32(memoryview(packet.image))
            if fingerprint != previous:
                # Require genuine content change, including on first opening the camera.
                if previous is not None:
                    changed = packet.monotonic
                previous = fingerprint
            preview = jpeg(packet.image)
            with self.frame_lock:
                self.latest, self.changed_at, self.live_jpg = packet, changed, preview
            self.error = ""

    def camera_status(self):
        with self.frame_lock:
            return self._frame_issue(self.latest, self.changed_at)

    @staticmethod
    def issue(code, message, measured, limit, remedy):
        return {"code": code, "message": message, "measured": measured,
                "limit": limit, "remedy": remedy}

    def diagnostics_status(self):
        return {"camera": self.last_camera_issue, "inspection": self.last_inspection_issue}

    def _frame_issue(self, packet, changed):
        now = time.monotonic()
        age = now - packet.monotonic if packet else None
        if age is None or age > self.cfg["frame_age_s"]:
            message = self.error or "Waiting for a fresh camera frame"
            self.last_camera_issue = self.issue(
                "FRAME_STALE", message, age, self.cfg["frame_age_s"],
                "Reconnect the camera and confirm a changing preview.")
            return message
        still = now - changed if changed else None
        if still is None or still > self.cfg["frozen_s"]:
            message = "Camera is repeating a frozen frame"
            self.last_camera_issue = self.issue(
                "FRAME_FROZEN", message, still, self.cfg["frozen_s"],
                "Move a hand in front of the camera and check the live preview.")
            return message
        self.last_camera_issue = None
        return ""

    def _cover_issue(self, result):
        metrics = result.metrics
        if result.issues:
            issue = result.issues[0]
            checks = {
                "TOO_SMALL": ("source_short_edge_px", self.geometry.min_source_short_edge,
                              "Move the camera closer or center the book."),
                "BLURRY": ("sharpness", self.geometry.min_sharpness,
                           "Refocus the camera and secure the mount."),
                "BAD_LIGHT": ("brightness", [self.geometry.min_brightness, self.geometry.max_brightness],
                              "Adjust lighting and avoid glare."),
                "BAD_ASPECT": ("aspect_ratio", self.geometry.aspect_tolerance,
                               "Align the camera above the cover and expose all four edges."),
            }
            if issue in checks:
                key, limit, remedy = checks[issue]
                measured = metrics.get(key)
                if issue == "BAD_ASPECT" and measured is not None:
                    measured = abs(measured / (105 / 148) - 1)
                return self.issue(issue, issue.replace("_", " ").title(), measured, limit, remedy)
        if result.status == "MOVING":
            return self.issue("COVER_MOVING", "Cover has not stabilized", result.stable_count,
                              self.geometry.stable_frames, "Wait for the belt and cover to stop.")
        return self.issue(result.status, "A full cover could not be isolated", None, None,
                          "Center a single book and keep all four edges visible.")

    def classify_snapshot(self):
        with self.work:
            with self.frame_lock:
                packet = self.latest
                if issue := self._frame_issue(packet, self.changed_at):
                    raise ValueError(issue)
                # CameraAdapter publishes a new array for each frame.
                frame = packet.image
            if self.classifier is None:
                self.classifier = Classifier(self.cfg.get("camera_test_model", self.cfg))
            label, confidence = self.classifier.predict(square_cover(frame, self.classifier.size))
            return self.classifier.mapping[label], label, confidence, jpeg(frame)

    def reason(self):
        if self.settings_error:
            return self.settings_error
        if not self.classifier:
            return self.error or "Đang tải model"
        if issue := self.camera_status():
            return issue
        if self.direct_routing:
            return ""
        if self.background is None:
            return "Cần lưu ảnh băng tải trống"
        if not self.thresholds:
            return "Cần hiệu chỉnh ngưỡng AI bằng sách đã biết nhãn"
        return ""

    def calibrate_background(self):
        with self.work:
            if issue := self.camera_status():
                raise ValueError(issue)
            with self.frame_lock:
                if self.latest is None:
                    raise ValueError("Mất camera khi lấy nền trống")
                frame = self.latest.image.copy()
            self.folder.mkdir(parents=True, exist_ok=True)
            temporary = self.folder / "empty-new.png"
            if not cv2.imwrite(str(temporary), frame):
                raise OSError("Không lưu được nền trống")
            temporary.replace(self.background_path)
            self.background = frame
            self.thresholds = None

    def _cover_crop(self, packet, geometry, baseline):
        if packet.image.shape != baseline.shape:
            reason = "Camera resolution changed after baseline capture"
            self.last_inspection_issue = self.issue(
                "FRAME_SIZE_CHANGED", reason, list(packet.image.shape[:2]),
                list(baseline.shape[:2]), "Restore camera resolution and recapture the empty belt.")
            raise ValueError(reason)
        result = geometry.process(packet.image, decode=False)
        if result.status != "QR_PENDING":
            self.last_inspection_issue = self._cover_issue(result)
            return None
        # Reject border-only contours already present on the empty belt.
        h, w = result.mask.shape
        scale = np.array([w / packet.image.shape[1], h / packet.image.shape[0]])
        polygon = np.zeros_like(result.mask)
        cv2.fillConvexPoly(polygon, np.int32(result.corners * scale), 255)
        foreground = cv2.countNonZero(cv2.bitwise_and(polygon, result.mask))
        fraction = foreground / max(1, cv2.countNonZero(polygon))
        minimum = self.cfg.get("min_foreground_fraction", 0.45)
        if fraction < minimum:
            reason = "Cover does not separate from the empty belt"
            self.last_inspection_issue = self.issue(
                "WEAK_FOREGROUND", reason, fraction, minimum,
                "Check lighting and recapture the empty belt without a book.")
            return None
        return result.crop

    def inspect(self, stopped_at, cancelled, *, direct=False):
        with self.work:
            self.last_inspection_issue = None
            deadline = stopped_at + self.cfg["inspection_s"]
            geometry = None
            baseline = self.background
            if not direct:
                if baseline is None:
                    raise ValueError("Chưa hiệu chuẩn nền")
                geometry = CoverVision(self.geometry)
                geometry.calibrate(baseline)
            reason = "Waiting for a stable cover"
            previous = None
            with self.frame_lock:
                session = self.latest.camera_session_id if self.latest else None
            while time.monotonic() < deadline and not cancelled.wait(0.025):
                if issue := self.camera_status():
                    self.last_inspection_issue = self.last_camera_issue
                    raise ValueError(issue)
                with self.frame_lock:
                    packet = self.latest
                if not packet or packet.camera_session_id != session:
                    reason = "Camera session changed during inspection"
                    self.last_inspection_issue = self.issue(
                        "CAMERA_SESSION", reason, None, None, "Reconnect the camera and retry.")
                    raise ValueError(reason)
                if (
                    not packet
                    or packet.monotonic < stopped_at + self.cfg["stabilize_s"]
                    or packet.sequence == previous
                ):
                    continue
                previous = packet.sequence
                crop = packet.image
                if geometry is not None:
                    crop = self._cover_crop(packet, geometry, baseline)
                    if crop is None:
                        reason = self.last_inspection_issue["message"]
                        continue
                image = square_cover(crop, self.classifier.size)
                try:
                    started = time.perf_counter()
                    label, confidence = self.classifier.predict(image)
                    inference_ms = (time.perf_counter() - started) * 1000
                    route = self.classifier.mapping[label]
                    if not math.isfinite(confidence) or not 0 <= confidence <= 1:
                        raise ValueError("Invalid model confidence")
                except Exception:
                    self.last_inspection_issue = self.issue(
                        "MODEL_ERROR", "Classification failed", None, None,
                        "Check the configured weights and class mapping.")
                    raise
                if cancelled.is_set() or time.monotonic() >= deadline:
                    reason = "Inspection expired or was cancelled"
                    self.last_inspection_issue = self.issue(
                        "INSPECTION_EXPIRED", reason, time.monotonic() - stopped_at,
                        self.cfg["inspection_s"], "Check camera stability and inference speed.")
                    raise ValueError(reason)
                if issue := self.camera_status():
                    self.last_inspection_issue = self.last_camera_issue
                    raise ValueError(issue)
                with self.frame_lock:
                    if self.latest is None or self.latest.camera_session_id != session:
                        reason = "Camera session changed during inference"
                        self.last_inspection_issue = self.issue(
                            "CAMERA_SESSION", reason, None, None, "Reconnect the camera and retry.")
                        raise ValueError(reason)
                reason = ""
                self.last_inspection_issue = None
                verdict = route
                if not direct:
                    threshold = self.thresholds[route] if self.thresholds else None
                    verdict = decide_prediction(route, confidence, self.thresholds,
                                                self.cfg.get("uncertain_policy", "hold"))
                    if threshold is None or confidence < threshold:
                        reason = "Model confidence is below the validated threshold" if threshold is not None else "No validated threshold profile"
                        self.last_inspection_issue = self.issue(
                            "LOW_CONFIDENCE" if threshold is not None else "UNCALIBRATED",
                            reason, confidence, threshold, "Use known books to validate the thresholds.")
                return Reading(
                    label,
                    confidence,
                    verdict,
                    reason,
                    jpeg(image),
                    jpeg(packet.image),
                    self.classifier.checksum, inference_ms,
                )
            if self.last_inspection_issue is None:
                self.last_inspection_issue = self.issue(
                    "INSPECTION_EXPIRED", reason, time.monotonic() - stopped_at,
                    self.cfg["inspection_s"], "Check frame timing and whether the book is stable.")
            raise ValueError(reason)

    def close(self):
        self.closed.set()
        self.worker.join(timeout=3)
