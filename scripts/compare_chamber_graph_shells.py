#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter

import networkx as nx

from hyperxi.combinatorics.chamber_graph import build_incidence_quotient_graph
from hyperxi.combinatorics.chamber_graph_scaffold import build_scaffold_chamber_graph


def to_nx(g) -> nx.Graph:
    G = nx.Graph()
    G.add_nodes_from(g.vertices)
    G.add_edges_from(g.edges)
    return G


def shell_counts(G: nx.Graph, root: int) -> list[int]:
    d = nx.single_source_shortest_path_length(G, root)
    ecc = max(d.values())
    return [sum(1 for _, dist in d.items() if dist == k) for k in range(ecc + 1)]


def centers(G: nx.Graph) -> list[int]:
    return list(nx.center(G))


def girth(G: nx.Graph) -> int | None:
    best = None
    for s in G.nodes():
        dist = {s: 0}
        parent = {s: None}
        q = [s]
        qi = 0
        while qi < len(q):
            u = q[qi]
            qi += 1
            for v in G.neighbors(u):
                if v not in dist:
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    q.append(v)
                elif parent[u] != v:
                    cyc = dist[u] + dist[v] + 1
                    if best is None or cyc < best:
                        best = cyc
    return best


def profile(name: str, G: nx.Graph) -> None:
    print("=" * 80)
    print(name.upper())
    print("=" * 80)

    ctrs = centers(G)
    print("centers:", ctrs)
    print("center count:", len(ctrs))
    print("girth:", girth(G))
    print()

    print("SHELL COUNTS FROM CENTERS")
    print("-" * 80)
    seen_profiles = Counter()

    for c in ctrs:
        shells = tuple(shell_counts(G, c))
        seen_profiles[shells] += 1

    for shells, mult in sorted(seen_profiles.items()):
        print(f"{list(shells)}   multiplicity={mult}")

    print()

    print("SHELL COUNTS FROM FIRST FEW VERTICES")
    print("-" * 80)
    for v in sorted(G.nodes())[:8]:
        print(f"{v:2d}: {shell_counts(G, v)}")

    print()


def main() -> None:
    G_scaffold = to_nx(build_scaffold_chamber_graph())
    G_incidence = to_nx(build_incidence_quotient_graph())

    profile("scaffold chamber graph", G_scaffold)
    profile("incidence quotient graph", G_incidence)


if __name__ == "__main__":
    main()
