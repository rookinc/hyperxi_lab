from __future__ import annotations

import math
from pathlib import Path
from collections import deque, defaultdict

import matplotlib.pyplot as plt
import networkx as nx

from hyperxi.combinatorics.chamber_graph import ChamberGraph, build_chamber_graph


ROOT = Path(__file__).resolve().parents[2]
OUTDIR = ROOT / "paper" / "thalean-paper" / "figures" / "generated"


def to_networkx(graph_obj: ChamberGraph) -> nx.Graph:
    G = nx.Graph()
    G.add_nodes_from(graph_obj.vertices)
    G.add_edges_from(graph_obj.edges)
    return G


def bfs_shells(graph: nx.Graph, source: int) -> dict[int, list[int]]:
    dist = {source: 0}
    q = deque([source])

    while q:
        u = q.popleft()
        for v in graph.neighbors(u):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)

    shells: dict[int, list[int]] = defaultdict(list)
    for v, d in dist.items():
        shells[d].append(v)

    for d in shells:
        shells[d].sort()

    return dict(sorted(shells.items()))


def layered_radial_layout(
    graph: nx.Graph,
    source: int = 0,
    base_radius: float = 1.6,
    radius_step: float = 1.25,
) -> dict[int, tuple[float, float]]:
    shells = bfs_shells(graph, source)
    pos: dict[int, tuple[float, float]] = {source: (0.0, 0.0)}

    for shell_index, vertices in shells.items():
        if shell_index == 0:
            continue

        n = len(vertices)
        radius = base_radius + radius_step * (shell_index - 1)
        angle_offset = math.pi / (n if n > 1 else 1) + 0.33 * shell_index

        for k, v in enumerate(vertices):
            theta = angle_offset + 2.0 * math.pi * k / n
            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            pos[v] = (x, y)

    return pos


def draw_graph(graph_obj: ChamberGraph, outpath: Path, source: int = 0) -> None:
    graph = to_networkx(graph_obj)
    pos = layered_radial_layout(graph, source=source)
    shells = bfs_shells(graph, source)

    node_colors = {}
    max_shell = max(shells)
    for d, vertices in shells.items():
        shade = 0.15 + 0.75 * (d / max_shell if max_shell else 0.0)
        for v in vertices:
            node_colors[v] = str(shade)

    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    ax.set_aspect("equal")
    ax.axis("off")

    nx.draw_networkx_edges(
        graph,
        pos,
        ax=ax,
        width=0.9,
        alpha=0.7,
    )

    nx.draw_networkx_nodes(
        graph,
        pos,
        ax=ax,
        node_size=120,
        node_color=[node_colors[v] for v in graph.nodes()],
        edgecolors="black",
        linewidths=0.6,
    )

    nx.draw_networkx_labels(
        graph,
        pos,
        labels={source: str(source)},
        font_size=10,
        font_weight="bold",
        ax=ax,
    )

    ax.set_title("The 60-vertex Thalean graph", fontsize=14, pad=16)

    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    graph_obj = build_chamber_graph()
    graph = to_networkx(graph_obj)

    pdf_path = OUTDIR / "thalean_graph_canonical.pdf"
    png_path = OUTDIR / "thalean_graph_canonical.png"

    draw_graph(graph_obj, pdf_path, source=0)
    draw_graph(graph_obj, png_path, source=0)

    print(f"Wrote: {pdf_path}")
    print(f"Wrote: {png_path}")
    print(f"vertices={graph.number_of_nodes()} edges={graph.number_of_edges()}")


if __name__ == "__main__":
    main()
