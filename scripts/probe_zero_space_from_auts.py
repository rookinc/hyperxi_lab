from __future__ import annotations

import itertools
from pathlib import Path
import numpy as np
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
G_PATHS = [
    ROOT / "reports" / "true_quotients" / "true_chamber_graph.g6",
    ROOT / "artifacts" / "census" / "thalean_graph.g6",
]

def load_graph():
    for p in G_PATHS:
        if p.exists():
            print(f"loading: {p}")
            return nx.read_graph6(p)
    raise FileNotFoundError("No G60 graph found")

def permutation_matrix(mapping, n):
    P = np.zeros((n, n), dtype=float)
    for i in range(n):
        P[mapping[i], i] = 1.0
    return P

def zero_basis(A, tol=1e-9):
    vals, vecs = np.linalg.eigh(A)
    idx = [i for i, v in enumerate(vals) if abs(v) < tol]
    return vals, vecs[:, idx]

def main():
    G = load_graph()
    A = nx.to_numpy_array(G, dtype=float)
    vals, Z = zero_basis(A)
    print(f"zero eigenspace dimension = {Z.shape[1]}")

    gm = nx.algorithms.isomorphism.GraphMatcher(G, G)
    autos = []
    for i, mapping in enumerate(gm.isomorphisms_iter()):
        autos.append(mapping)
        if len(autos) >= 12:
            break

    print(f"sampled automorphisms: {len(autos)}")

    for k, mapping in enumerate(autos):
        P = permutation_matrix(mapping, G.number_of_nodes())
        M = Z.T @ P @ Z
        evals = np.linalg.eigvals(M)
        evals = sorted((complex(x) for x in evals), key=lambda z: (round(z.real, 8), round(z.imag, 8)))
        print(f"\nautomorphism {k}")
        print("trace on zero space =", round(float(np.trace(M)), 8))
        print("det on zero space   =", round(float(np.linalg.det(M)), 8))
        print("eigenvalues:")
        for x in evals:
            if abs(x.imag) < 1e-8:
                print(" ", round(x.real, 8))
            else:
                print(" ", complex(round(x.real, 8), round(x.imag, 8)))

if __name__ == "__main__":
    main()
