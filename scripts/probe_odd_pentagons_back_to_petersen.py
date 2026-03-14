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
        cu, cv = cls_of[u], cls_of[v]
        if cu != cv:
            Q.add_edge(cu, cv)
    return Q, classes, cls_of


def simple_cycles_length_k(G, k):
    DG = nx.DiGraph()
    DG.add_edges_from((u, v) for u, v in G.edges())
    DG.add_edges_from((v, u) for u, v in G.edges())
    out = set()
    for cyc in nx.simple_cycles(DG):
        if len(cyc) != k:
            continue
        rots = []
        for i in range(k):
            rots.append(tuple(cyc[i:] + cyc[:i]))
        rev = list(reversed(cyc))
        for i in range(k):
            rots.append(tuple(rev[i:] + rev[:i]))
        out.add(min(rots))
    return sorted(out)


def build_sign_on_g15(G30, G15, classes15):
    # sign via same pattern we already established:
    # edge in G15 gets sign 0 if the two lifted cross-edges in G30 are "parallel"
    # with respect to the antipodal pairing in classes15, and 1 otherwise.
    #
    # Since each G15 edge lifts to exactly two G30 edges among a 2x2 cross block,
    # pattern is determined combinatorially from indices.
    sign = {}
    for x, y in G15.edges():
        A = classes15[x]
        B = classes15[y]
        cross = []
        for a in A:
            for b in B:
                if G30.has_edge(a, b):
                    cross.append((a, b))

        # normalize to positions 0/1 inside the two fibers
        posA = {A[0]: 0, A[1]: 1}
        posB = {B[0]: 0, B[1]: 1}
        patt = sorted((posA[a], posB[b]) for a, b in cross)

        # parallel matching = [(0,0),(1,1)], crossed = [(0,1),(1,0)]
        if patt == [(0, 0), (1, 1)]:
            sign[tuple(sorted((x, y)))] = 0
        elif patt == [(0, 1), (1, 0)]:
            sign[tuple(sorted((x, y)))] = 1
        else:
            raise RuntimeError(f"Unexpected lift pattern {patt} on {(x,y)}")
    return sign


def main():
    print("=" * 80)
    print("PROBE ODD PENTAGONS BACK TO PETERSEN")
    print("=" * 80)

    # recover G15
    G60 = load_thalean_graph()
    a60 = antipode_map(G60)
    G30, _, _ = quotient_by_pairs(G60, a60)
    a30 = antipode_map(G30)
    G15, classes15, _ = quotient_by_pairs(G30, a30)

    # build odd pentagons in G15
    sign = build_sign_on_g15(G30, G15, classes15)
    pentagons = simple_cycles_length_k(G15, 5)

    odd_pents = []
    for cyc in pentagons:
        parity = 0
        for i in range(5):
            e = tuple(sorted((cyc[i], cyc[(i + 1) % 5])))
            parity ^= sign[e]
        if parity == 1:
            odd_pents.append(cyc)

    print("odd pentagons in G15:", len(odd_pents))

    # identify G15 with L(Petersen)
    P = nx.petersen_graph()
    LP = nx.line_graph(P)
    gm = nx.algorithms.isomorphism.GraphMatcher(G15, LP)
    iso = gm.is_isomorphic()
    print("G15 ≅ L(Petersen):", iso)
    if not iso:
        raise RuntimeError("G15 is not matching line graph of Petersen here.")
    phi = next(gm.isomorphisms_iter())  # maps G15 vertices -> LP vertices = P edges

    print()
    print("ODD PENTAGONS AS 5-EDGE SETS IN PETERSEN")
    print("-" * 80)

    type_hist = Counter()

    for cyc in odd_pents:
        edge_set = [tuple(sorted(phi[v])) for v in cyc]  # edges of Petersen
        sub = nx.Graph()
        sub.add_edges_from(edge_set)

        degs = sorted(dict(sub.degree()).values())
        comp_sizes = sorted(len(c) for c in nx.connected_components(sub))
        is_cycle5 = (
            sub.number_of_nodes() == 5 and
            sub.number_of_edges() == 5 and
            sorted(dict(sub.degree()).values()) == [2,2,2,2,2]
        )

        kind = None
        if is_cycle5:
            kind = "5-cycle-in-Petersen"
        else:
            kind = f"nodes={sub.number_of_nodes()},degs={degs},comps={comp_sizes}"

        type_hist[kind] += 1
        print(f"G15 cycle {cyc}")
        print(f"  Petersen edges: {edge_set}")
        print(f"  induced type: {kind}")

    print()
    print("TYPE HISTOGRAM")
    print("-" * 80)
    print(dict(type_hist))

    print()
    print("INTERPRETATION")
    print("-" * 80)
    print("If all six odd pentagons map to canonical 5-cycles in the Petersen graph,")
    print("then the 'rotation loops' are directly inherited from the Petersen pentagon")
    print("structure, explaining why Petersen appears at the core.")


if __name__ == "__main__":
    main()
