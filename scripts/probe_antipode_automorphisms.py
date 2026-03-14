#!/usr/bin/env python3

import networkx as nx
from collections import Counter
from load_thalean_graph import load_spec, build_graph


def load_thalean_graph():
    spec = load_spec()
    return build_graph(spec)


def antipode_map(G):
    dist = dict(nx.all_pairs_shortest_path_length(G))
    a = {}
    for v in G.nodes():
        far = [u for u, d in dist[v].items() if d == 6]
        if len(far) != 1:
            raise RuntimeError(f"vertex {v} has {len(far)} antipodes")
        a[v] = far[0]
    return a


def quotient_by_antipodes(G, a):
    seen = set()
    classes = []
    cls_of = {}
    for v in sorted(G.nodes()):
        if v in seen:
            continue
        pair = tuple(sorted((v, a[v])))
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


def automorphisms(G, max_count=None):
    gm = nx.algorithms.isomorphism.GraphMatcher(G, G)
    out = []
    for i, phi in enumerate(gm.isomorphisms_iter(), start=1):
        out.append(dict(phi))
        if max_count is not None and i >= max_count:
            break
    return out


def preserves_antipodes(phi, a):
    # phi(a(v)) must equal a(phi(v))
    for v in a:
        if phi[a[v]] != a[phi[v]]:
            return False
    return True


def induced_on_quotient(phi, classes, cls_of):
    # Since antipodal classes are preserved, each class maps to one class
    induced = {}
    for i, pair in enumerate(classes):
        image_class = cls_of[phi[pair[0]]]
        # sanity: both members should land in same class
        if cls_of[phi[pair[1]]] != image_class:
            raise RuntimeError("automorphism did not descend cleanly to quotient")
        induced[i] = image_class
    return induced


def orbit_partition(perms, nodes):
    unseen = set(nodes)
    orbits = []
    while unseen:
        seed = next(iter(unseen))
        orb = {seed}
        changed = True
        while changed:
            changed = False
            for p in perms:
                img = {p[x] for x in orb}
                inv = {x for x, y in p.items() if y in orb}
                new = img | inv
                if not new.issubset(orb):
                    orb |= new
                    changed = True
        unseen -= orb
        orbits.append(sorted(orb))
    return sorted(orbits, key=lambda x: (len(x), x))


def shell_counts(G, root=0):
    d = nx.single_source_shortest_path_length(G, root)
    c = Counter(d.values())
    return tuple(c[i] for i in range(max(c) + 1))


def triangle_count(G):
    return sum(nx.triangles(G).values()) // 3


def main():
    print("=" * 80)
    print("ANTIPODE AUTOMORPHISM PROBE")
    print("=" * 80)

    G = load_thalean_graph()
    a = antipode_map(G)
    Q, classes, cls_of = quotient_by_antipodes(G, a)

    print("THALEAN GRAPH")
    print("-" * 80)
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted(set(dict(G.degree()).values())))
    print("diameter:", nx.diameter(G))
    print("triangles:", triangle_count(G))
    print("shell counts from 0:", shell_counts(G, 0))

    print()
    print("ANTIPODAL QUOTIENT")
    print("-" * 80)
    print("vertices:", Q.number_of_nodes())
    print("edges:", Q.number_of_edges())
    print("degree set:", sorted(set(dict(Q.degree()).values())))
    print("connected:", nx.is_connected(Q))
    print("diameter:", nx.diameter(Q))
    print("triangles:", triangle_count(Q))
    print("shell counts from 0:", shell_counts(Q, 0))

    print()
    print("COMPUTING AUTOMORPHISMS OF 60-GRAPH")
    print("-" * 80)

    # Warning: depending on graph symmetry this may be big, but for this graph it should be manageable.
    autos = automorphisms(G)
    print("automorphisms found:", len(autos))

    preserve_flags = [preserves_antipodes(phi, a) for phi in autos]
    print("preserve antipodal relation:", all(preserve_flags))
    print("count preserving antipodes:", sum(preserve_flags))

    if not all(preserve_flags):
        print("WARNING: some automorphisms do not preserve antipodal pairs")
        return

    print()
    print("INDUCED AUTOMORPHISMS ON 30-QUOTIENT")
    print("-" * 80)
    induced = [induced_on_quotient(phi, classes, cls_of) for phi in autos]

    # deduplicate induced perms
    seen = set()
    induced_unique = []
    for p in induced:
        key = tuple(p[i] for i in range(len(classes)))
        if key not in seen:
            seen.add(key)
            induced_unique.append(p)

    print("distinct induced automorphisms:", len(induced_unique))

    q_orbits = orbit_partition(induced_unique, list(Q.nodes()))
    print("vertex orbits on 30-quotient:", [len(o) for o in q_orbits])
    for i, orb in enumerate(q_orbits[:10], start=1):
        print(f"orbit {i}: {orb}")

    print()
    print("FIRST 15 ANTIPODAL CLASSES")
    print("-" * 80)
    for i, pair in enumerate(classes[:15]):
        print(f"{i:2d} -> {pair}")

    print()
    print("GRAPH6 OF 30-QUOTIENT")
    print("-" * 80)
    print(nx.to_graph6_bytes(Q, header=False).decode().strip())


if __name__ == "__main__":
    main()
