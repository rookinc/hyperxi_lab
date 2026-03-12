#!/usr/bin/env python3

"""
visualize_thalean_mode.py

Compute and inspect a single harmonic mode of the Thalean graph.

Outputs:
  artifacts/reports/thalean_mode_<k>.txt
  artifacts/reports/thalean_mode_<k>.csv

Usage:
  python3 scripts/visualize_thalean_mode.py --mode 0
  python3 scripts/visualize_thalean_mode.py --mode 17
"""

from __future__ import annotations

from pathlib import Path
import argparse
import csv
import math

import numpy as np
import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "artifacts" / "census" / "thalion_graph.g6"
REPORT_DIR = ROOT / "artifacts" / "reports"


def load_graph() -> nx.Graph:
    data = GRAPH_PATH.read_text(encoding="utf-8").strip()
    g = nx.from_graph6_bytes(data.encode("ascii"))
    return nx.convert_node_labels_to_integers(g)


def laplacian_matrix(g: nx.Graph) -> np.ndarray:
    a = nx.to_numpy_array(g, dtype=float)
    return 4.0 * np.eye(g.number_of_nodes()) - a


def mode_data(g: nx.Graph) -> tuple[np.ndarray, np.ndarray]:
    L = laplacian_matrix(g)
    vals, vecs = np.linalg.eigh(L)
    return vals, vecs


def sign_label(x: float, tol: float = 1e-9) -> str:
    if x > tol:
        return "+"
    if x < -tol:
        return "-"
    return "0"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", type=int, required=True, help="Mode index in ascending Laplacian order")
    args = ap.parse_args()

    g = load_graph()
    vals, vecs = mode_data(g)

    n = g.number_of_nodes()
    k = args.mode
    if not (0 <= k < n):
        raise SystemExit(f"mode index must be in [0, {n-1}]")

    lam = float(vals[k])
    vec = vecs[:, k].astype(float)

    # normalize for readability
    maxabs = float(np.max(np.abs(vec)))
    if maxabs > 0:
        vec = vec / maxabs

    order = sorted(range(n), key=lambda i: vec[i])

    pos = sum(1 for x in vec if x > 1e-9)
    neg = sum(1 for x in vec if x < -1e-9)
    zer = n - pos - neg

    out_txt = REPORT_DIR / f"thalean_mode_{k:02d}.txt"
    out_csv = REPORT_DIR / f"thalean_mode_{k:02d}.csv"

    # CSV
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["vertex", "amplitude", "sign"])
        for i, x in enumerate(vec):
            w.writerow([i, f"{x:.10f}", sign_label(float(x))])

    # Text report
    lines: list[str] = []
    lines.append("=" * 80)
    lines.append("THALEAN MODE VISUALIZATION")
    lines.append("=" * 80)
    lines.append(f"graph: {GRAPH_PATH}")
    lines.append(f"mode index: {k}")
    lines.append(f"laplacian eigenvalue: {lam:.10f}")
    lines.append("")
    lines.append("SIGN COUNTS")
    lines.append("-" * 80)
    lines.append(f"positive: {pos}")
    lines.append(f"negative: {neg}")
    lines.append(f"zero-ish : {zer}")
    lines.append("")
    lines.append("VERTEX AMPLITUDES (sorted)")
    lines.append("-" * 80)
    for i in order:
        lines.append(f"v={i:02d}  amp={vec[i]: .10f}  sign={sign_label(float(vec[i]))}")
    lines.append("")
    lines.append("TOP POSITIVE VERTICES")
    lines.append("-" * 80)
    for i in sorted(range(n), key=lambda j: vec[j], reverse=True)[:12]:
        lines.append(f"v={i:02d}  amp={vec[i]: .10f}")
    lines.append("")
    lines.append("TOP NEGATIVE VERTICES")
    lines.append("-" * 80)
    for i in sorted(range(n), key=lambda j: vec[j])[:12]:
        lines.append(f"v={i:02d}  amp={vec[i]: .10f}")

    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print()
    print(f"wrote: {out_txt}")
    print(f"wrote: {out_csv}")


if __name__ == "__main__":
    main()
