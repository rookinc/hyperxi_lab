#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from collections import Counter, defaultdict
from dataclasses import dataclass

import networkx as nx


@dataclass(frozen=True)
class EdgeRef:
    u: int
    v: int

    def norm(self) -> tuple[int, int]:
        return tuple(sorted((self.u, self.v)))


def petersen_graph() -> nx.Graph:
    return nx.petersen_graph()


def base_graph() -> nx.Graph:
    # 15-vertex base graph
    return nx.line_graph(petersen_graph())


def relabel_base_to_ints(G: nx.Graph) -> tuple[nx.Graph, dict[int, tuple[int, int]], dict[tuple[int, int], int]]:
    nodes = sorted(tuple(sorted(x)) for x in G.nodes())
    edge_to_id = {n: i for i, n in enumerate(nodes)}
    id_to_edge = {i: n for n, i in edge_to_id.items()}
    H = nx.Graph()
    H.add_nodes_from(range(len(nodes)))
    for a, b in G.edges():
        ia = edge_to_id[tuple(sorted(a))]
        ib = edge_to_id[tuple(sorted(b))]
        H.add_edge(ia, ib)
    return H, id_to_edge, edge_to_id


def sorted_edges(G: nx.Graph) -> list[tuple[int, int]]:
    return [tuple(sorted(e)) for e in sorted(tuple(sorted(e)) for e in G.edges())]


def all_cycles_basis(G: nx.Graph) -> list[list[int]]:
    return nx.cycle_basis(G)


def cycle_edge_parity(cycle: list[int], signing: dict[tuple[int, int], int]) -> int:
    prod = 1
    m = len(cycle)
    for i in range(m):
        a = cycle[i]
        b = cycle[(i + 1) % m]
        prod *= signing[tuple(sorted((a, b)))]
    return prod


def signing_from_mask(edges: list[tuple[int, int]], mask: int) -> dict[tuple[int, int], int]:
    # 1 bit => negative edge, 0 bit => positive edge
    out = {}
    for i, e in enumerate(edges):
        out[e] = -1 if ((mask >> i) & 1) else 1
    return out


def switching_signature(G: nx.Graph, signing: dict[tuple[int, int], int], switch_bits: int) -> dict[tuple[int, int], int]:
    sw = {v: -1 if ((switch_bits >> v) & 1) else 1 for v in G.nodes()}
    out = {}
    for u, v in G.edges():
        e = tuple(sorted((u, v)))
        out[e] = sw[u] * signing[e] * sw[v]
    return out


def canonical_switch_class(G: nx.Graph, signing: dict[tuple[int, int], int], edges: list[tuple[int, int]]) -> tuple[int, ...]:
    best = None
    n = G.number_of_nodes()
    # gauge-fix vertex 0 to cut switching search in half
    for bits in range(1 << (n - 1)):
        switched = switching_signature(G, signing, bits)
        sig = tuple(switched[e] for e in edges)
        if best is None or sig < best:
            best = sig
    return best


def signed_2_lift(G: nx.Graph, signing: dict[tuple[int, int], int]) -> nx.Graph:
    H = nx.Graph()
    for v in G.nodes():
        H.add_node((v, 0))
        H.add_node((v, 1))
    for u, v in G.edges():
        e = tuple(sorted((u, v)))
        s = signing[e]
        if s == 1:
            H.add_edge((u, 0), (v, 0))
            H.add_edge((u, 1), (v, 1))
        else:
            H.add_edge((u, 0), (v, 1))
            H.add_edge((u, 1), (v, 0))
    return H


def wl_hash(G: nx.Graph) -> str:
    return nx.weisfeiler_lehman_graph_hash(G)


def automorphism_orbit_representatives(G: nx.Graph) -> list[dict[int, int]]:
    # For a first pass, use GraphMatcher automorphisms.
    # Petersen line graph is small enough that this is workable.
    gm = nx.algorithms.isomorphism.GraphMatcher(G, G)
    seen = set()
    reps = []
    for iso in gm.isomorphisms_iter():
        frozen = tuple(iso[i] for i in sorted(G.nodes()))
        if frozen not in seen:
            seen.add(frozen)
            reps.append(iso.copy())
    return reps


def apply_automorphism_to_signing(
    signing: dict[tuple[int, int], int],
    automorphism: dict[int, int],
) -> dict[tuple[int, int], int]:
    out = {}
    for (u, v), s in signing.items():
        e2 = tuple(sorted((automorphism[u], automorphism[v])))
        out[e2] = s
    return out


def canonical_full_orbit(
    G: nx.Graph,
    signing: dict[tuple[int, int], int],
    edges: list[tuple[int, int]],
    autos: list[dict[int, int]],
) -> tuple[int, ...]:
    best = None
    for auto in autos:
        moved = apply_automorphism_to_signing(signing, auto)
        rep = canonical_switch_class(G, moved, edges)
        if best is None or rep < best:
            best = rep
    return best


def main() -> None:
    G0 = base_graph()
    G, id_to_edge, edge_to_id = relabel_base_to_ints(G0)
    edges = sorted_edges(G)
    cycle_basis = all_cycles_basis(G)

    print("=" * 80)
    print("SIGNING RIGIDITY TEST ON L(PETERSEN)")
    print("=" * 80)
    print(f"vertices: {G.number_of_nodes()}")
    print(f"edges:    {G.number_of_edges()}")
    print(f"beta_1:   {G.number_of_edges() - G.number_of_nodes() + 1}")
    print(f"cycle basis size: {len(cycle_basis)}")
    print()

    print("Computing automorphism group representatives...")
    autos = automorphism_orbit_representatives(G)
    print(f"automorphisms found: {len(autos)}")
    print()

    # First pass:
    # examine all signings with exactly 14 negative / 16 positive edges
    # and bucket by:
    #   1) cycle-basis parity signature
    #   2) switch class
    #   3) switch+automorphism orbit
    #   4) 2-lift WL hash
    #
    # This is 30 choose 14 = 145,422,675, so too large to brute force in one shot.
    # Instead sample masks deterministically at first.
    #
    # You can later replace this with an admissible-signing generator from transport.
    SAMPLE_LIMIT = 200000

    neg_target = 14
    print(f"sampling signings with exactly {neg_target} negative edges")
    print(f"sample limit: {SAMPLE_LIMIT}")
    print()

    cycle_parity_counter = Counter()
    switch_class_counter = Counter()
    orbit_counter = Counter()
    lift_hash_counter = Counter()

    examined = 0
    kept = 0

    for neg_edges in itertools.combinations(range(len(edges)), neg_target):
        mask = 0
        for i in neg_edges:
            mask |= (1 << i)

        signing = signing_from_mask(edges, mask)

        # record cycle basis parity pattern
        parity_sig = tuple(cycle_edge_parity(c, signing) for c in cycle_basis)
        cycle_parity_counter[parity_sig] += 1

        switch_rep = canonical_switch_class(G, signing, edges)
        switch_class_counter[switch_rep] += 1

        orbit_rep = canonical_full_orbit(G, signing, edges, autos)
        orbit_counter[orbit_rep] += 1

        H = signed_2_lift(G, signing)
        lift_hash_counter[wl_hash(H)] += 1

        examined += 1
        kept += 1
        if kept >= SAMPLE_LIMIT:
            break
        if examined % 1000 == 0:
            print(f"... examined {examined}")

    summary = {
        "vertices": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "beta_1": G.number_of_edges() - G.number_of_nodes() + 1,
        "cycle_basis_size": len(cycle_basis),
        "automorphisms_found": len(autos),
        "negative_target": neg_target,
        "sample_limit": SAMPLE_LIMIT,
        "examined": examined,
        "distinct_cycle_parity_signatures": len(cycle_parity_counter),
        "distinct_switch_classes": len(switch_class_counter),
        "distinct_switch_plus_aut_classes": len(orbit_counter),
        "distinct_2lift_hashes": len(lift_hash_counter),
        "top_lift_hashes": lift_hash_counter.most_common(10),
    }

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for k, v in summary.items():
        print(f"{k}: {v}")

    with open("reports/rigidity/test_signing_rigidity_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    with open("reports/rigidity/test_signing_rigidity_top_hashes.json", "w", encoding="utf-8") as f:
        json.dump(dict(lift_hash_counter.most_common(50)), f, indent=2)


if __name__ == "__main__":
    main()
