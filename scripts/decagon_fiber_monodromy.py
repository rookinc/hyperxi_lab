from __future__ import annotations

from collections import deque
from typing import Dict, List, Tuple

# Edge fibers from the verified decagon intersection graph.
# Each simple edge (i,j) carries a 2-element fiber of S-pairs.
EDGE_FIBERS: Dict[Tuple[int, int], Tuple[int, int]] = {
    (0, 1): (0, 57),
    (0, 4): (15, 33),
    (0, 5): (14, 54),
    (0, 6): (5, 48),
    (0, 11): (27, 41),
    (1, 5): (8, 45),
    (1, 6): (29, 44),
    (1, 7): (23, 35),
    (1, 10): (11, 52),
    (2, 3): (1, 58),
    (2, 6): (20, 38),
    (2, 7): (19, 34),
    (2, 9): (10, 53),
    (2, 11): (7, 46),
    (3, 7): (13, 50),
    (3, 8): (28, 40),
    (3, 9): (9, 49),
    (3, 10): (16, 32),
    (4, 5): (2, 59),
    (4, 8): (24, 39),
    (4, 9): (25, 43),
    (4, 11): (12, 51),
    (5, 8): (18, 30),
    (5, 10): (21, 37),
    (6, 7): (3, 55),
    (6, 11): (17, 31),
    (7, 10): (26, 42),
    (8, 9): (4, 56),
    (8, 10): (6, 47),
    (9, 11): (22, 36),
}

# Ordered pair cycles from extract_ordered_decagon_pair_cycles.py
PAIR_CYCLES: Dict[int, List[int]] = {
    0: [0, 14, 15, 41, 48, 57, 54, 33, 27, 5],
    1: [0, 29, 23, 52, 45, 57, 44, 35, 11, 8],
    2: [1, 19, 20, 46, 53, 58, 34, 38, 7, 10],
    3: [1, 9, 28, 32, 50, 58, 49, 40, 16, 13],
    4: [2, 24, 25, 51, 33, 59, 39, 43, 12, 15],
    5: [2, 14, 8, 37, 30, 59, 54, 45, 21, 18],
    6: [3, 29, 5, 31, 38, 55, 44, 48, 17, 20],
    7: [3, 19, 13, 42, 35, 55, 34, 50, 26, 23],
    8: [4, 24, 18, 47, 40, 56, 39, 30, 6, 28],
    9: [4, 9, 10, 36, 43, 56, 49, 53, 22, 25],
    10: [6, 37, 11, 42, 16, 47, 21, 52, 26, 32],
    11: [7, 31, 27, 51, 22, 46, 17, 41, 12, 36],
}


def canon_edge(i: int, j: int) -> Tuple[int, int]:
    return (i, j) if i < j else (j, i)


def adjacency() -> Dict[int, List[int]]:
    adj = {i: [] for i in PAIR_CYCLES}
    for i, j in EDGE_FIBERS:
        adj[i].append(j)
        adj[j].append(i)
    for i in adj:
        adj[i].sort()
    return adj


def edge_positions(decagon: int, edge: Tuple[int, int]) -> Tuple[int, int]:
    cyc = PAIR_CYCLES[decagon]
    a, b = EDGE_FIBERS[edge]
    pa = cyc.index(a)
    pb = cyc.index(b)
    return (pa, pb)


def local_edge_label(decagon: int, edge: Tuple[int, int]) -> Tuple[int, int]:
    cyc = PAIR_CYCLES[decagon]
    a, b = EDGE_FIBERS[edge]
    pa = cyc.index(a)
    pb = cyc.index(b)
    # choose the one encountered first when traversing the cycle forward
    return (a, b) if pa < pb else (b, a)


def compare_edge_orientation(i: int, j: int) -> str:
    e = canon_edge(i, j)
    li = local_edge_label(i, e)
    lj = local_edge_label(j, e)
    if li == lj:
        return "same"
    if li == (lj[1], lj[0]):
        return "swap"
    return "inconsistent"


def triangle_cycles(adj: Dict[int, List[int]]) -> List[Tuple[int, int, int]]:
    tris = set()
    for a in adj:
        na = set(adj[a])
        for b in adj[a]:
            if b <= a:
                continue
            common = na & set(adj[b])
            for c in common:
                if c > b:
                    tris.add((a, b, c))
    return sorted(tris)


def main() -> None:
    adj = adjacency()

    print("=" * 80)
    print("DECAGON FIBER MONODROMY")
    print("=" * 80)

    print("Edge orientation comparisons")
    print("-" * 80)
    same = 0
    swap = 0
    for i, j in sorted(EDGE_FIBERS):
        rel = compare_edge_orientation(i, j)
        print(f"edge ({i:2d},{j:2d}) -> {rel}")
        if rel == "same":
            same += 1
        elif rel == "swap":
            swap += 1

    print()
    print(f"same-oriented edges: {same}")
    print(f"swap-oriented edges: {swap}")

    print()
    print("Triangles in the icosahedral base graph")
    print("-" * 80)
    tris = triangle_cycles(adj)
    for tri in tris:
        a, b, c = tri
        rel_ab = compare_edge_orientation(a, b)
        rel_bc = compare_edge_orientation(b, c)
        rel_ca = compare_edge_orientation(c, a)
        print(f"triangle {tri} -> [{rel_ab}, {rel_bc}, {rel_ca}]")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("This is a first-pass monodromy probe.")
    print("If edge orientations can be made globally consistent, the 2-sheet fiber")
    print("is untwisted. If cycle traversal forces swaps, the edge fiber is twisted.")
    print("This script checks local same/swap behavior using ordered decagon cycles.")
