#!/usr/bin/env python3

import json
from collections import deque
from pathlib import Path

SIGNED_EDGE_JSON = Path("cocycles/tables/signed_edge_table.json")
OUTPUT_JSON = Path("cocycles/tables/parity_sector_table.json")
REPORT_TXT = Path("cocycles/tables/parity_sector_table_report.txt")


def norm(u, v):
    return (u, v) if u <= v else (v, u)


def load_signed_edges():
    if not SIGNED_EDGE_JSON.exists():
        raise SystemExit(f"Missing signed edge table: {SIGNED_EDGE_JSON}")
    data = json.loads(SIGNED_EDGE_JSON.read_text(encoding="utf-8"))
    edges = []
    eps = {}
    for row in data:
        u, v = int(row["edge"][0]), int(row["edge"][1])
        e = norm(u, v)
        edges.append(e)
        eps[e] = int(row["epsilon"])
    return sorted(set(edges)), eps


def build_adj(edges):
    verts = sorted({x for e in edges for x in e})
    adj = {v: set() for v in verts}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def shortest_path_tree_with_parity(adj, eps, root):
    """
    Canonical BFS tree rooted at `root`.
    Records parity of the unique tree path from root to each vertex.
    """
    dist = {root: 0}
    parent = {root: None}
    q = deque([root])

    while q:
        x = q.popleft()
        for y in sorted(adj[x]):
            if y not in dist:
                dist[y] = dist[x] + 1
                parent[y] = x
                q.append(y)
            elif dist[y] == dist[x] + 1:
                if parent[y] is None or x < parent[y]:
                    parent[y] = x

    path_parity = {root: 0}
    verts_by_dist = sorted(dist.keys(), key=lambda z: dist[z])
    for y in verts_by_dist:
        p = parent[y]
        if p is None:
            continue
        e = norm(y, p)
        path_parity[y] = path_parity[p] ^ eps[e]

    even_edges = []
    odd_edges = []
    for y, p in parent.items():
        if p is None:
            continue
        e = norm(y, p)
        # parity of the rooted transport incidence at this tree edge
        if path_parity[y] == 0:
            even_edges.append(list(e))
        else:
            odd_edges.append(list(e))

    even_edges.sort()
    odd_edges.sort()
    return even_edges, odd_edges


def main():
    edges, eps = load_signed_edges()
    adj = build_adj(edges)
    verts = sorted(adj.keys())

    out = []
    total_even = 0
    total_odd = 0

    for v in verts:
        even_edges, odd_edges = shortest_path_tree_with_parity(adj, eps, v)
        if len(even_edges) + len(odd_edges) != len(verts) - 1:
            raise SystemExit(
                f"Root {v}: expected {len(verts)-1} sector edges, got {len(even_edges)+len(odd_edges)}"
            )
        total_even += len(even_edges)
        total_odd += len(odd_edges)
        out.append({
            "vertex": int(v),
            "even_edges": even_edges,
            "odd_edges": odd_edges,
        })

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps({"sectors": out}, indent=2),
        encoding="utf-8",
    )

    report = []
    report.append("PARITY SECTOR EXPORT")
    report.append("=" * 60)
    report.append(f"vertices: {len(out)}")
    report.append(f"sector size: {len(out[0]['even_edges']) + len(out[0]['odd_edges']) if out else 0}")
    report.append(f"even incidences: {total_even}")
    report.append(f"odd incidences: {total_odd}")
    REPORT_TXT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"saved {OUTPUT_JSON}")
    print(f"saved {REPORT_TXT}")
    print(f"vertices: {len(out)}")
    print(f"sector size: {len(out[0]['even_edges']) + len(out[0]['odd_edges']) if out else 0}")


if __name__ == "__main__":
    main()
