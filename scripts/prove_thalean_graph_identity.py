#!/usr/bin/env python3

"""
prove_thalean_graph_identity.py

Canonical identity verification for the Thalean graph.

This script loads the graph6 encoding of the Thalean graph and
verifies the structural invariants that uniquely identify it.

Outputs a reproducible identity report suitable for citation
in the paper and repository documentation.
"""

import networkx as nx
from collections import Counter
from pathlib import Path

GRAPH_PATH = Path("artifacts/census/thalion_graph.g6")


def shell_counts(G, root=0):
    dist = nx.single_source_shortest_path_length(G, root)
    c = Counter(dist.values())
    return tuple(c[i] for i in range(max(c)+1))


def triangle_count(G):
    return sum(nx.triangles(G).values()) // 3


def main():

    print("="*72)
    print("THALEAN GRAPH IDENTITY REPORT")
    print("="*72)

    if not GRAPH_PATH.exists():
        raise FileNotFoundError(f"Graph file not found: {GRAPH_PATH}")

    G = nx.from_graph6_bytes(GRAPH_PATH.read_bytes().strip())

    n = G.number_of_nodes()
    m = G.number_of_edges()
    degs = sorted(set(dict(G.degree()).values()))

    print(f"nodes: {n}")
    print(f"edges: {m}")
    print(f"degree set: {degs}")

    diam = nx.diameter(G)
    tri = triangle_count(G)
    shells = shell_counts(G)

    print()
    print("STRUCTURAL INVARIANTS")
    print("-"*72)
    print(f"diameter: {diam}")
    print(f"triangles: {tri}")
    print(f"shell counts: {shells}")

    print()
    print("SPECTRUM")
    print("-"*72)

    import numpy as np

    A = nx.to_numpy_array(G)
    vals = np.linalg.eigvals(A)
    vals = sorted([round(v.real, 6) for v in vals])

    counts = Counter(vals)

    for v,c in sorted(counts.items()):
        print(f"{v:10.6f} : {c}")

    print()
    print("IDENTITY CHECK")
    print("-"*72)

    expected = {
        "nodes":60,
        "edges":120,
        "degree":4,
        "diameter":6,
        "triangles":40,
        "shells":(1,4,8,16,24,6,1)
    }

    ok = True

    if n != expected["nodes"]:
        ok = False

    if m != expected["edges"]:
        ok = False

    if degs != [expected["degree"]]:
        ok = False

    if diam != expected["diameter"]:
        ok = False

    if tri != expected["triangles"]:
        ok = False

    if shells != expected["shells"]:
        ok = False

    if ok:
        print("STATUS: MATCHES THALEAN GRAPH SPECIFICATION")
        print()
        print("Graph corresponds to:")
        print("  AT4val[60,6]")
        print("  HouseOfGraphs Graph52002")
    else:
        print("STATUS: INVARIANT MISMATCH DETECTED")


if __name__ == "__main__":
    main()
