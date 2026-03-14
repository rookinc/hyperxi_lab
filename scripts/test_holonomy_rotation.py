#!/usr/bin/env python3

import networkx as nx
import numpy as np


# ------------------------------------------------------------
# graph loader
# ------------------------------------------------------------

def load_graph():
    from hyperxi.combinatorics.chamber_graph import build_chamber_graph
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


# ------------------------------------------------------------
# spectral helpers
# ------------------------------------------------------------

def laplacian_modes(G):

    A = nx.to_numpy_array(G)
    deg = A.sum(axis=1)

    L = np.diag(deg) - A

    vals, vecs = np.linalg.eigh(L)

    return vals, vecs


def first_excited(vals, vecs, tol=1e-8):

    base = vals[0]

    lam = None
    for v in vals:
        if v > base + tol:
            lam = v
            break

    idx = [i for i,v in enumerate(vals) if abs(v-lam) < tol]

    return lam, vecs[:,idx]


# ------------------------------------------------------------
# permutation from loop
# ------------------------------------------------------------

def loop_perm(n, cycle):

    P = np.eye(n)

    for i in range(len(cycle)-1):

        a = cycle[i]
        b = cycle[i+1]

        S = np.eye(n)
        S[[a,b],:] = S[[b,a],:]

        P = S @ P

    return P


# ------------------------------------------------------------
# polar decomposition
# ------------------------------------------------------------

def polar_rotation(M):

    U, s, Vt = np.linalg.svd(M)

    Q = U @ Vt   # orthogonal part

    return Q


# ------------------------------------------------------------
# rotation angle
# ------------------------------------------------------------

def rotation_angle(Q):

    tr = np.trace(Q)

    x = (tr - 1) / 2

    x = max(-1,min(1,x))

    return np.degrees(np.arccos(x))


# ------------------------------------------------------------
# main
# ------------------------------------------------------------

def main():

    print("="*80)
    print("PURE HOLONOMY ROTATION TEST")
    print("="*80)

    G = load_graph()

    vals, vecs = laplacian_modes(G)

    lam1, basis = first_excited(vals,vecs)

    print("first excited eigenvalue:",lam1)
    print("eigenspace dimension:",basis.shape[1])

    cycles = nx.cycle_basis(G)

    angles = []

    for c in cycles:

        loop = c + [c[0]]

        P = loop_perm(G.number_of_nodes(),loop)

        M = basis.T @ P @ basis

        Q = polar_rotation(M)

        angle = rotation_angle(Q)

        angles.append((len(c),angle))

        print("--------------------------------")
        print("cycle length:",len(c))
        print("rotation angle:",round(angle,3))
        print("Q=")
        print(np.round(Q,5))

    print("\nSUMMARY")

    bylen = {}

    for L,a in angles:
        bylen.setdefault(L,[]).append(a)

    for L in sorted(bylen):

        arr = np.array(bylen[L])

        print(
            "len",
            L,
            "mean angle",
            round(arr.mean(),3),
            "count",
            len(arr)
        )

    print("="*80)


if __name__=="__main__":
    main()
