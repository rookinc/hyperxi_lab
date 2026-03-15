from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
import json
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
            elif du == dv:
                pass
            else:
                raise RuntimeError(f"bad jump {v}->{u}: {dv}->{du}")

    for v in G.nodes():
        parents[v] = sorted(parents[v])
        children[v] = sorted(children[v])

    return dist, parents, children

def count_geodesic_paths(G: nx.Graph, root: int):
    dist, parents, children = shortest_path_dag(G, root)
    layers = defaultdict(list)
    for v, d in dist.items():
        layers[d].append(v)

    num_paths = {root: 1}
    D = max(dist.values())
    for d in range(1, D + 1):
        for v in layers[d]:
            num_paths[v] = sum(num_paths[p] for p in parents[v])

    return dist, parents, children, layers, num_paths

def radial_type(G: nx.Graph, dist: dict[int, int], v: int):
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

def state_of(G: nx.Graph, dist: dict[int, int], num_paths: dict[int, int], v: int):
    return (radial_type(G, dist, v), num_paths[v])

def enumerate_geodesic_histories(G: nx.Graph, root: int, max_depth: int = 3):
    dist, parents, children, layers, num_paths = count_geodesic_paths(G, root)

    histories = defaultdict(list)
    q = deque([(root, (root,))])

    while q:
        v, path = q.popleft()
        d = len(path) - 1
        histories[v].append(path)

        if d >= max_depth:
            continue

        for u in children[v]:
            q.append((u, path + (u,)))

    return dist, parents, children, num_paths, histories

def canonical_step_labels(G: nx.Graph, dist, num_paths, path):
    """
    Replace arbitrary child order by intrinsic state-sequence labels.
    Each step is labeled by the destination augmented state.
    """
    labels = []
    for i in range(1, len(path)):
        v = path[i]
        labels.append(state_of(G, dist, num_paths, v))
    return tuple(labels)

def pretty_state(st):
    return f"{st}"

def pretty_state_path(state_path):
    return " -> ".join(pretty_state(s) for s in state_path)

def pretty_vertex_path(path):
    return " -> ".join(map(str, path))

def inspect_root(G: nx.Graph, root: int):
    dist, parents, children, num_paths, histories = enumerate_geodesic_histories(G, root, max_depth=3)

    collisions = []
    for v, paths in histories.items():
        if dist[v] == 3 and len(paths) > 1:
            collisions.append((v, paths))

    print("\n" + "=" * 80)
    print(f"ROOT {root}")
    print("=" * 80)

    if not collisions:
        print("No depth-3 collisions found.")
        return {"root": root, "collisions": []}

    out = {"root": root, "collisions": []}

    for v, paths in sorted(collisions, key=lambda x: x[0]):
        print(f"\nvertex {v} at depth 3")
        print(f"parents = {parents[v]}")
        print(f"collision multiplicity = {len(paths)}")

        state_paths = []
        for p in paths:
            sp = canonical_step_labels(G, dist, num_paths, p)
            state_paths.append((p, sp))

        print("canonical state-sequence relation candidates:")
        for _, sp in state_paths:
            print(f"  {pretty_state_path(sp)}")

        if len(state_paths) == 2:
            print("relation schema:")
            print(f"  {pretty_state_path(state_paths[0][1])}")
            print("  ==")
            print(f"  {pretty_state_path(state_paths[1][1])}")

        print("full vertex paths:")
        for p, sp in state_paths:
            print(f"  {pretty_vertex_path(p)}")
            print(f"    states: {pretty_state_path(sp)}")

        out["collisions"].append({
            "vertex": v,
            "parents": parents[v],
            "paths": [list(p) for p, _ in state_paths],
            "state_paths": [[str(s) for s in sp] for _, sp in state_paths],
        })

    return out

def main():
    G = load_g60()
    full = {"roots": []}

    for root in [0, 1, 4, 38]:
        full["roots"].append(inspect_root(G, root))

    out_path = ROOT / "reports" / "extract_canonical_relation_schema.json"
    out_path.write_text(json.dumps(full, indent=2), encoding="utf-8")
    print(f"\nsaved {out_path}")

if __name__ == "__main__":
    main()
