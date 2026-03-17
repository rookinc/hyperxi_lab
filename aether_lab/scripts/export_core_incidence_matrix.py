from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT_TXT = ROOT / "reports" / "quotients" / "export_core_incidence_matrix.txt"
OUT_JSON = ROOT / "reports" / "quotients" / "export_core_incidence_matrix.json"


def build_lp_reference():
    P = nx.petersen_graph()
    L = nx.line_graph(P)

    nodes = sorted(tuple(sorted(x)) for x in L.nodes())
    edge_to_id = {n: i for i, n in enumerate(nodes)}
    id_to_edge = {i: n for i, n in enumerate(nodes)}

    G = nx.Graph()
    G.add_nodes_from(range(len(nodes)))
    for a, b in L.edges():
        ia = edge_to_id[tuple(sorted(a))]
        ib = edge_to_id[tuple(sorted(b))]
        G.add_edge(ia, ib)

    return G, id_to_edge


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
    G, id_to_edge = build_lp_reference()
    roots = list(range(G.number_of_nodes()))
    core_edges = sorted(tuple(sorted(e)) for e in G.edges())
    edge_index = {e: i for i, e in enumerate(core_edges)}

    sectors = {r: transport_sector_edges(G, r) for r in roots}

    M = np.zeros((len(roots), len(core_edges)), dtype=int)
    for r in roots:
        for e in sectors[r]:
            M[r, edge_index[e]] = 1

    row_sums = M.sum(axis=1).tolist()
    col_sums = M.sum(axis=0).tolist()
    Gram = (M @ M.T).tolist()

    dist = dict(nx.all_pairs_shortest_path_length(G))
    ok = True
    bad = []
    for r in roots:
        for s in roots:
            val = Gram[r][s]
            if r == s and val != 14:
                ok = False
                bad.append((r, s, val, "diag"))
            elif r != s:
                d = dist[r][s]
                target = {1: 9, 2: 5, 3: 4}[d]
                if val != target:
                    ok = False
                    bad.append((r, s, val, d, target))

    lines = []
    lines.append("=" * 80)
    lines.append("EXPORT CORE INCIDENCE MATRIX")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"matrix shape: {M.shape[0]} x {M.shape[1]}")
    lines.append(f"row sums: {sorted(set(row_sums))}")
    lines.append(f"column sums: {sorted(set(col_sums))}")
    lines.append(f"gram law matches distances: {ok}")
    lines.append("")

    lines.append("FIRST 5 ROWS OF INCIDENCE MATRIX")
    lines.append("-" * 80)
    for r in range(5):
        lines.append(f"root {r}: {' '.join(map(str, M[r].tolist()))}")
    lines.append("")

    lines.append("GRAM MATRIX (FIRST 5x5 BLOCK)")
    lines.append("-" * 80)
    for r in range(5):
        lines.append(" ".join(f"{Gram[r][s]:2d}" for s in range(5)))
    lines.append("")

    if bad:
        lines.append("MISMATCHES")
        lines.append("-" * 80)
        for x in bad[:20]:
            lines.append(str(x))
        lines.append("")

    payload = {
        "shape": [int(M.shape[0]), int(M.shape[1])],
        "row_sum_set": sorted(set(int(x) for x in row_sums)),
        "column_sum_set": sorted(set(int(x) for x in col_sums)),
        "gram_matches_distance_law": ok,
        "core_edges": [[u, v] for (u, v) in core_edges],
        "incidence_matrix": M.tolist(),
        "gram_matrix": Gram,
    }

    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("\n".join(lines))
    print(f"saved {OUT_TXT}")
    print(f"saved {OUT_JSON}")


if __name__ == "__main__":
    main()
