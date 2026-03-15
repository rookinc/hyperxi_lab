#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from collections import Counter, defaultdict
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


def quotient_adjacency_table(Q: nx.Graph) -> dict[int, list[int]]:
    return {v: sorted(Q.neighbors(v)) for v in sorted(Q.nodes())}


def fiber_neighbor_lifts(G: nx.Graph, owner: dict[int, int], Q: nx.Graph, sample_limit: int = 10):
    rows = []
    for u in sorted(G.nodes())[:sample_limit]:
        qu = owner[u]
        grouped = defaultdict(list)
        for v in sorted(G.neighbors(u)):
            grouped[owner[v]].append(v)
        rows.append({
            "upstairs_vertex": u,
            "fiber": qu,
            "downstairs_neighbors": sorted(Q.neighbors(qu)),
            "lifted_neighbor_groups": {k: grouped[k] for k in sorted(grouped)},
        })
    return rows


def explicit_line_graph_petersen_isomorphism(Q15: nx.Graph):
    P = nx.petersen_graph()
    LP = nx.line_graph(P)
    gm = nx.algorithms.isomorphism.GraphMatcher(Q15, LP)
    ok = gm.is_isomorphic()
    if not ok:
        raise RuntimeError("Quotient is not isomorphic to L(Petersen)")
    phi = next(gm.isomorphisms_iter())
    # normalize target edges as sorted tuples
    norm_phi = {int(k): tuple(sorted(v)) for k, v in phi.items()}
    return LP, norm_phi


def main():
    print("=" * 80)
    print("EXPORT V4 COVER CERTIFICATE")
    print("=" * 80)

    G60 = build_graph(load_spec())
    a = antipode_map(G60)
    autos = automorphisms(G60)
    b, orbits = find_second_involution(G60, a, autos)
    Q15, owner = quotient_by_orbits(G60, orbits)
    ok_cover, witness = covering_test(G60, Q15, owner)
    LP, phi = explicit_line_graph_petersen_isomorphism(Q15)

    print("G60 SUMMARY")
    print("-" * 80)
    print("vertices:", G60.number_of_nodes())
    print("edges:", G60.number_of_edges())
    print("degree set:", sorted(set(dict(G60.degree()).values())))
    print("triangles:", triangle_count(G60))
    print("diameter:", nx.diameter(G60))
    print("shell profile:", shell_profile(G60, 0))
    print()

    print("V4 DATA")
    print("-" * 80)
    print("a involution:", is_involution(a), "fixed points:", len(fixed_points(a)))
    print("b involution:", is_involution(b), "fixed points:", len(fixed_points(b)))
    print("a,b commute:", commute(a, b))
    print("orbit count:", len(orbits))
    print("orbit size histogram:", dict(sorted(Counter(len(o) for o in orbits).items())))
    print()

    print("QUOTIENT SUMMARY")
    print("-" * 80)
    print("vertices:", Q15.number_of_nodes())
    print("edges:", Q15.number_of_edges())
    print("degree set:", sorted(set(dict(Q15.degree()).values())))
    print("triangles:", triangle_count(Q15))
    print("diameter:", nx.diameter(Q15))
    print("shell profile:", shell_profile(Q15, 0))
    print("isomorphic to L(Petersen):", nx.is_isomorphic(Q15, LP))
    print("covering projection:", ok_cover)
    if witness is not None:
        print("covering witness:", witness)
    print()

    print("FIRST 10 ORBITS")
    print("-" * 80)
    for i, orb in enumerate(orbits[:10]):
        print(f"{i:2d} -> {orb}")
    print()

    print("QUOTIENT ADJACENCY")
    print("-" * 80)
    qadj = quotient_adjacency_table(Q15)
    for i in range(15):
        print(f"{i:2d} -> {qadj[i]}")
    print()

    print("ISOMORPHISM TO L(PETERSEN))")
    print("-" * 80)
    for i in range(15):
        print(f"{i:2d} -> {phi[i]}")
    print()

    print("FIRST 10 FIBER LIFT CHECKS")
    print("-" * 80)
    lift_rows = fiber_neighbor_lifts(G60, owner, Q15, sample_limit=10)
    for row in lift_rows:
        print(row)

    out_dir = ROOT / "reports" / "true_quotients"
    out_dir.mkdir(parents=True, exist_ok=True)

    txt_path = out_dir / "export_v4_cover_certificate.txt"
    json_path = out_dir / "export_v4_cover_certificate.json"

    lines = [
        "=" * 80,
        "EXPORT V4 COVER CERTIFICATE",
        "=" * 80,
        "",
        "G60 SUMMARY",
        "-" * 80,
        f"vertices: {G60.number_of_nodes()}",
        f"edges: {G60.number_of_edges()}",
        f"degree set: {sorted(set(dict(G60.degree()).values()))}",
        f"triangles: {triangle_count(G60)}",
        f"diameter: {nx.diameter(G60)}",
        f"shell profile: {shell_profile(G60, 0)}",
        "",
        "V4 DATA",
        "-" * 80,
        f"a involution: {is_involution(a)} fixed points: {len(fixed_points(a))}",
        f"b involution: {is_involution(b)} fixed points: {len(fixed_points(b))}",
        f"a,b commute: {commute(a, b)}",
        f"orbit count: {len(orbits)}",
        f"orbit size histogram: {dict(sorted(Counter(len(o) for o in orbits).items()))}",
        "",
        "FIRST 10 ORBITS",
        "-" * 80,
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
        f"shell profile: {shell_profile(Q15, 0)}",
        f"isomorphic to L(Petersen): {nx.is_isomorphic(Q15, LP)}",
        f"covering projection: {ok_cover}",
    ])

    if witness is not None:
        lines.append(f"covering witness: {witness}")

    lines.extend([
        "",
        "QUOTIENT ADJACENCY",
        "-" * 80,
    ])

    for i in range(15):
        lines.append(f"{i:2d} -> {qadj[i]}")

    lines.extend([
        "",
        "ISOMORPHISM TO L(PETERSEN)",
        "-" * 80,
    ])

    for i in range(15):
        lines.append(f"{i:2d} -> {phi[i]}")

    lines.extend([
        "",
        "FIRST 10 FIBER LIFT CHECKS",
        "-" * 80,
    ])

    for row in lift_rows:
        lines.append(str(row))

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
        "a": {int(k): int(v) for k, v in a.items()},
        "b": {int(k): int(v) for k, v in b.items()},
        "orbits": [[int(x) for x in orb] for orb in orbits],
        "Q15_summary": {
            "vertices": Q15.number_of_nodes(),
            "edges": Q15.number_of_edges(),
            "degree_set": sorted(set(dict(Q15.degree()).values())),
            "triangles": triangle_count(Q15),
            "diameter": nx.diameter(Q15),
            "shell_profile": shell_profile(Q15, 0),
            "isomorphic_to_line_graph_petersen": nx.is_isomorphic(Q15, LP),
            "covering_projection": ok_cover,
        },
        "quotient_adjacency": {int(k): v for k, v in qadj.items()},
        "quotient_to_line_graph_petersen": {int(k): list(v) for k, v in phi.items()},
        "fiber_lift_checks_first_10": lift_rows,
    }

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print()
    print(f"saved {txt_path.relative_to(ROOT)}")
    print(f"saved {json_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
