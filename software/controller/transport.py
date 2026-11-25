"""USB serial transport for the inspection station."""

import asyncio
import contextlib
import json
import re
import secrets
import time


MAX_JOB = 0xFFFFFFFF


def _validate_reply(reply, boot):
    if (
        not isinstance(reply, dict)
        or type(reply.get("v")) is not int
        or reply["v"] != 1
        or not isinstance(reply.get("boot"), str)
        or not re.fullmatch("[0-9a-f]{32}", reply["boot"])
        or reply.get("phase")
        not in (
            "OFF",
            "RUN",
            "WAIT_AI",
            "PUSH",
            "RETRACT",
            "SETTLE",
            "RELEASE",
            "FAULT",
        )
        or type(reply.get("job")) is not int
        or not 0 <= reply["job"] <= MAX_JOB
        or type(reply.get("completed")) is not int
        or not 0 <= reply["completed"] <= MAX_JOB
        or type(reply.get("ir")) is not bool
        or type(reply.get("pwm")) is not int
        or not 0 <= reply["pwm"] <= 1023
        or type(reply.get("servo")) is not int
        or not 0 <= reply["servo"] <= 180
        or reply["completed"] > reply["job"]
        or (reply["phase"] not in ("RUN", "RELEASE") and reply["pwm"] != 0)
        or not isinstance(reply.get("reason"), str)
    ):
        raise ValueError("Bản tin ESP32 không hợp lệ")
    if boot != "-" and reply["boot"] != boot:
        raise ValueError("ESP32 đã khởi động lại")


class SerialController:
    """A USB-UART heartbeat with one outstanding exchange."""

    def __init__(self, port="", *, bridge_port=""):
        self.configured_port = port.strip().upper()
        if self.configured_port and not re.fullmatch(r"COM[1-9][0-9]*", self.configured_port):
            raise ValueError("Nhập tên cổng USB, ví dụ COM5")
        self.bridge_port = bridge_port.upper()
        self.bridge = None
        self.port = None
        self._device = None
        self._boot = None
        self._capture_id = None
        self._rx = bytearray()
        self._lock = asyncio.Lock()

    def _open(self):
        import serial
        from serial.tools import list_ports

        port = self.configured_port
        if not port:
            # The project board uses a CP210x USB-UART bridge.
            matches = [
                entry.device
                for entry in list_ports.comports()
                if (entry.vid, entry.pid) == (0x10C4, 0xEA60)
            ]
            if not matches:
                raise OSError("Chưa tìm thấy ESP32 CP210x qua USB. Chọn cổng COM nếu dùng adapter khác.")
            if len(matches) > 1:
                raise OSError("Có nhiều cổng CP210x. Chọn cổng COM của ESP32.")
            port = matches[0]
        device = serial.Serial(baudrate=115200, timeout=0.03, write_timeout=0.20)
        # Deassert both modem-control lines before opening an auto-reset board.
        device.dtr = False
        device.rts = False
        device.port = port
        try:
            device.open()
            device.reset_input_buffer()
        except Exception:
            device.close()
            raise
        self._device, self.port = device, port
        self.bridge = None
        # Legacy USB receivers treat BRIDGE? as a malformed motion-protocol frame.
        if port.upper() != self.bridge_port:
            return
        device.write(b"BRIDGE?\n")
        for line in self._lines(time.monotonic() + 0.18, True):
            if line.startswith("PBL5_BRIDGE,1,"):
                self.bridge = dict(port=port, radio=line.split(",")[2], seen=time.monotonic())
                break

    def _close(self):
        device = self._device
        if device is not None and self._boot:
            # If the wire is still usable, withdraw permission immediately.
            # The ESP32 watchdog also covers a physically disconnected cable.
            with contextlib.suppress(OSError):
                device.write(f"PING,{secrets.token_hex(4)},{self._boot},0\n".encode("ascii"))
        self._device = self._boot = self._capture_id = self.port = None
        self._rx.clear()
        if device is not None:
            device.close()

    async def close(self):
        async with self._lock:
            await self._worker(self._close)

    async def _worker(self, operation, *args):
        worker = asyncio.create_task(asyncio.to_thread(operation, *args))
        try:
            return await asyncio.shield(worker)
        except asyncio.CancelledError:
            # Keep the lock until bounded serial I/O stops using this handle.
            with contextlib.suppress(Exception):
                await worker
            raise

    async def exchange(self, boot, ready=False, job=0, decision="WAIT"):
        async with self._lock:
            try:
                return await self._worker(self._exchange, boot, ready, job, decision)
            except (Exception, asyncio.CancelledError):
                await self._worker(self._close)
                raise

    def _exchange(self, boot, ready, job, decision):
        if boot != "-" and boot != self._boot:
            raise ValueError("Cần bắt tay lại với ESP32")
        if self._device is None:
            self._open()

        # Some USB bridges reset the board on open. Retry only the inert
        # handshake on this same handle, never a motion decision.
        for attempt in range(3 if boot == "-" else 1):
            try:
                return self._roundtrip(boot, ready, job, decision)
            except TimeoutError:
                if boot != "-" or attempt == 2:
                    raise

    def _roundtrip(self, boot, ready, job, decision):
        seq = secrets.token_hex(4)
        decision_line = ""
        matching_ack = None
        ready = ready and boot != "-"
        if ready and decision != "WAIT":
            job_id = f"{boot}-{job}"
            if job_id != self._capture_id or decision not in ("OK", "NG", "HOLD"):
                raise ValueError("Kết quả không khớp yêu cầu CAPTURE")
            verdict = {"OK": "PASS", "NG": "FAIL", "HOLD": "HOLD"}[decision]
            decision_line = (f"HOLD,{job_id}\n" if verdict == "HOLD"
                             else f"RESULT,{job_id},{verdict}\n")
            matching_ack = f"ACK,{job_id},{verdict}"

        request = f"{decision_line}PING,{seq},{boot},{int(ready)}\n".encode("ascii")
        if self._device.write(request) != len(request):
            raise OSError("Gửi lệnh USB tới ESP32 chưa hoàn tất")

        ack = None
        captures = set()
        startup = boot == "-"
        for line in self._lines(time.monotonic() + 0.75, startup):
            if line == matching_ack:
                ack = decision
            elif line.startswith("CAPTURE,"):
                capture = line.removeprefix("CAPTURE,")
                if not re.fullmatch(r"[0-9a-f]{32}-[1-9][0-9]{0,9}", capture):
                    raise ValueError("ID trong CAPTURE không hợp lệ")
                captures.add(capture)
            elif line.startswith("{"):
                try:
                    reply = json.loads(line)
                except ValueError:
                    if startup:
                        continue
                    raise
                if not isinstance(reply, dict) or reply.get("seq") != seq:
                    if startup:
                        continue
                    raise ValueError("Trạng thái USB không khớp lượt hỏi")
                _validate_reply(reply, boot)
                if matching_ack and not ack:
                    raise ValueError("Thiếu ACK của ESP32 cho kết quả vừa gửi")
                self._boot = reply["boot"]
                job_id = f"{self._boot}-{reply['job']}"
                if startup and reply["phase"] not in ("OFF", "FAULT"):
                    raise ValueError("ESP32 phải dừng khi bắt tay USB")
                if reply["phase"] == "WAIT_AI" and captures != {job_id}:
                    raise ValueError("Thiếu CAPTURE đúng mã sách")
                if captures - {job_id}:
                    raise ValueError("CAPTURE không khớp trạng thái ESP32")
                self._capture_id = job_id if reply["phase"] == "WAIT_AI" else None
                reply["capture_id"] = self._capture_id
                reply["ack"] = ack
                return reply
            elif not startup:
                raise ValueError("Bản tin USB hoặc ACK không hợp lệ")
        raise TimeoutError(f"ESP32 không phản hồi qua {self.port} ở 115200 baud")

    def _lines(self, deadline, startup):
        # Keep bytes after a status line: an unsolicited CAPTURE can arrive
        # in the very same USB read and belongs to the next exchange.
        while time.monotonic() < deadline:
            end = self._rx.find(b"\n")
            if end >= 0:
                line = bytes(self._rx[:end]).removesuffix(b"\r")
                del self._rx[:end + 1]
                if len(line) <= 512 and line.isascii():
                    yield line.decode("ascii")
                elif not startup:
                    raise ValueError("Dòng USB quá dài hoặc sai mã ASCII")
                continue
            if len(self._rx) > 512:
                if not startup:
                    raise ValueError("Dòng USB quá dài")
                self._rx.clear()
            self._rx.extend(self._device.read(min(self._device.in_waiting or 1, 512)))
