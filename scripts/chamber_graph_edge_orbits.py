from __future__ import annotations

from pathlib import Path
import ast
import networkx as nx

DECAGON_FILE = Path("artifacts/cycles/ordered_decagon_pair_cycles.txt")


def load_decagons(path):
    out = []

    for line in path.read_text().splitlines():
        line = line.strip()

        if not line.startswith("decagon"):
            continue

        if ":" not in line:
            continue

        payload = line.split(":", 1)[1].strip()

        try:
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
        for i in range(len(cyc)):
            a = cyc[i]
            b = cyc[(i + 1) % len(cyc)]
            G.add_edge(a, b)

    return G


def canon_edge(a, b):
    return (a, b) if a < b else (b, a)


def main():
    decagons = load_decagons(DECAGON_FILE)

    if not decagons:
        print("No decagons loaded.")
        return

    G = build_graph(decagons)

    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())

    gm = nx.algorithms.isomorphism.GraphMatcher(G, G)
    autos = list(gm.isomorphisms_iter())

    print("automorphisms found:", len(autos))

    edges = sorted(canon_edge(a, b) for a, b in G.edges())

    seen = set()
    orbits = []

    for e in edges:
        if e in seen:
            continue

        a, b = e
        orb = set()

        for perm in autos:
            x, y = perm[a], perm[b]
            orb.add(canon_edge(x, y))

        seen.update(orb)
        orbits.append(sorted(orb))

    print("=" * 80)
    print("CHAMBER GRAPH EDGE ORBITS")
    print("=" * 80)
    print("number of edge orbits:", len(orbits))
    print("orbit sizes:", [len(o) for o in orbits])


if __name__ == "__main__":
    main()
