#!/usr/bin/env python3

import networkx as nx
import numpy as np


# ------------------------------------------------------------
# Graph loader
# ------------------------------------------------------------

def load_graph():

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

    raise RuntimeError("Could not extract graph")


# ------------------------------------------------------------
# Laplacian without SciPy
# ------------------------------------------------------------

def compute_modes(G):

    A = nx.to_numpy_array(G)
    deg = np.sum(A, axis=1)

    L = np.diag(deg) - A

    vals, vecs = np.linalg.eigh(L)

    return vals, vecs


# ------------------------------------------------------------

def pick_first_excited(vals, vecs, tol=1e-6):

    base = vals[0]

    target = None
    for v in vals:
        if v > base + tol:
            target = v
            break

    idx = [i for i,v in enumerate(vals) if abs(v-target) < tol]

    return target, vecs[:,idx]


# ------------------------------------------------------------

def transport_vector(vec, path):

    v = vec.copy()

    for i in range(len(path)-1):
        a = path[i]
        b = path[i+1]

        v[a], v[b] = v[b], v[a]

    return v


# ------------------------------------------------------------

def compare_states(v0, v1):

    dot = float(np.dot(v0, v1))
    n0 = float(np.dot(v0, v0))
    n1 = float(np.dot(v1, v1))

    return dot / np.sqrt(n0*n1)


# ------------------------------------------------------------

def main():

    print("="*80)
    print("SPINORIAL MONODROMY TEST")
    print("="*80)

    G = load_graph()

    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())

    vals, vecs = compute_modes(G)

    val, space = pick_first_excited(vals, vecs)

    print()
    print("first excited eigenvalue:", val)
    print("multiplicity:", space.shape[1])

    vec = np.array(space[:,0]).flatten()

    nodes = list(G.nodes())
    loop = nodes[:6] + [nodes[0]]

    print()
    print("test loop:", loop)

    transported = transport_vector(vec, loop)

    cos = compare_states(vec, transported)

    print()
    print("cos(angle) between states:", cos)

    if abs(cos - 1) < 1e-3:
        print("Result: trivial monodromy (psi -> psi)")
    elif abs(cos + 1) < 1e-3:
        print("Result: spinorial flip (psi -> -psi)")
    else:
        print("Result: rotated state in eigenspace")

    print("="*80)


if __name__ == "__main__":
    main()

