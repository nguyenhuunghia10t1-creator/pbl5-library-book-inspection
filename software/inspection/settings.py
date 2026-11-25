"""Validated station-only settings and the shared classifier decision rule."""

from copy import deepcopy
import math


LIMITS = {
    "min_confidence": {"minimum": 0.51, "maximum": 1.0},
    "frame_age_s": {"minimum": 0.1, "maximum": 2.0},
    "frozen_s": {"minimum": 0.2, "maximum": 3.0},
    "stabilize_s": {"minimum": 0.05, "maximum": 2.0},
    "inspection_s": {"minimum": 1.0, "maximum": 7.0},
    "uncertain_policy": {"choices": ["hold", "strict_ng"]},
    "min_sharpness": {"minimum": 1, "maximum": 2000, "unit": "Laplacian variance"},
    "min_brightness": {"minimum": 0, "maximum": 250, "unit": "gray level"},
    "max_brightness": {"minimum": 5, "maximum": 255, "unit": "gray level"},
    "min_source_short_edge": {"minimum": 50, "maximum": 470, "unit": "px", "integer": True},
    "min_area_fraction": {"minimum": 0.01, "maximum": 0.9, "unit": "fraction"},
    "max_area_fraction": {"minimum": 0.1, "maximum": 0.99, "unit": "fraction"},
    "aspect_tolerance": {"minimum": 0.01, "maximum": 0.79, "unit": "fraction"},
    "background_tolerance": {"minimum": 2, "maximum": 100, "unit": "gray level"},
    "stable_frames": {"minimum": 2, "maximum": 12, "unit": "frames", "integer": True},
    "stable_motion_pixels": {"minimum": 1, "maximum": 30, "unit": "px"},
    "min_foreground_fraction": {"minimum": 0.1, "maximum": 1, "unit": "fraction"},
}

for field in ("frame_age_s", "frozen_s", "stabilize_s", "inspection_s"):
    LIMITS[field]["unit"] = "s"
LIMITS["min_confidence"]["unit"] = "probability"


def station_defaults(cfg, geometry):
    return {
        field: deepcopy(cfg[field]) if field in cfg else getattr(geometry, field)
        for field in LIMITS
    }


def validate_settings(defaults, changes):
    if not isinstance(changes, dict) or changes.keys() - LIMITS.keys():
        raise ValueError("Unknown station setting")
    values = deepcopy(defaults)
    for field, value in changes.items():
        if field == "min_confidence":
            if not isinstance(value, dict) or value.keys() - {"OK", "NG"}:
                raise ValueError("min_confidence must contain OK and/or NG")
            values[field].update(value)
        else:
            values[field] = value
    for field, limit in LIMITS.items():
        if field == "uncertain_policy":
            if values[field] not in limit["choices"]:
                raise ValueError("uncertain_policy must be hold or strict_ng")
            continue
        candidates = values[field].values() if field == "min_confidence" else (values[field],)
        for value in candidates:
            if (type(value) not in (int, float)
                    or (limit.get("integer") and type(value) is not int)
                    or not limit["minimum"] <= value <= limit["maximum"]
                    or not math.isfinite(value)):
                raise ValueError(f"{field} must be between {limit['minimum']} and {limit['maximum']}")
    if values["frozen_s"] < values["frame_age_s"]:
        raise ValueError("frozen_s must be at least frame_age_s")
    # Reserve time for frame acquisition and inference after stabilization.
    if values["inspection_s"] - values["stabilize_s"] < 0.5:
        raise ValueError("inspection_s must exceed stabilize_s by at least 0.5 seconds")
    if values["min_brightness"] >= values["max_brightness"]:
        raise ValueError("min_brightness must be less than max_brightness")
    if values["min_area_fraction"] >= values["max_area_fraction"]:
        raise ValueError("min_area_fraction must be less than max_area_fraction")
    return values


def decide_prediction(route, confidence, thresholds, policy):
    if not thresholds:
        return "HOLD"
    if confidence >= thresholds[route]:
        return route
    return "NG" if policy == "strict_ng" else "HOLD"
