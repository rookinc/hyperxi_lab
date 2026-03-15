import networkx as nx
from collections import Counter
from itertools import combinations

from load_thalean_graph import load_spec, build_graph

G = build_graph(load_spec())
dist = dict(nx.all_pairs_shortest_path_length(G))
diam = nx.diameter(G)

print("=" * 80)
print("CANONICAL THALEAN GRAPH ANTIPODE CHECK")
print("=" * 80)
print("vertices:", G.number_of_nodes())
print("edges:", G.number_of_edges())
print("diameter:", diam)

antipodes = {}
bad = []

for v in G.nodes():
    far = [u for u, d in dist[v].items() if d == diam]
    if len(far) != 1:
        bad.append((v, far))
    else:
        antipodes[v] = far[0]

print()
print("distance-diameter partner counts:")
print(Counter(len([u for u, d in dist[v].items() if d == diam]) for v in G.nodes()))

if bad:
    print()
    print("BAD VERTICES")
    for v, far in bad[:10]:
        print(v, far)
else:
    print()
    print("All vertices have a unique distance-%d partner." % diam)

    ok_involution = all(antipodes[antipodes[v]] == v for v in G.nodes())
    fixed_free = all(antipodes[v] != v for v in G.nodes())

    print("involution:", ok_involution)
    print("fixed-point-free:", fixed_free)

    pairs = sorted({tuple(sorted((v, antipodes[v]))) for v in G.nodes()})
    print("pair count:", len(pairs))
    print("first 20 pairs:", pairs[:20])
