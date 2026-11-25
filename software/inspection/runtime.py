"""One active physical job. Only the controller can authorize motion."""

import asyncio
import contextlib
from datetime import datetime, timezone
import json
import threading
import time
from pathlib import Path

from software.controller.simulator import Simulator
from software.controller.transport import SerialController
from software.inspection.file_simulation import Decision, FileClassifier, decode_photo
from software.inspection.store import Store

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/local/station"
MANUAL_DECISION_S = 8.0


class CalibrationFailure(ValueError):
    def __init__(self, detail):
        super().__init__(detail["message"])
        self.detail = detail


def save_json(path, data):
    tmp = path.with_suffix(".new")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf8")
    tmp.replace(path)


class Runtime:
    def __init__(self, simulation=False, folder=DATA, *, manual=False, direct=False):
        if sum((simulation, manual, direct)) > 1:
            raise ValueError("Choose one station mode.")
        self.cfg = json.loads(
            (ROOT / "configs/station.json").read_text(encoding="utf8")
        )
        self.folder = Path(folder)
        self.mode = "simulation" if simulation else ("hardware-manual" if manual else "hardware")
        self.store = Store(self.folder, self.mode)
        self.last_stop_path = self.folder / f"last-stop-{self.mode}.json"
        self.last_stop = None
        self.stop_signature = None
        try:
            saved = json.loads(self.last_stop_path.read_text(encoding="utf8"))
            if isinstance(saved, dict):
                self.last_stop = saved
        except (OSError, ValueError):
            pass
        self.serial_path = self.folder / "serial.json"
        settings = (
            json.loads(self.serial_path.read_text(encoding="utf8"))
            if self.serial_path.exists() and not simulation
            else {}
        )
        self.port = settings.get("port", self.cfg.get("serial_port", ""))
        self.ctrl = Simulator() if simulation else SerialController(self.port, bridge_port=self.cfg.get("bridge_diagnostic_port", ""))
        self.vision = None
        if self.mode == "hardware":
            from vision.yolo.station import StationVision

            self.vision = StationVision(self.cfg)
            self.vision.direct_routing = direct
        self.initialize_settings()
        self.simulation_photo = None
        self.file_classifier = FileClassifier(self.cfg) if simulation else None
        self.manual_deadline = None
        self.hold_issue = None
        self.last_board = {}
        self.board_seen = None
        self.board = {}
        self.link_error = "Đang kết nối"
        self.key = None
        self.pending = "WAIT"
        self.candidate = None
        self.inspection = None
        self.cancel = None
        self.service = None
        self.busy = False
        self.sample_result = None

    def health(self):
        if self.busy:
            return "Đang hiệu chuẩn hoặc lấy mẫu"
        if self.vision:
            return self.vision.reason()
        if self.mode == "hardware-manual":
            return ""
        if not self.ctrl.camera_ok:
            return "Mất camera mô phỏng"
        if not self.ctrl.ai_ok:
            return "AI lỗi mô phỏng"
        return ""

    def start(self):
        if self.vision:
            self.vision.start()
        self.service = asyncio.create_task(self.run())

    def end_job(self, status, reason):
        if self.cancel:
            self.cancel.set()
        if self.inspection:
            self.inspection.cancel()
        if self.key:
            self.store.finish(self.key, status, reason)
        self.key = self.cancel = self.inspection = None
        self.manual_deadline = None
        self.hold_issue = None
        self.pending = "WAIT"
        self.candidate = None

    def manual_remaining(self):
        if (
            self.mode != "hardware-manual"
            or self.pending != "WAIT"
            or self.manual_deadline is None
            or self.link_error
            or self.board.get("phase") != "WAIT_AI"
            or not self.board.get("ir")
            or self.board.get("capture_id") != self.key
        ):
            return None
        return max(0.0, self.manual_deadline - time.monotonic())

    def manual_decision(self, key, verdict):
        if self.mode != "hardware-manual" or verdict not in ("OK", "NG"):
            raise ValueError("Choose OK or NG in manual hardware mode.")
        if not self.key or key != self.key or not self.manual_remaining():
            raise ValueError("This capture is no longer accepting a decision.")
        self.candidate = Decision("Manual", None, verdict)
        self.pending = verdict

    def manual_decision_status(self):
        if self.manual_deadline is None or self.pending == "WAIT":
            return None
        # Only a matching board ACK clears the candidate while its job is active.
        state = "queued" if self.candidate is not None else "acknowledged"
        return {"key": self.key, "verdict": self.pending, "state": state}

    async def sim_image(self, data: bytes):
        if self.mode != "simulation":
            raise ValueError("Image files are only available in simulation.")
        self.require_sim_source_change()
        photo = await asyncio.to_thread(decode_photo, data)
        self.require_sim_source_change()
        await asyncio.to_thread(self.file_classifier.prepare)
        self.require_sim_source_change()
        self.simulation_photo = photo

    @property
    def simulation_preview(self):
        return self.simulation_photo.preview if self.simulation_photo else b""

    def require_sim_source_change(self):
        if self.ctrl.phase == "WAIT_AI":
            raise ValueError("Wait for the current simulated capture before changing its source.")

    def sim_event(self, action):
        if self.mode != "simulation":
            raise ValueError("This control is only available in simulation.")
        if action in ("OK", "NG", "HOLD"):
            self.require_sim_source_change()
        self.ctrl.event(action)
        if action in ("OK", "NG", "HOLD"):
            self.simulation_photo = None

    def record_stop(self, phase, reason, key=None, readiness_issue=None):
        # A refused start is reported in live board status, without replacing the last stop.
        if not reason or reason in ("STARTUP", "CLEAR_STATION", "RETURN_WAIT"):
            return
        if phase == "OFF" and reason == "PC_NOT_READY":
            return
        signature = (phase, reason, key)
        if signature == self.stop_signature:
            return
        self.stop_signature = signature
        issue = None
        if reason == "INSPECTION_HOLD" and key == self.key and self.pending == "HOLD":
            issue = self.hold_issue
        elif reason == "PC_NOT_READY":
            issue = readiness_issue
        self.last_stop = dict(
            phase=phase,
            reason=reason,
            job_id=key,
            occurred_at=datetime.now(timezone.utc).isoformat(),
            diagnostic=issue,
            diagnostics={("camera" if reason == "PC_NOT_READY" else "inspection"): issue} if issue else {},
        )
        try:
            save_json(self.last_stop_path, self.last_stop)
        except OSError:
            # Preserve the running status even when local storage is unavailable.
            pass

    async def inspect(self, key, stop, cancelled, photo=None):
        try:
            if self.vision:
                reading = await asyncio.to_thread(
                    self.vision.inspect, stop, cancelled, direct=self.vision.direct_routing
                )
            elif photo:
                reading = await asyncio.wait_for(
                    asyncio.to_thread(self.file_classifier.inspect, photo),
                    timeout=self.cfg["inspection_s"],
                )
            else:
                await asyncio.sleep(0.35)
                choice = self.ctrl.choice
                reading = Decision(
                    choice,
                    0.55 if choice == "HOLD" else 0.98,
                    choice,
                    "Operator selected a simulated hold." if choice == "HOLD" else "",
                    b"",
                    b"",
                    "simulation",
                )
            if self.key == key and not cancelled.is_set():
                self.candidate = reading
                self.pending = reading.verdict
                if reading.verdict == "HOLD":
                    self.hold_issue = (self.vision.last_inspection_issue if self.vision
                                       else getattr(reading, "diagnostic", None))
                    if self.hold_issue is None:
                        self.hold_issue = dict(code="INSPECTION_HOLD", message=reading.reason or "Inspection requested a hold.",
                                               remedy="Review the book before restarting.")
        except Exception as exc:
            if self.key == key and not cancelled.is_set():
                detail = str(exc) or type(exc).__name__
                self.store.inspection_issue(key, detail)
                if photo:
                    if isinstance(exc, TimeoutError):
                        detail = "Image prediction timed out."
                        self.hold_issue = dict(code="INSPECTION_EXPIRED", message=detail,
                                               measured=time.monotonic() - stop, limit=self.cfg["inspection_s"],
                                               remedy="Check classifier speed and the inspection time limit.")
                    self.candidate = Decision("Image file", None, "HOLD", detail, raw=photo.preview)
                else:
                    self.candidate = Decision("", None, "HOLD", detail)
                    if self.vision:
                        self.hold_issue = self.vision.last_inspection_issue
                if self.hold_issue is None:
                    self.hold_issue = dict(code="INSPECTION_ERROR", message=detail,
                                           remedy="Check the input image and classifier before restarting.")
                self.pending = "HOLD"

    def observe(self, board, readiness_issue=None):
        previous = self.board
        self.last_board = board.copy()
        self.board_seen = time.monotonic()
        self.board = board
        key = f"{board['boot']}-{board['job']}"
        if board["phase"] in ("OFF", "FAULT"):
            # Pressing start in FAULT may change only the reason to PC_NOT_READY.
            refused_restart = (
                board["reason"] == "PC_NOT_READY" and previous.get("phase") == board["phase"]
                and previous.get("boot") == board["boot"] and previous.get("job") == board["job"]
            )
            if not refused_restart:
                self.record_stop(board["phase"], board["reason"], key if board["job"] else None, readiness_issue)
        else:
            self.stop_signature = None
        if self.key:
            completed = f"{board['boot']}-{board['completed']}"
            # Only an acknowledgement for our active command counts as a decision.
            if (
                self.key in (key, completed)
                and self.candidate is not None
                and board.get("ack") == self.pending
            ):
                self.store.decision(self.key, self.candidate)
                self.candidate = None
            if self.key == completed:
                self.end_job("COMPLETE", "")
            elif key != self.key or board["phase"] in ("OFF", "FAULT"):
                reason = board["reason"]
                status = {
                    "INSPECTION_HOLD": "HOLD",
                    "NG_NOT_CLEAR": "FAULT",
                    "RELEASE_JAM": "FAULT",
                    "AI_TIMEOUT": "FAULT",
                    "BOOK_MOVED": "FAULT",
                }.get(reason, "UNCONFIRMED")
                self.end_job(status, reason)
        if (
            board["phase"] == "WAIT_AI"
            and board.get("capture_id") == key
            and self.key is None
        ):
            self.key = key
            self.cancel = threading.Event()
            if self.store.begin(key, ("direct" if self.vision.direct_routing else "calibrated") if self.vision else self.mode):
                start = time.monotonic()
                if self.mode == "hardware-manual":
                    self.manual_deadline = start + MANUAL_DECISION_S
                else:
                    self.inspection = asyncio.create_task(
                        self.inspect(key, start, self.cancel, self.simulation_photo)
                    )
            else:
                self.pending = "HOLD"

    async def run(self):
        boot = "-"
        previous_ctrl = None
        try:
            while True:
                ctrl = self.ctrl
                if ctrl is not previous_ctrl:
                    boot = "-"
                    previous_ctrl = ctrl
                try:
                    if (
                        self.manual_deadline is not None
                        and self.pending == "WAIT"
                        and time.monotonic() >= self.manual_deadline
                    ):
                        self.candidate = Decision("Manual", None, "HOLD", "Manual decision timed out.")
                        self.hold_issue = dict(code="MANUAL_TIMEOUT", message=self.candidate.reason,
                                               measured=time.monotonic() - self.manual_deadline + MANUAL_DECISION_S,
                                               limit=MANUAL_DECISION_S, remedy="Respond to the next book within the decision window.")
                        self.pending = "HOLD"
                    verdict = (
                        self.pending
                        if self.key and self.board.get("phase") == "WAIT_AI"
                        else "WAIT"
                    )
                    health = self.health()
                    readiness_issue = None
                    if health:
                        camera = self.vision.last_camera_issue if self.vision else None
                        readiness_issue = (
                            camera if camera and camera["message"] == health
                            else dict(code="PC_NOT_READY", message=health)
                        )
                    board = await ctrl.exchange(boot, not health, self.board.get("job", 0), verdict)
                    if ctrl is not self.ctrl:
                        boot = "-"
                        continue
                    boot = board["boot"]
                    self.link_error = ""
                    self.observe(board, readiness_issue)
                    await asyncio.sleep(self.cfg["heartbeat_s"])
                except Exception as exc:
                    if ctrl is not self.ctrl:
                        continue
                    self.link_error = str(exc) or type(exc).__name__
                    if self.board.get("phase") not in (None, "OFF", "FAULT"):
                        self.record_stop("FAULT", "LINK_LOST", self.key)
                    self.board = {}
                    self.end_job("UNCONFIRMED", "LINK_LOST")
                    await ctrl.close()
                    boot = "-"
                    await asyncio.sleep(0.5)
        finally:
            self.end_job("UNCONFIRMED", "SERVICE_STOPPED")
            await self.ctrl.close()

    async def stop(self):
        self.service.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await self.service
        if self.vision:
            await asyncio.to_thread(self.vision.close)
        self.store.db.close()

    def is_idle(self):
        return (
            not self.busy
            and not self.key
            and self.board.get("phase", "OFF") in ("OFF", "FAULT")
        )

    def require_idle(self):
        if not self.is_idle():
            raise ValueError("Tắt trạm bằng nút vật lý trước")

    async def connect_serial(self, port):
        self.require_idle()
        if self.mode == "simulation":
            raise ValueError("Đang mô phỏng")
        new_ctrl = SerialController(port, bridge_port=self.cfg.get("bridge_diagnostic_port", ""))
        save_json(self.serial_path, dict(port=port))
        old = self.ctrl
        self.port = port
        self.ctrl = new_ctrl
        self.board = {}
        self.link_error = "Đang kết nối USB"
        await old.close()

    def initialize_settings(self):
        from software.inspection.settings import station_defaults, validate_settings
        from vision.opencv.config import load_config

        filename = "simulation-vision-settings.json" if self.mode == "simulation" else "vision-settings.json"
        self.settings_path = self.folder / filename
        if self.mode == "hardware-manual":
            self.settings_defaults = self.settings_values = {}
            self.calibration_error = None
            return
        self.calibration_error = None
        geometry = self.vision.geometry if self.vision else load_config()
        self.settings_defaults = station_defaults(self.cfg, geometry)
        self.settings_values = validate_settings(self.settings_defaults, {})
        if self.vision:
            self.vision.folder = self.folder
        try:
            if self.settings_path.is_file():
                overrides = json.loads(self.settings_path.read_text(encoding="utf8"))
                self.settings_values = validate_settings(self.settings_defaults, overrides)
        except (OSError, ValueError) as exc:
            if self.vision:
                self.vision.settings_error = f"Invalid station settings: {exc}. Reset settings."
        if self.vision and self.vision.direct_routing:
            self.direct_base = self.settings_values.copy()
            self.settings_path = self.folder / "direct-vision-settings.json"
            if self.settings_path.is_file():
                try:
                    self.settings_values = validate_settings(self.direct_base, json.loads(self.settings_path.read_text(encoding="utf8")))
                except (ValueError, OSError) as exc:
                    self.vision.settings_error = str(exc)
        self.cfg.update(self.settings_values)
        if self.vision:
            self.vision.apply_settings(self.settings_values)

    def settings_status(self):
        from software.inspection.settings import LIMITS

        thresholds = self.vision.thresholds if self.vision else None
        return {
            "values": self.settings_values,
            "defaults": self.settings_defaults,
            "limits": LIMITS,
            "calibration": {
                "valid": thresholds is not None,
                "error": self.calibration_error,
                "thresholds": thresholds,
            },
        }

    async def update_settings(self, values, reset=False):
        from software.inspection.settings import validate_settings

        self.require_idle()
        if self.mode == "hardware-manual":
            raise ValueError("Vision settings are available in automatic mode and simulation.")
        base = self.settings_defaults if reset else self.settings_values
        direct = self.vision and self.vision.direct_routing
        if direct:
            if set(values) - {"stabilize_s"}:
                raise ValueError("Chỉ chỉnh thời gian ổn định trong AI trực tiếp")
            if reset:
                base = self.direct_base
        updated = validate_settings(base, {} if reset else values)
        if self.vision and not self.vision.work.acquire(blocking=False):
            raise ValueError("Wait for the current vision operation to finish.")
        try:
            if updated != self.settings_values or reset or (self.vision and self.vision.settings_error):
                if self.vision and not direct:
                    self.invalidate_profile()
                save_json(self.settings_path, ({} if reset else {"stabilize_s": updated["stabilize_s"]}) if direct else updated)
                self.settings_values = updated
                self.cfg.update(updated)
                if self.vision:
                    self.vision.apply_settings(updated)
                    self.vision.settings_error = ""
                self.sample_result = None
        finally:
            if self.vision:
                self.vision.work.release()
        return self.settings_status()

    async def pilot(self, book, truth, split):
        self.require_idle()
        if not self.vision:
            raise ValueError("Calibration requires the station camera.")
        if not isinstance(book, str) or not book.strip() or truth not in ("OK", "NG") or split not in ("cal", "test"):
            raise ValueError("Enter a known book ID, truth, and calibration or test split.")
        if self.vision.settings_error:
            raise ValueError(self.vision.settings_error)
        provenance = self.vision.provenance_key()
        if not provenance:
            raise ValueError("Load the model and capture the empty belt first.")
        self.busy = True
        cancelled = threading.Event()
        try:
            r = await asyncio.to_thread(self.vision.inspect, time.monotonic(), cancelled)
            if provenance != self.vision.provenance_key():
                raise ValueError("Vision inputs changed during sampling. Retake this sample.")
            self.invalidate_profile()
            self.store.sample(book.strip(), truth, split, r, provenance)
            self.sample_result = dict(
                label=r.label, confidence=r.confidence, truth=truth, book=book.strip()
            )
            return self.sample_result
        finally:
            cancelled.set()
            self.busy = False

    def invalidate_profile(self):
        self.vision.thresholds = None
        self.calibration_error = None
        (self.folder / "thresholds.json").unlink(missing_ok=True)

    def calibration_failure(self, code, message, remedy, **details):
        self.calibration_error = dict(code=code, message=message, remedy=remedy, **details)
        raise CalibrationFailure(self.calibration_error)

    def calibrate_thresholds(self):
        from software.inspection.settings import decide_prediction

        self.require_idle()
        if not self.vision:
            raise ValueError("Calibration requires the station camera.")
        self.invalidate_profile()
        model = self.vision.classifier
        provenance = self.vision.provenance_key()
        if self.vision.settings_error or not provenance:
            self.calibration_failure(
                "CALIBRATION_INPUTS", "Calibration inputs are missing or invalid.",
                "Use Manual Mechanics now without a model. For automatic sorting, load a compatible classifier, "
                "capture the empty belt, and validate with independent known books.",
            )
        rows = self.store.db.execute(
            "SELECT book,truth,split,label,confidence FROM samples WHERE model_hash=? AND provenance=?",
            (model.checksum, provenance),
        ).fetchall()
        thresholds = {}
        for route in ("OK", "NG"):
            pool = [
                r for r in rows
                if r["split"] == "cal" and model.mapping.get(r["label"]) == route
            ]
            matches = [r for r in pool if r["truth"] == route]
            if not matches:
                mislabeled = [r for r in rows if r["split"] == "cal" and r["truth"] == route]
                if mislabeled:
                    example = max(mislabeled, key=lambda r: r["confidence"])
                    predicted = model.mapping[example["label"]]
                    threshold = self.cfg["min_confidence"][predicted]
                    decision = decide_prediction(
                        predicted, example["confidence"], {predicted: threshold}, self.cfg["uncertain_policy"]
                    )
                    self._known_book_failure(example, predicted, threshold, decision)
                self.calibration_failure(
                    "CALIBRATION_COVERAGE", f"No correctly predicted {route} calibration sample.",
                    "Retake known books with the current model, geometry, background, and settings. "
                    "Use Manual Mechanics for belt testing in the meantime.",
                )
            wrong = [r["confidence"] for r in pool if r["truth"] != route]
            floor = self.cfg["min_confidence"][route]
            threshold = max(floor, max(wrong, default=0) + 0.000001)
            best = max(matches, key=lambda r: r["confidence"])
            if best["confidence"] < threshold:
                self._known_book_failure(best, route, threshold, "HOLD")
            thresholds[route] = threshold
        test = [r for r in rows if r["split"] == "test"]
        if {r["truth"] for r in test} != {"OK", "NG"}:
            self.calibration_failure(
                "TEST_COVERAGE", "Independent tests require known OK and NG books.",
                "Use different books for calibration and independent testing. "
                "Use Manual Mechanics for belt testing in the meantime.",
            )
        stats = {"OK": 0, "NG": 0, "HOLD": 0, "wrong_ok": 0, "wrong_ng": 0}
        correct = set()
        misses = []
        policy = self.cfg["uncertain_policy"]
        for r in test:
            route = model.mapping[r["label"]]
            result = decide_prediction(route, r["confidence"], thresholds, policy)
            stats[result] += 1
            if result == r["truth"]:
                correct.add(result)
            else:
                misses.append((r, route, thresholds[route], result))
                if result != "HOLD":
                    stats["wrong_" + result.lower()] += 1
        for miss in misses:
            row, _, _, result = miss
            if result == "OK" or row["truth"] not in correct:
                self._known_book_failure(*miss)
        profile = dict(
            provenance=self.vision.provenance(),
            sha256=model.checksum,
            classes=model.mapping,
            image_size=model.size,
            thresholds=thresholds,
            test=stats,
            test_books=len({r["book"] for r in test}),
        )
        return profile

    async def validate_known_books(self):
        from software.inspection.reference import REFERENCE_SHA256, inspect_reference
        from software.inspection.settings import decide_prediction

        def check_reference():
            with self.vision.work:
                return inspect_reference(self.vision.classifier)

        profile = self.calibrate_thresholds()
        self.busy = True
        try:
            try:
                reference = await asyncio.to_thread(check_reference)
                if reference["book"] != "IMG_7" or reference["truth"] != "NG":
                    raise ValueError("Reference identity or truth does not match")
                route = profile["classes"][reference["label"]]
                confidence = reference["confidence"]
                if type(confidence) not in (int, float) or not 0 <= confidence <= 1:
                    raise ValueError("Reference model returned invalid confidence")
            except Exception as exc:
                self.calibration_failure(
                    "REFERENCE_ERROR", f"IMG_7 could not be checked: {exc}",
                    "Use Manual Mechanics now without a model. Restore the IMG_7 reference and verify the configured "
                    "classifier before repeating calibration and independent testing.",
                    book="IMG_7", truth="NG",
                )
            if profile["provenance"] != self.vision.provenance():
                self.calibration_failure(
                    "CALIBRATION_INPUTS", "Vision inputs changed during validation.",
                    "Keep sorting stopped and repeat calibration after the changes.",
                )
            thresholds = profile["thresholds"]
            verdict = decide_prediction(route, confidence, thresholds, self.cfg["uncertain_policy"])
            if verdict == "OK":
                self._known_book_failure(reference, route, thresholds[route], verdict)
            profile["reference"] = dict(reference, sha256=REFERENCE_SHA256, decision=verdict)
            save_json(self.folder / "thresholds.json", profile)
            self.vision.thresholds = thresholds
            return profile
        finally:
            self.busy = False

    def _known_book_failure(self, row, route, threshold, result):
        self.calibration_failure(
            "KNOWN_BOOK_FAILURE",
            f"{row['book']}: expected {row['truth']}, predicted {row['label']} "
            f"({row['confidence']:.3f}, threshold {threshold:.3f}), decision {result}.",
            "Use Manual Mechanics now on this PC without a model. Keep automatic sorting stopped. "
            "Check lighting and framing, or switch to a compatible classifier and repeat calibration "
            "with independent known books. Strict NG only affects valid, low-confidence images. "
            "A high-confidence false OK requires a corrected classifier or a profile that passes independent tests.",
            book=row["book"], truth=row["truth"], label=row["label"],
            confidence=row["confidence"], threshold=threshold, route=route, decision=result,
        )


    def status(self):
        counts, jobs = self.store.summary()
        return dict(
            mode=self.mode,
            board=self.board,
            last_board=self.last_board,
            board_age_s=time.monotonic() - self.board_seen if self.board_seen is not None else None,
            bridge=({**self.ctrl.bridge, "age_s": time.monotonic() - self.ctrl.bridge["seen"]} if getattr(self.ctrl, "bridge", None) else None),
            shift_id=self.store.db.execute("SELECT max(id) FROM shifts").fetchone()[0],
            port=self.port,
            connected_port=self.ctrl.port if self.mode != "simulation" and self.board else "",
            link_error=self.link_error,
            health=self.health(),
            direct_routing=bool(self.vision and self.vision.direct_routing),
            camera=self.vision.camera_status()
            if self.vision
            else (
                "Mất camera mô phỏng"
                if self.mode == "simulation" and not self.ctrl.camera_ok
                else ""
            ),
            diagnostics=self.vision.diagnostics_status() if self.vision else {},
            last_stop=self.last_stop,
            idle=self.is_idle(),
            manual_remaining_s=self.manual_remaining(),
            manual_decision=self.manual_decision_status(),
            simulation_image=bool(self.simulation_preview),
            simulation_image_version=self.simulation_photo.version if self.simulation_photo else None,
            counts=counts,
            jobs=jobs,
            pilot=self.sample_result,
        )
