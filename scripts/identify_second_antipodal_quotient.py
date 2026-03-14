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
    diam = nx.diameter(G)
    for v in G.nodes():
        far = [u for u, d in dist[v].items() if d == diam]
        if len(far) != 1:
            raise RuntimeError(
                f"vertex {v} has {len(far)} distance-{diam} partners"
            )
        a[v] = far[0]
    return a, diam


def quotient_by_pairs(G, pair_map):
    seen = set()
    classes = []
    cls_of = {}

    for v in sorted(G.nodes()):
        if v in seen:
            continue
        pair = tuple(sorted((v, pair_map[v])))
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

    return Q, classes, cls_of


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


def print_graph_summary(name, G):
    print(name)
    print("-" * 80)
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted(set(dict(G.degree()).values())))
    print("connected:", nx.is_connected(G))
    print("diameter:", nx.diameter(G))
    print("girth:", min(len(c) for c in nx.cycle_basis(G)))
    print("triangles:", triangle_count(G))
    print("shell counts from 0:", shell_counts(G, 0))
    print()


def main():
    print("=" * 80)
    print("SECOND ANTIPODAL QUOTIENT IDENTIFICATION")
    print("=" * 80)

    G60 = load_thalean_graph()

    a60, diam60 = antipode_map(G60)
    G30, classes30, _ = quotient_by_pairs(G60, a60)

    a30, diam30 = antipode_map(G30)
    G15, classes15, _ = quotient_by_pairs(G30, a30)

    print_graph_summary("THALEAN GRAPH (60)", G60)
    print_graph_summary("FIRST ANTIPODAL QUOTIENT (30)", G30)
    print_graph_summary("SECOND ANTIPODAL QUOTIENT (15)", G15)

    print("FIRST 15 CLASSES IN 30 -> 15 QUOTIENT")
    print("-" * 80)
    for i, pair in enumerate(classes15[:15]):
        print(f"{i:2d} -> {pair}")

    print()
    print("SPECTRUM OF 15-GRAPH")
    print("-" * 80)
    vals = np.linalg.eigvals(nx.to_numpy_array(G15))
    vals = sorted(round(v.real, 6) for v in vals)
    counts = Counter(vals)
    for v, c in sorted(counts.items()):
        print(f"{v:10.6f} : {c}")

    print()
    print("CLOSED WALK TRACES OF 15-GRAPH")
    print("-" * 80)
    traces = closed_walk_traces(G15, max_k=8)
    for k, t in traces.items():
        print(f"trace(A^{k}) = {t}")

    outdir = Path("artifacts/census")
    outdir.mkdir(parents=True, exist_ok=True)

    g6_30 = nx.to_graph6_bytes(G30, header=False).decode().strip()
    g6_15 = nx.to_graph6_bytes(G15, header=False).decode().strip()

    (outdir / "thalean_antipodal_quotient.g6").write_text(g6_30 + "\n")
    (outdir / "thalean_second_antipodal_quotient.g6").write_text(g6_15 + "\n")

    print()
    print("GRAPH6 OF 15-GRAPH")
    print("-" * 80)
    print(g6_15)

    print()
    print("SAVED")
    print("-" * 80)
    print(outdir / "thalean_antipodal_quotient.g6")
    print(outdir / "thalean_second_antipodal_quotient.g6")


if __name__ == "__main__":
    main()
