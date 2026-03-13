#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "spectral"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_graph() -> nx.Graph:
    from hyperxi.combinatorics.chamber_graph import build_chamber_graph

    raw = build_chamber_graph()
    G = nx.Graph()
    G.add_nodes_from(raw.vertices)
    G.add_edges_from(raw.edges)
    return G


def adjacency_spectrum(G: nx.Graph) -> tuple[np.ndarray, np.ndarray]:
    nodes = sorted(G.nodes())
    A = nx.to_numpy_array(G, nodelist=nodes, dtype=float)
    eigvals, eigvecs = np.linalg.eigh(A)
    order = np.argsort(eigvals)[::-1]
    return eigvals[order], eigvecs[:, order]


def multiplicity_block(eigvals: np.ndarray, idx: int, tol: float = 1e-8) -> list[int]:
    target = eigvals[idx]
    return [j for j, val in enumerate(eigvals) if abs(val - target) <= tol]


def sign_pattern(vec: np.ndarray, eps: float = 1e-10) -> tuple[int, int, int]:
    pos = int(np.sum(vec > eps))
    neg = int(np.sum(vec < -eps))
    zero = int(len(vec) - pos - neg)
    return pos, neg, zero


def save_mode_plot(
    G: nx.Graph,
    vec: np.ndarray,
    outpath: Path,
    title: str,
    seed: int = 42,
) -> None:
    pos = nx.spring_layout(G, seed=seed)
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
    print("=" * 80)
    print("CHAMBER GRAPH LOW MODE ANALYSIS")
    print("=" * 80)

    G = load_graph()
    n = G.number_of_nodes()
    m = G.number_of_edges()
    degs = sorted(set(dict(G.degree()).values()))

    print(f"vertices: {n}")
    print(f"edges:    {m}")
    print(f"degrees:  {degs}")

    eigvals, eigvecs = adjacency_spectrum(G)

    report_lines: list[str] = []
    report_lines.append("=" * 80)
    report_lines.append("CHAMBER GRAPH LOW MODE ANALYSIS")
    report_lines.append("=" * 80)
    report_lines.append(f"vertices: {n}")
    report_lines.append(f"edges:    {m}")
    report_lines.append(f"degrees:  {degs}")
    report_lines.append("")

    report_lines.append("TOP 12 ADJACENCY EIGENVALUES")
    report_lines.append("-" * 80)
    for i, val in enumerate(eigvals[:12]):
        report_lines.append(f"{i:2d}: {val: .9f}")
    report_lines.append("")

    lam0 = eigvals[0]
    block0 = multiplicity_block(eigvals, 0)
    report_lines.append("GROUND BLOCK")
    report_lines.append("-" * 80)
    report_lines.append(f"lambda_0 = {lam0:.9f}")
    report_lines.append(f"multiplicity = {len(block0)}")
    report_lines.append("")

    lam1 = eigvals[1]
    block1 = multiplicity_block(eigvals, 1)
    report_lines.append("FIRST EXCITED BLOCK")
    report_lines.append("-" * 80)
    report_lines.append(f"lambda_1 = {lam1:.9f}")
    report_lines.append(f"multiplicity = {len(block1)}")
    report_lines.append(f"indices = {block1}")
    report_lines.append(f"laplacian eigenvalue = {4.0 - lam1:.9f}")
    report_lines.append(f"mode frequency sqrt(4-lambda_1) = {math.sqrt(max(0.0, 4.0 - lam1)):.9f}")
    report_lines.append("")

    print()
    print("FIRST EXCITED BLOCK")
    print("-" * 80)
    print(f"lambda_1 ≈ {lam1:.9f}")
    print(f"multiplicity = {len(block1)}")
    print(f"indices = {block1}")

    for k, j in enumerate(block1, start=1):
        vec = eigvecs[:, j].copy()
        anchor = int(np.argmax(np.abs(vec)))
        if vec[anchor] < 0:
            vec *= -1.0

        pos, neg, zero = sign_pattern(vec)
        l2 = float(np.linalg.norm(vec))
        linf = float(np.max(np.abs(vec)))

        png_path = REPORT_DIR / f"chamber_low_mode_{k:02d}.png"
        save_mode_plot(
            G,
            vec,
            png_path,
            title=f"Chamber Low Mode {k}  (lambda={lam1:.6f})",
        )

        report_lines.append(f"MODE {k}")
        report_lines.append("-" * 80)
        report_lines.append(f"eigen-index = {j}")
        report_lines.append(f"eigenvalue  = {eigvals[j]:.9f}")
        report_lines.append(f"sign counts = +:{pos}  -:{neg}  0:{zero}")
        report_lines.append(f"||v||_2     = {l2:.9f}")
        report_lines.append(f"||v||_inf   = {linf:.9f}")
        report_lines.append(f"image       = {png_path.relative_to(ROOT)}")
        report_lines.append("")

        print(f"mode {k}: saved {png_path.relative_to(ROOT)}")

    txt_path = REPORT_DIR / "chamber_low_modes.txt"
    txt_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print()
    print(f"saved report: {txt_path.relative_to(ROOT)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
