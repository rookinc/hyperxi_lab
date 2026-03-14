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


def canonical_edge(e):
    u, v = e
    return tuple(sorted((u, v)))


def all_faces_of_dodecahedron(D):
    found = set()
    for s in D.nodes():
        stack = [(s, [s])]
        while stack:
            v, path = stack.pop()
            if len(path) == 5:
                if s in D[v]:
                    cyc = path[:]
                    rots = []
                    for k in range(5):
                        rots.append(tuple(cyc[k:] + cyc[:k]))
                    rev = list(reversed(cyc))
                    for k in range(5):
                        rots.append(tuple(rev[k:] + rev[:k]))
                    found.add(min(rots))
                continue
            for w in D[v]:
                if w == s and len(path) < 5:
                    continue
                if w in path:
                    continue
                stack.append((w, path + [w]))
    faces = sorted({cyc for cyc in found if len(cyc) == 5})
    if len(faces) != 12:
        raise RuntimeError(f"Expected 12 faces, got {len(faces)}")
    return faces


def edge_in_face(face, e):
    e = canonical_edge(e)
    for i in range(5):
        a, b = face[i], face[(i + 1) % 5]
        if canonical_edge((a, b)) == e:
            return True
    return False


def dodecahedron_opposite_edge_pairs(D):
    L = nx.line_graph(D)
    dist = dict(nx.all_pairs_shortest_path_length(L))
    diam = nx.diameter(L)
    seen = set()
    pairs = []
    for e in sorted(canonical_edge(x) for x in L.nodes()):
        if e in seen:
            continue
        far = [canonical_edge(f) for f, d in dist[e].items() if d == diam]
        if len(far) != 1:
            raise RuntimeError(f"edge {e} has {len(far)} opposite edges")
        f = far[0]
        pair = tuple(sorted((e, f)))
        seen.add(e)
        seen.add(f)
        pairs.append(pair)
    pairs = sorted(set(pairs))
    if len(pairs) != 15:
        raise RuntimeError(f"Expected 15 opposite-edge classes, got {len(pairs)}")
    return pairs


def build_canonical_g15_from_dodecahedron(D):
    pairs = dodecahedron_opposite_edge_pairs(D)
    L = nx.line_graph(D)
    G15 = nx.Graph()
    G15.add_nodes_from(range(len(pairs)))
    for i, j in itertools.combinations(range(len(pairs)), 2):
        A = pairs[i]
        B = pairs[j]
        edges_between = 0
        for e in A:
            for f in B:
                if L.has_edge(e, f):
                    edges_between += 1
        if edges_between == 2:
            G15.add_edge(i, j)
    return G15, pairs


def relation_signature(e, f, D, faces, opposite_of):
    e = canonical_edge(e)
    f = canonical_edge(f)
    shares_vertex = len(set(e) & set(f)) == 1
    same_face = any(edge_in_face(face, e) and edge_in_face(face, f) for face in faces)
    opposite = opposite_of[e] == f
    local = shares_vertex and same_face
    non_local = (not shares_vertex) and (not same_face) and (not opposite)
    if local:
        return "L"
    if non_local:
        return "N"
    return "O"


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


def main():
    print("=" * 80)
    print("PUSH TRANSPORT SIGN TO PETERSEN")
    print("=" * 80)

    # Recover G30 and G15 from Thalean graph
    G60 = load_thalean_graph()
    a60 = antipode_map(G60)
    G30, _, _ = quotient_by_pairs(G60, a60)

    a30 = antipode_map(G30)
    G15, classes15, _ = quotient_by_pairs(G30, a30)

    # Canonical dodecahedral labeling of G15 vertices
    D = nx.dodecahedral_graph()
    faces = all_faces_of_dodecahedron(D)
    G15_can, opposite_pairs = build_canonical_g15_from_dodecahedron(D)

    gm15_can = nx.algorithms.isomorphism.GraphMatcher(G15, G15_can)
    phi15_can = next(gm15_can.isomorphisms_iter())

    edge_label_of_30 = {}
    for i, pair30 in enumerate(classes15):
        pair_edges = opposite_pairs[phi15_can[i]]
        edge_label_of_30[pair30[0]] = pair_edges[0]
        edge_label_of_30[pair30[1]] = pair_edges[1]

    opposite_of = {}
    for e, f in opposite_pairs:
        opposite_of[e] = f
        opposite_of[f] = e

    # Build the actual transport sign on E(G15) from LL/NN in G30
    sign = {}
    for x, y in G15.edges():
        A = classes15[x]
        B = classes15[y]
        labels = []
        for a in A:
            for b in B:
                if G30.has_edge(a, b):
                    ea = edge_label_of_30[a]
                    eb = edge_label_of_30[b]
                    labels.append(relation_signature(ea, eb, D, faces, opposite_of))
        patt = tuple(sorted(labels))
        if patt == ("L", "L"):
            sign[tuple(sorted((x, y)))] = 0
        elif patt == ("N", "N"):
            sign[tuple(sorted((x, y)))] = 1
        else:
            raise RuntimeError(f"Unexpected pattern {patt} on edge {(x,y)}")

    print("transport sign histogram on G15:", Counter(sign.values()))

    # Extract pentagons and split by transport parity
    pentagons = simple_cycles_length_k(G15, 5)
    odd = []
    even = []

    for cyc in pentagons:
        parity = 0
        edge_signs = []
        for i in range(5):
            e = tuple(sorted((cyc[i], cyc[(i + 1) % 5])))
            parity ^= sign[e]
            edge_signs.append((e, sign[e]))
        if parity == 1:
            odd.append((cyc, edge_signs))
        else:
            even.append((cyc, edge_signs))

    print("pentagons total:", len(pentagons))
    print("odd pentagons  :", len(odd))
    print("even pentagons :", len(even))

    # Identify G15 with L(Petersen)
    P = nx.petersen_graph()
    LP = nx.line_graph(P)
    gm_lp = nx.algorithms.isomorphism.GraphMatcher(G15, LP)
    iso = gm_lp.is_isomorphic()
    print("G15 ≅ L(Petersen):", iso)
    if not iso:
        raise RuntimeError("G15 does not match line graph of Petersen.")
    phi_lp = next(gm_lp.isomorphisms_iter())  # G15 vertex -> LP vertex = edge of Petersen

    print()
    print("ODD PENTAGONS PUSHED TO PETERSEN")
    print("-" * 80)
    odd_type_hist = Counter()
    for cyc, edge_signs in odd:
        p_edges = [tuple(sorted(phi_lp[v])) for v in cyc]
        sub = nx.Graph()
        sub.add_edges_from(p_edges)

        is_cycle5 = (
            sub.number_of_nodes() == 5 and
            sub.number_of_edges() == 5 and
            sorted(dict(sub.degree()).values()) == [2, 2, 2, 2, 2]
        )
        kind = "5-cycle-in-Petersen" if is_cycle5 else "other"
        odd_type_hist[kind] += 1
        print(f"G15 cycle {cyc}")
        print(f"  edge signs: {edge_signs}")
        print(f"  Petersen edges: {p_edges}")
        print(f"  induced type: {kind}")

    print()
    print("EVEN PENTAGONS PUSHED TO PETERSEN")
    print("-" * 80)
    even_type_hist = Counter()
    for cyc, edge_signs in even:
        p_edges = [tuple(sorted(phi_lp[v])) for v in cyc]
        sub = nx.Graph()
        sub.add_edges_from(p_edges)

        is_cycle5 = (
            sub.number_of_nodes() == 5 and
            sub.number_of_edges() == 5 and
            sorted(dict(sub.degree()).values()) == [2, 2, 2, 2, 2]
        )
        kind = "5-cycle-in-Petersen" if is_cycle5 else "other"
        even_type_hist[kind] += 1
        print(f"G15 cycle {cyc}")
        print(f"  edge signs: {edge_signs}")
        print(f"  Petersen edges: {p_edges}")
        print(f"  induced type: {kind}")

    print()
    print("TYPE HISTOGRAMS")
    print("-" * 80)
    print("odd pentagons :", dict(odd_type_hist))
    print("even pentagons:", dict(even_type_hist))

    print()
    print("INTERPRETATION")
    print("-" * 80)
    print("This probe uses the actual transport sign from G30 -> G15.")
    print("If both odd and even pentagons push to 5-cycles in Petersen, then the")
    print("transport sign does not create the pentagons; it polarizes the canonical")
    print("Petersen pentagon system into two parity classes (6 odd, 6 even).")


if __name__ == "__main__":
    main()
