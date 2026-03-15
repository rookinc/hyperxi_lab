import networkx as nx
from collections import defaultdict

G = nx.read_graph6("reports/true_quotients/true_chamber_graph.g6")

dist = dict(nx.all_pairs_shortest_path_length(G))

v0 = list(G.nodes())[0]

D = max(dist[v0].values())

b = []
c = []

for i in range(D):
    bi = None
    ci = None

    for v in G.nodes():
        if dist[v0][v] != i:
            continue

        for u in G.neighbors(v):

            if dist[v0][u] == i+1:
                bi = bi + 1 if bi is not None else 1

            if dist[v0][u] == i-1:
                ci = ci + 1 if ci is not None else 1

    b.append(bi)
    c.append(ci)

print("b:", b)
print("c:", c)
