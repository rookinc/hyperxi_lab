#!/usr/bin/env python3

from pathlib import Path
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

ROOT = Path(__file__).resolve().parents[1]
G6_PATH = ROOT / "artifacts/census/thalion_graph.g6"


def load_graph():
    g6 = G6_PATH.read_text().strip()
    G = nx.from_graph6_bytes(g6.encode())
    return nx.convert_node_labels_to_integers(G)


def find_triangles(G):
    tris = set()
    for u in G.nodes():
        for v in G.neighbors(u):
            for w in G.neighbors(v):
                if w != u and G.has_edge(w, u):
                    tri = tuple(sorted((u, v, w)))
                    tris.add(tri)
    return sorted(tris)


def orbit_partition(elements, autos, action):
    """Partition elements into automorphism orbits."""
    seen = set()
    orbits = []

    for e in elements:
        if e in seen:
            continue
        orbit = set()
        for a in autos:
            orbit.add(action(a, e))
        seen |= orbit
        orbits.append(sorted(orbit))

    return orbits


def main():
    G = load_graph()

    print("=" * 80)
    print("THALEAN ORBIT ANALYSIS")
    print("=" * 80)

    gm = GraphMatcher(G, G)
    autos = list(gm.isomorphisms_iter())

    print("automorphisms:", len(autos))
    print()

    vertices = list(G.nodes())
    edges = [tuple(sorted(e)) for e in G.edges()]
    triangles = find_triangles(G)

    v_orbits = orbit_partition(vertices, autos, lambda a, x: a[x])
    e_orbits = orbit_partition(edges, autos,
                               lambda a, e: tuple(sorted((a[e[0]], a[e[1]]))))
    t_orbits = orbit_partition(triangles, autos,
                               lambda a, t: tuple(sorted((a[t[0]], a[t[1]], a[t[2]]))))

    print("vertex orbits:", len(v_orbits))
    for i, o in enumerate(v_orbits):
        print("  orbit", i, "size", len(o))

    print()

    print("edge orbits:", len(e_orbits))
    for i, o in enumerate(e_orbits):
        print("  orbit", i, "size", len(o))

    print()

    print("triangle orbits:", len(t_orbits))
    for i, o in enumerate(t_orbits):
        print("  orbit", i, "size", len(o))


if __name__ == "__main__":
    main()
