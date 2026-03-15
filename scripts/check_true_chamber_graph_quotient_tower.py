#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from collections import Counter

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT / "scripts"))

from build_true_chamber_graph_from_flags import build_true_chamber_graph


def shell_profile(G: nx.Graph, src: int = 0) -> tuple[int, ...]:
    d = nx.single_source_shortest_path_length(G, src)
    c = Counter(d.values())
    return tuple(c[k] for k in range(max(c) + 1))


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


def quotient_by_pairs(G: nx.Graph, pair_map: dict[int, int]):
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


def main() -> None:
    print("=" * 80)
    print("CHECK TRUE CHAMBER GRAPH QUOTIENT TOWER")
    print("=" * 80)

    G60, _, _, _ = build_true_chamber_graph()

    a60 = antipode_map(G60)
    G30, classes30, _ = quotient_by_pairs(G60, a60)

    a30 = antipode_map(G30)
    G15, classes15, _ = quotient_by_pairs(G30, a30)

    P = nx.petersen_graph()
    LP = nx.line_graph(P)
    D = nx.dodecahedral_graph()
    LD = nx.line_graph(D)

    for name, G in [("G60", G60), ("G30", G30), ("G15", G15)]:
        print(name)
        print("-" * 80)
        print("vertices:", G.number_of_nodes())
        print("edges:", G.number_of_edges())
        print("degree set:", sorted(set(dict(G.degree()).values())))
        print("connected:", nx.is_connected(G))
        print("triangles:", triangle_count(G))
        print("diameter:", nx.diameter(G))
        print("shell profile from 0:", shell_profile(G, 0))
        print()

    print("IDENTIFICATIONS")
    print("-" * 80)
    print("G30 ≅ line_graph(dodecahedron):", nx.is_isomorphic(G30, LD))
    print("G15 ≅ line_graph(Petersen):   ", nx.is_isomorphic(G15, LP))
    print()

    print("FIRST 15 G30 CLASSES")
    print("-" * 80)
    for i, pair in enumerate(classes30[:15]):
        print(f"{i:2d} -> {pair}")
    print()

    print("ALL G15 CLASSES")
    print("-" * 80)
    for i, pair in enumerate(classes15):
        print(f"{i:2d} -> {pair}")

    out_dir = ROOT / "reports" / "true_quotients"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "check_true_chamber_graph_quotient_tower.txt"

    lines = [
        "=" * 80,
        "CHECK TRUE CHAMBER GRAPH QUOTIENT TOWER",
        "=" * 80,
        "",
    ]

    for name, G in [("G60", G60), ("G30", G30), ("G15", G15)]:
        lines.extend([
            name,
            "-" * 80,
            f"vertices: {G.number_of_nodes()}",
            f"edges: {G.number_of_edges()}",
            f"degree set: {sorted(set(dict(G.degree()).values()))}",
            f"connected: {nx.is_connected(G)}",
            f"triangles: {triangle_count(G)}",
            f"diameter: {nx.diameter(G)}",
            f"shell profile from 0: {shell_profile(G, 0)}",
            "",
        ])

    lines.extend([
        "IDENTIFICATIONS",
        "-" * 80,
        f"G30 ≅ line_graph(dodecahedron): {nx.is_isomorphic(G30, LD)}",
        f"G15 ≅ line_graph(Petersen):    {nx.is_isomorphic(G15, LP)}",
        "",
        "FIRST 15 G30 CLASSES",
        "-" * 80,
    ])

    for i, pair in enumerate(classes30[:15]):
        lines.append(f"{i:2d} -> {pair}")

    lines.extend([
        "",
        "ALL G15 CLASSES",
        "-" * 80,
    ])

    for i, pair in enumerate(classes15):
        lines.append(f"{i:2d} -> {pair}")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print()
    print(f"saved {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
