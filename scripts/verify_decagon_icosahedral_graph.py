from __future__ import annotations

import numpy as np
from collections import defaultdict

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


def permutation_orbits(states, op):
    seen = set()
    orbits = []

    for s in states:
        if s in seen:
            continue

        orbit = []
        x = s
        while x not in seen:
            seen.add(x)
            orbit.append(x)
            x = op(x)

        orbits.append(orbit)

    return orbits


def compose(f, g):
    return lambda x: f(g(x))


def build_state_to_pair_id(s_pairs):
    out = {}
    for pid, (a, b) in enumerate(s_pairs):
        out[a] = pid
        out[b] = pid
    return out


def main():

    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    states = list(fm.flags)

    S = gen.S
    V = gen.V

    # ----------------------------------
    # S pairs
    # ----------------------------------

    s_orbits = permutation_orbits(states, S)
    s_pairs = [tuple(o) for o in s_orbits]

    state_to_pair = build_state_to_pair_id(s_pairs)

    # ----------------------------------
    # SV decagons
    # ----------------------------------

    SV = compose(V, S)

    sv_orbits = permutation_orbits(states, SV)

    decagons = []

    for orbit in sv_orbits:
        decagons.append([state_to_pair[s] for s in orbit])

    pair_sets = {i: set(c) for i, c in enumerate(decagons)}

    # ----------------------------------
    # intersection graph
    # ----------------------------------

    edges = []

    for i in range(len(decagons)):
        for j in range(i + 1, len(decagons)):

            shared = pair_sets[i] & pair_sets[j]

            if shared:
                edges.append((i, j))

    # ----------------------------------
    # adjacency matrix
    # ----------------------------------

    n = 12
    A = np.zeros((n, n))

    for i, j in edges:
        A[i, j] = 1
        A[j, i] = 1

    degrees = A.sum(axis=1)

    print("=" * 80)
    print("DECAHEDRAL INTERSECTION GRAPH")
    print("=" * 80)

    print("vertices:", n)
    print("edges:", len(edges))
    print("degree sequence:", list(degrees.astype(int)))

    # ----------------------------------
    # spectrum
    # ----------------------------------

    eigvals = np.linalg.eigvals(A)
    eigvals = sorted(np.real_if_close(eigvals), reverse=True)

    print()
    print("adjacency eigenvalues:")
    for v in eigvals:
        print(round(v, 6))

    print()
    print("Expected icosahedral spectrum:")
    print("5, sqrt(5)^3, -sqrt(5)^3, -3")


if __name__ == "__main__":
    main()
