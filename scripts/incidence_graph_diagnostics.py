#!/usr/bin/env python3
from __future__ import annotations

import networkx as nx
import numpy as np

from hyperxi.combinatorics.chamber_graph import build_chamber_graph


def main():

    g = build_chamber_graph()

    G = nx.Graph()
    G.add_nodes_from(g.vertices)
    G.add_edges_from(g.edges)

    print("=" * 80)
    print("INCIDENCE QUOTIENT GRAPH DIAGNOSTICS")
    print("=" * 80)

    print("nodes:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted(set(dict(G.degree()).values())))
    print()

    print("connected:", nx.is_connected(G))
    print("components:", nx.number_connected_components(G))
    print("bipartite:", nx.is_bipartite(G))
    print("triangles:", sum(nx.triangles(G).values()) // 3)

    if nx.is_connected(G):
        print("diameter:", nx.diameter(G))
        print("radius:", nx.radius(G))

    print()

    # adjacency matrix
    nodes = sorted(G.nodes())
    A = nx.to_numpy_array(G, nodelist=nodes, dtype=int)

    print("CLOSED WALK TRACES")
    print("-" * 80)

    for k in range(1, 11):
        Ak = np.linalg.matrix_power(A, k)
        tr = int(np.trace(Ak))
        print(f"trace(A^{k}) = {tr}")

    print()

    print("SPECTRUM")
    print("-" * 80)

    eigvals = np.linalg.eigvalsh(A.astype(float))
    eigvals = np.round(eigvals, 6)

    uniq, counts = np.unique(eigvals, return_counts=True)

    for v, c in zip(uniq, counts):
        print(f"{v: .6f}: {c}")

    print("=" * 80)


if __name__ == "__main__":
    main()
