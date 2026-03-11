from __future__ import annotations

from collections import deque
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


def spanning_tree(adj: Dict[int, List[int]], root: int = 0):
    parent = {root: None}
    order = [root]
    q = deque([root])

    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in parent:
                parent[v] = u
                order.append(v)
                q.append(v)

    tree_edges = set()
    for v, p in parent.items():
        if p is not None:
            tree_edges.add(canon(v, p))
    return parent, tree_edges


def path_to_root(parent: Dict[int, int | None], v: int) -> List[int]:
    out = []
    while v is not None:
        out.append(v)
        v = parent[v]
    return out


def tree_path(parent: Dict[int, int | None], a: int, b: int) -> List[int]:
    pa = path_to_root(parent, a)
    pb = path_to_root(parent, b)
    sb = set(pb)

    lca = None
    for x in pa:
        if x in sb:
            lca = x
            break

    out_a = []
    x = a
    while x != lca:
        out_a.append(x)
        x = parent[x]
    out_a.append(lca)

    out_b = []
    x = b
    while x != lca:
        out_b.append(x)
        x = parent[x]

    return out_a + list(reversed(out_b))


def cycle_edges_from_path(path: List[int]) -> List[Tuple[int, int]]:
    return [canon(path[i], path[i + 1]) for i in range(len(path) - 1)]


def main() -> None:
    adj = build_adj()
    parent, tree_edges = spanning_tree(adj, 0)

    all_edges = set(EDGE_REL)
    cotree_edges = sorted(all_edges - tree_edges)

    print("=" * 80)
    print("DECAGON FIBER COCYCLE")
    print("=" * 80)
    print(f"tree edges:   {len(tree_edges)}")
    print(f"cotree edges: {len(cotree_edges)}")
    print()

    odd_cycles = 0

    print("Fundamental cycle parities")
    print("-" * 80)
    for e in cotree_edges:
        a, b = e
        p = tree_path(parent, a, b)
        cyc_edges = cycle_edges_from_path(p) + [e]
        parity = sum(EDGE_REL[x] for x in cyc_edges) % 2
        if parity == 1:
            odd_cycles += 1
        print(f"edge {e} -> cycle {cyc_edges} -> parity {parity}")

    print()
    print(f"odd fundamental cycles: {odd_cycles} / {len(cotree_edges)}")

    print()
    print("Gauge consistency test")
    print("-" * 80)
    gauge = {0: 0}
    q = deque([0])
    consistent = True

    while q and consistent:
        u = q.popleft()
        for v in adj[u]:
            target = gauge[u] ^ edge_value(u, v)
            if v in gauge:
                if gauge[v] != target:
                    consistent = False
                    print(f"conflict on edge {(u, v)}: existing {gauge[v]}, required {target}")
                    break
            else:
                gauge[v] = target
                q.append(v)

    print(f"global gauge solution exists: {consistent}")
    if consistent:
        print("bundle is untwisted / cocycle exact")
    else:
        print("bundle is twisted / cocycle non-exact")


if __name__ == "__main__":
    main()
