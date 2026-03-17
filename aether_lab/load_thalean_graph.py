"""
Minimal loader shim for Thalean graph.
Bridges legacy scripts to artifact-based workflow.
"""

import networkx as nx
from pathlib import Path


ARTIFACT_PATHS = [
    "artifacts/census/thalean_graph.g6",
    "../hyperxi_lab/artifacts/census/thalean_graph.g6",
]


def _find_g6():
    for p in ARTIFACT_PATHS:
        path = Path(p)
        if path.exists():
            return path
    raise FileNotFoundError("Could not locate thalean_graph.g6")


def load_spec():
    """
    Placeholder for compatibility.
    """
    return {
        "graph_id": "AT4val[60,6]",
        "source": "HouseOfGraphs Graph52002"
    }


def build_graph():
    """
    Load the canonical Thalean graph from .g6
    """
    path = _find_g6()

    with open(path, "rb") as f:
        G = nx.from_graph6_bytes(f.read().strip())

    return G
