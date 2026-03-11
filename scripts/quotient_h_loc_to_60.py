from __future__ import annotations

import numpy as np
from collections import deque, Counter

from hyperxi.spectral.operators import LocalOperatorFactory


def build_h_loc_support() -> np.ndarray:
    ops = LocalOperatorFactory()
    H = ops.build_H_loc()
    A = (H != 0).astype(int)
    np.fill_diagonal(A, 0)
    return A


def quotient_by_pairs(A: np.ndarray) -> np.ndarray:
    """
    Quotient 120 vertices to 60 by pairing:
        {0,1}, {2,3}, ..., {118,119}
    Change this pairing later if needed.
    """
    n = A.shape[0]
    assert n % 2 == 0
    m = n // 2

    Q = np.zeros((m, m), dtype=int)

    for i in range(m):
        block_i = [2 * i, 2 * i + 1]
        for j in range(m):
            if i == j:
                continue
            block_j = [2 * j, 2 * j + 1]

            hit = False
            for u in block_i:
                for v in block_j:
                    if A[u, v] != 0:
                        hit = True
                        break
                if hit:
                    break

            if hit:
                Q[i, j] = 1

    np.fill_diagonal(Q, 0)
    return Q


def count_edges(A: np.ndarray) -> int:
    return int(A.sum() // 2)


def count_triangles(A: np.ndarray) -> int:
    A3 = A @ A @ A
    return int(np.trace(A3) // 6)


def bfs_shells(A: np.ndarray, start: int = 0):
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
    print("QUOTIENT OF H_LOC SUPPORT GRAPH BY ADJACENT FLAG PAIRS")
    print("=" * 80)
    print()

    A = build_h_loc_support()
    Q = quotient_by_pairs(A)

    deg = Q.sum(axis=1)
    shells, diam = bfs_shells(Q)

    print("original vertices:", A.shape[0])
    print("quotient vertices:", Q.shape[0])
    print("quotient edges:", count_edges(Q))
    print("quotient degree set:", sorted(set(int(x) for x in deg)))
    print("quotient triangles:", count_triangles(Q))
    print("quotient diameter:", diam)
    print("quotient shell counts:", tuple(shells))

    print()
    print("=" * 80)
    print("Quotient scan complete.")


if __name__ == "__main__":
    main()
