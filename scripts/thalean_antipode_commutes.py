#!/usr/bin/env python3

from pathlib import Path
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

ROOT = Path(__file__).resolve().parents[1]
G6_PATH = ROOT / "artifacts/census/thalion_graph.g6"


def load_graph():
    g6 = G6_PATH.read_text(encoding="utf-8").strip()
    G = nx.from_graph6_bytes(g6.encode())
    return nx.convert_node_labels_to_integers(G)


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
    G = load_graph()
    diam, a = antipode_map(G)

    print("=" * 80)
    print("THALEAN ANTIPODE COMMUTATION CHECK")
    print("=" * 80)
    print("vertices:", G.number_of_nodes())
    print("edges:", G.number_of_edges())
    print("diameter:", diam)
    print()

    gm = GraphMatcher(G, G)

    total = 0
    bad = 0
    bad_examples = []

    for phi in gm.isomorphisms_iter():
        total += 1
        ok = True
        for v in G.nodes():
            lhs = phi[a[v]]
            rhs = a[phi[v]]
            if lhs != rhs:
                ok = False
                if len(bad_examples) < 5:
                    bad_examples.append({
                        "v": v,
                        "phi(v)": phi[v],
                        "phi(a(v))": lhs,
                        "a(phi(v))": rhs
                    })
                break
        if not ok:
            bad += 1

    print("automorphisms checked:", total)
    print("commuting failures   :", bad)
    print()

    if bad_examples:
        print("SAMPLE FAILURES")
        print("-" * 80)
        for ex in bad_examples:
            print(ex)
        print()

    print("INTERPRETATION")
    print("-" * 80)
    if bad == 0:
        print("The antipode map commutes with every automorphism.")
        print("So the antipodal pairing is a canonical symmetry of the Thalean graph.")
    else:
        print("The antipode map does not commute with every automorphism.")
        print("So the antipodal pairing is not fully canonical under Aut(G).")


if __name__ == "__main__":
    main()
