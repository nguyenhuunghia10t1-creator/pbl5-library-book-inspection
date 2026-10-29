from dataclasses import asdict, dataclass, fields
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Config:
    camera_index: int = 0
    backend: str = "auto"
    width: int = 1280
    height: int = 720
    fps: int = 30
    processing_width: int = 960
    output_width: int = 630
    output_height: int = 888
    background_tolerance: float = 22.0
    min_area_fraction: float = 0.05
    max_area_fraction: float = 0.85
    aspect_tolerance: float = 0.30
    min_sharpness: float = 65.0
    min_brightness: float = 35.0
    max_brightness: float = 235.0
    min_source_short_edge: int = 180
    stable_frames: int = 4
    stable_motion_pixels: float = 8.0
    max_frame_age_seconds: float = 1.5
    qr_interval_seconds: float = 0.15
    orient_by_qr: bool = True
    output_dir: str = "data/opencv/collection"

    def validate(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if field.type is int and type(value) is not int:
                raise ValueError(f"{field.name} must be an integer")
            if field.type is float and (type(value) not in (int, float) or not math.isfinite(value)):
                raise ValueError(f"{field.name} must be a finite number")
        if type(self.orient_by_qr) is not bool:
            raise ValueError("orient_by_qr must be true/false")
        if self.camera_index < 0 or self.backend not in ("auto", "dshow", "msmf"):
            raise ValueError("Invalid camera index/backend")
        for key in ("width", "height", "fps", "processing_width", "output_width", "output_height",
                    "min_source_short_edge", "stable_frames"):
            if getattr(self, key) <= 0:
                raise ValueError(f"{key} must be positive")
        if not 0 < self.min_area_fraction < self.max_area_fraction < 1:
            raise ValueError("Invalid area fractions")
        if not 0 < self.aspect_tolerance < 0.8:
            raise ValueError("Invalid aspect tolerance")
        if abs(self.output_width / self.output_height - 105 / 148) > 0.015:
            raise ValueError("Output must have portrait A6 aspect ratio (105:148)")
        if not 0 < self.background_tolerance <= 100 or self.min_sharpness < 0:
            raise ValueError("Invalid background/sharpness threshold")
        if not 0 <= self.min_brightness < self.max_brightness <= 255:
            raise ValueError("Invalid brightness thresholds")
        if min(self.stable_motion_pixels, self.max_frame_age_seconds, self.qr_interval_seconds) <= 0:
            raise ValueError("Motion/age/interval must be positive")
        if not isinstance(self.output_dir, str) or not self.output_dir.strip():
            raise ValueError("output_dir must be a nonempty path")
        return self

    def to_dict(self):
        return asdict(self)


def load_config(filename=None):
    filename = Path(filename) if filename else ROOT / "vision/opencv/configs/cover_capture.json"
    data = json.loads(filename.read_text(encoding="utf-8-sig"))
    unknown = set(data) - {f.name for f in fields(Config)}
    if unknown:
        raise ValueError(f"Unknown config keys: {sorted(unknown)}")
    return Config(**data).validate()
