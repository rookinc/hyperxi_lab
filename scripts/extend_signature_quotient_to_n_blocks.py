#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IN_SIG = ROOT / "reports" / "spectral" / "generator_sign_reps.json"
IN_MIX = ROOT / "reports" / "spectral" / "block_transitions" / "low_block_transition_graph.json"
OUT_DIR = ROOT / "reports" / "spectral" / "signature_transitions"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sig_tuple_to_str(sig: tuple[str, str, str]) -> str:
    return f"({sig[0]},{sig[1]},{sig[2]})"


def parse_signature_payload(payload: dict) -> dict[int, tuple[str, str, str]]:
    """
    Expected generator_sign_reps.json shape:
      {
        "blocks": [
          {"block": 1, "lambda": ..., "dim": ..., "F": "-I", "S": "-I", "V": "-I"},
          ...
        ]
      }

    Also tolerates a dict keyed by block id.
    """
    out: dict[int, tuple[str, str, str]] = {}

    if "blocks" in payload and isinstance(payload["blocks"], list):
        for row in payload["blocks"]:
            try:
                b = int(row["block"])
                out[b] = (str(row["F"]), str(row["S"]), str(row["V"]))
            except KeyError as e:
                raise SystemExit(f"generator_sign_reps.json missing key {e} in row: {row}")
        return out

    if "signatures" in payload and isinstance(payload["signatures"], dict):
        for k, row in payload["signatures"].items():
            b = int(k)
            if isinstance(row, dict):
                out[b] = (str(row["F"]), str(row["S"]), str(row["V"]))
            else:
                out[b] = tuple(row)  # type: ignore[assignment]
        return out

    raise SystemExit("Unrecognized generator_sign_reps.json format")


def parse_transition_payload(payload: dict) -> tuple[list[int], dict[str, np.ndarray]]:
    """
    Tolerates several shapes for low_block_transition_graph.json:

      1) {"blocks": [1,2,...], "operators": {"F": matrix, "S": matrix, "V": matrix}}
      2) {"block_ids": [1,2,...], ...}
      3) {"blocks": [{"block":1,...}, {"block":2,...}], ...}
      4) {"operators": [{"name":"F","norm_matrix":[...]}, ...]}

    Also tolerates top-level "F"/"S"/"V".
    """
    if "blocks" in payload:
        raw_blocks = payload["blocks"]
        if not raw_blocks:
            raise SystemExit("Transition graph JSON has empty blocks list")
        if isinstance(raw_blocks[0], dict):
            if "block" in raw_blocks[0]:
                blocks = [int(row["block"]) for row in raw_blocks]
            elif "id" in raw_blocks[0]:
                blocks = [int(row["id"]) for row in raw_blocks]
            else:
                raise SystemExit("blocks entries are dicts but have no block/id field")
        else:
            blocks = [int(x) for x in raw_blocks]
    elif "block_ids" in payload:
        blocks = [int(x) for x in payload["block_ids"]]
    else:
        raise SystemExit("Transition graph JSON missing blocks/block_ids")

    ops: dict[str, np.ndarray] = {}

    if "operators" in payload:
        ops_src = payload["operators"]

        # Case A: dict like {"F": matrix, "S": matrix, "V": matrix}
        if isinstance(ops_src, dict):
            for op in ("F", "S", "V"):
                if op not in ops_src:
                    raise SystemExit(f"Transition graph JSON missing operator {op}")
                val = ops_src[op]
                if isinstance(val, dict):
                    if "norm_matrix" in val:
                        ops[op] = np.array(val["norm_matrix"], dtype=float)
                    elif "matrix" in val:
                        ops[op] = np.array(val["matrix"], dtype=float)
                    else:
                        raise SystemExit(f"Operator {op} dict missing norm_matrix/matrix")
                else:
                    ops[op] = np.array(val, dtype=float)

        # Case B: list like [{"name":"F","norm_matrix":[...]}, ...]
        elif isinstance(ops_src, list):
            by_name = {}
            for row in ops_src:
                if not isinstance(row, dict):
                    raise SystemExit("operators list contains non-dict entry")
                name = row.get("name")
                if name is None:
                    raise SystemExit("operators list entry missing name")
                by_name[str(name)] = row

            for op in ("F", "S", "V"):
                if op not in by_name:
                    raise SystemExit(f"Transition graph JSON missing operator {op}")
                row = by_name[op]
                if "norm_matrix" in row:
                    ops[op] = np.array(row["norm_matrix"], dtype=float)
                elif "matrix" in row:
                    ops[op] = np.array(row["matrix"], dtype=float)
                else:
                    raise SystemExit(f"Operator {op} entry missing norm_matrix/matrix")
        else:
            raise SystemExit("Transition graph JSON has unrecognized operators field")

    else:
        # Legacy top-level format
        for op in ("F", "S", "V"):
            if op not in payload:
                raise SystemExit(f"Transition graph JSON missing operator {op}")
            val = payload[op]
            if isinstance(val, dict):
                if "norm_matrix" in val:
                    ops[op] = np.array(val["norm_matrix"], dtype=float)
                elif "matrix" in val:
                    ops[op] = np.array(val["matrix"], dtype=float)
                else:
                    raise SystemExit(f"Top-level operator {op} missing norm_matrix/matrix")
            else:
                ops[op] = np.array(val, dtype=float)

    n = len(blocks)
    for op, M in ops.items():
        if M.shape != (n, n):
            raise SystemExit(f"Operator {op} has shape {M.shape}, expected {(n, n)}")

    return blocks, ops


def build_signature_quotient(
    keep_blocks: list[int],
    block2sig: dict[int, tuple[str, str, str]],
    all_blocks: list[int],
    ops: dict[str, np.ndarray],
) -> dict:
    idx_of = {b: i for i, b in enumerate(all_blocks)}

    missing = [b for b in keep_blocks if b not in block2sig]
    if missing:
        raise SystemExit(f"Missing signatures for blocks: {missing}")

    sig2blocks: dict[str, list[int]] = defaultdict(list)
    for b in keep_blocks:
        sig2blocks[sig_tuple_to_str(block2sig[b])].append(b)

    signatures = sorted(sig2blocks.keys())
    sidx = {sig: i for i, sig in enumerate(signatures)}
    m = len(signatures)

    directed_by_op: dict[str, np.ndarray] = {op: np.zeros((m, m), dtype=float) for op in ops}
    directed_total = np.zeros((m, m), dtype=float)

    for op, M in ops.items():
        for bi in keep_blocks:
            ii = idx_of[bi]
            sig_i = sig_tuple_to_str(block2sig[bi])
            si = sidx[sig_i]
            for bj in keep_blocks:
                jj = idx_of[bj]
                sig_j = sig_tuple_to_str(block2sig[bj])
                sj = sidx[sig_j]
                w = float(M[ii, jj])
                if w != 0.0:
                    directed_by_op[op][si, sj] += w
                    directed_total[si, sj] += w

    sym = directed_total + directed_total.T
    np.fill_diagonal(sym, np.diag(directed_total))

    row_sums = directed_total.sum(axis=1)
    P = np.zeros_like(directed_total)
    for i in range(m):
        if row_sums[i] > 0:
            P[i] = directed_total[i] / row_sums[i]
        else:
            P[i, i] = 1.0

    evals, evecs = np.linalg.eig(P.T)
    k = int(np.argmin(np.abs(evals - 1.0)))
    v = np.real(evecs[:, k])
    v = np.abs(v)
    pi = v / v.sum() if v.sum() > 0 else np.full(m, 1.0 / m)

    return {
        "kept_blocks": keep_blocks,
        "signatures": signatures,
        "signature_to_blocks": {sig: sig2blocks[sig] for sig in signatures},
        "directed_quotient_matrix": directed_total.tolist(),
        "symmetrized_quotient_matrix": sym.tolist(),
        "directed_by_operator": {op: directed_by_op[op].tolist() for op in ("F", "S", "V")},
        "transition_matrix": P.tolist(),
        "stationary_distribution": {signatures[i]: float(pi[i]) for i in range(m)},
    }


def summarize(payload: dict) -> None:
    sigs = payload["signatures"]
    P = np.array(payload["transition_matrix"], dtype=float)
    pi = payload["stationary_distribution"]

    print("=" * 80)
    print("EXTENDED SIGNATURE QUOTIENT")
    print("=" * 80)
    print(f"block count kept: {len(payload['kept_blocks'])}")
    print(f"signature count : {len(sigs)}")
    print()

    print("SIGNATURE CLASSES")
    print("-" * 80)
    for sig in sigs:
        print(f"{sig:18s}  blocks={payload['signature_to_blocks'][sig]}")
    print()

    print("STATIONARY DISTRIBUTION")
    print("-" * 80)
    for sig, w in sorted(pi.items(), key=lambda x: x[1], reverse=True):
        print(f"{sig:18s}  {w:.6f}")
    print()

    print("STRONGEST OUTGOING EDGE PER SIGNATURE")
    print("-" * 80)
    for i, sig in enumerate(sigs):
        row = P[i].copy()
        row[i] = -1.0
        j = int(np.argmax(row))
        if P[i, j] <= 0:
            print(f"{sig:18s}  (no outgoing edge)")
        else:
            print(f"{sig:18s} -> {sigs[j]:18s}   p={P[i,j]:.6f}")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20, help="number of lowest blocks to keep")
    args = ap.parse_args()

    sig_payload = load_json(IN_SIG)
    mix_payload = load_json(IN_MIX)

    block2sig = parse_signature_payload(sig_payload)
    all_blocks, ops = parse_transition_payload(mix_payload)

    keep_blocks = all_blocks[: args.n]
    payload = build_signature_quotient(keep_blocks, block2sig, all_blocks, ops)

    stem = f"signature_transition_quotient_{args.n:03d}_blocks"
    out_json = OUT_DIR / f"{stem}.json"
    out_txt = OUT_DIR / f"{stem}.txt"

    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = []
    lines.append("=" * 80)
    lines.append(f"SIGNATURE TRANSITION QUOTIENT ({args.n} BLOCKS)")
    lines.append("=" * 80)
    lines.append(f"block count kept: {len(payload['kept_blocks'])}")
    lines.append(f"signature count : {len(payload['signatures'])}")
    lines.append("")
    lines.append("SIGNATURE CLASSES")
    lines.append("-" * 80)
    for sig in payload["signatures"]:
        lines.append(f"{sig:18s}  blocks={payload['signature_to_blocks'][sig]}")
    lines.append("")
    lines.append("STATIONARY DISTRIBUTION")
    lines.append("-" * 80)
    for sig, w in sorted(payload["stationary_distribution"].items(), key=lambda x: x[1], reverse=True):
        lines.append(f"{sig:18s}  {w:.6f}")
    lines.append("")
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

    summarize(payload)
    print(f"saved {out_txt.relative_to(ROOT)}")
    print(f"saved {out_json.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
