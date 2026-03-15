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
OUT = ROOT / "reports" / "spectral" / "nodal" / "thalion_face_phase_signatures.txt"


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
    for name in ("face", "f", "face_id"):
        if hasattr(flag, name):
            return int(getattr(flag, name))
    raise AttributeError("Could not find face attribute on Flag; edit extract_face().")


def thalion_face_map():
    thalions = build_thalions()
    out = {}
    for th in thalions:
        faces = sorted({extract_face(member) for member in th.members})
        out[th.id] = faces
    return out


def sign_of(x: float, eps: float = 1e-10) -> str:
    if x > eps:
        return "+"
    if x < -eps:
        return "-"
    return "0"


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

    face_signatures = {f: [] for f in all_faces}
    face_counts_by_phase = []

    for k in range(12):
        theta = 2.0 * math.pi * k / 12.0
        vec = math.cos(theta) * v1 + math.sin(theta) * v2

        face_counts = {f: {"+": 0, "-": 0, "0": 0} for f in all_faces}

        for th_id, faces in th_faces.items():
            s = sign_of(vec[node_to_idx[th_id]])
            for f in faces:
                face_counts[f][s] += 1

        face_counts_by_phase.append(face_counts)

        for f in all_faces:
            p = face_counts[f]["+"]
            n = face_counts[f]["-"]
            z = face_counts[f]["0"]

            if p > n:
                dom = "+"
            elif n > p:
                dom = "-"
            else:
                dom = "0"

            face_signatures[f].append(dom)

    signature_to_faces = defaultdict(list)
    for f, sig in face_signatures.items():
        signature_to_faces["".join(sig)].append(f)

    lines = []
    lines.append("=" * 80)
    lines.append("THALION FACE PHASE SIGNATURES")
    lines.append("=" * 80)
    lines.append(f"thalion vertices: {G.number_of_nodes()}")
    lines.append(f"thalion edges:    {G.number_of_edges()}")
    lines.append(f"lambda_1:         {eigvals[1]:.9f}")
    lines.append(f"first block:      {block}")
    lines.append("")

    lines.append("FACE SIGNATURES BY PHASE")
    lines.append("-" * 80)
    header = "face : " + " ".join([f"{k:02d}" for k in range(12)])
    lines.append(header)
    for f in all_faces:
        sig = " ".join(face_signatures[f])
        lines.append(f"{f:>4} : {sig}")
    lines.append("")

    lines.append("FACE SIGNATURE CLUSTERS")
    lines.append("-" * 80)
    for sig, faces in sorted(signature_to_faces.items(), key=lambda x: (len(x[1]), x[0]), reverse=True):
        lines.append(f"{sig}  ->  faces {sorted(faces)}")
    lines.append("")

    lines.append("PER-PHASE FACE DOMINANCE COUNTS")
    lines.append("-" * 80)
    for k in range(12):
        lines.append(f"PHASE {k:02d}")
        counts = face_counts_by_phase[k]
        for f in all_faces:
            p = counts[f]["+"]
            n = counts[f]["-"]
            z = counts[f]["0"]
            dom = face_signatures[f][k]
            lines.append(f"  face {f:>2}: +={p} -={n} 0={z} dom={dom}")
        lines.append("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("=" * 80)
    print("THALION FACE PHASE SIGNATURES")
    print("=" * 80)
    print(f"lambda_1 ≈ {eigvals[1]:.9f}")
    print("signature clusters:")
    for sig, faces in sorted(signature_to_faces.items(), key=lambda x: (len(x[1]), x[0]), reverse=True):
        print(f"  {sig} -> {sorted(faces)}")
    print()
    print(f"saved {OUT.relative_to(ROOT)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
