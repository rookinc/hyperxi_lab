#!/usr/bin/env python3
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import networkx as nx

from hyperxi.combinatorics.chamber_graph import build_chamber_graph
from hyperxi.combinatorics.thalions import build_thalions

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "spectral" / "nodal" / "thalion_slot_law_automorphism_check.txt"

FACE_CLASS = {
    0: 0, 4: 0, 8: 0,
    1: 1, 5: 1, 9: 1,
    2: 2, 6: 2, 10: 2,
    3: 3, 7: 3, 11: 3,
}

P02 = [2, 1, 4, 3, 0]
P13 = [4, 3, 2, 0, 1]


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


def build_face_slot_map():
    thalions = build_thalions()
    face_buckets = defaultdict(list)
    th_face = {}

    for th in thalions:
        members = list(th.members)
        faces = sorted({extract_face(m) for m in members})
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


def make_map(face_slot_nodes, face_map, slot_perm):
    mapping = {}
    for f_src, f_dst in face_map.items():
        src_nodes = face_slot_nodes[f_src]
        dst_nodes = face_slot_nodes[f_dst]
        for s in range(5):
            mapping[src_nodes[s]] = dst_nodes[slot_perm[s]]
    return mapping


def is_graph_automorphism(G, mapping):
    for u, v in G.edges():
        mu = mapping[u]
        mv = mapping[v]
        if not G.has_edge(mu, mv):
            return False
    # bijection + edge count preservation is enough for simple graph here
    return len(set(mapping.values())) == G.number_of_nodes()


def main():
    G = load_graph()
    _, _, face_slot_nodes = build_face_slot_map()

    # class-pair face maps
    map_02 = {0: 2, 4: 6, 8: 10, 2: 0, 6: 4, 10: 8}
    map_13 = {1: 3, 5: 7, 9: 11, 3: 1, 7: 5, 11: 9}

    # identity elsewhere
    for f in range(12):
        map_02.setdefault(f, f)
        map_13.setdefault(f, f)

    m02 = make_map(face_slot_nodes, map_02, P02)
    m13 = make_map(face_slot_nodes, map_13, P13)

    ok02 = is_graph_automorphism(G, m02)
    ok13 = is_graph_automorphism(G, m13)

    text = []
    text.append("=" * 80)
    text.append("THALION SLOT LAW AUTOMORPHISM CHECK")
    text.append("=" * 80)
    text.append(f"P02 = {P02}")
    text.append(f"P13 = {P13}")
    text.append(f"P02 lifts to automorphism: {ok02}")
    text.append(f"P13 lifts to automorphism: {ok13}")

    OUT.write_text("\n".join(text) + "\n", encoding="utf-8")
    print("\n".join(text))


if __name__ == "__main__":
    main()
