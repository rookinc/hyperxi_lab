#!/usr/bin/env python3

from pathlib import Path
import json
import networkx as nx

EDGE_PATH = Path("artifacts/reports/flag_compare/candidate_c_flag_graph.edgelist")
LABELS_PATH = Path("artifacts/reports/flag_compare/candidate_c_flag_graph_labels.json")
OUT_G6 = Path("artifacts/census/thalion_graph.g6")
OUT_JSON = Path("spec/thalion_graph.v1.json")

def shell_counts(G, root=0):
    dist = nx.single_source_shortest_path_length(G, root)
    maxd = max(dist.values())
    return [sum(1 for d in dist.values() if d == i) for i in range(maxd + 1)]

def main():
    if not EDGE_PATH.exists():
        raise FileNotFoundError(f"Missing edge list: {EDGE_PATH}")

    G = nx.read_edgelist(EDGE_PATH, nodetype=int)
    G = nx.Graph(G)

    OUT_G6.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    g6 = nx.to_graph6_bytes(G, header=False)
    OUT_G6.write_bytes(g6)

    spec = {
        "name": "Thalean Graph",
        "version": "1.1",
        "canonical_encoding": {
            "format": "graph6",
            "graph6": g6.decode().strip()
        },
        "graph_invariants": {
            "vertices": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "degree": sorted(set(dict(G.degree()).values()))[0],
            "diameter": nx.diameter(G),
            "triangles": sum(nx.triangles(G).values()) // 3,
            "shells": shell_counts(G, 0)
        },
        "identifiers": {
            "graphsym": "AT4val[60,6]",
            "house_of_graphs": "Graph52002"
        },
        "provenance": {
            "derived_from": "flag quotient candidate C",
            "edge_list": str(EDGE_PATH),
            "label_map": str(LABELS_PATH)
        }
    }

    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)

    print("Wrote:")
    print(" ", OUT_G6)
    print(" ", OUT_JSON)
    print()
    print("graph6:")
    print(g6.decode().strip())

if __name__ == "__main__":
    main()
