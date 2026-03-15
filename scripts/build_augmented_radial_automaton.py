from __future__ import annotations

from collections import Counter, defaultdict
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

def augmented_state(G: nx.Graph, dist: dict[int, int], num_paths: dict[int, int], v: int):
    return (radial_type(G, dist, v), num_paths[v])

def summarize_root(G: nx.Graph, root: int):
    dist, parents, children, layers, num_paths = count_geodesic_paths(G, root)
    D = max(dist.values())

    print("\n" + "=" * 80)
    print(f"ROOT {root}")
    print("=" * 80)

    layer_counts = {}
    transitions = defaultdict(Counter)

    for d in range(D + 1):
        verts = layers[d]
        states = [augmented_state(G, dist, num_paths, v) for v in verts]
        counts = Counter(states)
        layer_counts[d] = counts

        print(f"\nlayer {d}:")
        for st, c in sorted(counts.items(), key=lambda x: (x[0][0], x[0][1])):
            print(f"  {st}  x{c}")

        for v in verts:
            src = augmented_state(G, dist, num_paths, v)
            dv = dist[v]
            for u in G.neighbors(v):
                du = dist[u]
                step = du - dv
                dst = augmented_state(G, dist, num_paths, u)
                transitions[(d, src)][(step, du, dst)] += 1

    print("\naugmented transition rules:")
    report = {
        "root": root,
        "layer_counts": {},
        "transitions": {},
    }

    for d in sorted(layer_counts):
        report["layer_counts"][str(d)] = {str(k): int(v) for k, v in sorted(layer_counts[d].items())}

    for (d, src), counter in sorted(transitions.items(), key=lambda x: (x[0][0], x[0][1][0], x[0][1][1])):
        total_vertices = layer_counts[d][src]
        print(f"\nsource layer {d}, source state {src}:")
        print(f"  source vertices of this state: {total_vertices}")
        for (step, du, dst), count in sorted(counter.items(), key=lambda x: (x[0][0], x[0][1], x[0][2][0], x[0][2][1])):
            label = {-1: "in", 0: "same", 1: "out"}[step]
            print(
                f"  --{label}--> layer {du}, state {dst}: "
                f"total {count}, per-vertex {count / total_vertices:.3f}"
            )
        report["transitions"][f"layer{d}_state{src}"] = {
            f"{step}:{du}:{dst}": {
                "total": int(count),
                "per_vertex": float(count / total_vertices),
            }
            for (step, du, dst), count in sorted(counter.items(), key=lambda x: (x[0][0], x[0][1], x[0][2][0], x[0][2][1]))
        }

    return report

def main():
    G = load_g60()
    roots = [0, 1, 4, 38]
    full = {"roots": []}

    for r in roots:
        full["roots"].append(summarize_root(G, r))

    out_path = ROOT / "reports" / "build_augmented_radial_automaton.json"
    out_path.write_text(json.dumps(full, indent=2), encoding="utf-8")
    print(f"\nsaved {out_path}")

if __name__ == "__main__":
    main()
