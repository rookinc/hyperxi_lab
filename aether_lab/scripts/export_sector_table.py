#!/usr/bin/env python3

import json
from collections import deque
from pathlib import Path

SIGNED_EDGE_JSON = Path("cocycles/tables/signed_edge_table.json")
OUTPUT = Path("cocycles/tables/transport_spec_summary.json")


def norm(u, v):
    return (u, v) if u <= v else (v, u)


def load_edges():
    if not SIGNED_EDGE_JSON.exists():
        raise SystemExit(f"Missing signed edge table: {SIGNED_EDGE_JSON}")
    data = json.loads(SIGNED_EDGE_JSON.read_text(encoding="utf-8"))
    edges = [norm(int(r["edge"][0]), int(r["edge"][1])) for r in data]
    return sorted(set(edges))


def build_adj(edges):
    verts = sorted({x for e in edges for x in e})
    adj = {v: set() for v in verts}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def shortest_path_tree(adj, root):
    """
    Canonical BFS tree rooted at `root`.
    Parent choice is the smallest-labeled predecessor.
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
                # smaller parent wins for canonical tree
                if parent[y] is None or x < parent[y]:
                    parent[y] = x

    tree_edges = []
    for y, p in parent.items():
        if p is not None:
            tree_edges.append(list(norm(y, p)))
    tree_edges.sort()
    return tree_edges


def main():
    edges = load_edges()
    adj = build_adj(edges)
    verts = sorted(adj.keys())

    out = []
    for v in verts:
        tree_edges = shortest_path_tree(adj, v)
        if len(tree_edges) != len(verts) - 1:
            raise SystemExit(
                f"Root {v}: expected {len(verts)-1} tree edges, got {len(tree_edges)}"
            )
        out.append({
            "vertex": int(v),
            "edges": tree_edges,
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"saved {OUTPUT}")
    print(f"vertices: {len(out)}")
    print(f"sector size: {len(out[0]['edges']) if out else 0}")


if __name__ == "__main__":
    main()
