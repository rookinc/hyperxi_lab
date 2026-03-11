from __future__ import annotations

from pathlib import Path
import ast
from collections import defaultdict, deque

DECAGON_FILE = Path("artifacts/cycles/ordered_decagon_pair_cycles.txt")


def load_decagons(path: Path) -> list[tuple[int, ...]]:
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line.startswith("decagon") or ":" not in line:
            continue
        payload = line.split(":", 1)[1].strip()
        obj = ast.literal_eval(payload)
        if isinstance(obj, list) and len(obj) == 10:
            out.append(tuple(int(x) for x in obj))
    return out


def build_intersection_data(decagons: list[tuple[int, ...]]):
    pair_shared: dict[tuple[int, int], list[int]] = {}
    state_to_blocks: dict[int, list[int]] = defaultdict(list)

    for d_idx, cyc in enumerate(decagons):
        for x in cyc:
            state_to_blocks[x].append(d_idx)

    # shared states by decagon pair
    for state, blocks in state_to_blocks.items():
        if len(blocks) != 2:
            raise ValueError(f"state {state} lies on {len(blocks)} decagons, expected 2")
        a, b = sorted(blocks)
        pair_shared.setdefault((a, b), []).append(state)

    # sanity: every intersecting pair shares exactly 2 states
    for k, v in pair_shared.items():
        if len(v) != 2:
            raise ValueError(f"pair {k} shares {len(v)} states, expected 2")

    return pair_shared, state_to_blocks


def local_neighbor_cycle(decagons: list[tuple[int, ...]], pair_shared: dict[tuple[int, int], list[int]]):
    """
    For each decagon D, return the cyclic order of its 5 neighboring decagons.
    If D = (x0,...,x9), each neighbor should occur at opposite positions i and i+5.
    """
    neighbor_cycles: dict[int, list[int]] = {}

    for d_idx, cyc in enumerate(decagons):
        pos = {x: i for i, x in enumerate(cyc)}
        neighbors_at_slot = [None] * 5

        # find all neighbors of d_idx
        neighs = []
        for (a, b), shared in pair_shared.items():
            if a == d_idx:
                other = b
            elif b == d_idx:
                other = a
            else:
                continue
            neighs.append((other, shared))

        if len(neighs) != 5:
            raise ValueError(f"decagon {d_idx} has {len(neighs)} neighbors, expected 5")

        for other, shared in neighs:
            i, j = sorted(pos[x] for x in shared)
            # shared positions should be opposite mod 10
            if (j - i) % 10 != 5:
                raise ValueError(
                    f"decagon {d_idx} with neighbor {other} shares positions {(i,j)}, not opposite"
                )
            slot = min(i, j) % 5
            if neighbors_at_slot[slot] is not None:
                raise ValueError(
                    f"decagon {d_idx} slot {slot} already occupied by {neighbors_at_slot[slot]}, now {other}"
                )
            neighbors_at_slot[slot] = other

        if any(x is None for x in neighbors_at_slot):
            raise ValueError(f"decagon {d_idx} has incomplete neighbor slots: {neighbors_at_slot}")

        neighbor_cycles[d_idx] = neighbors_at_slot

    return neighbor_cycles


def canonical_rotations(seq):
    n = len(seq)
    rots = [tuple(seq[i:] + seq[:i]) for i in range(n)]
    rev = list(reversed(seq))
    rots += [tuple(rev[i:] + rev[:i]) for i in range(n)]
    return set(rots)


def propagate_orders(neighbor_cycles: dict[int, list[int]], root: int = 0):
    """
    Probe whether local cyclic orders are globally consistent once one decagon is fixed.
    This does not prove uniqueness, but it detects hidden branching/incompatibility.
    """
    # Fix the root order exactly as given.
    assigned: dict[int, tuple[int, ...]] = {root: tuple(neighbor_cycles[root])}
    queue = deque([root])

    # For each block, the given cycle or its reverse are equivalent local orientations.
    # But adjacency constraints may force one choice.
    possibilities = {
        d: canonical_rotations(neighbor_cycles[d]) for d in neighbor_cycles
    }

    while queue:
        d = queue.popleft()
        d_cycle = assigned[d]
        d_neighbors = list(d_cycle)

        for slot, nbor in enumerate(d_neighbors):
            # nbor must contain d somewhere in its own cycle.
            # Of its possible local orders, keep only those with d at some slot consistent
            # with being adjacent to the two neighboring decagons around d.
            left = d_neighbors[(slot - 1) % 5]
            right = d_neighbors[(slot + 1) % 5]

            allowed = set()
            for cand in possibilities[nbor]:
                if d not in cand:
                    continue
                i = cand.index(d)
                # Around nbor, d has two neighbors; they must both be decagons that are
                # also neighbors of d in the icosahedral graph. We use a weak consistency:
                # left/right must both be neighbors of nbor somewhere in its cycle.
                cand_left = cand[(i - 1) % 5]
                cand_right = cand[(i + 1) % 5]
                if cand_left in neighbor_cycles[d] and cand_right in neighbor_cycles[d]:
                    allowed.add(cand)

            if not allowed:
                return False, assigned, f"inconsistency at decagon {nbor} forced by root path through {d}"

            # If already assigned, check compatibility
            if nbor in assigned:
                if assigned[nbor] not in allowed:
                    return False, assigned, f"assigned order of {nbor} conflicts with propagation from {d}"
                continue

            # If only one possibility survives, force it
            if len(allowed) == 1:
                assigned[nbor] = next(iter(allowed))
                queue.append(nbor)
            else:
                # shrink possibilities
                if allowed != possibilities[nbor]:
                    possibilities[nbor] = allowed

    unresolved = {d: possibilities[d] for d in neighbor_cycles if d not in assigned}
    return True, assigned, unresolved


def main():
    decagons = load_decagons(DECAGON_FILE)
    print("=" * 80)
    print("DEGAGON UNIQUENESS PROBE")
    print("=" * 80)
    print("decagons loaded:", len(decagons))

    pair_shared, state_to_blocks = build_intersection_data(decagons)
    print("states:", len(state_to_blocks))
    print("intersecting decagon pairs:", len(pair_shared))

    neighbor_cycles = local_neighbor_cycle(decagons, pair_shared)

    print()
    print("LOCAL CYCLIC ORDERS")
    print("-" * 80)
    for d in sorted(neighbor_cycles):
        print(f"decagon {d:2d}: {neighbor_cycles[d]}")

    ok, assigned, extra = propagate_orders(neighbor_cycles, root=0)

    print()
    print("PROPAGATION RESULT")
    print("-" * 80)
    print("consistent:", ok)
    print("forced assignments:", len(assigned))

    if ok:
        if isinstance(extra, dict):
            unresolved_counts = {k: len(v) for k, v in extra.items()}
            print("unresolved decagons:", len(extra))
            print("remaining possibility counts:", unresolved_counts)
            if len(extra) == 0:
                print("All local cyclic orders forced from normalization at decagon 0.")
            else:
                print("Some residual freedom remains (likely global symmetries or weak constraints).")
        else:
            print(extra)
    else:
        print("failure reason:", extra)


if __name__ == "__main__":
    main()
