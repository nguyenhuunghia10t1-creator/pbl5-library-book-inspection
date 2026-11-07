"""Texture-aware focus and clipping diagnostics; brightness alone is not exposure."""
import cv2
import numpy as np


def assess_quality(gray, config):
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(gray.mean())
    # Exclude warp/image boundaries; focus must be supported by actual cover detail.
    my, mx = max(1, gray.shape[0] // 10), max(1, gray.shape[1] // 10)
    interior = gray[my:-my, mx:-mx]
    if interior.size == 0:
        interior = gray
    laplacian = cv2.Laplacian(interior, cv2.CV_64F)
    detail = []
    for y in range(0, interior.shape[0] - 15, 32):
        for x in range(0, interior.shape[1] - 15, 32):
            tile = interior[y:y + 32, x:x + 32]
            if float(np.percentile(tile, 95) - np.percentile(tile, 5)) >= config.min_detail_contrast:
                detail.append(float(laplacian[y:y + 32, x:x + 32].var()))
    detail_sharpness = float(np.percentile(detail, 75)) if detail else 0.0
    clipped_high = float(np.mean(interior >= 254))
    clipped_low = float(np.mean(interior <= 1))
    issues = []
    if not detail:
        issues.append("FOCUS_UNVERIFIED")
    elif detail_sharpness < config.min_sharpness:
        issues.append("BLURRY")
    if max(clipped_high, clipped_low) >= config.max_clipped_fraction or (
            brightness < config.min_brightness and not detail):
        issues.append("BAD_LIGHT")
    return {"sharpness": sharpness, "brightness": brightness,
            "detail_sharpness": detail_sharpness, "focus_measurable": bool(detail),
            "detail_tiles": len(detail), "clipped_high_fraction": clipped_high,
            "clipped_low_fraction": clipped_low,
            "brightness_outside_legacy_range": not config.min_brightness <= brightness <= config.max_brightness}, issues
