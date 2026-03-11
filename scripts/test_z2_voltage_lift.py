from __future__ import annotations

from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple

import numpy as np

from vertex_connection_model import measured_graph_reindexed

# Icosahedral base graph on 12 decagons
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


def canon(i: int, j: int) -> Tuple[int, int]:
    return (i, j) if i < j else (j, i)


def oriented_edges() -> List[Tuple[int, int]]:
    out = []
    for u in sorted(BASE_ADJ):
        for v in sorted(BASE_ADJ[u]):
            out.append((u, v))
    return out


def voltage_arc_graph() -> Dict[Tuple[int, int, int], Set[Tuple[int, int, int]]]:
    """
    Nodes: (u, v, s) with u~v in the icosahedron and s in {0,1}
    Edges: (u,v,s) -- (v,w,t) for w != u, where t = s xor voltage(v,w)
           This is the simplest Z2 voltage lift of the oriented-edge graph.
    """
    nodes = [(u, v, s) for (u, v) in oriented_edges() for s in (0, 1)]
    adj = defaultdict(set)

    for u, v, s in nodes:
        for w in BASE_ADJ[v]:
            if w == u:
                continue
            t = s ^ EDGE_REL[canon(v, w)]
            a = (u, v, s)
            b = (v, w, t)
            adj[a].add(b)
            adj[b].add(a)

    return {k: set(v) for k, v in adj.items()}


def relabel_to_int(adj: Dict[Tuple[int, int, int], Set[Tuple[int, int, int]]]) -> Dict[int, Set[int]]:
    nodes = sorted(adj)
    idx = {v: i for i, v in enumerate(nodes)}
    out = defaultdict(set)
    for v in nodes:
        for w in adj[v]:
            out[idx[v]].add(idx[w])
    return {k: set(v) for k, v in out.items()}


def edge_set(adj: Dict[int, Set[int]]) -> Set[Tuple[int, int]]:
    out = set()
    for u, nbrs in adj.items():
        for v in nbrs:
            if u < v:
                out.add((u, v))
    return out


def triangle_count(adj: Dict[int, Set[int]]) -> int:
    total = 0
    for a in sorted(adj):
        for b in [x for x in adj[a] if x > a]:
            common = adj[a] & adj[b]
            for c in [x for x in common if x > b]:
                total += 1
    return total


def common_neighbor_profiles(adj: Dict[int, Set[int]]) -> Tuple[Counter, Counter]:
    nodes = sorted(adj)
    pa = Counter()
    pn = Counter()
    for i, u in enumerate(nodes):
        for v in nodes[i + 1:]:
            c = len(adj[u] & adj[v])
            if v in adj[u]:
                pa[c] += 1
            else:
                pn[c] += 1
    return pa, pn


def adjacency_matrix(adj: Dict[int, Set[int]]) -> np.ndarray:
    nodes = sorted(adj)
    idx = {v: i for i, v in enumerate(nodes)}
    A = np.zeros((len(nodes), len(nodes)), dtype=int)
    for v in nodes:
        for w in adj[v]:
            A[idx[v], idx[w]] = 1
    return A


def eigen_mults(adj: Dict[int, Set[int]]) -> Counter:
    A = adjacency_matrix(adj)
    vals = np.linalg.eigvals(A)
    vals = [round(float(np.real_if_close(v)), 6) for v in vals]
    return Counter(vals)


def summarize(name: str, adj: Dict[int, Set[int]]) -> None:
    print("=" * 80)
    print(name)
    print("=" * 80)
    print(f"vertices: {len(adj)}")
    print(f"edges: {len(edge_set(adj))}")
    print(f"degree set: {sorted({len(v) for v in adj.values()})}")
    print(f"triangles: {triangle_count(adj)}")

    pa, pn = common_neighbor_profiles(adj)
    print()
    print("adjacent common-neighbor profile:")
    for k in sorted(pa):
        print(f"  {k}: {pa[k]}")
    print("nonadjacent common-neighbor profile:")
    for k in sorted(pn):
        print(f"  {k}: {pn[k]}")

    print()
    print("eigenvalue multiplicities:")
    mults = eigen_mults(adj)
    for val in sorted(mults):
        print(f"  {val:>10}: {mults[val]}")


def main():
    measured = measured_graph_reindexed()
    model = relabel_to_int(voltage_arc_graph())

    summarize("MEASURED CHAMBER GRAPH", measured)
    print()
    summarize("Z2 VOLTAGE LIFT OF ICOSAHEDRAL ARC GRAPH", model)

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("If this model matches, the chamber graph is a plain Z2 voltage lift")
    print("of the icosahedral arc graph.")
    print("If it does not match, then the chamber graph is stricter: it uses")
    print("a Petrie/vertex-connection restriction in addition to the edge cocycle.")


if __name__ == "__main__":
    main()
