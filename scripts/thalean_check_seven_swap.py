#!/usr/bin/env python3

from pathlib import Path
from collections import Counter
import numpy as np
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
G6_PATH = ROOT / "artifacts/census/thalion_graph.g6"


def load_graph():
    g6 = G6_PATH.read_text(encoding="utf-8").strip()
    G = nx.from_graph6_bytes(g6.encode())
    return nx.convert_node_labels_to_integers(G)


def shell_counts(G, root):
    dist = nx.single_source_shortest_path_length(G, root)
    counts = Counter(dist.values())
    return [counts[k] for k in sorted(counts)], dist


def build_local_basis(G, root):
    """
    Local address space = root + its 4 neighbors, doubled by parity.
    We model an 8-state neighborhood by taking the 4 neighbors with two sheets.
    Basis ordering:
      n0+, n1+, n2+, n3+, n0-, n1-, n2-, n3-
    """
    nbrs = sorted(G.neighbors(root))
    if len(nbrs) != 4:
        raise ValueError("Root must have degree 4")
    return nbrs


def swap_operator_8():
    S = np.zeros((8, 8), dtype=float)
    for i in range(4):
        S[i, i + 4] = 1.0
        S[i + 4, i] = 1.0
    return S


def parity_projectors(S):
    I = np.eye(S.shape[0])
    Pp = 0.5 * (I + S)
    Pm = 0.5 * (I - S)
    return Pp, Pm


def local_preserve_swap_modes():
    """
    Construct canonical local vectors:
      - preserve-uniform: all + on both sheets
      - swap mode: + on one sheet, - on the other
    """
    preserve = np.ones(8, dtype=float)
    preserve /= np.linalg.norm(preserve)

    swap = np.array([1, 1, 1, 1, -1, -1, -1, -1], dtype=float)
    swap /= np.linalg.norm(swap)

    return preserve, swap


def orthonormal_complement(vectors, n=8):
    """
    Gram-Schmidt against supplied vectors, starting from standard basis.
    """
    basis = []
    for v in vectors:
        w = v.astype(float).copy()
        for b in basis:
            w -= np.dot(w, b) * b
        norm = np.linalg.norm(w)
        if norm > 1e-10:
            basis.append(w / norm)

    for i in range(n):
        e = np.zeros(n, dtype=float)
        e[i] = 1.0
        w = e.copy()
        for b in basis:
            w -= np.dot(w, b) * b
        norm = np.linalg.norm(w)
        if norm > 1e-10:
            basis.append(w / norm)

    return basis


def main():
    G = load_graph()
    root = 0
    shells, dist = shell_counts(G, root)
    nbrs = build_local_basis(G, root)

    print("=" * 80)
    print("THALEAN CHECK SEVEN / SWAP")
    print("=" * 80)
    print("root:", root)
    print("neighbors:", nbrs)
    print("shells:", shells)
    print()

    # 8-state local doubled frame
    S = swap_operator_8()
    Pp, Pm = parity_projectors(S)
    preserve, swap = local_preserve_swap_modes()

    print("8-STATE LOCAL DOUBLED FRAME")
    print("-" * 80)
    print("Interpretation: 4 local addresses x 2 sheets = 8 states")
    print()

    print("SWAP OPERATOR EIGENSTRUCTURE")
    print("-" * 80)
    vals, vecs = np.linalg.eigh(S)
    counts = Counter(np.round(vals, 6))
    for lam, mult in sorted(counts.items()):
        print(f"eigenvalue {lam:+.1f}  multiplicity {mult}")
    print()

    # Project canonical vectors
    pp = Pp @ preserve
    pm = Pm @ preserve
    sp = Pp @ swap
    sm = Pm @ swap

    print("CANONICAL LOCAL MODES")
    print("-" * 80)
    print("preserve-uniform vector:")
    print(np.round(preserve, 6))
    print("swap vector:")
    print(np.round(swap, 6))
    print()

    print("project preserve-uniform into + / - parity:")
    print("||P+ preserve|| =", round(float(np.linalg.norm(pp)), 6))
    print("||P- preserve|| =", round(float(np.linalg.norm(pm)), 6))
    print()

    print("project swap vector into + / - parity:")
    print("||P+ swap|| =", round(float(np.linalg.norm(sp)), 6))
    print("||P- swap|| =", round(float(np.linalg.norm(sm)), 6))
    print()

    # Build a basis where first vector is preserve-uniform and second is swap
    basis = orthonormal_complement([preserve, swap], n=8)

    print("DIMENSION COUNT")
    print("-" * 80)
    print("total local doubled space =", 8)
    print("distinguished preserve-uniform direction =", 1)
    print("distinguished swap direction =", 1)
    print("remaining orthogonal complement =", 8 - 2)
    print()

    print("SEVEN-SPACE CHECK")
    print("-" * 80)
    print("If you treat the swap vector as the special correction channel,")
    print("then the orthogonal complement to that single mode has dimension 7.")
    print("That is:")
    print("  8 total local doubled states")
    print("  1 distinguished swap-like mode")
    print("  7-dimensional complementary transport space")
    print()

    # Explicit projector onto complement of swap
    Ps = np.outer(swap, swap)
    P7 = np.eye(8) - Ps
    rank7 = int(round(np.trace(P7)))

    print("rank of complement-to-swap projector =", rank7)
    print()

    print("INTERPRETATION")
    print("-" * 80)
    print("This does NOT prove a canonical global 7-dimensional eigenspace of the")
    print("full Thalean graph. It does show that in the natural local doubled frame")
    print("(4 addresses x 2 sheets), there is a distinguished 1-dimensional swap")
    print("direction and therefore a natural 7-dimensional complementary space.")
    print("So the intuition '7 is the swap-space complement' is mathematically")
    print("coherent at the local state-space level.")


if __name__ == "__main__":
    main()
