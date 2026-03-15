import networkx as nx

from load_thalean_graph import load_spec, build_graph

def quotient_by_pairs(G, pair_map):
    seen = set()
    classes = []
    owner = {}
    for v in sorted(G.nodes()):
        if v in seen:
            continue
        pair = tuple(sorted((v, pair_map[v])))
        seen.update(pair)
        idx = len(classes)
        classes.append(pair)
        for x in pair:
            owner[x] = idx
    Q = nx.Graph()
    Q.add_nodes_from(range(len(classes)))
    for u, v in G.edges():
        a, b = owner[u], owner[v]
        if a != b:
            Q.add_edge(a, b)
    return Q, classes, owner

G60 = build_graph(load_spec())
dist60 = dict(nx.all_pairs_shortest_path_length(G60))
diam60 = nx.diameter(G60)

a = {}
for v in G60.nodes():
    far = [u for u, d in dist60[v].items() if d == diam60]
    if len(far) != 1:
        raise RuntimeError(f"vertex {v} has {len(far)} distance-{diam60} partners")
    a[v] = far[0]

G30, classes30, owner30 = quotient_by_pairs(G60, a)

dist30 = dict(nx.all_pairs_shortest_path_length(G30))
diam30 = nx.diameter(G30)

b = {}
for v in G30.nodes():
    far = [u for u, d in dist30[v].items() if d == diam30]
    if len(far) != 1:
        raise RuntimeError(f"vertex {v} has {len(far)} distance-{diam30} partners")
    b[v] = far[0]

is_involution = all(b[b[v]] == v for v in G30.nodes())
fixed_free = all(b[v] != v for v in G30.nodes())
bijective = len(set(b.values())) == G30.number_of_nodes()

edge_ok = True
bad_edges = []
for u, v in G30.edges():
    bu, bv = b[u], b[v]
    if not G30.has_edge(bu, bv):
        edge_ok = False
        bad_edges.append(((u, v), (bu, bv)))
        if len(bad_edges) >= 10:
            break

print("=" * 80)
print("CHECK SECOND ANTIPODE AS AUTOMORPHISM")
print("=" * 80)
print("vertices:", G30.number_of_nodes())
print("edges:", G30.number_of_edges())
print("diameter:", diam30)
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
    pairs = sorted({tuple(sorted((v, b[v]))) for v in G30.nodes()})
    print()
    print("pair count:", len(pairs))
    print("first 20 pairs:", pairs[:20])
