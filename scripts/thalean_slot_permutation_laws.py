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
OUT = ROOT / "reports" / "spectral" / "nodal" / "thalion_slot_permutation_laws.txt"

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
        cls = FACE_CLASS[th_face[node]]
        class_vals[cls].append(float(vec[node_to_idx[node]]))
    class_avg = {c: float(np.mean(vals)) for c, vals in class_vals.items()}
    lifted = np.array([class_avg[FACE_CLASS[th_face[node]]] for node in nodes], dtype=float)
    return lifted


def mean_face_vectors_by_class(residual, nodes, th_face, th_slot):
    node_to_idx = {node: i for i, node in enumerate(nodes)}
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

    class_means = {}
    for cls in range(4):
        arr = np.array([face_vecs[f] for f in range(12) if FACE_CLASS[f] == cls], dtype=float)
        class_means[cls] = np.mean(arr, axis=0)
    return class_means


def corr(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    return float(np.dot(a, b) / (na * nb)) if na and nb else 0.0


def best_perm(a: np.ndarray, b: np.ndarray):
    best = None
    for perm in permutations(range(len(a))):
        bp = b[list(perm)]
        same = corr(a, bp)
        flip = corr(a, -bp)
        cand_same = ("same", same, perm)
        cand_flip = ("flip", flip, perm)
        cand = cand_same if cand_same[1] >= cand_flip[1] else cand_flip
        if best is None or cand[1] > best[1]:
            best = cand
    return best  # mode, corr, perm


def perm_to_cycles(perm):
    n = len(perm)
    seen = [False] * n
    cycles = []
    for i in range(n):
        if seen[i]:
            continue
        cyc = []
        j = i
        while not seen[j]:
            seen[j] = True
            cyc.append(j)
            j = perm[j]
        cycles.append(tuple(cyc))
    return cycles


def compose(p, q):
    return tuple(p[q[i]] for i in range(len(p)))


def inverse(p):
    inv = [0] * len(p)
    for i, x in enumerate(p):
        inv[x] = i
    return tuple(inv)


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

    # One phase is enough; laws were phase-invariant in your previous run.
    theta = 0.0
    vec = math.cos(theta) * v1 + math.sin(theta) * v2
    coarse = project_to_classes(vec, nodes, th_face)
    residual = vec - coarse
    class_means = mean_face_vectors_by_class(residual, nodes, th_face, th_slot)

    law_02 = best_perm(class_means[0], class_means[2])
    law_13 = best_perm(class_means[1], class_means[3])

    p02 = tuple(law_02[2])
    p13 = tuple(law_13[2])

    lines = []
    lines.append("=" * 80)
    lines.append("THALION SLOT PERMUTATION LAWS")
    lines.append("=" * 80)
    lines.append(f"lambda_1: {eigvals[1]:.9f}")
    lines.append("")

    lines.append("CLASS MEAN SLOT VECTORS AT THETA=0")
    lines.append("-" * 80)
    for c in range(4):
        lines.append(f"C{c}: " + " ".join(f"{x:+.12f}" for x in class_means[c]))
    lines.append("")

    lines.append("OPPOSITE-PAIR LAWS")
    lines.append("-" * 80)
    lines.append(f"C0 -> C2 : mode={law_02[0]} corr={law_02[1]:.12f} perm={list(p02)} cycles={perm_to_cycles(p02)}")
    lines.append(f"C1 -> C3 : mode={law_13[0]} corr={law_13[1]:.12f} perm={list(p13)} cycles={perm_to_cycles(p13)}")
    lines.append("")

    comp = compose(p02, p13)
    lines.append("COMPOSED SLOT MAPS")
    lines.append("-" * 80)
    lines.append(f"p02 ∘ p13 = {list(comp)} cycles={perm_to_cycles(comp)}")
    lines.append(f"p02^-1     = {list(inverse(p02))} cycles={perm_to_cycles(inverse(p02))}")
    lines.append(f"p13^-1     = {list(inverse(p13))} cycles={perm_to_cycles(inverse(p13))}")
    lines.append("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("=" * 80)
    print("THALION SLOT PERMUTATION LAWS")
    print("=" * 80)
    print(f"C0 -> C2 : mode={law_02[0]} corr={law_02[1]:.12f} perm={list(p02)} cycles={perm_to_cycles(p02)}")
    print(f"C1 -> C3 : mode={law_13[0]} corr={law_13[1]:.12f} perm={list(p13)} cycles={perm_to_cycles(p13)}")
    print(f"p02 ∘ p13 = {list(comp)} cycles={perm_to_cycles(comp)}")
    print()
    print(f"saved {OUT.relative_to(ROOT)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
