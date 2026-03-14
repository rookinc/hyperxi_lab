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


def canonical_edge(e):
    u, v = e
    return tuple(sorted((u, v)))


def all_faces_of_dodecahedron(D):
    found = set()
    nodes = list(D.nodes())
    for s in nodes:
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
    edges = sorted(canonical_edge(e) for e in L.nodes())
    seen = set()
    pairs = []
    for e in edges:
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
    return shares_vertex, same_face, opposite


def main():
    print("=" * 80)
    print("FINAL PROBE: 30-LAYER AS SIGNED 2-LIFT OF 15-CORE")
    print("=" * 80)

    G60 = load_thalean_graph()
    a60 = antipode_map(G60)
    G30, _, _ = quotient_by_pairs(G60, a60)

    a30 = antipode_map(G30)
    G15_rec, classes15, cls15 = quotient_by_pairs(G30, a30)

    D = nx.dodecahedral_graph()
    faces = all_faces_of_dodecahedron(D)
    G15_can, opposite_pairs = build_canonical_g15_from_dodecahedron(D)

    gm15 = nx.algorithms.isomorphism.GraphMatcher(G15_rec, G15_can)
    phi15 = next(gm15.isomorphisms_iter())

    edge_label_of_30 = {}
    for i, pair30 in enumerate(classes15):
        pair_edges = opposite_pairs[phi15[i]]
        edge_label_of_30[pair30[0]] = pair_edges[0]
        edge_label_of_30[pair30[1]] = pair_edges[1]

    opposite_of = {}
    for e, f in opposite_pairs:
        opposite_of[e] = f
        opposite_of[f] = e

    pattern_hist = Counter()
    detailed = []

    for x, y in sorted(G15_rec.edges()):
        A = classes15[x]
        B = classes15[y]
        cross = []
        for a in A:
            for b in B:
                if G30.has_edge(a, b):
                    ea = edge_label_of_30[a]
                    eb = edge_label_of_30[b]
                    shares_vertex, same_face, opposite = relation_signature(
                        ea, eb, D, faces, opposite_of
                    )
                    local = shares_vertex and same_face
                    non_local = (not shares_vertex) and (not same_face) and (not opposite)
                    if local:
                        typ = "L"
                    elif non_local:
                        typ = "N"
                    else:
                        typ = "O"
                    cross.append((a, b, ea, eb, typ))
        patt = tuple(sorted(t for _, _, _, _, t in cross))
        pattern_hist[patt] += 1
        if len(detailed) < 40:
            detailed.append((x, y, A, B, cross, patt))

    print("PATTERN HISTOGRAM OVER 15-CORE EDGES")
    print("-" * 80)
    for patt, count in sorted(pattern_hist.items()):
        print(f"{patt}: {count}")

    print()
    print("FIRST 40 LIFTED 15-CORE EDGES")
    print("-" * 80)
    for x, y, A, B, cross, patt in detailed:
        print(f"{x:2d}-{y:2d}: {A} x {B} -> pattern {patt}")
        for row in cross:
            a, b, ea, eb, typ = row
            print(f"   {a:2d}-{b:2d}  {ea} -- {eb}  {typ}")

    print()
    print("INTERPRETATION")
    print("-" * 80)
    if pattern_hist == Counter({('L', 'N'): G15_rec.number_of_edges()}):
        print("Every 15-core edge lifts as exactly one local and one nonlocal 30-edge.")
        print("This is strong evidence that G30 is a signed 2-lift of the 15-core.")
    else:
        print("The lift pattern is not uniformly (L, N).")
        print("G30 is still a 2-lift over the 15-core, but with a more complicated rule.")


if __name__ == "__main__":
    main()
