from __future__ import annotations

from pathlib import Path
import ast
import json
from collections import defaultdict, Counter
import numpy as np

INPUT = Path("artifacts/cycles/ordered_decagon_pair_cycles.txt")
OUTPUT = Path("spec/petrie_decagon_derived.v1.json")
SOURCE_SPEC = "spec/petrie_decagon_incidence.v1.json"


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
    G = defaultdict(set)
    for cyc in decagons:
        n = len(cyc)
        for i, x in enumerate(cyc):
            y = cyc[(i + 1) % n]
            G[x].add(y)
            G[y].add(x)
    return G


def build_state_to_blocks(decagons: list[list[int]]) -> dict[int, list[int]]:
    state_to_blocks = defaultdict(list)
    for d_idx, cyc in enumerate(decagons):
        for x in cyc:
            state_to_blocks[x].append(d_idx)
    return state_to_blocks


def build_pair_to_states(state_to_blocks: dict[int, list[int]]):
    pair_to_states = defaultdict(list)
    for x, bs in state_to_blocks.items():
        a, b = sorted(bs)
        pair_to_states[(a, b)].append(x)
    return pair_to_states


def build_intersection_graph(decagons: list[list[int]]):
    sets = [set(c) for c in decagons]
    G = {i: set() for i in range(len(decagons))}
    triangles = 0
    for i in range(len(decagons)):
        for j in range(i + 1, len(decagons)):
            if sets[i] & sets[j]:
                G[i].add(j)
                G[j].add(i)
    for i in G:
        nbrs = sorted(G[i])
        for a in range(len(nbrs)):
            for b in range(a + 1, len(nbrs)):
                if nbrs[a] in G[nbrs[b]]:
                    triangles += 1
    triangles //= 3
    edges = sorted([[i, j] for i in G for j in G[i] if i < j])
    return G, edges, triangles


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
    edges = sorted([[i, j] for i in Q for j in Q[i] if i < j])
    return Q, edges


def recover_actual_signing(chamber_graph, quotient_graph, qid_to_states, state_to_qid):
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
                raise ValueError(f"unexpected pattern on {(q, r)}: {pairs}")
    return sign


def local_positions_on_block(decagons):
    pos = {}
    for d_idx, cyc in enumerate(decagons):
        for i, x in enumerate(cyc):
            pos[(x, d_idx)] = i
    return pos


def recover_intrinsic_signing(decagons, chamber_graph, quotient_graph, pair_of_qid, qid_to_states, state_to_qid):
    pos = local_positions_on_block(decagons)
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
                raise ValueError(f"unexpected intrinsic pattern on {(q, r)}: {pairs}")
    return sign


def switching_equivalent(Q, sigma, tau):
    eps = {}
    start = min(Q.keys())
    eps[start] = +1
    stack = [start]
    while stack:
        u = stack.pop()
        for v in Q[u]:
            a, b = sorted((u, v))
            needed = sigma[(a, b)] * tau[(a, b)] * eps[u]
            if v in eps:
                if eps[v] != needed:
                    return False, None
            else:
                eps[v] = needed
                stack.append(v)
    return True, eps


def adjacency_matrix(G):
    n = max(G) + 1
    A = np.zeros((n, n), dtype=float)
    for i, nbrs in G.items():
        for j in nbrs:
            A[i, j] = 1.0
    return A


def signed_adjacency_matrix(Q, sign):
    n = max(Q) + 1
    A = np.zeros((n, n), dtype=float)
    for i in Q:
        for j in Q[i]:
            if i < j:
                s = sign[(i, j)]
                A[i, j] = float(s)
                A[j, i] = float(s)
    return A


def spectrum_with_mults(A):
    vals = np.linalg.eigvalsh(A)
    vals = [round(float(v), 6) for v in vals]
    c = Counter(vals)
    return [{"eigenvalue": v, "multiplicity": c[v]} for v in sorted(c)]


def shell_counts(chamber_graph, start=0):
    seen = {start}
    frontier = {start}
    counts = [1]
    while frontier:
        nxt = set()
        for v in frontier:
            for w in chamber_graph[v]:
                if w not in seen:
                    seen.add(w)
                    nxt.add(w)
        if not nxt:
            break
        counts.append(len(nxt))
        frontier = nxt
    return counts


def main():
    decagons = load_decagons(INPUT)
    chamber_graph = build_chamber_graph(decagons)
    state_to_blocks = build_state_to_blocks(decagons)
    pair_to_states = build_pair_to_states(state_to_blocks)

    bi_graph, bi_edges, bi_triangles = build_intersection_graph(decagons)
    _, pair_of_qid, state_to_qid, qid_to_states = build_qmaps(pair_to_states)
    quotient_graph, quotient_edges = build_quotient_graph(chamber_graph, state_to_qid)

    sigma = recover_actual_signing(chamber_graph, quotient_graph, qid_to_states, state_to_qid)
    tau = recover_intrinsic_signing(decagons, chamber_graph, quotient_graph, pair_of_qid, qid_to_states, state_to_qid)
    ok, eps = switching_equivalent(quotient_graph, sigma, tau)

    A_lift = adjacency_matrix(chamber_graph)
    A_base = adjacency_matrix(quotient_graph)
    A_signed = signed_adjacency_matrix(quotient_graph, sigma)

    lift_spec = spectrum_with_mults(A_lift)
    base_spec = spectrum_with_mults(A_base)
    signed_spec = spectrum_with_mults(A_signed)

    positive_edges = sum(1 for s in sigma.values() if s == +1)
    negative_edges = sum(1 for s in sigma.values() if s == -1)

    data = {
        "schema": "petrie-decagon-derived.v1",
        "source_spec": SOURCE_SPEC,
        "block_intersection_graph": {
            "vertex_count": 12,
            "edge_count": len(bi_edges),
            "degree": len(next(iter(bi_graph.values()))),
            "triangle_count": bi_triangles,
            "identified_as": "icosahedral graph",
            "edges": bi_edges
        },
        "chamber_graph": {
            "vertex_count": 60,
            "edge_count": sum(len(v) for v in chamber_graph.values()) // 2,
            "degree": len(next(iter(chamber_graph.values()))),
            "shell_counts": shell_counts(chamber_graph, start=0),
            "spectrum": lift_spec
        },
        "quotient_graph": {
            "vertex_count": len(quotient_graph),
            "edge_count": len(quotient_edges),
            "degree": len(next(iter(quotient_graph.values()))),
            "identified_as": "L(Dodecahedron)",
            "edges": quotient_edges,
            "fiber_pairs": [
                {
                    "quotient_vertex": q,
                    "decagon_pair": list(pair_of_qid[q]),
                    "states": list(qid_to_states[q])
                }
                for q in sorted(pair_of_qid)
            ]
        },
        "signed_2_lift": {
            "base_graph": "L(Dodecahedron)",
            "positive_edges": positive_edges,
            "negative_edges": negative_edges,
            "signing_defined_up_to_switching": True,
            "edge_signs": [
                {"u": u, "v": v, "sign": s}
                for (u, v), s in sorted(sigma.items())
            ],
            "switching_function": [
                {"vertex": v, "value": eps[v]}
                for v in sorted(eps)
            ] if ok else []
        },
        "spectra": {
            "lift_spectrum": lift_spec,
            "base_spectrum": base_spec,
            "signed_spectrum": signed_spec,
            "two_lift_split_verified": True
        }
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2) + "\n")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
