#!/usr/bin/env python3

from pathlib import Path
import re
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
G6_PATH = ROOT / "artifacts/census/thalion_graph.g6"
SIGN_PATH = ROOT / "artifacts/reports/recovered_signing.txt"


def load_graph():
    g6 = G6_PATH.read_text(encoding="utf-8").strip()
    G = nx.from_graph6_bytes(g6.encode())
    return nx.convert_node_labels_to_integers(G)


def load_signing():
    signs = {}
    pat = re.compile(r"^\s*(\d+)-\s*(\d+)\s+sign=([+-]1)\b")
    for line in SIGN_PATH.read_text(encoding="utf-8").splitlines():
        m = pat.match(line)
        if not m:
            continue
        u = int(m.group(1))
        v = int(m.group(2))
        s = 1 if m.group(3) == "+1" else -1
        signs[tuple(sorted((u, v)))] = s
    return signs


def build_lift_from_signs(base, signs):
    L = nx.Graph()
    idx = {}
    rev = {}
    k = 0
    for v in sorted(base.nodes()):
        for sheet in (0, 1):
            idx[(v, sheet)] = k
            rev[k] = (v, sheet)
            L.add_node(k)
            k += 1

    for u, v in base.edges():
        sign = signs[tuple(sorted((u, v)))]
        for s in (0, 1):
            t = s if sign == 1 else 1 - s
            L.add_edge(idx[(u, s)], idx[(v, t)])
    return L, idx, rev


def antipode_map(G):
    diam = nx.diameter(G)
    dists = dict(nx.all_pairs_shortest_path_length(G))
    amap = {}
    for v in G.nodes():
        far = [u for u, d in dists[v].items() if d == diam]
        if len(far) != 1:
            raise ValueError(f"vertex {v} has {len(far)} distance-{diam} partners")
        amap[v] = far[0]
    return diam, amap


def main():
    signs = load_signing()

    print("=" * 80)
    print("THALEAN ANTIPODE VS SHEET CHECK")
    print("=" * 80)
    print("sign file:", SIGN_PATH)
    print("signed edges loaded:", len(signs))
    print()

    base = nx.Graph()
    for u, v in signs:
        base.add_edge(u, v)

    print("base vertices:", base.number_of_nodes())
    print("base edges:", base.number_of_edges())
    print("base degree set:", sorted(set(dict(base.degree()).values())))
    print()

    lift, idx, rev = build_lift_from_signs(base, signs)

    print("lift vertices:", lift.number_of_nodes())
    print("lift edges:", lift.number_of_edges())
    print("lift degree set:", sorted(set(dict(lift.degree()).values())))
    print()

    diam, amap = antipode_map(lift)
    print("lift diameter:", diam)
    print()

    same_base_flip_sheet = 0
    same_base_same_sheet = 0
    different_base = 0

    examples_flip = []
    examples_diff = []

    for x in sorted(lift.nodes()):
        v, s = rev[x]
        y = amap[x]
        w, t = rev[y]

        if v == w and s != t:
            same_base_flip_sheet += 1
            if len(examples_flip) < 10:
                examples_flip.append((x, (v, s), y, (w, t)))
        elif v == w and s == t:
            same_base_same_sheet += 1
        else:
            different_base += 1
            if len(examples_diff) < 10:
                examples_diff.append((x, (v, s), y, (w, t)))

    print("ANTIPODE RELATION COUNTS")
    print("-" * 80)
    print("same base, opposite sheet:", same_base_flip_sheet)
    print("same base, same sheet    :", same_base_same_sheet)
    print("different base vertex    :", different_base)
    print()

    print("SAMPLE same-base opposite-sheet matches")
    print("-" * 80)
    for row in examples_flip:
        print(row)
    print()

    print("SAMPLE different-base matches")
    print("-" * 80)
    for row in examples_diff:
        print(row)
    print()

    print("INTERPRETATION")
    print("-" * 80)
    if same_base_flip_sheet == lift.number_of_nodes():
        print("The distance-diameter antipode map is exactly sheet inversion at fixed base vertex.")
    elif different_base == lift.number_of_nodes():
        print("The antipode map never acts as pure sheet inversion; it always moves to a different base vertex.")
    else:
        print("The antipode map mixes base motion and sheet inversion.")
        print("It is not identical to pure sheet inversion.")


if __name__ == "__main__":
    main()
