#!/usr/bin/env python3

from collections import Counter
import math
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


def automorphisms(G):
    gm = nx.algorithms.isomorphism.GraphMatcher(G, G)
    return [dict(phi) for phi in gm.isomorphisms_iter()]


def compose(p, q):
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


def find_second_involution(G, a, autos):
    invols = [p for p in autos if is_involution(p)]
    candidates = []
    for p in invols:
        if is_identity(p):
            continue
        if equal_maps(p, a):
            continue
        if len(fixed_points(p)) == 0 and commute(p, a):
            candidates.append(p)

    good = []
    for p in candidates:
        orbits = orbit_partition([a, p], list(G.nodes()))
        sizes = Counter(len(o) for o in orbits)
        if sizes == Counter({4: 15}):
            good.append((p, orbits))

    if not good:
        raise RuntimeError("No suitable second involution found")

    return good[0]


def induced_on_fibers(phi, fibers, fiber_of):
    perm = {}
    for i, fiber in enumerate(fibers):
        img_fiber = fiber_of[phi[fiber[0]]]
        for v in fiber:
            if fiber_of[phi[v]] != img_fiber:
                raise RuntimeError("automorphism does not preserve fiber partition")
        perm[i] = img_fiber
    return perm


def perm_key(p, n):
    return tuple(p[i] for i in range(n))


def permutation_order(p, n):
    seen = [False] * n
    lcm = 1
    for i in range(n):
        if seen[i]:
            continue
        j = i
        cycle_len = 0
        while not seen[j]:
            seen[j] = True
            j = p[j]
            cycle_len += 1
        if cycle_len > 0:
            lcm = math.lcm(lcm, cycle_len)
    return lcm


def cycle_type(p, n):
    seen = [False] * n
    lengths = []
    for i in range(n):
        if seen[i]:
            continue
        j = i
        cycle_len = 0
        while not seen[j]:
            seen[j] = True
            j = p[j]
            cycle_len += 1
        lengths.append(cycle_len)
    return tuple(sorted(lengths))


def main():
    print("=" * 80)
    print("IDENTIFY INDUCED 120-GROUP ON 15 FIBERS")
    print("=" * 80)

    G60 = load_thalean_graph()
    autos60 = automorphisms(G60)
    print("automorphisms of G60:", len(autos60))

    a = antipode_map(G60)
    b, fibers = find_second_involution(G60, a, autos60)

    fiber_of = {}
    for i, f in enumerate(fibers):
        for v in f:
            fiber_of[v] = i

    induced = [induced_on_fibers(phi, fibers, fiber_of) for phi in autos60]

    # dedupe induced perms
    seen = set()
    induced_unique = []
    for p in induced:
        key = perm_key(p, len(fibers))
        if key not in seen:
            seen.add(key)
            induced_unique.append(p)

    print("distinct induced permutations:", len(induced_unique))

    # Build the actual 15-core and compare to its full automorphism group
    G30, _, cls30 = quotient_by_pairs(G60, a)
    a30 = antipode_map(G30)
    G15, _, _ = quotient_by_pairs(G30, a30)

    autos15 = automorphisms(G15)
    print("automorphisms of G15:", len(autos15))

    # compare permutation sets exactly
    induced_keys = {perm_key(p, 15) for p in induced_unique}
    autos15_keys = {tuple(phi[i] for i in range(15)) for phi in autos15}

    print("induced action equals full Aut(G15):", induced_keys == autos15_keys)

    print()
    print("ORDER DISTRIBUTION OF INDUCED 120-GROUP")
    print("-" * 80)
    order_hist = Counter(permutation_order(p, 15) for p in induced_unique)
    for k, c in sorted(order_hist.items()):
        print(f"order {k}: {c}")

    print()
    print("CYCLE-TYPE HISTOGRAM (TOP 20)")
    print("-" * 80)
    ct_hist = Counter(cycle_type(p, 15) for p in induced_unique)
    for ct, c in ct_hist.most_common(20):
        print(f"{ct}: {c}")

    print()
    print("POINT STABILIZER SIZE")
    print("-" * 80)
    stab0 = [p for p in induced_unique if p[0] == 0]
    print("stabilizer of vertex 0:", len(stab0))

    print()
    print("S5 SIGNATURE CHECK")
    print("-" * 80)
    s5_expected = {1: 1, 2: 25, 3: 20, 4: 30, 5: 24, 6: 20}
    print("expected S5 order histogram:", s5_expected)
    print("matches S5 exactly:", dict(order_hist) == s5_expected)

    print()
    print("INTERPRETATION")
    print("-" * 80)
    if len(induced_unique) == 120 and dict(order_hist) == s5_expected:
        print("The induced 120-group has the exact order distribution of S5.")
    else:
        print("The induced 120-group does not match the S5 order distribution exactly.")

    if induced_keys == autos15_keys:
        print("The induced action is the full automorphism group of the 15-core.")
    else:
        print("The induced action is a proper subgroup of Aut(G15).")


if __name__ == "__main__":
    main()
