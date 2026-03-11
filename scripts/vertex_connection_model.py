from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple

import numpy as np

BASE_ADJ: Dict[int, List[int]] = {
    0: [1, 4, 5, 6, 11],
    1: [0, 5, 6, 7, 10],
    2: [3, 6, 7, 9, 11],
    3: [2, 7, 8, 9, 10],
    4: [0, 5, 8, 9, 11],
    5: [0, 1, 4, 8, 10],
    6: [0, 1, 2, 7, 11],
    7: [1, 2, 3, 6, 10],
    8: [3, 4, 5, 9, 10],
    9: [2, 3, 4, 8, 11],
    10: [1, 3, 5, 7, 8],
    11: [0, 2, 4, 6, 9],
}

EDGE_FIBERS: Dict[Tuple[int, int], Tuple[int, int]] = {
    (0, 1): (0, 57),
    (0, 4): (15, 33),
    (0, 5): (14, 54),
    (0, 6): (5, 48),
    (0, 11): (27, 41),
    (1, 5): (8, 45),
    (1, 6): (29, 44),
    (1, 7): (23, 35),
    (1, 10): (11, 52),
    (2, 3): (1, 58),
    (2, 6): (20, 38),
    (2, 7): (19, 34),
    (2, 9): (10, 53),
    (2, 11): (7, 46),
    (3, 7): (13, 50),
    (3, 8): (28, 40),
    (3, 9): (9, 49),
    (3, 10): (16, 32),
    (4, 5): (2, 59),
    (4, 8): (24, 39),
    (4, 9): (25, 43),
    (4, 11): (12, 51),
    (5, 8): (18, 30),
    (5, 10): (21, 37),
    (6, 7): (3, 55),
    (6, 11): (17, 31),
    (7, 10): (26, 42),
    (8, 9): (4, 56),
    (8, 10): (6, 47),
    (9, 11): (22, 36),
}

PAIR_CYCLES: Dict[int, List[int]] = {
    0: [0, 14, 15, 41, 48, 57, 54, 33, 27, 5],
    1: [0, 29, 23, 52, 45, 57, 44, 35, 11, 8],
    2: [1, 19, 20, 46, 53, 58, 34, 38, 7, 10],
    3: [1, 9, 28, 32, 50, 58, 49, 40, 16, 13],
    4: [2, 24, 25, 51, 33, 59, 39, 43, 12, 15],
    5: [2, 14, 8, 37, 30, 59, 54, 45, 21, 18],
    6: [3, 29, 5, 31, 38, 55, 44, 48, 17, 20],
    7: [3, 19, 13, 42, 35, 55, 34, 50, 26, 23],
    8: [4, 24, 18, 47, 40, 56, 39, 30, 6, 28],
    9: [4, 9, 10, 36, 43, 56, 49, 53, 22, 25],
    10: [6, 37, 11, 42, 16, 47, 21, 52, 26, 32],
    11: [7, 31, 27, 51, 22, 46, 17, 41, 12, 36],
}


def canon(i: int, j: int) -> Tuple[int, int]:
    return (i, j) if i < j else (j, i)


def base_edges() -> List[Tuple[int, int]]:
    out = []
    for i, nbrs in BASE_ADJ.items():
        for j in nbrs:
            if i < j:
                out.append((i, j))
    return sorted(out)


def pair_to_edge_sheet() -> Dict[int, Tuple[Tuple[int, int], int]]:
    out = {}
    for e, (a, b) in EDGE_FIBERS.items():
        out[a] = (e, 0)
        out[b] = (e, 1)
    return out


def measured_pair_graph() -> Dict[int, Set[int]]:
    adj = defaultdict(set)
    for cyc in PAIR_CYCLES.values():
        n = len(cyc)
        for k in range(n):
            a = cyc[k]
            b = cyc[(k + 1) % n]
            adj[a].add(b)
            adj[b].add(a)
    return {k: set(v) for k, v in adj.items()}


def local_vertex_edges(v: int) -> List[Tuple[int, int]]:
    return [canon(v, u) for u in BASE_ADJ[v]]


def reconstruct_vertex_connection():
    adj = measured_pair_graph()
    p2es = pair_to_edge_sheet()

    rules = {}
    profile = Counter()
    skipped = 0

    for v in sorted(BASE_ADJ):
        inc_edges = local_vertex_edges(v)
        for i, e1 in enumerate(inc_edges):
            for e2 in inc_edges[i + 1:]:
                a0, a1 = EDGE_FIBERS[e1]
                b0, b1 = EDGE_FIBERS[e2]

                hits = []
                for x in (a0, a1):
                    for y in (b0, b1):
                        if y in adj[x]:
                            sx = p2es[x][1]
                            sy = p2es[y][1]
                            hits.append((sx, sy))

                pattern = tuple(sorted(hits))

                if pattern == ():
                    skipped += 1
                    continue

                if pattern not in [((0, 0), (1, 1)), ((0, 1), (1, 0))]:
                    raise RuntimeError(
                        f"Unexpected local pattern at vertex {v}, edges {e1}, {e2}: {pattern}"
                    )

                tag = "preserve" if pattern == ((0, 0), (1, 1)) else "swap"
                rules[(v, e1, e2)] = tag
                profile[tag] += 1

    return rules, profile, skipped


def edge_id_map() -> Dict[Tuple[int, int], int]:
    return {e: idx for idx, e in enumerate(base_edges())}


def node_id(edge_to_idx: Dict[Tuple[int, int], int], e: Tuple[int, int], sheet: int) -> int:
    return 2 * edge_to_idx[e] + sheet


def build_connection_model() -> Dict[int, Set[int]]:
    rules, _, _ = reconstruct_vertex_connection()
    e2i = edge_id_map()
    adj = defaultdict(set)

    for (_, e1, e2), tag in rules.items():
        for s in (0, 1):
            t = s if tag == "preserve" else 1 - s
            a = node_id(e2i, e1, s)
            b = node_id(e2i, e2, t)
            adj[a].add(b)
            adj[b].add(a)

    for e in base_edges():
        for s in (0, 1):
            adj[node_id(e2i, e, s)]

    return {k: set(v) for k, v in adj.items()}


def measured_graph_reindexed() -> Dict[int, Set[int]]:
    p2es = pair_to_edge_sheet()
    e2i = edge_id_map()
    raw = measured_pair_graph()

    out = defaultdict(set)
    for p, nbrs in raw.items():
        e, s = p2es[p]
        u = node_id(e2i, e, s)
        for q in nbrs:
            f, t = p2es[q]
            v = node_id(e2i, f, t)
            out[u].add(v)

    for e in base_edges():
        for s in (0, 1):
            out[node_id(e2i, e, s)]

    return {k: set(v) for k, v in out.items()}


def adjacency_matrix(adj: Dict[int, Set[int]]) -> np.ndarray:
    nodes = sorted(adj)
    idx = {v: i for i, v in enumerate(nodes)}
    A = np.zeros((len(nodes), len(nodes)), dtype=int)
    for v in nodes:
        for w in adj[v]:
            A[idx[v], idx[w]] = 1
    return A


def edge_set(adj: Dict[int, Set[int]]) -> Set[Tuple[int, int]]:
    out = set()
    for u, nbrs in adj.items():
        for v in nbrs:
            if u < v:
                out.add((u, v))
    return out


def triangle_count(adj: Dict[int, Set[int]]) -> int:
    nodes = sorted(adj)
    total = 0
    for i, a in enumerate(nodes):
        for b in [x for x in adj[a] if x > a]:
            common = adj[a] & adj[b]
            for c in [x for x in common if x > b]:
                total += 1
    return total


def common_neighbor_profiles(adj: Dict[int, Set[int]]) -> Tuple[Counter, Counter]:
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


def eigen_mults(adj: Dict[int, Set[int]]) -> Counter:
    A = adjacency_matrix(adj)
    vals = np.linalg.eigvals(A)
    vals = [round(float(np.real_if_close(v)), 6) for v in vals]
    return Counter(vals)


def summarize(name: str, adj: Dict[int, Set[int]]) -> None:
    edges = edge_set(adj)
    prof_adj, prof_non = common_neighbor_profiles(adj)
    mults = eigen_mults(adj)

    print("=" * 80)
    print(name)
    print("=" * 80)
    print(f"vertices: {len(adj)}")
    print(f"edges: {len(edges)}")
    print(f"degree set: {sorted({len(v) for v in adj.values()})}")
    print(f"triangles: {triangle_count(adj)}")

    print()
    print("adjacent common-neighbor profile:")
    for k in sorted(prof_adj):
        print(f"  {k}: {prof_adj[k]}")

    print("nonadjacent common-neighbor profile:")
    for k in sorted(prof_non):
        print(f"  {k}: {prof_non[k]}")

    print()
    print("eigenvalue multiplicities:")
    for val in sorted(mults):
        print(f"  {val:>10}: {mults[val]}")


def compare_graphs(a_name: str, a: Dict[int, Set[int]], b_name: str, b: Dict[int, Set[int]]) -> None:
    ea = edge_set(a)
    eb = edge_set(b)

    print("=" * 80)
    print(f"COMPARE: {a_name} vs {b_name}")
    print("=" * 80)
    print(f"edge sets equal: {ea == eb}")
    print(f"edges only in {a_name}: {len(ea - eb)}")
    print(f"edges only in {b_name}: {len(eb - ea)}")

    if ea != eb:
        print()
        print(f"first 20 edges only in {a_name}:")
        for e in sorted(ea - eb)[:20]:
            print(f"  {e}")
        print(f"first 20 edges only in {b_name}:")
        for e in sorted(eb - ea)[:20]:
            print(f"  {e}")


def main() -> None:
    rules, profile, skipped = reconstruct_vertex_connection()
    measured = measured_graph_reindexed()
    model = build_connection_model()

    print("=" * 80)
    print("VERTEX CONNECTION MODEL")
    print("=" * 80)
    print("Local connection profile")
    print("-" * 80)
    for k in sorted(profile):
        print(f"{k}: {profile[k]}")
    print(f"unused incident edge-pairs: {skipped}")

    print()
    summarize("MEASURED PAIR-FIBER GRAPH (REINDEXED)", measured)
    print()
    summarize("RECONSTRUCTED CONNECTION MODEL", model)
    print()
    compare_graphs("MEASURED", measured, "MODEL", model)

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("This builds the correct 60-state reference graph directly from:")
    print("- the icosahedral base graph on decagons")
    print("- the 2-sheet edge fiber on base edges")
    print("- the reconstructed vertex-local preserve/swap connection")
    print("- only the measured active incident edge-pairs at each base vertex")


if __name__ == "__main__":
    main()
