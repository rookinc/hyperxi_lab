from __future__ import annotations

from collections import Counter, defaultdict
import numpy as np

from vertex_connection_model import measured_graph_reindexed
from reconstruct_vertex_connection import pair_to_edge_sheet


def adjacency_matrix(adj):
    nodes = sorted(adj)
    idx = {v: i for i, v in enumerate(nodes)}
    A = np.zeros((len(nodes), len(nodes)), dtype=int)
    for v in nodes:
        for w in adj[v]:
            A[idx[v], idx[w]] = 1
    return A, nodes


def build_base_graph():
    p2es = pair_to_edge_sheet()
    edges30 = sorted({e for e, _ in p2es.values()})
    edge_to_idx = {e: i for i, e in enumerate(edges30)}

    chamber_meta = {}
    for pair_id, (e, s) in p2es.items():
        node = 2 * edge_to_idx[e] + s
        chamber_meta[node] = (e, s)

    chamber_adj = measured_graph_reindexed()
    qadj = defaultdict(set)
    for u in chamber_adj:
        eu, _ = chamber_meta[u]
        for v in chamber_adj[u]:
            ev, _ = chamber_meta[v]
            if eu != ev:
                qadj[eu].add(ev)
                qadj[ev].add(eu)
    return {k: set(v) for k, v in qadj.items()}


def main():
    adj = build_base_graph()
    A, nodes = adjacency_matrix(adj)

    print("=" * 80)
    print("30-VERTEX BASE GRAPH WALK HASH")
    print("=" * 80)
    print(f"vertices: {len(nodes)}")
    print(f"edges: {sum(len(adj[v]) for v in adj) // 2}")
    print()

    M = np.eye(len(nodes), dtype=int)
    for k in range(1, 11):
        M = M @ A
        tr = int(np.trace(M))
        print(f"trace(A^{k}) = {tr}")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("This short closed-walk trace sequence is a strong identification")
    print("fingerprint for the 30-vertex base graph.")

if __name__ == "__main__":
    main()
