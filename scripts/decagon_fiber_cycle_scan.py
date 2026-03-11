from __future__ import annotations

from itertools import combinations
from typing import Dict, List, Tuple, Set

EDGE_REL: Dict[Tuple[int, int], int] = {
    (0, 1): 0,
    (0, 4): 1,
    (0, 5): 0,
    (0, 6): 1,
    (0, 11): 1,
    (1, 5): 1,
    (1, 6): 0,
    (1, 7): 1,
    (1, 10): 1,
    (2, 3): 0,
    (2, 6): 1,
    (2, 7): 0,
    (2, 9): 1,
    (2, 11): 1,
    (3, 7): 1,
    (3, 8): 1,
    (3, 9): 0,
    (3, 10): 1,
    (4, 5): 0,
    (4, 8): 0,
    (4, 9): 1,
    (4, 11): 0,
    (5, 8): 1,
    (5, 10): 0,
    (6, 7): 0,
    (6, 11): 0,
    (7, 10): 0,
    (8, 9): 0,
    (8, 10): 1,
    (9, 11): 1,
}


def canon(i: int, j: int) -> Tuple[int, int]:
    return (i, j) if i < j else (j, i)


def build_adj() -> Dict[int, List[int]]:
    adj = {i: [] for i in range(12)}
    for i, j in EDGE_REL:
        adj[i].append(j)
        adj[j].append(i)
    for i in adj:
        adj[i].sort()
    return adj


def edge_value(i: int, j: int) -> int:
    return EDGE_REL[canon(i, j)]


def cycle_parity(cycle: List[int]) -> int:
    total = 0
    n = len(cycle)
    for i in range(n):
        total ^= edge_value(cycle[i], cycle[(i + 1) % n])
    return total


def triangles(adj: Dict[int, List[int]]) -> List[Tuple[int, int, int]]:
    out = set()
    for a in adj:
        sa = set(adj[a])
        for b in adj[a]:
            if b <= a:
                continue
            for c in sa & set(adj[b]):
                if c > b:
                    out.add((a, b, c))
    return sorted(out)


def norm_cycle(cyc: List[int]) -> Tuple[int, ...]:
    rots = []
    n = len(cyc)
    for k in range(n):
        rots.append(tuple(cyc[k:] + cyc[:k]))
    rc = list(reversed(cyc))
    for k in range(n):
        rots.append(tuple(rc[k:] + rc[:k]))
    return min(rots)


def simple_cycles_len5(adj: Dict[int, List[int]]) -> List[Tuple[int, ...]]:
    found: Set[Tuple[int, ...]] = set()

    def dfs(start: int, cur: int, path: List[int], used: Set[int]) -> None:
        if len(path) == 5:
            if start in adj[cur]:
                found.add(norm_cycle(path))
            return
        for nxt in adj[cur]:
            if nxt in used:
                continue
            dfs(start, nxt, path + [nxt], used | {nxt})

    for s in adj:
        dfs(s, s, [s], {s})

    return sorted(found)


def main() -> None:
    adj = build_adj()
    tris = triangles(adj)
    pentas = simple_cycles_len5(adj)

    print("=" * 80)
    print("DECAGON FIBER CYCLE SCAN")
    print("=" * 80)

    print("Triangles")
    print("-" * 80)
    odd_tri = 0
    for tri in tris:
        p = cycle_parity(list(tri))
        if p:
            odd_tri += 1
        print(f"{tri} -> parity {p}")
    print(f"odd triangles: {odd_tri} / {len(tris)}")

    print()
    print("5-cycles")
    print("-" * 80)
    odd_penta = 0
    for cyc in pentas:
        p = cycle_parity(list(cyc))
        if p:
            odd_penta += 1
        print(f"{cyc} -> parity {p}")
    print(f"odd 5-cycles: {odd_penta} / {len(pentas)}")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("Parity 1 means the binary fiber picks up a swap around the cycle.")
    print("This identifies where the nontrivial Z2 holonomy is geometrically supported.")


if __name__ == "__main__":
    main()
