from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]

G60_CANDIDATES = [
    ROOT / "reports" / "true_quotients" / "true_chamber_graph.g6",
    ROOT / "artifacts" / "census" / "thalean_graph.g6",
]

PARTITION_CANDIDATES = [
    ROOT / "reports" / "true_quotients" / "compare_v4_quotient_to_canonical_dodecahedral_15core.json",
    ROOT / "reports" / "true_quotients" / "export_v4_cover_certificate.json",
]

V4 = [(0, 0), (1, 0), (0, 1), (1, 1)]


def add_v4(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    return ((a[0] + b[0]) % 2, (a[1] + b[1]) % 2)


def find_existing(path_list):
    for p in path_list:
        if p.exists():
            return p
    return None


def load_g60() -> nx.Graph:
    path = find_existing(G60_CANDIDATES)
    if path is None:
        raise FileNotFoundError("Could not find G60 .g6 file.")
    print(f"loading G60 from: {path}")
    G = nx.read_graph6(path)
    print(f"G60: |V|={G.number_of_nodes()} |E|={G.number_of_edges()}")
    return G


def try_extract_partition(data):
    """
    Accept a few possible JSON layouts.
    We want:
        fibers = [[v1,v2,v3,v4], ...]   length 15
    """
    candidates = []

    if isinstance(data, dict):
        for key in [
            "fibers",
            "fiber_partition",
            "v4_fibers",
            "orbits",
            "blocks",
            "partition",
            "classes",
        ]:
            if key in data and isinstance(data[key], list):
                candidates.append(data[key])

        # nested hunt
        for k, v in data.items():
            if isinstance(v, dict):
                for kk in [
                    "fibers",
                    "fiber_partition",
                    "v4_fibers",
                    "orbits",
                    "blocks",
                    "partition",
                    "classes",
                ]:
                    if kk in v and isinstance(v[kk], list):
                        candidates.append(v[kk])

    elif isinstance(data, list):
        candidates.append(data)

    for cand in candidates:
        if len(cand) == 15 and all(isinstance(x, list) and len(x) == 4 for x in cand):
            return cand

    return None


def load_partition() -> list[list[int]]:
    path = find_existing(PARTITION_CANDIDATES)
    if path is None:
        raise FileNotFoundError("Could not find partition/certificate JSON.")
    print(f"loading partition candidate from: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    fibers = try_extract_partition(data)
    if fibers is None:
        raise ValueError("Could not recognize a 15x4 fiber partition in the JSON.")
    print("recognized 15 fibers of size 4")
    return fibers


def build_base_graph(G: nx.Graph, fibers: list[list[int]]):
    vertex_to_fiber = {}
    for i, fiber in enumerate(fibers):
        for v in fiber:
            if v in vertex_to_fiber:
                raise ValueError(f"vertex {v} appears in multiple fibers")
            vertex_to_fiber[v] = i

    if len(vertex_to_fiber) != G.number_of_nodes():
        missing = set(G.nodes()) - set(vertex_to_fiber)
        raise ValueError(f"partition does not cover all vertices, missing: {sorted(missing)[:10]}")

    H = nx.Graph()
    H.add_nodes_from(range(len(fibers)))

    edge_fiber_pairs = defaultdict(list)
    intra = 0

    for u, v in G.edges():
        fu = vertex_to_fiber[u]
        fv = vertex_to_fiber[v]
        if fu == fv:
            intra += 1
        else:
            a, b = sorted((fu, fv))
            H.add_edge(a, b)
            edge_fiber_pairs[(a, b)].append((u, v))

    print(f"base graph H: |V|={H.number_of_nodes()} |E|={H.number_of_edges()}")
    print(f"intra-fiber edges in G60: {intra}")
    return H, vertex_to_fiber, edge_fiber_pairs


def analyze_cover(G, fibers, H, edge_fiber_pairs):
    """
    For a regular V4 cover of a simple base graph:
    - each base edge should lift to exactly 4 edges
    - between two fibers there should be a perfect matching
    - after labeling one fiber by V4, the other should admit labels so that
      all 4 lifted edges are x -> x + delta for a single delta in V4
    """
    if H.number_of_nodes() != 15:
        print("WARNING: base graph is not 15-vertex.")
    if H.number_of_edges() != 30:
        print("WARNING: base graph is not 30-edge.")

    bad_counts = []
    for e, lifted in edge_fiber_pairs.items():
        if len(lifted) != 4:
            bad_counts.append((e, len(lifted)))

    if bad_counts:
        print("\nEdges whose lift multiplicity is not 4:")
        for e, c in bad_counts[:20]:
            print(f"  {e}: {c}")
    else:
        print("\nEvery base edge lifts to exactly 4 edges.")

    spanning = nx.minimum_spanning_tree(H)
    print(f"using spanning tree with {spanning.number_of_edges()} edges to assign V4 labels")

    # label assignment per base fiber vertex
    fiber_labels: dict[int, dict[int, tuple[int, int]]] = {}

    root = 0
    fiber_labels[root] = {v: lbl for v, lbl in zip(sorted(fibers[root]), V4)}

    # BFS over spanning tree
    queue = [root]
    seen = {root}

    while queue:
        a = queue.pop(0)
        for b in spanning.neighbors(a):
            if b in seen:
                continue

            # collect lifted edges between fiber a and fiber b
            key = tuple(sorted((a, b)))
            lifted = edge_fiber_pairs[key]

            # orient from a-fiber to b-fiber
            pairs = []
            fiber_a = set(fibers[a])
            fiber_b = set(fibers[b])
            for u, v in lifted:
                if u in fiber_a and v in fiber_b:
                    pairs.append((u, v))
                elif v in fiber_a and u in fiber_b:
                    pairs.append((v, u))
                else:
                    raise RuntimeError("lifted edge does not connect expected fibers")

            if len(pairs) != 4:
                raise RuntimeError("expected 4 oriented lifted edges")

            # induced bijection a->b from the perfect matching
            map_ab = {u: v for u, v in pairs}
            if len(map_ab) != 4 or len(set(map_ab.values())) != 4:
                raise RuntimeError("lift is not a perfect matching between fibers")

            # choose labels on b so that delta=(0,0) across the spanning edge
            labels_b = {}
            for u in fiber_labels[a]:
                v = map_ab[u]
                labels_b[v] = fiber_labels[a][u]

            fiber_labels[b] = labels_b
            seen.add(b)
            queue.append(b)

    # now compute voltage on every base edge
    edge_voltage = {}
    failures = []

    for (a, b), lifted in sorted(edge_fiber_pairs.items()):
        fiber_a = set(fibers[a])
        fiber_b = set(fibers[b])

        deltas = []
        for u, v in lifted:
            if u in fiber_a and v in fiber_b:
                uu, vv = u, v
            elif v in fiber_a and u in fiber_b:
                uu, vv = v, u
            else:
                failures.append(((a, b), "bad endpoint placement"))
                continue

            la = fiber_labels[a][uu]
            lb = fiber_labels[b][vv]
            delta = add_v4(lb, la)  # lb - la over Z2 == lb + la
            deltas.append(delta)

        distinct = sorted(set(deltas))
        if len(distinct) == 1:
            edge_voltage[(a, b)] = distinct[0]
        else:
            failures.append(((a, b), f"non-constant delta set: {distinct}"))

    print("\nVoltage assignment summary")
    print("--------------------------")
    counts = defaultdict(int)
    for e, d in edge_voltage.items():
        counts[d] += 1
    for d in sorted(counts):
        print(f"  {d}: {counts[d]} base edges")

    if failures:
        print("\nFAILED edges:")
        for item in failures[:20]:
            print(" ", item)
    else:
        print("\nSuccess: every base edge is translation by a single V4 element.")
        print("This strongly supports a regular V4-voltage-cover model.")

    out = {
        "base_vertices": H.number_of_nodes(),
        "base_edges": H.number_of_edges(),
        "fiber_labels": {
            str(i): {str(v): list(lbl) for v, lbl in lab.items()}
            for i, lab in fiber_labels.items()
        },
        "edge_voltage": {
            f"{a}-{b}": list(d) for (a, b), d in edge_voltage.items()
        },
        "failures": [str(x) for x in failures],
    }

    out_path = ROOT / "reports" / "v4_voltage_cover_reconstruction.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nsaved {out_path}")


def main():
    G = load_g60()
    fibers = load_partition()
    H, vertex_to_fiber, edge_fiber_pairs = build_base_graph(G, fibers)
    analyze_cover(G, fibers, H, edge_fiber_pairs)


if __name__ == "__main__":
    main()
