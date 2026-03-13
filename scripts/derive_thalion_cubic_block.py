#!/usr/bin/env python3
from __future__ import annotations

import sympy as sp
import networkx as nx
import numpy as np
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
    A = nx.to_numpy_array(G, nodelist=nodes, dtype=int)
    return G, nodes, sp.Matrix(A)


def adjacency_spectrum(A_np: np.ndarray):
    eigvals, eigvecs = np.linalg.eigh(A_np.astype(float))
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


def normalize(v: sp.Matrix) -> sp.Matrix:
    n2 = (v.T * v)[0]
    if n2 == 0:
        return v
    return v / sp.sqrt(sp.nsimplify(n2))


def gram_schmidt(vectors):
    basis = []
    for v in vectors:
        w = sp.Matrix(v)
        for b in basis:
            w = w - ((b.T * w)[0]) * b
        if sp.simplify((w.T * w)[0]) != 0:
            basis.append(normalize(w))
    return basis


def project_operator(A: sp.Matrix, basis):
    B = sp.Matrix.hstack(*basis)
    return sp.simplify(B.T * A * B)


def main():
    print("=" * 80)
    print("DERIVE THALION CUBIC BLOCK")
    print("=" * 80)

    G, nodes, A = load_graph()
    A_np = np.array(A.tolist(), dtype=float)
    eigvals, eigvecs = adjacency_spectrum(A_np)
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

    b1 = sp.Matrix([sp.nsimplify(x) for x in coarse0])
    b2 = sp.Matrix([sp.nsimplify(x) for x in coarse90])
    b3 = sp.Matrix([sp.nsimplify(x) for x in residual0])

    basis = gram_schmidt([b1, b2, b3])

    print(f"basis dimension = {len(basis)}")
    if len(basis) != 3:
        print("Did not get a 3D basis; stopping.")
        return

    T = project_operator(A, basis)
    x = sp.symbols("x")
    charpoly = sp.expand(T.charpoly(x).as_expr())
    factored = sp.factor(charpoly)

    print()
    print("Reduced 3x3 operator T:")
    sp.pprint(T)

    print()
    print("Characteristic polynomial of T:")
    print(charpoly)

    print()
    print("Factored:")
    print(factored)

    target = x**3 + x**2 - 7*x - 2
    print()
    print("Matches target cubic?")
    print(sp.expand(charpoly - target) == 0)

    print("=" * 80)


if __name__ == "__main__":
    main()
