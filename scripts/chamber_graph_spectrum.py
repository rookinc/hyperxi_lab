from __future__ import annotations

from pathlib import Path
import ast
from collections import Counter
import numpy as np
import networkx as nx

DECAGON_FILE = Path("artifacts/cycles/ordered_decagon_pair_cycles.txt")


def load_decagons(path: Path):
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line.startswith("decagon") or ":" not in line:
            continue
        payload = line.split(":", 1)[1].strip()
        obj = ast.literal_eval(payload)
        if isinstance(obj, list) and len(obj) == 10:
            out.append(tuple(int(x) for x in obj))
    return out


def build_graph(decagons):
    G = nx.Graph()
    for cyc in decagons:
        n = len(cyc)
        for i in range(n):
            G.add_edge(cyc[i], cyc[(i + 1) % n])
    return G


def main():
    decagons = load_decagons(DECAGON_FILE)
    print("=" * 80)
    print("CHAMBER GRAPH SPECTRUM")
    print("=" * 80)
    print("decagons loaded:", len(decagons))

    if not decagons:
        print("No decagons loaded.")
        return

    G = build_graph(decagons)
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted(set(dict(G.degree()).values())))

    A = nx.to_numpy_array(G, nodelist=sorted(G.nodes()), dtype=float)
    eigvals = np.linalg.eigvalsh(A)
    eigvals = np.round(eigvals, 6)

    counts = Counter(float(x) for x in eigvals)

    print()
    print("EIGENVALUE MULTIPLICITIES")
    print("-" * 80)
    for val in sorted(counts):
        print(f"{val:10.6f}: {counts[val]}")

    print()
    print("FIRST 10 EIGENVALUES")
    print("-" * 80)
    for x in eigvals[:10]:
        print(f"{x:10.6f}")

    print()
    print("LAST 10 EIGENVALUES")
    print("-" * 80)
    for x in eigvals[-10:]:
        print(f"{x:10.6f}")

    print()
    print("SANITY CHECKS")
    print("-" * 80)
    print("sum eigenvalues:", float(np.sum(eigvals)))
    print("max eigenvalue:", float(np.max(eigvals)))
    print("min eigenvalue:", float(np.min(eigvals)))


if __name__ == "__main__":
    main()
