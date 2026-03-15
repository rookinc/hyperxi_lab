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


def rooted_data(G: nx.Graph, root: int):
    dist = nx.single_source_shortest_path_length(G, root)
    D = max(dist.values())

    layers = defaultdict(list)
    for v, d in dist.items():
        layers[d].append(v)

    rows = []

    for i in range(D + 1):
        for v in layers[i]:
            inward = []
            same = []
            outward = []

            for u in G.neighbors(v):
                du = dist[u]
                if du == i - 1:
                    inward.append(u)
                elif du == i:
                    same.append(u)
                elif du == i + 1:
                    outward.append(u)
                else:
                    raise RuntimeError(f"bad jump from layer {i} to {du}")

            row = {
                "vertex": v,
                "layer": i,
                "type": (len(inward), len(same), len(outward)),
                "geodesic_parents": len(inward),
                "geodesic_children": len(outward),
                "same_shell_degree": len(same),
                "inward_neighbors": sorted(inward),
                "same_neighbors": sorted(same),
                "outward_neighbors": sorted(outward),
            }
            rows.append(row)

    return dist, layers, rows


def summarize_root(G: nx.Graph, root: int):
    dist, layers, rows = rooted_data(G, root)

    print("\n" + "=" * 80)
    print(f"ROOT {root}")
    print("=" * 80)

    by_layer = defaultdict(list)
    for row in rows:
        by_layer[row["layer"]].append(row)

    report = {"root": root, "layers": {}}

    for i in sorted(by_layer):
        group = by_layer[i]
        print(f"\nlayer {i}  size={len(group)}")

        type_counts = Counter(r["type"] for r in group)
        parent_counts = Counter(r["geodesic_parents"] for r in group)
        child_counts = Counter(r["geodesic_children"] for r in group)
        same_counts = Counter(r["same_shell_degree"] for r in group)

        print("  type counts:")
        for typ, c in sorted(type_counts.items()):
            print(f"    {typ}  x{c}")

        print("  geodesic parent counts:")
        for k, c in sorted(parent_counts.items()):
            print(f"    {k}  x{c}")

        print("  geodesic child counts:")
        for k, c in sorted(child_counts.items()):
            print(f"    {k}  x{c}")

        print("  same-shell degree counts:")
        for k, c in sorted(same_counts.items()):
            print(f"    {k}  x{c}")

        entry = {
            "size": len(group),
            "type_counts": {str(k): int(v) for k, v in sorted(type_counts.items())},
            "parent_counts": {str(k): int(v) for k, v in sorted(parent_counts.items())},
            "child_counts": {str(k): int(v) for k, v in sorted(child_counts.items())},
            "same_counts": {str(k): int(v) for k, v in sorted(same_counts.items())},
            "vertices": [],
        }

        if len(type_counts) > 1:
            print("  detailed rows:")
            for r in sorted(group, key=lambda x: (x["type"], x["vertex"])):
                print(
                    f"    v={r['vertex']:2d} "
                    f"type={r['type']} "
                    f"parents={r['geodesic_parents']} "
                    f"children={r['geodesic_children']} "
                    f"same={r['same_shell_degree']} "
                    f"in={r['inward_neighbors']} "
                    f"sameN={r['same_neighbors']} "
                    f"out={r['outward_neighbors']}"
                )

        for r in group:
            entry["vertices"].append({
                "vertex": r["vertex"],
                "type": list(r["type"]),
                "geodesic_parents": r["geodesic_parents"],
                "geodesic_children": r["geodesic_children"],
                "same_shell_degree": r["same_shell_degree"],
                "inward_neighbors": r["inward_neighbors"],
                "same_neighbors": r["same_neighbors"],
                "outward_neighbors": r["outward_neighbors"],
            })

        report["layers"][str(i)] = entry

    return report


def main():
    G = load_g60()

    roots = [0, 1, 4, 38]
    full = {"roots": []}

    for r in roots:
        rep = summarize_root(G, r)
        full["roots"].append(rep)

    out_path = ROOT / "reports" / "probe_geodesic_parent_child_law.json"
    out_path.write_text(json.dumps(full, indent=2), encoding="utf-8")
    print(f"\nsaved {out_path}")


if __name__ == "__main__":
    main()
