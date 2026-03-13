#!/usr/bin/env python3

from pathlib import Path
from collections import Counter, defaultdict
import networkx as nx
import numpy as np

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


def local_signature(G, dist, v):
    i = dist[v]
    c = a = b = 0
    for u in G.neighbors(v):
        j = dist[u]
        if j == i - 1:
            c += 1
        elif j == i:
            a += 1
        elif j == i + 1:
            b += 1
    return (c, a, b)


def adjacency_spectrum(G):
    A = nx.to_numpy_array(G, dtype=float)
    vals, vecs = np.linalg.eigh(A)
    vals = np.round(vals, 6)
    return vals, vecs


def main():
    G = load_graph()
    vals, vecs = adjacency_spectrum(G)

    print("=" * 80)
    print("THALEAN CHECK SEVEN")
    print("=" * 80)
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print()

    root = 0
    shells, dist = shell_counts(G, root)

    print("shells from root 0:", shells)
    print()

    # cumulative counts
    cum2 = sum(shells[:3])   # radius 0,1,2
    cum3 = sum(shells[:4])   # radius 0,1,2,3
    print("cumulative vertices within radius 2:", cum2)
    print("cumulative vertices within radius 3:", cum3)
    print()

    # local signatures in ball radius 3
    ball3 = [v for v, d in dist.items() if d <= 3]
    sigs = Counter(local_signature(G, dist, v) for v in ball3)
    print("signature counts inside radius-3 ball:")
    for sig, mult in sorted(sigs.items()):
        print(" ", sig, "count=", mult)
    print("number of distinct signatures in radius-3 ball:", len(sigs))
    print()

    # neighbor-shell union sizes
    for r in range(1, 5):
        layer = [v for v, d in dist.items() if d == r]
        union_prev = set()
        for v in layer:
            union_prev.update(u for u in G.neighbors(v) if dist[u] == r - 1)
        print(f"distance {r}: distinct inward neighbors =", len(union_prev))
    print()

    # unique nonzero spectral families seen by root projection
    psi = np.zeros(G.number_of_nodes())
    psi[root] = 1.0
    coeffs = vecs.T @ psi

    nonzero_families = Counter()
    for lam, c in zip(vals, coeffs):
        if abs(c) > 1e-9:
            nonzero_families[float(lam)] += 1

    print("nonzero eigenvalue families touched by delta at root:")
    for lam, mult in sorted(nonzero_families.items()):
        print(" ", lam, "basis vectors touched =", mult)
    print("number of distinct eigenvalue families touched:", len(nonzero_families))
    print()

    # raw candidate seven-related quantities
    candidates = {
        "3_plus_4": 3 + 4,
        "8_minus_1": 8 - 1,
        "radius3_minus_root_layer": cum3 - shells[0] - shells[1] - shells[2],  # = shell 3
        "distinct_eigenvalue_families_touched": len(nonzero_families),
        "distinct_radius3_signatures": len(sigs),
    }

    print("candidate seven-like quantities:")
    for k, v in candidates.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
