#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT / "scripts"))

from build_true_chamber_graph_from_flags import build_true_chamber_graph, graph6_string


def read_graph6(path: Path) -> nx.Graph:
    text = path.read_text(encoding="utf-8").strip()
    return nx.from_graph6_bytes(text.encode())


def main() -> None:
    print("=" * 80)
    print("CHECK TRUE CHAMBER GRAPH VS SAVED G6")
    print("=" * 80)

    G_true, _, _, _ = build_true_chamber_graph()

    candidates = [
        ROOT / "artifacts" / "census" / "thalean_graph.g6",
        ROOT / "artifacts" / "census" / "thalion_graph.g6",
        ROOT / "artifacts" / "census" / "thalean_antipodal_quotient.g6",
        ROOT / "reports" / "true_quotients" / "true_thalion_quotient.g6",
    ]

    print("TRUE GRAPH")
    print("-" * 80)
    print("vertices:", G_true.number_of_nodes())
    print("edges:", G_true.number_of_edges())
    print("degree set:", sorted(set(dict(G_true.degree()).values())))
    print("graph6:", graph6_string(G_true))
    print()

    print("COMPARISONS")
    print("-" * 80)

    found_any = False
    for path in candidates:
        if not path.exists():
            continue
        found_any = True
        G_saved = read_graph6(path)
        print(f"{path.relative_to(ROOT)}")
        print("  vertices:", G_saved.number_of_nodes())
        print("  edges:", G_saved.number_of_edges())
        print("  degree set:", sorted(set(dict(G_saved.degree()).values())))
        print("  isomorphic:", nx.is_isomorphic(G_true, G_saved))
        print()

    if not found_any:
        print("No candidate .g6 files found.")

    out_dir = ROOT / "reports" / "true_quotients"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "check_true_chamber_graph_vs_saved_g6.txt"

    lines = [
        "=" * 80,
        "CHECK TRUE CHAMBER GRAPH VS SAVED G6",
        "=" * 80,
        "",
        "TRUE GRAPH",
        "-" * 80,
        f"vertices: {G_true.number_of_nodes()}",
        f"edges: {G_true.number_of_edges()}",
        f"degree set: {sorted(set(dict(G_true.degree()).values()))}",
        f"graph6: {graph6_string(G_true)}",
        "",
        "COMPARISONS",
        "-" * 80,
    ]

    for path in candidates:
        if not path.exists():
            continue
        G_saved = read_graph6(path)
        lines.extend([
            str(path.relative_to(ROOT)),
            f"  vertices: {G_saved.number_of_nodes()}",
            f"  edges: {G_saved.number_of_edges()}",
            f"  degree set: {sorted(set(dict(G_saved.degree()).values()))}",
            f"  isomorphic: {nx.is_isomorphic(G_true, G_saved)}",
            "",
        ])

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"saved {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
