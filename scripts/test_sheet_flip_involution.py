from __future__ import annotations

from collections import Counter, deque
from typing import Dict, Set, Tuple

from vertex_connection_model import measured_graph_reindexed


def bfs_distances(adj: Dict[int, Set[int]], s: int) -> Dict[int, int]:
    dist = {s: 0}
    q = deque([s])
    while q:
        v = q.popleft()
        for w in adj[v]:
            if w not in dist:
                dist[w] = dist[v] + 1
                q.append(w)
    return dist


def all_distances(adj: Dict[int, Set[int]]) -> Dict[int, Dict[int, int]]:
    return {v: bfs_distances(adj, v) for v in adj}


def pair_profile(adj: Dict[int, Set[int]], dist: Dict[int, Dict[int, int]], x: int, y: int):
    i = dist[x][y]
    counts = Counter()
    for z in adj[y]:
        counts[dist[x][z]] += 1
    prof = tuple((k, counts[k]) for k in sorted(counts))
    return i, prof


def edge_set(adj: Dict[int, Set[int]]) -> Set[Tuple[int, int]]:
    out = set()
    for u in adj:
        for v in adj[u]:
            if u < v:
                out.add((u, v))
    return out


def main():
    adj = measured_graph_reindexed()
    dist = all_distances(adj)

    print("=" * 80)
    print("SHEET-FLIP INVOLUTION TEST")
    print("=" * 80)

    target_pairs = []
    for x in sorted(adj):
        for y in sorted(adj):
            if x >= y:
                continue
            d, prof = pair_profile(adj, dist, x, y)
            if d == 5 and prof == ((4, 4),):
                target_pairs.append((x, y))

    print(f"candidate distance-5 (4,4) pairs: {len(target_pairs)}")
    print(f"first 20 pairs: {target_pairs[:20]}")
    print()

    deg = Counter()
    for x, y in target_pairs:
        deg[x] += 1
        deg[y] += 1

    counts = Counter(deg.values())
    print("vertex participation counts in candidate pairs")
    print("-" * 80)
    print(dict(sorted(counts.items())))

    missing = [v for v in sorted(adj) if v not in deg]
    if missing:
        print(f"missing vertices: {missing}")
    else:
        print("all vertices appear in the candidate pair set")

    is_perfect_matching = (
        len(target_pairs) * 2 == len(adj)
        and all(deg[v] == 1 for v in adj)
    )

    print()
    print(f"perfect matching: {is_perfect_matching}")

    if not is_perfect_matching:
        print()
        print("=" * 80)
        print("INTERPRETATION")
        print("=" * 80)
        print("The special distance-5 class does not define a unique global")
        print("sheet-flip involution by itself.")
        return

    tau = {}
    for x, y in target_pairs:
        tau[x] = y
        tau[y] = x

    print()
    print("involution checks")
    print("-" * 80)
    print("fixed points:", [v for v in sorted(adj) if tau[v] == v][:10])
    print("tau^2=id:", all(tau[tau[v]] == v for v in adj))

    adjacency_ok = True
    bad = []
    for u in adj:
        lhs = {tau[v] for v in adj[u]}
        rhs = adj[tau[u]]
        if lhs != rhs:
            adjacency_ok = False
            bad.append(u)
            if len(bad) >= 10:
                break

    print("adjacency preserved:", adjacency_ok)
    if not adjacency_ok:
        print("first bad vertices:", bad)

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    if adjacency_ok:
        print("The distance-5 (4,4) class defines a fixed-point-free involution")
        print("that preserves adjacency. This is strong evidence for a genuine")
        print("2-sheet covering structure.")
    else:
        print("The distance-5 (4,4) class gives a perfect matching, but not a")
        print("graph involution. The binary fiber exists combinatorially, but")
        print("its transport action is more subtle than a simple global flip.")


if __name__ == "__main__":
    main()
