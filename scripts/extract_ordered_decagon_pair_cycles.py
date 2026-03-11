from __future__ import annotations

from collections import defaultdict
from typing import Callable, Dict, List, Tuple

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


# ---------------------------------------------------------------------
# Chamber adapter
# ---------------------------------------------------------------------

def load_chamber_data():
    """
    Returns:
        states : list[Flag]
        S      : function(Flag) -> Flag
        V      : function(Flag) -> Flag
    """
    fm = FlagModel()
    gens = CoxeterGenerators(fm)

    states = list(fm.flags)
    return states, gens.S, gens.V


# ---------------------------------------------------------------------
# Orbit utilities
# ---------------------------------------------------------------------

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


def cyclic_dist(n, i, j):
    d = abs(i - j)
    return min(d, n - d)


def positions_in_cycle(cycle, items):
    pos = {x: i for i, x in enumerate(cycle)}
    return [pos[x] for x in items]


# ---------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------

def main():
    states, S, V = load_chamber_data()

    states = list(states)

    # ----------------------------------------------------------
    # S-pairs
    # ----------------------------------------------------------

    s_orbits = permutation_orbits(states, S)

    if not all(len(o) == 2 for o in s_orbits):
        raise RuntimeError("S does not produce only 2-cycles")

    s_pairs = [tuple(o) for o in s_orbits]
    state_to_pair = build_state_to_pair_id(s_pairs)

    # ----------------------------------------------------------
    # SV-decagons
    # ----------------------------------------------------------

    SV = compose(V, S)
    sv_orbits = permutation_orbits(states, SV)

    if not all(len(o) == 10 for o in sv_orbits):
        bad = [len(o) for o in sv_orbits if len(o) != 10]
        raise RuntimeError(f"SV cycles not length 10: {bad}")

    # ----------------------------------------------------------
    # Convert ordered decagons to pair IDs
    # ----------------------------------------------------------

    pair_cycles = {}

    for did, orbit in enumerate(sv_orbits):
        pair_cycle = [state_to_pair[s] for s in orbit]

        if len(set(pair_cycle)) != 10:
            raise RuntimeError("Decagon does not hit 10 distinct S-pairs")

        pair_cycles[did] = pair_cycle

    # ----------------------------------------------------------
    # Pair intersections
    # ----------------------------------------------------------

    pair_sets = {d: set(c) for d, c in pair_cycles.items()}

    intersections = {}

    decs = sorted(pair_cycles)

    for i_idx, i in enumerate(decs):
        for j in decs[i_idx + 1:]:
            shared = sorted(pair_sets[i] & pair_sets[j])
            if shared:
                intersections[(i, j)] = shared

    # ----------------------------------------------------------
    # Output
    # ----------------------------------------------------------

    print("=" * 80)
    print("ORDERED DECAGON PAIR CYCLES")
    print("=" * 80)

    print("states:", len(states))
    print("S-pairs:", len(s_pairs))
    print("SV-decagons:", len(pair_cycles))
    print()

    print("=" * 80)
    print("ORDERED SV-DECAGONS (PAIR IDS)")
    print("=" * 80)

    for d in sorted(pair_cycles):
        print(f"decagon {d:2d}:", pair_cycles[d])

    print()
    print("=" * 80)
    print("EDGE FIBER POSITIONS")
    print("=" * 80)

    spacing_counter = defaultdict(int)

    for (i, j), shared in sorted(intersections.items()):

        ci = pair_cycles[i]
        cj = pair_cycles[j]

        pi = positions_in_cycle(ci, shared)
        pj = positions_in_cycle(cj, shared)

        si = cyclic_dist(10, pi[0], pi[1])
        sj = cyclic_dist(10, pj[0], pj[1])

        spacing_counter[(si, sj)] += 1

        print(f"edge ({i:2d},{j:2d}) shared {shared}")
        print(f"  decagon {i:2d} positions {pi} spacing {si}")
        print(f"  decagon {j:2d} positions {pj} spacing {sj}")

    print()
    print("=" * 80)
    print("SPACING SUMMARY")
    print("=" * 80)

    for k in sorted(spacing_counter):
        print(k, ":", spacing_counter[k])

    print()
    print("expected simple edges:", len(intersections))


if __name__ == "__main__":
    main()
