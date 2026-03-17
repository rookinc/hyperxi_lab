# src/hyperxi/viewer/cubic_mode_pil.py
from __future__ import annotations

from PIL import Image, ImageDraw


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _interp_rgb(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    t = _clamp01(t)
    return (
        round(a[0] + (b[0] - a[0]) * t),
        round(a[1] + (b[1] - a[1]) * t),
        round(a[2] + (b[2] - a[2]) * t),
    )


def cubic_value_to_rgb(value: float, vmax: float) -> tuple[int, int, int]:
    if vmax <= 1e-12:
        return (255, 255, 255)

    t = abs(value) / vmax
    white = (255, 255, 255)
    red = (220, 50, 47)
    blue = (38, 139, 210)

    if value > 0:
        return _interp_rgb(white, red, t)
    if value < 0:
        return _interp_rgb(white, blue, t)
    return white


def _regular_polygon(cx: float, cy: float, r: float, n: int, rotation_deg: float = -90.0) -> list[tuple[float, float]]:
    import math

    pts: list[tuple[float, float]] = []
    for i in range(n):
        ang = math.radians(rotation_deg + i * 360.0 / n)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def _slot_points(polygon_xy: list[tuple[float, float]]) -> list[tuple[float, float]]:
    cx = sum(x for x, _ in polygon_xy) / len(polygon_xy)
    cy = sum(y for _, y in polygon_xy) / len(polygon_xy)
    pts: list[tuple[float, float]] = []
    for vx, vy in polygon_xy[:5]:
        px = cx + 0.62 * (vx - cx)
        py = cy + 0.62 * (vy - cy)
        pts.append((px, py))
    return pts


def render_cubic_resonance_image(
    payload,
    phase_index: int,
    display_mode: str = "faces+slots",
    width: int = 900,
    height: int = 700,
) -> Image.Image:
    frame = payload.frame(phase_index)
    face_avg = frame["face_avg"]
    class_avg = frame["class_avg"]
    face_slot_values = frame["face_slot_values"]

    face_to_class: dict[int, int] = {}
    for cname, faces in payload.face_class_groups.items():
        cls = int(cname[1:])
        for f in faces:
            face_to_class[int(f)] = cls

    vmax = max(abs(float(v)) for v in face_avg.values())

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    cols = 4
    rows = 3
    margin_x = width * 0.08
    margin_y = height * 0.12
    cell_w = (width - 2 * margin_x) / cols
    cell_h = (height - 2 * margin_y) / rows
    radius = min(cell_w, cell_h) * 0.22

    for face_id in range(12):
        row = face_id // cols
        col = face_id % cols

        cx = margin_x + (col + 0.5) * cell_w
        cy = margin_y + (row + 0.5) * cell_h

        polygon = _regular_polygon(cx, cy, radius, 5, rotation_deg=-90.0)

        if display_mode == "classes":
            cls = face_to_class[face_id]
            value = float(class_avg[str(cls)])
        else:
            value = float(face_avg[str(face_id)])

        fill = cubic_value_to_rgb(value, vmax)
        draw.polygon(polygon, fill=fill, outline=(32, 32, 32), width=2)

        draw.text((cx - 6, cy - 8), str(face_id), fill=(17, 17, 17))

        cls = face_to_class[face_id]
        draw.text((cx - 10, cy + radius + 10), f"C{cls}", fill=(51, 51, 51))

        if display_mode == "faces+slots":
            slot_pts = _slot_points(polygon)
            slot_map = face_slot_values[str(face_id)]
            for slot_id, (px, py) in enumerate(slot_pts):
                sval = float(slot_map[str(slot_id)])
                scolor = cubic_value_to_rgb(sval, vmax * 1.35)
                r = 5 + 8 * min(1.0, abs(sval) / max(vmax, 1e-12))
                draw.ellipse((px - r, py - r, px + r, py + r), fill=scolor, outline=(17, 17, 17), width=1)

    return img
