#!/usr/bin/env python3
"""
Compare Candidate_C from flag geometry directly to the canonical Thalean graph
loaded from spec/thalion_graph.v1.json.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Set, Tuple

import networkx as nx

# ensure scripts directory is importable
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from load_thalean_graph import load_spec, build_graph

Face = int
Slot = int
Side = int
Flag = Tuple[Face, Slot, Side]
Chamber = Tuple[Face, Slot]

MOD = 5

FACE_CYCLES: Dict[Face, List[Face]] = {
    0:  [3, 5, 7, 9, 11],
    1:  [2, 4, 6, 8, 10],
    2:  [1, 4, 3, 11, 10],
    4:  [1, 6, 5, 3, 2],
    6:  [1, 8, 7, 5, 4],
    8:  [1, 10, 9, 7, 6],
    10: [1, 2, 11, 9, 8],
    3:  [0, 11, 2, 4, 5],
    5:  [0, 3, 4, 6, 7],
    7:  [0, 5, 6, 8, 9],
    9:  [0, 7, 8, 10, 11],
    11: [0, 9, 10, 2, 3],
}

FACES = sorted(FACE_CYCLES.keys())

EDGE_BACKREF: Dict[Tuple[Face, Slot], Tuple[Face, Slot]] = {}
for f, cyc in FACE_CYCLES.items():
    for k, g in enumerate(cyc):
        j = FACE_CYCLES[g].index(f)
        EDGE_BACKREF[(f, k)] = (g, j)


def chamber_of(flag: Flag) -> Chamber:
    f, k, _ = flag
    return (f, k)


def s0(flag: Flag) -> Flag:
    f, k, side = flag
    return (f, k, 1 - side)


def s1(flag: Flag) -> Flag:
    f, k, side = flag
    if side == 0:
        return (f, (k - 1) % MOD, 1)
    return (f, (k + 1) % MOD, 0)


def s2(flag: Flag) -> Flag:
    f, k, side = flag
    g, j = EDGE_BACKREF[(f, k)]
    return (g, j, 1 - side)


OPS: Dict[str, Callable[[Flag], Flag]] = {
    "s0": s0,
    "s1": s1,
    "s2": s2,
}


def apply_word(flag: Flag, word: Iterable[str]) -> Flag:
    x = flag
    for op_name in word:
        x = OPS[op_name](x)
    return x


CHAMBERS: List[Chamber] = [(f, k) for f in FACES for k in range(5)]


def reps(ch: Chamber) -> Tuple[Flag, Flag]:
    f, k = ch
    return (f, k, 0), (f, k, 1)


def branch(ch: Chamber, word: Iterable[str]) -> Set[Chamber]:
    return {chamber_of(apply_word(r, word)) for r in reps(ch)}


def move_s2s1(ch: Chamber) -> Set[Chamber]:
    return branch(ch, ["s1", "s2"])


def move_s1s2(ch: Chamber) -> Set[Chamber]:
    return branch(ch, ["s2", "s1"])


def build_candidate_c() -> nx.Graph:
    G = nx.Graph()
    G.add_nodes_from(CHAMBERS)

    for ch in CHAMBERS:
        nbrs = set()
        nbrs |= move_s2s1(ch)
        nbrs |= move_s1s2(ch)
        nbrs.discard(ch)

        for nb in nbrs:
            G.add_edge(ch, nb)

    return G


def invariants(G: nx.Graph) -> dict:
    triangles = sum(nx.triangles(G).values()) // 3
    diam = nx.diameter(G) if nx.is_connected(G) else None
    degree_set = sorted({d for _, d in G.degree()})

    return {
        "vertices": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "degree_set": degree_set,
        "connected": nx.is_connected(G),
        "triangles": triangles,
        "diameter": diam,
    }


def main():

    candidate = build_candidate_c()

    spec = load_spec()
    canonical = build_graph(spec)

    print("=" * 72)
    print("FLAG CANDIDATE C vs CANONICAL THALEAN GRAPH")
    print("=" * 72)

    print()
    print("CANDIDATE C")
    for k, v in invariants(candidate).items():
        print(f"{k:>10}: {v}")

    print()
    print("CANONICAL")
    for k, v in invariants(canonical).items():
        print(f"{k:>10}: {v}")

    print()
    print("=" * 72)
    print("ISOMORPHISM TEST")
    print("=" * 72)

    iso = nx.is_isomorphic(candidate, canonical)

    print("isomorphic:", iso)

    if iso:

        gm = nx.algorithms.isomorphism.GraphMatcher(candidate, canonical)
        mapping = next(gm.isomorphisms_iter())

        outdir = Path("artifacts/reports/flag_compare")
        outdir.mkdir(parents=True, exist_ok=True)

        mapping_path = outdir / "candidate_c_to_canonical_mapping.txt"

        with mapping_path.open("w") as f:
            for chamber, node in sorted(mapping.items(), key=lambda x: x[1]):
                f.write(f"{chamber[0]}:{chamber[1]} -> {node}\n")

        print()
        print("sample mapping entries:")
        preview = list(mapping.items())[:10]

        for left, right in preview:
            print(f"  {left} -> {right}")

        print()
        print("saved full mapping:", mapping_path)


if __name__ == "__main__":
    main()
