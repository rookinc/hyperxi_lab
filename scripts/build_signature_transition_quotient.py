#!/usr/bin/env python3

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from hyperxi.spectral.operators import LocalOperatorFactory


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "spectral" / "signature_transitions"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def eigenspace_blocks(vals: np.ndarray, tol: float = 1e-8):
    blocks = []
    used = np.zeros(len(vals), dtype=bool)
    for i, v in enumerate(vals):
        if used[i]:
            continue
        idx = [j for j, w in enumerate(vals) if abs(w - v) <= tol]
        for j in idx:
            used[j] = True
        blocks.append((float(v), idx))
    return blocks


def block_operator(U: np.ndarray, basis_i: np.ndarray, basis_j: np.ndarray) -> np.ndarray:
    return basis_i.T @ U @ basis_j


def fro_norm(M: np.ndarray) -> float:
    return float(np.linalg.norm(M))


def polar_unitary(M: np.ndarray) -> np.ndarray:
    U, _, Vt = np.linalg.svd(M)
    return U @ Vt


def scalar_sign_label(U: np.ndarray, tol: float = 1e-8) -> str:
    I = np.eye(U.shape[0], dtype=float)
    if np.allclose(U, I, atol=tol):
        return "+I"
    if np.allclose(U, -I, atol=tol):
        return "-I"
    return "non-scalar"


def signature_str(sig: tuple[str, str, str]) -> str:
    return f"({sig[0]},{sig[1]},{sig[2]})"


def hamming_signature_distance(sig_a: tuple[str, str, str], sig_b: tuple[str, str, str]) -> int:
    return sum(a != b for a, b in zip(sig_a, sig_b))


def main():
    print("=" * 80)
    print("BUILD SIGNATURE TRANSITION QUOTIENT")
    print("=" * 80)

    ops = LocalOperatorFactory()

    UF = ops.build_U_F().astype(float)
    US = ops.build_U_S().astype(float)
    UV = ops.build_U_V().astype(float)
    H = ops.build_H_loc().astype(float)

    vals, vecs = np.linalg.eigh(H)
    blocks_raw = eigenspace_blocks(vals)

    blocks = []
    for block_id, (lam, idx) in enumerate(blocks_raw[:20], start=1):
        basis = np.array(vecs[:, idx], dtype=float)

        PF = polar_unitary(block_operator(UF, basis, basis))
        PS = polar_unitary(block_operator(US, basis, basis))
        PV = polar_unitary(block_operator(UV, basis, basis))

        sig = (
            scalar_sign_label(PF),
            scalar_sign_label(PS),
            scalar_sign_label(PV),
        )

        blocks.append(
            {
                "block": block_id,
                "lambda": lam,
                "dim": len(idx),
                "basis": basis,
                "signature": sig,
                "signature_str": signature_str(sig),
            }
        )

    n = len(blocks)

    MF = np.zeros((n, n), dtype=float)
    MS = np.zeros((n, n), dtype=float)
    MV = np.zeros((n, n), dtype=float)

    for i, bi in enumerate(blocks):
        for j, bj in enumerate(blocks):
            MF[i, j] = fro_norm(block_operator(UF, bi["basis"], bj["basis"]))
            MS[i, j] = fro_norm(block_operator(US, bi["basis"], bj["basis"]))
            MV[i, j] = fro_norm(block_operator(UV, bi["basis"], bj["basis"]))

    np.fill_diagonal(MF, 0.0)
    np.fill_diagonal(MS, 0.0)
    np.fill_diagonal(MV, 0.0)

    MD = MF + MS + MV

    sig_to_blocks: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    for i, b in enumerate(blocks):
        sig_to_blocks[b["signature"]].append(i)

    signatures = sorted(sig_to_blocks.keys(), key=signature_str)
    m = len(signatures)

    qmat = np.zeros((m, m), dtype=float)

    for a, sig_a in enumerate(signatures):
        for b, sig_b in enumerate(signatures):
            total = 0.0
            for i in sig_to_blocks[sig_a]:
                for j in sig_to_blocks[sig_b]:
                    if i == j:
                        continue
                    total += MD[i, j]
            qmat[a, b] = total

    sym_qmat = qmat + qmat.T

    lines = []
    lines.append("=" * 80)
    lines.append("SIGNATURE TRANSITION QUOTIENT")
    lines.append("=" * 80)
    lines.append(f"low block count: {len(blocks)}")
    lines.append(f"observed signature count: {m}")
    lines.append("")

    lines.append("BLOCKS BY SIGNATURE")
    lines.append("-" * 80)
    for sig in signatures:
        idxs = sig_to_blocks[sig]
        block_list = [blocks[i]["block"] for i in idxs]
        lambdas = [blocks[i]["lambda"] for i in idxs]
        lines.append(
            f"{signature_str(sig)}  blocks={block_list}  lambdas={[round(x, 12) for x in lambdas]}"
        )
    lines.append("")

    lines.append("DIRECTED QUOTIENT MATRIX")
    lines.append("-" * 80)
    header = "sig".ljust(18) + " ".join(f"{signature_str(sig):>18s}" for sig in signatures)
    lines.append(header)
    for i, sig in enumerate(signatures):
        row = signature_str(sig).ljust(18) + " ".join(f"{qmat[i,j]:18.6f}" for j in range(m))
        lines.append(row)
    lines.append("")

    lines.append("SYMMETRIZED QUOTIENT MATRIX")
    lines.append("-" * 80)
    lines.append(header)
    for i, sig in enumerate(signatures):
        row = signature_str(sig).ljust(18) + " ".join(f"{sym_qmat[i,j]:18.6f}" for j in range(m))
        lines.append(row)
    lines.append("")

    edges = []
    for i, sig_i in enumerate(signatures):
        for j, sig_j in enumerate(signatures):
            if i == j:
                continue
            w = float(qmat[i, j])
            if w > 0:
                edges.append(
                    {
                        "src_signature": signature_str(sig_j),
                        "dst_signature": signature_str(sig_i),
                        "src_index": j,
                        "dst_index": i,
                        "weight": w,
                        "hamming": hamming_signature_distance(sig_i, sig_j),
                    }
                )
    edges.sort(key=lambda x: x["weight"], reverse=True)

    lines.append("TOP DIRECTED SIGNATURE EDGES")
    lines.append("-" * 80)
    for e in edges[:20]:
        lines.append(
            f"{e['src_signature']} -> {e['dst_signature']}   "
            f"weight={e['weight']:.6f}   hamming={e['hamming']}"
        )
    lines.append("")

    pair_edges = []
    for i in range(m):
        for j in range(i + 1, m):
            w = float(sym_qmat[i, j])
            pair_edges.append(
                {
                    "sig_a": signature_str(signatures[i]),
                    "sig_b": signature_str(signatures[j]),
                    "weight": w,
                    "hamming": hamming_signature_distance(signatures[i], signatures[j]),
                }
            )
    pair_edges.sort(key=lambda x: x["weight"], reverse=True)

    lines.append("TOP SYMMETRIZED SIGNATURE PAIRS")
    lines.append("-" * 80)
    for e in pair_edges[:20]:
        lines.append(
            f"{e['sig_a']} <-> {e['sig_b']}   "
            f"weight={e['weight']:.6f}   hamming={e['hamming']}"
        )
    lines.append("")

    lines.append("SUMMARY BY SIGNATURE HAMMING DISTANCE")
    lines.append("-" * 80)
    for h in range(4):
        vals_h = [e["weight"] for e in pair_edges if e["hamming"] == h]
        if vals_h:
            lines.append(
                f"hamming={h}   count={len(vals_h)}   "
                f"mean={np.mean(vals_h):.6f}   max={np.max(vals_h):.6f}"
            )
    lines.append("")

    txt_path = OUT_DIR / "signature_transition_quotient.txt"
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload = {
        "blocks": [
            {
                "block": b["block"],
                "lambda": b["lambda"],
                "dim": b["dim"],
                "signature": b["signature_str"],
            }
            for b in blocks
        ],
        "signatures": [signature_str(sig) for sig in signatures],
        "signature_to_blocks": {
            signature_str(sig): [blocks[i]["block"] for i in sig_to_blocks[sig]]
            for sig in signatures
        },
        "directed_quotient_matrix": qmat.tolist(),
        "symmetrized_quotient_matrix": sym_qmat.tolist(),
        "top_directed_edges": edges[:30],
        "top_symmetrized_pairs": pair_edges[:30],
    }

    json_path = OUT_DIR / "signature_transition_quotient.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"saved {txt_path.relative_to(ROOT)}")
    print(f"saved {json_path.relative_to(ROOT)}")
    print()

    print("OBSERVED SIGNATURE CLASSES")
    print("-" * 80)
    for sig in signatures:
        idxs = sig_to_blocks[sig]
        block_list = [blocks[i]["block"] for i in idxs]
        print(f"{signature_str(sig)}  blocks={block_list}")
    print()

    print("TOP SYMMETRIZED SIGNATURE PAIRS")
    print("-" * 80)
    for e in pair_edges[:15]:
        print(
            f"{e['sig_a']} <-> {e['sig_b']}   weight={e['weight']:.6f}   hamming={e['hamming']}"
        )
    print()

    print("SUMMARY BY SIGNATURE HAMMING DISTANCE")
    print("-" * 80)
    for h in range(4):
        vals_h = [e["weight"] for e in pair_edges if e["hamming"] == h]
        if vals_h:
            print(
                f"hamming={h}   count={len(vals_h)}   "
                f"mean={np.mean(vals_h):.6f}   max={np.max(vals_h):.6f}"
            )

    print("=" * 80)


if __name__ == "__main__":
    main()
