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
OUT = ROOT / "reports" / "spectral" / "nodal" / "chamber_nodal_face_audit.txt"


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


def extract_face(flag):
    """
    Try common attribute names used for face index on your Flag objects.
    """
    for name in ("face", "f", "face_id"):
        if hasattr(flag, name):
            return int(getattr(flag, name))
    raise AttributeError(
        "Could not find face attribute on Flag. "
        "Edit extract_face() in scripts/chamber_nodal_face_audit.py."
    )


def thalion_face_map():
    thalions = build_thalions()
    out = {}
    for th in thalions:
        faces = sorted({extract_face(member) for member in th.members})
        out[th.id] = faces
    return out


def sign_of(x: float, eps: float = 1e-10) -> int:
    if x > eps:
        return 1
    if x < -eps:
        return -1
    return 0


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

    node_to_idx = {node: i for i, node in enumerate(nodes)}
    th_faces = thalion_face_map()

    all_faces = sorted({f for faces in th_faces.values() for f in faces})

    lines = []
    lines.append("=" * 80)
    lines.append("CHAMBER NODAL FACE AUDIT")
    lines.append("=" * 80)
    lines.append(f"vertices: {G.number_of_nodes()}")
    lines.append(f"edges:    {G.number_of_edges()}")
    lines.append(f"lambda_1: {eigvals[1]:.9f}")
    lines.append(f"block:    {block}")
    lines.append(f"faces seen in thalions: {all_faces}")
    lines.append("")

    print("=" * 80)
    print("CHAMBER NODAL FACE AUDIT")
    print("=" * 80)
    print(f"lambda_1 ≈ {eigvals[1]:.9f}")
    print(f"faces = {all_faces}")
    print()

    for k in range(12):
        theta = 2.0 * math.pi * k / 12.0
        vec = math.cos(theta) * v1 + math.sin(theta) * v2

        face_counts = {f: {"+": 0, "-": 0, "0": 0} for f in all_faces}
        thalion_signs = {}

        for th_id, faces in th_faces.items():
            s = sign_of(vec[node_to_idx[th_id]])
            thalion_signs[th_id] = s
            label = "+" if s > 0 else "-" if s < 0 else "0"
            for f in faces:
                face_counts[f][label] += 1

        face_balance = []
        for f in all_faces:
            p = face_counts[f]["+"]
            n = face_counts[f]["-"]
            z = face_counts[f]["0"]
            face_balance.append((abs(p - n), f, p, n, z))

        face_balance.sort(reverse=True)

        lines.append(f"PHASE k={k:02d} theta={theta:.9f}")
        lines.append("-" * 80)
        for target in [0, 1, 7]:
            if target in face_counts:
                p = face_counts[target]["+"]
                n = face_counts[target]["-"]
                z = face_counts[target]["0"]
                lines.append(f"face {target}: +={p}  -={n}  0={z}  imbalance={p-n}")
        lines.append("top face imbalances:")
        for _, f, p, n, z in face_balance[:12]:
            lines.append(f"  face {f}: +={p}  -={n}  0={z}  imbalance={p-n}")
        lines.append("")

        print(f"k={k:02d} theta={theta:.3f}")
        for target in [0, 1, 7]:
            if target in face_counts:
                p = face_counts[target]['+']
                n = face_counts[target]['-']
                z = face_counts[target]['0']
                print(f"  face {target}: +={p} -={n} 0={z} imbalance={p-n}")

    lines.append("THALION -> FACE SUPPORT")
    lines.append("-" * 80)
    for th_id in sorted(th_faces):
        lines.append(f"{th_id}: {th_faces[th_id]}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print()
    print(f"saved {OUT.relative_to(ROOT)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
