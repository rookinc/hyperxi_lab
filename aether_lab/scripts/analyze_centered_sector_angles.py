from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT_TXT = ROOT / "reports" / "quotients" / "analyze_centered_sector_angles.txt"
OUT_JSON = ROOT / "reports" / "quotients" / "analyze_centered_sector_angles.json"


def build_lp_reference():
    P = nx.petersen_graph()
    L = nx.line_graph(P)

    nodes = sorted(tuple(sorted(x)) for x in L.nodes())
    edge_to_id = {n: i for i, n in enumerate(nodes)}

    G = nx.Graph()
    G.add_nodes_from(range(len(nodes)))
    for a, b in L.edges():
        ia = edge_to_id[tuple(sorted(a))]
        ib = edge_to_id[tuple(sorted(b))]
        G.add_edge(ia, ib)

    return G


def rooted_orientation(G: nx.Graph, root: int) -> nx.DiGraph:
    D = nx.DiGraph()
    D.add_nodes_from(G.nodes())
    dist = nx.single_source_shortest_path_length(G, root)

    for u, v in G.edges():
        du = dist[u]
        dv = dist[v]

        if du == 0 and dv == 1:
            D.add_edge(u, v)
        elif dv == 0 and du == 1:
            D.add_edge(v, u)
        elif du == 1 and dv == 1:
            a, b = sorted((u, v))
            D.add_edge(a, b)
        elif du == 1 and dv == 2:
            D.add_edge(u, v)
        elif dv == 1 and du == 2:
            D.add_edge(v, u)

    return D


def transport_sector_edges(G: nx.Graph, root: int) -> set[tuple[int, int]]:
    D = rooted_orientation(G, root)
    reached = {root: 0}
    frontier = [root]

    while frontier:
        nxt = []
        for u in frontier:
            if reached[u] == 2:
                continue
            for v in D.successors(u):
                if v not in reached:
                    reached[v] = reached[u] + 1
                    nxt.append(v)
        frontier = nxt

    edges = set()
    for u in reached:
        if reached[u] == 2:
            continue
        for v in D.successors(u):
            if v in reached and reached[v] <= 2:
                edges.add(tuple(sorted((u, v))))
    return edges


def main():
    G = build_lp_reference()
    roots = list(G.nodes())
    core_edges = sorted(tuple(sorted(e)) for e in G.edges())
    edge_index = {e: i for i, e in enumerate(core_edges)}

    sectors = {r: transport_sector_edges(G, r) for r in roots}

    M = np.zeros((len(roots), len(core_edges)), dtype=float)
    for r in roots:
        for e in sectors[r]:
            M[r, edge_index[e]] = 1.0

    mean = 7.0 / 15.0
    Mc = M - mean * np.ones_like(M)

    norms = np.linalg.norm(Mc, axis=1)
    unit = Mc / norms[:, None]

    # Raw centered Gram
    Gc = Mc @ Mc.T

    # Normalized Gram = cosines
    C = unit @ unit.T

    dist_all = dict(nx.all_pairs_shortest_path_length(G))

    raw_by_dist = defaultdict(list)
    cos_by_dist = defaultdict(list)
    for i in roots:
        for j in roots:
            if i >= j:
                continue
            d = dist_all[i][j]
            raw_by_dist[d].append(round(float(Gc[i, j]), 10))
            cos_by_dist[d].append(round(float(C[i, j]), 10))

    raw_hist = Counter(round(float(Gc[i, j]), 10) for i in roots for j in roots if i < j)
    cos_hist = Counter(round(float(C[i, j]), 10) for i in roots for j in roots if i < j)

    lines = []
    lines.append("=" * 80)
    lines.append("ANALYZE CENTERED SECTOR ANGLES")
    lines.append("=" * 80)
    lines.append("")
    lines.append("CENTERED VECTOR NORMS")
    lines.append("-" * 80)
    lines.append("distinct norms: " + str(sorted(set(round(float(x), 10) for x in norms))))
    lines.append("")
    lines.append("RAW CENTERED INNER PRODUCTS")
    lines.append("-" * 80)
    for v, c in sorted(raw_hist.items()):
        lines.append(f"{v}: {c} pairs")
    lines.append("")
    lines.append("NORMALIZED INNER PRODUCTS (COSINES)")
    lines.append("-" * 80)
    for v, c in sorted(cos_hist.items()):
        lines.append(f"{v}: {c} pairs")
    lines.append("")
    lines.append("BY ROOT DISTANCE")
    lines.append("-" * 80)
    for d in sorted(raw_by_dist):
        raw_vals = sorted(set(raw_by_dist[d]))
        cos_vals = sorted(set(cos_by_dist[d]))
        lines.append(f"distance {d}:")
        lines.append(f"  raw inner products: {raw_vals}")
        lines.append(f"  cosines: {cos_vals}")
    lines.append("")

    payload = {
        "distinct_norms": sorted(set(round(float(x), 10) for x in norms)),
        "raw_inner_product_histogram": dict(sorted(raw_hist.items())),
        "cosine_histogram": dict(sorted(cos_hist.items())),
        "by_distance": {
            str(d): {
                "raw": sorted(set(raw_by_dist[d])),
                "cos": sorted(set(cos_by_dist[d])),
            }
            for d in sorted(raw_by_dist)
        },
    }

    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("\n".join(lines))
    print(f"saved {OUT_TXT}")
    print(f"saved {OUT_JSON}")


if __name__ == "__main__":
    main()
