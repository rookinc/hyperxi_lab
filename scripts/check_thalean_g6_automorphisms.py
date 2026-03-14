#!/usr/bin/env python3
from __future__ import annotations

import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
G6 = ROOT / "artifacts" / "census" / "thalean_graph.g6"

def load_first_g6(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                return nx.from_graph6_bytes(line.encode())

    raise RuntimeError("No graph6 data found")


def main():

    print("=" * 80)
    print("THALEAN G6 AUTOMORPHISM GROUP")
    print("=" * 80)

    G = load_first_g6(G6)

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
