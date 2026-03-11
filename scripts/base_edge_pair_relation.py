from __future__ import annotations

from collections import defaultdict, deque, Counter
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


def chamber_to_edge_sheet():
    """
    map chamber node -> (base_edge, sheet)
    """
    p2es = pair_to_edge_sheet()
    edges = sorted({e for e, _ in p2es.values()})
    edge_to_idx = {e: idx for idx, e in enumerate(edges)}

    out = {}
    for pair_id, (e, s) in p2es.items():
        node = 2 * edge_to_idx[e] + s
        out[node] = (e, s)

    return out


def base_edge_graph(edges):
    """
    adjacency graph on base edges
    """
    adj = {e: set() for e in edges}

    for a in edges:
        for b in edges:
            if a == b:
                continue
            if len(set(a) & set(b)) == 1:
                adj[a].add(b)

    return adj


def main():

    chamber_adj = measured_graph_reindexed()
    chamber_dist = all_distances(chamber_adj)
    meta = chamber_to_edge_sheet()

    # ---------------------------------------------------------
    # build relation graph for distance-5 (4,4)
    # ---------------------------------------------------------

    rel = defaultdict(set)

    for x in chamber_adj:
        for y in chamber_adj:
            if x >= y:
                continue
            if chamber_dist[x][y] == 5:

                counts = Counter(chamber_dist[x][z] for z in chamber_adj[y])
                prof = tuple(sorted((k, counts[k]) for k in counts))

                if prof == ((4, 4),):
                    rel[x].add(y)
                    rel[y].add(x)

    # ---------------------------------------------------------
    # collect 4-cycles
    # ---------------------------------------------------------

    visited = set()
    cycles = []

    for v in rel:
        if v in visited:
            continue

        stack = [v]
        comp = []

        while stack:
            x = stack.pop()
            if x in visited:
                continue
            visited.add(x)
            comp.append(x)
            stack.extend(rel[x])

        cycles.append(sorted(comp))

    print("=" * 80)
    print("4-CYCLE BASE EDGE PAIRS")
    print("=" * 80)

    edge_pairs = []

    for comp in cycles:
        edges = {meta[v][0] for v in comp}

        if len(edges) != 2:
            continue

        e, f = sorted(edges)
        edge_pairs.append((e, f))

        print(f"{e}  <->  {f}")

    print()
    print("total base-edge pairs:", len(edge_pairs))

    # ---------------------------------------------------------
    # build base-edge adjacency
    # ---------------------------------------------------------

    base_edges = sorted({e for e, _ in meta.values()})
    base_adj = base_edge_graph(base_edges)
    base_dist = all_distances(base_adj)

    print()
    print("=" * 80)
    print("DISTANCE BETWEEN MATCHED BASE EDGES")
    print("=" * 80)

    dist_counts = Counter()

    for e, f in edge_pairs:
        d = base_dist[e][f]
        dist_counts[d] += 1
        print(f"{e}  <->  {f}   distance={d}")

    print()
    print("distance histogram:", dict(sorted(dist_counts.items())))

    # ---------------------------------------------------------
    # check matching properties
    # ---------------------------------------------------------

    deg = Counter()

    for e, f in edge_pairs:
        deg[e] += 1
        deg[f] += 1

    print()
    print("=" * 80)
    print("MATCHING CHECK")
    print("=" * 80)

    print("edge participation counts:", dict(sorted(Counter(deg.values()).items())))
    print("unique edges covered:", len(deg))
    print("total base edges:", len(base_edges))

    if len(deg) == len(base_edges) and all(deg[e] == 1 for e in base_edges):
        print("Result: perfect matching on the 30 base edges.")
    else:
        print("Result: not a perfect matching.")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("If all pairs lie at the same distance in the base-edge graph,")
    print("this relation likely corresponds to a geometric opposition")
    print("relation in the icosahedral vertex figure.")


if __name__ == "__main__":
    main()
