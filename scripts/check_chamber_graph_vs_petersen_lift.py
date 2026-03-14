#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


def build_chamber_graph() -> nx.Graph:
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    owner = {}
    classes = []
    seen = set()

    for i in range(fm.num_flags()):
        if i in seen:
            continue
        j = fm.index(gen.S(fm.get(i)))
        cyc = tuple(sorted((i, j)))
        cid = len(classes)
        classes.append(cyc)
        for x in cyc:
            seen.add(x)
            owner[x] = cid

    edges = set()
    for cyc in classes:
        src = owner[cyc[0]]
        for flag_idx in cyc:
            dst_flag = gen.V(fm.get(flag_idx))
            dst = owner[fm.index(dst_flag)]
            if dst != src:
                a, b = sorted((src, dst))
                edges.add((a, b))

    G = nx.Graph()
    G.add_nodes_from(range(len(classes)))
    G.add_edges_from(edges)
    return G


def shell_multiset(G: nx.Graph):
    out = []
    for u in G.nodes():
        dist = nx.single_source_shortest_path_length(G, u)
        diam = max(dist.values())
        prof = tuple(sum(1 for d in dist.values() if d == k) for k in range(diam + 1))
        out.append(prof)
    return sorted(out)


def summarize(name: str, G: nx.Graph):
    print("-" * 80)
    print(name)
    print("-" * 80)
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted(set(dict(G.degree()).values())))
    print("triangles:", sum(nx.triangles(G).values()) // 3)
    print("diameter:", nx.diameter(G))
    vals = sorted(round(float(x), 6) for x in nx.adjacency_spectrum(G).real)
    print("first 10 eigenvalues:", vals[:10])
    print("last 10 eigenvalues:", vals[-10:])


def main():
    print("=" * 80)
    print("CHECK CHAMBER GRAPH VS PETERSEN LIFT")
    print("=" * 80)

    G = build_chamber_graph()
    summarize("HYPERXI CHAMBER GRAPH", G)

    P = nx.petersen_graph()
    LP = nx.line_graph(P)
    C4 = nx.cycle_graph(4)
    H = nx.cartesian_product(LP, C4)

    summarize("L(PETERSEN) □ C4", H)

    print()
    print("=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print("same size:", G.number_of_nodes() == H.number_of_nodes() and G.number_of_edges() == H.number_of_edges())
    print("same shell multiset:", shell_multiset(G) == shell_multiset(H))
    print("isomorphic:", nx.is_isomorphic(G, H))

    out = ROOT / "reports" / "true_quotients" / "check_chamber_graph_vs_petersen_lift.txt"
    lines = [
        "=" * 80,
        "CHECK CHAMBER GRAPH VS PETERSEN LIFT",
        "=" * 80,
        f"same size: {G.number_of_nodes() == H.number_of_nodes() and G.number_of_edges() == H.number_of_edges()}",
        f"same shell multiset: {shell_multiset(G) == shell_multiset(H)}",
        f"isomorphic: {nx.is_isomorphic(G, H)}",
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    print()
    print(f"saved {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
