#!/usr/bin/env python3
from __future__ import annotations

import numpy as np
import networkx as nx
from collections import defaultdict

from hyperxi.combinatorics.chamber_graph import build_chamber_graph
from hyperxi.combinatorics.thalions import build_thalions

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


def coarse_projection(vec, nodes, th_face):
    node_to_idx = {node: i for i, node in enumerate(nodes)}
    class_vals = defaultdict(list)
    for node in nodes:
        cls = FACE_CLASS[th_face[node]]
        class_vals[cls].append(float(vec[node_to_idx[node]]))
    class_avg = {c: float(np.mean(class_vals[c])) for c in range(4)}
    lifted = np.array([class_avg[FACE_CLASS[th_face[node]]] for node in nodes], dtype=float)
    return lifted


def orthonormalize(vectors):
    basis = []
    for v in vectors:
        w = v.astype(float).copy()
        for b in basis:
            w = w - np.dot(b, w) * b
        n = np.linalg.norm(w)
        if n > 1e-12:
            basis.append(w / n)
    return basis


def main():
    print("=" * 80)
    print("DERIVE THALION CUBIC BLOCK (FAST)")
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

    coarse0 = coarse_projection(v1, nodes, th_face)
    coarse90 = coarse_projection(v2, nodes, th_face)
    residual0 = v1 - coarse0

    basis = orthonormalize([coarse0, coarse90, residual0])
    print(f"basis dimension = {len(basis)}")

    if len(basis) != 3:
        print("Did not get a 3D basis; stopping.")
        return

    B = np.column_stack(basis)
    T = B.T @ A @ B

    print()
    print("Reduced 3x3 operator T:")
    print(np.array_str(T, precision=12, suppress_small=False))

    coeffs = np.poly(T)  # characteristic polynomial coefficients
    print()
    print("Characteristic polynomial coefficients:")
    print(coeffs)
    print()
    print("Interpreted as:")
    print(f"x^3 + ({coeffs[1]:.12f}) x^2 + ({coeffs[2]:.12f}) x + ({coeffs[3]:.12f})")

    print()
    print("Target cubic:")
    print("x^3 + 1*x^2 - 7*x - 2")

    print()
    print("Difference from target coefficients:")
    target = np.array([1.0, 1.0, -7.0, -2.0])
    print(coeffs - target)

    print("=" * 80)


if __name__ == "__main__":
    main()
