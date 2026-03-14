#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def load_payload(path):
    payload = json.loads(Path(path).read_text())
    sigs = payload["signatures"]
    P = np.array(payload["transition_matrix"], dtype=float)
    return sigs, P


def strongest_edge(row, i):
    r = row.copy()
    r[i] = -1
    j = int(np.argmax(r))
    return j, r[j]


def build_graph(P):
    edges = {}
    for i in range(len(P)):
        j, w = strongest_edge(P[i], i)
        if w > 0:
            edges[i] = j
    return edges


def find_cycles(edges):
    visited = set()
    cycles = []

    for start in edges:
        if start in visited:
            continue

        path = []
        cur = start

        while cur not in path and cur in edges:
            path.append(cur)
            cur = edges[cur]

        if cur in path:
            k = path.index(cur)
            cycles.append(path[k:])

        visited.update(path)

    return cycles


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    args = ap.parse_args()

    sigs, P = load_payload(args.input)

    edges = build_graph(P)
    cycles = find_cycles(edges)

    print("="*80)
    print("SIGNATURE CYCLES")
    print("="*80)
    print()

    for cyc in cycles:
        names = [sigs[i] for i in cyc]
        print(" -> ".join(names))

    print()

if __name__ == "__main__":
    main()
