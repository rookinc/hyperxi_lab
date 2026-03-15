#!/usr/bin/env python3

import networkx as nx

from load_thalean_graph import load_spec, build_graph


def quotient_by_pairs(G, pair_map):
    seen = set()
    classes = []
    owner = {}

    for v in sorted(G.nodes()):
        if v in seen:
            continue
        pair = tuple(sorted((v, pair_map[v])))
        seen.update(pair)
        idx = len(classes)
        classes.append(pair)
        for x in pair:
            owner[x] = idx

    Q = nx.Graph()
    Q.add_nodes_from(range(len(classes)))

    for u, v in G.edges():
        a, b = owner[u], owner[v]
        if a != b:
            Q.add_edge(a, b)

    return Q, classes, owner


def unique_distance_partner_map(G):
    dist = dict(nx.all_pairs_shortest_path_length(G))
    diam = nx.diameter(G)
    out = {}
    for v in G.nodes():
        far = [u for u, d in dist[v].items() if d == diam]
        if len(far) != 1:
            raise RuntimeError(
                f"vertex {v} has {len(far)} distance-{diam} partners"
            )
        out[v] = far[0]
    return out, diam


def check_automorphism(G, phi):
    if len(set(phi.values())) != G.number_of_nodes():
        return False
    for u, v in G.edges():
        if not G.has_edge(phi[u], phi[v]):
            return False
    return True


def main():
    print("=" * 80)
    print("SEARCH LIFT OF SECOND INVOLUTION")
    print("=" * 80)

    G60 = build_graph(load_spec())

    a60, diam60 = unique_distance_partner_map(G60)
    G30, classes30, owner30 = quotient_by_pairs(G60, a60)
    b30, diam30 = unique_distance_partner_map(G30)

    print("G60 vertices:", G60.number_of_nodes())
    print("G30 vertices:", G30.number_of_nodes())
    print("diam(T):", diam60)
    print("diam(G30):", diam30)
    print()

    fiber30_to_vertices60 = {}
    for v60, c30 in owner30.items():
        fiber30_to_vertices60.setdefault(c30, []).append(v60)
    for c in fiber30_to_vertices60:
        fiber30_to_vertices60[c] = sorted(fiber30_to_vertices60[c])

    # We choose one bit per 30-fiber orbit of b30.
    # If c < b30[c], then choosing bit=0 means:
    #   first vertex in fiber c maps to first vertex in fiber b30[c]
    #   second maps to second
    # bit=1 swaps them.
    pairs30 = []
    seen = set()
    for c in sorted(G30.nodes()):
        if c in seen:
            continue
        d = b30[c]
        if c == d:
            raise RuntimeError("b30 has a fixed point unexpectedly")
        pairs30.append((c, d) if c < d else (d, c))
        seen.add(c)
        seen.add(d)
    pairs30 = sorted(set(pairs30))

    print("b30 orbit pairs:", pairs30)
    print("search space size:", 2 ** len(pairs30))
    print()

    solutions = []

    for mask in range(2 ** len(pairs30)):
        phi = {}

        for i, (c, d) in enumerate(pairs30):
            Fc = fiber30_to_vertices60[c]
            Fd = fiber30_to_vertices60[d]

            bit = (mask >> i) & 1
            if bit == 0:
                phi[Fc[0]] = Fd[0]
                phi[Fc[1]] = Fd[1]
                phi[Fd[0]] = Fc[0]
                phi[Fd[1]] = Fc[1]
            else:
                phi[Fc[0]] = Fd[1]
                phi[Fc[1]] = Fd[0]
                phi[Fd[0]] = Fc[1]
                phi[Fd[1]] = Fc[0]

        # involution
        if not all(phi[phi[v]] == v for v in G60.nodes()):
            continue

        # lifts b30
        if not all(owner30[phi[v]] == b30[owner30[v]] for v in G60.nodes()):
            continue

        # automorphism
        if not check_automorphism(G60, phi):
            continue

        commute_with_a = all(a60[phi[v]] == phi[a60[v]] for v in G60.nodes())

        solutions.append((mask, commute_with_a, phi))

    print("valid lifted involutions found:", len(solutions))

    if not solutions:
        print("No lifted involution of b30 exists as an automorphism of T.")
        return

    commuting = [s for s in solutions if s[1]]
    print("commuting with a:", len(commuting))
    print()

    for idx, (mask, commute, phi) in enumerate(solutions[:10], start=1):
        print(f"solution {idx}: mask={mask}, commute_with_a={commute}")

    if commuting:
        print()
        print("CONCLUSION")
        print("-" * 80)
        print("A lifted involution exists and commutes with the antipode a.")
        print("This is strong evidence for a Z2 x Z2 fiber action on T.")
    else:
        print()
        print("CONCLUSION")
        print("-" * 80)
        print("Lifted involutions exist, but none commute with a.")
        print("So the structure is not a simple Z2 x Z2 action.")

if __name__ == "__main__":
    main()
