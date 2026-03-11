from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple


# Ordered SV-decagons in chamber-state labels.
# Fill these from the actual ordered SV orbit output of your simulator.
#
# Each entry must be a cyclic orbit of 10 chamber-state IDs.
#
# Example shape only:
# DECAGON_STATES = {
#     0:  [ ... 10 chamber states in SV order ... ],
#     1:  [ ... ],
#     ...
#     11: [ ... ],
# }
DECAGON_STATES: Dict[int, List[int]] = {
    # TODO: paste the 12 ordered SV-decagons here
}


# S-pair partition on the 120 chamber states.
# Fill this from your actual S decomposition.
#
# Example shape only:
# S_PAIRS = [
#     (0, 1),
#     (2, 3),
#     ...
# ]
S_PAIRS: List[Tuple[int, int]] = [
    # TODO: paste the 60 S-pairs here
]


def build_state_to_pair_id(s_pairs: List[Tuple[int, int]]) -> Dict[int, int]:
    state_to_pair: Dict[int, int] = {}
    for pair_id, (a, b) in enumerate(s_pairs):
        if a in state_to_pair or b in state_to_pair:
            raise ValueError(f"State reused across S-pairs in pair_id={pair_id}")
        state_to_pair[a] = pair_id
        state_to_pair[b] = pair_id
    return state_to_pair


def ordered_pair_cycles(
    decagon_states: Dict[int, List[int]],
    state_to_pair: Dict[int, int],
) -> Dict[int, List[int]]:
    out: Dict[int, List[int]] = {}
    for d, orbit in sorted(decagon_states.items()):
        if len(orbit) != 10:
            raise ValueError(f"Decagon {d} does not have length 10")
        pair_cycle = [state_to_pair[s] for s in orbit]
        if len(set(pair_cycle)) != 10:
            raise ValueError(
                f"Decagon {d} does not map to 10 distinct S-pairs: {pair_cycle}"
            )
        out[d] = pair_cycle
    return out


def pair_sets_from_cycles(pair_cycles: Dict[int, List[int]]) -> Dict[int, set[int]]:
    return {d: set(cycle) for d, cycle in pair_cycles.items()}


def cyclic_dist(n: int, i: int, j: int) -> int:
    d = abs(i - j)
    return min(d, n - d)


def build_intersections(
    pair_cycles: Dict[int, List[int]]
) -> Dict[Tuple[int, int], List[int]]:
    pair_sets = pair_sets_from_cycles(pair_cycles)
    out: Dict[Tuple[int, int], List[int]] = {}
    decagons = sorted(pair_cycles)
    for ix, i in enumerate(decagons):
        for j in decagons[ix + 1:]:
            shared = sorted(pair_sets[i] & pair_sets[j])
            if shared:
                out[(i, j)] = shared
    return out


def positions_in_cycle(cycle: List[int], items: List[int]) -> List[int]:
    pos = {x: idx for idx, x in enumerate(cycle)}
    return [pos[x] for x in items]


def normalize_two_positions(n: int, pos: List[int]) -> Tuple[int, int, int]:
    a, b = sorted(pos)
    spacing = cyclic_dist(n, a, b)
    return (a, b, spacing)


def rotation_reversal_class(n: int, pos: List[int]) -> Tuple[int]:
    # For two points on a cycle, the only invariant under dihedral symmetry
    # is their cyclic spacing.
    return (cyclic_dist(n, pos[0], pos[1]),)


def main() -> None:
    if not DECAGON_STATES:
        print("=" * 80)
        print("ORDERED DECAGON PAIR CYCLES")
        print("=" * 80)
        print("No data loaded.")
        print()
        print("Populate these constants in the script:")
        print("  - DECAGON_STATES : ordered chamber-state cycles for the 12 SV-decagons")
        print("  - S_PAIRS        : the 60 S-pairs on the 120 chamber states")
        print()
        print("Then run:")
        print("  python3 scripts/ordered_decagon_pair_cycles.py | tee ordered_decagon_pair_cycles.txt")
        return

    state_to_pair = build_state_to_pair_id(S_PAIRS)
    pair_cycles = ordered_pair_cycles(DECAGON_STATES, state_to_pair)
    intersections = build_intersections(pair_cycles)

    print("=" * 80)
    print("ORDERED DECAGON PAIR CYCLES")
    print("=" * 80)
    print(f"decagons loaded: {len(pair_cycles)}")
    print(f"S-pairs loaded:  {len(S_PAIRS)}")
    print()

    print("=" * 80)
    print("ORDERED 10-CYCLES OF S-PAIR IDS")
    print("=" * 80)
    for d, cycle in sorted(pair_cycles.items()):
        print(f"decagon {d:2d}: {cycle}")

    print()
    print("=" * 80)
    print("ADJACENT DECAGON EDGE-FIBERS INSIDE ORDERED CYCLES")
    print("=" * 80)

    spacing_counter = defaultdict(int)
    edge_records = []

    for (i, j), shared in sorted(intersections.items()):
        ci = pair_cycles[i]
        cj = pair_cycles[j]

        pos_i = positions_in_cycle(ci, shared)
        pos_j = positions_in_cycle(cj, shared)

        norm_i = normalize_two_positions(len(ci), pos_i)
        norm_j = normalize_two_positions(len(cj), pos_j)

        cls_i = rotation_reversal_class(len(ci), pos_i)
        cls_j = rotation_reversal_class(len(cj), pos_j)

        spacing_counter[norm_i[2]] += 1
        edge_records.append((i, j, shared, pos_i, pos_j, norm_i, norm_j, cls_i, cls_j))

        print(f"edge ({i:2d}, {j:2d}) -> shared pairs {shared}")
        print(f"  decagon {i:2d} positions: {pos_i} | normalized={norm_i} | class={cls_i}")
        print(f"  decagon {j:2d} positions: {pos_j} | normalized={norm_j} | class={cls_j}")

    print()
    print("=" * 80)
    print("SPACING SUMMARY")
    print("=" * 80)
    for spacing in sorted(spacing_counter):
        print(f"cyclic spacing {spacing}: {spacing_counter[spacing]} edges")

    uniform_spacing = len(spacing_counter) == 1
    print()
    print(f"uniform spacing pattern across all 30 adjacency edges: {uniform_spacing}")

    same_local_class = all(rec[7] == rec[8] for rec in edge_records)
    print(f"same dihedral class on both sides of every edge:      {same_local_class}")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("Each adjacent decagon pair shares exactly two S-pairs, forming a 2-element")
    print("fiber over an edge of the icosahedral base graph.")
    print("This script locates those two pair IDs inside the ordered 10-cycle of each")
    print("decagon, so we can test whether the local fiber sits in a uniform cyclic")
    print("configuration across all edges.")
    print()
    print("If a uniform spacing pattern exists, that is strong evidence that the")
    print("2-fold edge fiber is geometrically rigid inside the Petrie decagon cycles.")
    print("That ordered local data is the input needed for a true monodromy test.")


if __name__ == "__main__":
    main()
