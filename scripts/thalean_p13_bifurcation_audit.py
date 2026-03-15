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
OUT = ROOT / "reports" / "spectral" / "nodal" / "thalion_p13_bifurcation_audit.txt"

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
    return best


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


def crossing_cut(G: nx.Graph, nodes: list[int], vec: np.ndarray):
    node_to_idx = {v: i for i, v in enumerate(nodes)}
    cut = []
    for a, b in sorted(G.edges()):
        ia = node_to_idx[a]
        ib = node_to_idx[b]
        sa = np.sign(vec[ia])
        sb = np.sign(vec[ib])
        if sa == 0 or sb == 0:
            continue
        if sa != sb:
            cut.append((a, b))
    return tuple(cut)


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

    # First collect nodal regimes
    cut_labels = {}
    seen_cuts = {}
    next_label = "A"

    records = []

    for k in range(12):
        theta = 2.0 * math.pi * k / 12.0
        vec = math.cos(theta) * v1 + math.sin(theta) * v2

        _, coarse = project_to_classes(vec, nodes, th_face)
        residual = vec - coarse
        class_means = mean_face_vectors_by_class(residual, nodes, th_face, th_slot)

        law13 = best_perm(class_means[1], class_means[3])
        perm13 = tuple(law13[2])
        cycles13 = perm_to_cycles(perm13)

        cut = crossing_cut(G, nodes, vec)
        if cut not in seen_cuts:
            seen_cuts[cut] = next_label
            next_label = "B" if next_label == "A" else chr(ord(next_label) + 1)
        cut_label = seen_cuts[cut]

        quarter_block = k // 3

        records.append({
            "k": k,
            "theta": theta,
            "quarter_block": quarter_block,
            "cut_label": cut_label,
            "mode13": law13[0],
            "corr13": law13[1],
            "perm13": perm13,
            "cycles13": cycles13,
        })

    # group by perm
    perm_groups = defaultdict(list)
    for r in records:
        perm_groups[r["perm13"]].append(r["k"])

    lines = []
    lines.append("=" * 80)
    lines.append("THALION P13 BIFURCATION AUDIT")
    lines.append("=" * 80)
    lines.append(f"lambda_1: {eigvals[1]:.9f}")
    lines.append("")

    lines.append("PER-PHASE P13 DATA")
    lines.append("-" * 80)
    for r in records:
        lines.append(
            f"phase {r['k']:02d}: "
            f"theta={r['theta']:.9f} "
            f"quarter_block={r['quarter_block']} "
            f"cut={r['cut_label']} "
            f"mode={r['mode13']} "
            f"corr={r['corr13']:.12f} "
            f"perm={list(r['perm13'])} "
            f"cycles={r['cycles13']}"
        )
    lines.append("")

    lines.append("P13 PERMUTATION GROUPS")
    lines.append("-" * 80)
    for perm, ks in perm_groups.items():
        lines.append(f"perm={list(perm)} cycles={perm_to_cycles(perm)} phases={ks}")
    lines.append("")

    lines.append("P13 VS QUARTER BLOCK")
    lines.append("-" * 80)
    by_block = defaultdict(list)
    for r in records:
        by_block[r["quarter_block"]].append(r["k"])
    for b in sorted(by_block):
        perms = sorted({tuple(rec["perm13"]) for rec in records if rec["quarter_block"] == b})
        lines.append(f"block {b}: phases={by_block[b]} perms={[list(p) for p in perms]}")
    lines.append("")

    lines.append("P13 VS NODAL CUT REGIME")
    lines.append("-" * 80)
    by_cut = defaultdict(list)
    for r in records:
        by_cut[r["cut_label"]].append(r["k"])
    for c in sorted(by_cut):
        perms = sorted({tuple(rec["perm13"]) for rec in records if rec["cut_label"] == c})
        lines.append(f"cut {c}: phases={by_cut[c]} perms={[list(p) for p in perms]}")
    lines.append("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("=" * 80)
    print("THALION P13 BIFURCATION AUDIT")
    print("=" * 80)
    for perm, ks in perm_groups.items():
        print(f"perm={list(perm)} cycles={perm_to_cycles(perm)} phases={ks}")
    print()
    print(f"saved {OUT.relative_to(ROOT)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
