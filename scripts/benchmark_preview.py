"""Compare synthetic UI scheduling against a Git revision; no camera or real QR timing."""
import argparse
from contextlib import ExitStack
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time
import types
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import cv2
import numpy as np
from software.desktop import cover_capture_app as current
from software.desktop.analysis_worker import AnalysisWorker
from vision.opencv.camera import Frame
from vision.opencv.config import Config
from vision.opencv.pipeline import Result


def measure(module, frame_count, delay):
    displayed, workers = [], []
    counts = {"camera": 0, "analysis": 0}
    class Camera:
        def start(self):
            return self
        def capture(self):
            counts["camera"] += 1
            return (Frame(np.zeros((64, 64, 3), np.uint8), datetime.now(timezone.utc).isoformat(),
                          time.monotonic(), counts["camera"], "synthetic-benchmark"), "LIVE", {})
        def release(self):
            pass
    class Vision:
        manual_points = background = None
        def __init__(self, config):
            pass
        def reset_tracking(self):
            pass
        def process(self, *args, **kwargs):
            counts["analysis"] += 1
            time.sleep(delay)
            return Result("NO_COVER")
    def render(packet, *args, **kwargs):
        displayed.append((time.perf_counter(), packet.sequence))
        return np.zeros((2, 2, 3), np.uint8), None
    def key(_):
        time.sleep(0.01)
        return ord("q") if len(displayed) >= frame_count else -1
    def make_worker():
        worker = AnalysisWorker()
        workers.append(worker)
        return worker
    with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
        for name, value in {"load_config": lambda _: Config(output_dir=folder, qr_interval_seconds=0.001),
                            "CameraAdapter": lambda _: Camera(), "CoverVision": Vision, "render": render}.items():
            stack.enter_context(patch.object(module, name, value))
        if hasattr(module, "AnalysisWorker"):
            stack.enter_context(patch.object(module, "AnalysisWorker", side_effect=make_worker))
            stack.enter_context(patch("software.desktop.analysis_worker.CoverVision", Vision))
        for name in ("namedWindow", "setMouseCallback", "imshow", "destroyAllWindows"):
            stack.enter_context(patch.object(cv2, name))
        stack.enter_context(patch.object(cv2, "getWindowProperty", return_value=1))
        stack.enter_context(patch.object(cv2, "waitKey", side_effect=key))
        started = time.perf_counter()
        code = module.main(["--source-kind", "synthetic"])
        elapsed = time.perf_counter() - started
        # Cleanup is outside the measured UI duration; all resources are synthetic.
        for worker in workers:
            worker.thread.join(delay + 2)
        if code:
            raise RuntimeError(f"Synthetic run returned {code}")
    gaps = [(b[0] - a[0]) * 1000 for a, b in zip(displayed, displayed[1:])]
    return {"ui_frames": len(displayed), "unique_preview_frames": len({seq for _, seq in displayed}),
            "analysis_calls": counts["analysis"], "ui_seconds": round(elapsed, 4),
            "median_preview_gap_ms": round(statistics.median(gaps), 3),
            "max_preview_gap_ms": round(max(gaps), 3)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-ref", default="4d3b402")
    parser.add_argument("--frames", type=int, default=15)
    parser.add_argument("--delay", type=float, default=0.2)
    args = parser.parse_args()
    if args.frames < 2 or not 0 < args.delay <= 5:
        parser.error("Use --frames >= 2 and 0 < --delay <= 5")
    source = subprocess.check_output(["git", "show", args.baseline_ref + ":software/desktop/cover_capture_app.py"],
                                     cwd=ROOT, text=True, encoding="utf-8")
    baseline = types.ModuleType("preview_baseline")
    exec(compile(source, "<Git baseline UI>", "exec"), baseline.__dict__)
    output = {"source_kind": "synthetic", "baseline_ref": args.baseline_ref,
              "analysis_delay_ms": args.delay * 1000, "fake_event_wait_ms": 10,
              "before": measure(baseline, args.frames, args.delay),
              "after": measure(current, args.frames, args.delay),
              "limitations": "Camera, renderer and analysis are fake; measures scheduling only, not real FPS or QR accuracy."}
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
