from __future__ import annotations

import tkinter as tk
import networkx as nx

from hyperxi.combinatorics.chamber_graph import build_chamber_graph
from hyperxi.combinatorics.thalions import build_thalions
from hyperxi.combinatorics.transport_scaffold import cycle_partition


def _flag_cycle_map(word: str) -> dict[object, int]:
    cycles = cycle_partition(word)
    out: dict[object, int] = {}
    for idx, cyc in enumerate(cycles):
        for flag in cyc:
            out[flag] = idx
    return out


def _thalion_bucket_map(petrie_word: str = "SV", thalion_word: str = "FSF") -> dict[int, int]:
    """
    Prototype 12-bucket map:
    assign each thalion a Petrie-derived class, then fold mod 12.
    """
    flag_to_cycle = _flag_cycle_map(petrie_word)
    thalions = build_thalions(thalion_word)

    out: dict[int, int] = {}
    for th in thalions:
        member_cycles = {flag_to_cycle[m] for m in th.members}
        cls = min(member_cycles)
        out[th.id] = cls % 12
    return out


def build_icosahedral_skeleton(
    petrie_word: str = "SV",
    thalion_word: str = "FSF",
) -> nx.Graph:
    chamber = build_chamber_graph()
    bucket_of = _thalion_bucket_map(petrie_word=petrie_word, thalion_word=thalion_word)

    G = nx.Graph()
    G.add_nodes_from(range(12))

    for a, b in chamber.edges:
        ca = bucket_of[a]
        cb = bucket_of[b]
        if ca != cb:
            G.add_edge(ca, cb)

    return G


def skeleton_summary(
    petrie_word: str = "SV",
    thalion_word: str = "FSF",
) -> list[str]:
    G = build_icosahedral_skeleton(petrie_word=petrie_word, thalion_word=thalion_word)
    degs = sorted(set(dict(G.degree()).values()))
    return [
        f"coarse vertices: {G.number_of_nodes()}",
        f"coarse edges: {G.number_of_edges()}",
        f"degree set: {degs}",
        f"connected: {nx.is_connected(G)}",
    ]


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _interp_rgb(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> str:
    t = _clamp01(t)
    r = round(a[0] + (b[0] - a[0]) * t)
    g = round(a[1] + (b[1] - a[1]) * t)
    b2 = round(a[2] + (b[2] - a[2]) * t)
    return f"#{r:02x}{g:02x}{b2:02x}"


def cubic_value_to_hex(value: float, vmax: float) -> str:
    if vmax <= 1e-12:
        return "#ffffff"

    t = abs(value) / vmax
    white = (255, 255, 255)
    red = (220, 50, 47)
    blue = (38, 139, 210)

    if value > 0:
        return _interp_rgb(white, red, t)
    if value < 0:
        return _interp_rgb(white, blue, t)
    return "#ffffff"


def _regular_polygon(cx: float, cy: float, r: float, n: int, rotation: float = -90.0) -> list[tuple[float, float]]:
    import math

    pts: list[tuple[float, float]] = []
    for i in range(n):
        ang = math.radians(rotation + i * 360.0 / n)
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


def draw_icosahedral_skeleton(
    canvas: tk.Canvas,
    petrie_word: str = "SV",
    thalion_word: str = "FSF",
) -> None:
    G = build_icosahedral_skeleton(petrie_word=petrie_word, thalion_word=thalion_word)
    pos = nx.spring_layout(G, seed=7)

    width = max(int(canvas.winfo_width()), 1)
    height = max(int(canvas.winfo_height()), 1)

    scale = min(width, height) * 0.35
    cx = width / 2
    cy = height / 2

    coords = {}
    for node, (x, y) in pos.items():
        coords[node] = (cx + x * scale, cy + y * scale)

    for a, b in G.edges:
        x1, y1 = coords[a]
        x2, y2 = coords[b]
        canvas.create_line(x1, y1, x2, y2, fill="#666666", width=2)

    r = 12
    for node, (x, y) in coords.items():
        canvas.create_oval(x - r, y - r, x + r, y + r, fill="#d9e6f2", outline="black")
        canvas.create_text(x, y, text=str(node))


def draw_cubic_resonance(
    canvas: tk.Canvas,
    payload,
    phase_index: int,
    display_mode: str = "faces",
) -> None:
    """
    Draw a 12-face viewer for the cubic resonance payload.

    display_mode:
        - faces
        - classes
        - faces+slots
    """
    frame = payload.frame(phase_index)

    face_avg = frame["face_avg"]
    class_avg = frame["class_avg"]
    face_slot_values = frame["face_slot_values"]

    width = max(int(canvas.winfo_width()), 1)
    height = max(int(canvas.winfo_height()), 1)

    cols = 4
    rows = 3
    margin_x = width * 0.08
    margin_y = height * 0.12
    cell_w = (width - 2 * margin_x) / cols
    cell_h = (height - 2 * margin_y) / rows
    radius = min(cell_w, cell_h) * 0.28

    vmax = 0.0
    for v in face_avg.values():
        vmax = max(vmax, abs(float(v)))

    face_to_class: dict[int, int] = {}
    for cname, faces in payload.face_class_groups.items():
        cls = int(cname[1:])
        for f in faces:
            face_to_class[int(f)] = cls

    for face_id in range(12):
        row = face_id // cols
        col = face_id % cols

        cx = margin_x + (col + 0.5) * cell_w
        cy = margin_y + (row + 0.5) * cell_h

        polygon = _regular_polygon(cx, cy, radius, 5, rotation=-90.0)
        flat = [coord for xy in polygon for coord in xy]

        if display_mode == "classes":
            cls = face_to_class[face_id]
            value = float(class_avg[str(cls)])
        else:
            value = float(face_avg[str(face_id)])

        fill = cubic_value_to_hex(value, vmax)

        canvas.create_polygon(
            *flat,
            fill=fill,
            outline="#202020",
            width=2,
        )

        canvas.create_text(cx, cy, text=str(face_id), fill="#111111")

        if display_mode == "faces+slots":
            slot_pts = _slot_points(polygon)
            slot_map = face_slot_values[str(face_id)]
            for slot_id, (px, py) in enumerate(slot_pts):
                sval = float(slot_map[str(slot_id)])
                scolor = cubic_value_to_hex(sval, vmax * 1.35)
                r = 5 + 8 * min(1.0, abs(sval) / max(vmax, 1e-12))
                canvas.create_oval(
                    px - r, py - r, px + r, py + r,
                    fill=scolor,
                    outline="#111111",
                    width=1,
                )

        cls = face_to_class[face_id]
        canvas.create_text(
            cx,
            cy + radius + 16,
            text=f"C{cls}",
            fill="#333333",
        )
