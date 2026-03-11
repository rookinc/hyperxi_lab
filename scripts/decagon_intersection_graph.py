from __future__ import annotations

from pathlib import Path
import ast
from collections import Counter, defaultdict
import networkx as nx

DECAGON_FILE = Path("artifacts/cycles/ordered_decagon_pair_cycles.txt")


def load_decagons(path: Path) -> list[tuple[int, ...]]:
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line.startswith("decagon") or ":" not in line:
            continue
        payload = line.split(":", 1)[1].strip()
        obj = ast.literal_eval(payload)
        if isinstance(obj, list) and len(obj) == 10:
            out.append(tuple(int(x) for x in obj))
    return out


def build_intersection_graph(decagons: list[tuple[int, ...]]):
    G = nx.Graph()
    for i in range(len(decagons)):
        G.add_node(i)

    shared_map: dict[tuple[int, int], list[int]] = {}
    for i in range(len(decagons)):
        si = set(decagons[i])
        for j in range(i + 1, len(decagons)):
            inter = sorted(si & set(decagons[j]))
            if inter:
                G.add_edge(i, j, weight=len(inter))
                shared_map[(i, j)] = inter
    return G, shared_map


def main() -> None:
    decagons = load_decagons(DECAGON_FILE)

    print("=" * 80)
    print("DECAGON INTERSECTION GRAPH")
    print("=" * 80)
    print("decagons loaded:", len(decagons))

    if len(decagons) != 12:
        print("WARNING: expected 12 decagons")

    G, shared_map = build_intersection_graph(decagons)

    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree sequence:", sorted(dict(G.degree()).values()))
    print("degree set:", sorted(set(dict(G.degree()).values())))

    print()
    print("PAIR INTERSECTION SIZES")
    print("-" * 80)
    hist = Counter(len(v) for v in shared_map.values())
    for k in sorted(hist):
        print(f"shared {k} states: {hist[k]} pairs")

    print()
    print("INTERSECTING PAIRS")
    print("-" * 80)
    for (i, j), inter in sorted(shared_map.items()):
        print(f"decagons ({i:2d}, {j:2d}) share {len(inter)} states: {inter}")

    print()
    print("CONNECTED:", nx.is_connected(G))
    print("TRIANGLES:", sum(nx.triangles(G).values()) // 3)
    print("SPECTRUM:")
    vals = sorted(round(float(x), 6) for x in nx.adjacency_spectrum(G).real)
    print(vals)

    print()
    print("COMPARE WITH ICOSAHEDRAL GRAPH")
    print("-" * 80)
    I = nx.icosahedral_graph()
    print("icosahedron vertices:", I.number_of_nodes())
    print("icosahedron edges:", I.number_of_edges())
    print("icosahedron degree sequence:", sorted(dict(I.degree()).values()))

    same_basic = (
        G.number_of_nodes() == I.number_of_nodes()
        and G.number_of_edges() == I.number_of_edges()
        and sorted(dict(G.degree()).values()) == sorted(dict(I.degree()).values())
    )
    print("same basic parameters:", same_basic)

    if same_basic:
        gm = nx.algorithms.isomorphism.GraphMatcher(G, I)
        iso = gm.is_isomorphic()
        print("isomorphic to icosahedral graph:", iso)
    else:
        print("isomorphic to icosahedral graph: skipped")

if __name__ == "__main__":
    main()
