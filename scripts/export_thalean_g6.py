#!/usr/bin/env python3

import sys
from pathlib import Path
import networkx as nx

# allow importing from scripts directory
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from load_thalean_graph import load_spec, build_graph

OUT = Path("artifacts/census/thalion_graph.g6")

def main():

    spec = load_spec()
    G = build_graph(spec)

    OUT.parent.mkdir(parents=True, exist_ok=True)

    g6 = nx.to_graph6_bytes(G, header=False)
    OUT.write_bytes(g6)

    print("Exported canonical graph to:")
    print(OUT)

    print()
    print("graph6 string:")
    print(g6.decode().strip())

if __name__ == "__main__":
    main()
