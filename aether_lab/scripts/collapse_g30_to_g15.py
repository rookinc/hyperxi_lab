import networkx as nx
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

G30_FILE = ROOT / "data/reports/quotients/g30_from_involution_simple.g6"

# the involution you found
pairs = [
(0,29),(1,25),(2,26),(3,27),(4,28),
(5,20),(6,21),(7,22),(8,23),(9,24),
(10,17),(11,18),(12,19),(13,15),(14,16)
]

G = nx.read_graph6(G30_FILE)

print("G30:",G.number_of_nodes(),"vertices")

# build mapping
mapping = {}
for i,(a,b) in enumerate(pairs):
    mapping[a] = i
    mapping[b] = i

G15 = nx.Graph()

for i in range(15):
    G15.add_node(i)

for u,v in G.edges():

    a = mapping[u]
    b = mapping[v]

    if a != b:
        G15.add_edge(a,b)

print()
print("G15 SUMMARY")
print("-----------")
print("vertices:",G15.number_of_nodes())
print("edges:",G15.number_of_edges())
print("degree set:",sorted(set(dict(G15.degree()).values())))

# test Petersen line graph
P = nx.petersen_graph()
Lp = nx.line_graph(P)

iso = nx.is_isomorphic(G15,Lp)

print()
print("ISOMORPHISM TEST")
print("----------------")
print("G15 ≅ L(Petersen):",iso)

out = ROOT / "data/reports/quotients/g15_verified.g6"
nx.write_graph6(G15,out,header=False)

print()
print("saved:",out)

