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
        # sanity: whole fiber must map to same fiber
        for v in fiber:
            if fiber_of[phi[v]] != img_fiber:
                raise RuntimeError("automorphism does not preserve fiber partition")
        perm[i] = img_fiber
    return perm


def perm_key(p, n):
    return tuple(p[i] for i in range(n))


def orbit_sizes_of_action(perms, n):
    unseen = set(range(n))
    out = []
    while unseen:
        seed = next(iter(unseen))
        orb = {seed}
        changed = True
        while changed:
            changed = False
            for p in perms:
                img = {p[x] for x in orb}
                inv = {x for x in range(n) if p[x] in orb}
                new = img | inv
                if not new.issubset(orb):
                    orb |= new
                    changed = True
        unseen -= orb
        out.append(sorted(orb))
    return sorted(out, key=lambda x: (len(x), x))


def main():
    print("=" * 80)
    print("AUTOMORPHISM ACTION ON 15 FIBERS")
    print("=" * 80)

    G = load_thalean_graph()
    autos = automorphisms(G)
    print("automorphisms of G60:", len(autos))

    a = antipode_map(G)
    b, fibers = find_second_involution(G, a, autos)

    print("found second involution b giving 15 fibers of size 4")
    print("first 15 fibers:")
    for i, f in enumerate(fibers[:15]):
        print(f"{i:2d} -> {f}")

    fiber_of = {}
    for i, f in enumerate(fibers):
        for v in f:
            fiber_of[v] = i

    induced = [induced_on_fibers(phi, fibers, fiber_of) for phi in autos]

    # deduplicate induced permutations
    seen = set()
    induced_unique = []
    for p in induced:
        key = perm_key(p, len(fibers))
        if key not in seen:
            seen.add(key)
            induced_unique.append(p)

    print()
    print("INDUCED ACTION ON 15 FIBERS")
    print("-" * 80)
    print("distinct induced permutations:", len(induced_unique))

    kernel = []
    for phi, p in zip(autos, induced):
        if all(p[i] == i for i in range(len(fibers))):
            kernel.append(phi)

    # dedupe kernel too
    kseen = set()
    kernel_unique = []
    for p in kernel:
        key = tuple(p[i] for i in sorted(G.nodes()))
        if key not in kseen:
            kseen.add(key)
            kernel_unique.append(p)

    print("kernel size (acts trivially on fibers):", len(kernel_unique))

    print()
    print("ORBIT STRUCTURE OF 15-FIBER ACTION")
    print("-" * 80)
    orbits = orbit_sizes_of_action(induced_unique, len(fibers))
    print("orbit sizes:", [len(o) for o in orbits])
    for i, orb in enumerate(orbits[:10], start=1):
        print(f"orbit {i}: {orb}")

    print()
    print("CHECK PRODUCT")
    print("-" * 80)
    print("kernel * induced =", len(kernel_unique) * len(induced_unique))
    print("full aut size      =", len(autos))

    print()
    print("INTERPRETATION")
    print("-" * 80)
    if len(kernel_unique) * len(induced_unique) == len(autos):
        print("Aut(G60) factors cleanly through the action on 15 fibers.")
    else:
        print("Aut(G60) does not factor cleanly in this simple count.")

    if len(induced_unique) == 120:
        print("The induced action on 15 fibers has order 120.")
    else:
        print(f"The induced action on 15 fibers has order {len(induced_unique)}, not 120.")

    print("If kernel size is 4 and induced size is 120, this matches the V4 × 120 picture exactly.")


if __name__ == "__main__":
    main()
