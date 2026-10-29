import argparse
from dataclasses import replace
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import subprocess
import sys
import time
import uuid

import cv2
import numpy as np

from vision.opencv.camera import CameraAdapter, Frame, wait_for_frame
from vision.opencv.config import ROOT, load_config
from vision.opencv.dataset import DatasetWriter, annotate, read_image, rebuild_manifest
from vision.opencv.pipeline import CoverVision, Result, order_quad


WINDOW = "PBL5 | A6 Cover Capture"
SIZE = (1280, 800)
logger = logging.getLogger("cover_capture")


def text(canvas, value, pos, size=0.55, color=(210, 220, 230)):
    cv2.putText(canvas, str(value), pos, cv2.FONT_HERSHEY_SIMPLEX, size, color, 1, cv2.LINE_AA)


def fit_image(canvas, image, box):
    x, y, width, height = box
    if image is None:
        return None
    ratio = min(width / image.shape[1], height / image.shape[0])
    shape = (max(1, round(image.shape[1] * ratio)), max(1, round(image.shape[0] * ratio)))
    left, top = x + (width - shape[0]) // 2, y + (height - shape[1]) // 2
    canvas[top:top + shape[1], left:left + shape[0]] = cv2.resize(image, shape)
    return left, top, shape[0], shape[1]


HINTS = {
    "NO_COVER": "Keep one whole A6 cover in view. B: calibrate empty background; M: pick corners.",
    "MULTIPLE_COVERS": "Remove extra covers. Only one book per capture.",
    "TOUCHING_FRAME": "Move the entire cover away from the image edges.",
    "QUALITY_WARNING": "Improve focus/light/distance. D saves separately for review.",
    "MOVING": "Hold the cover still for a moment.",
    "QR_UNREADABLE": "Make QR larger, sharp, glare-free, with a clean white border.",
    "QR_AMBIGUOUS": "Multiple QR codes found. Keep only one on the cover.",
    "QR_INVALID_FORMAT": "Expected PBL5-B04 or LIB1:<copy_id>; check the printed payload.",
    "QR_INVALID_NAMESPACE": "QR payload is outside the supported PBL5/LIB1 formats.",
    "READY": "S: save the NEXT fresh frame. Check the crop and ID first.",
}


def render(packet, result, camera_status, message, properties, manual_points=None,
           mask_mode=False, fps=0, frozen=False):
    canvas = np.full((SIZE[1], SIZE[0], 3), (28, 24, 20), np.uint8)
    text(canvas, "PBL5 / A6 COVER CAPTURE", (24, 35), 0.85, (110, 220, 245))
    text(canvas, "FROZEN SNAPSHOT" if frozen else camera_status, (24, 64), 0.52)
    text(canvas, "RECTIFIED A6 / 630 x 888 default", (904, 64), 0.47)
    image = None if packet is None else annotate(packet.image, result)
    if mask_mode and result.mask is not None:
        image = cv2.cvtColor(result.mask, cv2.COLOR_GRAY2BGR)
    placement = fit_image(canvas, image, (20, 82, 860, 505))
    if packet and placement and manual_points:
        x, y, width, height = placement
        for i, p in enumerate(manual_points):
            point = (int(x + p[0] / packet.image.shape[1] * width),
                     int(y + p[1] / packet.image.shape[0] * height))
            cv2.circle(canvas, point, 7, (0, 180, 255), -1)
            text(canvas, str(i + 1), (point[0] + 10, point[1]))
    fit_image(canvas, result.crop, (906, 82, 354, 500))
    color = (100, 235, 110) if result.status == "READY" else (60, 190, 255)
    text(canvas, result.status, (24, 615), 0.75, color)
    text(canvas, "ID: " + (result.qr.book_id or "--") + "   QR: " + result.qr.status, (24, 646), 0.55)
    m = result.metrics
    if m:
        center = m["center_px"]
        text(canvas, f"Center ({center[0]:.0f}, {center[1]:.0f})px | Angle {m['angle_deg']:.1f}deg | "
             f"Sharp {m['sharpness']:.0f} | Light {m['brightness']:.0f} | Stable {result.stable_count}", (24, 675), 0.48)
    text(canvas, ", ".join(result.issues) or HINTS.get(result.status, "Check camera index, Windows privacy and other camera apps."),
         (24, 701), 0.46)
    text(canvas, message[:142], (24, 728), 0.47, (110, 220, 245))
    text(canvas, "S Save | D Review | B Empty background | M Freeze/pick 4 corners | R Flip 180 | V Mask | Q Quit", (24, 759), 0.48)
    text(canvas, f"[ / ] Background tolerance | C Clear calibration | Pipeline {fps:.1f} fps | "
         f"Camera {properties.get('camera_index', '--')}", (24, 785), 0.45)
    return canvas, placement


def process_snapshot(vision, packet, flip, manual=False):
    result = vision.process(packet.image, decode=True, flip=flip)
    if manual and result.crop is not None:
        # A deliberately frozen snapshot has no temporal stability measurement.
        result.stable_count = 0
        result.status = "QUALITY_WARNING" if result.issues else (
            "READY" if result.qr.status == "VALID_FORMAT" else "QR_" + result.qr.status)
    return result


def run_ui(config, args):
    source_kind = args.source_kind or ("imported" if args.image else "real")
    writer = DatasetWriter(config, source_kind, str(args.image) if args.image else "USB camera via OpenCV")
    logfile = writer.session_dir / "runtime.log"
    old_level, old_propagate = logger.level, logger.propagate
    session_handlers = [logging.FileHandler(logfile, encoding="utf-8"), logging.StreamHandler()]
    for handler in session_handlers:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.info("Session %s; output %s", writer.session_id, writer.root)
    vision = CoverVision(config)
    camera = None
    packet, properties, packet_properties = None, {}, {}
    result = Result("STARTING_CAMERA")
    message = "Remove books, press B once to calibrate the empty tabletop."
    frozen = bool(args.image)
    manual_selecting, selected, placement = False, [], None
    flip, mask_mode = False, False
    background_path = None
    save_request = None
    last_key, last_processed, last_decode = None, None, 0.0
    status, fps = "IMAGE_INPUT" if args.image else "STARTING_CAMERA", 0.0
    started = time.monotonic()

    def mouse(event, x, y, flags, userdata):
        nonlocal message, result, last_decode, manual_selecting
        if event != cv2.EVENT_LBUTTONDOWN or not manual_selecting or not placement or packet is None:
            return
        left, top, width, height = placement
        if not left <= x < left + width or not top <= y < top + height:
            return
        selected.append([(x - left) / width * packet.image.shape[1],
                         (y - top) / height * packet.image.shape[0]])
        message = f"Pick corner {len(selected) + 1}/4 (any order). M cancels." if len(selected) < 4 else "Corners selected."
        if len(selected) == 4:
            try:
                vision.manual_points = order_quad(selected)
                result = process_snapshot(vision, packet, flip, manual=True)
                manual_selecting = False
                message = "Manual snapshot: check crop; S saves; M returns to live."
            except ValueError as error:
                selected.clear()
                message = str(error) + "; pick four outer corners again."

    try:
        if args.image:
            image = read_image(args.image)
            packet = Frame(image, datetime.now(timezone.utc).isoformat(), time.monotonic(), 1, str(uuid.uuid4()))
            properties = {"input_file": str(Path(args.image).resolve()), "actual_frame_size": [image.shape[1], image.shape[0]]}
            packet_properties = properties.copy()
            # Static imported input bypasses movement gate without claiming a live-camera test.
            for _ in range(config.stable_frames):
                result = vision.process(image, flip=flip)
            message = "Imported image. S saves; M selects corners; Q quits."
        else:
            camera = CameraAdapter(config).start()
        cv2.namedWindow(WINDOW, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(WINDOW, mouse)
        while True:
            now = time.monotonic()
            if args.duration and now - started >= args.duration:
                break
            if camera:
                incoming, status, properties = camera.capture()
                if not frozen:
                    if incoming is None or now - incoming.monotonic > config.max_frame_age_seconds:
                        packet = None
                        result = Result("WAITING_FOR_FRESH_FRAME")
                        vision.reset_tracking()
                    else:
                        key = (incoming.camera_session_id, incoming.sequence)
                        if last_key and key[0] != last_key[0]:
                            vision.reset_tracking()
                            vision.background = None
                            background_path = None
                        due = now - last_decode >= config.qr_interval_seconds or save_request is not None
                        if key != last_key and due:
                            packet = incoming
                            packet_properties = properties.copy()
                            if save_request and packet.monotonic <= save_request[1]:
                                continue
                            result = process_snapshot(vision, packet, flip)
                            ended = time.monotonic()
                            fps = 0 if last_processed is None else 1 / max(0.001, ended - last_processed)
                            last_processed, last_decode, last_key = ended, ended, key
                            if save_request:
                                review = save_request[0]
                                save_request = None
                                try:
                                    saved = writer.save(packet, result, packet_properties, review, background_path,
                                                        time.monotonic() - packet.monotonic)
                                    message = "Saved " + saved.name + (" [REVIEW]" if review else " [ACCEPTED]")
                                    logger.info(message)
                                    if writer.manifest_warning:
                                        message = writer.manifest_warning
                                        logger.warning(message)
                                except (ValueError, OSError) as error:
                                    message = str(error)
                                    logger.warning(message)
                if now - started > 20 and packet is None and not args.duration:
                    message = "No frames. Q to quit; try --camera 1 or --backend msmf. See runtime.log."
            if save_request and now - save_request[1] > 3:
                save_request = None
                message = "Save cancelled: no fresh frame received."
            canvas, placement = render(packet, result, status, message, properties,
                                        selected, mask_mode, fps, frozen)
            cv2.imshow(WINDOW, canvas)
            if args.screenshot:
                # One preview artifact, explicitly requested; never a dataset sample.
                ok, encoded = cv2.imencode(".png", canvas)
                if ok:
                    Path(args.screenshot).write_bytes(encoded.tobytes())
                args.screenshot = None
            key = cv2.waitKey(10) & 0xFF
            if cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1 or key in (ord("q"), ord("Q"), 27):
                break
            if key in (ord("v"), ord("V")):
                mask_mode = not mask_mode
            elif key in (ord("b"), ord("B")) and packet and not frozen:
                vision.calibrate(packet.image)
                background_path = writer.save_background(packet.image)
                message = "Background calibrated. Place one cover in view. Press C if calibrated with a book present."
                logger.info("Background reference %s", background_path)
            elif key in (ord("c"), ord("C")):
                vision.background, background_path = None, None
                vision.reset_tracking()
                message = "Background calibration cleared; using frame border color."
            elif key in (ord("["), ord("]")):
                config.background_tolerance = min(100, max(1, config.background_tolerance + (2 if key == ord("]") else -2)))
                vision.reset_tracking()
                message = f"Background tolerance: {config.background_tolerance:.0f} (session only). V shows mask."
            elif key in (ord("r"), ord("R")):
                flip = not flip
                if packet:
                    result = process_snapshot(vision, packet, flip, manual=vision.manual_points is not None)
                message = "Manual 180-degree flip " + ("ON" if flip else "OFF")
            elif key in (ord("m"), ord("M")) and packet:
                save_request = None
                if manual_selecting or vision.manual_points is not None:
                    manual_selecting, selected, vision.manual_points = False, [], None
                    frozen = bool(args.image)
                    vision.reset_tracking()
                    message = "Manual selection cleared."
                else:
                    frozen, manual_selecting, selected, mask_mode = True, True, [], False
                    result = Result("PICK_4_OUTER_CORNERS")
                    message = "Click four outer cover corners in the left frozen image (any order). M cancels."
            elif key in (ord("s"), ord("S"), ord("d"), ord("D")):
                review = key in (ord("d"), ord("D"))
                if packet is None or manual_selecting:
                    message = "No usable frame / finish selecting four corners first."
                elif frozen:
                    try:
                        saved = writer.save(packet, result, packet_properties, review, background_path,
                                            time.monotonic() - packet.monotonic, frozen=True)
                        message = writer.manifest_warning or ("Saved frozen snapshot " + saved.name)
                        logger.info(message)
                    except (ValueError, OSError) as error:
                        message = str(error)
                else:
                    save_request = (review, time.monotonic())
                    message = "Waiting for next fresh camera frame..."
    finally:
        if camera:
            camera.release()
        cv2.destroyAllWindows()
        logger.info("Session closed")
        for handler in session_handlers:
            logger.removeHandler(handler)
            handler.close()
        logger.setLevel(old_level)
        logger.propagate = old_propagate
    return 0


def headless(config, args):
    camera = None
    try:
        properties = {}
        if args.image:
            image = read_image(args.image)
            packet = Frame(image, datetime.now(timezone.utc).isoformat(), time.monotonic(), 1, str(uuid.uuid4()))
            properties = {"input_file": str(Path(args.image).resolve())}
        else:
            camera = CameraAdapter(config).start()
            packet, properties = wait_for_frame(camera, timeout=12)
        vision = CoverVision(config)
        result = vision.process(packet.image)
        if args.image:
            for _ in range(config.stable_frames - 1):
                result = vision.process(packet.image)
        output = {"vision_status": result.status, "qr": result.qr.status, "copy_id": result.qr.book_id,
                  "metrics": result.metrics, "issues": result.issues, "camera": properties}
        if args.save:
            # Single headless camera snapshot has no temporal stability proof.
            writer = DatasetWriter(config, args.source_kind or ("imported" if args.image else "real"), args.image)
            saved = writer.save(packet, result, properties, review=result.status != "READY",
                                frame_age_seconds=time.monotonic() - packet.monotonic,
                                frozen=bool(args.image))
            output["saved"] = str(saved)
            output["manifest_warning"] = writer.manifest_warning
        print(json.dumps(output, ensure_ascii=True, allow_nan=False))
        return 0
    finally:
        if camera:
            camera.release()


def probe(config, count):
    results = []
    for index in range(count):
        command = [sys.executable, str(ROOT / "scripts/capture_covers.py"), "--probe-one", str(index), "--backend", config.backend]
        try:
            completed = subprocess.run(command, capture_output=True, text=True, timeout=17)
            info = json.loads(completed.stdout.strip().splitlines()[-1]) if completed.stdout.strip() else {"error": completed.stderr[-300:]}
            info["exit_code"] = completed.returncode
        except subprocess.TimeoutExpired:
            info = {"error": "Driver probe timed out (17s); child terminated"}
        except (ValueError, OSError) as error:
            info = {"error": str(error)}
        info["camera_index"] = index
        results.append(info)
        print(json.dumps(info, ensure_ascii=True), flush=True)
    return 0 if any(item.get("opened") for item in results) else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description="A6 cover geometry, QR and dataset capture. See docs/COVER_CAPTURE.md")
    parser.add_argument("--config")
    parser.add_argument("--camera", type=int)
    parser.add_argument("--backend", choices=["auto", "dshow", "msmf"])
    parser.add_argument("--output")
    parser.add_argument("--image", help="Process an existing image; source is marked imported")
    parser.add_argument("--source-kind", choices=["real", "synthetic", "imported"])
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--save", action="store_true", help="Save headless snapshot; uncertain samples go to review")
    parser.add_argument("--probe", action="store_true", help="Probe camera indexes in isolated child processes")
    parser.add_argument("--probe-count", type=int, default=3)
    parser.add_argument("--probe-one", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--duration", type=float, help="Close GUI after N seconds (smoke test)")
    parser.add_argument("--screenshot", help=argparse.SUPPRESS)
    parser.add_argument("--rebuild-manifest", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        if args.camera is not None:
            config.camera_index = args.camera
        if args.backend:
            config.backend = args.backend
        if args.output:
            config.output_dir = args.output
        config.validate()
        if args.duration is not None and args.duration <= 0:
            parser.error("--duration must be positive")
        if not 1 <= args.probe_count <= 10:
            parser.error("--probe-count must be 1..10")
        if args.rebuild_manifest:
            print(f"Validated and indexed {rebuild_manifest(config.output_dir)} captures")
            return 0
        if args.probe_one is not None:
            config.camera_index = args.probe_one
            camera = CameraAdapter(config).start()
            try:
                packet, properties = wait_for_frame(camera)
                print(json.dumps({"opened": True, "camera": properties, "capture_seq": packet.sequence}))
            finally:
                camera.release()
            return 0
        if args.probe:
            return probe(config, args.probe_count)
        return headless(config, args) if args.headless else run_ui(config, args)
    except KeyboardInterrupt:
        print("Stopped.")
        return 130
    except (OSError, ValueError, RuntimeError, cv2.error) as error:
        print(f"ERROR: {error}\nSee docs/COVER_CAPTURE.md. Camera: close other apps, check Windows privacy, try --camera 1.", file=sys.stderr)
        return 1
