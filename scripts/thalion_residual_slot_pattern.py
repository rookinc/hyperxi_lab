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
OUT = ROOT / "reports" / "spectral" / "nodal" / "thalion_residual_slot_pattern.txt"

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
    """
    Assign each internal vertex (thalion-graph vertex) a slot 0..4 within its face.

    We use a deterministic ordering of the thalions inside each face.
    Prefer edge id if available, then vertex id, then thalion id.
    """
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

        # deterministic local label
        key = (
            edge if edge is not None else 10**9,
            vertex if vertex is not None else 10**9,
            th.id,
        )
        face_buckets[face].append((key, th.id))

    th_slot = {}
    slot_summary = {}

    for face in sorted(face_buckets):
        items = sorted(face_buckets[face])
        if len(items) != 5:
            raise RuntimeError(f"Expected 5 internal vertices on face {face}, got {len(items)}")
        slot_summary[face] = [th_id for _, th_id in items]
        for slot, (_, th_id) in enumerate(items):
            th_slot[th_id] = slot

    return th_face, th_slot, slot_summary


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

    th_face, th_slot, slot_summary = build_face_slot_map()
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    lines = []
    lines.append("=" * 80)
    lines.append("THALION RESIDUAL SLOT PATTERN")
    lines.append("=" * 80)
    lines.append(f"internal vertices: {G.number_of_nodes()}")
    lines.append(f"internal edges:    {G.number_of_edges()}")
    lines.append(f"lambda_1:          {eigvals[1]:.9f}")
    lines.append(f"first block:       {block}")
    lines.append("")
    lines.append("FACE -> SLOT ORDERING")
    lines.append("-" * 80)
    for face in sorted(slot_summary):
        lines.append(f"face {face:2d}: {slot_summary[face]}")
    lines.append("")

    print("=" * 80)
    print("THALION RESIDUAL SLOT PATTERN")
    print("=" * 80)
    print(f"lambda_1 ≈ {eigvals[1]:.9f}")
    print()

    slot_profiles = []

    for k in range(12):
        theta = 2.0 * math.pi * k / 12.0
        vec = math.cos(theta) * v1 + math.sin(theta) * v2

        class_avg, coarse = project_to_classes(vec, nodes, th_face)
        residual = vec - coarse

        slot_vals = defaultdict(list)
        face_slot_vals = defaultdict(dict)

        for node in nodes:
            slot = th_slot[node]
            val = float(residual[node_to_idx[node]])
            slot_vals[slot].append(val)
            face = th_face[node]
            face_slot_vals[face][slot] = val

        slot_mean = {s: float(np.mean(vals)) for s, vals in slot_vals.items()}
        slot_std = {s: float(np.std(vals)) for s, vals in slot_vals.items()}
        slot_profiles.append(np.array([slot_mean[s] for s in sorted(slot_mean)], dtype=float))

        lines.append(f"PHASE {k:02d} theta={theta:.9f}")
        lines.append("-" * 80)
        lines.append("slot means / stddev:")
        for s in sorted(slot_mean):
            lines.append(
                f"  slot {s}: mean={slot_mean[s]:+.12f} std={slot_std[s]:.12f}"
            )
        lines.append("per-face residuals by slot:")
        for face in sorted(face_slot_vals):
            vals = [face_slot_vals[face][s] for s in sorted(face_slot_vals[face])]
            lines.append(
                f"  face {face:2d}: " +
                " ".join(f"{v:+.12f}" for v in vals)
            )
        lines.append("")

        print(
            f"k={k:02d} theta={theta:.3f} "
            + " ".join(f"s{s}={slot_mean[s]:+.6f}" for s in sorted(slot_mean))
        )

    # Compare phase profiles
    lines.append("PROFILE COMPARISON")
    lines.append("-" * 80)
    ref = slot_profiles[0]
    ref_norm = float(np.linalg.norm(ref))
    for k, prof in enumerate(slot_profiles):
        dot = float(np.dot(ref, prof))
        denom = ref_norm * float(np.linalg.norm(prof))
        corr = dot / denom if denom else 0.0
        lines.append(f"phase {k:02d}: slot-profile correlation with phase 00 = {corr:.12f}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print()
    print(f"saved {OUT.relative_to(ROOT)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
