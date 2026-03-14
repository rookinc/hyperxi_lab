#!/usr/bin/env python3

"""
Test whether chamber holonomy rotations admit a natural SU(2)-style lift.

Current approach:
1. load the chamber graph
2. compute the first excited Laplacian eigenspace
3. extract orthogonal holonomy Q(gamma) on that eigenspace for simple 5- and 10-cycles
4. convert each SO(3)-type rotation into axis-angle data
5. build the corresponding SU(2) lift candidate
6. report half-angle structure and whether loop doubling is closer to identity

This does not prove a physical spin structure.
It is a structural probe for whether the observed chamber holonomy
naturally wants a double-cover interpretation.
"""

from __future__ import annotations

import networkx as nx
import numpy as np


# ------------------------------------------------------------
# graph loader
# ------------------------------------------------------------

def load_graph() -> nx.Graph:
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
# spectral helpers
# ------------------------------------------------------------

def compute_laplacian_modes(G: nx.Graph) -> tuple[np.ndarray, np.ndarray]:
    A = nx.to_numpy_array(G, dtype=float)
    deg = np.sum(A, axis=1)
    L = np.diag(deg) - A
    vals, vecs = np.linalg.eigh(L)
    return vals, vecs


def first_excited_eigenspace(
    vals: np.ndarray,
    vecs: np.ndarray,
    tol: float = 1e-8,
) -> tuple[float, list[int], np.ndarray]:
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

    return float(target), idx, basis


# ------------------------------------------------------------
# loop operators
# ------------------------------------------------------------

def loop_permutation_matrix(n: int, cycle: list[int]) -> np.ndarray:
    P = np.eye(n, dtype=float)

    for i in range(len(cycle) - 1):
        a = cycle[i]
        b = cycle[i + 1]

        S = np.eye(n, dtype=float)
        S[[a, b], :] = S[[b, a], :]
        P = S @ P

    return P


def induced_action_on_subspace(P: np.ndarray, basis: np.ndarray) -> np.ndarray:
    return basis.T @ P @ basis


def polar_rotation(M: np.ndarray) -> np.ndarray:
    U, _, Vt = np.linalg.svd(M)
    return U @ Vt


# ------------------------------------------------------------
# cycle enumeration
# ------------------------------------------------------------

def canonical_cycle(cycle: list[int]) -> tuple[int, ...]:
    n = len(cycle)
    rots = []
    for seq in (cycle, list(reversed(cycle))):
        for i in range(n):
            rots.append(tuple(seq[i:] + seq[:i]))
    return min(rots)


def simple_cycles_of_length(G: nx.Graph, target_len: int) -> list[list[int]]:
    nodes = sorted(G.nodes())
    seen: set[tuple[int, ...]] = set()
    out: list[list[int]] = []

    for start in nodes:
        stack: list[tuple[int, list[int], set[int]]] = [(start, [start], {start})]

        while stack:
            current, path, used = stack.pop()

            if len(path) == target_len:
                if G.has_edge(current, start):
                    cyc = canonical_cycle(path)
                    if cyc not in seen:
                        seen.add(cyc)
                        out.append(list(cyc))
                continue

            for nxt in G.neighbors(current):
                if nxt < start:
                    continue
                if nxt in used:
                    continue
                stack.append((nxt, path + [nxt], used | {nxt}))

    out.sort()
    return out


# ------------------------------------------------------------
# SO(3) -> axis-angle
# ------------------------------------------------------------

def rotation_angle_so3(Q: np.ndarray) -> float:
    x = (float(np.trace(Q)) - 1.0) / 2.0
    x = max(-1.0, min(1.0, x))
    return float(np.arccos(x))


def rotation_axis_so3(Q: np.ndarray, theta: float) -> np.ndarray:
    """
    For small nonzero theta, recover axis from antisymmetric part:
        axis ~ (Q32-Q23, Q13-Q31, Q21-Q12) / (2 sin theta)
    """
    if abs(np.sin(theta)) < 1e-10:
        return np.array([1.0, 0.0, 0.0], dtype=float)

    axis = np.array([
        Q[2, 1] - Q[1, 2],
        Q[0, 2] - Q[2, 0],
        Q[1, 0] - Q[0, 1],
    ], dtype=float) / (2.0 * np.sin(theta))

    n = np.linalg.norm(axis)
    if n < 1e-12:
        return np.array([1.0, 0.0, 0.0], dtype=float)

    return axis / n


# ------------------------------------------------------------
# SU(2) lift candidate
# ------------------------------------------------------------

def pauli_matrices() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    return sx, sy, sz


def su2_from_axis_angle(axis: np.ndarray, theta: float) -> np.ndarray:
    """
    U = cos(theta/2) I - i sin(theta/2) (n · sigma)
    """
    sx, sy, sz = pauli_matrices()
    I = np.eye(2, dtype=complex)

    nx_, ny_, nz_ = axis
    sigma_n = nx_ * sx + ny_ * sy + nz_ * sz

    return np.cos(theta / 2.0) * I - 1j * np.sin(theta / 2.0) * sigma_n


def distance_to_identity(U: np.ndarray) -> float:
    I = np.eye(U.shape[0], dtype=complex)
    return float(np.linalg.norm(U - I))


def distance_to_neg_identity(U: np.ndarray) -> float:
    I = np.eye(U.shape[0], dtype=complex)
    return float(np.linalg.norm(U + I))


# ------------------------------------------------------------
# main analysis
# ------------------------------------------------------------

def analyze_cycles(G: nx.Graph, basis: np.ndarray, target_len: int) -> None:
    cycles = simple_cycles_of_length(G, target_len)

    print()
    print("=" * 80)
    print(f"SPIN-LIFT CANDIDATE TEST ON CYCLES OF LENGTH {target_len}")
    print("=" * 80)
    print("count:", len(cycles))

    if not cycles:
        print("No cycles of this length found.")
        return

    thetas_deg: list[float] = []
    half_thetas_deg: list[float] = []
    d_id_list: list[float] = []
    d_neg_list: list[float] = []
    d_double_id_list: list[float] = []

    for cyc in cycles:
        loop = cyc + [cyc[0]]

        P = loop_permutation_matrix(G.number_of_nodes(), loop)
        M = induced_action_on_subspace(P, basis)
        Q = polar_rotation(M)

        theta = rotation_angle_so3(Q)
        axis = rotation_axis_so3(Q, theta)
        U = su2_from_axis_angle(axis, theta)
        U2 = U @ U

        theta_deg = float(np.degrees(theta))
        half_deg = float(np.degrees(theta / 2.0))

        d_id = distance_to_identity(U)
        d_neg = distance_to_neg_identity(U)
        d_double_id = distance_to_identity(U2)

        thetas_deg.append(theta_deg)
        half_thetas_deg.append(half_deg)
        d_id_list.append(d_id)
        d_neg_list.append(d_neg)
        d_double_id_list.append(d_double_id)

        print("-" * 80)
        print("cycle:", loop)
        print("SO(3) angle:", round(theta_deg, 6), "deg")
        print("axis:", np.round(axis, 6))
        print("SU(2) half-angle:", round(half_deg, 6), "deg")
        print("eig(Q):", np.round(np.linalg.eigvals(Q), 6))
        print("eig(U):", np.round(np.linalg.eigvals(U), 6))
        print("||U - I||   =", round(d_id, 6))
        print("||U + I||   =", round(d_neg, 6))
        print("||U^2 - I|| =", round(d_double_id, 6))
        print("U:")
        print(np.round(U, 6))

    print()
    print("SUMMARY")
    print("-" * 80)
    print(f"length {target_len}:")
    print(f"  mean SO(3) angle      : {np.mean(thetas_deg):.6f} deg")
    print(f"  mean SU(2) half-angle : {np.mean(half_thetas_deg):.6f} deg")
    print(f"  mean ||U - I||        : {np.mean(d_id_list):.6f}")
    print(f"  mean ||U + I||        : {np.mean(d_neg_list):.6f}")
    print(f"  mean ||U^2 - I||      : {np.mean(d_double_id_list):.6f}")


def main() -> None:
    print("=" * 80)
    print("DOUBLE-COVER HOLONOMY TEST")
    print("=" * 80)

    G = load_graph()
    vals, vecs = compute_laplacian_modes(G)
    lam1, idx, basis = first_excited_eigenspace(vals, vecs)

    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("first excited eigenvalue:", lam1)
    print("indices:", idx)
    print("eigenspace dimension:", basis.shape[1])

    if basis.shape[1] != 3:
        print()
        print("Warning: first excited eigenspace is not 3D.")
        print("This SU(2)-lift probe is designed for a 3D SO(3)-type sector.")

    analyze_cycles(G, basis, target_len=5)
    analyze_cycles(G, basis, target_len=10)

    print("=" * 80)


if __name__ == "__main__":
    main()
