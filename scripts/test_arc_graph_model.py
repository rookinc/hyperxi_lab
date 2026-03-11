from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple

import numpy as np

from vertex_connection_model import measured_graph_reindexed

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


def oriented_edges():
    out = []
    for u in sorted(BASE_ADJ):
        for v in BASE_ADJ[u]:
            out.append((u, v))
    return out


def arc_graph():
    """
    Nodes are oriented edges (u,v).
    Undirected adjacency joins:
      (u,v) -- (v,w) with w != u
    This is the undirected 1-arc graph / directed line graph skeleton.
    """
    arcs = oriented_edges()
    aset = set(arcs)
    adj = defaultdict(set)

    for u, v in arcs:
        for w in BASE_ADJ[v]:
            if w == u:
                continue
            x = (u, v)
            y = (v, w)
            adj[x].add(y)
            adj[y].add(x)

    return {k: set(v) for k, v in adj.items()}


def relabel_to_int(adj):
    nodes = sorted(adj)
    idx = {v: i for i, v in enumerate(nodes)}
    out = defaultdict(set)
    for v in nodes:
        for w in adj[v]:
            out[idx[v]].add(idx[w])
    return {k: set(v) for k, v in out.items()}


def edge_set(adj):
    out = set()
    for u, nbrs in adj.items():
        for v in nbrs:
            if u < v:
                out.add((u, v))
    return out


def triangle_count(adj):
    total = 0
    for a in sorted(adj):
        for b in [x for x in adj[a] if x > a]:
            common = adj[a] & adj[b]
            for c in [x for x in common if x > b]:
                total += 1
    return total


def common_neighbor_profiles(adj):
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


def adjacency_matrix(adj):
    nodes = sorted(adj)
    idx = {v: i for i, v in enumerate(nodes)}
    A = np.zeros((len(nodes), len(nodes)), dtype=int)
    for v in nodes:
        for w in adj[v]:
            A[idx[v], idx[w]] = 1
    return A


def eigen_mults(adj):
    A = adjacency_matrix(adj)
    vals = np.linalg.eigvals(A)
    vals = [round(float(np.real_if_close(v)), 6) for v in vals]
    return Counter(vals)


def summarize(name, adj):
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
    for val in sorted(eigen_mults(adj)):
        print(f"  {val:>10}: {eigen_mults(adj)[val]}")


def main():
    measured = measured_graph_reindexed()
    arc = relabel_to_int(arc_graph())

    summarize("MEASURED CHAMBER GRAPH", measured)
    print()
    summarize("ORIENTED-EDGE ARC GRAPH OF ICOSAHEDRON", arc)

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("If these invariants match, the chamber graph is an arc-graph /")
    print("oriented-edge transport graph of the icosahedral base.")
    print("If they do not match, the chamber graph is a stricter Petrie-twisted")
    print("edge-state graph rather than the plain arc graph.")
    

if __name__ == "__main__":
    main()
