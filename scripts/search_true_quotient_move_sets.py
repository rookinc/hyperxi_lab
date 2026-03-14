#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from itertools import combinations
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


QUOTIENT_WORD = "S"

CANDIDATE_WORDS = [
    "F",
    "V",
    "FF",
    "FV",
    "VF",
    "VV",
    "FFF",
    "FFV",
    "FVF",
    "FVV",
    "VFF",
    "VFV",
    "VVF",
    "VVV",
    "FS",
    "SF",
    "SV",
    "VS",
    "FSV",
    "FVS",
    "SFV",
    "SVF",
    "VFS",
    "VSF",
]


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


def quotient_graph(fm: FlagModel, gen: CoxeterGenerators, quotient_word: str, move_words: tuple[str, ...]):
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


def shell_profile(G: nx.Graph, src: int = 0):
    dist = nx.single_source_shortest_path_length(G, src)
    diam = max(dist.values())
    return tuple(sum(1 for v in dist.values() if v == k) for k in range(diam + 1))


def signature(G: nx.Graph):
    degset = sorted(set(dict(G.degree()).values()))
    tris = sum(nx.triangles(G).values()) // 3
    diam = nx.diameter(G) if nx.is_connected(G) else None
    shell = shell_profile(G, 0) if nx.is_connected(G) else None
    return {
        "vertices": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "degree_set": degset,
        "connected": nx.is_connected(G),
        "triangles": tris,
        "diameter": diam,
        "shell_profile_0": shell,
    }


def main():
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    print("=" * 80)
    print("SEARCH TRUE QUOTIENT MOVE SETS")
    print("=" * 80)
    print(f"quotient word: {QUOTIENT_WORD}")
    print(f"candidate words: {CANDIDATE_WORDS}")
    print()

    out_lines = []
    out_lines.append("=" * 80)
    out_lines.append("SEARCH TRUE QUOTIENT MOVE SETS")
    out_lines.append("=" * 80)
    out_lines.append(f"quotient word: {QUOTIENT_WORD}")
    out_lines.append("")

    hits = []

    for r in (1, 2, 3):
        for move_set in combinations(CANDIDATE_WORDS, r):
            try:
                G, cycles = quotient_graph(fm, gen, QUOTIENT_WORD, move_set)
                sig = signature(G)
            except Exception as e:
                out_lines.append(f"move_set={move_set} ERROR {e}")
                continue

            line = (
                f"move_set={move_set} | "
                f"v={sig['vertices']} e={sig['edges']} deg={sig['degree_set']} "
                f"conn={sig['connected']} tri={sig['triangles']} "
                f"diam={sig['diameter']} shell0={sig['shell_profile_0']}"
            )
            print(line)
            out_lines.append(line)

            if (
                sig["vertices"] == 60
                and sig["edges"] == 120
                and sig["degree_set"] == [4]
            ):
                hits.append((move_set, sig))

    out_dir = ROOT / "reports" / "true_quotients"
    out_dir.mkdir(parents=True, exist_ok=True)
    txt_path = out_dir / "search_true_quotient_move_sets.txt"

    out_lines.append("")
    out_lines.append("=" * 80)
    out_lines.append("HITS FOR (60,120,4)")
    out_lines.append("=" * 80)

    if hits:
        for move_set, sig in hits:
            out_lines.append(
                f"move_set={move_set} | "
                f"tri={sig['triangles']} diam={sig['diameter']} shell0={sig['shell_profile_0']}"
            )
    else:
        out_lines.append("No hits found.")

    txt_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")

    print()
    print("=" * 80)
    print("HITS FOR (60,120,4)")
    print("=" * 80)
    if hits:
        for move_set, sig in hits:
            print(
                f"move_set={move_set} | "
                f"tri={sig['triangles']} diam={sig['diameter']} shell0={sig['shell_profile_0']}"
            )
    else:
        print("No hits found.")

    print()
    print(f"saved {txt_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
