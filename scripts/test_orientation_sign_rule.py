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


def local_neighbor_cycles(decagons: list[list[int]], pair_to_states: dict[tuple[int, int], list[int]]):
    """
    For each decagon D=(x0..x9), determine the cyclic order of its 5 neighboring decagons:
    slot s in {0..4} corresponds to the neighbor meeting D at positions s and s+5.
    """
    neighbor_cycles: dict[int, list[int]] = {}
    for d_idx, cyc in enumerate(decagons):
        pos = {x: i for i, x in enumerate(cyc)}
        slots = [None] * 5
        for (a, b), xs in pair_to_states.items():
            if d_idx not in (a, b):
                continue
            other = b if a == d_idx else a
            i, j = sorted(pos[x] for x in xs)
            if (j - i) % 10 != 5:
                raise ValueError(f"shared positions {(i,j)} not opposite for decagon {d_idx} with {other}")
            slot = min(i, j) % 5
            if slots[slot] is not None:
                raise ValueError(f"duplicate slot on decagon {d_idx}")
            slots[slot] = other
        if any(v is None for v in slots):
            raise ValueError(f"incomplete neighbor cycle for decagon {d_idx}: {slots}")
        neighbor_cycles[d_idx] = slots
    return neighbor_cycles


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
            if pairs == [(0, 0), (1, 1)]:
                edge_sign[(q, r)] = +1
            elif pairs == [(0, 1), (1, 0)]:
                edge_sign[(q, r)] = -1
            else:
                raise ValueError(f"unexpected fiber pattern on edge {(q, r)}: {pairs}")
    return edge_sign


def classify_turn(pair_q: tuple[int, int], pair_r: tuple[int, int], neighbor_cycles: dict[int, list[int]]):
    """
    q and r are quotient vertices = icosahedral edges = unordered pairs of decagons.
    If q and r are adjacent in the quotient, they share exactly one decagon = common endpoint.
    Around that endpoint's local 5-cycle, compare the two other endpoints and measure the step.
    Returns (common_endpoint, step_mod_5, signed_step_mod_5) where signed_step is chosen in {-2,-1,1,2}.
    """
    common = sorted(set(pair_q) & set(pair_r))
    if len(common) != 1:
        raise ValueError(f"quotient edge {pair_q}--{pair_r} does not share exactly one decagon")
    v = common[0]
    a = next(x for x in pair_q if x != v)
    b = next(x for x in pair_r if x != v)

    cyc = neighbor_cycles[v]
    ia = cyc.index(a)
    ib = cyc.index(b)
    diff = (ib - ia) % 5
    # minimal signed representative
    if diff == 0:
        raise ValueError("same neighbor, impossible")
    if diff == 1:
        sdiff = +1
    elif diff == 4:
        sdiff = -1
    elif diff == 2:
        sdiff = +2
    elif diff == 3:
        sdiff = -2
    else:
        raise ValueError("bad diff")
    return v, diff, sdiff


def main():
    decagons = load_decagons(DECAGON_FILE)
    chamber_graph = build_chamber_graph(decagons)
    state_to_blocks = build_state_to_blocks(decagons)
    pair_to_states = build_pair_to_states(state_to_blocks)
    neighbor_cycles = local_neighbor_cycles(decagons, pair_to_states)

    _, pair_of_qid, state_to_qid, state_to_fiber, qid_to_states = build_qvertex_maps(pair_to_states)
    quotient_graph = build_quotient_graph(chamber_graph, state_to_qid)
    edge_sign = recover_signing(
        chamber_graph, quotient_graph, qid_to_states, state_to_qid, state_to_fiber
    )

    records = []
    for (q, r), s in sorted(edge_sign.items()):
        pair_q = pair_of_qid[q]
        pair_r = pair_of_qid[r]
        v, diff, sdiff = classify_turn(pair_q, pair_r, neighbor_cycles)
        records.append((q, r, s, pair_q, pair_r, v, diff, sdiff))

    print("=" * 80)
    print("ORIENTATION SIGN RULE TEST")
    print("=" * 80)

    print("\nSIGN VS UNSIGNED STEP SIZE")
    print("-" * 80)
    hist_abs = Counter((s, abs(sdiff)) for _, _, s, *_rest, sdiff in records)
    for key in sorted(hist_abs):
        print(f"sign={key[0]:+d}, |step|={key[1]}  -> {hist_abs[key]}")

    print("\nSIGN VS SIGNED STEP")
    print("-" * 80)
    hist_signed = Counter((s, sdiff) for _, _, s, *_rest, sdiff in records)
    for key in sorted(hist_signed):
        print(f"sign={key[0]:+d}, step={key[1]:+d}  -> {hist_signed[key]}")

    print("\nDETAILED EDGE DATA")
    print("-" * 80)
    for q, r, s, pair_q, pair_r, v, diff, sdiff in records:
        print(
            f"{q:2d}-{r:2d} sign={s:+d} "
            f"common={v:2d} "
            f"{pair_q} -> {pair_r} "
            f"turn={sdiff:+d}"
        )

    # simple candidate rules
    rule_abs = {}
    for sign in (+1, -1):
        vals = {abs(sdiff) for _, _, s, *_rest, sdiff in records if s == sign}
        rule_abs[sign] = vals

    print("\nCANDIDATE RULE CHECKS")
    print("-" * 80)
    print(f"positive edges use |turn| in {sorted(rule_abs[+1])}")
    print(f"negative edges use |turn| in {sorted(rule_abs[-1])}")

    out = Path("artifacts/reports/test_orientation_sign_rule.txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        f.write("ORIENTATION SIGN RULE TEST\n")
        f.write("=" * 80 + "\n\n")
        f.write("SIGN VS UNSIGNED STEP SIZE\n")
        f.write("-" * 80 + "\n")
        for key in sorted(hist_abs):
            f.write(f"sign={key[0]:+d}, |step|={key[1]}  -> {hist_abs[key]}\n")
        f.write("\nSIGN VS SIGNED STEP\n")
        f.write("-" * 80 + "\n")
        for key in sorted(hist_signed):
            f.write(f"sign={key[0]:+d}, step={key[1]:+d}  -> {hist_signed[key]}\n")
        f.write("\nDETAILED EDGE DATA\n")
        f.write("-" * 80 + "\n")
        for q, r, s, pair_q, pair_r, v, diff, sdiff in records:
            f.write(
                f"{q:2d}-{r:2d} sign={s:+d} common={v:2d} "
                f"{pair_q} -> {pair_r} turn={sdiff:+d}\n"
            )
        f.write("\nCANDIDATE RULE CHECKS\n")
        f.write("-" * 80 + "\n")
        f.write(f"positive edges use |turn| in {sorted(rule_abs[+1])}\n")
        f.write(f"negative edges use |turn| in {sorted(rule_abs[-1])}\n")

    print()
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
