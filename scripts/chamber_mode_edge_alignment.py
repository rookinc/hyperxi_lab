#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path

import networkx as nx
import numpy as np

from hyperxi.combinatorics.thalions import build_thalions
from hyperxi.combinatorics.transport_scaffold import F, V

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "spectral" / "chamber_mode_edge_alignment.txt"


def build_typed_graph():
    thalions = build_thalions()

    owner = {}
    for th in thalions:
        for member in th.members:
            owner[member] = th.id

    G = nx.Graph()
    G.add_nodes_from(th.id for th in thalions)

    edge_types: dict[tuple[int, int], set[str]] = {}

    for th in thalions:
        src = th.id
        for flag in th.members:
            for label, move in (("F", F), ("V", V)):
                dst = owner[move(flag)]
                if dst == src:
                    continue
                e = tuple(sorted((src, dst)))
                G.add_edge(*e)
                edge_types.setdefault(e, set()).add(label)

    return G, edge_types


def adjacency_spectrum(G: nx.Graph):
    nodes = sorted(G.nodes())
    A = nx.to_numpy_array(G, nodelist=nodes, dtype=float)
    eigvals, eigvecs = np.linalg.eigh(A)
    order = np.argsort(eigvals)[::-1]
    return nodes, eigvals[order], eigvecs[:, order]


def multiplicity_block(eigvals: np.ndarray, idx: int, tol: float = 1e-8):
    target = eigvals[idx]
    return [j for j, val in enumerate(eigvals) if abs(val - target) <= tol]


def edge_energy(vec: np.ndarray, nodes: list[int], edges: list[tuple[int, int]]) -> float:
    index = {v: i for i, v in enumerate(nodes)}
    total = 0.0
    for a, b in edges:
        da = vec[index[a]] - vec[index[b]]
        total += da * da
    return total


def edge_mean_abs_diff(vec: np.ndarray, nodes: list[int], edges: list[tuple[int, int]]) -> float:
    index = {v: i for i, v in enumerate(nodes)}
    vals = [abs(vec[index[a]] - vec[index[b]]) for a, b in edges]
    return float(sum(vals) / len(vals)) if vals else 0.0


def main():
    G, edge_types = build_typed_graph()
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

    f_edges = sorted([e for e, labels in edge_types.items() if "F" in labels])
    v_edges = sorted([e for e, labels in edge_types.items() if "V" in labels])
    both_edges = sorted([e for e, labels in edge_types.items() if labels == {"F", "V"}])

    lines = []
    lines.append("=" * 80)
    lines.append("CHAMBER MODE EDGE ALIGNMENT")
    lines.append("=" * 80)
    lines.append(f"vertices: {G.number_of_nodes()}")
    lines.append(f"edges:    {G.number_of_edges()}")
    lines.append(f"lambda_1: {eigvals[1]:.9f}")
    lines.append(f"first excited block indices: {block}")
    lines.append("")
    lines.append("EDGE TYPE COUNTS")
    lines.append("-" * 80)
    lines.append(f"F-edges carrying at least one F relation: {len(f_edges)}")
    lines.append(f"V-edges carrying at least one V relation: {len(v_edges)}")
    lines.append(f"edges tagged by both F and V:            {len(both_edges)}")
    lines.append("")

    print("=" * 80)
    print("CHAMBER MODE EDGE ALIGNMENT")
    print("=" * 80)
    print(f"lambda_1 ≈ {eigvals[1]:.9f}")
    print(f"F-edge count = {len(f_edges)}")
    print(f"V-edge count = {len(v_edges)}")
    print(f"both-tagged  = {len(both_edges)}")
    print()

    steps = 12
    ratios = []

    for k in range(steps):
        theta = 2.0 * math.pi * k / steps
        vec = math.cos(theta) * v1 + math.sin(theta) * v2

        f_energy = edge_energy(vec, nodes, f_edges)
        v_energy = edge_energy(vec, nodes, v_edges)
        f_mean = edge_mean_abs_diff(vec, nodes, f_edges)
        v_mean = edge_mean_abs_diff(vec, nodes, v_edges)

        ratio = (f_energy / v_energy) if v_energy > 0 else float("inf")
        ratios.append(ratio)

        lines.append(f"PHASE k={k:02d} theta={theta:.9f}")
        lines.append("-" * 80)
        lines.append(f"F energy      = {f_energy:.9f}")
        lines.append(f"V energy      = {v_energy:.9f}")
        lines.append(f"F/V ratio     = {ratio:.9f}")
        lines.append(f"F mean |Δ|    = {f_mean:.9f}")
        lines.append(f"V mean |Δ|    = {v_mean:.9f}")
        lines.append("")

        print(
            f"k={k:02d}  theta={theta:.3f}  "
            f"F_energy={f_energy:.6f}  V_energy={v_energy:.6f}  ratio={ratio:.6f}"
        )

    lines.append("SUMMARY")
    lines.append("-" * 80)
    lines.append(f"min F/V ratio = {min(ratios):.9f}")
    lines.append(f"max F/V ratio = {max(ratios):.9f}")
    lines.append(f"avg F/V ratio = {sum(ratios)/len(ratios):.9f}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print()
    print(f"saved {OUT.relative_to(ROOT)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
