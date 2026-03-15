#!/usr/bin/env python3

"""
Probe the Thalean graph for Desargues subgraphs.

Goal
----
Check whether the 60-vertex cubic Thalean graph contains
20-vertex subgraphs isomorphic to the Desargues graph.

If such subgraphs exist, that strongly supports the hypothesis
that the Thalean graph is a lift or extension of Desargues.

WARNING
-------
A naive 60 choose 20 search is enormous.

Instead we prune using:
- degree constraints
- BFS neighborhoods
- induced subgraph filtering
"""

import networkx as nx
from itertools import combinations

print("============================================================")
print("PROBE DESARGUES SUBSTRUCTURES")
print("============================================================")

PATH = "reports/true_quotients/true_chamber_graph.g6"

print("loading:", PATH)
G = nx.read_graph6(PATH)

print("|V| =", G.number_of_nodes())
print("|E| =", G.number_of_edges())

print("\nloading Desargues reference graph")
D = nx.desargues_graph()

print("Desargues:")
print("vertices =", D.number_of_nodes())
print("edges    =", D.number_of_edges())

print("\nsearching neighborhoods for candidate sets...")

found = 0

# heuristic: start from each vertex and take radius-3 neighborhoods
for v in G.nodes():

    nodes = nx.single_source_shortest_path_length(G, v, cutoff=3).keys()
    nodes = list(nodes)

    if len(nodes) < 20:
        continue

    # examine combinations within neighborhood
    for subset in combinations(nodes, 20):

        H = G.subgraph(subset)

        if H.number_of_edges() != 30:
            continue

        if nx.is_isomorphic(H, D):
            print("\nFOUND DESARGUES COPY")
            print("subset:", subset)
            found += 1

            if found >= 10:
                break

    if found >= 10:
        break

print("\n============================================================")
print("TOTAL DESARGUES COPIES FOUND:", found)
print("============================================================")

