#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import networkx as nx
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports" / "rigidity"
CHECKPOINT_DIR = REPORT_DIR / "checkpoints"
INPUT_JSON = REPORT_DIR / "phase1_sample_lifts.json"
OUTPUT_JSON = REPORT_DIR / "phase2_switch_reduce.json"
OUTPUT_TXT = REPORT_DIR / "phase2_switch_reduce.txt"


def petersen_graph() -> nx.Graph:
    return nx.petersen_graph()


def base_graph() -> nx.Graph:
    return nx.line_graph(petersen_graph())


def relabel_base_to_ints(G: nx.Graph) -> nx.Graph:
    nodes = sorted(tuple(sorted(x)) for x in G.nodes())
    edge_to_id = {n: i for i, n in enumerate(nodes)}
    H = nx.Graph()
    H.add_nodes_from(range(len(nodes)))
    for a, b in G.edges():
        ia = edge_to_id[tuple(sorted(a))]
        ib = edge_to_id[tuple(sorted(b))]
        H.add_edge(ia, ib)
    return H


def sorted_edges(G: nx.Graph) -> list[tuple[int, int]]:
    return sorted(tuple(sorted(e)) for e in G.edges())


def signing_from_neg_list(num_edges: int, neg_choice: list[int]) -> np.ndarray:
    s = np.ones(num_edges, dtype=np.int8)
    if neg_choice:
        s[np.array(neg_choice, dtype=int)] = -1
    return s


def switching_signature_fast(
    edge_u: np.ndarray,
    edge_v: np.ndarray,
    signing: np.ndarray,
    bits: int,
    n_vertices: int,
) -> np.ndarray:
    sw = np.ones(n_vertices, dtype=np.int8)
    for v in range(1, n_vertices):
        if (bits >> (v - 1)) & 1:
            sw[v] = -1
    return sw[edge_u] * signing * sw[edge_v]


def canonical_switch_class(
    edge_u: np.ndarray,
    edge_v: np.ndarray,
    signing: np.ndarray,
    n_vertices: int,
) -> tuple[int, ...]:
    best: tuple[int, ...] | None = None
    for bits in range(1 << (n_vertices - 1)):
        switched = switching_signature_fast(edge_u, edge_v, signing, bits, n_vertices)
        rep = tuple(int(x) for x in switched.tolist())
        if best is None or rep < best:
            best = rep
    assert best is not None
    return best


def main() -> None:
    if not INPUT_JSON.exists():
        raise FileNotFoundError(
            f"Missing {INPUT_JSON}. Run phase1_sample_lifts.py first."
        )

    print("=" * 80)
    print("PHASE 2 — SWITCHING REDUCTION ON LIFT REPRESENTATIVES")
    print("=" * 80)

    phase1 = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    rep_masks: dict[str, list[int]] = phase1.get("representative_masks", {})
    if not rep_masks:
        raise RuntimeError("No representative masks found in phase1 output.")

    G = relabel_base_to_ints(base_graph())
    edges = sorted_edges(G)
    n_vertices = G.number_of_nodes()
    edge_u = np.array([u for u, _ in edges], dtype=np.int16)
    edge_v = np.array([v for _, v in edges], dtype=np.int16)

    switch_counter: Counter = Counter()
    lift_to_switch: dict[str, tuple[int, ...]] = {}

    total = len(rep_masks)
    print(f"lift representatives from phase 1: {total}")
    print()

    for idx, (lift_hash, neg_choice) in enumerate(sorted(rep_masks.items()), start=1):
        signing = signing_from_neg_list(len(edges), neg_choice)
        switch_rep = canonical_switch_class(edge_u, edge_v, signing, n_vertices)
        switch_counter[switch_rep] += 1
        lift_to_switch[lift_hash] = switch_rep

        if idx % 10 == 0 or idx == total:
            print(
                f"... processed={idx}/{total} "
                f"distinct_switch_classes={len(switch_counter)}"
            )

    summary = {
        "phase1_distinct_lift_hashes": len(rep_masks),
        "distinct_switch_classes": len(switch_counter),
        "switch_class_multiplicities": [
            {"count": count, "repr": list(rep)}
            for rep, count in switch_counter.most_common(50)
        ],
        "lift_hash_to_switch_repr": {
            h: list(rep) for h, rep in lift_to_switch.items()
        },
    }

    lines: list[str] = []
    lines.append("=" * 80)
    lines.append("PHASE 2 — SWITCHING REDUCTION ON LIFT REPRESENTATIVES")
    lines.append("=" * 80)
    lines.append(f"phase1 distinct lift hashes: {len(rep_masks)}")
    lines.append(f"distinct switch classes:     {len(switch_counter)}")
    lines.append("")
    lines.append("TOP SWITCH CLASSES")
    lines.append("-" * 80)
    for rep, count in switch_counter.most_common(20):
        lines.append(f"count={count} repr_prefix={list(rep[:12])} ...")
    lines.append("")

    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print()
    print(f"saved {OUTPUT_TXT}")
    print(f"saved {OUTPUT_JSON}")
    print("=" * 80)


if __name__ == "__main__":
    main()
