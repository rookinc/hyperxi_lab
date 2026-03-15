from __future__ import annotations

from collections import Counter, defaultdict, deque
from pathlib import Path
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]

G60_CANDIDATES = [
    ROOT / "reports" / "true_quotients" / "true_chamber_graph.g6",
    ROOT / "artifacts" / "census" / "thalean_graph.g6",
]

def find_existing(paths):
    for p in paths:
        if p.exists():
            return p
    return None

def load_g60() -> nx.Graph:
    path = find_existing(G60_CANDIDATES)
    if path is None:
        raise FileNotFoundError("Could not find G60 .g6 file.")
    print(f"loading G60 from: {path}")
    G = nx.read_graph6(path)
    print(f"G60: |V|={G.number_of_nodes()} |E|={G.number_of_edges()}")
    return G

def shortest_path_dag(G: nx.Graph, root: int):
    dist = nx.single_source_shortest_path_length(G, root)
    parents = defaultdict(list)
    children = defaultdict(list)

    for v in G.nodes():
        for u in G.neighbors(v):
            if dist.get(u, 10**9) == dist[v] + 1:
                children[v].append(u)
            if dist.get(u, 10**9) == dist[v] - 1:
                parents[v].append(u)

    for v in G.nodes():
        parents[v] = sorted(parents[v])
        children[v] = sorted(children[v])

    return dist, parents, children

def count_geodesic_paths(G: nx.Graph, root: int):
    dist, parents, children = shortest_path_dag(G, root)
    by_layer = defaultdict(list)
    for v, d in dist.items():
        by_layer[d].append(v)

    num_paths = {root: 1}
    D = max(dist.values())
    for d in range(1, D + 1):
        for v in by_layer[d]:
            num_paths[v] = sum(num_paths[p] for p in parents[v])

    return dist, parents, children, num_paths

def radial_type(dist, G: nx.Graph, v: int):
    i = dist[v]
    c = a = b = 0
    for u in G.neighbors(v):
        du = dist[u]
        if du == i - 1:
            c += 1
        elif du == i:
            a += 1
        elif du == i + 1:
            b += 1
        else:
            raise RuntimeError(f"bad jump from layer {i} to {du}")
    return (c, a, b)

def pretty_path(path):
    return " -> ".join(map(str, path))

def enumerate_geodesic_words_to_depth(G: nx.Graph, root: int, max_depth: int = 5):
    dist, parents, children = shortest_path_dag(G, root)
    words_to_vertex = defaultdict(list)

    q = deque([(root, (root,))])
    while q:
        v, path = q.popleft()
        d = len(path) - 1
        words_to_vertex[v].append(path)
        if d >= max_depth:
            continue
        for u in children[v]:
            q.append((u, path + (u,)))
    return words_to_vertex

def inspect_root(G: nx.Graph, root: int):
    dist, parents, children, num_paths = count_geodesic_paths(G, root)
    words_to_vertex = enumerate_geodesic_words_to_depth(G, root, max_depth=5)

    layer5 = [v for v in G.nodes() if dist[v] == 5]
    rows = []
    for v in sorted(layer5):
        typ = radial_type(dist, G, v)
        rows.append({
            "vertex": v,
            "type": typ,
            "paths": num_paths[v],
            "parents": parents[v],
            "same_neighbors": sorted(u for u in G.neighbors(v) if dist[u] == 5),
            "children": children[v],
        })

    print("\n" + "=" * 80)
    print(f"ROOT {root}")
    print("=" * 80)

    print("layer-5 counts by radial type:")
    print(Counter(r["type"] for r in rows))

    print("\nlayer-5 counts by geodesic multiplicity:")
    print(Counter(r["paths"] for r in rows))

    print("\n(type, geodesic multiplicity) table:")
    combo = Counter((r["type"], r["paths"]) for r in rows)
    for k, v in sorted(combo.items(), key=lambda x: (x[0][0], x[0][1])):
        print(f"  {k}  x{v}")

    print("\ndetailed layer-5 rows:")
    for r in rows:
        print(
            f"v={r['vertex']:2d} "
            f"type={r['type']} "
            f"paths={r['paths']} "
            f"parents={r['parents']} "
            f"same={r['same_neighbors']} "
            f"children={r['children']}"
        )

    # show actual words for multiplicity > 1
    print("\nlayer-5 vertices with multiple geodesic words:")
    for r in rows:
        if r["paths"] > 1:
            print(f"\nvertex {r['vertex']} type={r['type']} paths={r['paths']}")
            for i, w in enumerate(words_to_vertex[r["vertex"]][:12], start=1):
                print(f"  word {i}: {pretty_path(w)}")

def main():
    G = load_g60()
    for root in [0, 1, 4, 38]:
        inspect_root(G, root)

if __name__ == "__main__":
    main()
