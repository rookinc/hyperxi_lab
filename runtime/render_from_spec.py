import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx


SPEC_PATH = Path("specs/thalean_graph_spec.json")
OUT_PATH = Path("artifacts/thalean_from_spec_circular.png")


def load_spec(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def extract_edges(spec: dict):
    # Preferred location
    if "graph" in spec and isinstance(spec["graph"], dict) and "edges" in spec["graph"]:
        return spec["graph"]["edges"]

    # Fallback locations
    if "edges" in spec:
        return spec["edges"]

    raise KeyError(
        "No edge list found in JSON spec. Add graph.edges = [[u,v], ...] to the spec."
    )


def extract_vertex_count(spec: dict, edges):
    if "graph" in spec and isinstance(spec["graph"], dict) and "vertices" in spec["graph"]:
        return int(spec["graph"]["vertices"])

    max_v = max(max(int(u), int(v)) for u, v in edges)
    return max_v + 1


def circular_positions(n: int, radius: float = 1.0):
    return {
        i: (
            radius * math.cos(2.0 * math.pi * i / n),
            radius * math.sin(2.0 * math.pi * i / n),
        )
        for i in range(n)
    }


def build_graph(n: int, edges):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for u, v in edges:
        G.add_edge(int(u), int(v))
    return G


def main():
    spec = load_spec(SPEC_PATH)
    edges = extract_edges(spec)
    n = extract_vertex_count(spec, edges)

    G = build_graph(n, edges)
    pos = circular_positions(n)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 10))
    nx.draw_networkx_edges(G, pos, width=0.5)
    nx.draw_networkx_nodes(G, pos, node_size=14)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=300, bbox_inches="tight")
    print(f"saved {OUT_PATH}")


if __name__ == "__main__":
    main()
