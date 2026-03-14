#!/usr/bin/env python3

from collections import Counter
import itertools
import networkx as nx

from load_thalean_graph import load_spec, build_graph


def load_thalean_graph():
    return build_graph(load_spec())


def antipode_map(G):
    dist = dict(nx.all_pairs_shortest_path_length(G))
    diam = nx.diameter(G)
    a = {}
    for v in G.nodes():
        far = [u for u, d in dist[v].items() if d == diam]
        if len(far) != 1:
            raise RuntimeError(f"vertex {v} has {len(far)} distance-{diam} partners")
        a[v] = far[0]
    return a


def quotient_by_pairs(G, pair_map):
    seen = set()
    classes = []
    cls_of = {}

    for v in sorted(G.nodes()):
        if v in seen:
            continue
        pair = tuple(sorted((v, pair_map[v])))
        seen.update(pair)
        idx = len(classes)
        classes.append(pair)
        for x in pair:
            cls_of[x] = idx

    Q = nx.Graph()
    Q.add_nodes_from(range(len(classes)))

    for u, v in G.edges():
        cu, cv = cls_of[u], cls_of[v]
        if cu != cv:
            Q.add_edge(cu, cv)

    return Q, classes, cls_of


def shell_counts(G, root=0):
    d = nx.single_source_shortest_path_length(G, root)
    c = Counter(d.values())
    return tuple(c[i] for i in range(max(c) + 1))


def triangle_count(G):
    return sum(nx.triangles(G).values()) // 3


def build_direct_15_from_30(G30):
    """
    Build 15-core directly from the 30-layer by:
      1. pairing each 30-vertex with its antipode in G30
      2. making one 15-vertex for each antipodal pair
      3. connecting two 15-vertices iff there are exactly two edges
         between the underlying 30-pairs
    """
    a30 = antipode_map(G30)

    seen = set()
    classes15 = []
    for v in sorted(G30.nodes()):
        if v in seen:
            continue
        pair = tuple(sorted((v, a30[v])))
        seen.update(pair)
        classes15.append(pair)

    G15_direct = nx.Graph()
    G15_direct.add_nodes_from(range(len(classes15)))

    for i, j in itertools.combinations(range(len(classes15)), 2):
        A = classes15[i]
        B = classes15[j]

        edges_between = 0
        for x in A:
            for y in B:
                if G30.has_edge(x, y):
                    edges_between += 1

        if edges_between == 2:
            G15_direct.add_edge(i, j)

    return G15_direct, classes15


def main():
    print("=" * 80)
    print("RECOVER 15-CORE DIRECTLY FROM DODECAHEDRON EDGE SYSTEM")
    print("=" * 80)

    # Start from Thalean graph only to recover the canonical 30-layer
    # (which we already identified as the edge-resolution layer).
    G60 = load_thalean_graph()
    a60 = antipode_map(G60)
    G30, classes30, _ = quotient_by_pairs(G60, a60)

    # Canonical 15-layer from second quotient
    a30 = antipode_map(G30)
    G15_quotient, classes15_quotient, _ = quotient_by_pairs(G30, a30)

    # Direct reconstruction from 30-layer compatibility rule
    G15_direct, classes15_direct = build_direct_15_from_30(G30)

    print("30-LAYER SUMMARY")
    print("-" * 80)
    print("vertices:", G30.number_of_nodes())
    print("edges:", G30.number_of_edges())
    print("degree set:", sorted(set(dict(G30.degree()).values())))

    print()
    print("DIRECT 15-CORE SUMMARY")
    print("-" * 80)
    print("vertices:", G15_direct.number_of_nodes())
    print("edges:", G15_direct.number_of_edges())
    print("degree set:", sorted(set(dict(G15_direct.degree()).values())))
    print("connected:", nx.is_connected(G15_direct))
    print("diameter:", nx.diameter(G15_direct))
    print("triangles:", triangle_count(G15_direct))
    print("shell counts from 0:", shell_counts(G15_direct, 0))

    print()
    print("QUOTIENT 15-CORE SUMMARY")
    print("-" * 80)
    print("vertices:", G15_quotient.number_of_nodes())
    print("edges:", G15_quotient.number_of_edges())
    print("degree set:", sorted(set(dict(G15_quotient.degree()).values())))
    print("connected:", nx.is_connected(G15_quotient))
    print("diameter:", nx.diameter(G15_quotient))
    print("triangles:", triangle_count(G15_quotient))
    print("shell counts from 0:", shell_counts(G15_quotient, 0))

    print()
    print("ISOMORPHISM TEST")
    print("-" * 80)
    iso = nx.is_isomorphic(G15_direct, G15_quotient)
    print("direct reconstruction isomorphic to quotient core:", iso)

    print()
    print("FIRST 15 DIRECT OPPOSITE-EDGE CLASSES")
    print("-" * 80)
    for i, pair in enumerate(classes15_direct):
        print(f"{i:2d} -> {pair}")

    print()
    print("GRAPH6")
    print("-" * 80)
    print("direct  :", nx.to_graph6_bytes(G15_direct, header=False).decode().strip())
    print("quotient:", nx.to_graph6_bytes(G15_quotient, header=False).decode().strip())

    print()
    print("INTERPRETATION")
    print("-" * 80)
    if iso:
        print("The 15-core can be recovered directly from the 30-layer edge system")
        print("using opposite-edge classes and the exact-two-cross-adjacencies rule.")
        print("This strongly supports the interpretation of the 15-core as a native")
        print("geometric compatibility graph of the dodecahedral edge system.")
    else:
        print("The direct reconstruction does not match the quotient core.")
        print("The 15-core may require additional structure beyond opposite-edge pairing.")


if __name__ == "__main__":
    main()
