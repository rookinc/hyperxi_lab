#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from collections import Counter
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


def graph6_string(G: nx.Graph) -> str:
    return nx.to_graph6_bytes(G, header=False).decode().strip()


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


def edge_list(G: nx.Graph) -> list[list[int]]:
    return [list(e) for e in sorted((min(u, v), max(u, v)) for u, v in G.edges())]


def adjacency_table(G: nx.Graph) -> dict[int, list[int]]:
    return {int(v): sorted(G.neighbors(v)) for v in sorted(G.nodes())}


def permutation_cycles(p: dict[int, int]) -> list[list[int]]:
    seen = set()
    cycles = []

    for v in sorted(p):
        if v in seen or p[v] == v:
            continue
        cyc = []
        cur = v
        while cur not in seen:
            seen.add(cur)
            cyc.append(cur)
            cur = p[cur]
        if len(cyc) > 1:
            cycles.append(cyc)

    return cycles


def cycle_string(cycles: list[list[int]]) -> str:
    if not cycles:
        return "()"
    return "".join("(" + " ".join(str(x) for x in cyc) + ")" for cyc in cycles)


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


def main():
    print("=" * 80)
    print("EXPORT THALEAN GRAPH DEFINITION")
    print("=" * 80)

    G = build_graph(load_spec())
    a = antipode_map(G)
    autos = automorphisms(G)
    b, orbits = find_second_involution(G, a, autos)
    Q15, owner = quotient_by_orbits(G, orbits)

    print("GRAPH SUMMARY")
    print("-" * 80)
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted(set(dict(G.degree()).values())))
    print("triangles:", triangle_count(G))
    print("diameter:", nx.diameter(G))
    print("shell profile from 0:", shell_profile(G, 0))
    print("automorphism count:", len(autos))
    print("graph6:", graph6_string(G))
    print()

    print("INVOLUTIONS")
    print("-" * 80)
    print("a involution:", is_involution(a), "fixed points:", len(fixed_points(a)))
    print("b involution:", is_involution(b), "fixed points:", len(fixed_points(b)))
    print("a,b commute:", commute(a, b))
    print("a cycles:", cycle_string(permutation_cycles(a)))
    print("b cycles:", cycle_string(permutation_cycles(b)))
    print()

    print("FIRST 15 ADJACENCY ROWS")
    print("-" * 80)
    adj = adjacency_table(G)
    for i in range(15):
        print(f"{i:2d} -> {adj[i]}")
    print()

    print("FIRST 10 V4 ORBITS")
    print("-" * 80)
    for i, orb in enumerate(orbits[:10]):
        print(f"{i:2d} -> {orb}")
    print()

    print("QUOTIENT SUMMARY")
    print("-" * 80)
    print("vertices:", Q15.number_of_nodes())
    print("edges:", Q15.number_of_edges())
    print("degree set:", sorted(set(dict(Q15.degree()).values())))
    print("triangles:", triangle_count(Q15))
    print("diameter:", nx.diameter(Q15))
    print("shell profile from 0:", shell_profile(Q15, 0))

    out_dir = ROOT / "reports" / "true_quotients"
    out_dir.mkdir(parents=True, exist_ok=True)

    txt_path = out_dir / "export_thalean_graph_definition.txt"
    json_path = out_dir / "export_thalean_graph_definition.json"
    g6_path = out_dir / "export_thalean_graph_definition.g6"

    lines = [
        "=" * 80,
        "EXPORT THALEAN GRAPH DEFINITION",
        "=" * 80,
        "",
        "GRAPH SUMMARY",
        "-" * 80,
        f"vertices: {G.number_of_nodes()}",
        f"edges: {G.number_of_edges()}",
        f"degree set: {sorted(set(dict(G.degree()).values()))}",
        f"triangles: {triangle_count(G)}",
        f"diameter: {nx.diameter(G)}",
        f"shell profile from 0: {shell_profile(G, 0)}",
        f"automorphism count: {len(autos)}",
        f"graph6: {graph6_string(G)}",
        "",
        "INVOLUTIONS",
        "-" * 80,
        f"a involution: {is_involution(a)} fixed points: {len(fixed_points(a))}",
        f"b involution: {is_involution(b)} fixed points: {len(fixed_points(b))}",
        f"a,b commute: {commute(a, b)}",
        f"a cycles: {cycle_string(permutation_cycles(a))}",
        f"b cycles: {cycle_string(permutation_cycles(b))}",
        "",
        "ADJACENCY TABLE",
        "-" * 80,
    ]

    for i in range(G.number_of_nodes()):
        lines.append(f"{i:2d} -> {adj[i]}")

    lines.extend([
        "",
        "V4 ORBITS",
        "-" * 80,
    ])

    for i, orb in enumerate(orbits):
        lines.append(f"{i:2d} -> {orb}")

    txt_path.write_text("\n".join(lines), encoding="utf-8")

    payload = {
        "summary": {
            "vertices": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "degree_set": sorted(set(dict(G.degree()).values())),
            "triangles": triangle_count(G),
            "diameter": nx.diameter(G),
            "shell_profile": shell_profile(G, 0),
            "automorphism_count": len(autos),
            "graph6": graph6_string(G),
        },
        "adjacency_table": {str(k): v for k, v in adj.items()},
        "edge_list": edge_list(G),
        "a": {str(k): int(v) for k, v in a.items()},
        "b": {str(k): int(v) for k, v in b.items()},
        "a_cycles": permutation_cycles(a),
        "b_cycles": permutation_cycles(b),
        "v4_orbits": orbits,
        "quotient_summary": {
            "vertices": Q15.number_of_nodes(),
            "edges": Q15.number_of_edges(),
            "degree_set": sorted(set(dict(Q15.degree()).values())),
            "triangles": triangle_count(Q15),
            "diameter": nx.diameter(Q15),
            "shell_profile": shell_profile(Q15, 0),
        },
    }

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    g6_path.write_text(graph6_string(G) + "\n", encoding="utf-8")

    print()
    print(f"saved {txt_path.relative_to(ROOT)}")
    print(f"saved {json_path.relative_to(ROOT)}")
    print(f"saved {g6_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
