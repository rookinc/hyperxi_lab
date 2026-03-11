from __future__ import annotations

from pathlib import Path
import ast
import networkx as nx

DECAGON_FILE = Path("artifacts/cycles/ordered_decagon_pair_cycles.txt")


def load_decagons(path):
    out = []

    if not path.exists():
        print("ERROR: file not found:", path)
        return out

    for line in path.read_text().splitlines():
        line = line.strip()
        if not line.startswith("decagon"):
            continue

        try:
            payload = line.split(":", 1)[1].strip()
            obj = ast.literal_eval(payload)
            if isinstance(obj, list) and len(obj) == 10:
                out.append(tuple(int(x) for x in obj))
        except Exception:
            pass

    print("decagons loaded:", len(out))
    return out


def build_graph(decagons):
    G = nx.Graph()

    for cyc in decagons:
        n = len(cyc)
        for i in range(n):
            a = cyc[i]
            b = cyc[(i + 1) % n]
            G.add_edge(a, b)

    return G


def main():
    decagons = load_decagons(DECAGON_FILE)

    if not decagons:
        print("No decagons loaded. Check file format.")
        return

    G = build_graph(decagons)

    gm = nx.algorithms.isomorphism.GraphMatcher(G, G)
    count = sum(1 for _ in gm.isomorphisms_iter())

    print("=" * 80)
    print("CHAMBER GRAPH AUTOMORPHISM ORDER")
    print("=" * 80)
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("automorphism order:", count)


if __name__ == "__main__":
    main()
