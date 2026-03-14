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
            raise RuntimeError(
                f"vertex {v} has {len(far)} distance-{diam} partners"
            )
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
    print("PROBE: THALEAN GRAPH AS 4-LIFT OF 15-VERTEX CORE")
    print("=" * 80)

    G60 = load_thalean_graph()

    a60 = antipode_map(G60)
    G30, classes30, cls30 = quotient_by_pairs(G60, a60)

    a30 = antipode_map(G30)
    G15, classes15, cls15 = quotient_by_pairs(G30, a30)

    # Map each 60-vertex directly to a 15-vertex fiber
    cls15_of_60 = {}
    for v60 in G60.nodes():
        v30 = cls30[v60]
        v15 = cls15[v30]
        cls15_of_60[v60] = v15

    print("GRAPH SIZES")
    print("-" * 80)
    print("60-layer:", G60.number_of_nodes(), "vertices,", G60.number_of_edges(), "edges")
    print("30-layer:", G30.number_of_nodes(), "vertices,", G30.number_of_edges(), "edges")
    print("15-layer:", G15.number_of_nodes(), "vertices,", G15.number_of_edges(), "edges")

    print()
    print("FIBER SIZES OVER 15-LAYER")
    print("-" * 80)
    fiber_sizes = Counter(cls15_of_60.values())
    print("fiber size histogram:", Counter(fiber_sizes.values()))
    for i in range(len(classes15)):
        members = sorted(v for v, c in cls15_of_60.items() if c == i)
        print(f"{i:2d} : size={len(members)} members={members}")

    print()
    print("EDGE COUNTS BETWEEN 15-FIBERS")
    print("-" * 80)
    fiber_edge_counts = defaultdict(int)
    intra_fiber_edges = 0

    for u, v in G60.edges():
        cu = cls15_of_60[u]
        cv = cls15_of_60[v]
        if cu == cv:
            intra_fiber_edges += 1
        else:
            key = tuple(sorted((cu, cv)))
            fiber_edge_counts[key] += 1

    print("intra-fiber edges:", intra_fiber_edges)

    print()
    print("FIRST 30 INTER-FIBER EDGE MULTIPLICITIES")
    print("-" * 80)
    for i, (pair, mult) in enumerate(sorted(fiber_edge_counts.items())[:30], start=1):
        print(f"{pair} -> {mult}")

    print()
    print("UNIFORMITY CHECK OVER 15-GRAPH EDGES")
    print("-" * 80)

    missing = []
    extra = []
    multiplicities = []

    for u, v in G15.edges():
        key = tuple(sorted((u, v)))
        mult = fiber_edge_counts.get(key, 0)
        multiplicities.append(mult)
        if mult == 0:
            missing.append(key)

    for key in fiber_edge_counts:
        if not G15.has_edge(*key):
            extra.append(key)

    print("edge multiplicity histogram:", Counter(multiplicities))
    print("missing base edges in lift:", len(missing))
    if missing:
        print("sample missing:", missing[:10])
    print("extra inter-fiber adjacencies not in 15-core:", len(extra))
    if extra:
        print("sample extra:", extra[:10])

    print()
    print("LOCAL FIBER-DEGREE CHECK")
    print("-" * 80)

    # For each vertex in 60-layer, count how many neighbors land in each 15-fiber
    patterns = Counter()
    sample = {}

    for v in sorted(G60.nodes()):
        counts = Counter(cls15_of_60[n] for n in G60.neighbors(v))
        sig = tuple(sorted(counts.values()))
        patterns[sig] += 1
        sample.setdefault(sig, v)

    print("neighbor-to-fiber pattern histogram:")
    for sig, count in sorted(patterns.items()):
        print(f"  {sig} : {count} vertices (sample {sample[sig]})")

    print()
    print("INTERPRETATION")
    print("-" * 80)
    if len(set(fiber_sizes.values())) == 1:
        print("All 15-core fibers have the same size.")
    else:
        print("Fiber sizes are not uniform.")

    if intra_fiber_edges == 0:
        print("No edges lie entirely within a 15-core fiber.")
    else:
        print("There are intra-fiber edges, so this is not a simple covering in the strictest sense.")

    if len(set(multiplicities)) == 1 and not extra and not missing:
        print("Each base edge lifts with uniform multiplicity; strong evidence for a regular lift.")
    else:
        print("Lift multiplicities vary or extra structure is present; likely a structured but nontrivial lift.")


if __name__ == "__main__":
    main()
