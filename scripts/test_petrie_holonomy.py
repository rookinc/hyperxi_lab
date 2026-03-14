#!/usr/bin/env python3

"""
Test eigenspace holonomy on geometrically meaningful loops.

Current version:
- loads the chamber graph
- computes Laplacian modes
- extracts the first excited eigenspace
- scans all simple cycles of a chosen target length
- computes the orthogonal holonomy (polar factor) on that eigenspace
- reports trace / determinant / eigenvalues / rotation angle

Start with target_len=5 for pentagons.
Then try target_len=10 if your graph actually contains Petrie decagons.
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


def rotation_angle_so3(Q: np.ndarray) -> float:
    x = (float(np.trace(Q)) - 1.0) / 2.0
    x = max(-1.0, min(1.0, x))
    return float(np.degrees(np.arccos(x)))


def classify_matrix(Q: np.ndarray, tol: float = 1e-6) -> str:
    I = np.eye(Q.shape[0])
    if np.allclose(Q, I, atol=tol):
        return "identity"
    if np.allclose(Q, -I, atol=tol):
        return "global sign flip"
    det = float(np.linalg.det(Q))
    if abs(det - 1.0) < 1e-3:
        return "rotation"
    if abs(det + 1.0) < 1e-3:
        return "reflection-like"
    return "general"


# ------------------------------------------------------------
# cycle enumeration
# ------------------------------------------------------------

def canonical_cycle(cycle: list[int]) -> tuple[int, ...]:
    """
    Canonicalize an undirected simple cycle up to rotation and reversal.
    Input should NOT repeat the first vertex at the end.
    """
    n = len(cycle)
    rots = []
    for seq in (cycle, list(reversed(cycle))):
        for i in range(n):
            rots.append(tuple(seq[i:] + seq[:i]))
    return min(rots)


def simple_cycles_of_length(G: nx.Graph, target_len: int) -> list[list[int]]:
    """
    Enumerate simple undirected cycles of a given length by DFS.
    Suitable for small target lengths like 5 or 6 on this graph size.
    """
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
# reporting
# ------------------------------------------------------------

def analyze_cycles(G: nx.Graph, basis: np.ndarray, target_len: int) -> None:
    cycles = simple_cycles_of_length(G, target_len)

    print()
    print("=" * 80)
    print(f"HOLONOMY ON SIMPLE CYCLES OF LENGTH {target_len}")
    print("=" * 80)
    print(f"count: {len(cycles)}")

    if not cycles:
        print("No cycles of this length found.")
        return

    angles: list[float] = []

    for cyc in cycles:
        loop = cyc + [cyc[0]]
        P = loop_permutation_matrix(G.number_of_nodes(), loop)
        M = induced_action_on_subspace(P, basis)
        Q = polar_rotation(M)

        det = float(np.linalg.det(Q))
        tr = float(np.trace(Q))
        eigvals = np.linalg.eigvals(Q)
        angle = rotation_angle_so3(Q)
        angles.append(angle)

        print("-" * 80)
        print("cycle:", loop)
        print("class:", classify_matrix(Q))
        print("trace:", np.round(tr, 6))
        print("det:", np.round(det, 6))
        print("eigvals:", np.round(eigvals, 6))
        print("angle:", round(angle, 6), "degrees")
        print("Q:")
        print(np.round(Q, 6))

    arr = np.array(angles, dtype=float)
    print()
    print("SUMMARY")
    print("-" * 80)
    print(f"length {target_len}:")
    print(f"  mean angle: {arr.mean():.6f}")
    print(f"  min angle : {arr.min():.6f}")
    print(f"  max angle : {arr.max():.6f}")
    print(f"  std dev   : {arr.std():.6f}")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------

def main() -> None:
    print("=" * 80)
    print("PETRIE / PENTAGON HOLONOMY TEST")
    print("=" * 80)

    G = load_graph()
    vals, vecs = compute_laplacian_modes(G)
    lam1, idx, basis = first_excited_eigenspace(vals, vecs)

    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("first excited eigenvalue:", lam1)
    print("indices:", idx)
    print("eigenspace dimension:", basis.shape[1])

    # Start with pentagons.
    analyze_cycles(G, basis, target_len=5)

    # Then try 10-cycles. Depending on the graph, this may be empty.
    analyze_cycles(G, basis, target_len=10)

    print("=" * 80)


if __name__ == "__main__":
    main()
