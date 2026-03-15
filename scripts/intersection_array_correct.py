import networkx as nx
from collections import defaultdict, Counter

G = nx.read_graph6("reports/true_quotients/true_chamber_graph.g6")

root = list(G.nodes())[0]
dist = nx.single_source_shortest_path_length(G, root)
D = max(dist.values())

layers = defaultdict(list)
for v, d in dist.items():
    layers[d].append(v)

print("root =", root)
print("diameter =", D)
print("shells =", [len(layers[i]) for i in range(D + 1)])

b = []
c = []
a = []

print("\nlayer-wise neighbor counts:")
for i in range(D + 1):
    a_vals = []
    b_vals = []
    c_vals = []

    for v in layers[i]:
        ai = bi = ci = 0
        for u in G.neighbors(v):
            du = dist[u]
            if du == i - 1:
                ci += 1
            elif du == i:
                ai += 1
            elif du == i + 1:
                bi += 1
            else:
                raise RuntimeError(f"bad jump from layer {i} to {du}")

        a_vals.append(ai)
        b_vals.append(bi)
        c_vals.append(ci)

    print(f"layer {i}:")
    print("  a counts:", Counter(a_vals))
    print("  b counts:", Counter(b_vals))
    print("  c counts:", Counter(c_vals))

    a.append(a_vals[0])
    if i < D:
        b.append(b_vals[0])
    if i > 0:
        c.append(c_vals[0])

print("\nintersection array candidate:")
print("b =", b)
print("c =", c)
print("a =", a)
