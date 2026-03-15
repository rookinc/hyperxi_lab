#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from collections import Counter, defaultdict
import itertools
import json

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


def canonical_edge(e):
    u, v = e
    return tuple(sorted((u, v)))


def dodecahedron_opposite_edge_pairs(D: nx.Graph):
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


def build_canonical_15core_from_dodecahedron(D: nx.Graph):
    pairs = dodecahedron_opposite_edge_pairs(D)
    L = nx.line_graph(D)

    G15 = nx.Graph()
    G15.add_nodes_from(range(len(pairs)))

    for i, j in itertools.combinations(range(len(pairs)), 2):
        A = pairs[i]
        B = pairs[j]

        edges_between = 0
        witnesses = []

        for e in A:
            for f in B:
                if L.has_edge(e, f):
                    edges_between += 1
                    witnesses.append((e, f))

        if edges_between == 2:
            G15.add_edge(i, j)

    return G15, pairs


def quotient_adjacency_table(Q: nx.Graph) -> dict[int, list[int]]:
    return {v: sorted(Q.neighbors(v)) for v in sorted(Q.nodes())}


def main():
    print("=" * 80)
    print("COMPARE V4 QUOTIENT TO CANONICAL DODECAHEDRAL 15-CORE")
    print("=" * 80)

    # Live 60-graph and its V4 quotient
    G60 = build_graph(load_spec())
    a = antipode_map(G60)
    autos = automorphisms(G60)
    b, orbits = find_second_involution(G60, a, autos)
    Q15, owner = quotient_by_orbits(G60, orbits)

    # Canonical dodecahedral 15-core
    D = nx.dodecahedral_graph()
    K15, opposite_pairs = build_canonical_15core_from_dodecahedron(D)

    iso = nx.is_isomorphic(Q15, K15)

    print("UPSTAIRS G60")
    print("-" * 80)
    print("vertices:", G60.number_of_nodes())
    print("edges:", G60.number_of_edges())
    print("degree set:", sorted(set(dict(G60.degree()).values())))
    print("triangles:", triangle_count(G60))
    print("diameter:", nx.diameter(G60))
    print("shell profile:", shell_profile(G60, 0))
    print()

    print("V4 QUOTIENT Q15")
    print("-" * 80)
    print("vertices:", Q15.number_of_nodes())
    print("edges:", Q15.number_of_edges())
    print("degree set:", sorted(set(dict(Q15.degree()).values())))
    print("triangles:", triangle_count(Q15))
    print("diameter:", nx.diameter(Q15))
    print("shell profile:", shell_profile(Q15, 0))
    print()

    print("CANONICAL DODECAHEDRAL 15-CORE K15")
    print("-" * 80)
    print("vertices:", K15.number_of_nodes())
    print("edges:", K15.number_of_edges())
    print("degree set:", sorted(set(dict(K15.degree()).values())))
    print("triangles:", triangle_count(K15))
    print("diameter:", nx.diameter(K15))
    print("shell profile:", shell_profile(K15, 0))
    print()

    print("ISOMORPHISM TEST")
    print("-" * 80)
    print("Q15 ≅ K15:", iso)
    print()

    if not iso:
        raise RuntimeError("V4 quotient is not isomorphic to canonical dodecahedral 15-core")

    gm = nx.algorithms.isomorphism.GraphMatcher(Q15, K15)
    phi = next(gm.isomorphisms_iter())

    print("FIRST 10 V4 FIBERS")
    print("-" * 80)
    for i, orb in enumerate(orbits[:10]):
        print(f"{i:2d} -> {orb}")
    print()

    print("QUOTIENT -> OPPOSITE-EDGE-CLASS MAP")
    print("-" * 80)
    for i in range(15):
        print(f"{i:2d} -> {opposite_pairs[phi[i]]}")
    print()

    print("QUOTIENT ADJACENCY")
    print("-" * 80)
    qadj = quotient_adjacency_table(Q15)
    for i in range(15):
        print(f"{i:2d} -> {qadj[i]}")
    print()

    # Lift fibers annotated by canonical opposite-edge class
    annotated_fibers = []
    for i, orb in enumerate(orbits):
        annotated_fibers.append({
            "fiber_id": i,
            "upstairs_vertices": orb,
            "canonical_opposite_edge_class": [list(e) for e in opposite_pairs[phi[i]]],
        })

    out_dir = ROOT / "reports" / "true_quotients"
    out_dir.mkdir(parents=True, exist_ok=True)

    txt_path = out_dir / "compare_v4_quotient_to_canonical_dodecahedral_15core.txt"
    json_path = out_dir / "compare_v4_quotient_to_canonical_dodecahedral_15core.json"

    lines = [
        "=" * 80,
        "COMPARE V4 QUOTIENT TO CANONICAL DODECAHEDRAL 15-CORE",
        "=" * 80,
        "",
        "UPSTAIRS G60",
        "-" * 80,
        f"vertices: {G60.number_of_nodes()}",
        f"edges: {G60.number_of_edges()}",
        f"degree set: {sorted(set(dict(G60.degree()).values()))}",
        f"triangles: {triangle_count(G60)}",
        f"diameter: {nx.diameter(G60)}",
        f"shell profile: {shell_profile(G60, 0)}",
        "",
        "V4 QUOTIENT Q15",
        "-" * 80,
        f"vertices: {Q15.number_of_nodes()}",
        f"edges: {Q15.number_of_edges()}",
        f"degree set: {sorted(set(dict(Q15.degree()).values()))}",
        f"triangles: {triangle_count(Q15)}",
        f"diameter: {nx.diameter(Q15)}",
        f"shell profile: {shell_profile(Q15, 0)}",
        "",
        "CANONICAL DODECAHEDRAL 15-CORE K15",
        "-" * 80,
        f"vertices: {K15.number_of_nodes()}",
        f"edges: {K15.number_of_edges()}",
        f"degree set: {sorted(set(dict(K15.degree()).values()))}",
        f"triangles: {triangle_count(K15)}",
        f"diameter: {nx.diameter(K15)}",
        f"shell profile: {shell_profile(K15, 0)}",
        "",
        "ISOMORPHISM TEST",
        "-" * 80,
        f"Q15 ≅ K15: {iso}",
        "",
        "FIRST 10 V4 FIBERS",
        "-" * 80,
    ]

    for i, orb in enumerate(orbits[:10]):
        lines.append(f"{i:2d} -> {orb}")

    lines.extend([
        "",
        "QUOTIENT -> OPPOSITE-EDGE-CLASS MAP",
        "-" * 80,
    ])

    for i in range(15):
        lines.append(f"{i:2d} -> {opposite_pairs[phi[i]]}")

    lines.extend([
        "",
        "QUOTIENT ADJACENCY",
        "-" * 80,
    ])

    for i in range(15):
        lines.append(f"{i:2d} -> {qadj[i]}")

    txt_path.write_text("\n".join(lines), encoding="utf-8")

    payload = {
        "G60_summary": {
            "vertices": G60.number_of_nodes(),
            "edges": G60.number_of_edges(),
            "degree_set": sorted(set(dict(G60.degree()).values())),
            "triangles": triangle_count(G60),
            "diameter": nx.diameter(G60),
            "shell_profile": shell_profile(G60, 0),
        },
        "Q15_summary": {
            "vertices": Q15.number_of_nodes(),
            "edges": Q15.number_of_edges(),
            "degree_set": sorted(set(dict(Q15.degree()).values())),
            "triangles": triangle_count(Q15),
            "diameter": nx.diameter(Q15),
            "shell_profile": shell_profile(Q15, 0),
        },
        "K15_summary": {
            "vertices": K15.number_of_nodes(),
            "edges": K15.number_of_edges(),
            "degree_set": sorted(set(dict(K15.degree()).values())),
            "triangles": triangle_count(K15),
            "diameter": nx.diameter(K15),
            "shell_profile": shell_profile(K15, 0),
        },
        "isomorphic": iso,
        "v4_fibers": [[int(x) for x in orb] for orb in orbits],
        "quotient_to_canonical_opposite_edge_class": {
            int(i): [list(e) for e in opposite_pairs[phi[i]]]
            for i in range(15)
        },
        "quotient_adjacency": {int(k): v for k, v in qadj.items()},
        "annotated_fibers": annotated_fibers,
    }

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"saved {txt_path.relative_to(ROOT)}")
    print(f"saved {json_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
