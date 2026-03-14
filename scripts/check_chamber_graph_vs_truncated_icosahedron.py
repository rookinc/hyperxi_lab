#!/usr/bin/env python3
from __future__ import annotations

import networkx as nx

from hyperxi.combinatorics.chamber_graph import build_chamber_graph


def summarize(name: str, G: nx.Graph) -> None:
    print("=" * 80)
    print(name)
    print("=" * 80)
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted({d for _, d in G.degree()}))
    print("triangles:", sum(nx.triangles(G).values()) // 3)
    print("diameter:", nx.diameter(G) if nx.is_connected(G) else None)
    print("spectrum (top 10):")
    vals = sorted(nx.adjacency_spectrum(G).real, reverse=True)
    for x in vals[:10]:
        print(f"  {x:.6f}")
    print()


def main() -> None:
    G_hx = build_chamber_graph()
    G_ti = nx.truncated_icosahedron_graph()

    summarize("HYPERXI CHAMBER GRAPH", G_hx)
    summarize("TRUNCATED ICOSAHEDRON GRAPH", G_ti)

    print("=" * 80)
    print("ISOMORPHISM TEST")
    print("=" * 80)
    iso = nx.is_isomorphic(G_hx, G_ti)
    print("isomorphic:", iso)

    if not iso:
        em_hx = sorted(nx.adjacency_spectrum(G_hx).real)
        em_ti = sorted(nx.adjacency_spectrum(G_ti).real)
        same_spec = len(em_hx) == len(em_ti) and all(abs(a - b) < 1e-8 for a, b in zip(em_hx, em_ti))
        print("cospectral:", same_spec)

        tri_hx = sum(nx.triangles(G_hx).values()) // 3
        tri_ti = sum(nx.triangles(G_ti).values()) // 3
        print("triangle counts:", tri_hx, tri_ti)

        shells_hx = sorted(
            tuple(sum(1 for v in nx.single_source_shortest_path_length(G_hx, u).values() if v == k)
                  for k in range(nx.diameter(G_hx) + 1))
            for u in G_hx.nodes()
        )
        shells_ti = sorted(
            tuple(sum(1 for v in nx.single_source_shortest_path_length(G_ti, u).values() if v == k)
                  for k in range(nx.diameter(G_ti) + 1))
            for u in G_ti.nodes()
        )
        print("same shell multiset:", shells_hx == shells_ti)


if __name__ == "__main__":
    main()
