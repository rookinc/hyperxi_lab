from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


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


def spectral_embedding_3d(G: nx.Graph) -> tuple[dict[int, np.ndarray], np.ndarray, np.ndarray]:
    A, nodes = adjacency_matrix(G)

    vals, vecs = np.linalg.eigh(A)
    order = np.argsort(vals)[::-1]
    vals = vals[order]
    vecs = vecs[:, order]

    # Skip the principal eigenvector and use the next three coordinates.
    X = vecs[:, 1:4].copy()

    norms = np.linalg.norm(X, axis=1)
    max_norm = float(np.max(norms))
    if max_norm > 0:
        X /= max_norm

    pos3 = {nodes[i]: X[i] for i in range(len(nodes))}
    return pos3, vals, vecs


def partition_by_sign(pos3: dict[int, np.ndarray], axis: int = 2) -> tuple[list[int], list[int]]:
    neg = []
    pos = []
    for v in sorted(pos3):
        if pos3[v][axis] < 0:
            neg.append(v)
        else:
            pos.append(v)
    return neg, pos


def draw_3d() -> tuple[Path, Path]:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    G = build_nx_graph()
    pos3, vals, _ = spectral_embedding_3d(G)
    nodes = sorted(G.nodes())

    lower, upper = partition_by_sign(pos3, axis=2)

    fig = plt.figure(figsize=(9.2, 8.8))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_axis_off()

    # Draw edges first
    for u, v in G.edges():
        x1, y1, z1 = pos3[u]
        x2, y2, z2 = pos3[v]
        ax.plot(
            [x1, x2],
            [y1, y2],
            [z1, z2],
            linewidth=0.9,
            alpha=0.55,
            color="0.30",
            zorder=1,
        )

    # Draw nodes in two passes for a little depth clarity
    xs0 = [pos3[v][0] for v in lower]
    ys0 = [pos3[v][1] for v in lower]
    zs0 = [pos3[v][2] for v in lower]

    xs1 = [pos3[v][0] for v in upper]
    ys1 = [pos3[v][1] for v in upper]
    zs1 = [pos3[v][2] for v in upper]

    ax.scatter(xs0, ys0, zs0, s=34, edgecolors="black", facecolors="0.80", linewidths=0.8, depthshade=False)
    ax.scatter(xs1, ys1, zs1, s=40, edgecolors="black", facecolors="white", linewidths=0.9, depthshade=False)

    # Light guide axes through the origin
    ax.plot([-1.15, 1.15], [0.0, 0.0], [0.0, 0.0], linewidth=0.6, alpha=0.25, color="0.4")
    ax.plot([0.0, 0.0], [-1.15, 1.15], [0.0, 0.0], linewidth=0.6, alpha=0.25, color="0.4")
    ax.plot([0.0, 0.0], [0.0, 0.0], [-1.15, 1.15], linewidth=0.6, alpha=0.25, color="0.4")

    ax.view_init(elev=22, azim=38)

    limit = 1.08
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(-limit, limit)

    pdf_path = OUTDIR / "thalean_graph_spectral_3d.pdf"
    png_path = OUTDIR / "thalean_graph_spectral_3d.png"

    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, bbox_inches="tight", dpi=260)
    plt.close(fig)

    print("Top 10 eigenvalues:")
    for lam in vals[:10]:
        print(f"  {lam:.6f}")

    print(f"z<0 count: {len(lower)}")
    print(f"z>=0 count: {len(upper)}")

    return pdf_path, png_path


def main() -> None:
    pdf_path, png_path = draw_3d()
    print(f"Wrote: {pdf_path}")
    print(f"Wrote: {png_path}")


if __name__ == "__main__":
    main()
