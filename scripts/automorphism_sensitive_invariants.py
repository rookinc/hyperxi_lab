from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, Set

import numpy as np

from vertex_connection_model import measured_graph_reindexed


def edge_set(adj):
    out = set()
    for u, nbrs in adj.items():
        for v in nbrs:
            if u < v:
                out.add((u, v))
    return out


def adjacency_matrix(adj):
    nodes = sorted(adj)
    idx = {v: i for i, v in enumerate(nodes)}
    A = np.zeros((len(nodes), len(nodes)), dtype=int)
    for v in nodes:
        for w in adj[v]:
            A[idx[v], idx[w]] = 1
    return A, nodes, idx


def bfs_distances(adj, s):
    dist = {s: 0}
    frontier = [s]
    while frontier:
        new = []
        for v in frontier:
            for w in adj[v]:
                if w not in dist:
                    dist[w] = dist[v] + 1
                    new.append(w)
        frontier = new
    return dist


def distance_partition(adj):
    parts = {}
    for v in sorted(adj):
        d = bfs_distances(adj, v)
        counts = Counter(d.values())
        parts[v] = tuple(counts[k] for k in sorted(counts))
    return parts


def local_signature(adj, v):
    nbrs = sorted(adj[v])

    nn_edges = 0
    for i, a in enumerate(nbrs):
        for b in nbrs[i + 1:]:
            if b in adj[a]:
                nn_edges += 1

    d2 = []
    for u in adj:
        if u == v or u in adj[v]:
            continue
        c = len(adj[v] & adj[u])
        if c > 0:
            d2.append(c)

    return (
        len(nbrs),
        nn_edges,
        tuple(sorted(Counter(d2).items())),
    )


def vertex_signature_classes(adj):
    sigs = defaultdict(list)
    dist_parts = distance_partition(adj)
    for v in sorted(adj):
        sig = (local_signature(adj, v), dist_parts[v])
        sigs[sig].append(v)
    return sigs


def edge_signature(adj, e):
    a, b = e
    na = adj[a] - {b}
    nb = adj[b] - {a}
    common = na & nb
    only_a = na - nb
    only_b = nb - na

    pair_counts = []
    for x in only_a:
        for y in only_b:
            pair_counts.append(len(adj[x] & adj[y]))

    return (
        len(common),
        len(only_a),
        len(only_b),
        tuple(sorted(Counter(pair_counts).items())),
    )


def edge_signature_classes(adj):
    sigs = defaultdict(list)
    for e in sorted(edge_set(adj)):
        sigs[edge_signature(adj, e)].append(e)
    return sigs


def triangle_set(adj):
    tris = set()
    for a in sorted(adj):
        for b in [x for x in adj[a] if x > a]:
            common = adj[a] & adj[b]
            for c in [x for x in common if x > b]:
                tris.add((a, b, c))
    return tris


def triangle_intersection_profile(adj):
    tris = sorted(triangle_set(adj))
    profile = Counter()
    for i, t1 in enumerate(tris):
        s1 = set(t1)
        for t2 in tris[i + 1:]:
            s2 = set(t2)
            profile[len(s1 & s2)] += 1
    return profile


def walk_counts_by_vertex(adj, kmax=6):
    A, nodes, idx = adjacency_matrix(adj)
    Ak = np.identity(len(nodes), dtype=int)
    out = {v: [] for v in nodes}
    for k in range(1, kmax + 1):
        Ak = Ak @ A
        diag = np.diag(Ak)
        for v in nodes:
            out[v].append(int(diag[idx[v]]))
    return out


def main():
    adj = measured_graph_reindexed()

    print("=" * 80)
    print("AUTOMORPHISM-SENSITIVE INVARIANTS")
    print("=" * 80)

    print("Vertex signature classes")
    print("-" * 80)
    vclasses = vertex_signature_classes(adj)
    print(f"number of vertex signature classes: {len(vclasses)}")
    for i, (sig, verts) in enumerate(sorted(vclasses.items(), key=lambda kv: (len(kv[1]), kv[1][0]))):
        label = "..." if len(verts) > 12 else ""
        print(f"class {i}: size={len(verts)} verts={verts[:12]}{label}")
        print(f"  signature={sig}")

    print()
    print("Edge signature classes")
    print("-" * 80)
    eclasses = edge_signature_classes(adj)
    print(f"number of edge signature classes: {len(eclasses)}")
    for i, (sig, edges) in enumerate(sorted(eclasses.items(), key=lambda kv: (len(kv[1]), kv[1][0]))):
        label = "..." if len(edges) > 10 else ""
        print(f"class {i}: size={len(edges)} first_edges={edges[:10]}{label}")
        print(f"  signature={sig}")

    print()
    print("Triangle intersection profile")
    print("-" * 80)
    tprof = triangle_intersection_profile(adj)
    for k in sorted(tprof):
        print(f"triangle pairs sharing {k} vertices: {tprof[k]}")

    print()
    print("Closed walk counts by vertex")
    print("-" * 80)
    wc = walk_counts_by_vertex(adj, 6)
    wc_classes = Counter(tuple(v) for v in wc.values())
    print(f"number of walk-signature classes: {len(wc_classes)}")
    for sig, count in sorted(wc_classes.items()):
        print(f"{sig}: {count}")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("If there is a single vertex-signature class and a single edge-signature")
    print("class, that is strong evidence for vertex- and edge-transitivity.")
    print("Multiple classes indicate symmetry breaking relative to the full")
    print("icosahedral expectation.")


if __name__ == "__main__":
    main()
