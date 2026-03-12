#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
from collections import Counter
import argparse
import json

import networkx as nx
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
THALEAN_G6 = ROOT / "artifacts" / "census" / "thalion_graph.g6"
OUT_PATH = ROOT / "artifacts" / "reports" / "random_regular_vs_thalean.txt"


def load_thalean() -> nx.Graph:
    data = THALEAN_G6.read_text(encoding="utf-8").strip()
    g = nx.from_graph6_bytes(data.encode("ascii"))
    return nx.convert_node_labels_to_integers(g)


def shell_counts(g: nx.Graph, root: int = 0) -> list[int]:
    dist = nx.single_source_shortest_path_length(g, root)
    counts = Counter(dist.values())
    return [counts[k] for k in sorted(counts)]


def triangle_count(g: nx.Graph) -> int:
    return sum(nx.triangles(g).values()) // 3


def graph_spectrum(g: nx.Graph) -> list[float]:
    A = nx.to_numpy_array(g, dtype=float)
    vals = np.linalg.eigvalsh(A)
    return sorted(float(round(x, 6)) for x in vals)


def fingerprint(g: nx.Graph) -> dict:
    return {
        "vertices": g.number_of_nodes(),
        "edges": g.number_of_edges(),
        "degree_set": sorted(set(dict(g.degree()).values())),
        "triangles": triangle_count(g),
        "diameter": nx.diameter(g) if nx.is_connected(g) else None,
        "shells": shell_counts(g, 0) if nx.is_connected(g) else None,
        "spectrum": graph_spectrum(g),
    }


def spectrum_distance(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return float("inf")
    return float(sum(abs(x - y) for x, y in zip(a, b)))


def score_against(th_fp: dict, fp: dict) -> dict:
    return {
        "degree_match": fp["degree_set"] == th_fp["degree_set"],
        "triangle_match": fp["triangles"] == th_fp["triangles"],
        "diameter_match": fp["diameter"] == th_fp["diameter"],
        "shell_match": fp["shells"] == th_fp["shells"],
        "spectrum_distance": spectrum_distance(fp["spectrum"], th_fp["spectrum"]),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=12)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)

    th = load_thalean()
    th_fp = fingerprint(th)

    rows = []

    for i in range(args.samples):
        # random 4-regular graph on 60 vertices
        g = nx.random_regular_graph(4, 60, seed=int(rng.integers(0, 10**9)))
        fp = fingerprint(g)
        cmp = score_against(th_fp, fp)

        score = (
            int(cmp["degree_match"]) +
            int(cmp["triangle_match"]) +
            int(cmp["diameter_match"]) +
            int(cmp["shell_match"])
        )

        rows.append({
            "sample": i,
            "score": score,
            "triangles": fp["triangles"],
            "diameter": fp["diameter"],
            "shells": fp["shells"],
            "spectrum_distance": cmp["spectrum_distance"],
            "matches": cmp,
        })

    rows.sort(key=lambda r: (r["score"], -r["spectrum_distance"]), reverse=True)

    lines = []
    lines.append("=" * 80)
    lines.append("RANDOM 4-REGULAR 60-VERTEX GRAPHS VS THALEAN")
    lines.append("=" * 80)
    lines.append("THALEAN FINGERPRINT")
    lines.append("-" * 80)
    lines.append(json.dumps({
        "triangles": th_fp["triangles"],
        "diameter": th_fp["diameter"],
        "shells": th_fp["shells"],
    }, indent=2))
    lines.append("")
    lines.append("SAMPLES")
    lines.append("-" * 80)

    for row in rows:
        lines.append(f"sample={row['sample']}  score={row['score']}  spectrum_distance={row['spectrum_distance']:.6f}")
        lines.append(f"    triangles={row['triangles']}  diameter={row['diameter']}")
        lines.append(f"    shells={row['shells']}")
        lines.append(f"    matches={row['matches']}")
        lines.append("")

    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
