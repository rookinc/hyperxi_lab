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


def intersection_profile_for_pair(
    adj: Dict[int, Set[int]],
    dist: Dict[int, Dict[int, int]],
    x: int,
    y: int,
) -> Tuple[int, Tuple[Tuple[int, int], ...]]:
    i = dist[x][y]
    counts = Counter()
    for z in adj[y]:
        j = dist[x][z]
        counts[j] += 1
    profile = tuple((j, counts[j]) for j in sorted(counts))
    return i, profile


def intersection_arrays(adj: Dict[int, Set[int]]):
    dist = all_distances(adj)
    diameter = max(max(d.values()) for d in dist.values())

    per_distance_profiles = defaultdict(Counter)

    for x in sorted(adj):
        for y in sorted(adj):
            if x == y:
                continue
            i, profile = intersection_profile_for_pair(adj, dist, x, y)
            per_distance_profiles[i][profile] += 1

    return diameter, per_distance_profiles, dist


def shell_counts(adj: Dict[int, Set[int]], dist: Dict[int, Dict[int, int]]):
    out = {}
    for x in sorted(adj):
        c = Counter(dist[x].values())
        out[x] = tuple(c[k] for k in sorted(c))
    return out


def main():
    adj = measured_graph_reindexed()
    diameter, per_distance_profiles, dist = intersection_arrays(adj)
    shells = shell_counts(adj, dist)

    print("=" * 80)
    print("DISTANCE-REGULAR TESTS")
    print("=" * 80)
    print(f"vertices: {len(adj)}")
    print(f"diameter: {diameter}")

    print()
    print("Shell count classes")
    print("-" * 80)
    shell_classes = Counter(shells.values())
    print(f"number of shell-count classes: {len(shell_classes)}")
    for sig, count in sorted(shell_classes.items()):
        print(f"{sig}: {count}")

    print()
    print("Intersection-profile classes by pair distance")
    print("-" * 80)
    for i in range(1, diameter + 1):
        profiles = per_distance_profiles[i]
        print(f"distance {i}: {len(profiles)} profile class(es)")
        for prof, count in sorted(profiles.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"  count={count} profile={prof}")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("A distance-regular graph has exactly one intersection profile for")
    print("each pair distance i. If every pair-distance profile collapses to")
    print("a single class, that is strong evidence the graph is distance-regular.")


if __name__ == "__main__":
    main()
