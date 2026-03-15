from __future__ import annotations

from collections import Counter
from pathlib import Path
import numpy as np
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = [
    ROOT / "reports" / "true_quotients" / "true_chamber_graph.g6",
    ROOT / "artifacts" / "census" / "thalean_graph.g6",
]

def load_graph() -> nx.Graph:
    for path in CANDIDATES:
        if path.exists():
            print(f"loading: {path}")
            return nx.read_graph6(path)
    raise FileNotFoundError("Could not find Thalean graph .g6")

def main():
    G = load_graph()
    print(f"|V|={G.number_of_nodes()} |E|={G.number_of_edges()}")
    print(f"degree set = {sorted(set(dict(G.degree()).values()))}")
    print(f"connected = {nx.is_connected(G)}")
    print(f"bipartite = {nx.is_bipartite(G)}")

    A = nx.to_numpy_array(G, dtype=float)
    eigs = np.linalg.eigvalsh(A)
    rounded = [round(float(x), 12) for x in eigs]
    mults = Counter(rounded)

    print("\nadjacency spectrum (rounded to 12 dp):")
    for lam in sorted(mults):
        print(f"{lam: .12f}  x{mults[lam]}")

    print("\nlargest eigenvalue:", float(eigs[-1]))
    print("smallest eigenvalue:", float(eigs[0]))
    print("spectral gap:", float(eigs[-1] - eigs[-2]))

    # trace moments
    trA2 = float(np.trace(A @ A))
    trA3 = float(np.trace(A @ A @ A))
    trA4 = float(np.trace(A @ A @ A @ A))
    trA5 = float(np.trace(A @ A @ A @ A @ A))
    trA6 = float(np.trace(A @ A @ A @ A @ A @ A))

    print("\ntrace moments:")
    print("tr(A^2) =", trA2)
    print("tr(A^3) =", trA3)
    print("tr(A^4) =", trA4)
    print("tr(A^5) =", trA5)
    print("tr(A^6) =", trA6)

    # check for integrality / algebraic patterns
    roots5 = [(1 + np.sqrt(5)) / 2, (1 - np.sqrt(5)) / 2,
              (-1 + np.sqrt(5)) / 2, (-1 - np.sqrt(5)) / 2]
    print("\nclosest matches to common algebraic values:")
    common = [3, 2, 1, 0, -1, -2, -3] + roots5
    for c in common:
        closest = min(eigs, key=lambda x: abs(x - c))
        print(f"target {c: .12f} -> closest {float(closest): .12f}  delta={abs(float(closest-c)):.3e}")

if __name__ == "__main__":
    main()
