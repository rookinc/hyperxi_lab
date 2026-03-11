from __future__ import annotations

from collections import Counter, defaultdict, deque
from typing import Dict, Set, Tuple

import numpy as np

from vertex_connection_model import measured_graph_reindexed
from reconstruct_vertex_connection import pair_to_edge_sheet


def bfs_distances(adj: Dict, s):
    dist = {s: 0}
    q = deque([s])
    while q:
        v = q.popleft()
        for w in adj[v]:
            if w not in dist:
                dist[w] = dist[v] + 1
                q.append(w)
    return dist


def all_distances(adj: Dict):
    return {v: bfs_distances(adj, v) for v in adj}


def chamber_to_base_edges():
    p2es = pair_to_edge_sheet()
    edges = sorted({e for e, _ in p2es.values()})
    edge_to_idx = {e: idx for idx, e in enumerate(edges)}

    node_to_edge_sheet = {}
    for pair_id, (e, s) in p2es.items():
        node = 2 * edge_to_idx[e] + s
        node_to_edge_sheet[node] = (e, s)

    return edges, node_to_edge_sheet


def chamber_pair_profile(adj: Dict[int, Set[int]], dist: Dict[int, Dict[int, int]], x: int, y: int):
    i = dist[x][y]
    counts = Counter()
    for z in adj[y]:
        counts[dist[x][z]] += 1
    prof = tuple((k, counts[k]) for k in sorted(counts))
    return i, prof


def build_base_graph(edges):
    """
    30-vertex graph on icosahedral edges:
    adjacency = share a vertex
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


def connected_components(adj: Dict):
    seen = set()
    comps = []
    for v in adj:
        if v in seen:
            continue
        stack = [v]
        comp = []
        seen.add(v)
        while stack:
            x = stack.pop()
            comp.append(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        comps.append(sorted(comp))
    return comps


def edge_set(adj: Dict):
    out = set()
    for u in adj:
        for v in adj[u]:
            if u < v:
                out.add((u, v))
    return out


def triangle_count(adj: Dict):
    total = 0
    for a in sorted(adj):
        for b in [x for x in adj[a] if x > a]:
            common = adj[a] & adj[b]
            for c in [x for x in common if x > b]:
                total += 1
    return total


def adjacency_matrix(adj: Dict):
    nodes = sorted(adj)
    idx = {v: i for i, v in enumerate(nodes)}
    A = np.zeros((len(nodes), len(nodes)), dtype=int)
    for v in nodes:
        for w in adj[v]:
            A[idx[v], idx[w]] = 1
    return A


def eigen_mults(adj: Dict):
    A = adjacency_matrix(adj)
    vals = np.linalg.eigvals(A)
    vals = [round(float(np.real_if_close(v)), 6) for v in vals]
    return Counter(vals)


def shell_classes(adj: Dict):
    dist = all_distances(adj)
    sigs = {}
    for v in adj:
        c = Counter(dist[v].values())
        sigs[v] = tuple(c[k] for k in sorted(c))
    return Counter(sigs.values())


def main():
    chamber_adj = measured_graph_reindexed()
    chamber_dist = all_distances(chamber_adj)
    edges, node_to_edge_sheet = chamber_to_base_edges()

    # ---------------------------------------------------------
    # Recover the 15 opposition pairs on base edges
    # via the distance-5 (4,4) chamber relation
    # ---------------------------------------------------------
    rel = defaultdict(set)
    for x in chamber_adj:
        for y in chamber_adj:
            if x >= y:
                continue
            d, prof = chamber_pair_profile(chamber_adj, chamber_dist, x, y)
            if d == 5 and prof == ((4, 4),):
                rel[x].add(y)
                rel[y].add(x)

    comps = connected_components(rel)

    opposition_pairs = []
    for comp in comps:
        base_edges = sorted({node_to_edge_sheet[v][0] for v in comp})
        if len(base_edges) == 2:
            opposition_pairs.append(tuple(base_edges))

    opposition_pairs = sorted(opposition_pairs)

    print("=" * 80)
    print("OPPOSITION MATCHING ON 30 BASE EDGES")
    print("=" * 80)
    for e, f in opposition_pairs:
        print(f"{e}  <->  {f}")
    print()
    print(f"total matched pairs: {len(opposition_pairs)}")

    # perfect matching check
    deg = Counter()
    for e, f in opposition_pairs:
        deg[e] += 1
        deg[f] += 1

    print("perfect matching on base edges:",
          len(opposition_pairs) == 15 and len(deg) == 30 and all(deg[e] == 1 for e in edges))
    print()

    # ---------------------------------------------------------
    # Build 30-vertex base graph
    # ---------------------------------------------------------
    base_adj = build_base_graph(edges)

    # ---------------------------------------------------------
    # Quotient by opposition matching -> 15 vertices
    # ---------------------------------------------------------
    orbit_of = {}
    orbits = []
    for e, f in opposition_pairs:
        orb = tuple(sorted((e, f)))
        orbits.append(orb)
        orbit_of[e] = orb
        orbit_of[f] = orb

    qadj = defaultdict(set)
    for e in base_adj:
        E = orbit_of[e]
        for f in base_adj[e]:
            F = orbit_of[f]
            if E != F:
                qadj[E].add(F)
                qadj[F].add(E)

    qadj = {k: set(v) for k, v in qadj.items()}

    print("=" * 80)
    print("15-VERTEX QUOTIENT GRAPH")
    print("=" * 80)
    print(f"vertices: {len(qadj)}")
    print(f"edges: {len(edge_set(qadj))}")
    print(f"degree set: {sorted({len(qadj[v]) for v in qadj})}")
    print(f"triangles: {triangle_count(qadj)}")
    print()

    print("shell-count classes")
    print("-" * 80)
    sc = shell_classes(qadj)
    print(f"classes: {len(sc)}")
    for sig, count in sorted(sc.items()):
        print(f"{sig}: {count}")
    print()

    print("eigenvalue multiplicities")
    print("-" * 80)
    mults = eigen_mults(qadj)
    for val in sorted(mults):
        print(f"{val:>10}: {mults[val]}")
    print()

    print("first 10 quotient vertices")
    print("-" * 80)
    for orb in sorted(qadj)[:10]:
        print(orb)
    print()

    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("This quotient collapses the canonical distance-3 opposition matching")
    print("on the 30-edge base graph. If the quotient has a clean symmetric")
    print("profile, then the chamber graph may be organized over a 15-object")
    print("geometry beneath the 30-edge line-graph level.")


if __name__ == "__main__":
    main()
