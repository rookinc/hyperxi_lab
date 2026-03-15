#!/usr/bin/env python3
from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path

import networkx as nx
import numpy as np

from hyperxi.combinatorics.chamber_graph import build_chamber_graph
from hyperxi.combinatorics.thalions import build_thalions

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "spectral" / "nodal" / "thalion_mode_coarse_residual_split.txt"

FACE_CLASS = {
    0: 0, 4: 0, 8: 0,
    1: 1, 5: 1, 9: 1,
    2: 2, 6: 2, 10: 2,
    3: 3, 7: 3, 11: 3,
}


def extract_face(flag):
    for name in ("face", "f", "face_id"):
        if hasattr(flag, name):
            return int(getattr(flag, name))
    raise AttributeError("Could not find face attribute on Flag.")


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
    return [j for j, v in enumerate(eigvals) if abs(v - target) <= tol]


def thalion_face_map():
    thalions = build_thalions()
    out = {}
    for th in thalions:
        faces = sorted({extract_face(m) for m in th.members})
        if len(faces) != 1:
            raise RuntimeError(f"Expected one face per internal vertex, got {th.id}: {faces}")
        out[th.id] = faces[0]
    return out


def project_to_classes(vec, nodes, th_face):
    node_to_idx = {node: i for i, node in enumerate(nodes)}
    class_vals = defaultdict(list)

    for node in nodes:
        face = th_face[node]
        cls = FACE_CLASS[face]
        val = float(vec[node_to_idx[node]])
        class_vals[cls].append(val)

    class_avg = {c: float(np.mean(vals)) for c, vals in class_vals.items()}
    lifted = np.array([class_avg[FACE_CLASS[th_face[node]]] for node in nodes], dtype=float)
    return class_avg, lifted


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

    th_face = thalion_face_map()

    lines = []
    lines.append("=" * 80)
    lines.append("THALION MODE COARSE / RESIDUAL SPLIT")
    lines.append("=" * 80)
    lines.append(f"internal vertices: {G.number_of_nodes()}")
    lines.append(f"internal edges:    {G.number_of_edges()}")
    lines.append(f"lambda_1:          {eigvals[1]:.9f}")
    lines.append(f"first block:       {block}")
    lines.append("")

    print("=" * 80)
    print("THALION MODE COARSE / RESIDUAL SPLIT")
    print("=" * 80)
    print(f"lambda_1 ≈ {eigvals[1]:.9f}")
    print()

    for k in range(12):
        theta = 2.0 * math.pi * k / 12.0
        vec = math.cos(theta) * v1 + math.sin(theta) * v2

        class_avg, coarse = project_to_classes(vec, nodes, th_face)
        residual = vec - coarse

        total_norm = float(np.linalg.norm(vec))
        coarse_norm = float(np.linalg.norm(coarse))
        residual_norm = float(np.linalg.norm(residual))

        coarse_frac = coarse_norm / total_norm if total_norm else 0.0
        resid_frac = residual_norm / total_norm if total_norm else 0.0

        face_resid = defaultdict(list)
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        for node in nodes:
            face = th_face[node]
            face_resid[face].append(float(residual[node_to_idx[node]]))

        lines.append(f"PHASE {k:02d} theta={theta:.9f}")
        lines.append("-" * 80)
        lines.append(f"||mode||      = {total_norm:.12f}")
        lines.append(f"||coarse||    = {coarse_norm:.12f}")
        lines.append(f"||residual||  = {residual_norm:.12f}")
        lines.append(f"coarse frac   = {coarse_frac:.12f}")
        lines.append(f"residual frac = {resid_frac:.12f}")
        lines.append("class averages:")
        for c in sorted(class_avg):
            lines.append(f"  C{c}: {class_avg[c]:+.12f}")
        lines.append("residual face means / stddev:")
        for f in sorted(face_resid):
            arr = np.array(face_resid[f], dtype=float)
            lines.append(
                f"  face {f:2d}: mean={float(np.mean(arr)):+.12f} "
                f"std={float(np.std(arr)):.12f} "
                f"min={float(np.min(arr)):+.12f} "
                f"max={float(np.max(arr)):+.12f}"
            )
        lines.append("")

        print(
            f"k={k:02d} theta={theta:.3f} "
            f"coarse={coarse_frac:.12f} residual={resid_frac:.12f}"
        )

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print()
    print(f"saved {OUT.relative_to(ROOT)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
