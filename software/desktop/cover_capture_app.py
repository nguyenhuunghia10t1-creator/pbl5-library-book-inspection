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
from software.desktop.analysis_worker import AnalysisRequest, AnalysisWorker
from software.desktop.ui_text import draw_text
from software.desktop.ui_vietnamese import state_label, qr_label, issue_label, save_error_label


WINDOW = "PBL5 | Thu ảnh bìa sách A6"
SIZE = (1280, 800)
logger = logging.getLogger("cover_capture")


def text(canvas, value, pos, size=0.55, color=(210, 220, 230)):
    draw_text(canvas, value, pos, size, color)


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
    "NO_COVER": "Đặt trọn một bìa A6 trong khung. B: ghi nền trống; M: chọn góc thủ công.",
    "MULTIPLE_COVERS": "Lấy bìa thừa ra. Mỗi lần chỉ chụp một cuốn sách.",
    "TOUCHING_FRAME": "Đưa toàn bộ bìa vào giữa, chừa nền quanh bốn cạnh.",
    "QUALITY_WARNING": "Kiểm tra nét, ánh sáng và khoảng cách. D: lưu riêng để xem lại.",
    "MOVING": "Giữ yên điện thoại và sách, chờ các góc bìa ổn định.",
    "QR_UNREADABLE": "Đưa QR gần hơn, lấy nét, tránh lóa và giữ viền trắng quanh mã.",
    "QR_AMBIGUOUS": "Có nhiều QR. Chỉ để một mã trên bìa trong khung.",
    "QR_INVALID_FORMAT": "Mã cần có dạng PBL5-B04 hoặc LIB1:<copy_id>. Kiểm tra nội dung QR đã in.",
    "QR_INVALID_NAMESPACE": "Nội dung QR chưa thuộc định dạng PBL5/LIB1 được hỗ trợ.",
    "QR_DECODE_ERROR": "Chưa giải mã được QR. Chỉnh nét hoặc xem runtime.log.",
    "QR_PENDING": "Đang đọc mã QR, vui lòng chờ.",
    "READY": "S: lưu ảnh mới đủ điều kiện. Kiểm tra góc bìa và mã sách trước khi lưu.",
    "PICK_4_OUTER_CORNERS": "Bấm vào 4 góc ngoài của bìa trên ảnh bên trái. M: hủy.",
    "WAITING_FOR_ANALYSIS": "Đang phân tích ảnh, vui lòng chờ.",
    "WAITING_FOR_FRESH_FRAME": "Đang chờ camera gửi ảnh mới. Kiểm tra kết nối điện thoại.",
    "STARTING_CAMERA": "Đang mở nguồn camera, vui lòng chờ.",
    "PROCESSING_ERROR": "Phân tích thất bại. Đang thử lại; xem runtime.log nếu lỗi lặp lại.",
}


def render(packet, result, camera_status, message, properties, manual_points=None,
           mask_mode=False, fps=0, frozen=False, analysis_packet=None):
    canvas = np.full((SIZE[1], SIZE[0], 3), (28, 24, 20), np.uint8)
    text(canvas, "PBL5 / THU ẢNH BÌA SÁCH A6", (24, 35), 0.85, (110, 220, 245))
    caption = "ẢNH ĐÃ ĐÓNG BĂNG" if frozen else state_label(camera_status)
    if packet:
        caption += f" | Khung #{packet.sequence}"
    if mask_mode and analysis_packet and result.mask is not None:
        caption = f"MẶT NẠ TÁCH NỀN | Khung #{analysis_packet.sequence}"
    text(canvas, caption, (24, 64), 0.52)
    text(canvas, "BÌA ĐÃ CĂN / 630 × 888 px mặc định", (904, 64), 0.47)
    same_frame = packet is not None and analysis_packet is not None and (
        packet.camera_session_id, packet.sequence) == (analysis_packet.camera_session_id, analysis_packet.sequence)
    image = None if packet is None else packet.image
    if same_frame:
        image = annotate(packet.image, result, show_status=False)
        text(image, state_label(result.status), (15, 30), 0.7, (0, 100, 255))
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
    if analysis_packet:
        age = max(0, time.monotonic() - analysis_packet.monotonic)
        text(canvas, f"Đã xử lý #{analysis_packet.sequence} | Cách đây {age:.2f}s", (906, 600), 0.43)
    else:
        text(canvas, "Đang chờ phân tích...", (906, 600), 0.43)

    color = (100, 235, 110) if result.status == "READY" else (60, 190, 255)
    text(canvas, state_label(result.status), (24, 615), 0.75, color)
    text(canvas, "Mã sách: " + (result.qr.book_id or "--") + "   QR: " + qr_label(result.qr.status), (24, 646), 0.55)
    m = result.metrics
    if m:
        center = m["center_px"]
        text(canvas, f"Tâm ({center[0]:.0f}, {center[1]:.0f})px | Góc {m['angle_deg']:.1f}° | "
             f"Độ nét {m['sharpness']:.0f} | Độ sáng {m['brightness']:.0f}/255 | Ổn định {result.stable_count} lượt", (24, 675), 0.48)
        if "focus_measurable" in m:
            focus = f"{m['detail_sharpness']:.0f}" if m["focus_measurable"] else "chưa xác minh"
            text(canvas, f"Nét tại vùng chi tiết: {focus}", (906, 625), 0.44)
            text(canvas, f"Trắng/đen bão hòa: {100*m['clipped_high_fraction']:.1f}% / "
                 f"{100*m['clipped_low_fraction']:.1f}%", (906, 649), 0.41)
    hint = "Ảnh đã đóng băng: S lưu ảnh này; M chọn góc hoặc về trực tiếp." if frozen and result.status == "READY" else (
        HINTS.get(result.status, "Kiểm tra nguồn camera, quyền camera Windows và ứng dụng đang dùng camera."))
    if "FOCUS_UNVERIFIED" in result.issues:
        hint = "; ".join(issue_label(issue) for issue in result.issues) + ". D: lưu xem lại."
    text(canvas, (hint if "FOCUS_UNVERIFIED" in result.issues else "; ".join(issue_label(issue) for issue in result.issues)) or hint,
         (24, 701), 0.46)
    text(canvas, message, (24, 728), 0.47, (110, 220, 245))
    text(canvas, "S Lưu ảnh | D Lưu xem lại | B Ghi nền trống | M Chọn 4 góc | R Lật 180° | V Xem mặt nạ | Q Thoát", (24, 759), 0.48)
    text(canvas, f"[ / ] Ngưỡng tách nền | C Xóa nền đã ghi | Xử lý {fps:.1f} lượt/giây | "
         f"Nguồn camera {properties.get('camera_index', '--')}", (24, 785), 0.45)
    return canvas, placement


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
    camera = worker = None
    packet, properties, packet_properties = None, {}, {}
    result, analysis = Result("STARTING_CAMERA"), None
    message = "Lấy sách ra, bấm B để ghi nền bàn trống; sau đó đặt sách vào."
    frozen = bool(args.image)
    manual_selecting, selected, placement, manual_points = False, [], None, None
    flip, mask_mode = False, False
    background, background_path = None, None
    save_request = None
    revision, live_session = 0, None
    last_submitted, last_submit_time = None, 0.0
    status, fps = "IMAGE_INPUT" if args.image else "STARTING_CAMERA", 0.0
    started = time.monotonic()

    def invalidate(state="WAITING_FOR_ANALYSIS"):
        nonlocal revision, result, analysis, last_submitted, save_request
        revision += 1
        result, analysis, last_submitted, save_request = Result(state), None, None, None

    def save_completion(completion, review):
        nonlocal message
        request = completion.request
        try:
            saved = writer.save(request.packet, completion.result, request.properties,
                                review, request.background_path,
                                time.monotonic() - request.packet.monotonic, frozen=request.frozen)
            message = ("Đã lưu ảnh nhưng chưa cập nhật danh sách. Xem runtime.log; dùng --rebuild-manifest." if writer.manifest_warning else "Đã lưu " + saved.name + (" [CẦN XEM LẠI]" if review else " [ĐẠT ĐIỀU KIỆN THU ẢNH]"))
            logger.info("Saved capture %s; review=%s; manifest_warning=%s", saved.name, review, writer.manifest_warning)
        except (ValueError, OSError) as error:
            message = save_error_label(error)
            logger.warning("Save failed: %s", error)

    def mouse(event, x, y, flags, userdata):
        nonlocal message, manual_selecting, manual_points
        if event != cv2.EVENT_LBUTTONDOWN or not manual_selecting or not placement or packet is None:
            return
        left, top, width, height = placement
        if not left <= x < left + width or not top <= y < top + height:
            return
        selected.append([(x - left) / width * packet.image.shape[1],
                         (y - top) / height * packet.image.shape[0]])
        message = f"Chọn góc {len(selected) + 1}/4 (thứ tự tùy ý). M: hủy." if len(selected) < 4 else "Đã chọn đủ 4 góc."
        if len(selected) == 4:
            try:
                manual_points = order_quad(selected)
                manual_selecting = False
                invalidate()
                message = "Đã chọn góc: kiểm tra ảnh bìa. S: lưu; M: về trực tiếp."
            except ValueError as error:
                selected.clear()
                message = "Bốn góc chưa hợp lệ. Chọn lại 4 góc ngoài khác nhau, tạo thành hình tứ giác."

    try:
        worker = AnalysisWorker()
        if args.image:
            image = read_image(args.image)
            packet = Frame(image, datetime.now(timezone.utc).isoformat(), time.monotonic(), 1, str(uuid.uuid4()))
            properties = {"input_file": str(Path(args.image).resolve()), "actual_frame_size": [image.shape[1], image.shape[0]]}
            packet_properties = properties.copy()
            result = Result("WAITING_FOR_ANALYSIS")
            message = "Ảnh từ tệp. S: lưu; M: chọn góc; Q: thoát."
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
                        if packet is not None or live_session is not None:
                            invalidate("WAITING_FOR_FRESH_FRAME")
                            if live_session is not None:
                                background, background_path = None, None
                        packet, live_session = None, None
                        result = Result("WAITING_FOR_FRESH_FRAME")
                    else:
                        if incoming.camera_session_id != live_session:
                            invalidate()
                            background, background_path = None, None
                            live_session = incoming.camera_session_id
                        # Live preview advances on every fresh read, independently of analysis.
                        packet, packet_properties = incoming, properties.copy()
                if now - started > 20 and packet is None and not args.duration:
                    message = "Chưa có ảnh. Q: thoát; thử --camera 1 hoặc --backend msmf. Xem runtime.log."

            if save_request and now - save_request[1] > 3:
                save_request = None
                message = "Đã hủy lưu vì chưa nhận ảnh hoặc kết quả kịp thời. Bấm S/D để thử lại."
            completed = worker.poll()
            if completed is not None:
                request = completed.request
                matching = (packet is not None and request.revision == revision and
                            request.packet.camera_session_id == packet.camera_session_id and
                            (not frozen or request.packet.sequence == packet.sequence))
                fresh = request.frozen or time.monotonic() - request.packet.monotonic <= config.max_frame_age_seconds
                if matching and fresh:
                    if completed.error:
                        result, analysis = Result("PROCESSING_ERROR", issues=[completed.error]), None
                        last_submitted = None
                        message = "Phân tích lỗi, đang thử lại. Xem chi tiết trong runtime.log."
                        logger.warning("Analysis failed: %s", completed.error)
                        if request.save_request == save_request:
                            save_request = None
                    else:
                        analysis, result = completed, completed.result
                        fps = 1 / max(0.001, completed.elapsed)
                        if save_request is not None and request.save_request == save_request:
                            review, requested_at = save_request
                            save_request = None
                            if request.frozen or request.packet.monotonic > requested_at:
                                save_completion(completed, review)
                elif save_request is not None and request.save_request == save_request:
                    # Retry a fresh frame; never persist an expired completion.
                    last_submitted = None
            if analysis is not None and not frozen and (
                    time.monotonic() - analysis.request.packet.monotonic > config.max_frame_age_seconds):
                analysis, result = None, Result("WAITING_FOR_ANALYSIS")

            if packet is not None and not manual_selecting:
                request_key = (revision, packet.camera_session_id, packet.sequence)
                due = frozen or save_request is not None or now - last_submit_time >= config.qr_interval_seconds
                after_keypress = (save_request is None or frozen or packet.monotonic > save_request[1])
                if request_key != last_submitted and due and after_keypress:
                    request = AnalysisRequest(packet, packet_properties.copy(), replace(config), revision,
                                              flip, manual_points, background, background_path, frozen,
                                              bool(args.image) and manual_points is None, save_request)
                    if worker.submit(request):
                        last_submitted, last_submit_time = request_key, now

            analyzed_packet = None if analysis is None else analysis.request.packet
            canvas, placement = render(packet, result, status, message, properties,
                                        selected, mask_mode, fps, frozen, analysis_packet=analyzed_packet)
            cv2.imshow(WINDOW, canvas)
            if args.screenshot and analysis is not None:
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
                background = packet.image.copy()
                background_path = writer.save_background(background)
                invalidate()
                message = "Đã ghi nền. Đặt một bìa vào khung. Nếu ghi nhầm lúc có sách, bấm C rồi ghi lại bằng B."
                logger.info("Background reference %s", background_path)
            elif key in (ord("c"), ord("C")):
                background, background_path = None, None
                invalidate()
                message = "Đã xóa nền ghi trước đó; dùng màu ở mép khung hình để tách nền."
            elif key in (ord("["), ord("]")):
                config.background_tolerance = min(100, max(1, config.background_tolerance + (2 if key == ord("]") else -2)))
                invalidate()
                message = f"Ngưỡng tách nền: {config.background_tolerance:.0f} (chỉ phiên này). V: xem mặt nạ."
            elif key in (ord("r"), ord("R")):
                flip = not flip
                invalidate()
                message = "Lật ảnh 180°: " + ("BẬT" if flip else "TẮT")
            elif key in (ord("m"), ord("M")) and packet:
                if manual_selecting or manual_points is not None:
                    manual_selecting, selected, manual_points = False, [], None
                    frozen = bool(args.image)
                    invalidate()
                    message = "Đã bỏ chọn góc thủ công."
                else:
                    frozen, manual_selecting, selected, mask_mode = True, True, [], False
                    invalidate("PICK_4_OUTER_CORNERS")
                    message = "Bấm 4 góc ngoài bìa ở ảnh đóng băng bên trái (thứ tự tùy ý). M: hủy."
            elif key in (ord("s"), ord("S"), ord("d"), ord("D")):
                review = key in (ord("d"), ord("D"))
                if packet is None or manual_selecting:
                    message = "Chưa có ảnh để lưu, hoặc chưa chọn đủ 4 góc. Hoàn tất chọn góc trước."
                elif frozen and analysis is not None:
                    save_completion(analysis, review)
                else:
                    save_request = (review, time.monotonic())
                    last_submitted = None
                    message = "Đang chờ phân tích ảnh đóng băng..." if frozen else "Đang chờ ảnh mới từ camera để lưu..."
    finally:
        if worker:
            worker.close()
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
