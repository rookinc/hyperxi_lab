#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from collections import defaultdict

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


def build_g60_and_fibers():
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    owner60 = {}
    classes60 = []
    seen = set()

    for i in range(fm.num_flags()):
        if i in seen:
            continue
        j = fm.index(gen.S(fm.get(i)))
        cyc = tuple(sorted((i, j)))
        cid = len(classes60)
        classes60.append(cyc)
        for x in cyc:
            seen.add(x)
            owner60[x] = cid

    G60 = nx.Graph()
    G60.add_nodes_from(range(len(classes60)))

    for cyc in classes60:
        src = owner60[cyc[0]]
        for flag_idx in cyc:
            dst_flag = gen.V(fm.get(flag_idx))
            dst = owner60[fm.index(dst_flag)]
            if dst != src:
                a, b = sorted((src, dst))
                G60.add_edge(a, b)

    return G60, classes60


def antipodal_pairs(G: nx.Graph):
    dist = dict(nx.all_pairs_shortest_path_length(G))
    diam = nx.diameter(G)

    pairs = []
    used = set()

    for u in G.nodes():
        if u in used:
            continue
        far = [v for v, d in dist[u].items() if d == diam]
        if len(far) != 1:
            raise RuntimeError(f"Vertex {u} has {len(far)} antipodes at distance {diam}, expected 1.")
        v = far[0]
        if v in used:
            continue
        a, b = sorted((u, v))
        pairs.append((a, b))
        used.add(a)
        used.add(b)

    if len(pairs) * 2 != G.number_of_nodes():
        raise RuntimeError("Antipodal pairing did not cover all vertices.")

    return sorted(pairs), diam


def quotient_graph_and_owner(G: nx.Graph, pairs):
    owner = {}
    for i, (a, b) in enumerate(pairs):
        owner[a] = i
        owner[b] = i

    Q = nx.Graph()
    Q.add_nodes_from(range(len(pairs)))

    multiplicities = defaultdict(int)
    lifts = defaultdict(list)

    for u, v in G.edges():
        a = owner[u]
        b = owner[v]
        if a == b:
            continue
        x, y = sorted((a, b))
        multiplicities[(x, y)] += 1
        lifts[(x, y)].append((u, v))
        Q.add_edge(x, y)

    return Q, owner, multiplicities, lifts


def build_g15_data():
    G60, classes60 = build_g60_and_fibers()

    pairs60, diam60 = antipodal_pairs(G60)
    G30, owner30, mult30, lifts30 = quotient_graph_and_owner(G60, pairs60)

    pairs30, diam30 = antipodal_pairs(G30)
    G15, owner15, mult15, lifts15 = quotient_graph_and_owner(G30, pairs30)

    return {
        "G60": G60,
        "G30": G30,
        "G15": G15,
        "pairs60": pairs60,
        "pairs30": pairs30,
        "owner30": owner30,
        "owner15": owner15,
        "lifts30": lifts30,
        "lifts15": lifts15,
        "diam60": diam60,
        "diam30": diam30,
    }


def classify_signed_lift_for_g30_to_g15(G30, pairs30, owner15):
    fiber_nodes = {}
    for g30_vertex, base in owner15.items():
        fiber_nodes.setdefault(base, []).append(g30_vertex)

    for base, xs in fiber_nodes.items():
        fiber_nodes[base] = sorted(xs)

    edge_rows = []

    for u, v in sorted(nx.Graph([(a, b) for a, b in nx.Graph().edges()]).edges()):
        pass

    G15_edges = set()
    for a in owner15:
        for b in G30.neighbors(a):
            x, y = sorted((owner15[a], owner15[b]))
            if x != y:
                G15_edges.add((x, y))

    for x, y in sorted(G15_edges):
        fx = fiber_nodes[x]
        fy = fiber_nodes[y]

        if len(fx) != 2 or len(fy) != 2:
            raise RuntimeError(f"Expected 2-sheet fibers over G15 edge {(x, y)}, got {fx}, {fy}")

        x0, x1 = fx
        y0, y1 = fy

        present = {
            tuple(sorted((x0, y0))): G30.has_edge(x0, y0),
            tuple(sorted((x0, y1))): G30.has_edge(x0, y1),
            tuple(sorted((x1, y0))): G30.has_edge(x1, y0),
            tuple(sorted((x1, y1))): G30.has_edge(x1, y1),
        }

        parallel = present[tuple(sorted((x0, y0)))] and present[tuple(sorted((x1, y1)))]
        crossed = present[tuple(sorted((x0, y1)))] and present[tuple(sorted((x1, y0)))]

        if parallel and not crossed:
            lift_type = "parallel"
            sign = +1
        elif crossed and not parallel:
            lift_type = "crossed"
            sign = -1
        else:
            raise RuntimeError(
                f"Edge {(x, y)} is not a clean signed 2-lift edge. "
                f"parallel={parallel}, crossed={crossed}, present={present}"
            )

        edge_rows.append(
            {
                "u": x,
                "v": y,
                "fiber_u": fx,
                "fiber_v": fy,
                "lift_type": lift_type,
                "sign": sign,
                "adjacency_pattern": {
                    "u0_v0": present[tuple(sorted((x0, y0)))],
                    "u0_v1": present[tuple(sorted((x0, y1)))],
                    "u1_v0": present[tuple(sorted((x1, y0)))],
                    "u1_v1": present[tuple(sorted((x1, y1)))],
                },
            }
        )

    return edge_rows, fiber_nodes


def main():
    data = build_g15_data()

    G60 = data["G60"]
    G30 = data["G30"]
    G15 = data["G15"]

    rows, fiber_nodes = classify_signed_lift_for_g30_to_g15(
        G30=data["G30"],
        pairs30=data["pairs30"],
        owner15=data["owner15"],
    )

    pos = sum(1 for r in rows if r["sign"] == +1)
    neg = sum(1 for r in rows if r["sign"] == -1)

    out_dir = ROOT / "reports" / "quotients"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "g15_edge_sign_table.json"
    txt_path = out_dir / "g15_edge_sign_table.txt"

    payload = {
        "summary": {
            "G60_vertices": G60.number_of_nodes(),
            "G60_edges": G60.number_of_edges(),
            "G30_vertices": G30.number_of_nodes(),
            "G30_edges": G30.number_of_edges(),
            "G15_vertices": G15.number_of_nodes(),
            "G15_edges": G15.number_of_edges(),
            "positive_edges": pos,
            "negative_edges": neg,
        },
        "fibers_over_G15_vertices": {str(k): v for k, v in sorted(fiber_nodes.items())},
        "edge_rows": rows,
    }

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = []
    lines.append("=" * 80)
    lines.append("G15 EDGE SIGN TABLE")
    lines.append("=" * 80)
    lines.append(f"G60: vertices={G60.number_of_nodes()} edges={G60.number_of_edges()}")
    lines.append(f"G30: vertices={G30.number_of_nodes()} edges={G30.number_of_edges()}")
    lines.append(f"G15: vertices={G15.number_of_nodes()} edges={G15.number_of_edges()}")
    lines.append("")
    lines.append("SIGN COUNTS")
    lines.append("-" * 80)
    lines.append(f"+1 / parallel: {pos}")
    lines.append(f"-1 / crossed : {neg}")
    lines.append("")
    lines.append("FIBERS OVER G15 VERTICES")
    lines.append("-" * 80)
    for k, v in sorted(fiber_nodes.items()):
        lines.append(f"{k:2d} -> {v}")
    lines.append("")
    lines.append("EDGE TABLE")
    lines.append("-" * 80)
    for r in rows:
        lines.append(
            f"({r['u']:2d},{r['v']:2d}) "
            f"fiber_u={r['fiber_u']} fiber_v={r['fiber_v']} "
            f"type={r['lift_type']:8s} sign={r['sign']:>2d} "
            f"pattern={r['adjacency_pattern']}"
        )

    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("=" * 80)
    print("EXPORT G15 SIGNED LIFT TABLE")
    print("=" * 80)
    print(f"G60: {G60.number_of_nodes()} vertices, {G60.number_of_edges()} edges")
    print(f"G30: {G30.number_of_nodes()} vertices, {G30.number_of_edges()} edges")
    print(f"G15: {G15.number_of_nodes()} vertices, {G15.number_of_edges()} edges")
    print()
    print("SIGN COUNTS")
    print("-" * 80)
    print(f"+1 / parallel: {pos}")
    print(f"-1 / crossed : {neg}")
    print()
    print(f"saved {txt_path.relative_to(ROOT)}")
    print(f"saved {json_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
