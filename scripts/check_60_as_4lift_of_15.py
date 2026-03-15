#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from collections import defaultdict

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]

# allow importing helper script
sys.path.insert(0, str(ROOT / "scripts"))

from load_thalean_graph import load_spec, build_graph


# ------------------------------------------------------------
# helpers
# ------------------------------------------------------------

def shell_profile(G: nx.Graph, src: int = 0):
    dist = nx.single_source_shortest_path_length(G, src)
    hist = defaultdict(int)

    for d in dist.values():
        hist[d] += 1

    return tuple(hist[i] for i in range(max(hist) + 1))


def degree_signature(G):
    sig = {}

    for v in G:
        dist = nx.single_source_shortest_path_length(G, v)
        sig[v] = tuple(sorted(dist.values()))

    return sig


# ------------------------------------------------------------
# clustering attempt for 4-lift fibers
# ------------------------------------------------------------

def cluster_vertices(G60, fiber_size=4):

    sig = degree_signature(G60)

    buckets = defaultdict(list)

    for v, s in sig.items():
        buckets[s].append(v)

    fibers = []

    for vs in buckets.values():
        for i in range(0, len(vs), fiber_size):
            fibers.append(vs[i:i + fiber_size])

    return fibers


# ------------------------------------------------------------
# lift check
# ------------------------------------------------------------

def check_lift(G60, G15, fibers):

    fiber_map = {}

    for i, f in enumerate(fibers):
        for v in f:
            fiber_map[v] = i

    if len(fibers) != 15:
        return False

    H = nx.Graph()
    H.add_nodes_from(range(len(fibers)))

    for u, v in G60.edges():

        fu = fiber_map[u]
        fv = fiber_map[v]

        if fu != fv:
            H.add_edge(fu, fv)

    return nx.is_isomorphic(H, G15)


# ------------------------------------------------------------
# graph loading
# ------------------------------------------------------------

def load_graphs():

    # build the live 60-graph
    G60 = build_graph(load_spec())

    # canonical 15-core
    P = nx.petersen_graph()
    G15 = nx.line_graph(P)

    return G60, G15


# ------------------------------------------------------------
# main
# ------------------------------------------------------------

def main():

    print("=" * 80)
    print("CHECK 60 GRAPH AS 4-LIFT OF 15 CORE")
    print("=" * 80)

    G60, G15 = load_graphs()

    print("G60 summary")
    print("-" * 80)
    print("vertices:", G60.number_of_nodes())
    print("edges:", G60.number_of_edges())
    print("degree set:", sorted(set(dict(G60.degree()).values())))
    print("shell profile:", shell_profile(G60))
    print()

    print("G15 summary")
    print("-" * 80)
    print("vertices:", G15.number_of_nodes())
    print("edges:", G15.number_of_edges())
    print("degree set:", sorted(set(dict(G15.degree()).values())))
    print()

    fibers = cluster_vertices(G60)

    print("candidate fibers:", len(fibers))
    print("fiber sizes:", sorted(len(x) for x in fibers))
    print()

    ok = check_lift(G60, G15, fibers)

    print("is 4-lift of G15:", ok)


if __name__ == "__main__":
    main()
