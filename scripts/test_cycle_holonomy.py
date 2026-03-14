#!/usr/bin/env python3

import networkx as nx
import numpy as np

from hyperxi.combinatorics.chamber_graph import build_chamber_graph


def load_graph():

    CG = build_chamber_graph()

    if isinstance(CG, nx.Graph):
        return CG

    if hasattr(CG, "G"):
        return CG.G

    if hasattr(CG, "graph"):
        return CG.graph

    G = nx.Graph()
    G.add_edges_from(CG.edges)
    return G


def compute_modes(G):

    A = nx.to_numpy_array(G)
    deg = np.sum(A, axis=1)

    L = np.diag(deg) - A

    vals, vecs = np.linalg.eigh(L)

    return vals, vecs


def first_excited(vals, vecs):

    base = vals[0]

    for v in vals:
        if v > base:
            target = v
            break

    idx = [i for i,v in enumerate(vals) if abs(v-target) < 1e-6]

    return vecs[:,idx][:,0]


def transport(vec, cycle):

    v = vec.copy()

    for i in range(len(cycle)-1):
        a = cycle[i]
        b = cycle[i+1]
        v[a], v[b] = v[b], v[a]

    return v


def angle(v0, v1):

    dot = np.dot(v0, v1)
    n = np.linalg.norm(v0)*np.linalg.norm(v1)

    return np.degrees(np.arccos(dot/n))


def main():

    print("="*80)
    print("CYCLE HOLONOMY SCAN")
    print("="*80)

    G = load_graph()

    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())

    vals, vecs = compute_modes(G)
    mode = first_excited(vals, vecs)

    cycles = nx.cycle_basis(G)

    print()
    print("cycle count:", len(cycles))
    print()

    results = []

    for c in cycles:

        cycle = c + [c[0]]

        v2 = transport(mode, cycle)

        ang = angle(mode, v2)

        results.append((len(c), ang))

        print("cycle length:", len(c), " angle:", round(ang,3))

    print()
    print("SUMMARY")
    print("-"*40)

    bylen = {}

    for L,a in results:
        bylen.setdefault(L, []).append(a)

    for L in sorted(bylen):

        vals = bylen[L]

        print(
            "len",L,
            "mean angle", round(np.mean(vals),3),
            "count", len(vals)
        )

    print("="*80)


if __name__ == "__main__":
    main()

