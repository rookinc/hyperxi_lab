#!/usr/bin/env python3

from collections import Counter
from pathlib import Path
import ast
import networkx as nx

from load_thalean_graph import load_spec, build_graph


SIGN_PATH = Path("artifacts/reports/recovered_signing.txt")


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


def load_signing():
    """
    Expect lines or Python-literal structure mapping 60-vertices to (base, sheet).
    This parser is intentionally permissive.
    """
    if not SIGN_PATH.exists():
        return None

    text = SIGN_PATH.read_text().strip()

    # Try full literal first
    try:
        obj = ast.literal_eval(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    mapping = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # formats like: 0 -> (0, 0)
        if "->" in line:
            left, right = line.split("->", 1)
            try:
                v = int(left.strip().strip(","))
                pair = ast.literal_eval(right.strip())
                mapping[v] = pair
                continue
            except Exception:
                pass
        # formats like: 0 (0,0)
        parts = line.split(None, 1)
        if len(parts) == 2:
            try:
                v = int(parts[0])
                pair = ast.literal_eval(parts[1])
                mapping[v] = pair
                continue
            except Exception:
                pass

    return mapping if mapping else None


def main():
    print("=" * 80)
    print("PROBE GEOMETRIC MEANING OF SECOND INVOLUTION b")
    print("=" * 80)

    G60 = load_thalean_graph()
    autos = automorphisms(G60)
    a = antipode_map(G60)
    b, fibers = find_second_involution(G60, a, autos)

    print("found b with 15 four-element fibers")
    print("first 10 actions:")
    for v in range(10):
        print(f"  {v} -> {b[v]}")

    # 60 -> 30
    G30, classes30, cls30 = quotient_by_pairs(G60, a)

    # 30 -> 15
    a30 = antipode_map(G30)
    G15, classes15, cls15 = quotient_by_pairs(G30, a30)

    print()
    print("RELATION TO 30-LAYER")
    print("-" * 80)
    rel30 = Counter()
    for v in sorted(G60.nodes()):
        c0 = cls30[v]
        c1 = cls30[b[v]]
        rel30["same_30_class" if c0 == c1 else "different_30_class"] += 1
    print(dict(rel30))

    print()
    print("RELATION TO 15-LAYER")
    print("-" * 80)
    # map each 60-vertex to 15-core fiber via 30 then 15
    cls15_of_60 = {}
    for v in G60.nodes():
        cls15_of_60[v] = cls15[cls30[v]]

    rel15 = Counter()
    for v in sorted(G60.nodes()):
        f0 = cls15_of_60[v]
        f1 = cls15_of_60[b[v]]
        rel15["same_15_fiber" if f0 == f1 else "different_15_fiber"] += 1
    print(dict(rel15))

    print()
    print("COMPARE WITH SHEET STRUCTURE (if available)")
    print("-" * 80)
    signing = load_signing()
    if signing is None:
        print(f"No readable signing found at {SIGN_PATH}")
    else:
        # normalize keys if stored as strings
        norm = {}
        for k, v in signing.items():
            try:
                norm[int(k)] = tuple(v)
            except Exception:
                pass
        signing = norm

        # classify b relative to (base, sheet)
        hist = Counter()
        samples = []
        for v in sorted(G60.nodes()):
            if v not in signing or b[v] not in signing:
                continue
            base0, sheet0 = signing[v]
            base1, sheet1 = signing[b[v]]

            if base0 == base1 and sheet0 != sheet1:
                kind = "pure_sheet_flip"
            elif base0 == base1 and sheet0 == sheet1:
                kind = "same_base_same_sheet"
            elif base0 != base1 and sheet0 == sheet1:
                kind = "base_swap_same_sheet"
            else:
                kind = "base_swap_sheet_flip"

            hist[kind] += 1
            if len(samples) < 20:
                samples.append((v, signing[v], b[v], signing[b[v]], kind))

        print("classification histogram:", dict(sorted(hist.items())))
        print("sample moves:")
        for row in samples:
            print(" ", row)

    print()
    print("COMPARE b TO a, ab")
    print("-" * 80)
    ab = compose(a, b)
    print("b fixed points:", len(fixed_points(b)))
    print("ab fixed points:", len(fixed_points(ab)))
    print("a and b commute:", commute(a, b))

    print()
    print("FIRST 15 FOUR-ELEMENT FIBERS")
    print("-" * 80)
    for i, fiber in enumerate(fibers[:15]):
        print(f"{i:2d} -> {fiber}")

    print()
    print("INTERPRETATION")
    print("-" * 80)
    print("If b preserves the 15-fiber and usually changes the 30-layer representative,")
    print("then b is the second binary distinction inside each 4-lift fiber.")
    print("If b also appears as a pure sheet flip with respect to recovered signing,")
    print("that is strong evidence b is the chamber-side flip on a fixed edge class.")

if __name__ == "__main__":
    main()
