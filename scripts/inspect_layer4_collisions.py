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
            if dist.get(u, 10**9) == dist[v] + 1:
                children[v].append(u)
            if dist.get(u, 10**9) == dist[v] - 1:
                parents[v].append(u)

    for v in G.nodes():
        parents[v] = sorted(parents[v])
        children[v] = sorted(children[v])

    return dist, parents, children


def enumerate_geodesic_words(G: nx.Graph, root: int, max_depth: int = 4):
    dist, parents, children = shortest_path_dag(G, root)
    words_to_vertex = defaultdict(list)

    queue = deque()
    queue.append((root, (root,)))

    while queue:
        v, path = queue.popleft()
        d = len(path) - 1
        words_to_vertex[v].append(path)

        if d >= max_depth:
            continue

        for u in children[v]:
            queue.append((u, path + (u,)))

    return dist, parents, children, words_to_vertex


def pretty_path(path):
    return " -> ".join(map(str, path))


def inspect_root(G: nx.Graph, root: int):
    dist, parents, children, words_to_vertex = enumerate_geodesic_words(G, root, max_depth=4)

    print("\n" + "=" * 80)
    print(f"ROOT {root}")
    print("=" * 80)

    layer4 = []
    for v, words in words_to_vertex.items():
        if dist[v] == 4 and len(words) > 1:
            layer4.append((v, words))

    layer4.sort(key=lambda x: (-len(x[1]), x[0]))

    print(f"collided vertices at layer 4: {len(layer4)}")
    print("multiplicities:", [len(words) for _, words in layer4])

    for v, words in layer4:
        print("\n" + "-" * 80)
        print(f"vertex {v} at layer 4")
        print(f"geodesic parents: {parents[v]}")
        print(f"number of geodesic words: {len(words)}")

        by_parent = defaultdict(list)
        for w in words:
            if len(w) >= 2:
                by_parent[w[-2]].append(w)

        print("grouped by immediate parent:")
        for p in sorted(by_parent):
            print(f"  parent {p}: {len(by_parent[p])} words")
            for w in by_parent[p]:
                print(f"    {pretty_path(w)}")

        print("grouped by first step from root:")
        by_first = defaultdict(list)
        for w in words:
            if len(w) >= 2:
                by_first[w[1]].append(w)
        for a in sorted(by_first):
            print(f"  first-step {a}: {len(by_first[a])} words")
            for w in by_first[a]:
                print(f"    {pretty_path(w)}")


def main():
    G = load_g60()
    for root in [0, 1, 4, 38]:
        inspect_root(G, root)


if __name__ == "__main__":
    main()
