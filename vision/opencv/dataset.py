"""Immutable capture bundles. metadata.json is authoritative; manifest is rebuildable."""
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import uuid

import cv2
import numpy as np

from . import __version__
from .config import ROOT


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def read_image(path):
    image = cv2.imdecode(np.fromfile(str(path), np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Cannot decode image: {path}")
    return image


def write_image(path, image):
    ok, buffer = cv2.imencode(".png", image)
    if not ok:
        raise OSError(f"Cannot encode image: {path}")
    with open(path, "xb") as stream:
        stream.write(buffer.tobytes())
        stream.flush()
        os.fsync(stream.fileno())


def write_json(path, data):
    with open(path, "x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def annotate(frame, result):
    image = frame.copy()
    if result.corners is not None:
        cv2.polylines(image, [result.corners.astype(np.int32)], True, (70, 230, 100), 3)
        for i, p in enumerate(result.corners):
            cv2.circle(image, tuple(p.astype(int)), 6, (0, 180, 255), -1)
            cv2.putText(image, str(i), tuple(p.astype(int) + [8, 0]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        center = np.array(result.metrics.get("center_px", [0, 0])).astype(int)
        cv2.drawMarker(image, tuple(center), (0, 0, 255), cv2.MARKER_CROSS, 24, 2)
    cv2.putText(image, result.status, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 100, 255), 2)
    return image


class DatasetWriter:
    def __init__(self, config, source_kind="real", source_description=None):
        output = Path(config.output_dir)
        self.root = output if output.is_absolute() else ROOT / output
        self.root.mkdir(parents=True, exist_ok=True)
        self.config = config
        self.session_id = str(uuid.uuid4())
        self.source_kind = source_kind
        self.source_description = source_description
        self.saved_packets = set()
        self.manifest_warning = None
        self.session_dir = self.root / "sessions" / self.session_id
        self.session_dir.mkdir(parents=True)
        write_json(self.session_dir / "session.json", {
            "session_id": self.session_id, "created_utc": utc_now(), "config": config.to_dict(),
            "source_kind": source_kind, "source_description": source_description,
            "python": sys.version, "opencv": cv2.__version__, "numpy": np.__version__,
            "app_version": __version__})

    def save_background(self, image):
        filename = "background_" + uuid.uuid4().hex[:12] + ".png"
        write_image(self.session_dir / filename, image)
        return (self.session_dir / filename).relative_to(self.root).as_posix()

    def save(self, packet, result, camera_properties, review=False, background_path=None,
             frame_age_seconds=0.0, frozen=False):
        if result.crop is None:
            raise ValueError("No cover crop: cannot save")
        if not review and result.status != "READY":
            raise ValueError("Not READY; improve image/QR or use D to save a review sample")
        if not frozen and frame_age_seconds > self.config.max_frame_age_seconds:
            raise ValueError("Stale frame: capture a new frame")
        key = (packet.camera_session_id, packet.sequence)
        if key in self.saved_packets:
            raise ValueError("This frame was already saved; capture a new frame")
        image_id = str(uuid.uuid4())
        captures = self.root / "captures"
        captures.mkdir(exist_ok=True)
        staging = captures / (".pending_" + image_id)
        final = captures / image_id
        staging.mkdir()
        group = "review" if review else "accepted"
        record = {
            "schema_version": 1, "app_version": __version__, "image_id": image_id,
            "session_id": self.session_id, "timestamp_utc": packet.timestamp_utc,
            "saved_utc": utc_now(), "capture_seq": packet.sequence,
            "camera_session_id": packet.camera_session_id, "source_kind": self.source_kind,
            "source_description": self.source_description, "collection_status": group,
            "copy_id": result.qr.book_id, "title_id": None, "identity_status": "NOT_CHECKED",
            "qr": asdict(result.qr), "vision_status": result.status, "issues": result.issues,
            "metrics": result.metrics, "corners_source_px": result.corners.tolist(),
            "geometry_method": result.method, "stable_frames": result.stable_count,
            "rotation_after_warp_deg": result.rotation, "orientation_basis": result.orientation_basis,
            "frame_age_at_save_seconds": frame_age_seconds, "manual_frozen_snapshot": frozen,
            "camera": camera_properties, "config_at_capture": self.config.to_dict(),
            "background_reference": background_path,
            "ai_quality": None, "defect_labels": None,
            "label_note": "Image quality checks are not defect classification or ground truth.",
            "files": {name: f"captures/{image_id}/{name}.png" for name in ("raw", "cover", "debug")},
        }
        try:
            write_image(staging / "raw.png", packet.image)
            write_image(staging / "cover.png", result.crop)
            write_image(staging / "debug.png", annotate(packet.image, result))
            record["sha256"] = {name: hashlib.sha256((staging / (name + ".png")).read_bytes()).hexdigest()
                                for name in record["files"]}
            write_json(staging / "metadata.json", record)
            staging.rename(final)
        except Exception:
            # Only remove the staging directory created by this call, never existing captures.
            shutil.rmtree(staging, ignore_errors=True)
            raise
        self.saved_packets.add(key)
        self.manifest_warning = None
        try:
            with (self.root / "manifest.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
        except OSError as error:
            self.manifest_warning = f"Capture saved; manifest append failed: {error}. Use --rebuild-manifest."
        return final


def rebuild_manifest(output):
    root = Path(output)
    if not root.is_absolute():
        root = ROOT / root
    records = []
    for entry in sorted((root / "captures").glob("*/metadata.json")):
        if entry.parent.name.startswith("."):
            continue
        record = json.loads(entry.read_text(encoding="utf-8"))
        for name, relative in record["files"].items():
            image = root / relative
            if not image.is_file() or hashlib.sha256(image.read_bytes()).hexdigest() != record["sha256"][name]:
                raise ValueError(f"Missing/changed capture: {image}")
        records.append(record)
    temporary = root / (".manifest_" + uuid.uuid4().hex + ".jsonl")
    with temporary.open("x", encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, root / "manifest.jsonl")
    return len(records)
