from __future__ import annotations

from pathlib import Path
import ast
from collections import defaultdict, Counter

DECAGON_FILE = Path("artifacts/cycles/ordered_decagon_pair_cycles.txt")


def load_decagons(path: Path) -> list[list[int]]:
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line.startswith("decagon") or ":" not in line:
            continue
        payload = line.split(":", 1)[1].strip()
        obj = ast.literal_eval(payload)
        if isinstance(obj, list) and len(obj) == 10:
            out.append([int(x) for x in obj])
    return out


def build_chamber_graph(decagons: list[list[int]]) -> dict[int, set[int]]:
    G: dict[int, set[int]] = defaultdict(set)
    for cyc in decagons:
        n = len(cyc)
        for i, x in enumerate(cyc):
            y = cyc[(i + 1) % n]
            G[x].add(y)
            G[y].add(x)
    return G


def build_state_to_blocks(decagons: list[list[int]]) -> dict[int, list[int]]:
    state_to_blocks: dict[int, list[int]] = defaultdict(list)
    for d_idx, cyc in enumerate(decagons):
        for x in cyc:
            state_to_blocks[x].append(d_idx)
    for x, bs in state_to_blocks.items():
        if len(bs) != 2:
            raise ValueError(f"state {x} lies on {len(bs)} decagons, expected 2")
    return state_to_blocks


def build_pair_to_states(state_to_blocks: dict[int, list[int]]):
    pair_to_states: dict[tuple[int, int], list[int]] = defaultdict(list)
    for x, bs in state_to_blocks.items():
        a, b = sorted(bs)
        pair_to_states[(a, b)].append(x)
    for pair, xs in pair_to_states.items():
        if len(xs) != 2:
            raise ValueError(f"pair {pair} has {len(xs)} states, expected 2")
    return pair_to_states


def build_qvertex_maps(pair_to_states: dict[tuple[int, int], list[int]]):
    qpairs = sorted(pair_to_states.keys())
    qid_of_pair = {pair: i for i, pair in enumerate(qpairs)}
    pair_of_qid = {i: pair for pair, i in qid_of_pair.items()}

    state_to_qid: dict[int, int] = {}
    state_to_fiber: dict[int, int] = {}
    qid_to_states: dict[int, tuple[int, int]] = {}

    for pair, qid in qid_of_pair.items():
        s0, s1 = sorted(pair_to_states[pair])
        qid_to_states[qid] = (s0, s1)
        state_to_qid[s0] = qid
        state_to_qid[s1] = qid
        state_to_fiber[s0] = 0
        state_to_fiber[s1] = 1

    return qid_of_pair, pair_of_qid, state_to_qid, state_to_fiber, qid_to_states


def build_quotient_graph(chamber_graph: dict[int, set[int]], state_to_qid: dict[int, int]):
    Q: dict[int, set[int]] = defaultdict(set)
    for x, nbrs in chamber_graph.items():
        qx = state_to_qid[x]
        for y in nbrs:
            qy = state_to_qid[y]
            if qx != qy:
                Q[qx].add(qy)
                Q[qy].add(qx)
    return Q


def recover_signing(
    chamber_graph: dict[int, set[int]],
    quotient_graph: dict[int, set[int]],
    qid_to_states: dict[int, tuple[int, int]],
    state_to_qid: dict[int, int],
    state_to_fiber: dict[int, int],
):
    edge_sign: dict[tuple[int, int], int] = {}
    edge_pattern: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for q in quotient_graph:
        for r in quotient_graph[q]:
            if q >= r:
                continue
            pairs = []
            sq0, sq1 = qid_to_states[q]
            for x in (sq0, sq1):
                for y in chamber_graph[x]:
                    if state_to_qid[y] == r:
                        pairs.append((state_to_fiber[x], state_to_fiber[y]))
            pairs = sorted(pairs)
            edge_pattern[(q, r)] = pairs
            if pairs == [(0, 0), (1, 1)]:
                edge_sign[(q, r)] = +1
            elif pairs == [(0, 1), (1, 0)]:
                edge_sign[(q, r)] = -1
            else:
                raise ValueError(f"unexpected fiber pattern on edge {(q, r)}: {pairs}")
    return edge_sign, edge_pattern


def local_positions_on_block(decagons: list[list[int]], state_to_blocks: dict[int, list[int]]):
    """
    For each state x and each incident decagon D, record the index of x on D.
    """
    pos = {}
    for d_idx, cyc in enumerate(decagons):
        for i, x in enumerate(cyc):
            pos[(x, d_idx)] = i
    return pos


def build_fiber_orientations(
    pair_of_qid: dict[int, tuple[int, int]],
    qid_to_states: dict[int, tuple[int, int]],
    pos_on_block: dict[tuple[int, int], int],
):
    """
    For each quotient vertex q = (A,B), define an intrinsic local fiber order
    from the cyclic order on the smaller-index block A.
    Since the two shared states on q are opposite on A, one occurs first
    among the pair {i, i+5} with i in {0,...,4}. We use that to orient the fiber.

    Returns:
      fiber_order[q] = (state_first, state_second)
      state_to_orderbit[(q, state)] = 0/1 according to this intrinsic order
    """
    fiber_order = {}
    state_to_orderbit = {}

    for q, (A, B) in pair_of_qid.items():
        s0, s1 = qid_to_states[q]

        # Use the smaller block index as canonical reference.
        R = min(A, B)
        i0 = pos_on_block[(s0, R)]
        i1 = pos_on_block[(s1, R)]

        # opposite positions mod 10
        if (i1 - i0) % 10 not in (5,):
            if (i0 - i1) % 10 != 5:
                raise ValueError(f"states {s0},{s1} are not opposite on reference block {R}")

        # Canonicalize to the one whose position mod 5 is smaller, tie by position.
        key0 = (i0 % 5, i0)
        key1 = (i1 % 5, i1)
        if key0 < key1:
            first, second = s0, s1
        else:
            first, second = s1, s0

        fiber_order[q] = (first, second)
        state_to_orderbit[(q, first)] = 0
        state_to_orderbit[(q, second)] = 1

    return fiber_order, state_to_orderbit


def test_rule(
    chamber_graph: dict[int, set[int]],
    quotient_graph: dict[int, set[int]],
    pair_of_qid: dict[int, tuple[int, int]],
    qid_to_states: dict[int, tuple[int, int]],
    state_to_qid: dict[int, int],
    edge_sign: dict[tuple[int, int], int],
    state_to_orderbit: dict[tuple[int, int], int],
):
    """
    For each quotient edge q-r, inspect the actual lifted edges between the two fibers.
    Re-express them in the intrinsic local fiber order bits. Then ask whether sign
    is exactly 'preserve/reverse intrinsic order'.
    """
    records = []
    for q in quotient_graph:
        for r in quotient_graph[q]:
            if q >= r:
                continue

            pairs = []
            for x in qid_to_states[q]:
                for y in chamber_graph[x]:
                    if state_to_qid[y] == r:
                        bx = state_to_orderbit[(q, x)]
                        by = state_to_orderbit[(r, y)]
                        pairs.append((bx, by))
            pairs = sorted(pairs)

            if pairs == [(0, 0), (1, 1)]:
                inferred = +1
            elif pairs == [(0, 1), (1, 0)]:
                inferred = -1
            else:
                inferred = None

            records.append((q, r, edge_sign[(q, r)], inferred, pair_of_qid[q], pair_of_qid[r], pairs))
    return records


def main():
    decagons = load_decagons(DECAGON_FILE)
    chamber_graph = build_chamber_graph(decagons)
    state_to_blocks = build_state_to_blocks(decagons)
    pair_to_states = build_pair_to_states(state_to_blocks)
    pos_on_block = local_positions_on_block(decagons, state_to_blocks)

    _, pair_of_qid, state_to_qid, state_to_fiber, qid_to_states = build_qvertex_maps(pair_to_states)
    quotient_graph = build_quotient_graph(chamber_graph, state_to_qid)
    edge_sign, edge_pattern = recover_signing(
        chamber_graph, quotient_graph, qid_to_states, state_to_qid, state_to_fiber
    )

    fiber_order, state_to_orderbit = build_fiber_orientations(pair_of_qid, qid_to_states, pos_on_block)
    records = test_rule(
        chamber_graph,
        quotient_graph,
        pair_of_qid,
        qid_to_states,
        state_to_qid,
        edge_sign,
        state_to_orderbit,
    )

    print("=" * 80)
    print("FIBER-ORDER SIGN RULE TEST")
    print("=" * 80)

    hist = Counter((actual, inferred) for _, _, actual, inferred, *_ in records)
    print("\nACTUAL SIGN VS INTRINSIC FIBER-ORDER BEHAVIOR")
    print("-" * 80)
    for key in sorted(hist):
        print(f"actual={key[0]:+d}, inferred={key[1]:+d}  -> {hist[key]}")

    exact = all(actual == inferred for _, _, actual, inferred, *_ in records)
    print("\nEXACT MATCH:", exact)

    print("\nDETAILED EDGE DATA")
    print("-" * 80)
    for q, r, actual, inferred, pair_q, pair_r, pairs in records:
        print(
            f"{q:2d}-{r:2d}  actual={actual:+d} inferred={inferred:+d}  "
            f"{pair_q} <-> {pair_r}  intrinsic_pairs={pairs}"
        )

    out = Path("artifacts/reports/test_fiber_order_sign_rule.txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        f.write("FIBER-ORDER SIGN RULE TEST\n")
        f.write("=" * 80 + "\n\n")
        f.write("ACTUAL SIGN VS INTRINSIC FIBER-ORDER BEHAVIOR\n")
        f.write("-" * 80 + "\n")
        for key in sorted(hist):
            f.write(f"actual={key[0]:+d}, inferred={key[1]:+d}  -> {hist[key]}\n")
        f.write(f"\nEXACT MATCH: {exact}\n\n")
        f.write("DETAILED EDGE DATA\n")
        f.write("-" * 80 + "\n")
        for q, r, actual, inferred, pair_q, pair_r, pairs in records:
            f.write(
                f"{q:2d}-{r:2d}  actual={actual:+d} inferred={inferred:+d}  "
                f"{pair_q} <-> {pair_r}  intrinsic_pairs={pairs}\n"
            )

    print()
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
