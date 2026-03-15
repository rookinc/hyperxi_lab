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
OUT = ROOT / "reports" / "spectral" / "nodal" / "thalion_mode_face_projection.txt"


def extract_face(flag):
    for name in ("face", "f", "face_id"):
        if hasattr(flag, name):
            return int(getattr(flag, name))
    raise AttributeError("Could not find face attribute on Flag.")


def load_graph():
    raw = build_chamber_graph()
    G = nx.Graph()
    G.add_nodes_from(raw.vertices)
    G.add_edges_from(raw.edges)
    return G


def adjacency_spectrum(G):
    nodes = sorted(G.nodes())
    A = nx.to_numpy_array(G, nodelist=nodes, dtype=float)
    eigvals, eigvecs = np.linalg.eigh(A)
    order = np.argsort(eigvals)[::-1]
    return nodes, eigvals[order], eigvecs[:, order]


def multiplicity_block(eigvals, idx, tol=1e-8):
    target = eigvals[idx]
    return [j for j, v in enumerate(eigvals) if abs(v - target) <= tol]


def thalion_face_map():
    thalions = build_thalions()
    out = {}
    for th in thalions:
        faces = sorted({extract_face(m) for m in th.members})
        out[th.id] = faces[0]
    return out


def main():

    G = load_graph()
    nodes, eigvals, eigvecs = adjacency_spectrum(G)

    block = multiplicity_block(eigvals, 1)

    v1 = eigvecs[:, block[0]]
    v2 = eigvecs[:, block[1]]

    node_to_idx = {node: i for i, node in enumerate(nodes)}
    th_face = thalion_face_map()

    lines = []
    lines.append("="*80)
    lines.append("THALION MODE FACE PROJECTION")
    lines.append("="*80)
    lines.append(f"lambda1 = {eigvals[1]:.9f}")
    lines.append("")

    print("="*80)
    print("THALION MODE FACE PROJECTION")
    print("="*80)

    for k in range(12):

        theta = 2.0 * math.pi * k / 12.0
        vec = math.cos(theta)*v1 + math.sin(theta)*v2

        face_sum = defaultdict(float)
        face_count = defaultdict(int)

        for th in nodes:
            face = th_face[th]
            val = vec[node_to_idx[th]]
            face_sum[face] += val
            face_count[face] += 1

        face_avg = {f: face_sum[f]/face_count[f] for f in face_sum}

        lines.append(f"PHASE {k:02d} theta={theta:.6f}")
        print(f"\nPHASE {k:02d}")

        for f in sorted(face_avg):
            val = face_avg[f]
            lines.append(f"face {f:2d}  amp={val:+.6f}")
            print(f"face {f:2d}  {val:+.6f}")

    OUT.write_text("\n".join(lines))
    print()
    print(f"saved {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
