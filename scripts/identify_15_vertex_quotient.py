#!/usr/bin/env python3

from collections import Counter
from pathlib import Path

import networkx as nx
import numpy as np


G6_PATH = Path("artifacts/census/thalean_second_antipodal_quotient.g6")


def load_graph():
    if not G6_PATH.exists():
        raise FileNotFoundError(f"Missing {G6_PATH}")
    return nx.from_graph6_bytes(G6_PATH.read_text().strip().encode())


def shell_counts(G, root=0):
    d = nx.single_source_shortest_path_length(G, root)
    c = Counter(d.values())
    return tuple(c[i] for i in range(max(c) + 1))


def triangle_count(G):
    return sum(nx.triangles(G).values()) // 3


def spectrum_counts(G):
    vals = np.linalg.eigvals(nx.to_numpy_array(G))
    vals = sorted(round(v.real, 6) for v in vals)
    return Counter(vals)


def summary(name, G):
    print(name)
    print("-" * 72)
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted(set(dict(G.degree()).values())))
    print("connected:", nx.is_connected(G))
    print("diameter:", nx.diameter(G))
    print("triangles:", triangle_count(G))
    print("shell counts from 0:", shell_counts(G, 0))
    print("spectrum:")
    for v, c in sorted(spectrum_counts(G).items()):
        print(f"  {v:10.6f} : {c}")
    print()


def candidate_graphs():
    cands = {}

    # Obvious named small graphs
    cands["triangular_graph(6) / line_graph(K6)"] = nx.line_graph(nx.complete_graph(6))
    cands["complement(triangular_graph(6))"] = nx.complement(cands["triangular_graph(6) / line_graph(K6)"])

    # Generalized Petersen graphs with 15 vertices where possible
    # g(n,k) has 2n vertices, so none are 15; skip

    # Rook graph K3 □ K5 has 15 vertices, degree 6; still useful to rule out
    cands["rook_graph(3,5)"] = nx.cartesian_product(nx.complete_graph(3), nx.complete_graph(5))

    # Complete tripartite K5,5,5 has 15 vertices, degree 10; rule out
    cands["complete_multipartite_graph(5,5,5)"] = nx.complete_multipartite_graph(5, 5, 5)

    # Complement of Petersen is 10 vertices, so omitted

    return cands


def main():
    print("=" * 72)
    print("IDENTIFY 15-VERTEX QUOTIENT")
    print("=" * 72)

    G = load_graph()
    summary("TARGET 15-GRAPH", G)

    print("GRAPH6")
    print("-" * 72)
    print(nx.to_graph6_bytes(G, header=False).decode().strip())
    print()

    print("CANDIDATE COMPARISONS")
    print("-" * 72)
    matched = []

    for name, H in candidate_graphs().items():
        print(f"checking: {name}")
        print(f"  order={H.number_of_nodes()} size={H.number_of_edges()} degree set={sorted(set(dict(H.degree()).values()))}")
        iso = nx.is_isomorphic(G, H) if H.number_of_nodes() == G.number_of_nodes() else False
        print(f"  isomorphic: {iso}")
        if iso:
            matched.append(name)

    print()
    if matched:
        print("MATCHES")
        print("-" * 72)
        for name in matched:
            print(name)
    else:
        print("No matches among built-in candidate graphs.")

if __name__ == "__main__":
    main()
