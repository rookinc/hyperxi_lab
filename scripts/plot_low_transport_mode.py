#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "spectral" / "transport_modes"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_pair_graph(path: Path) -> nx.Graph:
    G = nx.Graph()

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if not line.lower().startswith("decagon"):
            continue
        if ":" not in line:
            continue

        _, rhs = line.split(":", 1)
        rhs = rhs.strip()
        if not rhs.startswith("["):
            continue

        cyc = ast.literal_eval(rhs)
        if not isinstance(cyc, list):
            continue

        cyc = [int(x) for x in cyc]
        n = len(cyc)
        for i in range(n):
            a = cyc[i]
            b = cyc[(i + 1) % n]
            G.add_edge(a, b)

    if G.number_of_nodes() == 0:
        raise SystemExit(f"No decagon cycles parsed from {path}")

    return G


def adjacency_eigs(G: nx.Graph):
    nodes = sorted(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    A = np.zeros((len(nodes), len(nodes)), dtype=float)

    for u, v in G.edges():
        i = idx[u]
        j = idx[v]
        A[i, j] = 1.0
        A[j, i] = 1.0

    vals, vecs = np.linalg.eigh(A)
    order = np.argsort(vals)
    vals = vals[order]
    vecs = vecs[:, order]
    return nodes, A, vals, vecs


def shell_profile(G: nx.Graph, src: int) -> tuple[int, ...]:
    d = nx.single_source_shortest_path_length(G, src)
    diam = max(d.values())
    return tuple(sum(1 for x in d.values() if x == k) for k in range(diam + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input",
        default=str(ROOT / "reports" / "decagons" / "ordered_decagon_pair_cycles.txt"),
        help="Path to ordered_decagon_pair_cycles.txt",
    )
    ap.add_argument(
        "--mode-index",
        type=int,
        default=1,
        help="Eigenmode index after sorting eigenvalues ascending.",
    )
    args = ap.parse_args()

    in_path = Path(args.input)
    if not in_path.is_absolute():
        in_path = (ROOT / args.input).resolve()
    if not in_path.exists():
        raise SystemExit(f"Missing input file: {in_path}")

    G = load_pair_graph(in_path)
    nodes, A, vals, vecs = adjacency_eigs(G)

    if not (0 <= args.mode_index < len(vals)):
        raise SystemExit(f"--mode-index must be in [0, {len(vals)-1}]")

    lam = float(vals[args.mode_index])
    vec = vecs[:, args.mode_index].copy()

    if vec[np.argmax(np.abs(vec))] < 0:
        vec *= -1.0

    prof = shell_profile(G, nodes[0])

    print("=" * 80)
    print("LOW TRANSPORT MODE")
    print("=" * 80)
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted({d for _, d in G.degree()}))
    print("diameter:", nx.diameter(G))
    print("shell profile from node 0:", prof)
    print()
    print("selected mode index:", args.mode_index)
    print("eigenvalue:", f"{lam:.6f}")
    print()
    print("largest amplitudes")
    top = sorted(zip(nodes, vec), key=lambda x: abs(x[1]), reverse=True)[:12]
    for node, amp in top:
        print(f"node {node:2d}: {amp:+.6f}")

    pos = nx.spring_layout(G, seed=7)

    fig, ax = plt.subplots(figsize=(9, 9))
    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.35, width=1.0)
    vmax = float(np.max(np.abs(vec))) if np.max(np.abs(vec)) > 0 else 1.0

    nx.draw_networkx_nodes(
        G,
        pos,
        ax=ax,
        nodelist=nodes,
        node_color=vec,
        cmap="coolwarm",
        vmin=-vmax,
        vmax=vmax,
        node_size=260,
    )
    nx.draw_networkx_labels(
        G,
        pos,
        ax=ax,
        labels={n: str(n) for n in nodes},
        font_size=7,
    )

    ax.set_title(f"Pair-Transport Eigenmode {args.mode_index} (eigenvalue {lam:.6f})")
    ax.set_axis_off()
    fig.tight_layout()

    png_path = OUT_DIR / f"transport_mode_{args.mode_index:02d}.png"
    fig.savefig(png_path, dpi=220)
    plt.close(fig)

    txt_path = OUT_DIR / f"transport_mode_{args.mode_index:02d}.txt"
    lines = []
    lines.append("=" * 80)
    lines.append("PAIR-TRANSPORT EIGENMODE")
    lines.append("=" * 80)
    lines.append(f"input: {in_path}")
    lines.append(f"mode index: {args.mode_index}")
    lines.append(f"eigenvalue: {lam:.12f}")
    lines.append(f"vertices: {G.number_of_nodes()}")
    lines.append(f"edges: {G.number_of_edges()}")
    lines.append(f"degree set: {sorted({d for _, d in G.degree()})}")
    lines.append(f"diameter: {nx.diameter(G)}")
    lines.append(f"shell profile from node 0: {prof}")
    lines.append("")
    lines.append("NODE AMPLITUDES")
    lines.append("-" * 80)
    for node, amp in zip(nodes, vec):
        lines.append(f"{node:2d}  {amp:+.12f}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print()
    print(f"saved {txt_path.relative_to(ROOT)}")
    print(f"saved {png_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
