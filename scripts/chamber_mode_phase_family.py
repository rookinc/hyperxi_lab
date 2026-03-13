#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "reports" / "spectral" / "phase_family"
OUTDIR.mkdir(parents=True, exist_ok=True)


def load_graph() -> nx.Graph:
    from hyperxi.combinatorics.chamber_graph import build_chamber_graph
    raw = build_chamber_graph()
    G = nx.Graph()
    G.add_nodes_from(raw.vertices)
    G.add_edges_from(raw.edges)
    return G


def adjacency_spectrum(G: nx.Graph):
    nodes = sorted(G.nodes())
    A = nx.to_numpy_array(G, nodelist=nodes, dtype=float)
    eigvals, eigvecs = np.linalg.eigh(A)
    order = np.argsort(eigvals)[::-1]
    return nodes, eigvals[order], eigvecs[:, order]


def multiplicity_block(eigvals: np.ndarray, idx: int, tol: float = 1e-8):
    target = eigvals[idx]
    return [j for j, val in enumerate(eigvals) if abs(val - target) <= tol]


def save_plot(G: nx.Graph, vec: np.ndarray, outpath: Path, title: str, pos) -> None:
    vmax = float(np.max(np.abs(vec))) or 1.0
    plt.figure(figsize=(8, 8))
    nx.draw_networkx_edges(G, pos, alpha=0.25, width=1.0)
    nodes = nx.draw_networkx_nodes(
        G,
        pos,
        node_color=vec,
        cmap="coolwarm",
        vmin=-vmax,
        vmax=vmax,
        node_size=140,
        linewidths=0.5,
        edgecolors="black",
    )
    plt.colorbar(nodes, shrink=0.8)
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(outpath, dpi=180)
    plt.close()


def main() -> None:
    G = load_graph()
    nodes, eigvals, eigvecs = adjacency_spectrum(G)
    block = multiplicity_block(eigvals, 1)
    if len(block) != 2:
        raise RuntimeError(f"Expected a 2D first excited block, got {len(block)}")

    v1 = eigvecs[:, block[0]].copy()
    v2 = eigvecs[:, block[1]].copy()

    a1 = int(np.argmax(np.abs(v1)))
    if v1[a1] < 0:
        v1 *= -1.0
    a2 = int(np.argmax(np.abs(v2)))
    if v2[a2] < 0:
        v2 *= -1.0

    pos = nx.spring_layout(G, seed=42)

    report = []
    report.append("PHASE FAMILY OF FIRST EXCITED CHAMBER MODES")
    report.append("=" * 72)
    report.append(f"lambda_1 = {eigvals[1]:.9f}")
    report.append(f"indices = {block}")
    report.append("")

    steps = 12
    for k in range(steps):
        theta = 2.0 * math.pi * k / steps
        vec = math.cos(theta) * v1 + math.sin(theta) * v2

        pos_count = int(np.sum(vec > 1e-10))
        neg_count = int(np.sum(vec < -1e-10))
        zero_count = int(len(vec) - pos_count - neg_count)

        outpath = OUTDIR / f"phase_{k:02d}.png"
        save_plot(
            G,
            vec,
            outpath,
            title=f"Phase family k={k}, theta={theta:.3f}",
            pos=pos,
        )

        report.append(f"k={k:02d}  theta={theta:.9f}")
        report.append(f"sign counts: +:{pos_count}  -:{neg_count}  0:{zero_count}")
        report.append(f"image: {outpath.relative_to(ROOT)}")
        report.append("")

        print(f"saved {outpath.relative_to(ROOT)}")

    (OUTDIR / "phase_family_report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"saved {OUTDIR.relative_to(ROOT) / 'phase_family_report.txt'}")


if __name__ == "__main__":
    main()
