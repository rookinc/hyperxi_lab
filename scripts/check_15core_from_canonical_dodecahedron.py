#!/usr/bin/env python3

from collections import Counter
import itertools
import networkx as nx


TARGET_G6 = "Nto`GCJAIAAHPA@CaAg"


def canonicalize_edge(e):
    u, v = e
    return tuple(sorted((u, v)))


def dodecahedron_opposite_edge_pairs(D):
    """
    In a dodecahedron, each edge has a unique opposite edge at maximum
    distance in the line graph.
    Return the 15 opposite-edge classes.
    """
    L = nx.line_graph(D)
    dist = dict(nx.all_pairs_shortest_path_length(L))
    diam = nx.diameter(L)

    edges = sorted(L.nodes())
    seen = set()
    pairs = []

    for e in edges:
        if e in seen:
            continue
        far = [f for f, d in dist[e].items() if d == diam]
        if len(far) != 1:
            raise RuntimeError(f"edge {e} has {len(far)} opposite edges in line graph")
        f = far[0]
        pair = tuple(sorted((canonicalize_edge(e), canonicalize_edge(f))))
        seen.add(e)
        seen.add(f)
        pairs.append(pair)

    pairs = sorted(set(pairs))
    if len(pairs) != 15:
        raise RuntimeError(f"Expected 15 opposite-edge classes, got {len(pairs)}")

    return pairs, L


def build_15core_from_dodecahedron(D):
    """
    Build 15-core directly from dodecahedron edges:
    - vertices = opposite-edge classes
    - adjacency iff exactly two cross-adjacencies exist in line_graph(D)
    """
    pairs, L = dodecahedron_opposite_edge_pairs(D)

    G15 = nx.Graph()
    G15.add_nodes_from(range(len(pairs)))

    for i, j in itertools.combinations(range(len(pairs)), 2):
        A = pairs[i]
        B = pairs[j]

        edges_between = 0
        witnesses = []
        for e in A:
            for f in B:
                if L.has_edge(e, f):
                    edges_between += 1
                    witnesses.append((e, f))

        if edges_between == 2:
            G15.add_edge(i, j)

    return G15, pairs


def shell_counts(G, root=0):
    d = nx.single_source_shortest_path_length(G, root)
    c = Counter(d.values())
    return tuple(c[i] for i in range(max(c) + 1))


def triangle_count(G):
    return sum(nx.triangles(G).values()) // 3


def main():
    print("=" * 80)
    print("CHECK 15-CORE FROM CANONICAL DODECAHEDRON")
    print("=" * 80)

    D = nx.dodecahedral_graph()
    G15_direct, pairs = build_15core_from_dodecahedron(D)
    G15_target = nx.from_graph6_bytes(TARGET_G6.encode())

    print("DIRECT GRAPH SUMMARY")
    print("-" * 80)
    print("vertices:", G15_direct.number_of_nodes())
    print("edges:", G15_direct.number_of_edges())
    print("degree set:", sorted(set(dict(G15_direct.degree()).values())))
    print("connected:", nx.is_connected(G15_direct))
    print("diameter:", nx.diameter(G15_direct))
    print("triangles:", triangle_count(G15_direct))
    print("shell counts from 0:", shell_counts(G15_direct, 0))

    print()
    print("TARGET GRAPH SUMMARY")
    print("-" * 80)
    print("vertices:", G15_target.number_of_nodes())
    print("edges:", G15_target.number_of_edges())
    print("degree set:", sorted(set(dict(G15_target.degree()).values())))
    print("connected:", nx.is_connected(G15_target))
    print("diameter:", nx.diameter(G15_target))
    print("triangles:", triangle_count(G15_target))
    print("shell counts from 0:", shell_counts(G15_target, 0))

    print()
    print("ISOMORPHISM TEST")
    print("-" * 80)
    iso = nx.is_isomorphic(G15_direct, G15_target)
    print("direct-from-dodecahedron ≅ recovered 15-core:", iso)

    print()
    print("FIRST 15 OPPOSITE-EDGE CLASSES")
    print("-" * 80)
    for i, pair in enumerate(pairs):
        print(f"{i:2d} -> {pair}")

    print()
    print("GRAPH6")
    print("-" * 80)
    print("direct :", nx.to_graph6_bytes(G15_direct, header=False).decode().strip())
    print("target :", TARGET_G6)

    print()
    print("INTERPRETATION")
    print("-" * 80)
    if iso:
        print("The recovered 15-core is exactly the compatibility graph on")
        print("opposite-edge classes of the canonical dodecahedron.")
        print("This identifies the 15-core as a native polyhedral object.")
    else:
        print("The recovered 15-core does not match this canonical construction.")
        print("The 30-layer transport graph is therefore a Petrie-twisted edge system,")
        print("not the ordinary dodecahedral edge graph.")


if __name__ == "__main__":
    main()
