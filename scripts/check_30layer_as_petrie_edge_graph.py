#!/usr/bin/env python3

from collections import Counter
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


def canonical_edge(u, v):
    return tuple(sorted((u, v)))


def all_faces_of_dodecahedron(D):
    """
    Recover the 12 pentagonal faces as induced 5-cycles.
    """
    faces = set()
    cycles = nx.cycle_basis(D)
    for cyc in cycles:
        if len(cyc) != 5:
            continue
        # canonicalize cycle up to rotation/reversal
        cyc = list(cyc)
        rots = []
        n = len(cyc)
        for k in range(n):
            rots.append(tuple(cyc[k:] + cyc[:k]))
        rev = list(reversed(cyc))
        for k in range(n):
            rots.append(tuple(rev[k:] + rev[:k]))
        faces.add(min(rots))
    # cycle_basis on dodecahedron returns 11 faces typically; close under all simple cycles of len 5
    if len(faces) != 12:
        # brute-force all simple cycles length 5 via directed search
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
    u, v = e
    n = len(face)
    for i in range(n):
        a, b = face[i], face[(i + 1) % n]
        if canonical_edge(a, b) == e:
            return True
    return False


def other_face_of_edge(faces, e, current_face_idx):
    hits = [i for i, f in enumerate(faces) if edge_in_face(f, e)]
    if len(hits) != 2:
        raise RuntimeError(f"Edge {e} lies in {len(hits)} faces, expected 2")
    return hits[1] if hits[0] == current_face_idx else hits[0]


def next_edge_petrie(face, current_edge):
    """
    In a pentagon face, given an edge, return the two edges not adjacent to it.
    Those are the two possible Petrie continuations in that face.
    """
    edges = [canonical_edge(face[i], face[(i + 1) % 5]) for i in range(5)]
    idx = edges.index(current_edge)
    return edges[(idx + 2) % 5], edges[(idx + 3) % 5]


def petrie_graph_on_edges(D):
    """
    Build a graph on the 30 edges of the dodecahedron:
    two edges are adjacent if one Petrie step can move between them.
    """
    faces = all_faces_of_dodecahedron(D)
    edges = sorted(canonical_edge(u, v) for u, v in D.edges())

    Gp = nx.Graph()
    Gp.add_nodes_from(edges)

    # For each incident pair (edge, face), one Petrie step:
    # cross to the other face through the same edge, then choose one of the two nonadjacent
    # edges in that new face. This gives two continuations per side, total four neighbors.
    for e in edges:
        face_idxs = [i for i, f in enumerate(faces) if edge_in_face(f, e)]
        for fi in face_idxs:
            fj = other_face_of_edge(faces, e, fi)
            cont1, cont2 = next_edge_petrie(faces[fj], e)
            Gp.add_edge(e, cont1)
            Gp.add_edge(e, cont2)

    return Gp, faces


def shell_counts(G, root):
    d = nx.single_source_shortest_path_length(G, root)
    c = Counter(d.values())
    return tuple(c[i] for i in range(max(c) + 1))


def triangle_count(G):
    return sum(nx.triangles(G).values()) // 3


def relabel_to_ints(G):
    nodes = sorted(G.nodes())
    mapping = {v: i for i, v in enumerate(nodes)}
    return nx.relabel_nodes(G, mapping), mapping


def main():
    print("=" * 80)
    print("CHECK 30-LAYER AS PETRIE EDGE GRAPH")
    print("=" * 80)

    # recovered 30-layer from Thalean graph
    G60 = load_thalean_graph()
    a60 = antipode_map(G60)
    G30, classes30, _ = quotient_by_pairs(G60, a60)

    print("RECOVERED 30-LAYER")
    print("-" * 80)
    print("vertices:", G30.number_of_nodes())
    print("edges:", G30.number_of_edges())
    print("degree set:", sorted(set(dict(G30.degree()).values())))
    print("diameter:", nx.diameter(G30))
    print("triangles:", triangle_count(G30))
    print("shell counts from 0:", shell_counts(G30, 0))

    D = nx.dodecahedral_graph()
    Gp_edge, faces = petrie_graph_on_edges(D)
    Gp, edge_map = relabel_to_ints(Gp_edge)

    print()
    print("DIRECT PETRIE EDGE GRAPH")
    print("-" * 80)
    print("faces found:", len(faces))
    print("vertices:", Gp.number_of_nodes())
    print("edges:", Gp.number_of_edges())
    print("degree set:", sorted(set(dict(Gp.degree()).values())))
    print("diameter:", nx.diameter(Gp))
    print("triangles:", triangle_count(Gp))
    print("shell counts from 0:", shell_counts(Gp, 0))

    print()
    print("ISOMORPHISM TEST")
    print("-" * 80)
    iso = nx.is_isomorphic(G30, Gp)
    print("G30 ≅ Petrie-edge graph:", iso)

    print()
    print("FIRST 12 FACES")
    print("-" * 80)
    for i, f in enumerate(faces):
        print(f"{i:2d} -> {f}")

    print()
    print("FIRST 20 EDGE LABELS")
    print("-" * 80)
    inv_map = {i: e for e, i in edge_map.items()}
    for i in range(min(20, len(inv_map))):
        print(f"{i:2d} -> {inv_map[i]}")

    print()
    print("INTERPRETATION")
    print("-" * 80)
    if iso:
        print("The 30-layer is exactly the Petrie transport graph on dodecahedron edges.")
    else:
        print("This simple Petrie-edge rule does not yet match the 30-layer.")
        print("If so, the 30-layer is still Petrie-related, but via a more refined chamber-induced rule.")


if __name__ == "__main__":
    main()
