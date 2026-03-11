from __future__ import annotations

from collections import Counter, defaultdict, deque
from typing import Dict, Set, Tuple

import numpy as np

from reconstruct_vertex_connection import pair_to_edge_sheet


def chamber_to_base_edges():
    """
    Recover the 30 base edges from the 60 chamber states.
    """
    p2es = pair_to_edge_sheet()
    edges = sorted({e for e, _ in p2es.values()})
    return edges


def build_base_edge_graph(edges):
    """
    Base graph:
      vertices = 30 base edges
      adjacency = share a vertex in the icosahedral vertex figure
    """
    adj = {e: set() for e in edges}
    for a in edges:
        sa = set(a)
        for b in edges:
            if a == b:
                continue
            if len(sa & set(b)) == 1:
                adj[a].add(b)
    return adj


def edge_set(adj: Dict[Tuple[int, int], Set[Tuple[int, int]]]):
    out = set()
    for u in adj:
        for v in adj[u]:
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


def bfs_distances(adj, s):
    dist = {s: 0}
    q = deque([s])
    while q:
        v = q.popleft()
        for w in adj[v]:
            if w not in dist:
                dist[w] = dist[v] + 1
                q.append(w)
    return dist


def all_distances(adj):
    return {v: bfs_distances(adj, v) for v in adj}


def shell_classes(adj):
    dist = all_distances(adj)
    sigs = {}
    for v in adj:
        c = Counter(dist[v].values())
        sigs[v] = tuple(c[k] for k in sorted(c))
    return Counter(sigs.values())


def common_neighbor_profiles(adj):
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


def diameter(adj):
    dist = all_distances(adj)
    return max(max(d.values()) for d in dist.values())


def find_opposition_matching(adj):
    """
    Recover the distance-3 perfect matching on the base graph by using
    the 15 pairs already observed in the chamber analysis:
    two base edges are matched if their full 2-sheet fibers formed one
    of the distance-5 (4,4) 4-cycles.

    Here we can characterize it intrinsically as a perfect matching
    among distance-3 pairs if such a unique structure exists.
    """
    dist = all_distances(adj)

    # candidate distance-3 graph
    d3 = {v: set() for v in adj}
    for u in adj:
        for v in adj:
            if u == v:
                continue
            if dist[u][v] == 3:
                d3[u].add(v)

    # print degree profile only; we do not assume uniqueness
    d3_deg = Counter(len(d3[v]) for v in d3)
    return d3, d3_deg


def main():
    edges = chamber_to_base_edges()
    adj = build_base_edge_graph(edges)

    print("=" * 80)
    print("30-VERTEX BASE GRAPH")
    print("=" * 80)
    print(f"vertices: {len(adj)}")
    print(f"edges: {len(edge_set(adj))}")
    print(f"degree set: {sorted({len(adj[v]) for v in adj})}")
    print(f"triangles: {triangle_count(adj)}")
    print(f"diameter: {diameter(adj)}")
    print()

    print("shell-count classes")
    print("-" * 80)
    sc = shell_classes(adj)
    print(f"classes: {len(sc)}")
    for sig, count in sorted(sc.items()):
        print(f"{sig}: {count}")
    print()

    pa, pn = common_neighbor_profiles(adj)
    print("adjacent common-neighbor profile")
    print("-" * 80)
    for k in sorted(pa):
        print(f"{k}: {pa[k]}")
    print()

    print("nonadjacent common-neighbor profile")
    print("-" * 80)
    for k in sorted(pn):
        print(f"{k}: {pn[k]}")
    print()

    print("eigenvalue multiplicities")
    print("-" * 80)
    mults = eigen_mults(adj)
    for val in sorted(mults):
        print(f"{val:>10}: {mults[val]}")
    print()

    d3, d3_deg = find_opposition_matching(adj)
    print("distance-3 relation degree profile")
    print("-" * 80)
    print(dict(sorted(d3_deg.items())))
    print()

    print("first 15 base vertices")
    print("-" * 80)
    print(edges[:15])
    print()

    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("The icosidodecahedral graph has:")
    print("  30 vertices")
    print("  60 edges")
    print("  degree 4")
    print("  20 triangles")
    print()
    print("If the invariants above match that profile, then the 30-edge base graph")
    print("is extremely plausibly the icosidodecahedral graph (or an isomorphic")
    print("quartic graph with the same symmetry package).")


if __name__ == "__main__":
    main()
