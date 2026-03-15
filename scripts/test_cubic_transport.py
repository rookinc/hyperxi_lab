import numpy as np
import networkx as nx
from pathlib import Path

print("=== Cubic Transport Probe ===")

ROOT = Path(__file__).resolve().parents[1]
G6_PATHS = [
    ROOT / "reports" / "true_quotients" / "true_chamber_graph.g6",
    ROOT / "artifacts" / "census" / "thalean_graph.g6",
]

g6_path = None
for p in G6_PATHS:
    if p.exists():
        g6_path = p
        break

if g6_path is None:
    raise FileNotFoundError("Could not find a G60 graph .g6 file in expected locations.")

print(f"loading graph from: {g6_path}")

G = nx.read_graph6(g6_path)
A = nx.to_numpy_array(G, dtype=float)

n = A.shape[0]
I = np.eye(n)

P = 64 * (A @ A @ A) + 64 * (A @ A) + 7 * A - 9 * I

fro_norm = np.linalg.norm(P)
spec_norm = np.linalg.norm(P, ord=2)

print(f"vertices: {G.number_of_nodes()}")
print(f"edges:    {G.number_of_edges()}")
print(f"||64A^3 + 64A^2 + 7A - 9I||_F = {fro_norm}")
print(f"||64A^3 + 64A^2 + 7A - 9I||_2 = {spec_norm}")

eig = np.linalg.eigvalsh(A)

print("\nEigenvalues (rounded):")
for e in eig:
    print(f"{e:.12f}")

poly_vals = 64 * eig**3 + 64 * eig**2 + 7 * eig - 9
max_resid = np.max(np.abs(poly_vals))

print("\nMax |64λ^3 + 64λ^2 + 7λ - 9| over adjacency eigenvalues:")
print(f"{max_resid:.12f}")

real_root = 0.290442704136390
closest = eig[np.argmin(np.abs(eig - real_root))]
print("\nClosest adjacency eigenvalue to cubic real root:")
print(f"root    = {real_root:.12f}")
print(f"closest = {closest:.12f}")
print(f"delta   = {abs(closest - real_root):.12f}")
