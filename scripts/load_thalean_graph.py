#!/usr/bin/env python3

"""
Load the canonical Thalean graph from the JSON spec and verify invariants.
"""

import json
from pathlib import Path

import networkx as nx


SPEC_PATH = Path("spec/thalion_graph.v1.json")


def load_spec():
    if not SPEC_PATH.exists():
        raise FileNotFoundError(f"Spec not found: {SPEC_PATH}")
    return json.loads(SPEC_PATH.read_text())


def build_graph(spec):
    g6 = spec["canonical_encoding"]["graph6"]
    G = nx.from_graph6_bytes(g6.encode())
    return G


def verify_invariants(G, spec):
    inv = spec["graph_invariants"]

    print("===================================================")
    print("THALEAN GRAPH LOAD REPORT")
    print("===================================================")

    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())

    degree_set = sorted(set(dict(G.degree()).values()))
    print("degree set:", degree_set)

    print()

    assert G.number_of_nodes() == inv["vertices"], "vertex count mismatch"
    assert G.number_of_edges() == inv["edges"], "edge count mismatch"
    assert degree_set == [inv["degree"]], "degree mismatch"

    print("Invariant checks: OK")


def main():
    spec = load_spec()
    G = build_graph(spec)
    verify_invariants(G, spec)


if __name__ == "__main__":
    main()

