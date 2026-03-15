from __future__ import annotations

from collections import defaultdict, deque
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
            du = dist.get(u, 10**9)
            dv = dist[v]
            if du == dv + 1:
                children[v].append(u)
            elif du == dv - 1:
                parents[v].append(u)

    for v in G.nodes():
        parents[v] = sorted(children for children in parents[v])
        children[v] = sorted(children[v])

    return dist, parents, children

def build_local_codes(G: nx.Graph, root: int, max_depth: int = 3):
    """
    Assign abstract rooted word codes by local branching order.

    depth 1: A,B,C
    deeper: append 0/1 according to sorted outward neighbors
    """
    dist, parents, children = shortest_path_dag(G, root)

    root_children = sorted(children[root])
    first_labels = {v: chr(ord('A') + i) for i, v in enumerate(root_children)}

    coded_paths_to_vertex = defaultdict(list)

    q = deque()
    for v in root_children:
        q.append((v, (root, v), first_labels[v]))

    while q:
        v, path, code = q.popleft()
        coded_paths_to_vertex[v].append((path, code))

        d = len(path) - 1
        if d >= max_depth:
            continue

        outs = sorted(children[v])
        index_map = {u: str(i) for i, u in enumerate(outs)}

        for u in outs:
            q.append((u, path + (u,), code + index_map[u]))

    return dist, parents, children, coded_paths_to_vertex

def pretty_path(path):
    return " -> ".join(map(str, path))

def inspect_root(G: nx.Graph, root: int):
    dist, parents, children, coded = build_local_codes(G, root, max_depth=3)

    collisions = []
    for v, items in coded.items():
        if dist[v] == 3 and len(items) > 1:
            collisions.append((v, items))

    print("\n" + "=" * 80)
    print(f"ROOT {root}")
    print("=" * 80)

    if not collisions:
        print("No depth-3 collisions found.")
        return

    print(f"depth-3 collided vertices: {len(collisions)}")
    for v, items in sorted(collisions, key=lambda x: x[0]):
        print(f"\nvertex {v} at depth 3")
        print(f"parents = {parents[v]}")
        print(f"collision multiplicity = {len(items)}")

        codes = sorted(code for _, code in items)
        print("abstract relation candidates:")
        for c in codes:
            print(f"  {c}")
        if len(codes) == 2:
            print(f"relation: {codes[0]} == {codes[1]}")

        print("full paths:")
        for path, code in sorted(items, key=lambda x: x[1]):
            print(f"  {code:>4} : {pretty_path(path)}")

def main():
    G = load_g60()
    for root in [0, 1, 4, 38]:
        inspect_root(G, root)

if __name__ == "__main__":
    main()
