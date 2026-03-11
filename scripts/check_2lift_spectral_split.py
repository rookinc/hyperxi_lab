from __future__ import annotations

from pathlib import Path
import ast
from collections import defaultdict, Counter
import numpy as np

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


def build_state_to_decagons(decagons: list[list[int]]) -> dict[int, list[int]]:
    state_to_blocks: dict[int, list[int]] = defaultdict(list)
    for d_idx, cyc in enumerate(decagons):
        for x in cyc:
            state_to_blocks[x].append(d_idx)
    return state_to_blocks


def build_intersection_pairs(state_to_blocks: dict[int, list[int]]):
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


def adjacency_matrix_from_graph(G: dict[int, set[int]]) -> np.ndarray:
    n = max(G) + 1
    A = np.zeros((n, n), dtype=float)
    for i, nbrs in G.items():
        for j in nbrs:
            A[i, j] = 1.0
    return A


def signed_adjacency_matrix(Q: dict[int, set[int]], edge_sign: dict[tuple[int, int], int]) -> np.ndarray:
    n = max(Q) + 1
    A = np.zeros((n, n), dtype=float)
    for i in Q:
        for j in Q[i]:
            if i < j:
                s = edge_sign[(i, j)]
                A[i, j] = float(s)
                A[j, i] = float(s)
    return A


def rounded_spec(A: np.ndarray, ndigits: int = 6) -> list[float]:
    vals = np.linalg.eigvalsh(A)
    return sorted(round(float(v), ndigits) for v in vals)


def multiset_hist(vals: list[float]) -> list[tuple[float, int]]:
    c = Counter(vals)
    return [(v, c[v]) for v in sorted(c)]


def print_hist(title: str, vals: list[float]):
    print(title)
    print("-" * 80)
    for v, m in multiset_hist(vals):
        print(f"{v:>10.6f}: {m}")
    print()


def main():
    decagons = load_decagons(DECAGON_FILE)
    chamber_graph = build_chamber_graph(decagons)
    state_to_blocks = build_state_to_decagons(decagons)
    pair_to_states = build_intersection_pairs(state_to_blocks)
    _, _, state_to_qid, state_to_fiber, qid_to_states = build_qvertex_maps(pair_to_states)
    quotient_graph = build_quotient_graph(chamber_graph, state_to_qid)
    edge_sign = recover_signing(
        chamber_graph, quotient_graph, qid_to_states, state_to_qid, state_to_fiber
    )

    A_lift = adjacency_matrix_from_graph(chamber_graph)
    A_base = adjacency_matrix_from_graph(quotient_graph)
    A_signed = signed_adjacency_matrix(quotient_graph, edge_sign)

    spec_lift = rounded_spec(A_lift)
    spec_base = rounded_spec(A_base)
    spec_signed = rounded_spec(A_signed)
    spec_union = sorted(spec_base + spec_signed)

    print("=" * 80)
    print("2-LIFT SPECTRAL SPLIT CHECK")
    print("=" * 80)
    print(f"lift vertices:   {A_lift.shape[0]}")
    print(f"base vertices:   {A_base.shape[0]}")
    print(f"signed vertices: {A_signed.shape[0]}")
    print()

    print_hist("LIFT SPECTRUM", spec_lift)
    print_hist("BASE SPECTRUM", spec_base)
    print_hist("SIGNED SPECTRUM", spec_signed)
    print_hist("UNION(BASE,SIGNED)", spec_union)

    ok = spec_lift == spec_union
    print("MATCHES 2-LIFT THEOREM:", ok)

    out = Path("artifacts/reports/check_2lift_spectral_split.txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        f.write("2-LIFT SPECTRAL SPLIT CHECK\n")
        f.write("=" * 80 + "\n\n")
        for title, vals in [
            ("LIFT SPECTRUM", spec_lift),
            ("BASE SPECTRUM", spec_base),
            ("SIGNED SPECTRUM", spec_signed),
            ("UNION(BASE,SIGNED)", spec_union),
        ]:
            f.write(title + "\n")
            f.write("-" * 80 + "\n")
            for v, m in multiset_hist(vals):
                f.write(f"{v:>10.6f}: {m}\n")
            f.write("\n")
        f.write(f"MATCHES 2-LIFT THEOREM: {ok}\n")

    print()
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
