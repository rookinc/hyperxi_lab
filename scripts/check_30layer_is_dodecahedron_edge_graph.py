#!/usr/bin/env python3

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

        cu = cls_of[u]
        cv = cls_of[v]

        if cu != cv:
            Q.add_edge(cu, cv)

    return Q, classes


def main():

    print("=" * 80)
    print("CHECK 30-LAYER = EDGE GRAPH OF DODECAHEDRON")
    print("=" * 80)

    G60 = load_thalean_graph()

    a60 = antipode_map(G60)

    G30, classes = quotient_by_pairs(G60, a60)

    print("30-LAYER SUMMARY")
    print("-" * 80)

    print("vertices:", G30.number_of_nodes())
    print("edges:", G30.number_of_edges())
    print("degree set:", sorted(set(dict(G30.degree()).values())))

    print()

    # canonical dodecahedron
    D = nx.dodecahedral_graph()

    L = nx.line_graph(D)

    print("DODECAHEDRON EDGE GRAPH")
    print("-" * 80)

    print("vertices:", L.number_of_nodes())
    print("edges:", L.number_of_edges())
    print("degree set:", sorted(set(dict(L.degree()).values())))

    print()

    iso = nx.is_isomorphic(G30, L)

    print("ISOMORPHISM TEST")
    print("-" * 80)
    print("G30 ≅ line_graph(dodecahedron) :", iso)

    print()

    if iso:
        print("INTERPRETATION")
        print("-" * 80)
        print("The 30-layer is exactly the edge graph of the dodecahedron.")
        print("Thus the reduction ladder becomes:")
        print()
        print("60 : chamber states")
        print("30 : edges of dodecahedron")
        print("15 : opposite-edge compatibility graph")
    else:
        print("The 30-layer is not the dodecahedron edge graph.")


if __name__ == "__main__":
    main()
