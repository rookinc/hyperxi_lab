#!/usr/bin/env python3
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import networkx as nx
import numpy as np

from hyperxi.combinatorics.chamber_graph import build_chamber_graph
from hyperxi.combinatorics.thalions import build_thalions

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "spectral" / "nodal" / "thalion_face_class_quotient.txt"

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


def load_graph() -> nx.Graph:
    raw = build_chamber_graph()
    G = nx.Graph()
    G.add_nodes_from(raw.vertices)
    G.add_edges_from(raw.edges)
    return G


def thalion_face_and_class_maps():
    thalions = build_thalions()

    th_face = {}
    th_class = {}

    for th in thalions:
        faces = sorted({extract_face(m) for m in th.members})
        if len(faces) != 1:
            raise RuntimeError(
                f"Expected each thalion to sit on one face, but thalion {th.id} has faces {faces}"
            )
        face = faces[0]
        th_face[th.id] = face
        th_class[th.id] = FACE_CLASS[face]

    return th_face, th_class


def main():
    G = load_graph()
    th_face, th_class = thalion_face_and_class_maps()

    class_nodes = defaultdict(list)
    for th_id, cls in th_class.items():
        class_nodes[cls].append(th_id)

    edge_counts = np.zeros((4, 4), dtype=int)
    for a, b in G.edges():
        ca = th_class[a]
        cb = th_class[b]
        edge_counts[ca, cb] += 1
        if ca != cb:
            edge_counts[cb, ca] += 1

    # Directed-by-count version above is convenient for reading.
    # Build symmetric undirected inter-class counts separately.
    undirected_inter = np.zeros((4, 4), dtype=int)
    intra_edges = np.zeros(4, dtype=int)

    for a, b in G.edges():
        ca = th_class[a]
        cb = th_class[b]
        if ca == cb:
            intra_edges[ca] += 1
        else:
            i, j = sorted((ca, cb))
            undirected_inter[i, j] += 1
            undirected_inter[j, i] += 1

    # Quotient adjacency: weight between classes = number of edges across the partition
    Q = undirected_inter.astype(float)
    q_eigvals, _ = np.linalg.eigh(Q)
    q_eigvals = np.sort(q_eigvals)[::-1]

    # Class-signature model inferred from your spectral result
    signature_vectors = {
        "A": np.array([+1, +1, -1, -1], dtype=float),
        "B": np.array([+1, -1, -1, +1], dtype=float),
    }

    lines = []
    lines.append("=" * 80)
    lines.append("THALION FACE-CLASS QUOTIENT")
    lines.append("=" * 80)
    lines.append(f"thalion vertices: {G.number_of_nodes()}")
    lines.append(f"thalion edges:    {G.number_of_edges()}")
    lines.append("")

    lines.append("FACE CLASSES")
    lines.append("-" * 80)
    for cls in range(4):
        faces = [f for f, c in FACE_CLASS.items() if c == cls]
        nodes = sorted(class_nodes[cls])
        lines.append(f"class C{cls}: faces={faces}  thalions={nodes}")
    lines.append("")

    lines.append("INTRA-CLASS EDGE COUNTS")
    lines.append("-" * 80)
    for cls in range(4):
        lines.append(f"C{cls}-C{cls}: {int(intra_edges[cls])}")
    lines.append("")

    lines.append("INTER-CLASS EDGE MATRIX")
    lines.append("-" * 80)
    lines.append("      C0  C1  C2  C3")
    for i in range(4):
        row = " ".join(f"{int(undirected_inter[i,j]):3d}" for j in range(4))
        lines.append(f"C{i} : {row}")
    lines.append("")

    lines.append("QUOTIENT ADJACENCY EIGENVALUES")
    lines.append("-" * 80)
    for val in q_eigvals:
        lines.append(f"{val:.9f}")
    lines.append("")

    lines.append("SIGNATURE TESTS ON QUOTIENT")
    lines.append("-" * 80)
    lines.append("Using vectors on classes [C0,C1,C2,C3].")
    for name, vec in signature_vectors.items():
        image = Q @ vec
        # Rayleigh quotient
        rq = float(vec @ image) / float(vec @ vec)
        lines.append(f"{name}: vec={vec.astype(int).tolist()}  Qv={image.astype(int).tolist()}  rq={rq:.9f}")
    lines.append("")

    print("=" * 80)
    print("THALION FACE-CLASS QUOTIENT")
    print("=" * 80)
    print("INTER-CLASS EDGE MATRIX")
    print("-" * 80)
    print("      C0  C1  C2  C3")
    for i in range(4):
        row = " ".join(f"{int(undirected_inter[i,j]):3d}" for j in range(4))
        print(f"C{i} : {row}")
    print()
    print("QUOTIENT EIGENVALUES")
    print("-" * 80)
    for val in q_eigvals:
        print(f"{val:.9f}")
    print()
    print("SIGNATURE TESTS")
    print("-" * 80)
    for name, vec in signature_vectors.items():
        image = Q @ vec
        rq = float(vec @ image) / float(vec @ vec)
        print(f"{name}: vec={vec.astype(int).tolist()}  Qv={image.astype(int).tolist()}  rq={rq:.9f}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print()
    print(f"saved {OUT.relative_to(ROOT)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
