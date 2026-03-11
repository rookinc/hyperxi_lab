from __future__ import annotations

import ast
import re
from collections import defaultdict

import numpy as np


def load_cycles(path: str):
    cycles = []

    pattern = re.compile(r"^decagon\s+\d+:\s*(\[.*\])\s*$")

    with open(path) as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue

            m = pattern.match(line)
            if not m:
                continue

            arr = ast.literal_eval(m.group(1))
            if not isinstance(arr, list):
                continue
            if len(arr) != 10:
                raise ValueError(f"Expected 10 entries, got {len(arr)} in line: {line}")

            nums = [int(x) for x in arr]
            cycles.append(nums)

    return cycles


def build_pair_graph(cycles):
    adj = defaultdict(set)

    for cyc in cycles:
        n = len(cyc)
        for i in range(n):
            a = cyc[i]
            b = cyc[(i + 1) % n]
            adj[a].add(b)
            adj[b].add(a)

    return adj


def adjacency_matrix(adj):
    nodes = sorted(adj.keys())
    index = {v: i for i, v in enumerate(nodes)}

    A = np.zeros((len(nodes), len(nodes)), dtype=int)

    for v in nodes:
        for w in adj[v]:
            A[index[v], index[w]] = 1

    return A, nodes


def connected_components(adj):
    seen = set()
    comps = []

    for start in sorted(adj):
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        comp = []

        while stack:
            u = stack.pop()
            comp.append(u)
            for v in sorted(adj[u]):
                if v not in seen:
                    seen.add(v)
                    stack.append(v)

        comps.append(sorted(comp))

    return comps


def spectrum(A):
    vals = np.linalg.eigvals(A)
    vals = np.sort(np.real_if_close(vals))
    return vals


def main():
    print("=" * 80)
    print("PAIR FIBER TRANSPORT OPERATOR")
    print("=" * 80)

    cycles = load_cycles("ordered_decagon_pair_cycles.txt")
    print("decagon cycles:", len(cycles))

    if len(cycles) != 12:
        raise RuntimeError(f"Expected 12 decagon cycles, found {len(cycles)}")

    flat = sorted(set(x for cyc in cycles for x in cyc))
    print("distinct S-pair ids seen:", len(flat))
    if len(flat) != 60:
        raise RuntimeError(f"Expected 60 distinct S-pairs, found {len(flat)}")

    adj = build_pair_graph(cycles)

    print("S-pair states:", len(adj))

    degrees = sorted(len(v) for v in adj.values())
    print("min degree:", min(degrees))
    print("max degree:", max(degrees))
    print("degree distribution:", sorted(set(degrees)))

    comps = connected_components(adj)
    print("connected components:", len(comps))
    print("component sizes:", [len(c) for c in comps])

    A, nodes = adjacency_matrix(adj)

    print()
    print("operator size:", A.shape)
    print("undirected edges:", int(A.sum() // 2))

    vals = spectrum(A)

    print()
    print("first 10 eigenvalues")
    print("-" * 80)
    for v in vals[:10]:
        print(f"{v:.6f}")

    print()
    print("last 10 eigenvalues")
    print("-" * 80)
    for v in vals[-10:]:
        print(f"{v:.6f}")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("This operator encodes adjacency between S-pairs along ordered")
    print("SV Petrie decagon cycles. Because each S-pair lies on two decagons,")
    print("the induced pair graph measures transport on the twisted binary")
    print("edge-fiber structure over the icosahedral decagon graph.")


if __name__ == "__main__":
    main()
