#!/usr/bin/env python3

import json
from pathlib import Path

SIGNED_EDGE_JSON = Path("cocycles/tables/signed_edge_table.json")
OUTPUT = Path("cocycles/tables/petrie_cycles.json")


def norm(u, v):
    return (u, v) if u <= v else (v, u)


def load_edges():
    data = json.loads(SIGNED_EDGE_JSON.read_text(encoding="utf-8"))
    return sorted({norm(int(r["edge"][0]), int(r["edge"][1])) for r in data})


def build_adj(edges):
    verts = sorted({x for e in edges for x in e})
    adj = {v: [] for v in verts}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    for v in adj:
        adj[v] = sorted(adj[v])
    return adj


def canonical_cycle(cycle):
    cyc = list(cycle)
    n = len(cyc)
    reps = []
    for i in range(n):
        reps.append(tuple(cyc[i:] + cyc[:i]))
    rev = list(reversed(cyc))
    for i in range(n):
        reps.append(tuple(rev[i:] + rev[:i]))
    return min(reps)


def find_cycles_of_length(adj, length=10):
    seen = set()

    def dfs(start, cur, path, used):
        if len(path) == length:
            if start in adj[cur]:
                cyc = canonical_cycle(tuple(path))
                seen.add(cyc)
            return
        for nxt in adj[cur]:
            if nxt in used:
                continue
            dfs(start, nxt, path + [nxt], used | {nxt})

    for start in sorted(adj):
        dfs(start, start, [start], {start})

    return sorted(seen)


def main():
    if not SIGNED_EDGE_JSON.exists():
        raise SystemExit(f"Missing signed edge table: {SIGNED_EDGE_JSON}")

    edges = load_edges()
    adj = build_adj(edges)
    cycles = find_cycles_of_length(adj, length=10)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"cycles": [list(c) for c in cycles]}, indent=2), encoding="utf-8")
    print(f"saved {OUTPUT}")
    print(f"petrie cycles found: {len(cycles)}")


if __name__ == "__main__":
    main()
