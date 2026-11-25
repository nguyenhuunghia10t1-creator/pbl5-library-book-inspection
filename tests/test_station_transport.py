import asyncio
import json
import re
import time
import sys
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch

from software.controller.transport import SerialController


BOOT = "a" * 32
JOB_ID = f"{BOOT}-2"


class FakeSerial:
    def __init__(self, **options):
        self.options = options
        self.writes = []
        self.rx = bytearray()
        self.boot = BOOT
        self.phase = "WAIT_AI"
        self.capture = JOB_ID
        self.ack = True
        self.silent = False
        self.closed = False
        self.drop_writes = 0
        self.extra = ""

    def open(self):
        assert self.dtr is False and self.rts is False
        assert self.options["baudrate"] == 115200
        self.closed = False

    def close(self):
        self.closed = True

    def reset_input_buffer(self):
        self.rx.clear()

    @property
    def in_waiting(self):
        return len(self.rx)

    def read(self, limit):
        data = bytes(self.rx[: min(limit, 7)])
        del self.rx[: len(data)]
        if not data:
            time.sleep(0.01)
        return data

    def write(self, packet):
        lines = packet.decode("ascii").splitlines()
        if lines == ["BRIDGE?"]:
            self.rx.extend(b"PBL5_BRIDGE,1,RADIO_READY,00:11:22:33:44:55,CH=1,TX_QUEUE=1,RX=1\n")
            return len(packet)
        self.writes.append(lines)
        ping, seq, boot, ready = lines[-1].split(",")
        assert ping == "PING" and re.fullmatch("[0-9a-f]{8}", seq)
        assert ready in ("0", "1")
        if self.silent or len(self.writes) <= self.drop_writes:
            return len(packet)
        startup = boot == "-"
        frames = ["boot chatter", "!" * 513] if startup else []
        if self.extra:
            frames.append(self.extra)
        if len(lines) > 1:
            command = lines[0].split(",")
            verdict = command[2] if len(command) == 3 else "HOLD"
            if self.ack:
                frames.append(f"ACK,{command[1]},{verdict}")
        if self.capture and not startup:
            frames.append(f"CAPTURE,{self.capture}")
        reply = dict(
            v=1, seq=seq, boot=self.boot, job=2, completed=1, phase="OFF" if startup else self.phase,
            ir=True, pwm=0, servo=0, reason="",
        )
        if startup:
            frames.append(json.dumps(dict(reply, seq="expired-request", phase="OFF")))
        frames.append(json.dumps(reply))
        self.rx.extend(("\r\n".join(frames) + "\r\n").encode("ascii"))
        return len(packet)


class StationWireTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.device = FakeSerial(baudrate=115200)
        serial = ModuleType("serial")
        serial.Serial = self.factory = Mock(return_value=self.device)
        serial_tools = ModuleType("serial.tools")
        serial_tools.list_ports = SimpleNamespace(comports=Mock())
        self.ports = serial_tools.list_ports.comports
        self.enterContext(patch.dict(sys.modules, {
            "serial": serial,
            "serial.tools": serial_tools,
        }))
        self.ports.return_value = [
            SimpleNamespace(device="COM8", vid=0x10C4, pid=0xEA60),
            SimpleNamespace(device="COM9", vid=None, pid=None),
        ]
        self.ctrl = SerialController(bridge_port="COM8")
        self.addAsyncCleanup(self.ctrl.close)

    async def test_handshake_capture_result_and_ack(self):
        hello = await self.ctrl.exchange("-", True, 2, "OK")
        self.assertEqual(hello["boot"], BOOT)
        self.assertIsNone(hello["capture_id"])
        self.assertEqual(self.ctrl.bridge["radio"], "RADIO_READY")
        self.assertEqual(self.ctrl.port, "COM8")
        self.assertEqual(self.ctrl.configured_port, "")
        self.assertEqual(len(self.device.writes[0]), 1)
        self.assertTrue(self.device.writes[0][0].endswith(",-,0"))
        for route, phase, command in (("OK", "RELEASE", f"RESULT,{JOB_ID},PASS"),
                                      ("NG", "PUSH", f"RESULT,{JOB_ID},FAIL"),
                                      ("HOLD", "FAULT", f"HOLD,{JOB_ID}")):
            self.device.phase, self.device.capture = "WAIT_AI", JOB_ID
            self.assertEqual((await self.ctrl.exchange(BOOT, True))["capture_id"], JOB_ID)
            self.device.phase, self.device.capture = phase, None
            self.assertEqual((await self.ctrl.exchange(BOOT, True, 2, route))["ack"], route)
            self.assertEqual(self.device.writes[-1][0], command)

    async def test_stale_events_and_unready_suppress_decision(self):
        await self.ctrl.exchange("-")
        await self.ctrl.exchange(BOOT, True)
        self.device.phase, self.device.capture = "FAULT", None
        reply = await self.ctrl.exchange(BOOT, False, 2, "NG")
        self.assertIsNone(reply["ack"])
        self.assertEqual(len(self.device.writes[-1]), 1)
        self.assertTrue(self.device.writes[-1][0].endswith(f",{BOOT},0"))

    async def test_malformed_stale_missing_capture_and_lost_ack_close_link(self):
        for noise, capture, send in (("?" * 513, JOB_ID, False), ("RESULT", JOB_ID, False),
                                     ("", f"{BOOT}-1", False), ("", None, False),
                                     (f"ACK,{BOOT}-1,FAIL", None, True), ("", None, True)):
            with self.subTest(noise=noise[:3], capture=capture, send=send):
                self.device.extra = ""
                self.device.phase, self.device.capture = "WAIT_AI", JOB_ID
                await self.ctrl.exchange("-")
                await self.ctrl.exchange(BOOT, True)
                self.device.extra, self.device.capture = noise, capture
                self.device.ack = False
                self.device.phase = "PUSH" if send else "WAIT_AI"
                with self.assertRaises(ValueError):
                    await self.ctrl.exchange(BOOT, True, 2, "NG" if send else "WAIT")
                self.assertIsNone(self.ctrl.port)

    async def test_boot_delay_retries_without_reopening_or_sending_result(self):
        self.device.drop_writes = 1
        self.assertEqual((await self.ctrl.exchange("-", True, 2, "OK"))["phase"], "OFF")
        self.factory.assert_called_once()
        self.assertEqual(len(self.device.writes), 2)
        self.assertTrue(all(len(lines) == 1 and lines[0].endswith(",-,0") for lines in self.device.writes))

    async def test_reboot_requires_new_handshake(self):
        await self.ctrl.exchange("-")
        self.device.boot = "b" * 32
        with self.assertRaisesRegex(ValueError, "khởi động lại"):
            await self.ctrl.exchange(BOOT)
        self.assertTrue(self.device.closed)
        self.assertIsNone(self.ctrl.port)
        with self.assertRaises(ValueError):
            await self.ctrl.exchange(BOOT, True, 2, "NG")
        reply = await self.ctrl.exchange("-")
        self.assertEqual(reply["boot"], "b" * 32)
        self.assertIsNone(reply["capture_id"])
        self.assertTrue(self.device.writes[-1][0].endswith(",-,0"))

    async def test_no_matching_or_ambiguous_port_and_explicit_override(self):
        self.ports.return_value = self.ports.return_value[1:]
        with self.assertRaises(OSError):
            await self.ctrl.exchange("-")
        self.ports.return_value = [
            SimpleNamespace(device=port, vid=0x10C4, pid=0xEA60)
            for port in ("COM8", "COM9")
        ]
        with self.assertRaises(OSError):
            await self.ctrl.exchange("-")
        self.factory.assert_not_called()
        with self.assertRaises(ValueError):
            SerialController("not-a-com-port")
        explicit = SerialController(" com5 ")
        self.addAsyncCleanup(explicit.close)
        await explicit.exchange("-")
        self.assertEqual(explicit.configured_port, "COM5")
        self.assertEqual(explicit.port, "COM5")

    async def test_timeout_keeps_event_loop_responsive_and_releases_port(self):
        await self.ctrl.exchange("-")
        self.device.silent = True
        exchange = asyncio.create_task(self.ctrl.exchange(BOOT))
        await asyncio.sleep(0.05)
        self.assertFalse(exchange.done())
        with self.assertRaises(TimeoutError):
            await asyncio.wait_for(exchange, 1.0)
        self.assertTrue(self.device.closed)
        self.assertIsNone(self.ctrl.port)

    async def test_cancel_waits_for_serial_worker_before_closing(self):
        await self.ctrl.exchange("-")
        self.device.silent = True
        exchange = asyncio.create_task(self.ctrl.exchange(BOOT))
        await asyncio.sleep(0.05)
        exchange.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await asyncio.wait_for(exchange, 1.0)
        self.assertTrue(self.device.closed)
        self.assertIsNone(self.ctrl.port)
