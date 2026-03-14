#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hyperxi.combinatorics.chamber_graph import build_chamber_graph


def to_networkx(chg) -> nx.Graph:
    G = nx.Graph()
    G.add_nodes_from(chg.vertices)
    G.add_edges_from(chg.edges)
    return G


def main():
    print("=" * 80)
    print("CHAMBER GRAPH AUTOMORPHISM GROUP")
    print("=" * 80)

    raw = build_chamber_graph()
    G = to_networkx(raw)

    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted(set(dict(G.degree()).values())))
    print()

    gm = GraphMatcher(G, G)

    count = 0
    for _ in gm.isomorphisms_iter():
        count += 1

    print("automorphism group size:", count)
    print()


if __name__ == "__main__":
    main()
