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
OUT = ROOT / "reports" / "spectral" / "nodal" / "thalion_mode_face_class_lift_error.txt"

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


def face_class_projection(vec, nodes, th_face):
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    face_vals = defaultdict(list)
    class_vals = defaultdict(list)

    for node in nodes:
        face = th_face[node]
        cls = FACE_CLASS[face]
        val = float(vec[node_to_idx[node]])
        face_vals[face].append(val)
        class_vals[cls].append(val)

    face_avg = {f: float(np.mean(vals)) for f, vals in face_vals.items()}
    class_avg = {c: float(np.mean(vals)) for c, vals in class_vals.items()}

    lifted_face = np.array([face_avg[th_face[node]] for node in nodes], dtype=float)
    lifted_class = np.array([class_avg[FACE_CLASS[th_face[node]]] for node in nodes], dtype=float)

    return face_avg, class_avg, lifted_face, lifted_class


def rel_error(vec, approx):
    num = float(np.linalg.norm(vec - approx))
    den = float(np.linalg.norm(vec))
    return num / den if den > 0 else 0.0


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
    lines.append("THALION MODE FACE-CLASS LIFT ERROR")
    lines.append("=" * 80)
    lines.append(f"internal vertices: {G.number_of_nodes()}")
    lines.append(f"internal edges:    {G.number_of_edges()}")
    lines.append(f"lambda_1:          {eigvals[1]:.9f}")
    lines.append(f"first block:       {block}")
    lines.append("")

    print("=" * 80)
    print("THALION MODE FACE-CLASS LIFT ERROR")
    print("=" * 80)
    print(f"lambda_1 ≈ {eigvals[1]:.9f}")
    print()

    face_errs = []
    class_errs = []

    for k in range(12):
        theta = 2.0 * math.pi * k / 12.0
        vec = math.cos(theta) * v1 + math.sin(theta) * v2

        face_avg, class_avg, lifted_face, lifted_class = face_class_projection(vec, nodes, th_face)

        err_face = rel_error(vec, lifted_face)
        err_class = rel_error(vec, lifted_class)

        face_errs.append(err_face)
        class_errs.append(err_class)

        lines.append(f"PHASE {k:02d} theta={theta:.9f}")
        lines.append("-" * 80)
        lines.append(f"relative error to 12-face projection = {err_face:.12f}")
        lines.append(f"relative error to 4-class lift       = {err_class:.12f}")
        lines.append("face averages:")
        for f in sorted(face_avg):
            lines.append(f"  face {f:2d}: {face_avg[f]:+.12f}")
        lines.append("class averages:")
        for c in sorted(class_avg):
            lines.append(f"  C{c}: {class_avg[c]:+.12f}")
        lines.append("")

        print(
            f"k={k:02d}  theta={theta:.3f}  "
            f"err(face)={err_face:.12e}  err(class)={err_class:.12e}"
        )

    lines.append("SUMMARY")
    lines.append("-" * 80)
    lines.append(f"face projection error  min/max/avg = {min(face_errs):.12f} / {max(face_errs):.12f} / {sum(face_errs)/len(face_errs):.12f}")
    lines.append(f"class lift error       min/max/avg = {min(class_errs):.12f} / {max(class_errs):.12f} / {sum(class_errs)/len(class_errs):.12f}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print()
    print(f"saved {OUT.relative_to(ROOT)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
