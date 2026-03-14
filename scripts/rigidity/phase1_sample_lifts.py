#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
import math
import time
from collections import Counter
from pathlib import Path

import networkx as nx
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports" / "rigidity"
CHECKPOINT_DIR = REPORT_DIR / "checkpoints"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

NEG_TARGET = 14
NUM_EDGES = 30
TOTAL_SIGNINGS = math.comb(NUM_EDGES, NEG_TARGET)

# Full exact enumeration on the M3 Pro
SAMPLE_LIMIT = TOTAL_SIGNINGS

CHECKPOINT_EVERY = 50_000
PROGRESS_EVERY = 5_000


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


def cycle_basis(G: nx.Graph) -> list[list[int]]:
    return nx.cycle_basis(G)


def signing_from_choice(num_edges: int, neg_choice: tuple[int, ...]) -> np.ndarray:
    s = np.ones(num_edges, dtype=np.int8)
    s[list(neg_choice)] = -1
    return s


def cycle_parity_signature(
    cbasis: list[list[int]],
    edge_index: dict[tuple[int, int], int],
    signing: np.ndarray,
) -> tuple[int, ...]:
    out: list[int] = []
    for cyc in cbasis:
        prod = 1
        m = len(cyc)
        for i in range(m):
            a = cyc[i]
            b = cyc[(i + 1) % m]
            idx = edge_index[tuple(sorted((a, b)))]
            prod *= int(signing[idx])
        out.append(prod)
    return tuple(out)


def signed_2_lift(
    G: nx.Graph,
    edges: list[tuple[int, int]],
    signing: np.ndarray,
) -> nx.Graph:
    H = nx.Graph()

    for v in G.nodes():
        H.add_node((v, 0))
        H.add_node((v, 1))

    for idx, (u, v) in enumerate(edges):
        s = int(signing[idx])

        if s == 1:
            H.add_edge((u, 0), (v, 0))
            H.add_edge((u, 1), (v, 1))
        else:
            H.add_edge((u, 0), (v, 1))
            H.add_edge((u, 1), (v, 0))

    return H


def wl_hash(G: nx.Graph) -> str:
    return nx.weisfeiler_lehman_graph_hash(G)


def format_seconds(seconds: float) -> str:
    seconds = max(0, int(seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def write_checkpoint(
    sample_count: int,
    elapsed: float,
    cycle_counter: Counter,
    lift_counter: Counter,
    representative_masks: dict[str, list[int]],
) -> None:
    rate = sample_count / elapsed if elapsed > 0 else 0.0
    remaining = TOTAL_SIGNINGS - sample_count
    eta = remaining / rate if rate > 0 else float("inf")

    payload = {
        "sample_count": sample_count,
        "total_signings": TOTAL_SIGNINGS,
        "percent_complete": 100.0 * sample_count / TOTAL_SIGNINGS,
        "elapsed_seconds": elapsed,
        "rate_samples_per_second": rate,
        "eta_seconds": eta,
        "distinct_cycle_parity_signatures": len(cycle_counter),
        "distinct_lift_hashes": len(lift_counter),
        "top_lift_hashes": lift_counter.most_common(20),
        "representative_masks": representative_masks,
    }

    out = CHECKPOINT_DIR / f"phase1_checkpoint_{sample_count:09d}.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    print("=" * 80)
    print("PHASE 1 — FULL ENUMERATION OF 14/16 SIGNINGS BY LIFT HASH")
    print("=" * 80)

    G = relabel_base_to_ints(base_graph())

    edges = sorted_edges(G)
    cbasis = cycle_basis(G)
    edge_index = {e: i for i, e in enumerate(edges)}

    print(f"vertices: {G.number_of_nodes()}")
    print(f"edges:    {G.number_of_edges()}")
    print(f"negatives target: {NEG_TARGET}")
    print(f"total signings:   {TOTAL_SIGNINGS}")
    print(f"cycle basis size: {len(cbasis)}")
    print()

    cycle_counter: Counter = Counter()
    lift_counter: Counter = Counter()
    representative_masks: dict[str, list[int]] = {}

    start = time.perf_counter()
    kept = 0

    for neg_choice in itertools.combinations(range(len(edges)), NEG_TARGET):
        signing = signing_from_choice(len(edges), neg_choice)

        parity_sig = cycle_parity_signature(cbasis, edge_index, signing)
        cycle_counter[parity_sig] += 1

        H = signed_2_lift(G, edges, signing)
        h = wl_hash(H)
        lift_counter[h] += 1

        if h not in representative_masks:
            representative_masks[h] = list(neg_choice)

        kept += 1

        if kept % PROGRESS_EVERY == 0:
            elapsed = time.perf_counter() - start
            rate = kept / elapsed if elapsed > 0 else 0.0
            remaining = TOTAL_SIGNINGS - kept
            eta = remaining / rate if rate > 0 else float("inf")
            pct = 100.0 * kept / TOTAL_SIGNINGS
            print(
                f"... samples={kept}/{TOTAL_SIGNINGS} "
                f"({pct:6.3f}%) "
                f"cycle_sigs={len(cycle_counter)} "
                f"lift_hashes={len(lift_counter)} "
                f"rate={rate:8.1f}/s "
                f"elapsed={format_seconds(elapsed)} "
                f"eta={format_seconds(eta)}"
            )

        if kept % CHECKPOINT_EVERY == 0:
            elapsed = time.perf_counter() - start
            write_checkpoint(kept, elapsed, cycle_counter, lift_counter, representative_masks)

        if kept >= SAMPLE_LIMIT:
            break

    elapsed = time.perf_counter() - start

    summary = {
        "sample_limit": SAMPLE_LIMIT,
        "negatives_target": NEG_TARGET,
        "total_signings": TOTAL_SIGNINGS,
        "samples_processed": kept,
        "elapsed_seconds": elapsed,
        "rate_samples_per_second": kept / elapsed if elapsed > 0 else 0.0,
        "distinct_cycle_parity_signatures": len(cycle_counter),
        "distinct_lift_hashes": len(lift_counter),
        "top_lift_hashes": lift_counter.most_common(50),
        "representative_masks": representative_masks,
    }

    txt_lines: list[str] = []
    txt_lines.append("=" * 80)
    txt_lines.append("PHASE 1 — FULL ENUMERATION OF 14/16 SIGNINGS BY LIFT HASH")
    txt_lines.append("=" * 80)
    txt_lines.append(f"vertices: {G.number_of_nodes()}")
    txt_lines.append(f"edges:    {G.number_of_edges()}")
    txt_lines.append(f"negatives target: {NEG_TARGET}")
    txt_lines.append(f"total signings:   {TOTAL_SIGNINGS}")
    txt_lines.append(f"samples processed: {kept}")
    txt_lines.append(f"elapsed seconds:   {elapsed:.6f}")
    txt_lines.append(f"rate samples/sec:  {kept / elapsed if elapsed > 0 else 0.0:.6f}")
    txt_lines.append(f"distinct cycle parity signatures: {len(cycle_counter)}")
    txt_lines.append(f"distinct lift hashes: {len(lift_counter)}")
    txt_lines.append("")

    txt_lines.append("TOP LIFT HASHES")
    txt_lines.append("-" * 80)
    for h, count in lift_counter.most_common(20):
        txt_lines.append(f"{h}  count={count}")
    txt_lines.append("")

    (REPORT_DIR / "phase1_sample_lifts.txt").write_text(
        "\n".join(txt_lines) + "\n",
        encoding="utf-8",
    )

    (REPORT_DIR / "phase1_sample_lifts.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    write_checkpoint(kept, elapsed, cycle_counter, lift_counter, representative_masks)

    print()
    print(f"saved {REPORT_DIR / 'phase1_sample_lifts.txt'}")
    print(f"saved {REPORT_DIR / 'phase1_sample_lifts.json'}")
    print("=" * 80)


if __name__ == "__main__":
    main()
