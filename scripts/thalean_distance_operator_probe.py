#!/usr/bin/env python3
from __future__ import annotations

from collections import defaultdict, Counter

import networkx as nx
import numpy as np
import sympy as sp

from hyperxi.combinatorics.chamber_graph import build_chamber_graph


def load_graph():
    raw = build_chamber_graph()
    G = nx.Graph()
    G.add_nodes_from(raw.vertices)
    G.add_edges_from(raw.edges)
    return G


def shell_partition(G: nx.Graph, root: int):
    dist = nx.single_source_shortest_path_length(G, root)
    shells = defaultdict(list)
    for v, d in dist.items():
        shells[d].append(v)
    return {k: sorted(vs) for k, vs in sorted(shells.items())}


def shell_quotient_matrix(G: nx.Graph, shells: dict[int, list[int]]):
    """
    Average shell-to-shell adjacency counts.
    Entry Q[i,j] = average number of neighbors in shell j
    for a vertex in shell i.
    """
    shell_ids = sorted(shells)
    shell_index = {s: i for i, s in enumerate(shell_ids)}
    vertex_shell = {}
    for s, vs in shells.items():
        for v in vs:
            vertex_shell[v] = s

    Q = np.zeros((len(shell_ids), len(shell_ids)), dtype=float)
    detail = {}

    for s in shell_ids:
        rows = []
        for v in shells[s]:
            counts = Counter(vertex_shell[nbr] for nbr in G.neighbors(v))
            row = [counts.get(t, 0) for t in shell_ids]
            rows.append(row)

        arr = np.array(rows, dtype=float)
        Q[shell_index[s], :] = np.mean(arr, axis=0)
        detail[s] = arr

    return shell_ids, Q, detail


def summarize_shell_variation(shell_ids, detail):
    lines = []
    for s in shell_ids:
        arr = detail[s]
        uniq = np.unique(arr, axis=0)
        lines.append(f"shell {s}: size={len(arr)} unique adjacency profiles={len(uniq)}")
        for row in uniq:
            lines.append(f"  profile={row.tolist()} count={np.sum(np.all(arr == row, axis=1))}")
    return lines


def main():
    print("=" * 80)
    print("THALION DISTANCE OPERATOR PROBE")
    print("=" * 80)

    G = load_graph()
    root = min(G.nodes())

    shells = shell_partition(G, root)
    shell_ids, Q, detail = shell_quotient_matrix(G, shells)

    print(f"root = {root}")
    print("shell sizes:")
    for s in shell_ids:
        print(f"  shell {s}: {len(shells[s])}")

    print()
    print("average shell quotient matrix:")
    print(Q)

    x = sp.symbols("x")
    Qsym = sp.Matrix(Q)
    charpoly = sp.expand(Qsym.charpoly(x).as_expr())

    print()
    print("characteristic polynomial of average shell quotient:")
    print(charpoly)

    print()
    print("shell variation summary:")
    for line in summarize_shell_variation(shell_ids, detail):
        print(line)

    print("=" * 80)


if __name__ == "__main__":
    main()
