from __future__ import annotations

from collections import Counter, defaultdict, deque
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


def shell_counts(adj: Dict[int, Set[int]], dist: Dict[int, Dict[int, int]]):
    out = {}
    for x in sorted(adj):
        c = Counter(dist[x].values())
        out[x] = tuple(c[i] for i in range(max(c) + 1))
    return out


def intersection_numbers_for_pair(adj, dist, x, y):
    i = dist[x][y]
    counts = Counter()
    for z in adj[y]:
        counts[dist[x][z]] += 1

    c_i = counts.get(i - 1, 0) if i >= 1 else 0
    a_i = counts.get(i, 0)
    b_i = counts.get(i + 1, 0)
    extras = tuple(sorted((k, v) for k, v in counts.items() if k not in {i - 1, i, i + 1}))
    full = tuple((k, counts[k]) for k in sorted(counts))

    return i, c_i, a_i, b_i, extras, full


def main():
    adj = measured_graph_reindexed()
    dist = all_distances(adj)
    diameter = max(max(d.values()) for d in dist.values())

    print("=" * 80)
    print("INTERSECTION ARRAY CANDIDATE")
    print("=" * 80)
    print(f"vertices: {len(adj)}")
    print(f"diameter: {diameter}")
    print()

    shells = shell_counts(adj, dist)
    shell_classes = Counter(shells.values())
    print("Shell count classes")
    print("-" * 80)
    print(f"classes: {len(shell_classes)}")
    for sig, count in sorted(shell_classes.items()):
        print(f"{sig}: {count}")

    print()
    print("Pair-distance intersection data")
    print("-" * 80)

    by_i = defaultdict(list)

    for x in sorted(adj):
        for y in sorted(adj):
            if x == y:
                continue
            i, c_i, a_i, b_i, extras, full = intersection_numbers_for_pair(adj, dist, x, y)
            by_i[i].append((c_i, a_i, b_i, extras, full))

    intersection_candidate = []

    for i in range(1, diameter + 1):
        counts = Counter((item[0], item[1], item[2], item[3]) for item in by_i[i])
        fulls = Counter(item[4] for item in by_i[i])

        print(f"distance {i}:")
        print(f"  (c_i, a_i, b_i, extras) classes = {len(counts)}")
        for key, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            c_i, a_i, b_i, extras = key
            print(f"    count={count} -> c_{i}={c_i}, a_{i}={a_i}, b_{i}={b_i}, extras={extras}")

        print(f"  full profiles = {len(fulls)}")
        for prof, count in sorted(fulls.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"    count={count} -> {prof}")

        if len(counts) == 1:
            (c_i, a_i, b_i, extras), _ = counts.most_common(1)[0]
            if not extras:
                intersection_candidate.append((i, c_i, a_i, b_i))
            else:
                intersection_candidate.append((i, c_i, a_i, b_i, extras))

    print()
    print("Uniform intersection-array entries")
    print("-" * 80)
    if intersection_candidate:
        for item in intersection_candidate:
            print(item)
    else:
        print("No fully uniform entries found.")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("For a distance-regular graph, each distance i would contribute a single")
    print("uniform triple (c_i, a_i, b_i) with no extras. Any split classes or extras")
    print("mark the precise places where distance-regularity fails.")


if __name__ == "__main__":
    main()
