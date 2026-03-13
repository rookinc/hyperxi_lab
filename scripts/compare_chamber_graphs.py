#!/usr/bin/env python3
from __future__ import annotations

import networkx as nx
import numpy as np

from hyperxi.combinatorics.chamber_graph import build_incidence_quotient_graph
from hyperxi.combinatorics.chamber_graph_scaffold import build_scaffold_chamber_graph


def to_nx(g):
    G = nx.Graph()
    G.add_nodes_from(g.vertices)
    G.add_edges_from(g.edges)
    return G


def describe(name, G):
    print("=" * 80)
    print(name.upper())
    print("=" * 80)

    print("nodes:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted(set(dict(G.degree()).values())))
    print("connected:", nx.is_connected(G))
    print("components:", nx.number_connected_components(G))
    print("bipartite:", nx.is_bipartite(G))
    print("triangles:", sum(nx.triangles(G).values()) // 3)

    if nx.is_connected(G):
        print("diameter:", nx.diameter(G))
        print("radius:", nx.radius(G))

    print()

    A = nx.to_numpy_array(G, nodelist=sorted(G.nodes()), dtype=float)

    vals = np.linalg.eigvalsh(A)
    vals = np.round(vals, 6)

    uniq, counts = np.unique(vals, return_counts=True)

    print("spectrum")
    print("-" * 80)

    for v, c in zip(uniq, counts):
        print(f"{v: .6f}: {c}")

    print()


def main():
    G_scaffold = to_nx(build_scaffold_chamber_graph())
    G_incidence = to_nx(build_incidence_quotient_graph())

    describe("scaffold chamber graph", G_scaffold)
    describe("incidence quotient graph", G_incidence)


if __name__ == "__main__":
    main()
