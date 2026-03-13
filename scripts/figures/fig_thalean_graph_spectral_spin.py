from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
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


def spectral_embedding_3d(G: nx.Graph) -> tuple[dict[int, np.ndarray], np.ndarray]:
    A, nodes = adjacency_matrix(G)

    vals, vecs = np.linalg.eigh(A)
    order = np.argsort(vals)[::-1]
    vals = vals[order]
    vecs = vecs[:, order]

    # Skip the principal eigenvector; use the next three coordinates.
    X = vecs[:, 1:4].copy()

    norms = np.linalg.norm(X, axis=1)
    max_norm = float(np.max(norms))
    if max_norm > 0:
        X /= max_norm

    pos3 = {nodes[i]: X[i] for i in range(len(nodes))}
    return pos3, vals


def partition_by_sign(pos3: dict[int, np.ndarray], axis: int = 2) -> tuple[list[int], list[int]]:
    neg = []
    pos = []
    for v in sorted(pos3):
        if pos3[v][axis] < 0:
            neg.append(v)
        else:
            pos.append(v)
    return neg, pos


def radius_stats(pos3: dict[int, np.ndarray]) -> tuple[float, float, float]:
    arr = np.array([pos3[v] for v in sorted(pos3)])
    r = np.linalg.norm(arr, axis=1)
    return float(r.min()), float(r.max()), float(r.std())


def draw_frame(
    ax,
    G: nx.Graph,
    pos3: dict[int, np.ndarray],
    elev: float,
    azim: float,
    lower: list[int],
    upper: list[int],
) -> None:
    ax.clear()
    ax.set_axis_off()
    ax.view_init(elev=elev, azim=azim)

    # edges
    for u, v in G.edges():
        x1, y1, z1 = pos3[u]
        x2, y2, z2 = pos3[v]
        ax.plot(
            [x1, x2],
            [y1, y2],
            [z1, z2],
            linewidth=0.9,
            alpha=0.50,
            color="0.30",
            zorder=1,
        )

    # nodes: two tones by sign of z-coordinate
    xs0 = [pos3[v][0] for v in lower]
    ys0 = [pos3[v][1] for v in lower]
    zs0 = [pos3[v][2] for v in lower]

    xs1 = [pos3[v][0] for v in upper]
    ys1 = [pos3[v][1] for v in upper]
    zs1 = [pos3[v][2] for v in upper]

    ax.scatter(
        xs0, ys0, zs0,
        s=34,
        edgecolors="black",
        facecolors="0.80",
        linewidths=0.8,
        depthshade=False,
    )
    ax.scatter(
        xs1, ys1, zs1,
        s=40,
        edgecolors="black",
        facecolors="white",
        linewidths=0.9,
        depthshade=False,
    )

    # faint coordinate axes
    ax.plot([-1.15, 1.15], [0.0, 0.0], [0.0, 0.0], linewidth=0.6, alpha=0.20, color="0.4")
    ax.plot([0.0, 0.0], [-1.15, 1.15], [0.0, 0.0], linewidth=0.6, alpha=0.20, color="0.4")
    ax.plot([0.0, 0.0], [0.0, 0.0], [-1.15, 1.15], linewidth=0.6, alpha=0.20, color="0.4")

    limit = 1.08
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(-limit, limit)


def save_static_views(
    G: nx.Graph,
    pos3: dict[int, np.ndarray],
    lower: list[int],
    upper: list[int],
) -> None:
    views = [
        ("view_a", 18, 20),
        ("view_b", 22, 38),
        ("view_c", 28, 52),
        ("view_d", 12, 72),
        ("view_e", 8, 110),
        ("view_f", 32, 145),
    ]

    for suffix, elev, azim in views:
        fig = plt.figure(figsize=(8.8, 8.4))
        ax = fig.add_subplot(111, projection="3d")
        draw_frame(ax, G, pos3, elev=elev, azim=azim, lower=lower, upper=upper)

        png_path = OUTDIR / f"thalean_graph_spectral_3d_{suffix}.png"
        pdf_path = OUTDIR / f"thalean_graph_spectral_3d_{suffix}.pdf"
        fig.savefig(png_path, bbox_inches="tight", dpi=240)
        fig.savefig(pdf_path, bbox_inches="tight")
        plt.close(fig)

        print(f"Wrote: {png_path}")
        print(f"Wrote: {pdf_path}")


def save_spin_gif(
    G: nx.Graph,
    pos3: dict[int, np.ndarray],
    lower: list[int],
    upper: list[int],
    elev: float = 22.0,
    nframes: int = 120,
) -> None:
    fig = plt.figure(figsize=(8.8, 8.4))
    ax = fig.add_subplot(111, projection="3d")

    def update(frame: int):
        azim = 360.0 * frame / nframes
        draw_frame(ax, G, pos3, elev=elev, azim=azim, lower=lower, upper=upper)
        return []

    anim = FuncAnimation(fig, update, frames=nframes, interval=60, blit=False)
    gif_path = OUTDIR / "thalean_graph_spectral_spin.gif"
    anim.save(gif_path, writer=PillowWriter(fps=20))
    plt.close(fig)

    print(f"Wrote: {gif_path}")


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    G = build_nx_graph()
    pos3, vals = spectral_embedding_3d(G)
    lower, upper = partition_by_sign(pos3, axis=2)

    rmin, rmax, rstd = radius_stats(pos3)

    print("Top 10 eigenvalues:")
    for lam in vals[:10]:
        print(f"  {lam:.6f}")

    print(f"z<0 count: {len(lower)}")
    print(f"z>=0 count: {len(upper)}")
    print(f"radius min: {rmin:.6f}")
    print(f"radius max: {rmax:.6f}")
    print(f"radius std: {rstd:.6f}")

    save_static_views(G, pos3, lower, upper)
    save_spin_gif(G, pos3, lower, upper, elev=22.0, nframes=120)


if __name__ == "__main__":
    main()
