from __future__ import annotations

from collections import Counter
import numpy as np
import networkx as nx

from chamber_graph_aut_order import load_decagons, build_graph, DECAGON_FILE


def triangle_count(G: nx.Graph) -> int:
    return sum(nx.triangles(G).values()) // 3


def common_neighbor_profiles(G: nx.Graph):
    adj = Counter()
    nonadj = Counter()
    nodes = sorted(G.nodes())
    for i, u in enumerate(nodes):
        Nu = set(G.neighbors(u))
        for v in nodes[i + 1:]:
            c = len(Nu.intersection(G.neighbors(v)))
            if G.has_edge(u, v):
                adj[c] += 1
            else:
                nonadj[c] += 1
    return dict(adj), dict(nonadj)


def rounded_spectrum(G: nx.Graph):
    A = nx.to_numpy_array(G, dtype=float)
    vals = np.linalg.eigvals(A).real
    rounded = [round(float(x), 6) for x in vals]
    return Counter(sorted(rounded))


def shell_histogram(G: nx.Graph):
    out = Counter()
    for s in G.nodes():
        d = nx.single_source_shortest_path_length(G, s)
        shells = []
        for k in range(max(d.values()) + 1):
            shells.append(sum(1 for v in d if d[v] == k))
        out[tuple(shells)] += 1
    return out


def main() -> None:
    decagons = load_decagons(DECAGON_FILE)
    G = build_graph(decagons)

    print("=" * 80)
    print("THALION GRAPH FINGERPRINT")
    print("=" * 80)
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted(set(dict(G.degree()).values())))
    print("triangles:", triangle_count(G))

    adj, nonadj = common_neighbor_profiles(G)
    print("adjacent common-neighbor profile:", adj)
    print("nonadjacent common-neighbor profile:", nonadj)

    print("shell histogram:")
    for k, v in sorted(shell_histogram(G).items()):
        print(f"  {k}: {v}")

    print("spectrum:")
    spec = rounded_spectrum(G)
    for ev, mult in sorted(spec.items()):
        print(f"  {ev}: {mult}")


if __name__ == "__main__":
    main()
