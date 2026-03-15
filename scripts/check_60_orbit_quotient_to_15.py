#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from collections import Counter

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from load_thalean_graph import load_spec, build_graph


def shell_profile(G: nx.Graph, src: int = 0):
    dist = nx.single_source_shortest_path_length(G, src)
    c = Counter(dist.values())
    return tuple(c[i] for i in range(max(c) + 1))


def triangle_count(G: nx.Graph) -> int:
    return sum(nx.triangles(G).values()) // 3


def antipode_map(G: nx.Graph) -> dict[int, int]:
    dist = dict(nx.all_pairs_shortest_path_length(G))
    diam = nx.diameter(G)
    a = {}

    for v in G.nodes():
        far = [u for u, d in dist[v].items() if d == diam]
        if len(far) != 1:
            raise RuntimeError(f"vertex {v} has {len(far)} distance-{diam} partners")
        a[v] = far[0]

    return a


def automorphisms(G: nx.Graph) -> list[dict[int, int]]:
    gm = nx.algorithms.isomorphism.GraphMatcher(G, G)
    return [dict(phi) for phi in gm.isomorphisms_iter()]


def compose(p: dict[int, int], q: dict[int, int]) -> dict[int, int]:
    return {k: p[q[k]] for k in q}


def equal_maps(p: dict[int, int], q: dict[int, int]) -> bool:
    return all(p[k] == q[k] for k in p)


def is_identity(p: dict[int, int]) -> bool:
    return all(k == v for k, v in p.items())


def is_involution(p: dict[int, int]) -> bool:
    return is_identity(compose(p, p))


def fixed_points(p: dict[int, int]) -> list[int]:
    return [k for k, v in p.items() if k == v]


def commute(p: dict[int, int], q: dict[int, int]) -> bool:
    return equal_maps(compose(p, q), compose(q, p))


def orbit_partition(gens: list[dict[int, int]], nodes: list[int]) -> list[list[int]]:
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
                pre = {x for x, y in g.items() if y in orb}
                new = img | pre
                if not new.issubset(orb):
                    orb |= new
                    changed = True

        unseen -= orb
        orbits.append(sorted(orb))

    return sorted(orbits, key=lambda x: (len(x), x))


def find_second_involution(
    G: nx.Graph,
    a: dict[int, int],
    autos: list[dict[int, int]],
) -> tuple[dict[int, int], list[list[int]]]:
    invols = [p for p in autos if is_involution(p)]

    candidates = []
    for p in invols:
        if is_identity(p):
            continue
        if equal_maps(p, a):
            continue
        if fixed_points(p):
            continue
        if not commute(p, a):
            continue

        orbits = orbit_partition([a, p], list(G.nodes()))
        sizes = Counter(len(o) for o in orbits)

        if sizes == Counter({4: 15}):
            candidates.append((p, orbits))

    if not candidates:
        raise RuntimeError("No suitable second involution found")

    return candidates[0]


def quotient_by_orbits(G: nx.Graph, orbits: list[list[int]]) -> tuple[nx.Graph, dict[int, int]]:
    owner = {}
    for i, orb in enumerate(orbits):
        for v in orb:
            owner[v] = i

    Q = nx.Graph()
    Q.add_nodes_from(range(len(orbits)))

    for u, v in G.edges():
        a = owner[u]
        b = owner[v]
        if a != b:
            Q.add_edge(a, b)

    return Q, owner


def covering_test(G: nx.Graph, Q: nx.Graph, owner: dict[int, int]) -> tuple[bool, tuple | None]:
    for u in G.nodes():
        qu = owner[u]
        target_classes = set(Q.neighbors(qu))
        counts = {qc: 0 for qc in target_classes}

        for v in G.neighbors(u):
            qv = owner[v]
            if qv in counts:
                counts[qv] += 1

        bad = {k: c for k, c in counts.items() if c != 1}
        if bad:
            return False, (u, qu, counts)

    return True, None


def main():
    print("=" * 80)
    print("CHECK 60-GRAPH ORBIT QUOTIENT TO 15-CORE")
    print("=" * 80)

    G60 = build_graph(load_spec())

    print("G60 SUMMARY")
    print("-" * 80)
    print("vertices:", G60.number_of_nodes())
    print("edges:", G60.number_of_edges())
    print("degree set:", sorted(set(dict(G60.degree()).values())))
    print("triangles:", triangle_count(G60))
    print("diameter:", nx.diameter(G60))
    print("shell profile from 0:", shell_profile(G60, 0))
    print()

    print("FINDING a")
    print("-" * 80)
    a = antipode_map(G60)
    print("a is fixed-point-free involution:", is_involution(a) and len(fixed_points(a)) == 0)
    print("first 15 images:", [(v, a[v]) for v in range(15)])
    print()

    print("ENUMERATING AUTOMORPHISMS")
    print("-" * 80)
    autos = automorphisms(G60)
    print("automorphism count:", len(autos))
    print()

    print("FINDING b")
    print("-" * 80)
    b, orbits = find_second_involution(G60, a, autos)
    print("b is fixed-point-free involution:", is_involution(b) and len(fixed_points(b)) == 0)
    print("a and b commute:", commute(a, b))
    print("orbit count:", len(orbits))
    print("orbit size histogram:", dict(sorted(Counter(len(o) for o in orbits).items())))
    print("first 10 orbit fibers:")
    for i, orb in enumerate(orbits[:10]):
        print(f"{i:2d} -> {orb}")
    print()

    Q15, owner = quotient_by_orbits(G60, orbits)

    print("QUOTIENT SUMMARY")
    print("-" * 80)
    print("vertices:", Q15.number_of_nodes())
    print("edges:", Q15.number_of_edges())
    print("degree set:", sorted(set(dict(Q15.degree()).values())))
    print("triangles:", triangle_count(Q15))
    print("diameter:", nx.diameter(Q15))
    print("shell profile from 0:", shell_profile(Q15, 0))
    print()

    P = nx.petersen_graph()
    LP = nx.line_graph(P)

    print("COMPARE TO L(PETERSEN)")
    print("-" * 80)
    print("isomorphic:", nx.is_isomorphic(Q15, LP))
    print()

    ok, witness = covering_test(G60, Q15, owner)

    print("COVERING TEST")
    print("-" * 80)
    print("is regular covering projection:", ok)
    if witness is not None:
        u, qu, counts = witness
        print("first failing upstairs vertex:", u)
        print("quotient class:", qu)
        print("neighbor-class counts:", counts)

    out_dir = ROOT / "reports" / "true_quotients"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "check_60_orbit_quotient_to_15.txt"

    lines = [
        "=" * 80,
        "CHECK 60-GRAPH ORBIT QUOTIENT TO 15-CORE",
        "=" * 80,
        "",
        "G60 SUMMARY",
        "-" * 80,
        f"vertices: {G60.number_of_nodes()}",
        f"edges: {G60.number_of_edges()}",
        f"degree set: {sorted(set(dict(G60.degree()).values()))}",
        f"triangles: {triangle_count(G60)}",
        f"diameter: {nx.diameter(G60)}",
        f"shell profile from 0: {shell_profile(G60, 0)}",
        "",
        "FINDING a",
        "-" * 80,
        f"a is fixed-point-free involution: {is_involution(a) and len(fixed_points(a)) == 0}",
        f"first 15 images: {[(v, a[v]) for v in range(15)]}",
        "",
        "ENUMERATING AUTOMORPHISMS",
        "-" * 80,
        f"automorphism count: {len(autos)}",
        "",
        "FINDING b",
        "-" * 80,
        f"b is fixed-point-free involution: {is_involution(b) and len(fixed_points(b)) == 0}",
        f"a and b commute: {commute(a, b)}",
        f"orbit count: {len(orbits)}",
        f"orbit size histogram: {dict(sorted(Counter(len(o) for o in orbits).items()))}",
        "first 10 orbit fibers:",
    ]

    for i, orb in enumerate(orbits[:10]):
        lines.append(f"{i:2d} -> {orb}")

    lines.extend([
        "",
        "QUOTIENT SUMMARY",
        "-" * 80,
        f"vertices: {Q15.number_of_nodes()}",
        f"edges: {Q15.number_of_edges()}",
        f"degree set: {sorted(set(dict(Q15.degree()).values()))}",
        f"triangles: {triangle_count(Q15)}",
        f"diameter: {nx.diameter(Q15)}",
        f"shell profile from 0: {shell_profile(Q15, 0)}",
        "",
        "COMPARE TO L(PETERSEN)",
        "-" * 80,
        f"isomorphic: {nx.is_isomorphic(Q15, LP)}",
        "",
        "COVERING TEST",
        "-" * 80,
        f"is regular covering projection: {ok}",
    ])

    if witness is not None:
        u, qu, counts = witness
        lines.append(f"first failing upstairs vertex: {u}")
        lines.append(f"quotient class: {qu}")
        lines.append(f"neighbor-class counts: {counts}")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print()
    print(f"saved {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
