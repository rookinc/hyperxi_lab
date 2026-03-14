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


def automorphisms(G):
    gm = nx.algorithms.isomorphism.GraphMatcher(G, G)
    return [dict(phi) for phi in gm.isomorphisms_iter()]


def compose(p, q):
    # p ∘ q
    return {k: p[q[k]] for k in q}


def is_identity(p):
    return all(k == v for k, v in p.items())


def is_involution(p):
    return is_identity(compose(p, p))


def fixed_points(p):
    return [k for k, v in p.items() if k == v]


def equal_maps(p, q):
    return all(p[k] == q[k] for k in p)


def commute(p, q):
    return equal_maps(compose(p, q), compose(q, p))


def orbit_partition(gens, nodes):
    unseen = set(nodes)
    orbits = []
    while unseen:
        seed = next(iter(unseen))
        orb = {seed}
        changed = True
        while changed:
            changed = False
            for g in gens:
                img = {g[x] for x in orb}
                inv = {x for x, y in g.items() if y in orb}
                new = img | inv
                if not new.issubset(orb):
                    orb |= new
                    changed = True
        unseen -= orb
        orbits.append(sorted(orb))
    return sorted(orbits, key=lambda x: (len(x), x))


def main():
    print("=" * 80)
    print("HUNT SECOND INVOLUTION")
    print("=" * 80)

    G = load_thalean_graph()
    a = antipode_map(G)

    print("loading automorphisms...")
    autos = automorphisms(G)
    print("automorphisms:", len(autos))

    invols = [p for p in autos if is_involution(p)]
    print("involutions:", len(invols))

    fp_hist = Counter(len(fixed_points(p)) for p in invols)
    print("fixed-point histogram among involutions:", dict(sorted(fp_hist.items())))

    # fixed-point-free involutions except identity and antipode
    candidates = []
    for p in invols:
        if is_identity(p):
            continue
        if equal_maps(p, a):
            continue
        if len(fixed_points(p)) == 0:
            candidates.append(p)

    print("fixed-point-free involutions excluding identity/antipode:", len(candidates))

    commuting = [p for p in candidates if commute(p, a)]
    print("of those, commuting with antipode:", len(commuting))

    print()
    print("TESTING 4-FIBER STRUCTURE WITH ANTIPODE")
    print("-" * 80)

    good = []
    for idx, b in enumerate(commuting):
        orbits = orbit_partition([a, b], list(G.nodes()))
        sizes = Counter(len(o) for o in orbits)
        # ideal case: 15 orbits of size 4
        if sizes == Counter({4: 15}):
            good.append((idx, b, orbits))

    print("commuting involutions giving 15 four-vertex fibers:", len(good))

    if good:
        idx, b, orbits = good[0]
        print("\nFOUND A GOOD CANDIDATE")
        print("-" * 80)
        print("candidate index among commuting involutions:", idx)
        print("first 15 fibers:")
        for i, orb in enumerate(orbits[:15]):
            print(f"{i:2d} -> {orb}")

        print()
        print("sample action on first 20 vertices")
        print("-" * 80)
        for v in range(20):
            print(f"v={v:2d}  a(v)={a[v]:2d}  b(v)={b[v]:2d}  ab(v)={a[b[v]]:2d}")

    else:
        print("No commuting fixed-point-free involution produced exactly 15 fibers of size 4.")

    print()
    print("SAMPLE COMMUTING INVOLUTIONS")
    print("-" * 80)
    for i, b in enumerate(commuting[:5]):
        fps = fixed_points(b)
        print(f"candidate {i}: fixed points={len(fps)}")
        moved = [(v, b[v]) for v in sorted(G.nodes())[:10]]
        print("  first moves:", moved)


if __name__ == "__main__":
    main()
