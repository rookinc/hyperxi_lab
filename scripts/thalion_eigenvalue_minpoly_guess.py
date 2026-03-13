#!/usr/bin/env python3

import networkx as nx
import numpy as np
import sympy as sp
import mpmath as mp

from hyperxi.combinatorics.chamber_graph import build_chamber_graph

mp.mp.dps = 120

def load_graph():
    raw = build_chamber_graph()
    G = nx.Graph()
    G.add_nodes_from(raw.vertices)
    G.add_edges_from(raw.edges)
    return G

def adjacency_spectrum(G):
    nodes = sorted(G.nodes())
    A = nx.to_numpy_array(G, nodelist=nodes, dtype=float)
    eigvals, _ = np.linalg.eigh(A)
    order = np.argsort(eigvals)[::-1]
    return eigvals[order]

G = load_graph()
eigvals = adjacency_spectrum(G)
lam = mp.mpf(str(eigvals[1]))

print("Searching minimal polynomial for:")
print(lam)
print()

x = sp.symbols("x")
found = False

for deg in range(2, 21):
    vec = [lam**k for k in range(deg + 1)]
    relation = mp.pslq(vec, maxcoeff=10_000_000)

    if relation is not None:
        found = True
        coeffs = list(relation)
        poly = sum(coeffs[i] * x**i for i in range(len(coeffs)))
        poly = sp.expand(poly)

        print("Candidate degree:", deg)
        print("Polynomial:")
        print(poly)
        print()

        residual = sp.N(poly.subs(x, sp.Float(str(lam), 80)), 50)
        print("Residual:")
        print(residual)
        print()

if not found:
    print("No relation found up to degree 20 with maxcoeff=10_000_000.")
