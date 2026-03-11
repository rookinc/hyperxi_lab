from __future__ import annotations

from pathlib import Path
import ast
from collections import defaultdict, deque

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


def build_chamber_graph(decagons):
    G = defaultdict(set)
    for cyc in decagons:
        n = len(cyc)
        for i, x in enumerate(cyc):
            y = cyc[(i + 1) % n]
            G[x].add(y)
            G[y].add(x)
    return G


def build_state_to_blocks(decagons):
    d = defaultdict(list)
    for bi, cyc in enumerate(decagons):
        for x in cyc:
            d[x].append(bi)
    return d


def build_pair_to_states(state_to_blocks):
    p = defaultdict(list)
    for x, bs in state_to_blocks.items():
        a, b = sorted(bs)
        p[(a, b)].append(x)
    return p


def build_qmaps(pair_to_states):
    qpairs = sorted(pair_to_states)
    qid_of_pair = {pair: i for i, pair in enumerate(qpairs)}
    pair_of_qid = {i: pair for pair, i in qid_of_pair.items()}
    state_to_qid = {}
    qid_to_states = {}
    for pair, qid in qid_of_pair.items():
        s0, s1 = sorted(pair_to_states[pair])
        qid_to_states[qid] = (s0, s1)
        state_to_qid[s0] = qid
        state_to_qid[s1] = qid
    return qid_of_pair, pair_of_qid, state_to_qid, qid_to_states


def build_quotient_graph(chamber_graph, state_to_qid):
    Q = defaultdict(set)
    for x, nbrs in chamber_graph.items():
        qx = state_to_qid[x]
        for y in nbrs:
            qy = state_to_qid[y]
            if qx != qy:
                Q[qx].add(qy)
                Q[qy].add(qx)
    return Q


def recover_actual_signing(chamber_graph, quotient_graph, qid_to_states, state_to_qid):
    # default fiber labels by sorted state ids
    state_to_fiber = {}
    for q, (s0, s1) in qid_to_states.items():
        state_to_fiber[s0] = 0
        state_to_fiber[s1] = 1

    sign = {}
    for q in quotient_graph:
        for r in quotient_graph[q]:
            if q >= r:
                continue
            pairs = []
            for x in qid_to_states[q]:
                for y in chamber_graph[x]:
                    if state_to_qid[y] == r:
                        pairs.append((state_to_fiber[x], state_to_fiber[y]))
            pairs = sorted(pairs)
            if pairs == [(0, 0), (1, 1)]:
                sign[(q, r)] = +1
            elif pairs == [(0, 1), (1, 0)]:
                sign[(q, r)] = -1
            else:
                raise ValueError(f"bad actual pattern on {(q,r)}: {pairs}")
    return sign


def local_positions_on_block(decagons):
    pos = {}
    for d_idx, cyc in enumerate(decagons):
        for i, x in enumerate(cyc):
            pos[(x, d_idx)] = i
    return pos


def recover_intrinsic_signing(decagons, chamber_graph, quotient_graph, pair_of_qid, qid_to_states, state_to_qid):
    pos = local_positions_on_block(decagons)

    # intrinsic local ordering on each quotient vertex from the smaller-index block
    state_to_orderbit = {}
    for q, (A, B) in pair_of_qid.items():
        s0, s1 = qid_to_states[q]
        R = min(A, B)
        i0 = pos[(s0, R)]
        i1 = pos[(s1, R)]
        key0 = (i0 % 5, i0)
        key1 = (i1 % 5, i1)
        if key0 < key1:
            first, second = s0, s1
        else:
            first, second = s1, s0
        state_to_orderbit[(q, first)] = 0
        state_to_orderbit[(q, second)] = 1

    sign = {}
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
                sign[(q, r)] = +1
            elif pairs == [(0, 1), (1, 0)]:
                sign[(q, r)] = -1
            else:
                raise ValueError(f"bad intrinsic pattern on {(q,r)}: {pairs}")
    return sign


def switching_equivalent(Q, sigma, tau):
    """
    Check whether sigma(qr) = eps(q)*tau(qr)*eps(r) for some eps:V->{+-1}.
    """
    eps = {}
    start = min(Q.keys())
    eps[start] = +1
    dq = deque([start])

    while dq:
        u = dq.popleft()
        for v in Q[u]:
            a, b = sorted((u, v))
            needed = sigma[(a, b)] * tau[(a, b)] * eps[u]
            # because sigma = eps(u)*tau*eps(v), so eps(v)=eps(u)*sigma*tau
            if v in eps:
                if eps[v] != needed:
                    return False, None
            else:
                eps[v] = needed
                dq.append(v)

    return True, eps


def main():
    decagons = load_decagons(DECAGON_FILE)
    chamber_graph = build_chamber_graph(decagons)
    state_to_blocks = build_state_to_blocks(decagons)
    pair_to_states = build_pair_to_states(state_to_blocks)
    _, pair_of_qid, state_to_qid, qid_to_states = build_qmaps(pair_to_states)
    Q = build_quotient_graph(chamber_graph, state_to_qid)

    sigma = recover_actual_signing(chamber_graph, Q, qid_to_states, state_to_qid)
    tau = recover_intrinsic_signing(decagons, chamber_graph, Q, pair_of_qid, qid_to_states, state_to_qid)

    ok, eps = switching_equivalent(Q, sigma, tau)

    print("=" * 80)
    print("SWITCHING EQUIVALENCE TEST")
    print("=" * 80)
    print("switching-equivalent:", ok)
    if ok:
        pos = sum(1 for v in eps.values() if v == +1)
        neg = sum(1 for v in eps.values() if v == -1)
        print(f"switch labels: +1 on {pos} vertices, -1 on {neg} vertices")
        print("vertex switching function:")
        for q in sorted(eps):
            print(f"{q:2d}: {eps[q]:+d}")
    else:
        print("No switching function exists.")

    out = Path("artifacts/reports/test_sign_switching_equivalence.txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        f.write("SWITCHING EQUIVALENCE TEST\n")
        f.write("=" * 80 + "\n")
        f.write(f"switching-equivalent: {ok}\n")
        if ok:
            pos = sum(1 for v in eps.values() if v == +1)
            neg = sum(1 for v in eps.values() if v == -1)
            f.write(f"switch labels: +1 on {pos} vertices, -1 on {neg} vertices\n")
            for q in sorted(eps):
                f.write(f"{q:2d}: {eps[q]:+d}\n")

    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
