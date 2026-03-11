from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List, Tuple

import numpy as np


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

# Verified same/swap cocycle on icosahedral edges
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

# Measured ordered pair cycles from chamber
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


def base_edges() -> List[Tuple[int, int]]:
    out = []
    for i, nbrs in BASE_ADJ.items():
        for j in nbrs:
            if i < j:
                out.append((i, j))
    return sorted(out)


def measured_pair_graph() -> Dict[int, set[int]]:
    adj = defaultdict(set)
    for cyc in PAIR_CYCLES.values():
        n = len(cyc)
        for i in range(n):
            a = cyc[i]
            b = cyc[(i + 1) % n]
            adj[a].add(b)
            adj[b].add(a)
    return {k: set(v) for k, v in adj.items()}


def edge_index_map() -> Dict[Tuple[int, int], int]:
    return {e: idx for idx, e in enumerate(base_edges())}


def lifted_node(edge_id: int, sheet: int) -> int:
    return 2 * edge_id + sheet


def build_reference_lift(twisted: bool) -> Dict[int, set[int]]:
    edges = base_edges()
    eidx = edge_index_map()
    adj = defaultdict(set)

    for v in sorted(BASE_ADJ):
        inc = [canon(v, u) for u in BASE_ADJ[v]]
        inc_ids = [eidx[e] for e in inc]

        # local cyclic order around each vertex inherited from sorted neighbor list
        # simple reference model: connect consecutive incident edges around vertex
        m = len(inc_ids)
        for k in range(m):
            e1 = inc[k]
            e2 = inc[(k + 1) % m]
            id1 = eidx[e1]
            id2 = eidx[e2]

            rel1 = EDGE_REL[e1] if twisted else 0
            rel2 = EDGE_REL[e2] if twisted else 0

            for s in [0, 1]:
                t1 = s ^ rel1
                t2 = s ^ rel2
                a = lifted_node(id1, t1)
                b = lifted_node(id2, t2)
                adj[a].add(b)
                adj[b].add(a)

    return {k: set(v) for k, v in adj.items()}


def adjacency_matrix(adj: Dict[int, set[int]]) -> np.ndarray:
    nodes = sorted(adj)
    idx = {v: i for i, v in enumerate(nodes)}
    A = np.zeros((len(nodes), len(nodes)), dtype=int)
    for v in nodes:
        for w in adj[v]:
            A[idx[v], idx[w]] = 1
    return A


def triangle_count(adj: Dict[int, set[int]]) -> int:
    nodes = sorted(adj)
    total = 0
    for i, a in enumerate(nodes):
        for b in [x for x in adj[a] if x > a]:
            common = adj[a] & adj[b]
            for c in [x for x in common if x > b]:
                total += 1
    return total


def common_neighbor_profiles(adj: Dict[int, set[int]]) -> Tuple[Counter, Counter]:
    nodes = sorted(adj)
    prof_adj = Counter()
    prof_non = Counter()
    for i, u in enumerate(nodes):
        for v in nodes[i + 1:]:
            c = len(adj[u] & adj[v])
            if v in adj[u]:
                prof_adj[c] += 1
            else:
                prof_non[c] += 1
    return prof_adj, prof_non


def eigen_mults(adj: Dict[int, set[int]]) -> Counter:
    A = adjacency_matrix(adj)
    vals = np.linalg.eigvals(A)
    vals = [round(float(np.real_if_close(v)), 6) for v in vals]
    return Counter(vals)


def summarize(name: str, adj: Dict[int, set[int]]) -> None:
    edges = sum(len(v) for v in adj.values()) // 2
    degs = sorted({len(v) for v in adj.values()})
    print("=" * 80)
    print(name)
    print("=" * 80)
    print(f"vertices: {len(adj)}")
    print(f"edges: {edges}")
    print(f"degree set: {degs}")
    print(f"triangles: {triangle_count(adj)}")

    prof_adj, prof_non = common_neighbor_profiles(adj)
    print()
    print("adjacent common-neighbor profile:")
    for k in sorted(prof_adj):
        print(f"  {k}: {prof_adj[k]}")
    print("nonadjacent common-neighbor profile:")
    for k in sorted(prof_non):
        print(f"  {k}: {prof_non[k]}")

    print()
    print("eigenvalue multiplicities:")
    mults = eigen_mults(adj)
    for val in sorted(mults):
        print(f"  {val:>10}: {mults[val]}")


def main() -> None:
    measured = measured_pair_graph()
    untwisted = build_reference_lift(twisted=False)
    twisted = build_reference_lift(twisted=True)

    summarize("MEASURED PAIR-FIBER GRAPH", measured)
    print()
    summarize("REFERENCE UNTWISTED EDGE-DOUBLE", untwisted)
    print()
    summarize("REFERENCE TWISTED EDGE-DOUBLE", twisted)

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("This compares the measured 60-state pair-fiber transport graph")
    print("against two explicit reference lifts of the icosahedral base graph:")
    print("a trivial binary edge-double and a cocycle-twisted binary edge-double.")
    print("Matching invariants with the twisted model would strengthen the claim")
    print("that ordered Petrie transport realizes a genuine twisted edge bundle.")


if __name__ == "__main__":
    main()
