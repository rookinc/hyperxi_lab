#!/usr/bin/env python3

"""
build_thalean_templates.py

Compute the eigenmodes of the Thalean chamber graph and export
them as a template library.

Each template represents a resonant harmonic of the graph.
"""

from pathlib import Path
import json
import numpy as np
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]

GRAPH_PATH = ROOT / "artifacts/census/thalion_graph.g6"
OUT_PATH = ROOT / "spec/thalean_templates.v1.json"


def load_graph():
    return nx.from_graph6_bytes(GRAPH_PATH.read_bytes())


def build_laplacian(g):

    A = nx.to_numpy_array(g, dtype=float)

    deg = 4

    L = deg * np.eye(len(A)) - A

    return L


def compute_templates():

    g = load_graph()

    L = build_laplacian(g)

    eigvals, eigvecs = np.linalg.eigh(L)

    templates = []

    for i,(lam,vec) in enumerate(zip(eigvals, eigvecs.T)):

        vec = vec / np.linalg.norm(vec)

        templates.append({

            "mode_index": int(i),

            "eigenvalue": float(lam),

            "frequency_parameter": float(lam),

            "vector": vec.tolist()

        })

    return templates


def main():

    templates = compute_templates()

    out = {

        "name": "Thalean Harmonic Template Library",

        "graph": "thalion_graph",

        "nodes": 60,

        "degree": 4,

        "template_count": len(templates),

        "templates": templates

    }

    OUT_PATH.write_text(json.dumps(out, indent=2))

    print("templates written to", OUT_PATH)


if __name__ == "__main__":
    main()

