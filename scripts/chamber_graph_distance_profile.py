from __future__ import annotations

from pathlib import Path
import ast
from collections import Counter
import networkx as nx

DECAGON_FILE = Path("artifacts/cycles/ordered_decagon_pair_cycles.txt")


def load_decagons(path: Path):
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line.startswith("decagon") or ":" not in line:
            continue
        payload = line.split(":", 1)[1].strip()
        try:
            obj = ast.literal_eval(payload)
            if isinstance(obj, list) and len(obj) == 10:
                out.append(tuple(int(x) for x in obj))
        except Exception:
            pass
    return out


def build_graph(decagons):
    G = nx.Graph()
    for cyc in decagons:
        n = len(cyc)
        for i in range(n):
            G.add_edge(cyc[i], cyc[(i + 1) % n])
    return G


def shell_counts(G: nx.Graph, root: int):
    d = nx.single_source_shortest_path_length(G, root)
    c = Counter(d.values())
    return tuple(c[i] for i in range(max(c) + 1))


def common_neighbor_profiles(G: nx.Graph):
    verts = sorted(G.nodes())
    adj = Counter()
    nonadj = Counter()
    for i, u in enumerate(verts):
        Nu = set(G.neighbors(u))
        for v in verts[i + 1:]:
            k = len(Nu & set(G.neighbors(v)))
            if G.has_edge(u, v):
                adj[k] += 1
            else:
                nonadj[k] += 1
    return adj, nonadj


def girth(G: nx.Graph):
    best = None
    for s in G.nodes():
        dist = {s: 0}
        parent = {s: None}
        q = [s]
        for u in q:
            for v in G.neighbors(u):
                if v not in dist:
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    q.append(v)
                elif parent[u] != v:
                    cyc = dist[u] + dist[v] + 1
                    if best is None or cyc < best:
                        best = cyc
    return best


def intersection_profile_by_distance(G: nx.Graph, root: int):
    d = nx.single_source_shortest_path_length(G, root)
    maxd = max(d.values())
    rows = []
    for i in range(1, maxd + 1):
        triples = Counter()
        layer = [v for v, dv in d.items() if dv == i]
        for v in layer:
            c_i = sum(1 for w in G.neighbors(v) if d[w] == i - 1)
            a_i = sum(1 for w in G.neighbors(v) if d[w] == i)
            b_i = sum(1 for w in G.neighbors(v) if d[w] == i + 1)
            triples[(c_i, a_i, b_i)] += 1
        rows.append((i, triples))
    return rows


def main():
    decagons = load_decagons(DECAGON_FILE)
    print("=" * 80)
    print("CHAMBER GRAPH DISTANCE PROFILE")
    print("=" * 80)
    print("decagons loaded:", len(decagons))

    if not decagons:
        print("No decagons loaded.")
        return

    G = build_graph(decagons)
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted(set(dict(G.degree()).values())))
    print("connected:", nx.is_connected(G))
    print("diameter:", nx.diameter(G))
    print("girth:", girth(G))

    root = min(G.nodes())
    shells = shell_counts(G, root)
    print("shell counts from root", root, ":", shells)

    same_shells = True
    for v in G.nodes():
        if shell_counts(G, v) != shells:
            same_shells = False
            break
    print("same shell counts for all vertices:", same_shells)

    print()
    print("INTERSECTION PROFILES BY DISTANCE FROM ROOT")
    print("-" * 80)
    for i, triples in intersection_profile_by_distance(G, root):
        print(f"distance {i}:")
        for triple, count in sorted(triples.items()):
            print(f"  {triple}: count={count}")

    adj_prof, nonadj_prof = common_neighbor_profiles(G)
    print()
    print("ADJACENT COMMON-NEIGHBOR PROFILE")
    print("-" * 80)
    for k in sorted(adj_prof):
        print(f"  {k}: {adj_prof[k]}")

    print()
    print("NONADJACENT COMMON-NEIGHBOR PROFILE")
    print("-" * 80)
    for k in sorted(nonadj_prof):
        print(f"  {k}: {nonadj_prof[k]}")


if __name__ == "__main__":
    main()
