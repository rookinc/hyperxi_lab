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
