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
    """
    We don't know the local flag generators here, so we use vertex paths as proxy words.
    Each geodesic word is represented by the vertex sequence root->...->v.
    """
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
            # geodesic extension only
            queue.append((u, path + (u,)))

    return dist, parents, children, words_to_vertex


def first_collision_layer(dist, words_to_vertex, root):
    by_layer = defaultdict(list)
    for v, words in words_to_vertex.items():
        d = dist[v]
        if d == 0:
            continue
        if len(words) > 1:
            by_layer[d].append((v, words))
    if not by_layer:
        return None, {}
    first = min(by_layer)
    return first, by_layer


def pretty_path(path):
    return " -> ".join(map(str, path))


def main():
    G = load_g60()

    roots = [0, 1, 4, 38]
    for root in roots:
        print("\n" + "=" * 80)
        print(f"ROOT {root}")
        print("=" * 80)

        dist, parents, children, words_to_vertex = enumerate_geodesic_words(G, root, max_depth=4)
        first, by_layer = first_collision_layer(dist, words_to_vertex, root)

        if first is None:
            print("No geodesic collisions found up to depth 4.")
            continue

        print(f"first collision layer = {first}")
        print(f"number of collided vertices in that layer = {len(by_layer[first])}")

        for v, words in sorted(by_layer[first], key=lambda x: x[0]):
            print(f"\nvertex {v} at layer {first}")
            print(f"  geodesic parents: {parents[v]}")
            print(f"  number of geodesic words: {len(words)}")
            for i, w in enumerate(words[:10], start=1):
                print(f"    word {i}: {pretty_path(w)}")

        # also summarize all collisions up to depth 4
        print("\ncollision summary by layer:")
        for d in sorted(by_layer):
            counts = [len(words) for _, words in by_layer[d]]
            print(f"  layer {d}: {len(by_layer[d])} collided vertices, multiplicities={counts}")

if __name__ == "__main__":
    main()
