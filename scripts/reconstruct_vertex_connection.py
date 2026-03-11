from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple

# Verified icosahedral base graph on decagons
BASE_ADJ: Dict[int, List[int]] = {
    0: [1, 4, 5, 6, 11],
    1: [0, 5, 6, 7, 10],
    2: [3, 6, 7, 9, 11],
    3: [2, 7, 8, 9, 10],
    4: [0, 5, 8, 9, 11],
    5: [0, 1, 4, 8, 10],
    6: [0, 1, 2, 7, 11],
    7: [1, 2, 3, 6, 10],
    8: [3, 4, 5, 9, 10],
    9: [2, 3, 4, 8, 11],
    10: [1, 3, 5, 7, 8],
    11: [0, 2, 4, 6, 9],
}

# Each base edge carries a 2-element S-pair fiber
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

# Ordered pair cycles from the measured chamber
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


def canon(i: int, j: int) -> Tuple[int, int]:
    return (i, j) if i < j else (j, i)


def measured_pair_graph() -> Dict[int, Set[int]]:
    adj = defaultdict(set)
    for cyc in PAIR_CYCLES.values():
        n = len(cyc)
        for k in range(n):
            a = cyc[k]
            b = cyc[(k + 1) % n]
            adj[a].add(b)
            adj[b].add(a)
    return {k: set(v) for k, v in adj.items()}


def pair_to_edge_sheet() -> Dict[int, Tuple[Tuple[int, int], int]]:
    out = {}
    for e, fib in EDGE_FIBERS.items():
        a, b = fib
        out[a] = (e, 0)
        out[b] = (e, 1)
    return out


def local_vertex_edges(v: int) -> List[Tuple[int, int]]:
    return [canon(v, u) for u in BASE_ADJ[v]]


def main() -> None:
    adj = measured_pair_graph()
    p2es = pair_to_edge_sheet()

    print("=" * 80)
    print("RECONSTRUCT VERTEX CONNECTION")
    print("=" * 80)

    global_profile = Counter()

    for v in sorted(BASE_ADJ):
        inc_edges = local_vertex_edges(v)

        print(f"base vertex {v}: incident edges {inc_edges}")

        for i, e1 in enumerate(inc_edges):
            for e2 in inc_edges[i + 1:]:
                a0, a1 = EDGE_FIBERS[e1]
                b0, b1 = EDGE_FIBERS[e2]

                local_hits = []
                for x in (a0, a1):
                    for y in (b0, b1):
                        if y in adj[x]:
                            sx = p2es[x][1]
                            sy = p2es[y][1]
                            local_hits.append((x, y, sx, sy))

                if local_hits:
                    pattern = tuple(sorted((sx, sy) for _, _, sx, sy in local_hits))
                    global_profile[pattern] += 1

                    print(f"  edge-pair {e1} <-> {e2}")
                    for x, y, sx, sy in local_hits:
                        print(f"    pair {x} (sheet {sx}) -- pair {y} (sheet {sy})")

        print()

    print("=" * 80)
    print("GLOBAL TRANSITION PATTERN COUNTS")
    print("=" * 80)
    for pat, count in sorted(global_profile.items(), key=lambda kv: (len(kv[0]), kv[0])):
        print(f"{pat}: {count}")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("This reconstructs how the measured 60-state pair graph couples")
    print("sheet states on incident base edges around each icosahedral vertex.")
    print("If the chamber transport were only a plain edge-double, these local")
    print("transition patterns would be trivial. Repeated nontrivial patterns show")
    print("that ordered Petrie transport carries an additional vertex connection.")


if __name__ == "__main__":
    main()
