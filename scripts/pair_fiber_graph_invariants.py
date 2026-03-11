from __future__ import annotations

import ast
import re
from collections import Counter, defaultdict

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
            nums = [int(x) for x in arr]
            if len(nums) != 10:
                raise ValueError(f"Expected 10 entries, got {len(nums)}")
            cycles.append(nums)

    return cycles


def build_adj(cycles):
    adj = defaultdict(set)
    for cyc in cycles:
        n = len(cyc)
        for i in range(n):
            a = cyc[i]
            b = cyc[(i + 1) % n]
            adj[a].add(b)
            adj[b].add(a)
    return {k: set(v) for k, v in adj.items()}


def adjacency_matrix(adj):
    nodes = sorted(adj)
    idx = {v: i for i, v in enumerate(nodes)}
    A = np.zeros((len(nodes), len(nodes)), dtype=int)
    for v in nodes:
        for w in adj[v]:
            A[idx[v], idx[w]] = 1
    return A, nodes


def eigen_mults(A):
    vals = np.linalg.eigvals(A)
    vals = [round(float(np.real_if_close(v)), 6) for v in vals]
    return Counter(vals)


def common_neighbor_profile(adj):
    nodes = sorted(adj)
    prof_adj = Counter()
    prof_non = Counter()

    for i, u in enumerate(nodes):
        for v in nodes[i + 1:]:
            c = len(adj[u] & adj[v])
            if v in adj[u]:
                prof_adj[c] += 1
            else:
                prof_non[c] += 1

    return prof_adj, prof_non


def triangle_count(adj):
    nodes = sorted(adj)
    count = 0
    for i, a in enumerate(nodes):
        for b in [x for x in adj[a] if x > a]:
            for c in [x for x in adj[a] & adj[b] if x > b]:
                count += 1
    return count


def main():
    cycles = load_cycles("ordered_decagon_pair_cycles.txt")
    adj = build_adj(cycles)
    A, nodes = adjacency_matrix(adj)

    print("=" * 80)
    print("PAIR FIBER GRAPH INVARIANTS")
    print("=" * 80)
    print(f"vertices: {len(nodes)}")
    print(f"edges: {sum(len(v) for v in adj.values()) // 2}")
    print(f"degree set: {sorted({len(v) for v in adj.values()})}")
    print(f"triangles: {triangle_count(adj)}")

    print()
    print("Eigenvalue multiplicities")
    print("-" * 80)
    mults = eigen_mults(A)
    for val in sorted(mults):
        print(f"{val:>10}: {mults[val]}")

    print()
    print("Common-neighbor profile for adjacent pairs")
    print("-" * 80)
    prof_adj, prof_non = common_neighbor_profile(adj)
    for k in sorted(prof_adj):
        print(f"{k} common neighbors: {prof_adj[k]}")

    print()
    print("Common-neighbor profile for nonadjacent pairs")
    print("-" * 80)
    for k in sorted(prof_non):
        print(f"{k} common neighbors: {prof_non[k]}")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("These invariants help identify the 60-vertex 4-regular graph induced")
    print("on the S-pair fiber by ordered Petrie adjacency.")
    print("They can distinguish between a generic 4-regular graph, a strongly")
    print("regular graph, a line-graph type object, or a twisted lift of the")
    print("icosahedral edge geometry.")


if __name__ == "__main__":
    main()
