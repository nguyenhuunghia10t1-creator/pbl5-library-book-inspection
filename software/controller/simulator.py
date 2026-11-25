"""Operator-driven simulator. It opens neither a socket nor a camera."""

import time
import uuid


class Simulator:
    def __init__(self):
        self.boot = uuid.uuid4().hex
        self.phase, self.reason = "OFF", "STARTUP"
        self.job = self.completed = 0
        self.ir = self.ready = False
        self.since = self.beat = self.clear_since = time.monotonic()
        self.return_started = self.since - 3
        self.motor_started = self.since
        self.camera_ok = self.ai_ok = self.online = True
        self.choice = "OK"

    def enter(self, phase, reason=""):
        if phase in ("FAULT", "OFF") and self.phase in ("PUSH", "RETRACT"):
            self.return_started = time.monotonic()
        if phase == "RETRACT":
            self.return_started = time.monotonic()
        if phase in ("RUN", "RELEASE") and self.phase not in ("RUN", "RELEASE"):
            self.motor_started = time.monotonic()
        self.phase, self.reason, self.since = phase, reason, time.monotonic()

    def event(self, action):
        now = time.monotonic()
        if action == "button":
            if self.phase not in ("OFF", "FAULT"):
                self.enter("OFF", "MANUAL_OFF")
                return
            if not self.online:
                self.reason = "LINK_LOST"
            elif not self.ready or now - self.beat >= 1:
                self.reason = "PC_NOT_READY"
            elif self.ir or now - self.clear_since < 0.18:
                self.reason = "CLEAR_STATION"
            elif now - self.return_started < 2.7:
                self.reason = "RETURN_WAIT"
            else:
                self.enter("RUN")
                return
            raise ValueError(self.reason)
        elif action in ("insert", "remove"):
            if action == "remove" and self.ir:
                self.clear_since = now
            self.ir = action == "insert"
            if self.ir and self.phase == "RUN":
                self.job += 1
                self.enter("WAIT_AI")
        elif action in ("OK", "NG", "HOLD"):
            self.choice = action
        elif action in ("link", "wifi"):
            self.online = not self.online
            if not self.online:
                self.ready = False
                self.enter("FAULT", "LINK_LOST")
        elif action == "camera":
            self.camera_ok = not self.camera_ok
        elif action == "ai":
            self.ai_ok = not self.ai_ok
        else:
            raise ValueError("Sự kiện mô phỏng không hợp lệ")

    async def exchange(self, boot, ready=False, job=0, decision="WAIT"):
        if not self.online:
            raise ConnectionError("Mất kết nối USB mô phỏng")
        if boot not in ("-", self.boot):
            raise ValueError("Sai phiên")
        now = time.monotonic()
        if self.phase not in ("OFF", "FAULT") and (
            not ready or now - self.beat >= 1 or boot == "-"
        ):
            self.enter("FAULT", "PC_NOT_READY")
        self.ready = ready and boot != "-"
        self.beat = now
        ack = None
        elapsed = now - self.since
        clear = not self.ir and now - self.clear_since >= 0.18
        if self.phase == "WAIT_AI":
            if clear or elapsed >= 10:
                self.enter("FAULT", "BOOK_MOVED" if clear else "AI_TIMEOUT")
            elif job == self.job and decision in ("OK", "NG", "HOLD") and not self.ir:
                self.enter("FAULT", "BOOK_MOVED")
            elif job == self.job and decision in ("OK", "NG", "HOLD"):
                ack = decision
                if decision == "OK":
                    self.enter("RELEASE")
                elif decision == "NG":
                    self.enter("PUSH")
                else:
                    self.enter("FAULT", "INSPECTION_HOLD")
        elif self.phase == "PUSH" and elapsed >= 0.7:
            self.enter("RETRACT")
        elif self.phase == "RETRACT" and elapsed >= 0.7:
            self.enter("SETTLE")
        elif self.phase == "SETTLE" and elapsed >= 2:
            if clear:
                self.completed = self.job
                self.enter("RUN")
            else:
                self.enter("FAULT", "NG_NOT_CLEAR")
        elif self.phase == "RELEASE":
            if clear:
                self.completed = self.job
                self.enter("RUN")
            elif elapsed >= 5:
                self.enter("FAULT", "RELEASE_JAM")
        return dict(
            v=1,
            boot=self.boot,
            phase=self.phase,
            capture_id=f"{self.boot}-{self.job}" if self.phase == "WAIT_AI" else None,
            ack=ack,
            job=self.job,
            completed=self.completed,
            ir=self.ir,
            pwm=min(1023, int(max(0, now - self.motor_started) * 1023 / 2))
            if self.phase in ("RUN", "RELEASE")
            else 0,
            servo=180 if self.phase == "PUSH" else 0,
            reason=self.reason,
        )

    async def close(self):
        self.ready = False
