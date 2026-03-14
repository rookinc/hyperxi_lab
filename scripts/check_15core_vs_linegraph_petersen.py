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
        if len(far) != 1:
            raise RuntimeError("unexpected antipode structure")
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

    return Q


def main():

    print("="*80)
    print("CHECK 15-CORE VS LINE GRAPH OF PETERSEN")
    print("="*80)

    G60 = load_thalean_graph()

    a60 = antipode_map(G60)
    G30 = quotient_by_pairs(G60, a60)

    a30 = antipode_map(G30)
    G15 = quotient_by_pairs(G30, a30)

    print("RECOVERED 15-CORE")
    print("-"*80)
    print("vertices:", G15.number_of_nodes())
    print("edges:", G15.number_of_edges())
    print("degree set:", sorted(set(dict(G15.degree()).values())))
    print()

    P = nx.petersen_graph()
    LP = nx.line_graph(P)

    print("LINE GRAPH OF PETERSEN")
    print("-"*80)
    print("vertices:", LP.number_of_nodes())
    print("edges:", LP.number_of_edges())
    print("degree set:", sorted(set(dict(LP.degree()).values())))
    print()

    gm = nx.algorithms.isomorphism.GraphMatcher(G15, LP)
    iso = gm.is_isomorphic()

    print("ISOMORPHISM TEST")
    print("-"*80)
    print("G15 ≅ L(Petersen):", iso)


if __name__ == "__main__":
    main()
