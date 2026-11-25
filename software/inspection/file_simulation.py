"""Decode uploaded photos and classify them without opening a camera."""

from dataclasses import dataclass
import hashlib
from io import BytesIO
import time
import threading


MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 12_000_000


@dataclass(frozen=True)
class Decision:
    label: str
    confidence: float | None
    verdict: str
    reason: str = ""
    image: bytes = b""
    raw: bytes = b""
    model_hash: str | None = None
    diagnostic: dict | None = None
    inference_ms: float | None = None


@dataclass(frozen=True)
class Photo:
    frame: object
    preview: bytes
    version: str | None = None


def decode_photo(data):
    if not data or len(data) > MAX_IMAGE_BYTES:
        raise ValueError("Upload a JPEG or PNG no larger than 10 MiB.")

    import cv2
    import numpy as np
    from PIL import Image
    from vision.yolo.station import jpeg

    try:
        with Image.open(BytesIO(data), formats=("JPEG", "PNG")) as image:
            if image.width * image.height > MAX_IMAGE_PIXELS or getattr(image, "is_animated", False):
                raise ValueError("Upload one image with at most 12 megapixels.")
    except (OSError, Image.DecompressionBombError) as exc:
        raise ValueError("The file is not a readable JPEG or PNG.") from exc
    frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("The file is not a readable JPEG or PNG.")
    return Photo(frame, jpeg(frame), hashlib.sha256(data).hexdigest())


def photo_quality(frame, cfg):
    import cv2

    short_edge = min(frame.shape[:2])
    minimum_edge = cfg["min_source_short_edge"]
    if short_edge < minimum_edge:
        return dict(code="TOO_SMALL", message=f"Cover is too small ({short_edge} px on the short edge).",
                    measured=short_edge, limit=minimum_edge, remedy="Choose a larger cover image.")
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brightness = float(gray.mean())
    low, high = cfg["min_brightness"], cfg["max_brightness"]
    if not low <= brightness <= high:
        return dict(code="BAD_LIGHT", message=f"Cover brightness is {brightness:.1f} (required {low}–{high}).",
                    measured=brightness, limit=[low, high], remedy="Use even lighting and avoid glare.")
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    minimum_sharpness = cfg["min_sharpness"]
    if sharpness < minimum_sharpness:
        return dict(code="BLURRY", message=f"Cover is blurred or blank (sharpness {sharpness:.1f}, minimum {minimum_sharpness}).",
                    measured=sharpness, limit=minimum_sharpness, remedy="Use a sharp photo with the full cover visible.")
    return None


class FileClassifier:
    def __init__(self, cfg):
        self.cfg = cfg
        self.classifier = None
        self.load_error = ""
        self.lock = threading.Lock()

    def prepare(self):
        # Model loading may be slower than a capture's decision window.
        with self.lock:
            if self.classifier is not None:
                return
            try:
                from vision.yolo.station import Classifier

                self.classifier = Classifier(self.cfg)
                self.load_error = ""
            except Exception as exc:
                self.load_error = str(exc) or type(exc).__name__

    def inspect(self, photo):
        if issue := photo_quality(photo.frame, self.cfg):
            return Decision("Image file", None, "HOLD", issue["message"], raw=photo.preview, diagnostic=issue)
        if not self.lock.acquire(blocking=False):
            raise ValueError("A previous image prediction is still running.")
        try:
            from vision.yolo.station import jpeg, square_cover

            if self.classifier is None:
                suffix = f" {self.load_error}" if self.load_error else ""
                raise ValueError(f"The image classifier is unavailable.{suffix}")
            model = self.classifier
            image = square_cover(photo.frame, model.size)
            started = time.perf_counter()
            label, confidence = model.predict(image)
            inference_ms = (time.perf_counter() - started) * 1000
            route = model.mapping[label]
            from software.inspection.settings import decide_prediction

            verdict = decide_prediction(
                route, confidence, self.cfg["min_confidence"],
                self.cfg.get("uncertain_policy", "hold"),
            )
            reason = ""
            issue = None
            if confidence < self.cfg["min_confidence"][route]:
                reason = "Prediction is below the simulation confidence floor."
                issue = dict(code="LOW_CONFIDENCE", message=reason, measured=confidence,
                             limit=self.cfg["min_confidence"][route], remedy="Check the photo and classifier with known books.")
            return Decision(
                label, confidence, verdict, reason, jpeg(image), photo.preview, model.checksum, issue, inference_ms,
            )
        finally:
            self.lock.release()
