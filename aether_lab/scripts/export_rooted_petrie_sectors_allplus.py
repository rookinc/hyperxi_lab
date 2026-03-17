#!/usr/bin/env python3

import json
from pathlib import Path

SIGNED_EDGE_JSON = Path("cocycles/tables/signed_edge_table.json")
PETRIE_JSON = Path("cocycles/tables/petrie_cycles.json")
OUTPUT = Path("cocycles/tables/rooted_petrie_allplus_sector_table.json")
REPORT = Path("cocycles/tables/rooted_petrie_allplus_sector_table_report.txt")


def norm_edge(u, v):
    return (u, v) if u <= v else (v, u)


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


def directed_rotations(cycle):
    cyc = list(cycle)
    n = len(cyc)
    out = []
    for i in range(n):
        out.append(tuple(cyc[i:] + cyc[:i]))
    rev = list(reversed(cyc))
    for i in range(n):
        out.append(tuple(rev[i:] + rev[:i]))
    return out


def load_edges_and_verts():
    data = json.loads(SIGNED_EDGE_JSON.read_text(encoding="utf-8"))
    edges = set()
    verts = set()
    for row in data:
        u, v = int(row["edge"][0]), int(row["edge"][1])
        e = norm_edge(u, v)
        edges.add(e)
        verts.add(u)
        verts.add(v)
    return sorted(edges), sorted(verts)


def load_cycles():
    data = json.loads(PETRIE_JSON.read_text(encoding="utf-8"))
    rows = data["cycles"] if isinstance(data, dict) and "cycles" in data else data
    seen = set()
    out = []
    for cyc in rows:
        cc = canonical_cycle(tuple(int(x) for x in cyc))
        if cc not in seen:
            seen.add(cc)
            out.append(cc)
    return out


def build_adjacency(verts, edges):
    adj = {v: set() for v in verts}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return {v: sorted(adj[v]) for v in adj}


def cycle_edges(cycle):
    n = len(cycle)
    return [norm_edge(cycle[i], cycle[(i + 1) % n]) for i in range(n)]


def choose_cycle_for_directed_edge(root, nbr, cycles):
    candidates = []
    for cyc in cycles:
        for rot in directed_rotations(cyc):
            if len(rot) >= 2 and rot[0] == root and rot[1] == nbr:
                candidates.append(rot)
    return min(candidates) if candidates else None


def rooted_sector_for_vertex(root, adj, cycles):
    chosen_cycles = []
    edge_set = set()
    for nbr in adj[root]:
        cyc = choose_cycle_for_directed_edge(root, nbr, cycles)
        if cyc is None:
            continue
        chosen_cycles.append(cyc)
        edge_set.update(cycle_edges(cyc))
    plus_edges = [[e[0], e[1]] for e in sorted(edge_set)]
    return chosen_cycles, plus_edges


def main():
    if not SIGNED_EDGE_JSON.exists():
        raise SystemExit(f"Missing signed edge table: {SIGNED_EDGE_JSON}")
    if not PETRIE_JSON.exists():
        raise SystemExit(f"Missing Petrie cycles file: {PETRIE_JSON}")

    edges, verts = load_edges_and_verts()
    cycles = load_cycles()
    adj = build_adjacency(verts, edges)

    out = []
    sizes = []
    chosen_counts = []

    for v in verts:
        chosen_cycles, plus_edges = rooted_sector_for_vertex(v, adj, cycles)
        sizes.append(len(plus_edges))
        chosen_counts.append(len(chosen_cycles))
        out.append({
            "vertex": int(v),
            "even_edges": plus_edges,
            "odd_edges": [],
            "chosen_cycles": [list(c) for c in chosen_cycles],
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"sectors": out}, indent=2), encoding="utf-8")

    report = []
    report.append("ROOTED LOCAL PETRIE ALL-PLUS SECTOR EXPORT")
    report.append("=" * 60)
    report.append(f"canonical petrie cycles available: {len(cycles)}")
    report.append(f"vertices: {len(out)}")
    report.append(f"chosen cycle counts per root: {chosen_counts}")
    report.append(f"sector sizes: {sizes}")
    report.append(f"min sector size: {min(sizes) if sizes else 0}")
    report.append(f"max sector size: {max(sizes) if sizes else 0}")
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"saved {OUTPUT}")
    print(f"saved {REPORT}")


if __name__ == "__main__":
    main()
