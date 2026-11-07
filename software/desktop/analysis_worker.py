"""One analysis at a time; UI never waits for geometry or native QR decoding."""
from dataclasses import dataclass, replace
import threading
import time

from vision.opencv.camera import Frame
from vision.opencv.config import Config
from vision.opencv.pipeline import CoverVision, Result


@dataclass(frozen=True)
class AnalysisRequest:
    packet: Frame
    properties: dict
    config: Config
    revision: int
    flip: bool = False
    manual_points: object = None
    background: object = None
    background_path: str | None = None
    frozen: bool = False
    stabilize: bool = False
    save_request: tuple | None = None


@dataclass(frozen=True)
class AnalysisCompletion:
    request: AnalysisRequest
    result: Result | None
    elapsed: float
    error: str | None = None


class SnapshotProcessor:
    """CoverVision and its temporal state belong exclusively to the worker."""
    def __init__(self):
        self.vision = None
        self.context = None

    def __call__(self, request):
        try:
            context = (request.revision, request.packet.camera_session_id)
            if context != self.context:
                self.vision = CoverVision(replace(request.config))
                self.context = context
                if request.background is not None:
                    self.vision.calibrate(request.background)
            self.vision.manual_points = request.manual_points
            repeats = request.config.stable_frames if request.stabilize else 1
            for _ in range(repeats):
                result = self.vision.process(request.packet.image, decode=True, flip=request.flip)
            if request.manual_points is not None and result.crop is not None:
                result.stable_count = 0
                result.status = "QUALITY_WARNING" if result.issues else (
                    "READY" if result.qr.status == "VALID_FORMAT" else "QR_" + result.qr.status)
            return result
        except Exception:
            self.context = None
            raise


class AnalysisWorker:
    """Bounded mailbox: busy work is never replaced, pending old frames never pile up."""
    def __init__(self, processor=None):
        self.processor = processor if processor is not None else SnapshotProcessor()
        self.condition = threading.Condition()
        self.pending = self.completed = None
        self.busy = self.closed = False
        self.thread = threading.Thread(target=self._run, daemon=True, name="cover-analysis")
        self.thread.start()

    def submit(self, request):
        with self.condition:
            if self.closed or self.busy or self.pending is not None or self.completed is not None:
                return False
            self.pending = request
            self.condition.notify()
            return True

    def poll(self):
        with self.condition:
            completion, self.completed = self.completed, None
            return completion

    def close(self):
        with self.condition:
            self.closed = True
            self.pending = self.completed = None
            self.condition.notify()
        # Native decode can block. Never join it indefinitely on the UI thread.
        # It owns no camera, files, windows or session logging resources.
        self.thread.join(timeout=0.05)

    def _run(self):
        while True:
            with self.condition:
                self.condition.wait_for(lambda: self.closed or self.pending is not None)
                if self.closed:
                    return
                request, self.pending = self.pending, None
                self.busy = True
            started = time.monotonic()
            try:
                result = self.processor(request)
                completion = AnalysisCompletion(request, result, time.monotonic() - started)
            except Exception as error:
                completion = AnalysisCompletion(request, None, time.monotonic() - started,
                                                f"{type(error).__name__}: {error}")
            with self.condition:
                self.busy = False
                if self.closed:
                    return
                self.completed = completion
