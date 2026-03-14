#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
import math
import os
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
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

# Parallel settings tuned for M3 Pro
N_WORKERS = 8
CHUNK_SIZE = 250_000
PROGRESS_EVERY_CHUNKS = 1


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
    num_vertices: int,
    edges: list[tuple[int, int]],
    signing: np.ndarray,
) -> nx.Graph:
    H = nx.Graph()
    for v in range(num_vertices):
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


def iter_combination_chunks(
    n: int,
    k: int,
    chunk_size: int,
):
    chunk: list[tuple[int, ...]] = []
    for combo in itertools.combinations(range(n), k):
        chunk.append(combo)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def worker_task(
    combos: list[tuple[int, ...]],
    edges: list[tuple[int, int]],
    cbasis: list[list[int]],
    edge_index: dict[tuple[int, int], int],
    num_vertices: int,
) -> dict:
    cycle_counter: Counter = Counter()
    lift_counter: Counter = Counter()
    representative_masks: dict[str, list[int]] = {}

    num_edges = len(edges)

    for neg_choice in combos:
        signing = signing_from_choice(num_edges, neg_choice)

        parity_sig = cycle_parity_signature(cbasis, edge_index, signing)
        cycle_counter[parity_sig] += 1

        H = signed_2_lift(num_vertices, edges, signing)
        h = wl_hash(H)
        lift_counter[h] += 1

        if h not in representative_masks:
            representative_masks[h] = list(neg_choice)

    return {
        "processed": len(combos),
        "cycle_counter": dict(cycle_counter),
        "lift_counter": dict(lift_counter),
        "representative_masks": representative_masks,
    }


def merge_counter_dict(counter: Counter, data: dict) -> None:
    for k, v in data.items():
        counter[k] += v


def write_checkpoint(
    processed: int,
    elapsed: float,
    cycle_counter: Counter,
    lift_counter: Counter,
    representative_masks: dict[str, list[int]],
) -> None:
    rate = processed / elapsed if elapsed > 0 else 0.0
    remaining = TOTAL_SIGNINGS - processed
    eta = remaining / rate if rate > 0 else float("inf")

    payload = {
        "processed": processed,
        "total_signings": TOTAL_SIGNINGS,
        "percent_complete": 100.0 * processed / TOTAL_SIGNINGS,
        "elapsed_seconds": elapsed,
        "rate_samples_per_second": rate,
        "eta_seconds": eta,
        "distinct_cycle_parity_signatures": len(cycle_counter),
        "distinct_lift_hashes": len(lift_counter),
        "top_lift_hashes": lift_counter.most_common(20),
        "representative_masks": representative_masks,
    }

    out = CHECKPOINT_DIR / f"phase1_parallel_checkpoint_{processed:09d}.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    print("=" * 80)
    print("PHASE 1 PARALLEL — FULL ENUMERATION OF 14/16 SIGNINGS BY LIFT HASH")
    print("=" * 80)

    G = relabel_base_to_ints(base_graph())
    edges = sorted_edges(G)
    cbasis = cycle_basis(G)
    edge_index = {e: i for i, e in enumerate(edges)}
    num_vertices = G.number_of_nodes()

    print(f"vertices:        {num_vertices}")
    print(f"edges:           {len(edges)}")
    print(f"negatives target:{NEG_TARGET}")
    print(f"total signings:  {TOTAL_SIGNINGS}")
    print(f"cycle basis size:{len(cbasis)}")
    print(f"workers:         {N_WORKERS}")
    print(f"chunk size:      {CHUNK_SIZE}")
    print()

    start = time.perf_counter()
    processed = 0
    submitted = 0
    finished_chunks = 0

    cycle_counter: Counter = Counter()
    lift_counter: Counter = Counter()
    representative_masks: dict[str, list[int]] = {}

    combo_chunks = iter_combination_chunks(NUM_EDGES, NEG_TARGET, CHUNK_SIZE)

    with ProcessPoolExecutor(max_workers=N_WORKERS) as ex:
        futures = set()

        # initial fill
        try:
            for _ in range(N_WORKERS):
                chunk = next(combo_chunks)
                fut = ex.submit(worker_task, chunk, edges, cbasis, edge_index, num_vertices)
                futures.add(fut)
                submitted += len(chunk)
        except StopIteration:
            pass

        while futures:
            done = next(as_completed(futures))
            futures.remove(done)
            result = done.result()

            processed += result["processed"]
            finished_chunks += 1

            merge_counter_dict(cycle_counter, result["cycle_counter"])
            merge_counter_dict(lift_counter, result["lift_counter"])

            for h, mask in result["representative_masks"].items():
                if h not in representative_masks:
                    representative_masks[h] = mask

            elapsed = time.perf_counter() - start
            rate = processed / elapsed if elapsed > 0 else 0.0
            remaining = TOTAL_SIGNINGS - processed
            eta = remaining / rate if rate > 0 else float("inf")
            pct = 100.0 * processed / TOTAL_SIGNINGS

            if finished_chunks % PROGRESS_EVERY_CHUNKS == 0:
                print(
                    f"... samples={processed}/{TOTAL_SIGNINGS} "
                    f"({pct:6.3f}%) "
                    f"chunks={finished_chunks} "
                    f"cycle_sigs={len(cycle_counter)} "
                    f"lift_hashes={len(lift_counter)} "
                    f"rate={rate:8.1f}/s "
                    f"elapsed={format_seconds(elapsed)} "
                    f"eta={format_seconds(eta)}"
                )

            if finished_chunks % 4 == 0:
                write_checkpoint(processed, elapsed, cycle_counter, lift_counter, representative_masks)

            try:
                chunk = next(combo_chunks)
                fut = ex.submit(worker_task, chunk, edges, cbasis, edge_index, num_vertices)
                futures.add(fut)
                submitted += len(chunk)
            except StopIteration:
                pass

    elapsed = time.perf_counter() - start
    rate = processed / elapsed if elapsed > 0 else 0.0

    summary = {
        "processed": processed,
        "total_signings": TOTAL_SIGNINGS,
        "elapsed_seconds": elapsed,
        "rate_samples_per_second": rate,
        "workers": N_WORKERS,
        "chunk_size": CHUNK_SIZE,
        "distinct_cycle_parity_signatures": len(cycle_counter),
        "distinct_lift_hashes": len(lift_counter),
        "top_lift_hashes": lift_counter.most_common(50),
        "representative_masks": representative_masks,
    }

    txt_lines: list[str] = []
    txt_lines.append("=" * 80)
    txt_lines.append("PHASE 1 PARALLEL — FULL ENUMERATION OF 14/16 SIGNINGS BY LIFT HASH")
    txt_lines.append("=" * 80)
    txt_lines.append(f"vertices: {num_vertices}")
    txt_lines.append(f"edges: {len(edges)}")
    txt_lines.append(f"negatives target: {NEG_TARGET}")
    txt_lines.append(f"total signings: {TOTAL_SIGNINGS}")
    txt_lines.append(f"workers: {N_WORKERS}")
    txt_lines.append(f"chunk size: {CHUNK_SIZE}")
    txt_lines.append(f"samples processed: {processed}")
    txt_lines.append(f"elapsed seconds: {elapsed:.6f}")
    txt_lines.append(f"rate samples/sec: {rate:.6f}")
    txt_lines.append(f"distinct cycle parity signatures: {len(cycle_counter)}")
    txt_lines.append(f"distinct lift hashes: {len(lift_counter)}")
    txt_lines.append("")
    txt_lines.append("TOP LIFT HASHES")
    txt_lines.append("-" * 80)
    for h, count in lift_counter.most_common(20):
        txt_lines.append(f"{h}  count={count}")
    txt_lines.append("")

    (REPORT_DIR / "phase1_sample_lifts_parallel.txt").write_text(
        "\n".join(txt_lines) + "\n",
        encoding="utf-8",
    )
    (REPORT_DIR / "phase1_sample_lifts_parallel.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    write_checkpoint(processed, elapsed, cycle_counter, lift_counter, representative_masks)

    print()
    print(f"saved {REPORT_DIR / 'phase1_sample_lifts_parallel.txt'}")
    print(f"saved {REPORT_DIR / 'phase1_sample_lifts_parallel.json'}")
    print("=" * 80)


if __name__ == "__main__":
    main()
