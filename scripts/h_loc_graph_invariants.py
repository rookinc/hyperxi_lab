from __future__ import annotations

import numpy as np
from collections import deque, Counter

from hyperxi.spectral.operators import LocalOperatorFactory


def build_graph():
    ops = LocalOperatorFactory()
    H = ops.build_H_loc()

    # adjacency = support of H
    A = (H != 0).astype(int)

    # remove self loops if present
    np.fill_diagonal(A, 0)

    return A


def degree(A):
    return A.sum(axis=1)


def count_edges(A):
    return int(A.sum() // 2)


def count_triangles(A):
    # trace(A^3)/6 for undirected graphs
    A3 = A @ A @ A
    return int(np.trace(A3) // 6)


def bfs_shells(A, start=0):
    n = A.shape[0]
    dist = [-1] * n
    dist[start] = 0

    q = deque([start])

    while q:
        v = q.popleft()
        for w in np.where(A[v] > 0)[0]:
            if dist[w] == -1:
                dist[w] = dist[v] + 1
                q.append(w)

    counts = Counter(dist)
    shells = [counts[d] for d in sorted(counts)]
    diameter = max(dist)

    return shells, diameter


def main():
    print("=" * 80)
    print("H_LOC GRAPH INVARIANT REPORT")
    print("=" * 80)

    A = build_graph()

    n = A.shape[0]
    deg = degree(A)

    print()
    print("vertices:", n)
    print("edges:", count_edges(A))
    print("degree set:", sorted(set(deg)))

    tri = count_triangles(A)
    print("triangles:", tri)

    shells, diam = bfs_shells(A)

    print("diameter:", diam)
    print("shell counts:", tuple(shells))

    print()
    print("=" * 80)
    print("Invariant scan complete.")


if __name__ == "__main__":
    main()
