#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from collections import defaultdict

import networkx as nx
import numpy as np

from hyperxi.combinatorics.chamber_graph import build_chamber_graph
from hyperxi.combinatorics.thalions import build_thalions

OUT = "reports/spectral/nodal/thalion_cubic_face_animation.json"

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


def load_graph():
    raw = build_chamber_graph()
    G = nx.Graph()
    G.add_nodes_from(raw.vertices)
    G.add_edges_from(raw.edges)
    nodes = sorted(G.nodes())
    A = nx.to_numpy_array(G, nodelist=nodes, dtype=float)
    return G, nodes, A


def adjacency_spectrum(A: np.ndarray):
    eigvals, eigvecs = np.linalg.eigh(A)
    order = np.argsort(eigvals)[::-1]
    return eigvals[order], eigvecs[:, order]


def multiplicity_block(eigvals, idx, tol=1e-8):
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


def face_average(vec, nodes, th_face):
    node_to_idx = {node: i for i, node in enumerate(nodes)}
    face_vals = defaultdict(list)
    for node in nodes:
        face = th_face[node]
        face_vals[face].append(float(vec[node_to_idx[node]]))
    return {face: float(sum(vals) / len(vals)) for face, vals in sorted(face_vals.items())}


def class_average(face_avg):
    class_vals = defaultdict(list)
    for face, val in face_avg.items():
        class_vals[FACE_CLASS[face]].append(val)
    return {cls: float(sum(vals) / len(vals)) for cls, vals in sorted(class_vals.items())}


def main():
    print("=" * 80)
    print("EXPORT THALION CUBIC FACE ANIMATION")
    print("=" * 80)

    _, nodes, A = load_graph()
    eigvals, eigvecs = adjacency_spectrum(A)
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

    frames = []
    steps = 12

    for k in range(steps):
        theta = 2.0 * math.pi * k / steps
        vec = math.cos(theta) * v1 + math.sin(theta) * v2

        face_avg = face_average(vec, nodes, th_face)
        class_avg = class_average(face_avg)

        frames.append({
            "phase_index": k,
            "theta": theta,
            "face_avg": {str(f): face_avg[f] for f in sorted(face_avg)},
            "class_avg": {str(c): class_avg[c] for c in sorted(class_avg)},
        })

    payload = {
        "name": "thalion_cubic_face_animation",
        "eigenvalue": float(eigvals[1]),
        "steps": steps,
        "face_class_groups": {
            "C0": [0, 4, 8],
            "C1": [1, 5, 9],
            "C2": [2, 6, 10],
            "C3": [3, 7, 11],
        },
        "frames": frames,
    }

    with open(OUT, "w") as fp:
        json.dump(payload, fp, indent=2)

    print("saved:", OUT)
    print("=" * 80)


if __name__ == "__main__":
    main()
