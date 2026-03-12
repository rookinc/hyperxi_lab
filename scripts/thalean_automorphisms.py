#!/usr/bin/env python3

from pathlib import Path
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

ROOT = Path(__file__).resolve().parents[1]
G6_PATH = ROOT / "artifacts/census/thalion_graph.g6"


def load_graph():
    g6 = G6_PATH.read_text().strip()
    G = nx.from_graph6_bytes(g6.encode())
    return nx.convert_node_labels_to_integers(G)


def main():
    G = load_graph()

    print("=" * 80)
    print("THALEAN AUTOMORPHISM ANALYSIS")
    print("=" * 80)

    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())

    print("\ncomputing automorphisms...")

    gm = GraphMatcher(G, G)

    count = 0
    for _ in gm.isomorphisms_iter():
        count += 1

    print("\nautomorphism group size:", count)

    if count == 1:
        print("graph is asymmetric")
    elif count < 10:
        print("very small symmetry group")
    elif count < 100:
        print("moderate symmetry")
    else:
        print("large symmetry group")

    print("\ncomplete")


if __name__ == "__main__":
    main()
