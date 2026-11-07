"""Reproducible synthetic cover/background scenes with known outer corners."""
import cv2
import numpy as np
from .test_cover_capture import qr_image


def color_scene(color=(250, 250, 250), bg_color=(240, 240, 240), pattern="plain",
                angle=0, perspective=False, details=True, print_border=True):
    h, w = 600, 800
    yy, xx = np.mgrid[:h, :w]
    bg = np.full((h, w, 3), bg_color, np.float32)
    if pattern == "gradient":
        bg += (20 * (xx / w - 0.5) + 15 * (yy / h - 0.5))[:, :, None]
    elif pattern == "texture":
        rng = np.random.default_rng(741)
        bg += (6 * np.sin(xx / 19) + 4 * np.cos(yy / 11))[:, :, None]
        bg += rng.normal(0, 2, (h, w, 1))
    elif pattern == "checker":
        bg += (((xx // 40 + yy // 40) % 2) * 24 - 12)[:, :, None]
    bg = np.uint8(np.clip(bg, 0, 255))
    if pattern == "seams":
        cv2.line(bg, (290, 0), (305, h - 1), (70, 72, 75), 3)
        cv2.line(bg, (0, 350), (w - 1, 360), (75, 75, 75), 3)
    sheet = np.full((395, 280, 3), color, np.uint8)
    ink = (45, 50, 55) if np.mean(color) > 130 else (215, 220, 225)
    if print_border:
        cv2.rectangle(sheet, (12, 12), (267, 382), ink, 3)
    if details:
        cv2.putText(sheet, "PBL5", (26, 75), cv2.FONT_HERSHEY_SIMPLEX, 1, ink, 2)
        for y in range(115, 240, 19):
            cv2.line(sheet, (26, y), (245, y), ink, 2)
        sheet[280:380, 164:264] = qr_image(size=100)
    src = np.float32([[0, 0], [279, 0], [279, 394], [0, 394]])
    if perspective:
        dst = np.float32([[276, 82], [534, 111], [549, 505], [251, 480]])
    else:
        theta = np.deg2rad(angle)
        rotate = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
        dst = ((src - [139.5, 197]) @ rotate.T + [400, 300]).astype(np.float32)
    transform = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(sheet, transform, (w, h), borderMode=cv2.BORDER_REPLICATE)
    mask = cv2.warpPerspective(np.full(sheet.shape[:2], 255, np.uint8), transform, (w, h))
    # Blend antialiased coverage against the backdrop, never an artificial black warp border.
    alpha = mask[:, :, None].astype(np.float32) / 255
    image = np.uint8(np.rint(warped * alpha + bg * (1 - alpha)))
    return image, dst, bg


def matrix_cases():
    colors = {"white": (250, 250, 250), "cream": (225, 242, 248),
              "black": (25, 30, 35), "blue": (160, 65, 35), "red": (35, 40, 205)}
    backdrops = {"light": ((240, 240, 240), "plain"), "dark": ((50, 50, 50), "plain"),
                 "texture": ((180, 190, 200), "texture"), "seams": ((210, 215, 220), "seams")}
    for color_name, color in colors.items():
        for bg_name, (bg, pattern) in backdrops.items():
            yield color_name + "_" + bg_name, dict(color=color, bg_color=bg, pattern=pattern)
    yield "near_white", dict(color=(250, 250, 250), bg_color=(245, 245, 245))
    yield "same_gray_chroma", dict(color=(20, 20, 255), bg_color=(20, 140, 20))
    yield "rotated_light", dict(angle=27)
    yield "perspective_cream", dict(color=(225, 242, 248), perspective=True, pattern="gradient", bg_color=(170, 170, 170))
    yield "checker_background", dict(pattern="checker", bg_color=(170, 170, 170))
