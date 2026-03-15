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
OUT = ROOT / "reports" / "spectral" / "nodal" / "thalion_mode_symmetry_algebra.txt"

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
    class_avg = np.array([float(np.mean(class_vals[c])) for c in range(4)], dtype=float)
    lifted = np.array([class_avg[FACE_CLASS[th_face[node]]] for node in nodes], dtype=float)
    return class_avg, lifted


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


def perm_order(p):
    ident = tuple(range(len(p)))
    cur = tuple(p)
    k = 1
    while cur != ident:
        cur = compose(p, cur)
        k += 1
        if k > 1000:
            return -1
    return k


def best_class_shift(a: np.ndarray, b: np.ndarray):
    best = None
    for shift in range(4):
        bs = np.roll(b, shift)
        same = corr(a, bs)
        flip = corr(a, -bs)
        cand_same = ("same", same, shift)
        cand_flip = ("flip", flip, shift)
        cand = cand_same if cand_same[1] >= cand_flip[1] else cand_flip
        if best is None or cand[1] > best[1]:
            best = cand
    return best  # mode, corr, shift


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

    phases = []
    for k in range(12):
        theta = 2.0 * math.pi * k / 12.0
        vec = math.cos(theta) * v1 + math.sin(theta) * v2

        class_avg, coarse = project_to_classes(vec, nodes, th_face)
        residual = vec - coarse
        class_means = mean_face_vectors_by_class(residual, nodes, th_face, th_slot)

        phases.append({
            "k": k,
            "theta": theta,
            "class_avg": class_avg,
            "class_means": class_means,
        })

    lines = []
    lines.append("=" * 80)
    lines.append("THALION MODE SYMMETRY ALGEBRA")
    lines.append("=" * 80)
    lines.append(f"lambda_1: {eigvals[1]:.9f}")
    lines.append("")

    print("=" * 80)
    print("THALION MODE SYMMETRY ALGEBRA")
    print("=" * 80)

    # Coarse phase action: compare consecutive class-average vectors
    lines.append("COARSE 4-CLASS PHASE ACTION")
    lines.append("-" * 80)
    coarse_actions = []
    for k in range(12):
        a = phases[k]["class_avg"]
        b = phases[(k + 1) % 12]["class_avg"]
        best = best_class_shift(a, b)
        coarse_actions.append(best)
        lines.append(
            f"{k:02d}->{(k+1)%12:02d}: mode={best[0]} corr={best[1]:.12f} shift={best[2]}"
        )
        print(f"coarse {k:02d}->{(k+1)%12:02d}: mode={best[0]} corr={best[1]:.6f} shift={best[2]}")
    lines.append("")

    # Fine action on opposite pairs
    lines.append("FINE 5-SLOT OPPOSITE-PAIR ACTION")
    lines.append("-" * 80)
    fine_actions_02 = []
    fine_actions_13 = []

    for k in range(12):
        cm = phases[k]["class_means"]
        law02 = best_perm(cm[0], cm[2])
        law13 = best_perm(cm[1], cm[3])
        p02 = tuple(law02[2])
        p13 = tuple(law13[2])
        fine_actions_02.append((law02[0], law02[1], p02))
        fine_actions_13.append((law13[0], law13[1], p13))

        lines.append(
            f"phase {k:02d}: "
            f"C0->C2 mode={law02[0]} corr={law02[1]:.12f} perm={list(p02)} cycles={perm_to_cycles(p02)} | "
            f"C1->C3 mode={law13[0]} corr={law13[1]:.12f} perm={list(p13)} cycles={perm_to_cycles(p13)}"
        )
    lines.append("")

    # Freeze representative laws from phase 0
    mode02, corr02, p02 = fine_actions_02[0]
    mode13, corr13, p13 = fine_actions_13[0]

    lines.append("REPRESENTATIVE SLOT LAWS (phase 00)")
    lines.append("-" * 80)
    lines.append(f"P02: mode={mode02} corr={corr02:.12f} perm={list(p02)} cycles={perm_to_cycles(p02)} order={perm_order(p02)}")
    lines.append(f"P13: mode={mode13} corr={corr13:.12f} perm={list(p13)} cycles={perm_to_cycles(p13)} order={perm_order(p13)}")
    lines.append("")

    comp = compose(p02, p13)
    lines.append("COMPOSITE SLOT LAW")
    lines.append("-" * 80)
    lines.append(f"P02 ∘ P13 = {list(comp)} cycles={perm_to_cycles(comp)} order={perm_order(comp)}")
    lines.append("")

    # Stability check
    stable02 = all((m == mode02 and tuple(p) == p02) for m, _, p in fine_actions_02)
    stable13 = all((m == mode13 and tuple(p) == p13) for m, _, p in fine_actions_13)
    lines.append("LAW STABILITY ACROSS PHASES")
    lines.append("-" * 80)
    lines.append(f"P02 stable across all 12 phases: {stable02}")
    lines.append(f"P13 stable across all 12 phases: {stable13}")
    lines.append("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print()
    print(f"saved {OUT.relative_to(ROOT)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
