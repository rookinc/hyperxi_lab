#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path

import networkx as nx
import numpy as np

from hyperxi.combinatorics.chamber_graph import build_chamber_graph

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "spectral" / "nodal" / "chamber_mode_nodal_scan.txt"


def load_graph() -> nx.Graph:
    raw = build_chamber_graph()
    G = nx.Graph()
    G.add_nodes_from(raw.vertices)
    G.add_edges_from(raw.edges)
    return G


def adjacency_spectrum(G: nx.Graph):
    nodes = sorted(G.nodes())
    A = nx.to_numpy_array(G, nodelist=nodes, dtype=float)
    eigvals, eigvecs = np.linalg.eigh(A)
    order = np.argsort(eigvals)[::-1]
    return nodes, eigvals[order], eigvecs[:, order]


def multiplicity_block(eigvals: np.ndarray, idx: int, tol: float = 1e-8):
    target = eigvals[idx]
    return [j for j, val in enumerate(eigvals) if abs(val - target) <= tol]


def sign_partition(vec: np.ndarray, eps: float = 1e-10):
    pos = [i for i, x in enumerate(vec) if x > eps]
    neg = [i for i, x in enumerate(vec) if x < -eps]
    zero = [i for i, x in enumerate(vec) if abs(x) <= eps]
    return pos, neg, zero


def main():
    G = load_graph()
    nodes, eigvals, eigvecs = adjacency_spectrum(G)
    block = multiplicity_block(eigvals, 1)
    if len(block) != 2:
        raise RuntimeError(f"Expected 2D first excited block, got {len(block)}")

    v1 = eigvecs[:, block[0]].copy()
    v2 = eigvecs[:, block[1]].copy()

    if v1[np.argmax(np.abs(v1))] < 0:
        v1 *= -1.0
    if v2[np.argmax(np.abs(v2))] < 0:
        v2 *= -1.0

    idx_to_node = {i: node for i, node in enumerate(nodes)}

    lines = []
    lines.append("=" * 80)
    lines.append("CHAMBER MODE NODAL SCAN")
    lines.append("=" * 80)
    lines.append(f"vertices: {G.number_of_nodes()}")
    lines.append(f"edges:    {G.number_of_edges()}")
    lines.append(f"lambda_1: {eigvals[1]:.9f}")
    lines.append(f"block:    {block}")
    lines.append("")

    print("=" * 80)
    print("CHAMBER MODE NODAL SCAN")
    print("=" * 80)
    print(f"lambda_1 ≈ {eigvals[1]:.9f}")
    print()

    steps = 12
    crossing_counts = []
    pos_comp_counts = []
    neg_comp_counts = []

    for k in range(steps):
        theta = 2.0 * math.pi * k / steps
        vec = math.cos(theta) * v1 + math.sin(theta) * v2

        pos_idx, neg_idx, zero_idx = sign_partition(vec)
        pos_nodes = [idx_to_node[i] for i in pos_idx]
        neg_nodes = [idx_to_node[i] for i in neg_idx]
        zero_nodes = [idx_to_node[i] for i in zero_idx]

        crossing = []
        for a, b in G.edges():
            ia = nodes.index(a)
            ib = nodes.index(b)
            sa = np.sign(vec[ia])
            sb = np.sign(vec[ib])
            if sa == 0 or sb == 0:
                continue
            if sa != sb:
                crossing.append((a, b))

        Gpos = G.subgraph(pos_nodes).copy()
        Gneg = G.subgraph(neg_nodes).copy()

        pos_comps = list(nx.connected_components(Gpos))
        neg_comps = list(nx.connected_components(Gneg))

        crossing_counts.append(len(crossing))
        pos_comp_counts.append(len(pos_comps))
        neg_comp_counts.append(len(neg_comps))

        lines.append(f"PHASE k={k:02d} theta={theta:.9f}")
        lines.append("-" * 80)
        lines.append(f"positive vertices: {len(pos_nodes)}")
        lines.append(f"negative vertices: {len(neg_nodes)}")
        lines.append(f"zero vertices:     {len(zero_nodes)}")
        lines.append(f"crossing edges:    {len(crossing)}")
        lines.append(f"positive comps:    {len(pos_comps)}")
        lines.append(f"negative comps:    {len(neg_comps)}")
        lines.append(f"largest + comp:    {max((len(c) for c in pos_comps), default=0)}")
        lines.append(f"largest - comp:    {max((len(c) for c in neg_comps), default=0)}")
        lines.append(f"crossing edge list: {crossing}")
        lines.append("")

        print(
            f"k={k:02d} theta={theta:.3f} "
            f"+={len(pos_nodes)} -={len(neg_nodes)} 0={len(zero_nodes)} "
            f"cross={len(crossing)}  comps(+/-)=({len(pos_comps)}/{len(neg_comps)})"
        )

    lines.append("SUMMARY")
    lines.append("-" * 80)
    lines.append(f"crossing edges min/max/avg = {min(crossing_counts)}/{max(crossing_counts)}/{sum(crossing_counts)/len(crossing_counts):.6f}")
    lines.append(f"positive comps min/max     = {min(pos_comp_counts)}/{max(pos_comp_counts)}")
    lines.append(f"negative comps min/max     = {min(neg_comp_counts)}/{max(neg_comp_counts)}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print()
    print(f"saved {OUT.relative_to(ROOT)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
