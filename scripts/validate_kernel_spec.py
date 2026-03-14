#!/usr/bin/env python3

import json
import sys
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SPEC = ROOT / "spec" / "hyperxi_kernel.v2.json"

sys.path.insert(0, str(SRC))

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


def build_chamber_graph():
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


def antipodal_pairs(G):
    dist = dict(nx.all_pairs_shortest_path_length(G))
    diam = nx.diameter(G)

    pairs = []
    used = set()

    for u in G.nodes():
        if u in used:
            continue

        far = [v for v, d in dist[u].items() if d == diam]

        if len(far) == 1:
            v = far[0]
            pairs.append((u, v))
            used.add(u)
            used.add(v)

    return pairs


def quotient_graph(G, pairs):
    owner = {}

    for i, (a, b) in enumerate(pairs):
        owner[a] = i
        owner[b] = i

    Q = nx.Graph()
    Q.add_nodes_from(range(len(pairs)))

    for u, v in G.edges():
        a = owner[u]
        b = owner[v]

        if a != b:
            Q.add_edge(a, b)

    return Q


def load_spec():
    with open(SPEC, "r") as f:
        return json.load(f)


def check_invariants(name, G, expected):
    ok = True

    v = G.number_of_nodes()
    e = G.number_of_edges()
    deg = sorted(set(dict(G.degree()).values()))

    if v != expected["vertex_count"]:
        print(f"[FAIL] {name} vertex count: {v} != {expected['vertex_count']}")
        ok = False

    if e != expected["edge_count"]:
        print(f"[FAIL] {name} edge count: {e} != {expected['edge_count']}")
        ok = False

    if deg != expected["degree_set"]:
        print(f"[FAIL] {name} degree set: {deg} != {expected['degree_set']}")
        ok = False

    if ok:
        print(f"[OK] {name} invariants match spec")

    return ok


def main():
    print("=" * 70)
    print("VALIDATE HYPERXI KERNEL SPEC")
    print("=" * 70)

    spec = load_spec()

    G60 = build_chamber_graph()

    print("\nChecking G60")

    check_invariants("G60", G60, spec["invariants"]["G60"])

    pairs60 = antipodal_pairs(G60)
    G30 = quotient_graph(G60, pairs60)

    print("\nChecking G30")

    check_invariants("G30", G30, spec["invariants"]["G30"])

    pairs30 = antipodal_pairs(G30)
    G15 = quotient_graph(G30, pairs30)

    print("\nChecking G15")

    check_invariants("G15", G15, spec["invariants"]["G15"])

    P = nx.petersen_graph()
    LP = nx.line_graph(P)

    print("\nPetersen identification")

    if nx.is_isomorphic(G15, LP):
        print("[OK] G15 ≅ L(Petersen)")
    else:
        print("[FAIL] G15 is not L(Petersen)")

    print("\nValidation complete.")


if __name__ == "__main__":
    main()
