from __future__ import annotations

from pathlib import Path
from collections import Counter
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

def shell_profile(G: nx.Graph, v) -> tuple[int, ...]:
    d = nx.single_source_shortest_path_length(G, v)
    counts = Counter(d.values())
    return tuple(counts[i] for i in range(max(counts) + 1))

def summarize(G: nx.Graph, name: str) -> None:
    print("\n" + "=" * 80)
    print(name)
    print("=" * 80)
    print(f"|V| = {G.number_of_nodes()}")
    print(f"|E| = {G.number_of_edges()}")
    degs = sorted(set(dict(G.degree()).values()))
    print(f"degree set = {degs}")
    print(f"connected = {nx.is_connected(G)}")

    if nx.is_connected(G):
        print(f"diameter = {nx.diameter(G)}")
        print(f"radius   = {nx.radius(G)}")

    tri = sum(nx.triangles(G).values()) // 3
    print(f"triangles = {tri}")

    # shell profiles
    profiles = Counter(shell_profile(G, v) for v in G.nodes())
    print(f"distinct shell profiles = {len(profiles)}")
    for prof, mult in profiles.most_common(10):
        print(f"  {prof}  x{mult}")

    # spectrum
    A = nx.to_numpy_array(G, dtype=float)
    eigs = sorted(round(x.real, 12) for x in nx.linalg.spectrum.adjacency_spectrum(G))
    mults = Counter(eigs)
    print("spectrum:")
    for lam in sorted(mults):
        print(f"  {lam: .12f}  x{mults[lam]}")

def compare_basic(G: nx.Graph, H: nx.Graph, name: str) -> None:
    print("\n" + "-" * 80)
    print(f"compare with {name}")
    print("-" * 80)
    print(f"same order: {G.number_of_nodes() == H.number_of_nodes()}")
    print(f"same size : {G.number_of_edges() == H.number_of_edges()}")
    print(f"isomorphic: {nx.is_isomorphic(G, H) if G.number_of_nodes()==H.number_of_nodes() else False}")

def main():
    G = load_graph()
    summarize(G, "THALEAN")

    des = nx.desargues_graph()     # 20 vertices
    pet = nx.petersen_graph()      # 10 vertices

    summarize(des, "DESARGUES")
    summarize(pet, "PETERSEN")

    compare_basic(G, des, "Desargues")
    compare_basic(G, pet, "Petersen")

    print("\n" + "=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    if G.number_of_nodes() != des.number_of_nodes():
        print("Thalean is not literally the Desargues graph.")
    if G.number_of_nodes() == 60 and G.number_of_edges() == 90:
        print("Thalean is a 60-vertex cubic graph.")
        print("So the better question is whether it has Petersen/Desargues-family quotients or coverings.")
    print("If you want the next step, check:")
    print("  1. bipartite?")
    print("  2. girth?")
    print("  3. distance-regularity?")
    print("  4. canonical quotients to Petersen-family graphs?")

if __name__ == "__main__":
    main()
