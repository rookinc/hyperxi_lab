from __future__ import annotations

from collections import Counter, defaultdict, deque
from typing import Dict, Set

import numpy as np

# reuse the chamber reconstruction
from vertex_connection_model import measured_graph_reindexed


def edge_set(adj):
    out = set()
    for u, nbrs in adj.items():
        for v in nbrs:
            if u < v:
                out.add((u, v))
    return out


def diameter(adj: Dict[int, Set[int]]):
    nodes = list(adj.keys())
    best = 0
    dist_profile = Counter()

    for s in nodes:
        seen = {s}
        q = deque([(s, 0)])

        while q:
            v, d = q.popleft()
            dist_profile[d] += 1
            best = max(best, d)

            for w in adj[v]:
                if w not in seen:
                    seen.add(w)
                    q.append((w, d + 1))

    return best, dist_profile


def girth(adj):
    nodes = list(adj.keys())
    best = float("inf")

    for s in nodes:
        q = deque([(s, -1, 0)])
        seen = {s: 0}

        while q:
            v, parent, d = q.popleft()

            for w in adj[v]:
                if w == parent:
                    continue

                if w in seen:
                    cycle = d + seen[w] + 1
                    best = min(best, cycle)
                else:
                    seen[w] = d + 1
                    q.append((w, v, d + 1))

    return best


def triangle_edges(adj):
    count = Counter()

    for a in adj:
        for b in adj[a]:
            if b <= a:
                continue

            common = adj[a] & adj[b]
            for c in common:
                if c > b:
                    count[(a, b)] += 1
                    count[(a, c)] += 1
                    count[(b, c)] += 1

    return Counter(count.values())


def adjacency_matrix(adj):
    nodes = sorted(adj)
    idx = {v: i for i, v in enumerate(nodes)}

    A = np.zeros((len(nodes), len(nodes)), dtype=int)

    for v in nodes:
        for w in adj[v]:
            A[idx[v], idx[w]] = 1

    return A


def walk_spectrum(adj, kmax=6):
    A = adjacency_matrix(adj)
    walks = {}

    Ak = np.identity(len(A), dtype=int)

    for k in range(1, kmax + 1):
        Ak = Ak @ A
        walks[k] = int(np.trace(Ak))

    return walks


def main():
    adj = measured_graph_reindexed()

    print("=" * 80)
    print("PAIR GRAPH IDENTIFICATION DATA")
    print("=" * 80)

    print("vertices:", len(adj))
    print("edges:", len(edge_set(adj)))
    print()

    d, prof = diameter(adj)
    print("diameter:", d)
    print("distance profile:")
    for k in sorted(prof):
        print(" ", k, prof[k])

    print()
    print("girth:", girth(adj))

    print()
    print("triangle participation per edge:")
    print(triangle_edges(adj))

    print()
    print("closed walk trace spectrum:")
    walks = walk_spectrum(adj)
    for k in walks:
        print(f"trace(A^{k}) =", walks[k])

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("These invariants can be used to identify the graph")
    print("in graph catalogs (Foster census, voltage lifts,")
    print("icosahedral constructions, etc.).")


if __name__ == "__main__":
    main()
