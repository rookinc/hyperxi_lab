#!/usr/bin/env python3

from collections import Counter, defaultdict
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


def main():
    print("=" * 80)
    print("PROBE 15-CORE AS OPPOSITE-EDGE PAIRS")
    print("=" * 80)

    G60 = load_thalean_graph()

    # 60 -> 30
    a60 = antipode_map(G60)
    G30, classes30, cls30 = quotient_by_pairs(G60, a60)

    # 30 -> 15
    a30 = antipode_map(G30)
    G15, classes15, cls15 = quotient_by_pairs(G30, a30)

    print("GRAPH SIZES")
    print("-" * 80)
    print("G60:", G60.number_of_nodes(), G60.number_of_edges())
    print("G30:", G30.number_of_nodes(), G30.number_of_edges())
    print("G15:", G15.number_of_nodes(), G15.number_of_edges())

    print()
    print("30-LAYER VERTICES AS PAIRS OF 60-VERTICES")
    print("-" * 80)
    for i, pair in enumerate(classes30[:30]):
        print(f"{i:2d} -> {pair}")

    print()
    print("15-LAYER VERTICES AS PAIRS OF 30-LAYER VERTICES")
    print("-" * 80)
    for i, pair in enumerate(classes15):
        print(f"{i:2d} -> {pair}")

    print()
    print("15-LAYER VERTICES EXPANDED BACK TO 60-LAYER")
    print("-" * 80)
    for i, (u30, v30) in enumerate(classes15):
        members = sorted(classes30[u30] + classes30[v30])
        print(f"{i:2d} -> 30-pair={classes15[i]} -> 60-members={members}")

    print()
    print("15-CORE ADJACENCY")
    print("-" * 80)
    for i in range(15):
        neigh = sorted(G15.neighbors(i))
        print(f"{i:2d} -> {neigh}")

    print()
    print("ADJACENCY RULE COUNTS BETWEEN 30-PAIRS")
    print("-" * 80)

    # For each edge in G15, count how many edges exist between the two underlying 30-pairs
    mult_hist = Counter()
    detailed = []

    for x, y in sorted(G15.edges()):
        A = classes15[x]
        B = classes15[y]

        edges_between = 0
        pairs = []
        for a in A:
            for b in B:
                if G30.has_edge(a, b):
                    edges_between += 1
                    pairs.append((a, b))

        mult_hist[edges_between] += 1
        detailed.append((x, y, A, B, edges_between, pairs))

    print("histogram of edge-counts between paired 30-classes:", dict(sorted(mult_hist.items())))

    print()
    print("FIRST 20 DETAILED 15-CORE EDGE EXPANSIONS")
    print("-" * 80)
    for row in detailed[:20]:
        x, y, A, B, m, pairs = row
        print(f"{x:2d}-{y:2d}: {A} <-> {B} | edges_between={m} | {pairs}")

    print()
    print("NONEDGES IN 15-CORE: EDGE COUNTS BETWEEN UNDERLYING 30-PAIRS")
    print("-" * 80)
    non_mult_hist = Counter()
    shown = 0
    for x in range(15):
        for y in range(x + 1, 15):
            if G15.has_edge(x, y):
                continue
            A = classes15[x]
            B = classes15[y]
            edges_between = 0
            for a in A:
                for b in B:
                    if G30.has_edge(a, b):
                        edges_between += 1
            non_mult_hist[edges_between] += 1
            if shown < 20:
                print(f"{x:2d}-{y:2d}: {A} <-> {B} | edges_between={edges_between}")
                shown += 1

    print("histogram for nonedges:", dict(sorted(non_mult_hist.items())))

    print()
    print("INTERPRETATION")
    print("-" * 80)
    print("If every 15-core edge corresponds to a uniform relation between the")
    print("two underlying 30-layer antipodal pairs, then the 15-core is likely")
    print("the graph of opposite-edge classes under a simple compatibility rule.")


if __name__ == "__main__":
    main()
