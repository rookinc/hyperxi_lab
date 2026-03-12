#!/usr/bin/env python3

"""
b32k_thalean_local_compare.py

Compare local neighborhoods in a B32K transition graph against the
Thalean graph fingerprint.

Expected B32K input formats:
  --b32k-edge-list path/to/edges.csv
    CSV with columns: source,target
  --b32k-json path/to/graph.json
    JSON with either:
      {"edges": [[u,v], [x,y], ...]}
    or
      {"adjacency": {"u": ["v1","v2"], ...}}

The script:
- loads the Thalean graph from artifacts/census/thalion_graph.g6
- loads a B32K graph
- extracts radius-r ego graphs around each B32K vertex
- computes invariants
- reports exact / near matches to the Thalean fingerprint
"""

from __future__ import annotations

from pathlib import Path
from collections import Counter, defaultdict
import argparse
import csv
import json
import math

import networkx as nx
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
THALEAN_G6 = ROOT / "artifacts" / "census" / "thalion_graph.g6"
OUT_PATH = ROOT / "artifacts" / "reports" / "b32k_thalean_local_compare.txt"


def load_thalean() -> nx.Graph:
    data = THALEAN_G6.read_text(encoding="utf-8").strip()
    g = nx.from_graph6_bytes(data.encode("ascii"))
    return nx.convert_node_labels_to_integers(g)


def load_b32k_from_csv(path: Path) -> nx.Graph:
    g = nx.Graph()
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if "source" not in reader.fieldnames or "target" not in reader.fieldnames:
            raise ValueError("CSV must contain columns: source,target")
        for row in reader:
            u = row["source"]
            v = row["target"]
            g.add_edge(u, v)
    return nx.convert_node_labels_to_integers(g)


def load_b32k_from_json(path: Path) -> nx.Graph:
    data = json.loads(path.read_text(encoding="utf-8"))
    g = nx.Graph()

    if "edges" in data:
        for u, v in data["edges"]:
            g.add_edge(str(u), str(v))
    elif "adjacency" in data:
        for u, nbrs in data["adjacency"].items():
            for v in nbrs:
                g.add_edge(str(u), str(v))
    else:
        raise ValueError("JSON must contain 'edges' or 'adjacency'")

    return nx.convert_node_labels_to_integers(g)


def shell_counts(g: nx.Graph, root: int) -> list[int]:
    dist = nx.single_source_shortest_path_length(g, root)
    counts = Counter(dist.values())
    return [counts[k] for k in sorted(counts)]


def graph_spectrum(g: nx.Graph) -> list[tuple[float, int]]:
    A = nx.to_numpy_array(g, dtype=float)
    vals = np.linalg.eigvalsh(A)
    rounded = np.round(vals, 6)
    counts = Counter(float(x) for x in rounded)
    return sorted(counts.items())


def triangle_count(g: nx.Graph) -> int:
    return sum(nx.triangles(g).values()) // 3


def fingerprint(g: nx.Graph, root: int | None = None) -> dict:
    if root is None:
        root = next(iter(g.nodes()))
    degs = sorted(set(dict(g.degree()).values()))
    return {
        "vertices": g.number_of_nodes(),
        "edges": g.number_of_edges(),
        "degree_set": degs,
        "triangles": triangle_count(g),
        "diameter": nx.diameter(g) if nx.is_connected(g) else None,
        "shells": shell_counts(g, root),
        "spectrum": graph_spectrum(g),
    }


def spectrum_distance(spec_a: list[tuple[float, int]], spec_b: list[tuple[float, int]]) -> float:
    def expand(spec):
        vals = []
        for lam, mult in spec:
            vals.extend([lam] * mult)
        return sorted(vals)

    a = expand(spec_a)
    b = expand(spec_b)
    if len(a) != len(b):
        return float("inf")
    return float(sum(abs(x - y) for x, y in zip(a, b)))


def compare_to_thalean(local_fp: dict, th_fp: dict) -> dict:
    return {
        "vertex_match": local_fp["vertices"] == th_fp["vertices"],
        "edge_match": local_fp["edges"] == th_fp["edges"],
        "degree_match": local_fp["degree_set"] == th_fp["degree_set"],
        "triangle_match": local_fp["triangles"] == th_fp["triangles"],
        "shell_match": local_fp["shells"] == th_fp["shells"],
        "diameter_match": local_fp["diameter"] == th_fp["diameter"],
        "spectrum_distance": spectrum_distance(local_fp["spectrum"], th_fp["spectrum"]),
    }


def score_match(comp: dict) -> int:
    score = 0
    for key in ["vertex_match", "edge_match", "degree_match", "triangle_match", "shell_match", "diameter_match"]:
        score += int(bool(comp[key]))
    if comp["spectrum_distance"] == 0.0:
        score += 2
    return score


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--b32k-edge-list", type=Path, help="CSV with columns source,target")
    ap.add_argument("--b32k-json", type=Path, help="JSON graph file")
    ap.add_argument("--radius", type=int, default=6, help="Neighborhood radius to probe")
    ap.add_argument("--top", type=int, default=12, help="Number of best matches to report")
    args = ap.parse_args()

    if not args.b32k_edge_list and not args.b32k_json:
        raise SystemExit("Provide --b32k-edge-list or --b32k-json")

    th = load_thalean()
    th_fp = fingerprint(th, root=0)

    if args.b32k_edge_list:
        b32k = load_b32k_from_csv(args.b32k_edge_list)
        source_path = args.b32k_edge_list
    else:
        b32k = load_b32k_from_json(args.b32k_json)
        source_path = args.b32k_json

    rows = []

    for v in b32k.nodes():
        ego = nx.ego_graph(b32k, v, radius=args.radius)
        if ego.number_of_nodes() < 8:
            continue

        local = nx.convert_node_labels_to_integers(ego)
        local_fp = fingerprint(local, root=0)
        comp = compare_to_thalean(local_fp, th_fp)
        score = score_match(comp)

        rows.append({
            "seed": v,
            "score": score,
            "vertices": local_fp["vertices"],
            "edges": local_fp["edges"],
            "triangles": local_fp["triangles"],
            "diameter": local_fp["diameter"],
            "shells": local_fp["shells"],
            "degree_set": local_fp["degree_set"],
            "spectrum_distance": comp["spectrum_distance"],
            "matches": comp,
        })

    rows.sort(key=lambda r: (-r["score"], r["spectrum_distance"], abs(r["vertices"] - th_fp["vertices"])))

    lines = []
    lines.append("=" * 80)
    lines.append("B32K ↔ THALEAN LOCAL COMPARISON")
    lines.append("=" * 80)
    lines.append(f"B32K source: {source_path}")
    lines.append(f"radius: {args.radius}")
    lines.append("")
    lines.append("THALEAN FINGERPRINT")
    lines.append("-" * 80)
    lines.append(json.dumps(th_fp, indent=2))
    lines.append("")
    lines.append("BEST LOCAL MATCHES")
    lines.append("-" * 80)

    for i, row in enumerate(rows[:args.top], start=1):
        lines.append(f"[{i}] seed={row['seed']}  score={row['score']}  spectrum_distance={row['spectrum_distance']:.6f}")
        lines.append(f"    vertices={row['vertices']} edges={row['edges']} triangles={row['triangles']} diameter={row['diameter']}")
        lines.append(f"    degree_set={row['degree_set']}")
        lines.append(f"    shells={row['shells']}")
        lines.append(f"    matches={row['matches']}")
        lines.append("")

    if rows and rows[0]["score"] >= 6 and rows[0]["spectrum_distance"] == 0.0:
        lines.append("EXACT THALEAN-LIKE LOCAL MATCH FOUND.")
    elif rows and rows[0]["score"] >= 4:
        lines.append("PARTIAL STRUCTURAL MATCH FOUND. Inspect top seeds.")
    else:
        lines.append("No strong Thalean-like local neighborhood found at this radius.")

    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
