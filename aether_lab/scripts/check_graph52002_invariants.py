#!/usr/bin/env python3
from __future__ import annotations

import networkx as nx
from hyperxi.combinatorics.chamber_graph import build_chamber_graph


def to_networkx(G):
    """Convert HyperXi ChamberGraph → networkx Graph."""
    H = nx.Graph()

    for v in G.vertices:
        H.add_node(v)

    for u, v in G.edges:
        H.add_edge(u, v)

    return H


def summarize(G):
    print("="*80)
    print("HYPERXI CHAMBER GRAPH")
    print("="*80)

    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted({d for _, d in G.degree()}))
    print("triangles:", sum(nx.triangles(G).values()) // 3)
    print("diameter:", nx.diameter(G))

    vals = sorted(nx.adjacency_spectrum(G).real)

    print("\nfirst 10 eigenvalues")
    for x in vals[:10]:
        print(f"{x:.6f}")

    print("\nlast 10 eigenvalues")
    for x in vals[-10:]:
        print(f"{x:.6f}")


def shell_profile(G, v):
    d = nx.single_source_shortest_path_length(G, v)
    diam = max(d.values())
    return tuple(sum(1 for x in d.values() if x == k) for k in range(diam+1))


def main():
    G_hx = build_chamber_graph()
    G = to_networkx(G_hx)

    summarize(G)

    print("\nSHELL PROFILE SAMPLE")
    for v in list(G.nodes())[:5]:
        print(v, shell_profile(G, v))


if __name__ == "__main__":
    main()
