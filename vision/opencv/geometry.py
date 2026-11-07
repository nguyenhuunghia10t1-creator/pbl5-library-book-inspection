"""Color-independent quad proposals, boundary evidence and calibrated foreground."""
import cv2
import numpy as np


def order_quad(points):
    """Clockwise cyclic order, starting with the upper short edge (no sum/diff ties)."""
    p = np.asarray(points, np.float32).reshape(4, 2)
    if not np.isfinite(p).all() or len(np.unique(p, axis=0)) != 4:
        raise ValueError("Four different finite corners required")
    center = p.mean(axis=0)
    p = p[np.argsort(np.arctan2(p[:, 1] - center[1], p[:, 0] - center[0]))]
    if not cv2.isContourConvex(p) or abs(cv2.contourArea(p)) < 25:
        raise ValueError("Corners must form a convex quadrilateral")
    lengths = np.linalg.norm(np.roll(p, -1, axis=0) - p, axis=1)
    pair = 0 if lengths[0] + lengths[2] < lengths[1] + lengths[3] else 1
    start = min((pair, pair + 2), key=lambda i: tuple(((p[i] + p[(i + 1) % 4]) / 2)[::-1]))
    return np.roll(p, -start, axis=0)


def quad_ratio(p):
    d = np.linalg.norm(np.roll(p, -1, axis=0) - p, axis=1)
    return float((d[0] + d[2]) / (d[1] + d[3])), d


def corner_motion(a, b):
    """Compare cyclic shifts, including canonical edge changes near 90 degrees."""
    return min(float(np.max(np.linalg.norm(a - np.roll(b, k, axis=0), axis=1))) for k in range(4))


def prepare_lab(small):
    return cv2.cvtColor(cv2.GaussianBlur(small, (5, 5), 0), cv2.COLOR_BGR2LAB).astype(np.float32)


def _border(values, width=8):
    return np.concatenate((values[:width].reshape(-1, *values.shape[2:]),
                           values[-width:].reshape(-1, *values.shape[2:]),
                           values[:, :width].reshape(-1, *values.shape[2:]),
                           values[:, -width:].reshape(-1, *values.shape[2:])))


def _foreground(lab, background, config):
    calibrated = background is not None and background.shape == lab.shape
    if calibrated:
        delta = lab - background
        # Empty border estimates global exposure/white-balance drift, not book color.
        shift = np.median(_border(delta), axis=0)
        delta -= shift
    else:
        delta = lab - np.median(_border(lab), axis=0)
    distance = np.linalg.norm(delta, axis=2)
    samples = _border(distance)
    noise = float(np.median(samples))
    mad = float(np.median(np.abs(samples - noise)))
    floor = config.background_tolerance * 0.15 if calibrated else config.background_tolerance
    threshold = max(config.min_foreground_delta, floor, noise + config.background_noise_factor * mad)
    mask = np.uint8(distance > threshold) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8), iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return mask, calibrated, threshold, calibrated or noise + mad < config.background_tolerance * 0.5


def _edges(lab, config):
    merged = np.zeros(lab.shape[:2], np.uint8)
    for channel in cv2.split(lab.astype(np.uint8)):
        gx = cv2.Sobel(channel, cv2.CV_32F, 1, 0)
        gy = cv2.Sobel(channel, cv2.CV_32F, 0, 1)
        magnitude = cv2.magnitude(gx, gy)
        median = float(np.median(magnitude))
        mad = float(np.median(np.abs(magnitude - median)))
        high = max(config.edge_min_threshold, median + config.edge_noise_factor * mad)
        merged |= cv2.Canny(channel, high * 0.4, high, L2gradient=True)
    return cv2.morphologyEx(merged, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))


def _sample(image, points):
    x = np.clip(np.rint(points[..., 0]).astype(int), 0, image.shape[1] - 1)
    y = np.clip(np.rint(points[..., 1]).astype(int), 0, image.shape[0] - 1)
    return image[y, x]


def _boundary(points, lab, distances, foreground, config):
    sides = np.roll(points, -1, axis=0) - points
    locations = points[:, None, :] + np.linspace(0.06, 0.94, 64)[None, :, None] * sides[:, None, :]
    normals = np.stack((-sides[:, 1], sides[:, 0]), axis=1)
    normals /= np.maximum(1e-6, np.linalg.norm(normals, axis=1, keepdims=True))
    toward_center = points.mean(axis=0) - (points + np.roll(points, -1, axis=0)) / 2
    normals[np.sum(normals * toward_center, axis=1) < 0] *= -1
    offset = normals[:, None, :] * config.geometry_ring_pixels
    inside, outside = locations + offset, locations - offset
    support = np.mean(_sample(distances, locations) <= 2.5, axis=1)
    near_contrast = np.median(np.linalg.norm(_sample(lab, inside) - _sample(lab, outside), axis=2), axis=1)
    far_contrast = np.median(np.linalg.norm(
        _sample(lab, locations + 2 * offset) - _sample(lab, locations - 2 * offset), axis=2), axis=1)
    # A narrow printed stroke returns to the same color at a greater distance.
    contrast = np.minimum(near_contrast, far_contrast)
    return (float(support.min()), float(contrast.min()),
            float(np.mean(_sample(foreground, inside) > 0)), float(np.mean(_sample(foreground, outside) > 0)))


def detect_cover(small, background, previous, config):
    lab = prepare_lab(small)
    foreground, calibrated, threshold, reliable = _foreground(lab, background, config)
    edges = _edges(lab, config)
    distances = cv2.distanceTransform(255 - edges, cv2.DIST_L2, 3)
    h, w = small.shape[:2]
    margin = max(3, min(h, w) * 0.008)
    candidates = []
    boundary_cache = {}
    for source, binary in (("background", foreground), ("adaptive_edges", edges)):
        contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        if source == "adaptive_edges":
            # Weak outer boundaries can be open curves with almost zero contour area.
            # A hull proposes their full extent; four-side evidence still decides acceptance.
            contours = [cv2.convexHull(contour) for contour in contours]
        for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:60]:
            area = cv2.contourArea(contour)
            if not config.min_area_fraction <= area / (w * h) <= config.max_area_fraction:
                continue
            perimeter = cv2.arcLength(contour, True)
            proposals = []
            for epsilon in (0.01, 0.02, 0.035, 0.05):
                approx = cv2.approxPolyDP(contour, epsilon * perimeter, True)
                if len(approx) == 4 and cv2.isContourConvex(approx):
                    proposals.append((approx, False))
            # A rectangle fallback must still have visible support on every side.
            proposals.append((cv2.boxPoints(cv2.minAreaRect(contour)), True))
            for proposal, rectangle in proposals:
                try:
                    points = order_quad(proposal)
                except ValueError:
                    continue
                quad_area = abs(cv2.contourArea(points))
                ratio, _ = quad_ratio(points)
                error = abs(ratio / (105 / 148) - 1)
                if error > config.aspect_tolerance or not 0.78 <= area / max(1, quad_area) <= 1.16:
                    continue
                if (np.any(points[:, 0] < margin) or np.any(points[:, 0] >= w - margin) or
                        np.any(points[:, 1] < margin) or np.any(points[:, 1] >= h - margin)):
                    continue
                if any(corner_motion(points, c[1]) < 4 for c in candidates):
                    continue
                key = points.tobytes()
                if key not in boundary_cache:
                    boundary_cache[key] = _boundary(points, lab, distances, foreground, config)
                support, contrast, inside, outside = boundary_cache[key]
                if support < max(config.min_side_support, 0.70 if rectangle else 0):
                    continue
                if contrast < config.min_boundary_delta:
                    continue
                # Static textured backgrounds are not a foreground book after B.
                if calibrated and inside < 0.30:
                    continue
                # An inset printed edge has foreground on both sides, unlike paper/background.
                if reliable and inside > 0.6 and outside > 0.6 and inside - outside < 0.1:
                    continue
                score = np.sqrt(quad_area) * (1 - error * 0.5) * (0.5 + support * 0.5)
                score *= 1 + 0.35 * max(0, inside - outside)
                metrics = {"boundary_support_min": support, "boundary_delta_min": contrast,
                           "foreground_inside": inside, "foreground_outside": outside,
                           "foreground_threshold": threshold, "background_calibrated": calibrated}
                candidates.append((score, points, source, metrics))
    if not candidates:
        return None, foreground, "auto", {"background_calibrated": calibrated, "foreground_threshold": threshold}
    # Prefer a supported enclosing paper boundary over a nested printed frame.
    enclosing = []
    for candidate in candidates:
        area = cv2.contourArea(candidate[1])
        nested = any(1.03 < cv2.contourArea(other[1]) / area < 1.55 and
                     all(cv2.pointPolygonTest(other[1], tuple(map(float, p)), True) >= -2 for p in candidate[1])
                     for other in candidates)
        if not nested:
            enclosing.append(candidate)
    ranked = sorted(enclosing or candidates, key=lambda c: c[0], reverse=True)
    best = ranked[0]
    if previous is not None:
        # Tie-break only among current candidates with independent boundary evidence.
        close = [c for c in ranked if c[0] >= best[0] * 0.95]
        best = min(close, key=lambda c: corner_motion(c[1], previous))
    for other in ranked:
        overlap, _ = cv2.intersectConvexConvex(best[1], other[1])
        smaller = min(cv2.contourArea(best[1]), cv2.contourArea(other[1]))
        if overlap / max(smaller, 1) < 0.20 and other[0] > best[0] * 0.55:
            return None, foreground, "multiple", {}
    return best[1], foreground, best[2], best[3]
