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
OUT = ROOT / "reports" / "spectral" / "nodal" / "thalion_residual_class_invariance.txt"

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


def vector_stats(vectors):
    arr = np.array(vectors, dtype=float)
    mean = np.mean(arr, axis=0)
    centered = arr - mean
    rms = float(np.sqrt(np.mean(np.sum(centered * centered, axis=1)))) if len(arr) else 0.0
    return mean, rms


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
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    lines = []
    lines.append("=" * 80)
    lines.append("THALION RESIDUAL CLASS INVARIANCE")
    lines.append("=" * 80)
    lines.append(f"internal vertices: {G.number_of_nodes()}")
    lines.append(f"internal edges:    {G.number_of_edges()}")
    lines.append(f"lambda_1:          {eigvals[1]:.9f}")
    lines.append(f"first block:       {block}")
    lines.append("")

    print("=" * 80)
    print("THALION RESIDUAL CLASS INVARIANCE")
    print("=" * 80)
    print(f"lambda_1 ≈ {eigvals[1]:.9f}")
    print()

    for k in range(12):
        theta = 2.0 * math.pi * k / 12.0
        vec = math.cos(theta) * v1 + math.sin(theta) * v2

        _, coarse = project_to_classes(vec, nodes, th_face)
        residual = vec - coarse

        face_slot_vec = {}
        for face in range(12):
            vals = np.zeros(5, dtype=float)
            count = np.zeros(5, dtype=int)

            for node in nodes:
                if th_face[node] != face:
                    continue
                slot = th_slot[node]
                vals[slot] = float(residual[node_to_idx[node]])
                count[slot] += 1

            if not np.all(count == 1):
                raise RuntimeError(f"Face {face} did not produce exactly one value per slot: {count.tolist()}")

            face_slot_vec[face] = vals

        class_groups = defaultdict(list)
        for face in range(12):
            cls = FACE_CLASS[face]
            class_groups[cls].append(face_slot_vec[face])

        lines.append(f"PHASE {k:02d} theta={theta:.9f}")
        lines.append("-" * 80)

        print(f"PHASE {k:02d} theta={theta:.3f}")

        for cls in range(4):
            mean_vec, rms = vector_stats(class_groups[cls])
            lines.append(f"class C{cls}: within-class RMS spread = {rms:.12f}")
            lines.append("  mean slot vector: " + " ".join(f"{x:+.12f}" for x in mean_vec))
            for face in sorted([f for f in range(12) if FACE_CLASS[f] == cls]):
                vecf = face_slot_vec[face]
                lines.append(f"  face {face:2d}: " + " ".join(f"{x:+.12f}" for x in vecf))
            lines.append("")
            print(f"  C{cls}: RMS spread = {rms:.12e}")

        # Compare class means to each other as well
        class_means = {}
        for cls in range(4):
            mean_vec, _ = vector_stats(class_groups[cls])
            class_means[cls] = mean_vec

        lines.append("class-mean correlations")
        for a in range(4):
            for b in range(a + 1, 4):
                va = class_means[a]
                vb = class_means[b]
                denom = float(np.linalg.norm(va) * np.linalg.norm(vb))
                corr = float(np.dot(va, vb) / denom) if denom else 0.0
                lines.append(f"  corr(C{a}, C{b}) = {corr:.12f}")
        lines.append("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print()
    print(f"saved {OUT.relative_to(ROOT)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
