from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT_TXT = ROOT / "reports" / "quotients" / "verify_core_polynomial_identity.txt"
OUT_JSON = ROOT / "reports" / "quotients" / "verify_core_polynomial_identity.json"


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
    G, _ = build_lp_reference()
    roots = list(G.nodes())
    core_edges = sorted(tuple(sorted(e)) for e in G.edges())
    edge_index = {e: i for i, e in enumerate(core_edges)}

    sectors = {r: transport_sector_edges(G, r) for r in roots}

    M = np.zeros((len(roots), len(core_edges)), dtype=int)
    for r in roots:
        for e in sectors[r]:
            M[r, edge_index[e]] = 1

    MMt = M @ M.T
    A = nx.to_numpy_array(G, nodelist=roots, dtype=int)

    dist = dict(nx.all_pairs_shortest_path_length(G))
    n = G.number_of_nodes()

    I = np.eye(n, dtype=int)
    A1 = A.astype(int)
    A2 = np.zeros((n, n), dtype=int)
    A3 = np.zeros((n, n), dtype=int)

    for i in roots:
        for j in roots:
            d = dist[i][j]
            if d == 2:
                A2[i, j] = 1
            elif d == 3:
                A3[i, j] = 1

    distance_form = 14 * I + 9 * A1 + 5 * A2 + 4 * A3
    poly_form = (A @ A @ A) + 2 * (A @ A) + 2 * I

    ok_distance = np.array_equal(MMt, distance_form)
    ok_poly = np.array_equal(MMt, poly_form)
    ok_cross = np.array_equal(distance_form, poly_form)

    lines = []
    lines.append("=" * 80)
    lines.append("VERIFY CORE POLYNOMIAL IDENTITY")
    lines.append("=" * 80)
    lines.append("")
    lines.append("CHECKS")
    lines.append("-" * 80)
    lines.append(f"MM^T = 14I + 9A1 + 5A2 + 4A3 : {ok_distance}")
    lines.append(f"MM^T = A^3 + 2A^2 + 2I       : {ok_poly}")
    lines.append(f"distance form = polynomial form: {ok_cross}")
    lines.append("")

    lines.append("FIRST 5x5 BLOCK OF MM^T")
    lines.append("-" * 80)
    for i in range(5):
        lines.append(" ".join(f"{int(MMt[i,j]):2d}" for j in range(5)))
    lines.append("")

    lines.append("FIRST 5x5 BLOCK OF A^3 + 2A^2 + 2I")
    lines.append("-" * 80)
    for i in range(5):
        lines.append(" ".join(f"{int(poly_form[i,j]):2d}" for j in range(5)))
    lines.append("")

    payload = {
        "distance_form_matches": bool(ok_distance),
        "polynomial_form_matches": bool(ok_poly),
        "cross_match": bool(ok_cross),
    }

    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("\n".join(lines))
    print(f"saved {OUT_TXT}")
    print(f"saved {OUT_JSON}")


if __name__ == "__main__":
    main()
