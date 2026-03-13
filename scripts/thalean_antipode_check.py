#!/usr/bin/env python3

from pathlib import Path
from collections import Counter
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
G6_PATH = ROOT / "artifacts/census/thalion_graph.g6"


def load_graph():
    g6 = G6_PATH.read_text(encoding="utf-8").strip()
    G = nx.from_graph6_bytes(g6.encode())
    return nx.convert_node_labels_to_integers(G)


def main():
    G = load_graph()

    print("=" * 80)
    print("THALEAN ANTIPODE CHECK")
    print("=" * 80)
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted(set(dict(G.degree()).values())))
    print()

    diameter = nx.diameter(G)
    print("diameter:", diameter)
    print()

    all_pairs = dict(nx.all_pairs_shortest_path_length(G))

    far_counts = {}
    far_partners = {}

    for v in G.nodes():
        far = sorted([u for u, d in all_pairs[v].items() if d == diameter])
        far_counts[v] = len(far)
        far_partners[v] = far

    hist = Counter(far_counts.values())

    print("DISTANCE-6 PARTNER COUNT HISTOGRAM")
    print("-" * 80)
    for k in sorted(hist):
        print(f"{k} far partners: {hist[k]} vertices")
    print()

    unique_antipode = all(c == 1 for c in far_counts.values())
    print("every vertex has a unique distance-6 partner:", unique_antipode)
    print()

    print("FIRST 20 VERTEX -> FAR PARTNER LISTS")
    print("-" * 80)
    for v in sorted(G.nodes())[:20]:
        print(f"{v:2d} -> {far_partners[v]}")
    print()

    # If unique, check involution property
    if unique_antipode:
        antipode_map = {v: far_partners[v][0] for v in G.nodes()}
        involution_ok = all(antipode_map[antipode_map[v]] == v for v in G.nodes())
        fixed_points = [v for v in G.nodes() if antipode_map[v] == v]

        print("UNIQUE ANTIPODE MAP")
        print("-" * 80)
        print("involution property a(a(v)) = v:", involution_ok)
        print("fixed points:", fixed_points)
        print()

        pair_set = set()
        for v, u in antipode_map.items():
            pair_set.add(tuple(sorted((v, u))))

        print("number of antipodal pairs:", len(pair_set))
        print("first 20 antipodal pairs:")
        for p in sorted(pair_set)[:20]:
            print(" ", p)
        print()

        # Quotient by antipodal pairs
        Q = nx.Graph()
        pair_index = {p: i for i, p in enumerate(sorted(pair_set))}
        vertex_to_class = {}
        for p, i in pair_index.items():
            a, b = p
            vertex_to_class[a] = i
            vertex_to_class[b] = i
            Q.add_node(i)

        for x, y in G.edges():
            cx = vertex_to_class[x]
            cy = vertex_to_class[y]
            if cx != cy:
                Q.add_edge(cx, cy)

        print("QUOTIENT BY ANTIPODAL PAIRS")
        print("-" * 80)
        print("classes:", Q.number_of_nodes())
        print("edges:", Q.number_of_edges())
        print("degree set:", sorted(set(dict(Q.degree()).values())))
        print("connected:", nx.is_connected(Q))
        if nx.is_connected(Q):
            print("diameter:", nx.diameter(Q))
        print()
    else:
        print("No unique antipodal partner map; strict antipodal-pair quotient not formed.")
        print()

    print("INTERPRETATION")
    print("-" * 80)
    if unique_antipode:
        print("The distance-6 relation defines a unique antipode for every vertex.")
        print("This supports an antipodal-style interpretation of the graph.")
    else:
        print("Vertices do not have unique distance-6 partners.")
        print("The graph may still show antipodal-style focusing without being")
        print("strictly antipodal in the pair-partition sense.")


if __name__ == "__main__":
    main()
