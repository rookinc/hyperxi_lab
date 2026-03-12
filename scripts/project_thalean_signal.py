#!/usr/bin/env python3

from pathlib import Path
import argparse
import json
import numpy as np
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "artifacts" / "census" / "thalion_graph.g6"
TEMPLATE_PATH = ROOT / "spec" / "thalean_templates.v1.json"
REPORT_DIR = ROOT / "artifacts" / "reports"


def load_graph():
    data = GRAPH_PATH.read_text(encoding="utf-8").strip()
    g = nx.from_graph6_bytes(data.encode("ascii"))
    return nx.convert_node_labels_to_integers(g)


def load_templates():
    data = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    return data["templates"]


def make_signal(kind: str, n: int, vertex: int) -> np.ndarray:
    psi = np.zeros(n, dtype=float)

    if kind == "delta":
        psi[vertex] = 1.0
    elif kind == "pair":
        psi[vertex] = 1.0
        psi[(vertex + 1) % n] = -1.0
    elif kind == "uniform":
        psi[:] = 1.0
    else:
        raise ValueError(f"unknown signal kind: {kind}")

    norm = np.linalg.norm(psi)
    if norm > 0:
        psi = psi / norm
    return psi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--signal", choices=["delta", "pair", "uniform"], default="delta")
    ap.add_argument("--vertex", type=int, default=0)
    ap.add_argument("--top", type=int, default=12)
    args = ap.parse_args()

    g = load_graph()
    n = g.number_of_nodes()
    psi = make_signal(args.signal, n, args.vertex)

    templates = load_templates()

    rows = []
    recon = np.zeros(n, dtype=float)

    for t in templates:
        mode = int(t["mode_index"])
        lam = float(t["eigenvalue"])
        vec = np.array(t["vector"], dtype=float)

        coeff = float(np.dot(vec, psi))
        power = coeff * coeff
        recon += coeff * vec

        rows.append({
            "mode_index": mode,
            "eigenvalue": lam,
            "coefficient": coeff,
            "power": power,
        })

    rows.sort(key=lambda r: abs(r["coefficient"]), reverse=True)

    err = float(np.linalg.norm(psi - recon))

    out_txt = REPORT_DIR / f"thalean_projection_{args.signal}_v{args.vertex:02d}.txt"

    lines = []
    lines.append("=" * 80)
    lines.append("THALEAN MODE PROJECTION")
    lines.append("=" * 80)
    lines.append(f"signal kind: {args.signal}")
    lines.append(f"vertex: {args.vertex}")
    lines.append(f"top modes shown: {args.top}")
    lines.append(f"reconstruction error: {err:.12f}")
    lines.append("")
    lines.append("TOP MODE OVERLAPS")
    lines.append("-" * 80)
    lines.append("rank  mode  eigenvalue      coefficient      power")
    for i, row in enumerate(rows[:args.top], start=1):
        lines.append(
            f"{i:>4d}  {row['mode_index']:>4d}  "
            f"{row['eigenvalue']:>10.6f}  "
            f"{row['coefficient']:>14.10f}  "
            f"{row['power']:>12.10f}"
        )

    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print()
    print(f"wrote: {out_txt}")


if __name__ == "__main__":
    main()
