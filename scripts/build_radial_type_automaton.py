from __future__ import annotations

import json
from collections import Counter, defaultdict
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


def root_layer_types(G: nx.Graph, root: int):
    dist = nx.single_source_shortest_path_length(G, root)
    D = max(dist.values())

    layers = defaultdict(list)
    for v, d in dist.items():
        layers[d].append(v)

    vertex_type = {}
    neighbor_profile = {}

    for i in range(D + 1):
        for v in layers[i]:
            ci = ai = bi = 0
            neigh_dists = []
            for u in G.neighbors(v):
                du = dist[u]
                neigh_dists.append(du)
                if du == i - 1:
                    ci += 1
                elif du == i:
                    ai += 1
                elif du == i + 1:
                    bi += 1
                else:
                    raise RuntimeError(f"bad jump from layer {i} to {du}")
            typ = (ci, ai, bi)
            vertex_type[v] = typ
            neighbor_profile[v] = tuple(sorted(neigh_dists))

    return dist, layers, vertex_type, neighbor_profile


def build_transition_data(G: nx.Graph, root: int):
    dist, layers, vertex_type, neighbor_profile = root_layer_types(G, root)

    D = max(dist.values())
    per_layer_type_counts = {}
    transitions = defaultdict(Counter)

    for i in range(D + 1):
        type_counts = Counter(vertex_type[v] for v in layers[i])
        per_layer_type_counts[i] = type_counts

        for v in layers[i]:
            src = {
                "layer": i,
                "type": vertex_type[v],
            }

            for u in G.neighbors(v):
                dst = {
                    "layer": dist[u],
                    "type": vertex_type[u],
                }
                key = (
                    i,
                    vertex_type[v],
                    dist[u] - i,   # -1 inward, 0 same layer, +1 outward
                    dist[u],
                    vertex_type[u],
                )
                transitions[key] = transitions.get(key, 0) + 1

    return dist, layers, vertex_type, per_layer_type_counts, transitions


def summarize_root(G: nx.Graph, root: int):
    dist, layers, vertex_type, per_layer_type_counts, transitions = build_transition_data(G, root)

    print("\n" + "=" * 80)
    print(f"ROOT {root}")
    print("=" * 80)

    print("layer type counts:")
    for i in sorted(per_layer_type_counts):
        print(f"  layer {i}:")
        for typ, c in sorted(per_layer_type_counts[i].items()):
            print(f"    {typ}  x{c}")

    print("\ntransition rules (aggregated):")
    by_src = defaultdict(Counter)
    for (i, src_type, step, j, dst_type), count in transitions.items():
        by_src[(i, src_type)][(step, j, dst_type)] += count

    report = {
        "root": root,
        "layer_type_counts": {},
        "transitions": {},
    }

    for i in sorted(per_layer_type_counts):
        report["layer_type_counts"][str(i)] = {
            str(k): int(v) for k, v in sorted(per_layer_type_counts[i].items())
        }

    for (i, src_type), counter in sorted(by_src.items()):
        print(f"\n  source layer {i}, source type {src_type}:")
        total_vertices = per_layer_type_counts[i][src_type]
        print(f"    source vertices of this type: {total_vertices}")
        for (step, j, dst_type), count in sorted(counter.items()):
            per_vertex = count / total_vertices
            arrow = { -1: "in", 0: "same", 1: "out" }[step]
            print(
                f"    --{arrow}--> layer {j}, type {dst_type}: "
                f"total {count}, per-vertex {per_vertex:.3f}"
            )

        report["transitions"][f"layer{i}_type{src_type}"] = {
            f"{step}:{j}:{dst_type}": {
                "total": int(count),
                "per_vertex": float(count / total_vertices),
            }
            for (step, j, dst_type), count in sorted(counter.items())
        }

    return report


def main():
    G = load_g60()

    roots = [0, 1, 4, 38]
    full = {"roots": []}

    for r in roots:
        rep = summarize_root(G, r)
        full["roots"].append(rep)

    out_path = ROOT / "reports" / "build_radial_type_automaton.json"
    out_path.write_text(json.dumps(full, indent=2), encoding="utf-8")
    print(f"\nsaved {out_path}")


if __name__ == "__main__":
    main()
