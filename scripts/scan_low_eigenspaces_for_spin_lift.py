#!/usr/bin/env python3

"""
Scan low Laplacian eigenspaces of the chamber graph for spin-lift candidates.

For each low nontrivial eigenspace:
1. enumerate simple 5-cycles and 10-cycles
2. project loop permutations to that eigenspace
3. if the eigenspace is 3D, extract SO(3)-type holonomy and build an SU(2) lift
4. rank sectors by how close any loop gets to a nontrivial spin-like signal

This is a search script, not a proof script.
"""

from __future__ import annotations

import math
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


def eigenspace_blocks(vals: np.ndarray, tol: float = 1e-8) -> list[tuple[float, list[int]]]:
    blocks: list[tuple[float, list[int]]] = []
    used = np.zeros(len(vals), dtype=bool)

    for i, v in enumerate(vals):
        if used[i]:
            continue
        idx = [j for j, w in enumerate(vals) if abs(w - v) <= tol]
        for j in idx:
            used[j] = True
        blocks.append((float(v), idx))

    return blocks


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
# SO(3) / SU(2) helpers
# ------------------------------------------------------------

def rotation_angle_so3(Q: np.ndarray) -> float:
    x = (float(np.trace(Q)) - 1.0) / 2.0
    x = max(-1.0, min(1.0, x))
    return float(np.arccos(x))


def rotation_axis_so3(Q: np.ndarray, theta: float) -> np.ndarray:
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


def pauli_matrices() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    return sx, sy, sz


def su2_from_axis_angle(axis: np.ndarray, theta: float) -> np.ndarray:
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


def classify_u2_behavior(U: np.ndarray) -> str:
    d_id = distance_to_identity(U)
    d_neg = distance_to_neg_identity(U)
    d2_id = distance_to_identity(U @ U)

    if d_neg < 0.2:
        return "near_minus_identity"
    if d2_id < d_id:
        return "double_loop_improves"
    return "near_identity_or_generic"


# ------------------------------------------------------------
# scan logic
# ------------------------------------------------------------

def analyze_3d_sector(
    G: nx.Graph,
    basis: np.ndarray,
    cycles5: list[list[int]],
    cycles10: list[list[int]],
) -> dict:
    best_neg = math.inf
    best_cycle: tuple[int, list[int]] | None = None
    best_u: np.ndarray | None = None
    best_theta = None

    mean_theta5 = []
    mean_theta10 = []
    mean_u_id_5 = []
    mean_u_id_10 = []

    for L, cycles in ((5, cycles5), (10, cycles10)):
        for cyc in cycles:
            loop = cyc + [cyc[0]]
            P = loop_permutation_matrix(G.number_of_nodes(), loop)
            M = induced_action_on_subspace(P, basis)
            Q = polar_rotation(M)

            theta = rotation_angle_so3(Q)
            axis = rotation_axis_so3(Q, theta)
            U = su2_from_axis_angle(axis, theta)

            d_neg = distance_to_neg_identity(U)
            d_id = distance_to_identity(U)

            if d_neg < best_neg:
                best_neg = d_neg
                best_cycle = (L, cyc)
                best_u = U
                best_theta = float(np.degrees(theta))

            if L == 5:
                mean_theta5.append(float(np.degrees(theta)))
                mean_u_id_5.append(d_id)
            else:
                mean_theta10.append(float(np.degrees(theta)))
                mean_u_id_10.append(d_id)

    return {
        "best_neg_distance": best_neg,
        "best_cycle": best_cycle,
        "best_u": best_u,
        "best_theta_deg": best_theta,
        "mean_theta5": float(np.mean(mean_theta5)) if mean_theta5 else None,
        "mean_theta10": float(np.mean(mean_theta10)) if mean_theta10 else None,
        "mean_u_id_5": float(np.mean(mean_u_id_5)) if mean_u_id_5 else None,
        "mean_u_id_10": float(np.mean(mean_u_id_10)) if mean_u_id_10 else None,
    }


def main() -> None:
    print("=" * 80)
    print("SCAN LOW EIGENSPACES FOR SPIN-LIFT CANDIDATES")
    print("=" * 80)

    G = load_graph()
    vals, vecs = compute_laplacian_modes(G)
    blocks = eigenspace_blocks(vals)

    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("eigenspace blocks:", len(blocks))
    print()

    print("enumerating 5-cycles...")
    cycles5 = simple_cycles_of_length(G, 5)
    print("count(5-cycles):", len(cycles5))

    print("enumerating 10-cycles...")
    cycles10 = simple_cycles_of_length(G, 10)
    print("count(10-cycles):", len(cycles10))
    print()

    results = []

    # Skip the ground block at index 0
    for block_id, (lam, idx) in enumerate(blocks[1:12], start=1):
        mult = len(idx)
        basis = np.array(vecs[:, idx], dtype=float)

        print("-" * 80)
        print(f"block {block_id}")
        print("eigenvalue:", lam)
        print("multiplicity:", mult)

        row = {
            "block": block_id,
            "eigenvalue": lam,
            "multiplicity": mult,
        }

        if mult == 3:
            info = analyze_3d_sector(G, basis, cycles5, cycles10)
            row.update(info)

            print("mean theta (5):", info["mean_theta5"])
            print("mean theta (10):", info["mean_theta10"])
            print("mean ||U-I|| (5):", info["mean_u_id_5"])
            print("mean ||U-I|| (10):", info["mean_u_id_10"])
            print("best ||U+I||^-candidate:", info["best_neg_distance"])
            print("best cycle:", info["best_cycle"])
            print("best SO(3) angle:", info["best_theta_deg"])

            if info["best_u"] is not None:
                print("best U behavior:", classify_u2_behavior(info["best_u"]))
                print("best U:")
                print(np.round(info["best_u"], 6))
        else:
            print("skipping SU(2) scan: multiplicity is not 3")

        results.append(row)

    print()
    print("=" * 80)
    print("RANKING OF 3D SECTORS BY CLOSENESS TO -I")
    print("=" * 80)

    ranked = [
        r for r in results
        if r.get("multiplicity") == 3 and r.get("best_neg_distance") is not None
    ]
    ranked.sort(key=lambda r: r["best_neg_distance"])

    for r in ranked:
        print(
            f"block={r['block']:2d} "
            f"lambda={r['eigenvalue']:.12f} "
            f"best||U+I||={r['best_neg_distance']:.6f} "
            f"best_cycle={r['best_cycle']} "
            f"best_theta={r['best_theta_deg']}"
        )

    print("=" * 80)


if __name__ == "__main__":
    main()
