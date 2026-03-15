from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


JSON_PATH = Path("reports/true_quotients/export_thalean_graph_definition.json")
FIGURES_DIR = Path("figures")


def load_kernel(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_g60(data: dict) -> nx.Graph:
    G = nx.Graph()
    adjacency = data["adjacency_table"]

    for u_str, nbrs in adjacency.items():
        u = int(u_str)
        G.add_node(u)
        for v in nbrs:
            G.add_edge(u, int(v))

    return G


def validate_g60(G: nx.Graph, data: dict) -> None:
    summary = data["summary"]

    assert G.number_of_nodes() == summary["vertices"], (
        G.number_of_nodes(),
        summary["vertices"],
    )
    assert G.number_of_edges() == summary["edges"], (
        G.number_of_edges(),
        summary["edges"],
    )

    degset = sorted(set(dict(G.degree()).values()))
    assert degset == summary["degree_set"], (degset, summary["degree_set"])

    triangles = sum(nx.triangles(G).values()) // 3
    assert triangles == summary["triangles"], (triangles, summary["triangles"])

    if nx.is_connected(G):
        diameter = nx.diameter(G)
        assert diameter == summary["diameter"], (diameter, summary["diameter"])


def build_quotient_graph(G: nx.Graph, v4_orbits: list[list[int]]) -> tuple[nx.Graph, dict[int, int]]:
    vertex_to_orbit: dict[int, int] = {}

    for orbit_idx, orbit in enumerate(v4_orbits):
        for v in orbit:
            vertex_to_orbit[int(v)] = orbit_idx

    Q = nx.Graph()
    Q.add_nodes_from(range(len(v4_orbits)))

    for u, v in G.edges():
        ou = vertex_to_orbit[u]
        ov = vertex_to_orbit[v]
        if ou != ov:
            Q.add_edge(ou, ov)

    return Q, vertex_to_orbit


def validate_q15(Q: nx.Graph, data: dict) -> None:
    qsum = data["quotient_summary"]

    assert Q.number_of_nodes() == qsum["vertices"], (
        Q.number_of_nodes(),
        qsum["vertices"],
    )
    assert Q.number_of_edges() == qsum["edges"], (
        Q.number_of_edges(),
        qsum["edges"],
    )

    degset = sorted(set(dict(Q.degree()).values()))
    assert degset == qsum["degree_set"], (degset, qsum["degree_set"])

    triangles = sum(nx.triangles(Q).values()) // 3
    assert triangles == qsum["triangles"], (triangles, qsum["triangles"])

    if nx.is_connected(Q):
        diameter = nx.diameter(Q)
        assert diameter == qsum["diameter"], (diameter, qsum["diameter"])


def build_petersen_line_graph() -> nx.Graph:
    P = nx.petersen_graph()
    L = nx.line_graph(P)

    # Relabel edge-vertices of the line graph to 0..14 for cleaner drawing.
    mapping = {node: i for i, node in enumerate(L.nodes())}
    return nx.relabel_nodes(L, mapping)


def shell_profile(G: nx.Graph, source: int | None = None) -> tuple[int, ...]:
    if source is None:
        source = next(iter(G.nodes()))
    lengths = nx.single_source_shortest_path_length(G, source)
    max_d = max(lengths.values())
    return tuple(sum(1 for d in lengths.values() if d == k) for k in range(max_d + 1))


def orbit_colors(n: int) -> list:
    cmap = plt.colormaps["tab20"]
    return [cmap(i / max(1, n - 1)) for i in range(n)]


def lifted_orbit_layout(
    v4_orbits: list[list[int]],
    quotient_pos: dict[int, np.ndarray],
    radius: float = 0.12,
) -> dict[int, np.ndarray]:
    pos: dict[int, np.ndarray] = {}
    for orbit_idx, orbit in enumerate(v4_orbits):
        center = np.array(quotient_pos[orbit_idx], dtype=float)
        orbit_sorted = sorted(int(v) for v in orbit)
        n = len(orbit_sorted)
        for j, v in enumerate(orbit_sorted):
            theta = 2.0 * np.pi * j / n
            offset = radius * np.array([np.cos(theta), np.sin(theta)])
            pos[v] = center + offset
    return pos


def draw_graph(
    G: nx.Graph,
    pos: dict,
    outpath: Path,
    title: str,
    node_color=None,
    node_size: int = 120,
    labels: bool = False,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title(title, fontsize=14)

    nx.draw_networkx_edges(G, pos, ax=ax, width=1.2, alpha=0.6)

    nx.draw_networkx_nodes(
        G,
        pos,
        ax=ax,
        node_color=node_color if node_color is not None else "#4C78A8",
        node_size=node_size,
        edgecolors="black",
        linewidths=0.5,
    )

    if labels:
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=8)

    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    data = load_kernel(JSON_PATH)
    G60 = build_g60(data)
    validate_g60(G60, data)

    v4_orbits = [[int(v) for v in orbit] for orbit in data["v4_orbits"]]
    Q15, vertex_to_orbit = build_quotient_graph(G60, v4_orbits)
    validate_q15(Q15, data)

    LP = build_petersen_line_graph()
    isomorphic = nx.is_isomorphic(Q15, LP)

    print("G60")
    print(f"  vertices: {G60.number_of_nodes()}")
    print(f"  edges: {G60.number_of_edges()}")
    print(f"  degree set: {sorted(set(dict(G60.degree()).values()))}")
    print(f"  triangles: {sum(nx.triangles(G60).values()) // 3}")
    print(f"  diameter: {nx.diameter(G60)}")
    print(f"  shell profile from 0: {shell_profile(G60, 0)}")

    print("\nQ15")
    print(f"  vertices: {Q15.number_of_nodes()}")
    print(f"  edges: {Q15.number_of_edges()}")
    print(f"  degree set: {sorted(set(dict(Q15.degree()).values()))}")
    print(f"  triangles: {sum(nx.triangles(Q15).values()) // 3}")
    print(f"  diameter: {nx.diameter(Q15)}")
    print(f"  shell profile from 0: {shell_profile(Q15, 0)}")

    print(f"\nQ15 ≅ L(Petersen): {isomorphic}")

    # Shared quotient layout
    q15_pos = nx.spring_layout(Q15, seed=17, iterations=300)

    # Figure 1: G60
    g60_pos = lifted_orbit_layout(v4_orbits, q15_pos, radius=0.11)
    draw_graph(
        G60,
        g60_pos,
        FIGURES_DIR / "g60_graph.png",
        "G60 Thalean Graph",
        node_size=90,
    )

    # Figure 2: G60 colored by V4 orbit
    palette = orbit_colors(len(v4_orbits))
    node_colors = [palette[vertex_to_orbit[v]] for v in G60.nodes()]
    draw_graph(
        G60,
        g60_pos,
        FIGURES_DIR / "g60_v4_orbits.png",
        "G60 Colored by V4 Orbits",
        node_color=node_colors,
        node_size=95,
    )

    # Figure 3: quotient graph
    draw_graph(
        Q15,
        q15_pos,
        FIGURES_DIR / "q15_graph.png",
        "Q15 = G60 / V4",
        node_size=650,
        labels=True,
    )

    # Figure 4: line graph of Petersen
    lp_pos = nx.spring_layout(LP, seed=17, iterations=300)
    draw_graph(
        LP,
        lp_pos,
        FIGURES_DIR / "petersen_line_graph.png",
        "Line Graph of the Petersen Graph",
        node_size=650,
        labels=False,
    )

    print("\nSaved:")
    print("  figures/g60_graph.png")
    print("  figures/g60_v4_orbits.png")
    print("  figures/q15_graph.png")
    print("  figures/petersen_line_graph.png")


if __name__ == "__main__":
    main()
