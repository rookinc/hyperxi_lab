from __future__ import annotations

from collections import Counter, defaultdict, deque
from typing import Dict, Set

from vertex_connection_model import measured_graph_reindexed
from reconstruct_vertex_connection import pair_to_edge_sheet


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
    return i, tuple((k, counts[k]) for k in sorted(counts))


def fiber_meta():
    """
    node -> (base_edge, sheet)
    in the reindexed 60-state model
    """
    p2es = pair_to_edge_sheet()
    edges = sorted({e for e, _ in p2es.values()})
    edge_to_idx = {e: idx for idx, e in enumerate(edges)}

    out = {}
    for pair_id, (e, s) in p2es.items():
        node = 2 * edge_to_idx[e] + s
        out[node] = (e, s)
    return out


def main():
    adj = measured_graph_reindexed()
    dist = all_distances(adj)
    meta = fiber_meta()

    classes = defaultdict(list)

    for x in sorted(adj):
        for y in sorted(adj):
            if x >= y:
                continue
            d, prof = pair_profile(adj, dist, x, y)
            if d in (4, 5):
                classes[(d, prof)].append((x, y))

    print("=" * 80)
    print("DISTANCE CLASS SPLIT")
    print("=" * 80)

    for key in sorted(classes.keys(), key=lambda k: (k[0], k[1])):
        d, prof = key
        pairs = classes[key]

        print(f"distance {d} profile {prof} -> {len(pairs)} unordered pairs")

        same_sheet = 0
        diff_sheet = 0
        same_base_edge = 0
        share_base_vertex = 0
        base_disjoint = 0

        for x, y in pairs:
            ex, sx = meta[x]
            ey, sy = meta[y]

            if sx == sy:
                same_sheet += 1
            else:
                diff_sheet += 1

            if ex == ey:
                same_base_edge += 1
            elif len(set(ex) & set(ey)) == 1:
                share_base_vertex += 1
            else:
                base_disjoint += 1

        print(f"  same sheet:        {same_sheet}")
        print(f"  different sheet:   {diff_sheet}")
        print(f"  same base edge:    {same_base_edge}")
        print(f"  share base vertex: {share_base_vertex}")
        print(f"  base disjoint:     {base_disjoint}")

        print("  first 12 samples:")
        for x, y in pairs[:12]:
            ex, sx = meta[x]
            ey, sy = meta[y]
            print(f"    ({x:2d},{y:2d}) -> {ex}/s{sx}  vs  {ey}/s{sy}")
        print()

    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("This isolates the two pair classes at distances 4 and 5 and records")
    print("how they differ in terms of the underlying base-edge geometry and")
    print("sheet labels in the binary edge fiber.")


if __name__ == "__main__":
    main()
