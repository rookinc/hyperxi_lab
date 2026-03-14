#!/usr/bin/env python3

from collections import Counter
from pathlib import Path

import networkx as nx
import numpy as np

from load_thalean_graph import load_spec, build_graph


def load_thalean_graph():
    return build_graph(load_spec())


def antipode_map(G):
    dist = dict(nx.all_pairs_shortest_path_length(G))
    a = {}
    for v in G.nodes():
        far = [u for u, d in dist[v].items() if d == 6]
        if len(far) != 1:
            raise RuntimeError(f"vertex {v} has {len(far)} distance-6 partners")
        a[v] = far[0]
    return a


def quotient_by_antipodes(G, a):
    seen = set()
    classes = []
    cls_of = {}

    for v in sorted(G.nodes()):
        if v in seen:
            continue
        pair = tuple(sorted((v, a[v])))
        seen.update(pair)
        idx = len(classes)
        classes.append(pair)
        for x in pair:
            cls_of[x] = idx

    Q = nx.Graph()
    Q.add_nodes_from(range(len(classes)))

    for u, v in G.edges():
        cu, cv = cls_of[u], cls_of[v]
        if cu != cv:
            Q.add_edge(cu, cv)

    return Q, classes


def shell_counts(G, root=0):
    d = nx.single_source_shortest_path_length(G, root)
    c = Counter(d.values())
    return tuple(c[i] for i in range(max(c) + 1))


def triangle_count(G):
    return sum(nx.triangles(G).values()) // 3


def closed_walk_traces(G, max_k=8):
    A = nx.to_numpy_array(G, dtype=int)
    traces = {}
    M = np.eye(A.shape[0], dtype=object)
    for k in range(1, max_k + 1):
        M = M @ A
        traces[k] = int(np.trace(M))
    return traces


def main():
    print("=" * 80)
    print("ANTIPODAL QUOTIENT IDENTIFICATION")
    print("=" * 80)

    G = load_thalean_graph()
    a = antipode_map(G)
    Q, classes = quotient_by_antipodes(G, a)

    outdir = Path("artifacts/census")
    outdir.mkdir(parents=True, exist_ok=True)
    g6_path = outdir / "thalean_antipodal_quotient.g6"
    g6 = nx.to_graph6_bytes(Q, header=False)
    g6_path.write_bytes(g6)

    print("QUOTIENT GRAPH")
    print("-" * 80)
    print("vertices:", Q.number_of_nodes())
    print("edges:", Q.number_of_edges())
    print("degree set:", sorted(set(dict(Q.degree()).values())))
    print("connected:", nx.is_connected(Q))
    print("diameter:", nx.diameter(Q))
    print("girth:", min(len(c) for c in nx.cycle_basis(Q)))
    print("triangles:", triangle_count(Q))
    print("shell counts from 0:", shell_counts(Q, 0))

    print()
    print("FIRST 15 ANTIPODAL CLASSES")
    print("-" * 80)
    for i, pair in enumerate(classes[:15]):
        print(f"{i:2d} -> {pair}")

    print()
    print("SPECTRUM")
    print("-" * 80)
    vals = np.linalg.eigvals(nx.to_numpy_array(Q))
    vals = sorted(round(v.real, 6) for v in vals)
    counts = Counter(vals)
    for v, c in sorted(counts.items()):
        print(f"{v:10.6f} : {c}")

    print()
    print("CLOSED WALK TRACE SPECTRUM")
    print("-" * 80)
    traces = closed_walk_traces(Q, max_k=8)
    for k, t in traces.items():
        print(f"trace(A^{k}) = {t}")

    print()
    print("GRAPH6")
    print("-" * 80)
    print(g6.decode().strip())

    print()
    print("SAVED")
    print("-" * 80)
    print(g6_path)


if __name__ == "__main__":
    main()
