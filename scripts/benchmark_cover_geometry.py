"""Compare real OpenCV processing on synthetic scenes; never opens a camera."""
import argparse
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import types

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import cv2
import numpy as np
from vision.opencv.config import Config
from vision.opencv.pipeline import CoverVision, corner_motion, order_quad
from tests.opencv.color_fixtures import color_scene, matrix_cases


def measure(vision_type, scenes, repeats, width):
    timings, errors, failed = [], [], []
    total = 0
    for label, image, expected, bg in scenes:
        for calibrated in (False, True):
            vision = vision_type(Config(processing_width=width, stable_frames=1))
            if calibrated:
                vision.calibrate(bg)
            vision.process(image, decode=False)  # Warm up per scene; exclude QR in both versions.
            for _ in range(repeats):
                start = time.perf_counter()
                result = vision.process(image, decode=False)
                timings.append((time.perf_counter() - start) * 1000)
            error = None if result.corners is None else corner_motion(result.corners, order_quad(expected))
            total += 1
            if error is not None:
                errors.append(error)
            if error is None or error >= 10 or result.crop is None or result.crop.shape != (888, 630, 3):
                failed.append({"case": label, "calibrated": calibrated,
                               "status": result.status, "max_corner_error_px": error})
    return {"cases": total, "within_10px_with_crop": total - len(failed),
            "max_corner_error_px": round(max(errors), 3) if errors else None,
            "median_process_ms": round(statistics.median(timings), 3),
            "p95_process_ms": round(float(np.percentile(timings, 95)), 3),
            "timed_frames": len(timings), "failed_cases": failed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-ref", default="8f9198f0c78030dd21000f4562a0492556c1dce2")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--processing-width", type=int, default=640)
    args = parser.parse_args()
    if args.repeats < 1 or args.processing_width < 32:
        parser.error("Use --repeats >= 1 and --processing-width >= 32")
    source = subprocess.check_output(["git", "show", args.baseline_ref + ":vision/opencv/pipeline.py"],
                                     cwd=ROOT, text=True, encoding="utf-8")
    baseline = types.ModuleType("vision.opencv._geometry_baseline")
    baseline.__package__ = "vision.opencv"
    sys.modules[baseline.__name__] = baseline
    exec(compile(source, "<Git baseline geometry>", "exec"), baseline.__dict__)
    scenes = [(name, *color_scene(**options)) for name, options in matrix_cases()]
    output = {"source_kind": "synthetic", "baseline_ref": args.baseline_ref,
              "python": platform.python_version(), "opencv": cv2.__version__, "numpy": np.__version__,
              "processing_width": args.processing_width, "repeats": args.repeats,
              "before": measure(baseline.CoverVision, scenes, args.repeats, args.processing_width),
              "after": measure(CoverVision, scenes, args.repeats, args.processing_width),
              "limitations": "Known fixture corners, no camera, no QR timing. Does not estimate hardware accuracy/FPS."}
    print(json.dumps(output, indent=2, allow_nan=False))
    return 0 if output["after"]["within_10px_with_crop"] == output["after"]["cases"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
