from __future__ import annotations

from pathlib import Path

from chamber_graph_aut_order import load_decagons, build_graph, DECAGON_FILE
import networkx as nx


def automorphisms(G: nx.Graph):
    gm = nx.algorithms.isomorphism.GraphMatcher(G, G)
    return list(gm.isomorphisms_iter())


def main():
    decagons = load_decagons(DECAGON_FILE)
    if not decagons:
        print("No decagons loaded. Check file format.")
        return

    G = build_graph(decagons)
    autos = automorphisms(G)

    arcs = []
    for u in sorted(G.nodes()):
        for v in sorted(G.neighbors(u)):
            arcs.append((u, v))

    seen = set()
    orbits = []

    for a in arcs:
        if a in seen:
            continue

        orb = set()
        u, v = a
        for perm in autos:
            orb.add((perm[u], perm[v]))

        seen.update(orb)
        orbits.append(sorted(orb))

    print("=" * 80)
    print("CHAMBER GRAPH ARC ORBITS")
    print("=" * 80)
    print(f"vertices: {G.number_of_nodes()}")
    print(f"edges: {G.number_of_edges()}")
    print(f"automorphisms found: {len(autos)}")
    print(f"number of arc orbits: {len(orbits)}")
    print(f"orbit sizes: {[len(o) for o in orbits]}")
    for i, orb in enumerate(orbits[:4]):
        print(f"orbit {i:2d}: first few={orb[:12]}")


if __name__ == "__main__":
    main()
