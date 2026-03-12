#!/usr/bin/env python3

from pathlib import Path
import numpy as np
import networkx as nx
import argparse

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "artifacts/census/thalion_graph.g6"


def load_graph():
    data = GRAPH_PATH.read_text().strip()
    return nx.from_graph6_bytes(data.encode())


def laplacian(g):
    A = nx.to_numpy_array(g)
    return 4*np.eye(len(A)) - A


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=int, default=20)
    args = parser.parse_args()

    g = load_graph()

    L = laplacian(g)

    vals, vecs = np.linalg.eigh(L)

    mode = args.mode
    vec = vecs[:,mode]

    # normalize
    vec = vec / np.max(np.abs(vec))

    # pick vertex with largest amplitude
    seed = int(np.argmax(np.abs(vec)))

    dist = nx.single_source_shortest_path_length(g, seed)

    ordered = sorted(dist.keys(), key=lambda x:(dist[x], vec[x]))

    print("="*70)
    print("THALEAN MODE STRUCTURE")
    print("="*70)

    print("mode index:",mode)
    print("eigenvalue :",vals[mode])
    print("seed vertex:",seed)
    print()

    current_shell = -1

    for v in ordered:

        shell = dist[v]

        if shell != current_shell:
            current_shell = shell
            print()
            print("shell",shell)
            print("-"*40)

        print(f"{v:02d}  amp={vec[v]:+.6f}")

    print()


if __name__ == "__main__":
    main()
