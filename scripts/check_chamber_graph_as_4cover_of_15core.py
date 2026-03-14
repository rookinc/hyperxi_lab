#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from collections import defaultdict
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


def build_chamber_graph() -> nx.Graph:
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    owner = {}
    classes = []
    seen = set()

    for i in range(fm.num_flags()):
        if i in seen:
            continue
        j = fm.index(gen.S(fm.get(i)))
        cyc = tuple(sorted((i, j)))
        cid = len(classes)
        classes.append(cyc)
        for x in cyc:
            seen.add(x)
            owner[x] = cid

    edges = set()
    for cyc in classes:
        src = owner[cyc[0]]
        for flag_idx in cyc:
            dst_flag = gen.V(fm.get(flag_idx))
            dst = owner[fm.index(dst_flag)]
            if dst != src:
                a, b = sorted((src, dst))
                edges.add((a, b))

    G = nx.Graph()
    G.add_nodes_from(range(len(classes)))
    G.add_edges_from(edges)
    return G


def find_antipodal_pairs(G: nx.Graph):
    dist = dict(nx.all_pairs_shortest_path_length(G))
    diam = nx.diameter(G)
    pairs = []
    used = set()

    for u in G.nodes():
        if u in used:
            continue
        far = [v for v, d in dist[u].items() if d == diam]
        if len(far) != 1:
            return None, diam, dist
        v = far[0]
        if u == v or dist[v][u] != diam:
            return None, diam, dist
        if v in used:
            continue
        pairs.append(tuple(sorted((u, v))))
        used.add(u)
        used.add(v)

    if len(pairs) * 2 != G.number_of_nodes():
        return None, diam, dist
    return sorted(pairs), diam, dist


def quotient_by_pairs(G: nx.Graph, pairs):
    owner = {}
    for i, (a, b) in enumerate(pairs):
        owner[a] = i
        owner[b] = i

    Q = nx.Graph()
    Q.add_nodes_from(range(len(pairs)))

    multiplicities = defaultdict(int)
    witness = defaultdict(list)

    for u, v in G.edges():
        a = owner[u]
        b = owner[v]
        if a == b:
            continue
        x, y = sorted((a, b))
        multiplicities[(x, y)] += 1
        witness[(x, y)].append((u, v))
        Q.add_edge(x, y)

    return Q, owner, multiplicities, witness


def is_covering_projection(G: nx.Graph, Q: nx.Graph, owner):
    # For each chamber vertex u and each neighbor class of its image in Q,
    # there must be exactly one neighbor of u mapping to that class.
    for u in G.nodes():
        qu = owner[u]
        target_classes = set(Q.neighbors(qu))
        counts = {qc: 0 for qc in target_classes}
        for v in G.neighbors(u):
            qv = owner[v]
            if qv in counts:
                counts[qv] += 1
        if any(c != 1 for c in counts.values()):
            return False, u, counts
    return True, None, None


def shell_profile(G: nx.Graph, src: int):
    dist = nx.single_source_shortest_path_length(G, src)
    m = max(dist.values())
    return tuple(sum(1 for d in dist.values() if d == k) for k in range(m + 1))


def main():
    print("=" * 80)
    print("CHECK CHAMBER GRAPH AS 4-COVER OF 15-CORE")
    print("=" * 80)

    G = build_chamber_graph()

    print("CHAMBER GRAPH")
    print("-" * 80)
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("degree set:", sorted(set(dict(G.degree()).values())))
    print("triangles:", sum(nx.triangles(G).values()) // 3)
    print("diameter:", nx.diameter(G))
    print("shell profile from 0:", shell_profile(G, 0))
    print()

    pairs, diam, _ = find_antipodal_pairs(G)
    if pairs is None:
        print("No canonical antipodal pairing found.")
        return

    print("ANTIPODAL PAIRING")
    print("-" * 80)
    print("diameter used:", diam)
    print("pair count:", len(pairs))
    print("first 15 pairs:", pairs[:15])
    print()

    Q, owner, multiplicities, witness = quotient_by_pairs(G, pairs)

    print("QUOTIENT GRAPH")
    print("-" * 80)
    print("vertices:", Q.number_of_nodes())
    print("edges:", Q.number_of_edges())
    print("degree set:", sorted(set(dict(Q.degree()).values())))
    print("triangles:", sum(nx.triangles(Q).values()) // 3)
    print("diameter:", nx.diameter(Q))
    print("shell profile from 0:", shell_profile(Q, 0))
    print()

    hist = defaultdict(int)
    for m in multiplicities.values():
        hist[m] += 1

    print("EDGE MULTIPLICITY HISTOGRAM (upstairs edges over quotient edges)")
    print("-" * 80)
    for k in sorted(hist):
        print(f"{k}: {hist[k]}")
    print()

    ok, bad_u, bad_counts = is_covering_projection(G, Q, owner)
    print("COVERING TEST")
    print("-" * 80)
    print("is covering projection:", ok)
    if not ok:
        print("first failing upstairs vertex:", bad_u)
        print("neighbor-class counts:", bad_counts)
    print()

    P = nx.petersen_graph()
    LP = nx.line_graph(P)

    print("COMPARE TO L(PETERSEN)")
    print("-" * 80)
    print("same size:", Q.number_of_nodes() == LP.number_of_nodes() and Q.number_of_edges() == LP.number_of_edges())
    print("isomorphic:", nx.is_isomorphic(Q, LP))
    print()

    out = ROOT / "reports" / "true_quotients" / "check_chamber_graph_as_4cover_of_15core.txt"
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "=" * 80,
        "CHECK CHAMBER GRAPH AS 4-COVER OF 15-CORE",
        "=" * 80,
        "",
        "CHAMBER GRAPH",
        "-" * 80,
        f"vertices: {G.number_of_nodes()}",
        f"edges: {G.number_of_edges()}",
        f"degree set: {sorted(set(dict(G.degree()).values()))}",
        f"triangles: {sum(nx.triangles(G).values()) // 3}",
        f"diameter: {nx.diameter(G)}",
        f"shell profile from 0: {shell_profile(G, 0)}",
        "",
        "ANTIPODAL PAIRING",
        "-" * 80,
        f"diameter used: {diam}",
        f"pair count: {len(pairs)}",
        f"first 15 pairs: {pairs[:15]}",
        "",
        "QUOTIENT GRAPH",
        "-" * 80,
        f"vertices: {Q.number_of_nodes()}",
        f"edges: {Q.number_of_edges()}",
        f"degree set: {sorted(set(dict(Q.degree()).values()))}",
        f"triangles: {sum(nx.triangles(Q).values()) // 3}",
        f"diameter: {nx.diameter(Q)}",
        f"shell profile from 0: {shell_profile(Q, 0)}",
        "",
        "EDGE MULTIPLICITY HISTOGRAM",
        "-" * 80,
    ]
    for k in sorted(hist):
        lines.append(f"{k}: {hist[k]}")
    lines += [
        "",
        "COVERING TEST",
        "-" * 80,
        f"is covering projection: {ok}",
    ]
    if not ok:
        lines.append(f"first failing upstairs vertex: {bad_u}")
        lines.append(f"neighbor-class counts: {bad_counts}")
    lines += [
        "",
        "COMPARE TO L(PETERSEN)",
        "-" * 80,
        f"same size: {Q.number_of_nodes() == LP.number_of_nodes() and Q.number_of_edges() == LP.number_of_edges()}",
        f"isomorphic: {nx.is_isomorphic(Q, LP)}",
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"saved {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
