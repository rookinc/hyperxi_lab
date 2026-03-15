import networkx as nx

from load_thalean_graph import load_spec, build_graph

G = build_graph(load_spec())
dist = dict(nx.all_pairs_shortest_path_length(G))
diam = nx.diameter(G)

a = {}
for v in G.nodes():
    far = [u for u, d in dist[v].items() if d == diam]
    if len(far) != 1:
        raise RuntimeError(f"vertex {v} has {len(far)} distance-{diam} partners")
    a[v] = far[0]

is_involution = all(a[a[v]] == v for v in G.nodes())
fixed_free = all(a[v] != v for v in G.nodes())

edge_ok = True
bad_edges = []
for u, v in G.edges():
    au, av = a[u], a[v]
    if not G.has_edge(au, av):
        edge_ok = False
        bad_edges.append(((u, v), (au, av)))
        if len(bad_edges) >= 10:
            break

bijective = len(set(a.values())) == G.number_of_nodes()

print("=" * 80)
print("CHECK CANONICAL ANTIPODE AS AUTOMORPHISM")
print("=" * 80)
print("vertices:", G.number_of_nodes())
print("edges:", G.number_of_edges())
print("diameter:", diam)
print()
print("involution:", is_involution)
print("fixed-point-free:", fixed_free)
print("bijective:", bijective)
print("edge-preserving:", edge_ok)

if bad_edges:
    print()
    print("FIRST BAD EDGES")
    for src, img in bad_edges:
        print(src, "->", img)

if edge_ok and is_involution and fixed_free and bijective:
    pairs = sorted({tuple(sorted((v, a[v]))) for v in G.nodes()})
    print()
    print("pair count:", len(pairs))
    print("first 20 pairs:", pairs[:20])
