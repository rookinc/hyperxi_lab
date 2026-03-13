from __future__ import annotations

import tkinter as tk

import networkx as nx

from hyperxi.combinatorics.chamber_graph import build_chamber_graph
from hyperxi.combinatorics.thalions import build_thalions
from hyperxi.combinatorics.transport_scaffold import cycle_partition
from hyperxi.viewer.polar_dodecahedron_layout import (
    ChamberKey,
    build_chamber_positions,
    build_polar_dodecahedron_face_centers,
    project_xy,
)

PALETTE = [
    "#4e79a7",
    "#f28e2b",
    "#e15759",
    "#76b7b2",
    "#59a14f",
    "#edc948",
    "#b07aa1",
    "#ff9da7",
    "#9c755f",
    "#bab0ab",
    "#1f77b4",
    "#d62728",
]

SIDE_PALETTE = {
    0: "#4e79a7",  # blue
    1: "#e15759",  # red
}


def _flag_cycle_map(word: str) -> dict[object, int]:
    cycles = cycle_partition(word)
    mapping: dict[object, int] = {}
    for idx, cyc in enumerate(cycles):
        for flag in cyc:
            mapping[flag] = idx
    return mapping


def _thalion_cycle_map(word: str = "SV", thalion_word: str = "FSF") -> dict[int, int]:
    flag_to_cycle = _flag_cycle_map(word)
    thalions = build_thalions(thalion_word)

    out: dict[int, int] = {}
    for th in thalions:
        member_cycles = {flag_to_cycle[m] for m in th.members}
        out[th.id] = min(member_cycles)
    return out


def _thalion_side_map(thalion_word: str = "FSF") -> dict[int, int]:
    """
    Two-shell split for the polar layout.
    """
    thalions = build_thalions(thalion_word)
    out: dict[int, int] = {}

    for th in thalions:
        rep = th.members[0]
        side = 0 if rep.face < 6 else 1
        out[th.id] = side

    return out


def _thalion_key_map(thalion_word: str = "FSF") -> dict[int, ChamberKey]:
    """
    Exact scaffold mapping:

    Under the current FSF quotient, each thalion corresponds exactly
    to one (face, slot) pair, with the two members differing only in orient.
    """
    thalions = build_thalions(thalion_word)
    out: dict[int, ChamberKey] = {}
    for th in thalions:
        rep = th.members[0]
        out[th.id] = ChamberKey(face=rep.face, slot=rep.slot)
    return out


def _face_to_shell_map() -> dict[int, int]:
    """
    Simple deterministic split:
      faces 0..5   -> south shell
      faces 6..11  -> north shell
    """
    return {f: 0 if f < 6 else 1 for f in range(12)}


def _to_canvas_coords(
    projected: dict[ChamberKey, tuple[float, float]],
    width: int,
    height: int,
) -> dict[ChamberKey, tuple[float, float]]:
    cx = width / 2.0
    cy = height / 2.0
    return {k: (cx + x, cy + y) for k, (x, y) in projected.items()}


def _draw_scaffold(
    canvas: tk.Canvas,
    width: int,
    height: int,
    yaw: float,
    pitch: float,
    scale: float,
    face_to_shell: dict[int, int],
    face7_twist: float,
) -> None:
    south_faces, north_faces = build_polar_dodecahedron_face_centers(
        shell_radius=3.0,
        shell_gap=3.2,
        face0_pole=0,
        face1_pole=1,
    )

    flat: dict[tuple[int, int], tuple[float, float, float]] = {}
    centers3: dict[int, tuple[float, float, float]] = {}

    for face in range(12):
        shell = face_to_shell[face]
        center = south_faces[face] if shell == 0 else north_faces[face]
        centers3[face] = center

        shell_origin = (0.0, 0.0, -1.6) if shell == 0 else (0.0, 0.0, 1.6)
        normal = (
            center[0] - shell_origin[0],
            center[1] - shell_origin[1],
            center[2] - shell_origin[2],
        )

        nlen = (normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2) ** 0.5
        normal = (normal[0] / nlen, normal[1] / nlen, normal[2] / nlen)

        # Stable tangent basis
        trial = (0.0, 0.0, 1.0)
        dot = normal[0] * trial[0] + normal[1] * trial[1] + normal[2] * trial[2]
        if abs(dot) > 0.9:
            trial = (0.0, 1.0, 0.0)

        u = (
            trial[1] * normal[2] - trial[2] * normal[1],
            trial[2] * normal[0] - trial[0] * normal[2],
            trial[0] * normal[1] - trial[1] * normal[0],
        )
        ulen = (u[0] ** 2 + u[1] ** 2 + u[2] ** 2) ** 0.5
        u = (u[0] / ulen, u[1] / ulen, u[2] / ulen)

        v = (
            normal[1] * u[2] - normal[2] * u[1],
            normal[2] * u[0] - normal[0] * u[2],
            normal[0] * u[1] - normal[1] * u[0],
        )
        vlen = (v[0] ** 2 + v[1] ** 2 + v[2] ** 2) ** 0.5
        v = (v[0] / vlen, v[1] / vlen, v[2] / vlen)

        twist = face7_twist if face == 7 else 0.0

        import math
        for slot in range(5):
            ang = twist + 2.0 * math.pi * slot / 5.0
            r = 0.42
            p = (
                center[0] + r * math.cos(ang) * u[0] + r * math.sin(ang) * v[0],
                center[1] + r * math.cos(ang) * u[1] + r * math.sin(ang) * v[1],
                center[2] + r * math.cos(ang) * u[2] + r * math.sin(ang) * v[2],
            )
            flat[(face, slot)] = p

    proj_in = {ChamberKey(face=f, slot=s): xyz for (f, s), xyz in flat.items()}
    center_in = {ChamberKey(face=f, slot=0): xyz for f, xyz in centers3.items()}

    proj_raw = project_xy(proj_in, yaw=yaw, pitch=pitch, scale=scale)
    center_raw = project_xy(center_in, yaw=yaw, pitch=pitch, scale=scale)

    # Fit BOTH slot points and face centers with the same transform
    all_xy = list(proj_raw.values()) + list(center_raw.values())
    xs = [x for x, _ in all_xy]
    ys = [y for _, y in all_xy]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    span_x = max(max_x - min_x, 1e-6)
    span_y = max(max_y - min_y, 1e-6)

    pad = 40.0
    avail_w = max(width - 2 * pad, 1.0)
    avail_h = max(height - 2 * pad, 1.0)
    s = min(avail_w / span_x, avail_h / span_y)

    cx_src = 0.5 * (min_x + max_x)
    cy_src = 0.5 * (min_y + max_y)
    cx_dst = width / 2.0
    cy_dst = height / 2.0

    def fit_xy(x: float, y: float) -> tuple[float, float]:
        return (
            cx_dst + s * (x - cx_src),
            cy_dst + s * (y - cy_src),
        )

    proj = {k: fit_xy(x, y) for k, (x, y) in proj_raw.items()}
    center_proj = {k: fit_xy(x, y) for k, (x, y) in center_raw.items()}

    # Pentagon face rings
    for face in range(12):
        pts = [proj[ChamberKey(face=face, slot=s)] for s in range(5)]
        ring_color = "#aa4444" if face == 7 else "#999999"
        ring_width = 2 if face == 7 else 1

        for i in range(5):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % 5]
            canvas.create_line(x1, y1, x2, y2, fill=ring_color, width=ring_width)

        cx, cy = center_proj[ChamberKey(face=face, slot=0)]
        label_fill = "#aa2222" if face == 7 else "#333333"
        canvas.create_text(cx, cy, text=str(face), fill=label_fill)

    # Pole guide line: face 0 to face 1
    x0, y0 = center_proj[ChamberKey(face=0, slot=0)]
    x1, y1 = center_proj[ChamberKey(face=1, slot=0)]
    canvas.create_line(x0, y0, x1, y1, fill="#444444", width=2, dash=(6, 4))


def draw_chamber_graph(
    canvas: tk.Canvas,
    petrie_word: str = "SV",
    thalion_word: str = "FSF",
    color_mode: str = "petrie",
    layout_mode: str = "spring",
    face7_twist: float = 0.6283185307179586,  # pi/5
) -> None:
    """
    Render the chamber graph.

    color_mode:
        - "petrie": color by Petrie cycle class
        - "side":   color by prototype two-cell side split

    layout_mode:
        - "spring"
        - "polar"
    """
    g = build_chamber_graph()

    G = nx.Graph()
    G.add_nodes_from(g.vertices)
    G.add_edges_from(g.edges)

    width = max(int(canvas.winfo_width()), 1)
    height = max(int(canvas.winfo_height()), 1)

    if color_mode == "side":
        side_of_thalion = _thalion_side_map(thalion_word=thalion_word)
    else:
        cycle_of_thalion = _thalion_cycle_map(
            word=petrie_word,
            thalion_word=thalion_word,
        )

    coords: dict[int, tuple[float, float]] = {}

    if layout_mode == "polar":
        key_of = _thalion_key_map(thalion_word=thalion_word)
        face_to_shell = _face_to_shell_map()

        pos3 = build_chamber_positions(
            face_slot_keys=key_of.values(),
            face_to_shell=face_to_shell,
            shell_radius=3.0,
            shell_gap=3.2,
            slot_radius=0.42,
            face0_pole=0,
            face1_pole=1,
            face7_twist=face7_twist,
        )

        proj = project_xy(
            pos3,
            yaw=0.55,
            pitch=-0.35,
            scale=min(width, height) * 0.11,
        )
        proj = _fit_projected_to_canvas(proj, width=width, height=height, pad=40.0)
        

        _draw_scaffold(
            canvas,
            width=width,
            height=height,
            yaw=0.55,
            pitch=-0.35,
            scale=min(width, height) * 0.11,
            face_to_shell=face_to_shell,
            face7_twist=face7_twist,
        )

        for node in G.nodes:
            coords[node] = proj[key_of[node]]

    else:
        pos = nx.spring_layout(G, seed=1)
        scale = min(width, height) * 0.38
        cx = width / 2
        cy = height / 2
        for node, (x, y) in pos.items():
            coords[node] = (cx + x * scale, cy + y * scale)

    for a, b in G.edges:
        x1, y1 = coords[a]
        x2, y2 = coords[b]
        canvas.create_line(x1, y1, x2, y2, fill="#666666")

    r = 6
    for node, (x, y) in coords.items():
        if color_mode == "side":
            side = side_of_thalion.get(node, 0)
            fill = SIDE_PALETTE[side]
        else:
            cls = cycle_of_thalion.get(node, 0)
            fill = PALETTE[cls % len(PALETTE)]

        canvas.create_oval(
            x - r,
            y - r,
            x + r,
            y + r,
            fill=fill,
            outline="black",
        )
def _fit_projected_to_canvas(
    projected: dict[ChamberKey, tuple[float, float]],
    width: int,
    height: int,
    pad: float = 40.0,
) -> dict[ChamberKey, tuple[float, float]]:
    xs = [x for x, _ in projected.values()]
    ys = [y for _, y in projected.values()]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    span_x = max(max_x - min_x, 1e-6)
    span_y = max(max_y - min_y, 1e-6)

    avail_w = max(width - 2 * pad, 1.0)
    avail_h = max(height - 2 * pad, 1.0)
    s = min(avail_w / span_x, avail_h / span_y)

    cx_src = 0.5 * (min_x + max_x)
    cy_src = 0.5 * (min_y + max_y)
    cx_dst = width / 2.0
    cy_dst = height / 2.0

    out = {}
    for k, (x, y) in projected.items():
        out[k] = (
            cx_dst + s * (x - cx_src),
            cy_dst + s * (y - cy_src),
        )
    return out

