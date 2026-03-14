#!/usr/bin/env python3

import itertools
import networkx as nx

from load_thalean_graph import load_spec, build_graph


def load_thalean_graph():
    spec = load_spec()
    return build_graph(spec)


def compute_antipode_map(G):
    """Return dict v -> antipode(v) using distance-6 property."""
    lengths = dict(nx.all_pairs_shortest_path_length(G))

    antipode = {}
    for v in G.nodes():
        far = [u for u, d in lengths[v].items() if d == 6]
        if len(far) != 1:
            raise RuntimeError(f"Vertex {v} has {len(far)} distance-6 partners")
        antipode[v] = far[0]

    return antipode


def build_generators(G):
    """
    Build crude adjacency generators from the sorted neighbor list.
    This is only a first probe for whether a short local word can realize
    the antipode map.
    """
    gens = {}
    nodes = sorted(G.nodes())

    for i in range(4):
        mapping = {}
        for v in nodes:
            neigh = sorted(G.neighbors(v))
            mapping[v] = neigh[i]
        gens[f"g{i}"] = mapping

    return gens


def compose(a, b):
    """Compose maps a∘b."""
    return {k: a[b[k]] for k in b}


def is_antipode(mapping, antipode):
    return all(mapping[v] == antipode[v] for v in mapping)


def main():
    print("=" * 80)
    print("THALEAN ANTIPODE WORD SEARCH")
    print("=" * 80)

    G = load_thalean_graph()
    antipode = compute_antipode_map(G)
    gens = build_generators(G)
    names = list(gens.keys())

    print(f"vertices: {G.number_of_nodes()}")
    print(f"edges: {G.number_of_edges()}")
    print(f"generators: {names}")

    max_len = 6
    found = []

    for L in range(1, max_len + 1):
        print(f"\nsearching words of length {L}")

        for word in itertools.product(names, repeat=L):
            perm = gens[word[0]]
            for w in word[1:]:
                perm = compose(gens[w], perm)

            if is_antipode(perm, antipode):
                found.append(word)
                print("FOUND:", word)

    print("\n" + "-" * 80)
    if not found:
        print(f"No generator word matched the antipode map up to length {max_len}.")
    else:
        print("Words matching antipode map:")
        for w in found:
            print(" ", w)


if __name__ == "__main__":
    main()
