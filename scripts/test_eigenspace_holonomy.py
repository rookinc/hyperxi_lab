#!/usr/bin/env python3

"""
Test loop holonomy on the full first-excited eigenspace.

Instead of transporting a single arbitrary eigenvector, this script:
1. loads the chamber graph
2. computes Laplacian eigenmodes
3. extracts the first excited eigenspace
4. builds the induced transport matrix on that eigenspace for each cycle
5. reports trace / determinant / eigenvalues / approximate rotation angle

This is a better probe for spinorial or gauge-like behavior than
tracking one basis vector.
"""

import networkx as nx
import numpy as np


# ------------------------------------------------------------
# Graph loader
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

    if hasattr(CG, "edges"):
        G = nx.Graph()
        G.add_edges_from(CG.edges)
        return G

    raise RuntimeError("Could not extract graph from ChamberGraph")


# ------------------------------------------------------------
# Spectral helpers
# ------------------------------------------------------------

def compute_laplacian_modes(G):

    A = nx.to_numpy_array(G, dtype=float)
    deg = np.sum(A, axis=1)
    L = np.diag(deg) - A

    vals, vecs = np.linalg.eigh(L)
    return vals, vecs


def first_excited_eigenspace(vals, vecs, tol=1e-8):

    base = vals[0]
    target = None

    for v in vals:
        if v > base + tol:
            target = v
            break

    if target is None:
        raise RuntimeError("Could not find first excited eigenvalue.")

    idx = [i for i, v in enumerate(vals) if abs(v - target) <= tol]
    basis = np.array(vecs[:, idx], dtype=float)

    return target, idx, basis


# ------------------------------------------------------------
# Transport operator from loop
# ------------------------------------------------------------

def loop_permutation_matrix(n, cycle):

    P = np.eye(n, dtype=float)

    for i in range(len(cycle) - 1):
        a = cycle[i]
        b = cycle[i + 1]

        # swap rows in the permutation action
        S = np.eye(n, dtype=float)
        S[[a, b], :] = S[[b, a], :]
        P = S @ P

    return P


def induced_action_on_subspace(P, basis):

    # basis is n x k with orthonormal columns from eigh
    # induced operator in that basis is B^T P B
    return basis.T @ P @ basis


# ------------------------------------------------------------
# Cycle analysis
# ------------------------------------------------------------

def real_angle_from_trace(M, tol=1e-10):
    """
    For 2x2 rotation blocks, cos(theta) = tr(M)/2.
    For higher dimensions, this is only heuristic.
    """
    k = M.shape[0]
    if k == 1:
        val = float(M[0, 0])
        if abs(val - 1.0) < tol:
            return 0.0
        if abs(val + 1.0) < tol:
            return 180.0
        return None

    if k == 2:
        x = float(np.trace(M)) / 2.0
        x = max(-1.0, min(1.0, x))
        return float(np.degrees(np.arccos(x)))

    return None


def classify_matrix(M, tol=1e-6):

    I = np.eye(M.shape[0])

    if np.allclose(M, I, atol=tol):
        return "identity"

    if np.allclose(M, -I, atol=tol):
        return "global sign flip"

    det = np.linalg.det(M)
    if abs(det - 1.0) < 1e-3:
        return "orientation-preserving"
    if abs(det + 1.0) < 1e-3:
        return "orientation-reversing"

    return "general"


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():

    print("=" * 80)
    print("EIGENSPACE HOLONOMY TEST")
    print("=" * 80)

    G = load_graph()

    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())

    vals, vecs = compute_laplacian_modes(G)
    lam1, idx, basis = first_excited_eigenspace(vals, vecs)

    n = G.number_of_nodes()
    k = basis.shape[1]

    print()
    print("first excited eigenvalue:", lam1)
    print("indices:", idx)
    print("eigenspace dimension:", k)

    cycles = nx.cycle_basis(G)

    print()
    print("cycle count:", len(cycles))
    print()

    summary = {}

    for c in cycles:
        loop = c + [c[0]]
        P = loop_permutation_matrix(n, loop)
        M = induced_action_on_subspace(P, basis)

        eigvals = np.linalg.eigvals(M)
        det = np.linalg.det(M)
        tr = np.trace(M)
        cls = classify_matrix(M)
        ang = real_angle_from_trace(M)

        print("-" * 80)
        print("cycle:", loop)
        print("length:", len(c))
        print("class:", cls)
        print("trace:", np.round(tr, 6))
        print("det:", np.round(det, 6))
        print("eigvals:", np.round(eigvals, 6))
        if ang is not None:
            print("approx angle:", round(ang, 6), "degrees")
        print("matrix:")
        print(np.round(M, 6))

        summary.setdefault(len(c), {"count": 0, "traces": [], "dets": []})
        summary[len(c)]["count"] += 1
        summary[len(c)]["traces"].append(float(np.real(tr)))
        summary[len(c)]["dets"].append(float(np.real(det)))

    print()
    print("=" * 80)
    print("SUMMARY BY CYCLE LENGTH")
    print("=" * 80)
    for L in sorted(summary):
        data = summary[L]
        print(
            f"len={L:2d} "
            f"count={data['count']:2d} "
            f"mean_trace={np.mean(data['traces']): .6f} "
            f"mean_det={np.mean(data['dets']): .6f}"
        )

    print("=" * 80)


if __name__ == "__main__":
    main()
