#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from collections import deque
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


QUOTIENT_WORD = "S"
MOVE_WORDS = ["F", "V"]


def cycle_decomposition(fm: FlagModel, gen: CoxeterGenerators, word: str):
    seen = [False] * fm.num_flags()
    cycles = []

    for start in range(fm.num_flags()):
        if seen[start]:
            continue

        cur = start
        cyc = []
        while not seen[cur]:
            seen[cur] = True
            cyc.append(cur)
            nxt = gen.apply_word(fm.get(cur), word)
            cur = fm.index(nxt)

        cycles.append(tuple(cyc))

    return cycles


def build_owner_map(cycles):
    owner = {}
    for cid, cyc in enumerate(cycles):
        for x in cyc:
            owner[x] = cid
    return owner


def quotient_graph(fm: FlagModel, gen: CoxeterGenerators, quotient_word: str, move_words: list[str]):
    cycles = cycle_decomposition(fm, gen, quotient_word)
    owner = build_owner_map(cycles)

    edge_set = set()

    for cyc in cycles:
        src = owner[cyc[0]]

        for flag_idx in cyc:
            state = fm.get(flag_idx)

            for word in move_words:
                nxt = gen.apply_word(state, word)
                j = fm.index(nxt)
                dst = owner[j]
                if dst == src:
                    continue
                a, b = sorted((src, dst))
                edge_set.add((a, b))

    G = nx.Graph()
    G.add_nodes_from(range(len(cycles)))
    G.add_edges_from(sorted(edge_set))
    return G, cycles


def shell_profile(G: nx.Graph, src: int):
    dist = nx.single_source_shortest_path_length(G, src)
    diam = max(dist.values())
    return tuple(sum(1 for v in dist.values() if v == k) for k in range(diam + 1))


def automorphism_count(G: nx.Graph):
    gm = nx.algorithms.isomorphism.GraphMatcher(G, G)
    count = 0
    for _ in gm.isomorphisms_iter():
        count += 1
    return count


def main():
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    print("=" * 80)
    print("REBUILD TRUE THALION QUOTIENT")
    print("=" * 80)
    print(f"quotient word: {QUOTIENT_WORD}")
    print(f"move words: {MOVE_WORDS}")
    print()

    G, cycles = quotient_graph(fm, gen, QUOTIENT_WORD, MOVE_WORDS)

    cycle_lengths = sorted({len(c) for c in cycles})
    print("upstairs flags:", fm.num_flags())
    print("quotient classes:", len(cycles))
    print("cycle lengths:", cycle_lengths)
    print()

    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted(set(dict(G.degree()).values())))
    print("connected:", nx.is_connected(G))
    print("triangles:", sum(nx.triangles(G).values()) // 3)
    print("diameter:", nx.diameter(G) if nx.is_connected(G) else None)
    print("shell profile from node 0:", shell_profile(G, 0))
    print()

    count = automorphism_count(G)
    print("automorphism group size:", count)
    print()

    out_dir = ROOT / "reports" / "true_quotients"
    out_dir.mkdir(parents=True, exist_ok=True)

    txt_path = out_dir / "true_thalion_quotient.txt"
    g6_path = out_dir / "true_thalion_quotient.g6"

    lines = [
        "=" * 80,
        "REBUILD TRUE THALION QUOTIENT",
        "=" * 80,
        f"quotient word: {QUOTIENT_WORD}",
        f"move words: {MOVE_WORDS}",
        "",
        f"upstairs flags: {fm.num_flags()}",
        f"quotient classes: {len(cycles)}",
        f"cycle lengths: {cycle_lengths}",
        "",
        f"vertices: {G.number_of_nodes()}",
        f"edges: {G.number_of_edges()}",
        f"degree set: {sorted(set(dict(G.degree()).values()))}",
        f"connected: {nx.is_connected(G)}",
        f"triangles: {sum(nx.triangles(G).values()) // 3}",
        f"diameter: {nx.diameter(G) if nx.is_connected(G) else None}",
        f"shell profile from node 0: {shell_profile(G, 0)}",
        "",
        f"automorphism group size: {count}",
        "",
    ]
    txt_path.write_text("\n".join(lines), encoding="utf-8")
    g6_path.write_text(nx.to_graph6_bytes(G, header=False).decode().strip() + "\n", encoding="utf-8")

    print(f"saved {txt_path.relative_to(ROOT)}")
    print(f"saved {g6_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
