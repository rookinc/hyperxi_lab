from __future__ import annotations

from collections import Counter, defaultdict, deque
from typing import Dict, Set, Tuple

from vertex_connection_model import measured_graph_reindexed
from reconstruct_vertex_connection import pair_to_edge_sheet


def bfs_distances(adj: Dict[int, Set[int]], s: int) -> Dict[int, int]:
    dist = {s: 0}
    q = deque([s])
    while q:
        v = q.popleft()
        for w in adj[v]:
            if w not in dist:
                dist[w] = dist[v] + 1
                q.append(w)
    return dist


def all_distances(adj: Dict[int, Set[int]]) -> Dict[int, Dict[int, int]]:
    return {v: bfs_distances(adj, v) for v in adj}


def pair_profile(adj: Dict[int, Set[int]], dist: Dict[int, Dict[int, int]], x: int, y: int):
    i = dist[x][y]
    counts = Counter()
    for z in adj[y]:
        counts[dist[x][z]] += 1
    prof = tuple((k, counts[k]) for k in sorted(counts))
    return i, prof


def fiber_meta():
    """
    node -> (base_edge, sheet)
    in the reindexed 60-state model
    """
    p2es = pair_to_edge_sheet()
    edges = sorted({e for e, _ in p2es.values()})
    edge_to_idx = {e: idx for idx, e in enumerate(edges)}

    out = {}
    for pair_id, (e, s) in p2es.items():
        node = 2 * edge_to_idx[e] + s
        out[node] = (e, s)
    return out


def components_of_relation(vertices: Set[int], rel_adj: Dict[int, Set[int]]):
    seen = set()
    comps = []
    for v in sorted(vertices):
        if v in seen:
            continue
        stack = [v]
        comp = []
        seen.add(v)
        while stack:
            x = stack.pop()
            comp.append(x)
            for y in rel_adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        comps.append(sorted(comp))
    return comps


def order_cycle(comp, rel_adj):
    """
    Since the relation graph should be 2-regular on each component,
    return the cyclic ordering of the component.
    """
    if len(comp) == 1:
        return comp[:]
    start = comp[0]
    n1 = sorted(rel_adj[start])
    prev = None
    cur = start
    out = []

    while True:
        out.append(cur)
        nbrs = sorted(rel_adj[cur])
        if prev is None:
            nxt = nbrs[0]
        else:
            nxt = nbrs[0] if nbrs[1] == prev else nbrs[1]

        prev, cur = cur, nxt
        if cur == start:
            break

        if len(out) > len(comp) + 2:
            raise RuntimeError("Cycle ordering failed: exceeded component size.")

    return out


def main():
    adj = measured_graph_reindexed()
    dist = all_distances(adj)
    meta = fiber_meta()

    rel_adj = defaultdict(set)

    for x in sorted(adj):
        for y in sorted(adj):
            if x >= y:
                continue
            d, prof = pair_profile(adj, dist, x, y)
            if d == 5 and prof == ((4, 4),):
                rel_adj[x].add(y)
                rel_adj[y].add(x)

    verts = set(rel_adj.keys())

    print("=" * 80)
    print("DISTANCE-5 (4,4) RELATION CYCLE DECOMPOSITION")
    print("=" * 80)
    print(f"vertices in relation: {len(verts)}")
    print(f"relation edges: {sum(len(v) for v in rel_adj.values()) // 2}")
    print()

    deg_counts = Counter(len(rel_adj[v]) for v in rel_adj)
    print("degree profile in relation graph")
    print("-" * 80)
    print(dict(sorted(deg_counts.items())))
    print()

    comps = components_of_relation(verts, rel_adj)
    lengths = Counter(len(c) for c in comps)

    print("component size counts")
    print("-" * 80)
    print(dict(sorted(lengths.items())))
    print()

    print("ordered components")
    print("-" * 80)
    for i, comp in enumerate(comps):
        cyc = order_cycle(comp, rel_adj)

        print(f"component {i}: size={len(comp)}")
        print(f"  cycle nodes: {cyc}")

        same_sheet_edges = 0
        diff_sheet_edges = 0
        share_vertex_edges = 0
        same_base_edges = 0

        annotated = []
        for v in cyc:
            e, s = meta[v]
            annotated.append((v, e, s))

        print("  annotated cycle:")
        for item in annotated:
            print(f"    node={item[0]:2d} edge={item[1]} sheet={item[2]}")

        for j in range(len(cyc)):
            a = cyc[j]
            b = cyc[(j + 1) % len(cyc)]
            ea, sa = meta[a]
            eb, sb = meta[b]

            if sa == sb:
                same_sheet_edges += 1
            else:
                diff_sheet_edges += 1

            if ea == eb:
                same_base_edges += 1
            elif len(set(ea) & set(eb)) == 1:
                share_vertex_edges += 1

        print(f"  consecutive relation edges with same sheet: {same_sheet_edges}")
        print(f"  consecutive relation edges with different sheet: {diff_sheet_edges}")
        print(f"  consecutive relation edges sharing a base vertex: {share_vertex_edges}")
        print(f"  consecutive relation edges on same base edge: {same_base_edges}")
        print()

    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("If the (4,4) relation decomposes into uniform cycles, then the special")
    print("distance-5 class is not a simple involution but a higher-order long-range")
    print("transport relation. The cycle lengths and edge/sheet patterns indicate")
    print("how the hidden binary fiber is mixed with residual geometric symmetry.")


if __name__ == "__main__":
    main()
