from __future__ import annotations

from collections import Counter, deque


# Decagon -> S-pair incidence, extracted from pair_decagon_incidence.py output
DECAGONS: dict[int, list[int]] = {
    0:  [0, 5, 14, 15, 27, 33, 41, 48, 54, 57],
    1:  [0, 8, 11, 23, 29, 35, 44, 45, 52, 57],
    2:  [1, 7, 10, 19, 20, 34, 38, 46, 53, 58],
    3:  [1, 9, 13, 16, 28, 32, 40, 49, 50, 58],
    4:  [2, 12, 15, 24, 25, 33, 39, 43, 51, 59],
    5:  [2, 8, 14, 18, 21, 30, 37, 45, 54, 59],
    6:  [3, 5, 17, 20, 29, 31, 38, 44, 48, 55],
    7:  [3, 13, 19, 23, 26, 34, 35, 42, 50, 55],
    8:  [4, 6, 18, 24, 28, 30, 39, 40, 47, 56],
    9:  [4, 9, 10, 22, 25, 36, 43, 49, 53, 56],
    10: [6, 11, 16, 21, 26, 32, 37, 42, 47, 52],
    11: [7, 12, 17, 22, 27, 31, 36, 41, 46, 51],
}


def build_intersection_matrix(decagons: dict[int, list[int]]) -> list[list[int]]:
    keys = sorted(decagons)
    sets = {k: set(v) for k, v in decagons.items()}
    matrix: list[list[int]] = []
    for i in keys:
        row = []
        for j in keys:
            row.append(len(sets[i] & sets[j]))
        matrix.append(row)
    return matrix


def build_shared_pairs(decagons: dict[int, list[int]]) -> dict[tuple[int, int], list[int]]:
    keys = sorted(decagons)
    sets = {k: set(v) for k, v in decagons.items()}
    shared: dict[tuple[int, int], list[int]] = {}
    for idx_i, i in enumerate(keys):
        for j in keys[idx_i + 1:]:
            inter = sorted(sets[i] & sets[j])
            shared[(i, j)] = inter
    return shared


def build_simple_adjacency(shared: dict[tuple[int, int], list[int]], n: int) -> dict[int, list[int]]:
    adj = {i: [] for i in range(n)}
    for (i, j), inter in shared.items():
        if inter:
            adj[i].append(j)
            adj[j].append(i)
    for i in adj:
        adj[i].sort()
    return adj


def connected_components(adj: dict[int, list[int]]) -> list[list[int]]:
    seen: set[int] = set()
    comps: list[list[int]] = []
    for start in sorted(adj):
        if start in seen:
            continue
        comp: list[int] = []
        q = deque([start])
        seen.add(start)
        while q:
            u = q.popleft()
            comp.append(u)
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    q.append(v)
        comps.append(sorted(comp))
    return comps


def print_matrix(matrix: list[list[int]]) -> None:
    n = len(matrix)
    print("Intersection matrix M_ij = |D_i ∩ D_j|")
    print("-" * 80)
    header = "      " + " ".join(f"{j:>3}" for j in range(n))
    print(header)
    for i, row in enumerate(matrix):
        print(f"{i:>3}: " + " ".join(f"{x:>3}" for x in row))


def main() -> None:
    n = len(DECAGONS)
    matrix = build_intersection_matrix(DECAGONS)
    shared = build_shared_pairs(DECAGONS)
    adj = build_simple_adjacency(shared, n)
    comps = connected_components(adj)

    print("=" * 80)
    print("DECAGON INTERSECTION GRAPH")
    print("=" * 80)
    print(f"decagons: {n}")
    print()

    print_matrix(matrix)
    print()

    print("=" * 80)
    print("UNORDERED DECAGON PAIR INTERSECTIONS")
    print("=" * 80)
    intersection_size_counter: Counter[int] = Counter()
    simple_edges = 0
    multi_edges = 0

    for (i, j), inter in sorted(shared.items()):
        sz = len(inter)
        intersection_size_counter[sz] += 1
        if sz > 0:
            simple_edges += 1
            multi_edges += sz
        print(f"({i:2d}, {j:2d}) -> size={sz} shared_pairs={inter}")

    print()
    print("=" * 80)
    print("INTERSECTION SIZE COUNTS")
    print("=" * 80)
    for sz in sorted(intersection_size_counter):
        print(f"size {sz}: {intersection_size_counter[sz]} unordered decagon pairs")

    print()
    print("=" * 80)
    print("SIMPLE ADJACENCY GRAPH")
    print("=" * 80)
    degree_sequence = []
    for i in range(n):
        nbrs = adj[i]
        degree_sequence.append(len(nbrs))
        print(f"decagon {i:2d} -> neighbors {nbrs}")

    print()
    print(f"degree sequence: {degree_sequence}")
    print(f"all degrees equal 5: {all(d == 5 for d in degree_sequence)}")
    print(f"simple graph vertices: {n}")
    print(f"simple graph edges:    {simple_edges}")
    print(f"sum of degrees:        {sum(degree_sequence)}")
    print(f"connected components:  {comps}")
    print(f"connected:             {len(comps) == 1}")

    print()
    print("=" * 80)
    print("EDGE FIBERS")
    print("=" * 80)
    print("For each simple edge (i,j), list the 2 shared S-pairs.")
    for (i, j), inter in sorted(shared.items()):
        if inter:
            print(f"edge ({i:2d}, {j:2d}) -> fiber {inter}")

    print()
    print("=" * 80)
    print("DISJOINT / OPPOSITE DECAGONS")
    print("=" * 80)
    for i in range(n):
        disjoint = [j for j in range(n) if j != i and matrix[i][j] == 0]
        print(f"decagon {i:2d} -> disjoint from {disjoint}")

    print()
    print("=" * 80)
    print("CHECKS")
    print("=" * 80)
    nonzero_sizes = sorted({len(inter) for inter in shared.values() if inter})
    print(f"nonzero intersection sizes present: {nonzero_sizes}")
    print(f"every nonzero intersection has size 2: {nonzero_sizes == [2]}")
    print(f"simple edge count should be 30:       {simple_edges == 30}")
    print(f"all degrees should be 5:              {all(d == 5 for d in degree_sequence)}")
    print(f"multi-edge count from shared pairs:   {multi_edges}")
    print(f"expected pair total 60 via 2-fold cover: {multi_edges == 60}")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("If every nonzero intersection has size 2, then the 60 S-pairs")
    print("form a 2-fold edge fiber over the simple decagon intersection graph.")
    print("If the simple graph has 12 vertices, 30 edges, and all degrees 5,")
    print("then it matches the size profile of the icosahedral graph.")


if __name__ == "__main__":
    main()
