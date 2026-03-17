import networkx as nx
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
AETHER_LAB = BASE_DIR.parent

def _find_g6():
    candidates = [
        AETHER_LAB / "data/graphs/thalean_graph.g6",
        AETHER_LAB / "artifacts/census/thalean_graph.g6"
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(f"Could not locate thalean_graph.g6 in {candidates}")

def load_spec():
    return {
        "graph_id": "AT4val[60,6]",
        "source": "HouseOfGraphs Graph52002"
    }

def build_graph(spec=None):
    path = _find_g6()
    with open(path, "rb") as f:
        return nx.from_graph6_bytes(f.read().strip())
