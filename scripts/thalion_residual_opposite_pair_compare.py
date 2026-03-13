#!/usr/bin/env python3
from __future__ import annotations

import math
from collections import defaultdict
from itertools import permutations
from pathlib import Path

import networkx as nx
import numpy as np

from hyperxi.combinatorics.chamber_graph import build_chamber_graph
from hyperxi.combinatorics.thalions import build_thalions

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "spectral" / "nodal" / "thalion_residual_opposite_pair_compare.txt"

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


def extract_edge(flag):
    for name in ("edge", "e", "edge_id"):
        if hasattr(flag, name):
            return int(getattr(flag, name))
    return None


def extract_vertex(flag):
    for name in ("vertex", "v", "vertex_id"):
        if hasattr(flag, name):
            return int(getattr(flag, name))
    return None


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


def build_face_slot_map():
    thalions = build_thalions()

    face_buckets = defaultdict(list)
    th_face = {}

    for th in thalions:
        members = list(th.members)
        faces = sorted({extract_face(m) for m in members})
        if len(faces) != 1:
            raise RuntimeError(f"Expected one face per internal vertex, got thalion {th.id}: {faces}")
        face = faces[0]
        th_face[th.id] = face

        m0 = members[0]
        edge = extract_edge(m0)
        vertex = extract_vertex(m0)
        key = (
            edge if edge is not None else 10**9,
            vertex if vertex is not None else 10**9,
            th.id,
        )
        face_buckets[face].append((key, th.id))

    th_slot = {}
    for face in sorted(face_buckets):
        items = sorted(face_buckets[face])
        if len(items) != 5:
            raise RuntimeError(f"Expected 5 internal vertices on face {face}, got {len(items)}")
        for slot, (_, th_id) in enumerate(items):
            th_slot[th_id] = slot

    return th_face, th_slot


def project_to_classes(vec, nodes, th_face):
    node_to_idx = {node: i for i, node in enumerate(nodes)}
    class_vals = defaultdict(list)
    for node in nodes:
        face = th_face[node]
        cls = FACE_CLASS[face]
        class_vals[cls].append(float(vec[node_to_idx[node]]))
    class_avg = {c: float(np.mean(vals)) for c, vals in class_vals.items()}
    lifted = np.array([class_avg[FACE_CLASS[th_face[node]]] for node in nodes], dtype=float)
    return class_avg, lifted


def mean_face_vectors_by_class(residual, nodes, th_face, th_slot):
    node_to_idx = {node: i for i, node in enumerate(nodes)}
    class_faces = defaultdict(list)

    # face -> 5-slot vector
    face_vecs = {}
    for face in range(12):
        v = np.zeros(5, dtype=float)
        seen = np.zeros(5, dtype=int)
        for node in nodes:
            if th_face[node] != face:
                continue
            s = th_slot[node]
            v[s] = float(residual[node_to_idx[node]])
            seen[s] += 1
        if not np.all(seen == 1):
            raise RuntimeError(f"Face {face} missing slot coverage: {seen.tolist()}")
        face_vecs[face] = v
        class_faces[FACE_CLASS[face]].append(face)

    class_means = {}
    for cls in range(4):
        arr = np.array([face_vecs[f] for f in sorted(class_faces[cls])], dtype=float)
        class_means[cls] = np.mean(arr, axis=0)

    return face_vecs, class_means


def corr(a: np.ndarray, b: np.ndarray) -> float:
    da = float(np.linalg.norm(a))
    db = float(np.linalg.norm(b))
    return float(np.dot(a, b) / (da * db)) if da and db else 0.0


def best_perm_match(a: np.ndarray, b: np.ndarray):
    best = None
    for perm in permutations(range(len(a))):
        bp = b[list(perm)]
        c_same = corr(a, bp)
        c_flip = corr(a, -bp)
        candidate = max(
            ("same", c_same, perm),
            ("flip", c_flip, perm),
            key=lambda x: x[1]
        )
        if best is None or candidate[1] > best[1]:
            best = candidate
    return best  # (mode, corr, perm)


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

    th_face, th_slot = build_face_slot_map()

    lines = []
    lines.append("=" * 80)
    lines.append("THALION RESIDUAL OPPOSITE-PAIR COMPARE")
    lines.append("=" * 80)
    lines.append(f"internal vertices: {G.number_of_nodes()}")
    lines.append(f"internal edges:    {G.number_of_edges()}")
    lines.append(f"lambda_1:          {eigvals[1]:.9f}")
    lines.append(f"first block:       {block}")
    lines.append("")

    print("=" * 80)
    print("THALION RESIDUAL OPPOSITE-PAIR COMPARE")
    print("=" * 80)
    print(f"lambda_1 ≈ {eigvals[1]:.9f}")
    print()

    for k in range(12):
        theta = 2.0 * math.pi * k / 12.0
        vec = math.cos(theta) * v1 + math.sin(theta) * v2

        _, coarse = project_to_classes(vec, nodes, th_face)
        residual = vec - coarse

        _, class_means = mean_face_vectors_by_class(residual, nodes, th_face, th_slot)

        a02 = class_means[0]
        b02 = class_means[2]
        a13 = class_means[1]
        b13 = class_means[3]

        c02_same = corr(a02, b02)
        c02_flip = corr(a02, -b02)
        c13_same = corr(a13, b13)
        c13_flip = corr(a13, -b13)

        best02 = best_perm_match(a02, b02)
        best13 = best_perm_match(a13, b13)

        lines.append(f"PHASE {k:02d} theta={theta:.9f}")
        lines.append("-" * 80)
        lines.append("class mean slot vectors:")
        lines.append("  C0: " + " ".join(f"{x:+.12f}" for x in a02))
        lines.append("  C2: " + " ".join(f"{x:+.12f}" for x in b02))
        lines.append("  C1: " + " ".join(f"{x:+.12f}" for x in a13))
        lines.append("  C3: " + " ".join(f"{x:+.12f}" for x in b13))
        lines.append("")
        lines.append(f"C0 vs C2 direct corr      = {c02_same:.12f}")
        lines.append(f"C0 vs -C2 direct corr     = {c02_flip:.12f}")
        lines.append(f"C0/C2 best perm match     = mode={best02[0]} corr={best02[1]:.12f} perm={list(best02[2])}")
        lines.append("")
        lines.append(f"C1 vs C3 direct corr      = {c13_same:.12f}")
        lines.append(f"C1 vs -C3 direct corr     = {c13_flip:.12f}")
        lines.append(f"C1/C3 best perm match     = mode={best13[0]} corr={best13[1]:.12f} perm={list(best13[2])}")
        lines.append("")

        print(f"PHASE {k:02d} theta={theta:.3f}")
        print(f"  C0/C2 direct same={c02_same:.6f} flip={c02_flip:.6f} best={best02[0]} {best02[1]:.6f} perm={list(best02[2])}")
        print(f"  C1/C3 direct same={c13_same:.6f} flip={c13_flip:.6f} best={best13[0]} {best13[1]:.6f} perm={list(best13[2])}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print()
    print(f"saved {OUT.relative_to(ROOT)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
