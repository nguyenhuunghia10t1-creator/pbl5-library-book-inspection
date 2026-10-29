"""Latest-frame camera reader. Driver calls never run on the UI thread."""
from dataclasses import dataclass
from datetime import datetime, timezone
import logging
import math
import threading
import time
import uuid

import cv2

logger = logging.getLogger("cover_capture.camera")


@dataclass
class Frame:
    image: object
    timestamp_utc: str
    monotonic: float
    sequence: int
    camera_session_id: str


class CameraAdapter:
    def __init__(self, config, factory=cv2.VideoCapture):
        self.config = config
        self.factory = factory
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self.latest = None
        self.status = "STARTING_CAMERA"
        self.properties = {}
        self.thread = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return self
        self.stop.clear()
        self.thread = threading.Thread(target=self._run, daemon=True, name="camera-reader")
        self.thread.start()
        return self

    def _invalidate(self, status):
        with self.lock:
            self.latest = None
            self.status = status

    def _run(self):
        config = self.config
        backends = {"dshow": cv2.CAP_DSHOW, "msmf": cv2.CAP_MSMF}
        choices = ["dshow", "msmf"] if config.backend == "auto" else [config.backend]
        try:
            for retry in range(3):
                for name in choices:
                    if self.stop.is_set():
                        return
                    self._invalidate(f"OPENING_{name.upper()}_CAMERA_{config.camera_index}")
                    cap = self.factory()
                    try:
                        if not cap.open(config.camera_index, backends[name]):
                            continue
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.width)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.height)
                        cap.set(cv2.CAP_PROP_FPS, config.fps)
                        session_id = str(uuid.uuid4())
                        def reported(prop):
                            value = cap.get(prop)
                            return value if math.isfinite(value) else None
                        properties = {"camera_index": config.camera_index, "backend": name,
                                      "reported_width": reported(cv2.CAP_PROP_FRAME_WIDTH),
                                      "reported_height": reported(cv2.CAP_PROP_FRAME_HEIGHT),
                                      "reported_fps": reported(cv2.CAP_PROP_FPS),
                                      "exposure_reported": reported(cv2.CAP_PROP_EXPOSURE),
                                      "gain_reported": reported(cv2.CAP_PROP_GAIN),
                                      "settings_note": "Driver reports; 0/-1 may mean unsupported. Not calibrated measurements."}
                        logger.info("Camera opened: %s", properties)
                        seq, failed, received_start = 0, 0, time.monotonic()
                        while not self.stop.is_set():
                            ok, image = cap.read()
                            if not ok or image is None or image.size == 0:
                                failed += 1
                                self._invalidate("READ_FAILED_RECONNECTING")
                                if failed >= 8:
                                    break
                                self.stop.wait(0.08)
                                continue
                            failed = 0
                            seq += 1
                            packet = Frame(image, datetime.now(timezone.utc).isoformat(), time.monotonic(), seq, session_id)
                            with self.lock:
                                self.properties = dict(properties, actual_frame_size=[image.shape[1], image.shape[0]],
                                                       host_received_fps=seq / max(0.001, packet.monotonic - received_start))
                                self.latest = packet
                                self.status = "LIVE"
                    finally:
                        cap.release()
                self.stop.wait(0.5)
            self._invalidate("CAMERA_UNAVAILABLE_CLOSE_OTHER_APPS_CHECK_INDEX_AND_PRIVACY")
        except Exception:
            logger.exception("Camera reader failed")
            self._invalidate("CAMERA_DRIVER_ERROR_SEE_LOG")

    def capture(self):
        with self.lock:
            return self.latest, self.status, self.properties.copy()

    def release(self):
        self.stop.set()
        if self.thread:
            self.thread.join(timeout=2)
        self._invalidate("CLOSED")
        # A driver can block read/open forever. Daemon shutdown keeps Q usable;
        # the owning worker releases the device if/when its driver call returns.


def wait_for_frame(camera, timeout=12):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        packet, _, properties = camera.capture()
        if packet is not None:
            return packet, properties
        if camera.stop.wait(0.05):
            break
    raise RuntimeError(camera.capture()[1])
