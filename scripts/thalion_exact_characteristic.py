#!/usr/bin/env python3

import sympy as sp
import networkx as nx
from hyperxi.combinatorics.chamber_graph import build_chamber_graph

print("="*80)
print("THALION EXACT CHARACTERISTIC POLYNOMIAL")
print("="*80)

# build graph
raw = build_chamber_graph()

G = nx.Graph()
G.add_nodes_from(raw.vertices)
G.add_edges_from(raw.edges)

nodes = sorted(G.nodes())

A = nx.to_numpy_array(G, nodelist=nodes, dtype=int)

# convert to sympy matrix
M = sp.Matrix(A)

x = sp.symbols('x')

print("computing characteristic polynomial...")
poly = M.charpoly(x)

print()
print("degree:", poly.degree())
print()

print("factoring polynomial...")
factors = sp.factor(poly.as_expr())

print()
print("FACTORIZATION:")
print(factors)

print()
print("="*80)
