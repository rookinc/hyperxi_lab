#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from collections import defaultdict

import networkx as nx
import numpy as np

from hyperxi.combinatorics.chamber_graph import build_chamber_graph
from hyperxi.combinatorics.thalions import build_thalions

OUT = "reports/spectral/nodal/thalion_cubic_slot_animation.json"

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


def build_face_slot_map():
    thalions = build_thalions()
    face_buckets = defaultdict(list)
    th_face = {}

    for th in thalions:
        members = list(th.members)
        faces = sorted({extract_face(m) for m in members})
        if len(faces) != 1:
            raise RuntimeError(f"Expected one face per internal vertex, got {th.id}: {faces}")
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
        face_slot_nodes[face] = []
        for slot, (_, th_id) in enumerate(items):
            th_slot[th_id] = slot
            face_slot_nodes[face].append(th_id)

    return th_face, th_slot, face_slot_nodes


def coarse_projection(vec, nodes, th_face):
    node_to_idx = {node: i for i, node in enumerate(nodes)}
    class_vals = defaultdict(list)
    for node in nodes:
        cls = FACE_CLASS[th_face[node]]
        class_vals[cls].append(float(vec[node_to_idx[node]]))
    class_avg = {c: float(np.mean(class_vals[c])) for c in range(4)}
    lifted = np.array([class_avg[FACE_CLASS[th_face[node]]] for node in nodes], dtype=float)
    return class_avg, lifted


def main():
    print("=" * 80)
    print("EXPORT THALION CUBIC SLOT ANIMATION")
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

    th_face, th_slot, face_slot_nodes = build_face_slot_map()
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    frames = []
    steps = 12

    for k in range(steps):
        theta = 2.0 * math.pi * k / steps
        vec = math.cos(theta) * v1 + math.sin(theta) * v2

        _, coarse = coarse_projection(vec, nodes, th_face)
        residual = vec - coarse

        face_slot_values = {}
        for face in range(12):
            slot_vals = {}
            for node in nodes:
                if th_face[node] != face:
                    continue
                slot = th_slot[node]
                slot_vals[str(slot)] = float(residual[node_to_idx[node]])
            face_slot_values[str(face)] = slot_vals

        frames.append({
            "phase_index": k,
            "theta": theta,
            "face_slot_values": face_slot_values,
        })

    payload = {
        "name": "thalion_cubic_slot_animation",
        "eigenvalue": float(eigvals[1]),
        "steps": steps,
        "face_slot_nodes": {str(face): nodes for face, nodes in sorted(face_slot_nodes.items())},
        "frames": frames,
    }

    with open(OUT, "w") as fp:
        json.dump(payload, fp, indent=2)

    print("saved:", OUT)
    print("=" * 80)


if __name__ == "__main__":
    main()
