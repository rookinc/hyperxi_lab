import networkx as nx
from collections import defaultdict

G = nx.read_graph6("reports/true_quotients/true_chamber_graph.g6")

print("checking distance regularity")

dist = dict(nx.all_pairs_shortest_path_length(G))

shell_profiles = set()

for v in G.nodes():
    counts = defaultdict(int)

    for u in G.nodes():
        counts[dist[v][u]] += 1

    profile = tuple(counts[i] for i in sorted(counts))
    shell_profiles.add(profile)

print("distinct shell profiles:", len(shell_profiles))

for p in shell_profiles:
    print(p)
