#!/usr/bin/env python3
from __future__ import annotations

from hyperxi.combinatorics.chamber_graph import build_chamber_graph


def main():
    G = build_chamber_graph()

    print("=" * 80)
    print("RAW build_chamber_graph() OBJECT")
    print("=" * 80)
    print("type:", type(G))
    print("dir has vertices:", hasattr(G, "vertices"))
    print("dir has edges:", hasattr(G, "edges"))
    print("dir has adjacency:", hasattr(G, "adjacency"))
    print()

    if hasattr(G, "vertices"):
        print("len(vertices):", len(G.vertices))
        print("first 10 vertices:", list(G.vertices)[:10])
        print()

    if hasattr(G, "edges"):
        print("len(edges):", len(G.edges))
        print("first 10 edges:", list(G.edges)[:10])
        print()

    if hasattr(G, "adjacency"):
        try:
            keys = list(G.adjacency.keys())
            print("adjacency vertex count:", len(keys))
            print("first 5 adjacency rows:")
            for k in keys[:5]:
                print(k, "->", G.adjacency[k])
        except Exception as e:
            print("could not inspect adjacency:", e)


if __name__ == "__main__":
    main()
