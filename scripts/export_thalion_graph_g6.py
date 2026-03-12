from __future__ import annotations

from pathlib import Path
import networkx as nx

from chamber_graph_aut_order import load_decagons, build_graph, DECAGON_FILE


def main() -> None:
    decagons = load_decagons(DECAGON_FILE)
    if not decagons:
        raise SystemExit("No decagons loaded.")

    G = build_graph(decagons)

    outdir = Path("artifacts/census")
    outdir.mkdir(parents=True, exist_ok=True)

    g6 = nx.to_graph6_bytes(G, header=False).decode().strip()
    (outdir / "thalion_graph.g6").write_text(g6 + "\n", encoding="utf-8")

    print("wrote artifacts/census/thalion_graph.g6")
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("graph6:", g6)


if __name__ == "__main__":
    main()
