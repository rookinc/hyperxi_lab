from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]

G60_CANDIDATES = [
    ROOT / "reports" / "true_quotients" / "true_chamber_graph.g6",
    ROOT / "artifacts" / "census" / "thalean_graph.g6",
]

PARTITION_CANDIDATES = [
    ROOT / "reports" / "true_quotients" / "compare_v4_quotient_to_canonical_dodecahedral_15core.json",
    ROOT / "reports" / "true_quotients" / "export_v4_cover_certificate.json",
]

ZERO_REPORT = ROOT / "reports" / "probe_zero_eigenspace.json"


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


def try_extract_partition(data):
    candidates = []

    if isinstance(data, dict):
        for key in ["fibers", "fiber_partition", "v4_fibers", "orbits", "blocks", "partition", "classes"]:
            if key in data and isinstance(data[key], list):
                candidates.append(data[key])
        for _, v in data.items():
            if isinstance(v, dict):
                for kk in ["fibers", "fiber_partition", "v4_fibers", "orbits", "blocks", "partition", "classes"]:
                    if kk in v and isinstance(v[kk], list):
                        candidates.append(v[kk])

    elif isinstance(data, list):
        candidates.append(data)

    for cand in candidates:
        if len(cand) == 15 and all(isinstance(x, list) and len(x) == 4 for x in cand):
            return cand

    return None


def load_partition():
    path = find_existing(PARTITION_CANDIDATES)
    if path is None:
        return None, None
    print(f"loading partition from: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    fibers = try_extract_partition(data)
    if fibers is None:
        return None, None
    v2f = {}
    for i, fiber in enumerate(fibers):
        for v in fiber:
            v2f[v] = i
    return fibers, v2f


def load_zero_weights():
    """
    Use the existing zero-space basis report to define a simple per-vertex
    'kernel mass' = sum_j |v_j(x)| over the 10 basis vectors.
    """
    if not ZERO_REPORT.exists():
        return None
    data = json.loads(ZERO_REPORT.read_text(encoding="utf-8"))
    basis = data.get("basis", [])
    if not basis:
        return None

    n = 60
    weights = np.zeros(n, dtype=float)

    # reconstruct sparse approximation from top support only if that's all we have
    # this is crude but still useful for correlations
    for row in basis:
        for idx, val in row.get("top_support", []):
            weights[int(idx)] += abs(float(val))

    return weights


def layer_signature(G: nx.Graph, root: int):
    dist = nx.single_source_shortest_path_length(G, root)
    D = max(dist.values())
    layers = defaultdict(list)
    for v, d in dist.items():
        layers[d].append(v)

    layer_data = {}

    for i in range(D + 1):
        typed = []
        for v in layers[i]:
            ai = bi = ci = 0
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

            typed.append({
                "vertex": v,
                "type": (ci, ai, bi),
                "neighbor_dists": tuple(sorted(neigh_dists)),
            })

        layer_data[i] = typed

    return dist, layer_data


def summarize_root(G, root, v2f=None, zero_weights=None):
    dist, layer_data = layer_signature(G, root)

    print("\n" + "=" * 80)
    print(f"ROOT {root}")
    print("=" * 80)

    out = {
        "root": root,
        "layers": {},
    }

    for i in sorted(layer_data):
        typed = layer_data[i]
        type_counts = Counter(t["type"] for t in typed)

        print(f"\nlayer {i}  size={len(typed)}")
        print("type counts:")
        for typ, c in sorted(type_counts.items()):
            print(f"  {typ}  x{c}")

        entry = {
            "size": len(typed),
            "type_counts": {str(k): int(v) for k, v in type_counts.items()},
            "vertices": [],
        }

        # print detailed info only for split layers
        if len(type_counts) > 1:
            print("detailed split:")
            for t in sorted(typed, key=lambda x: (x["type"], x["vertex"])):
                v = t["vertex"]
                fiber = v2f[v] if v2f is not None else None
                z = float(zero_weights[v]) if zero_weights is not None else None
                print(
                    f"  v={v:2d}  type={t['type']}  neigh_dists={t['neighbor_dists']}"
                    + (f"  fiber={fiber}" if fiber is not None else "")
                    + (f"  zero_mass={z:.6f}" if z is not None else "")
                )

        for t in typed:
            v = t["vertex"]
            entry["vertices"].append({
                "vertex": v,
                "type": list(t["type"]),
                "neighbor_dists": list(t["neighbor_dists"]),
                "fiber": v2f[v] if v2f is not None else None,
                "zero_mass": float(zero_weights[v]) if zero_weights is not None else None,
            })

        out["layers"][str(i)] = entry

    return out


def choose_roots(G: nx.Graph):
    # root 0 plus one vertex from the last shell of 0 plus a couple more
    roots = [0]
    dist0 = nx.single_source_shortest_path_length(G, 0)
    far = [v for v, d in dist0.items() if d == max(dist0.values())]
    roots.extend(far[:2])
    roots.extend(sorted(list(G.nodes()))[:2])
    roots = list(dict.fromkeys(roots))
    return roots[:4]


def main():
    G = load_g60()
    fibers, v2f = load_partition()
    zero_weights = load_zero_weights()

    roots = choose_roots(G)
    print(f"chosen roots: {roots}")

    report = {"roots": []}
    for r in roots:
        rep = summarize_root(G, r, v2f=v2f, zero_weights=zero_weights)
        report["roots"].append(rep)

    out_path = ROOT / "reports" / "classify_layer_split_types.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nsaved {out_path}")


if __name__ == "__main__":
    main()
