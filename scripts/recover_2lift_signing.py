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
    """
    Chamber graph: states are adjacent if consecutive on a decagon.
    """
    G: dict[int, set[int]] = defaultdict(set)
    for cyc in decagons:
        n = len(cyc)
        for i, x in enumerate(cyc):
            y = cyc[(i + 1) % n]
            G[x].add(y)
            G[y].add(x)
    return G


def build_state_to_decagons(decagons: list[list[int]]) -> dict[int, list[int]]:
    state_to_blocks: dict[int, list[int]] = defaultdict(list)
    for d_idx, cyc in enumerate(decagons):
        for x in cyc:
            state_to_blocks[x].append(d_idx)
    return state_to_blocks


def build_intersection_pairs(state_to_blocks: dict[int, list[int]]):
    """
    Quotient vertices correspond to intersecting decagon pairs.
    Since each state lies on exactly 2 decagons, each state belongs to one pair.
    Each pair has exactly 2 states.
    """
    pair_to_states: dict[tuple[int, int], list[int]] = defaultdict(list)
    for x, blocks in state_to_blocks.items():
        if len(blocks) != 2:
            raise ValueError(f"state {x} lies on {len(blocks)} decagons, expected 2")
        a, b = sorted(blocks)
        pair_to_states[(a, b)].append(x)

    for pair, states in pair_to_states.items():
        if len(states) != 2:
            raise ValueError(f"pair {pair} has {len(states)} states, expected 2")
    return pair_to_states


def build_state_to_qvertex(pair_to_states: dict[tuple[int, int], list[int]]):
    """
    Assign quotient vertex ids 0..29 to intersecting decagon pairs.
    Also give each quotient vertex a local fiber labeling 0/1 on its two states.
    """
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


def build_quotient_graph(
    chamber_graph: dict[int, set[int]],
    state_to_qid: dict[int, int],
) -> dict[int, set[int]]:
    """
    Project chamber edges to quotient edges between quotient vertices.
    """
    Q: dict[int, set[int]] = defaultdict(set)
    seen = set()
    for x, nbrs in chamber_graph.items():
        qx = state_to_qid[x]
        for y in nbrs:
            qy = state_to_qid[y]
            if qx == qy:
                # Should not happen in a simple 2-lift of a simple base graph
                continue
            a, b = sorted((qx, qy))
            if (a, b) not in seen:
                seen.add((a, b))
                Q[a].add(b)
                Q[b].add(a)
    return Q


def recover_signing(
    chamber_graph: dict[int, set[int]],
    quotient_graph: dict[int, set[int]],
    qid_to_states: dict[int, tuple[int, int]],
    state_to_qid: dict[int, int],
    state_to_fiber: dict[int, int],
):
    """
    For each quotient edge q-r, determine whether the 2-lift is + or -:
      + if fiber 0 connects to fiber 0 and fiber 1 to fiber 1
      - if fiber 0 connects to fiber 1 and fiber 1 to fiber 0
    """
    edge_sign: dict[tuple[int, int], int] = {}
    edge_pattern: dict[tuple[int, int], list[tuple[int, int]]] = {}

    for q in quotient_graph:
        for r in quotient_graph[q]:
            if q >= r:
                continue

            pairs = []
            sq0, sq1 = qid_to_states[q]
            sr0, sr1 = qid_to_states[r]

            # collect actual chamber edges between fibers over q and r
            for x in (sq0, sq1):
                for y in chamber_graph[x]:
                    if state_to_qid[y] == r:
                        pairs.append((state_to_fiber[x], state_to_fiber[y]))

            pairs_sorted = sorted(pairs)
            edge_pattern[(q, r)] = pairs_sorted

            if pairs_sorted == [(0, 0), (1, 1)]:
                edge_sign[(q, r)] = +1
            elif pairs_sorted == [(0, 1), (1, 0)]:
                edge_sign[(q, r)] = -1
            else:
                raise ValueError(
                    f"edge {(q,r)} has unexpected fiber pattern {pairs_sorted}"
                )

    return edge_sign, edge_pattern


def build_signed_adjacency(quotient_graph: dict[int, set[int]], edge_sign: dict[tuple[int, int], int]):
    """
    Return dense signed adjacency matrix as list of lists.
    """
    n = max(quotient_graph) + 1
    A = [[0 for _ in range(n)] for _ in range(n)]
    for q in quotient_graph:
        for r in quotient_graph[q]:
            if q < r:
                s = edge_sign[(q, r)]
                A[q][r] = s
                A[r][q] = s
    return A


def print_matrix_rows(A: list[list[int]], max_rows: int = 10):
    n = len(A)
    for i in range(min(n, max_rows)):
        print(f"{i:2d}:", " ".join(f"{x:2d}" for x in A[i]))


def main():
    decagons = load_decagons(DECAGON_FILE)
    chamber_graph = build_chamber_graph(decagons)
    state_to_blocks = build_state_to_decagons(decagons)
    pair_to_states = build_intersection_pairs(state_to_blocks)

    (
        qid_of_pair,
        pair_of_qid,
        state_to_qid,
        state_to_fiber,
        qid_to_states,
    ) = build_state_to_qvertex(pair_to_states)

    quotient_graph = build_quotient_graph(chamber_graph, state_to_qid)
    edge_sign, edge_pattern = recover_signing(
        chamber_graph,
        quotient_graph,
        qid_to_states,
        state_to_qid,
        state_to_fiber,
    )

    print("=" * 80)
    print("RECOVERED 2-LIFT SIGNING")
    print("=" * 80)
    print("quotient vertices:", len(qid_to_states))
    print("quotient edges:", len(edge_sign))
    print("degree set:", sorted({len(v) for v in quotient_graph.values()}))

    print()
    print("SIGN HISTOGRAM")
    print("-" * 80)
    hist = Counter(edge_sign.values())
    print({"+1": hist.get(+1, 0), "-1": hist.get(-1, 0)})

    print()
    print("EDGE SIGNS")
    print("-" * 80)
    for (q, r), s in sorted(edge_sign.items()):
        pair_q = pair_of_qid[q]
        pair_r = pair_of_qid[r]
        print(
            f"{q:2d}-{r:2d}  sign={s:+d}  "
            f"{pair_q} <-> {pair_r}  pattern={edge_pattern[(q,r)]}"
        )

    A_signed = build_signed_adjacency(quotient_graph, edge_sign)

    print()
    print("SIGNED ADJACENCY MATRIX (first 10 rows)")
    print("-" * 80)
    print_matrix_rows(A_signed, max_rows=10)

    out = Path("artifacts/reports/recovered_signing.txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        f.write("RECOVERED 2-LIFT SIGNING\n")
        f.write("========================\n")
        f.write(f"quotient vertices: {len(qid_to_states)}\n")
        f.write(f"quotient edges: {len(edge_sign)}\n")
        f.write(f"degree set: {sorted({len(v) for v in quotient_graph.values()})}\n\n")
        f.write("SIGN HISTOGRAM\n")
        f.write(str({"+1": hist.get(+1, 0), "-1": hist.get(-1, 0)}) + "\n\n")
        f.write("EDGE SIGNS\n")
        for (q, r), s in sorted(edge_sign.items()):
            pair_q = pair_of_qid[q]
            pair_r = pair_of_qid[r]
            f.write(
                f"{q:2d}-{r:2d}  sign={s:+d}  "
                f"{pair_q} <-> {pair_r}  pattern={edge_pattern[(q,r)]}\n"
            )

    print()
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
