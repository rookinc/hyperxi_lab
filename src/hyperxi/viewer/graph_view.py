from __future__ import annotations

import tkinter as tk

import networkx as nx

from hyperxi.combinatorics.chamber_graph import build_chamber_graph
from hyperxi.combinatorics.thalions import build_thalions
from hyperxi.combinatorics.transport_scaffold import cycle_partition

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
    Prototype two-cell split.

    Uses the representative flag's face chart to assign a side:
    faces 0..5  -> side 0
    faces 6..11 -> side 1
    """
    thalions = build_thalions(thalion_word)
    out: dict[int, int] = {}

    for th in thalions:
        rep = th.members[0]
        side = 0 if rep.face < 6 else 1
        out[th.id] = side

    return out


def draw_chamber_graph(
    canvas: tk.Canvas,
    petrie_word: str = "SV",
    thalion_word: str = "FSF",
    color_mode: str = "petrie",
) -> None:
    """
    Render the chamber graph using a NetworkX spring layout.

    color_mode:
        - "petrie": color by Petrie cycle class
        - "side":   color by prototype two-cell side split
    """

    g = build_chamber_graph()

    G = nx.Graph()
    G.add_nodes_from(g.vertices)
    G.add_edges_from(g.edges)

    pos = nx.spring_layout(G, seed=1)

    width = max(int(canvas.winfo_width()), 1)
    height = max(int(canvas.winfo_height()), 1)

    scale = min(width, height) * 0.38
    cx = width / 2
    cy = height / 2

    coords = {}
    for node, (x, y) in pos.items():
        coords[node] = (
            cx + x * scale,
            cy + y * scale,
        )

    if color_mode == "side":
        side_of_thalion = _thalion_side_map(thalion_word=thalion_word)

    else:
        cycle_of_thalion = _thalion_cycle_map(
            word=petrie_word,
            thalion_word=thalion_word,
        )

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
