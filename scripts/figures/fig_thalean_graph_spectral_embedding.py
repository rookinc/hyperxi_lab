from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUTDIR = ROOT / "paper" / "thalean-paper" / "figures" / "generated"

SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from vertex_connection_model import measured_graph_reindexed


def build_nx_graph() -> nx.Graph:
    adj = measured_graph_reindexed()
    G = nx.Graph()
    for u, nbrs in adj.items():
        G.add_node(u)
        for v in nbrs:
            if u < v:
                G.add_edge(u, v)
    return G


def adjacency_matrix(G: nx.Graph) -> tuple[np.ndarray, list[int]]:
    nodes = sorted(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    A = np.zeros((len(nodes), len(nodes)), dtype=float)
    for u, v in G.edges():
        i = idx[u]
        j = idx[v]
        A[i, j] = 1.0
        A[j, i] = 1.0
    return A, nodes


def spectral_layout_from_adjacency(G: nx.Graph) -> dict[int, np.ndarray]:
    A, nodes = adjacency_matrix(G)

    vals, vecs = np.linalg.eigh(A)
    order = np.argsort(vals)[::-1]
    vals = vals[order]
    vecs = vecs[:, order]

    # Skip the principal eigenvector; use next 3 coordinates
    X = vecs[:, 1:4].copy()

    # Normalize coordinates
    X /= np.max(np.linalg.norm(X, axis=1))

    pos = {nodes[i]: X[i] for i in range(len(nodes))}
    return pos


def project_3d_to_2d(points3: np.ndarray, yaw=0.72, pitch=0.48) -> np.ndarray:
    cy, sy = np.cos(yaw), np.sin(yaw)
    cp, sp = np.cos(pitch), np.sin(pitch)

    Ry = np.array([
        [cy, 0.0, sy],
        [0.0, 1.0, 0.0],
        [-sy, 0.0, cy],
    ])

    Rx = np.array([
        [1.0, 0.0, 0.0],
        [0.0, cp, -sp],
        [0.0, sp, cp],
    ])

    R = Rx @ Ry
    Y = points3 @ R.T
    return Y[:, :2]


def draw() -> tuple[Path, Path]:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    G = build_nx_graph()
    pos3 = spectral_layout_from_adjacency(G)

    nodes = sorted(G.nodes())
    arr3 = np.array([pos3[v] for v in nodes])
    arr2 = project_3d_to_2d(arr3, yaw=0.85, pitch=0.55)

    pos2 = {nodes[i]: arr2[i] for i in range(len(nodes))}

    fig, ax = plt.subplots(figsize=(8.6, 8.6))
    ax.set_aspect("equal")
    ax.axis("off")

    for u, v in G.edges():
        x1, y1 = pos2[u]
        x2, y2 = pos2[v]
        ax.plot([x1, x2], [y1, y2], color="0.25", linewidth=1.0, alpha=0.8, zorder=1)

    xs = [pos2[v][0] for v in nodes]
    ys = [pos2[v][1] for v in nodes]

    ax.scatter(
        xs,
        ys,
        s=36,
        facecolors="white",
        edgecolors="black",
        linewidths=0.9,
        zorder=2,
    )

    pdf_path = OUTDIR / "thalean_graph_spectral_embedding.pdf"
    png_path = OUTDIR / "thalean_graph_spectral_embedding.png"

    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, bbox_inches="tight", dpi=240)
    plt.close(fig)

    return pdf_path, png_path


def main() -> None:
    pdf_path, png_path = draw()
    print(f"Wrote: {pdf_path}")
    print(f"Wrote: {png_path}")


if __name__ == "__main__":
    main()
