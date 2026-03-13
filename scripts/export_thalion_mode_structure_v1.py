#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from collections import defaultdict
from itertools import permutations
from pathlib import Path

import networkx as nx
import numpy as np

from hyperxi.combinatorics.chamber_graph import build_chamber_graph
from hyperxi.combinatorics.thalions import build_thalions

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "spec" / "thalion_mode_structure_v1.json"

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
    face_slot_nodes = {}
    for face in sorted(face_buckets):
        items = sorted(face_buckets[face])
        if len(items) != 5:
            raise RuntimeError(f"Expected 5 internal vertices on face {face}, got {len(items)}")
        face_slot_nodes[face] = []
        for slot, (_, th_id) in enumerate(items):
            th_slot[th_id] = slot
            face_slot_nodes[face].append(th_id)

    return th_face, th_slot, face_slot_nodes


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


def rel_error(vec, approx):
    num = float(np.linalg.norm(vec - approx))
    den = float(np.linalg.norm(vec))
    return num / den if den > 0 else 0.0


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

    th_face, th_slot, face_slot_nodes = build_face_slot_map()

    face_class_groups = {
        "C0": [0, 4, 8],
        "C1": [1, 5, 9],
        "C2": [2, 6, 10],
        "C3": [3, 7, 11],
    }

    phases = []
    cut_labels = {}
    seen_cuts = {}
    next_label = "A"

    coarse_corrs = []
    face_errs = []
    class_errs = []

    for k in range(12):
        theta = 2.0 * math.pi * k / 12.0
        vec = math.cos(theta) * v1 + math.sin(theta) * v2

        class_avg, coarse = project_to_classes(vec, nodes, th_face)
        residual = vec - coarse
        class_means = mean_face_vectors_by_class(residual, nodes, th_face, th_slot)

        cut = crossing_cut(G, nodes, vec)
        if cut not in seen_cuts:
            seen_cuts[cut] = next_label
            next_label = chr(ord(next_label) + 1)
        cut_label = seen_cuts[cut]

        face_avg = {}
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        for f in range(12):
            vals = [float(vec[node_to_idx[n]]) for n in nodes if th_face[n] == f]
            face_avg[f] = float(np.mean(vals))
        lifted_face = np.array([face_avg[th_face[node]] for node in nodes], dtype=float)

        err_face = rel_error(vec, lifted_face)
        err_class = rel_error(vec, coarse)
        face_errs.append(err_face)
        class_errs.append(err_class)

        law02 = best_perm(class_means[0], class_means[2])
        law13 = best_perm(class_means[1], class_means[3])

        phases.append({
            "phase_index": k,
            "theta": theta,
            "quarter_block": k // 3,
            "cut_regime": cut_label,
            "class_avg": class_avg.tolist(),
            "face_avg": {str(f): face_avg[f] for f in sorted(face_avg)},
            "residual_norm_fraction": float(np.linalg.norm(residual) / np.linalg.norm(vec)),
            "coarse_norm_fraction": float(np.linalg.norm(coarse) / np.linalg.norm(vec)),
            "face_projection_error": err_face,
            "class_projection_error": err_class,
            "P02": {
                "mode": law02[0],
                "corr": law02[1],
                "perm": list(law02[2]),
                "cycles": [list(c) for c in perm_to_cycles(law02[2])],
            },
            "P13": {
                "mode": law13[0],
                "corr": law13[1],
                "perm": list(law13[2]),
                "cycles": [list(c) for c in perm_to_cycles(law13[2])],
            },
        })

    for k in range(12):
        a = np.array(phases[k]["class_avg"], dtype=float)
        b = np.array(phases[(k + 1) % 12]["class_avg"], dtype=float)
        coarse_corrs.append(corr(a, b))

    p13_groups = defaultdict(list)
    for r in phases:
        p13_groups[tuple(r["P13"]["perm"])].append(r["phase_index"])

    data = {
        "name": "thalion_mode_structure_v1",
        "object": "single_thalion_internal_60_vertex_graph",
        "version": "v1",
        "graph": {
            "vertex_count": G.number_of_nodes(),
            "edge_count": G.number_of_edges(),
            "degree_set": sorted(set(dict(G.degree()).values())),
        },
        "spectrum": {
            "first_excited_eigenvalue": float(eigvals[1]),
            "first_excited_block_indices": block,
            "first_excited_block_dimension": len(block),
        },
        "coarse_structure": {
            "face_class_groups": face_class_groups,
            "coarse_phase_step_correlation": {
                "min": min(coarse_corrs),
                "max": max(coarse_corrs),
                "avg": sum(coarse_corrs) / len(coarse_corrs),
                "interpretation": "cos(pi/6)-like fixed-basis phase advance",
            },
            "projection": {
                "face_projection_error_constant": all(abs(x - face_errs[0]) < 1e-12 for x in face_errs),
                "class_projection_error_constant": all(abs(x - class_errs[0]) < 1e-12 for x in class_errs),
                "face_projection_error": face_errs[0],
                "class_projection_error": class_errs[0],
                "coarse_norm_fraction": phases[0]["coarse_norm_fraction"],
                "residual_norm_fraction": phases[0]["residual_norm_fraction"],
            },
        },
        "fine_structure": {
            "stable_P02": {
                "mode": phases[0]["P02"]["mode"],
                "corr": phases[0]["P02"]["corr"],
                "perm": phases[0]["P02"]["perm"],
                "cycles": phases[0]["P02"]["cycles"],
                "order": 3,
                "phase_stable": all(
                    r["P02"]["mode"] == phases[0]["P02"]["mode"] and
                    r["P02"]["perm"] == phases[0]["P02"]["perm"]
                    for r in phases
                ),
                "interpretation": "opposite-pair C0<->C2 permuted sign reversal",
            },
            "default_P13": {
                "mode": "same",
                "perm": [4, 3, 2, 1, 0],
                "cycles": [[0, 4], [1, 3], [2]],
                "order": 2,
                "interpretation": "default opposite-pair C1<->C3 double-swap branch",
            },
            "exceptional_P13": {
                "mode": "same",
                "perm": [4, 3, 2, 0, 1],
                "cycles": [[0, 4, 1, 3], [2]],
                "order": 4,
                "phases": p13_groups.get((4, 3, 2, 0, 1), []),
                "interpretation": "exceptional C1<->C3 four-cycle branch",
            },
        },
        "slot_maps": {
            "face_slot_nodes": {str(face): nodes for face, nodes in sorted(face_slot_nodes.items())},
        },
        "phases": phases,
        "notes": [
            "One thalion carries an internal 60-vertex graph.",
            "The first excited mode has a 2D eigenspace.",
            "The coarse mode lives on four face classes, while the fine mode carries a 5-slot residual structure.",
            "P02 is robust and phase-stable; P13 is bifurcated with a default and an exceptional branch.",
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    print(f"saved {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
