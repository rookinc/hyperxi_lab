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


def build_graph():
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    # quotient by S
    owner = {}
    classes = []
    seen = set()

    for i in range(fm.num_flags()):
        if i in seen:
            continue
        a = i
        b = fm.index(gen.S(fm.get(i)))
        cyc = sorted([a, b])
        for x in cyc:
            seen.add(x)
        idx = len(classes)
        for x in cyc:
            owner[x] = idx
        classes.append(tuple(cyc))

    edges = set()

    for cyc in classes:
        src = owner[cyc[0]]
        for flag_idx in cyc:
            nxt = gen.V(fm.get(flag_idx))
            j = fm.index(nxt)
            dst = owner[j]
            if src != dst:
                a, b = sorted((src, dst))
                edges.add((a, b))

    G = nx.Graph()
    G.add_nodes_from(range(len(classes)))
    G.add_edges_from(edges)

    return G


def shell_profile(G, start=0):
    dist = nx.single_source_shortest_path_length(G, start)
    m = max(dist.values())
    return tuple(sum(1 for v in dist.values() if v == i) for i in range(m + 1))


def main():
    G = build_graph()

    print("=" * 80)
    print("CHAMBER GRAPH FINGERPRINT")
    print("=" * 80)

    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted(set(dict(G.degree()).values())))
    print("triangles:", sum(nx.triangles(G).values()) // 3)
    print("diameter:", nx.diameter(G))
    print("shell profile:", shell_profile(G))

    print()
    print("graph6:")
    print(nx.to_graph6_bytes(G, header=False).decode().strip())


if __name__ == "__main__":
    main()
