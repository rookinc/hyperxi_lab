from pathlib import Path
import networkx as nx
import json

ROOT = Path(__file__).resolve().parents[1]

G30_MULTI = ROOT / "data/reports/quotients/g30_from_involution_multigraph.gexf"

print("loading G30 multigraph:", G30_MULTI)

G30 = nx.read_gexf(G30_MULTI)
G30 = nx.MultiGraph(G30)

print("G30 vertices:", G30.number_of_nodes())
print("G30 edges:", G30.number_of_edges())

# ---------------------------------------------------
# build simple projection
# ---------------------------------------------------

G30_simple = nx.Graph()
G30_simple.add_nodes_from(G30.nodes())

for u,v in G30.edges():
    G30_simple.add_edge(u,v)

print("simple edges:", G30_simple.number_of_edges())

# ---------------------------------------------------
# detect parallel edges
# ---------------------------------------------------

parallel_pairs = []

for u,v in G30_simple.edges():
    if G30.number_of_edges(u,v) == 2:
        parallel_pairs.append((u,v))

print("parallel edge pairs:", len(parallel_pairs))

# ---------------------------------------------------
# collapse parallel pairs
# ---------------------------------------------------

mapping = {}
fiber = {}

i = 0
for u,v in parallel_pairs:
    if u not in mapping and v not in mapping:
        mapping[u] = i
        mapping[v] = i
        fiber[i] = [u,v]
        i += 1

# remaining vertices
for v in G30.nodes():
    if v not in mapping:
        mapping[v] = i
        fiber[i] = [v]
        i += 1

# build quotient
G15 = nx.Graph()

for i in set(mapping.values()):
    G15.add_node(i)

for u,v in G30_simple.edges():
    a = mapping[u]
    b = mapping[v]
    if a != b:
        G15.add_edge(a,b)

print()
print("G15 SUMMARY")
print("-----------")
print("vertices:", G15.number_of_nodes())
print("edges:", G15.number_of_edges())
print("degree set:", sorted(set(dict(G15.degree()).values())))

# ---------------------------------------------------
# compare with L(Petersen)
# ---------------------------------------------------

P = nx.petersen_graph()
Lp = nx.line_graph(P)

iso = nx.is_isomorphic(G15, Lp)

print()
print("ISOMORPHISM TEST")
print("----------------")
print("G15 ≅ L(Petersen):", iso)

# ---------------------------------------------------
# save
# ---------------------------------------------------

out = ROOT / "data/reports/quotients/g15_from_g30.g6"
nx.write_graph6(G15, out, header=False)

print()
print("saved:", out)

