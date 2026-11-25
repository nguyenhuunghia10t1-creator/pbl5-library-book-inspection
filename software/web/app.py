from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
import asyncio
import base64
import json

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from software.inspection.runtime import CalibrationFailure, Runtime, ROOT, DATA

ASSETS = Path(__file__).with_name("static")


class Connect(BaseModel, extra="forbid"):
    port: str = Field(
        default="", max_length=16, pattern=r"^(?:[Cc][Oo][Mm][1-9][0-9]*)?$"
    )


class Sample(BaseModel):
    book: str = Field(min_length=1, max_length=100)
    truth: str = Field(pattern=r"^(OK|NG)$")
    split: str = Field(pattern=r"^(cal|test)$")


class ManualDecision(BaseModel, extra="forbid"):
    key: str = Field(pattern=r"^[a-f0-9]{32}-[1-9][0-9]{0,9}$")
    verdict: Literal["OK", "NG"]


class SettingsChange(BaseModel, extra="forbid"):
    values: dict = Field(default_factory=dict)
    reset: bool = False


def create_app(simulation=False, folder=DATA, *, camera_test=False, manual=False, direct=False):
    if sum(map(bool, (simulation, camera_test, manual, direct))) > 1:
        raise ValueError("Choose one station mode.")
    capture_lock = asyncio.Lock()

    @asynccontextmanager
    async def lifespan(app):
        if camera_test:
            from vision.yolo.station import StationVision

            cfg = json.loads((ROOT / "configs/station.json").read_text(encoding="utf8"))
            vision = StationVision(cfg, camera_test=True)
            app.state.vision = vision
            vision.start()
            try:
                yield
            finally:
                await asyncio.to_thread(vision.close)
            return

        rt = Runtime(simulation, folder, manual=manual, direct=direct)
        app.state.runtime = rt
        app.state.vision = rt.vision
        rt.start()
        try:
            yield
        finally:
            await rt.stop()

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "testserver"]
    )

    @app.middleware("http")
    async def local_writes(request: Request, call_next):
        if request.method == "POST" and request.headers.get("origin") not in (
            None,
            str(request.base_url).rstrip("/"),
        ):
            return Response(status_code=403)
        return await call_next(request)

    @app.exception_handler(ValueError)
    async def bad_request(request, exc):
        from fastapi.responses import JSONResponse

        return JSONResponse({"detail": str(exc)}, status_code=409)

    @app.get("/")
    async def home():
        return FileResponse(ASSETS / ("camera.html" if camera_test else "index.html"))

    @app.get("/guide")
    async def guide():
        return FileResponse(ROOT / "docs" / "STATION_QUICKSTART.html")

    @app.get("/api/status")
    async def status():
        if camera_test:
            return {"mode": "camera-test", "camera": app.state.vision.camera_status()}
        return app.state.runtime.status()

    @app.get("/api/live.jpg")
    async def live():
        v = app.state.vision
        if camera_test:
            if issue := v.camera_status():
                raise ValueError(issue)
        if not v or (not camera_test and v.camera_status()) or not v.live_jpg:
            return Response(status_code=204)
        return Response(
            v.live_jpg, media_type="image/jpeg", headers={"Cache-Control": "no-store"}
        )

    @app.get("/api/live.mjpg")
    async def live_stream():
        vision = app.state.vision
        if not vision or vision.camera_status() or not vision.live_jpg:
            return Response(status_code=503, headers={"Cache-Control": "no-store"})

        async def frames():
            previous = None
            while not vision.closed.is_set():
                frame = None if vision.camera_status() else vision.live_jpg
                if frame and frame is not previous:
                    previous = frame
                    yield (b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "
                           + str(len(frame)).encode("ascii") + b"\r\n\r\n" + frame + b"\r\n")
                await asyncio.sleep(1 / 60)
            yield b"--frame--\r\n"

        return StreamingResponse(frames(), media_type="multipart/x-mixed-replace; boundary=frame",
                                 headers={"Cache-Control": "no-store"})

    app.mount("/static", StaticFiles(directory=ASSETS), name="static")
    if camera_test:
        @app.post("/api/capture")
        async def capture():
            if capture_lock.locked():
                raise ValueError("Đang phân loại ảnh vừa chụp")
            async with capture_lock:
                try:
                    verdict, label, confidence, image = await asyncio.to_thread(
                        app.state.vision.classify_snapshot
                    )
                except FileNotFoundError as exc:
                    raise ValueError("Thiếu tệp mô hình. Kiểm tra đường dẫn best.pt.") from exc
                except (OSError, RuntimeError) as exc:
                    raise ValueError(f"Không chạy được mô hình AI ({exc})") from exc
                return {
                    "prediction": verdict, "label": label, "confidence": confidence,
                    "model_sha256": app.state.vision.classifier.checksum,
                    "image": "data:image/jpeg;base64," + base64.b64encode(image).decode("ascii"),
                }

        return app

    @app.get("/api/jobs/{key}")
    async def job_detail(key: str):
        return app.state.runtime.store.job(key) or Response(status_code=404)

    @app.get("/api/jobs/{key}/image")
    async def image(key: str):
        row = app.state.runtime.store.db.execute(
            "SELECT image FROM jobs WHERE id=?", (key,)
        ).fetchone()
        if not row or not row[0]:
            return Response(status_code=204)
        return Response(row[0], media_type="image/jpeg")

    @app.post("/api/connect")
    async def connect(body: Connect):
        await app.state.runtime.connect_serial(body.port.upper())
        return {"ok": True}

    @app.post("/api/shift")
    async def shift():
        rt = app.state.runtime
        rt.require_idle()
        rt.store.shift()
        return {"ok": True}

    @app.post("/api/background")
    async def background():
        rt = app.state.runtime
        rt.require_idle()
        if not rt.vision or rt.board.get("ir"):
            raise ValueError("Cần trạm thật và băng trống")
        rt.busy = True
        try:
            rt.invalidate_profile()
            await asyncio.to_thread(rt.vision.calibrate_background)
        finally:
            rt.busy = False
        return {"ok": True}

    @app.post("/api/pilot")
    async def pilot(body: Sample):
        return await app.state.runtime.pilot(body.book.strip(), body.truth, body.split)

    @app.post("/api/thresholds")
    async def threshold():
        try:
            return await app.state.runtime.validate_known_books()
        except CalibrationFailure as exc:
            raise HTTPException(409, detail=exc.detail) from exc

    @app.get("/api/settings")
    async def settings():
        return app.state.runtime.settings_status()

    @app.post("/api/settings")
    async def change_settings(body: SettingsChange):
        if body.reset and body.values:
            raise ValueError("Choose either reset or new settings.")
        return await app.state.runtime.update_settings(body.values, reset=body.reset)

    @app.post("/api/manual/decision", status_code=202)
    async def manual_decision(body: ManualDecision):
        rt = app.state.runtime
        if rt.mode != "hardware-manual":
            raise HTTPException(404)
        rt.manual_decision(body.key, body.verdict)
        return {"queued": True, "key": body.key}

    @app.get("/api/sim/image")
    async def sim_preview(version: str | None = None):
        rt = app.state.runtime
        if rt.mode != "simulation":
            raise HTTPException(404)
        photo = rt.simulation_photo
        preview = photo.preview if photo and (version is None or version == photo.version) else b""
        return Response(preview or b"", status_code=200 if preview else 204,
                        media_type="image/jpeg", headers={"Cache-Control": "no-store"})

    @app.post("/api/sim/image")
    async def sim_image(request: Request):
        rt = app.state.runtime
        if rt.mode != "simulation":
            raise HTTPException(404)
        if request.headers.get("content-type", "").split(";")[0] not in (
            "image/jpeg", "image/png", "application/octet-stream"
        ):
            raise HTTPException(415, "Select a JPG or PNG cover image.")
        content = bytearray()
        async for chunk in request.stream():
            if len(content) + len(chunk) > 10 * 1024 * 1024:
                raise HTTPException(413, "Select an image smaller than 10 MiB.")
            content.extend(chunk)
        await rt.sim_image(bytes(content))
        return {"simulation_image": True, "simulation_image_version": rt.simulation_photo.version}

    @app.post("/api/sim/{action}")
    async def sim(action: str):
        rt = app.state.runtime
        if rt.mode != "simulation":
            raise HTTPException(404)
        rt.sim_event(action)
        return {"ok": True}

    return app
