#!/usr/bin/env python3

"""
Thalion Sector Projector Probe

Decompose a lifted 60-state wave into symmetric and antisymmetric sectors
using the sheet-swap operator.

ψ = ψ_sym + ψ_anti

ψ_sym  = (I + Σ)/2 ψ
ψ_anti = (I - Σ)/2 ψ
"""

from pathlib import Path
import numpy as np
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]

GRAPH_PATH = ROOT / "artifacts/census/thalion_graph.g6"

STEPS = 18
C2 = 0.5


def load_graph():
    return nx.from_graph6_bytes(GRAPH_PATH.read_bytes())


def adjacency_matrix(g):
    return nx.to_numpy_array(g, dtype=float)


def build_swap_operator(n):
    """
    Swap sheets of the 2-lift
    """
    half = n // 2
    S = np.zeros((n, n))

    for i in range(half):
        S[i, i + half] = 1
        S[i + half, i] = 1

    return S


def sector_projectors(S):
    n = S.shape[0]
    I = np.eye(n)

    P_sym = 0.5 * (I + S)
    P_anti = 0.5 * (I - S)

    return P_sym, P_anti


def evolve(A, psi0):
    n = A.shape[0]
    L = 4 * np.eye(n) - A

    psi_prev = psi0.copy()
    psi_curr = psi0.copy()

    states = [psi0]

    for _ in range(STEPS):
        psi_next = 2 * psi_curr - psi_prev - C2 * (L @ psi_curr)

        states.append(psi_next)

        psi_prev, psi_curr = psi_curr, psi_next

    return states


def energy(psi):
    return float(np.sum(psi * psi))


def main():

    g = load_graph()

    A = adjacency_matrix(g)

    n = A.shape[0]

    S = build_swap_operator(n)

    P_sym, P_anti = sector_projectors(S)

    psi0 = np.zeros(n)
    psi0[0] = 1

    psi_sym = P_sym @ psi0
    psi_anti = P_anti @ psi0

    states_full = evolve(A, psi0)
    states_sym = evolve(A, psi_sym)
    states_anti = evolve(A, psi_anti)

    print("="*70)
    print("THALION SECTOR PROJECTOR PROBE")
    print("="*70)

    print("\ninitial decomposition")
    print("sym energy :", energy(psi_sym))
    print("anti energy:", energy(psi_anti))

    print("\nenergy evolution")
    print("t   full      sym       anti")

    for t in range(len(states_full)):

        ef = energy(states_full[t])
        es = energy(states_sym[t])
        ea = energy(states_anti[t])

        print(f"{t:2d}  {ef:8.6f}  {es:8.6f}  {ea:8.6f}")


if __name__ == "__main__":
    main()
