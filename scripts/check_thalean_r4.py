from __future__ import annotations

from itertools import combinations
from pathlib import Path
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = [
    ROOT / "reports" / "true_quotients" / "true_chamber_graph.g6",
    ROOT / "artifacts" / "census" / "thalean_graph.g6",
]

def load_graph() -> nx.Graph:
    for path in CANDIDATES:
        if path.exists():
            print(f"loading: {path}")
            return nx.read_graph6(path)
    raise FileNotFoundError("Could not find Thalean graph .g6")

def count_4cycles(G: nx.Graph):
    seen = set()
    for u, v in combinations(G.nodes(), 2):
        common = sorted(set(G.neighbors(u)) & set(G.neighbors(v)))
        if len(common) >= 2:
            for a, b in combinations(common, 2):
                cyc = tuple(sorted((u, a, v, b)))
                seen.add(cyc)
    return sorted(seen)

def girth(G: nx.Graph):
    best = None
    for s in G.nodes():
        dist = {s: 0}
        parent = {s: None}
        queue = [s]
        for u in queue:
            for v in G.neighbors(u):
                if v not in dist:
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    queue.append(v)
                elif parent[u] != v:
                    cyc = dist[u] + dist[v] + 1
                    if best is None or cyc < best:
                        best = cyc
    return best

def main():
    G = load_graph()
    print(f"|V|={G.number_of_nodes()} |E|={G.number_of_edges()}")
    print(f"bipartite = {nx.is_bipartite(G)}")
    g = girth(G)
    print(f"girth = {g}")

    c4 = count_4cycles(G)
    print(f"number of 4-cycles = {len(c4)}")

    if c4:
        print("\nfirst few 4-cycles (as 4-vertex sets):")
        for cyc in c4[:20]:
            print(" ", cyc)
    else:
        print("\nNo 4-cycles found.")

if __name__ == "__main__":
    main()
