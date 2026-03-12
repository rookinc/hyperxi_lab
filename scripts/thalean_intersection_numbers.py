#!/usr/bin/env python3

from pathlib import Path
from collections import defaultdict, Counter
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
G6_PATH = ROOT / "artifacts/census/thalion_graph.g6"


def load_graph():
    g6 = G6_PATH.read_text(encoding="utf-8").strip()
    G = nx.from_graph6_bytes(g6.encode())
    return nx.convert_node_labels_to_integers(G)


def shell_partition(G, root):
    dist = nx.single_source_shortest_path_length(G, root)
    shells = defaultdict(list)
    for v, d in dist.items():
        shells[d].append(v)
    return dist, dict(shells)


def local_intersection_signature(G, dist, v):
    i = dist[v]
    c = a = b = 0
    for u in G.neighbors(v):
        j = dist[u]
        if j == i - 1:
            c += 1
        elif j == i:
            a += 1
        elif j == i + 1:
            b += 1
    return (c, a, b)


def main():
    G = load_graph()

    print("=" * 80)
    print("THALEAN INTERSECTION NUMBER ANALYSIS")
    print("=" * 80)
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted(set(dict(G.degree()).values())))
    print()

    # because the graph is vertex-transitive, root 0 is enough
    root = 0
    dist, shells = shell_partition(G, root)
    diameter = max(shells)

    print("root:", root)
    print("diameter:", diameter)
    print("shell sizes:", [len(shells[i]) for i in range(diameter + 1)])
    print()

    print("INTERSECTION SIGNATURES BY DISTANCE")
    print("-" * 80)

    split_detected = False

    for i in range(diameter + 1):
        sigs = Counter()
        for v in shells[i]:
            sigs[local_intersection_signature(G, dist, v)] += 1

        print(f"distance {i}:")
        for sig, mult in sorted(sigs.items()):
            c, a, b = sig
            print(f"  (c,a,b)=({c},{a},{b})  count={mult}")
        print()

        if len(sigs) > 1:
            split_detected = True

    print("INTERPRETATION")
    print("-" * 80)
    if not split_detected:
        print("The graph is distance-regular with respect to the chosen root.")
    else:
        print("The graph is not fully distance-regular.")
        print("Some distance shells split into multiple intersection signatures.")

    print()
    print("CANONICAL DISTANCE-REGULAR PREFIX")
    print("-" * 80)

    for i in range(diameter + 1):
        sigs = {
            local_intersection_signature(G, dist, v)
            for v in shells[i]
        }
        if len(sigs) == 1:
            c, a, b = next(iter(sigs))
            print(f"distance {i}: unique (c,a,b)=({c},{a},{b})")
        else:
            print(f"distance {i}: split into {len(sigs)} signatures")
            break


if __name__ == "__main__":
    main()
