#!/usr/bin/env python3

from collections import Counter, defaultdict
import itertools
import networkx as nx

from load_thalean_graph import load_spec, build_graph


TARGET_G15_G6 = "Nto`GCJAIAAHPA@CaAg"


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
    faces = set()
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
                    n = 5
                    for k in range(n):
                        rots.append(tuple(cyc[k:] + cyc[:k]))
                    rev = list(reversed(cyc))
                    for k in range(n):
                        rots.append(tuple(rev[k:] + rev[:k]))
                    found.add(min(rots))
                continue
            for w in D[v]:
                if w == s and len(path) < 5:
                    continue
                if w in path:
                    continue
                stack.append((w, path + [w]))
    faces = {cyc for cyc in found if len(cyc) == 5}
    if len(faces) != 12:
        raise RuntimeError(f"Expected 12 faces, got {len(faces)}")
    return sorted(faces)


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


def naive_petrie_edge_graph(D, faces):
    edges = sorted(canonical_edge(e) for e in D.edges())
    Gp = nx.Graph()
    Gp.add_nodes_from(edges)

    # two edges are adjacent if they are nonadjacent edges in a common face
    # (the simple Petrie-step surrogate tested earlier)
    for face in faces:
        face_edges = [canonical_edge((face[i], face[(i + 1) % 5])) for i in range(5)]
        for i, e in enumerate(face_edges):
            for j in ((i + 2) % 5, (i + 3) % 5):
                Gp.add_edge(e, face_edges[j])

    return Gp


def relation_signature(e, f, D, faces, opposite_of, Gp):
    e = canonical_edge(e)
    f = canonical_edge(f)

    shares_vertex = len(set(e) & set(f)) == 1
    same_face = any(edge_in_face(face, e) and edge_in_face(face, f) for face in faces)
    opposite = opposite_of[e] == f
    petrie_neighbor = Gp.has_edge(e, f)

    return {
        "shares_vertex": shares_vertex,
        "same_face": same_face,
        "opposite": opposite,
        "petrie_neighbor": petrie_neighbor,
    }


def main():
    print("=" * 80)
    print("CLASSIFY 30-LAYER ADJACENCY RULE")
    print("=" * 80)

    # Recover G30 and G15 from Thalean graph
    G60 = load_thalean_graph()
    a60 = antipode_map(G60)
    G30, classes30, _ = quotient_by_pairs(G60, a60)

    a30 = antipode_map(G30)
    G15_recovered, classes15, _ = quotient_by_pairs(G30, a30)

    # Build canonical 15-core from dodecahedron and match to recovered 15-core
    D = nx.dodecahedral_graph()
    faces = all_faces_of_dodecahedron(D)
    G15_canonical, opposite_pairs = build_canonical_g15_from_dodecahedron(D)

    iso = nx.is_isomorphic(G15_recovered, G15_canonical)
    print("Recovered 15-core matches canonical dodecahedral 15-core:", iso)
    if not iso:
        raise RuntimeError("15-core mismatch; cannot classify 30-layer geometrically.")

    # Get an explicit isomorphism from recovered 15-core to canonical one
    gm15 = nx.algorithms.isomorphism.GraphMatcher(G15_recovered, G15_canonical)
    phi15 = next(gm15.isomorphisms_iter())

    # Label each 30-layer vertex by a canonical dodecahedron edge
    # Each recovered 15-core vertex i is a pair of 30-layer vertices classes15[i]
    # Each canonical 15-core vertex phi15[i] is a pair of opposite canonical edges
    edge_label_of_30 = {}
    for i, pair30 in enumerate(classes15):
        pair_edges = opposite_pairs[phi15[i]]
        # assign the two 30-layer reps to the two canonical edges in both possible ways later
        # use the simple sorted pairing first
        edge_label_of_30[pair30[0]] = pair_edges[0]
        edge_label_of_30[pair30[1]] = pair_edges[1]

    # Build opposite-edge lookup
    opposite_of = {}
    for e, f in opposite_pairs:
        opposite_of[e] = f
        opposite_of[f] = e

    # Naive Petrie graph on canonical edges for comparison
    Gp = naive_petrie_edge_graph(D, faces)

    print()
    print("30-LAYER SUMMARY")
    print("-" * 80)
    print("vertices:", G30.number_of_nodes())
    print("edges:", G30.number_of_edges())
    print("degree set:", sorted(set(dict(G30.degree()).values())))

    # Classify every G30 edge by canonical edge relation
    hist = Counter()
    rows = []

    for u, v in sorted(G30.edges()):
        eu = edge_label_of_30[u]
        ev = edge_label_of_30[v]
        rel = relation_signature(eu, ev, D, faces, opposite_of, Gp)
        key = tuple(k for k, val in rel.items() if val)
        hist[key] += 1
        if len(rows) < 40:
            rows.append((u, v, eu, ev, rel))

    print()
    print("EDGE-RELATION HISTOGRAM IN G30")
    print("-" * 80)
    for key, count in sorted(hist.items(), key=lambda kv: (len(kv[0]), kv[0], kv[1])):
        print(f"{key if key else ('none',)} : {count}")

    print()
    print("FIRST 40 G30 EDGES WITH CANONICAL EDGE LABELS")
    print("-" * 80)
    for u, v, eu, ev, rel in rows:
        print(f"{u:2d}-{v:2d}  {eu} -- {ev}  {rel}")

    print()
    print("CHECK NONEDGES TOO")
    print("-" * 80)
    non_hist = Counter()
    shown = 0
    for u, v in itertools.combinations(sorted(G30.nodes()), 2):
        if G30.has_edge(u, v):
            continue
        eu = edge_label_of_30[u]
        ev = edge_label_of_30[v]
        rel = relation_signature(eu, ev, D, faces, opposite_of, Gp)
        key = tuple(k for k, val in rel.items() if val)
        non_hist[key] += 1
        if shown < 30:
            print(f"{u:2d}-{v:2d}  {eu} -- {ev}  {rel}")
            shown += 1

    print("nonedge relation histogram:")
    for key, count in sorted(non_hist.items(), key=lambda kv: (len(kv[0]), kv[0], kv[1])):
        print(f"{key if key else ('none',)} : {count}")

    print()
    print("INTERPRETATION")
    print("-" * 80)
    print("This probe classifies recovered 30-layer adjacency using canonical")
    print("dodecahedral edge labels inherited through the 15-core identification.")
    print("A clean dominant relation would reveal the true geometric adjacency law.")


if __name__ == "__main__":
    main()
