#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from hyperxi.spectral.operators import LocalOperatorFactory


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "spectral" / "block_transitions"
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


def scalar_sign_label(U: np.ndarray, tol: float = 1e-8) -> str:
    I = np.eye(U.shape[0], dtype=float)
    if np.allclose(U, I, atol=tol):
        return "+I"
    if np.allclose(U, -I, atol=tol):
        return "-I"
    return "non-scalar"


def polar_unitary(M: np.ndarray) -> np.ndarray:
    U, _, Vt = np.linalg.svd(M)
    return U @ Vt


def top_edges(norm_mat: np.ndarray, blocks: list[dict], top_k: int = 20):
    edges = []
    n = len(blocks)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            w = float(norm_mat[i, j])
            if w > 1e-12:
                edges.append(
                    {
                        "src_block": blocks[j]["block"],
                        "dst_block": blocks[i]["block"],
                        "src_lambda": blocks[j]["lambda"],
                        "dst_lambda": blocks[i]["lambda"],
                        "weight": w,
                    }
                )
    edges.sort(key=lambda x: x["weight"], reverse=True)
    return edges[:top_k]


def summarize_operator(name: str, U: np.ndarray, blocks: list[dict]):
    n = len(blocks)
    norm_mat = np.zeros((n, n), dtype=float)
    diag_labels = []

    for i, bi in enumerate(blocks):
        pii = block_operator(U, bi["basis"], bi["basis"])
        ui = polar_unitary(pii)
        diag_labels.append(scalar_sign_label(ui))

        for j, bj in enumerate(blocks):
            bij = block_operator(U, bi["basis"], bj["basis"])
            norm_mat[i, j] = fro_norm(bij)

    off_diag = norm_mat.copy()
    np.fill_diagonal(off_diag, 0.0)

    max_off = float(np.max(off_diag))
    total_diag = float(np.sum(np.diag(norm_mat)))
    total_off = float(np.sum(off_diag))

    return {
        "name": name,
        "norm_matrix": norm_mat,
        "diag_labels": diag_labels,
        "max_offdiag": max_off,
        "diag_total": total_diag,
        "offdiag_total": total_off,
        "top_edges": top_edges(norm_mat, blocks, top_k=25),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20, help="number of lowest eigenspace blocks to keep")
    args = ap.parse_args()

    print("=" * 80)
    print("BUILD LOW BLOCK TRANSITION GRAPH")
    print("=" * 80)

    ops = LocalOperatorFactory()

    UF = ops.build_U_F().astype(float)
    US = ops.build_U_S().astype(float)
    UV = ops.build_U_V().astype(float)
    H = ops.build_H_loc().astype(float)

    vals, vecs = np.linalg.eigh(H)
    blocks_raw = eigenspace_blocks(vals)

    if args.n <= 0:
        raise SystemExit("--n must be positive")
    if args.n > len(blocks_raw):
        raise SystemExit(f"Requested --n={args.n}, but only {len(blocks_raw)} eigenspace blocks exist")

    blocks = []
    for block_id, (lam, idx) in enumerate(blocks_raw[: args.n], start=1):
        basis = np.array(vecs[:, idx], dtype=float)
        blocks.append(
            {
                "block": block_id,
                "lambda": lam,
                "dim": len(idx),
                "basis": basis,
            }
        )

    print(f"low block count: {len(blocks)}")
    print()

    summaries = [
        summarize_operator("F", UF, blocks),
        summarize_operator("S", US, blocks),
        summarize_operator("V", UV, blocks),
    ]

    combined = np.zeros((len(blocks), len(blocks)), dtype=float)
    for s in summaries:
        combined += s["norm_matrix"]

    combined_edges = []
    n = len(blocks)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            w = float(combined[i, j])
            if w > 1e-12:
                combined_edges.append(
                    {
                        "src_block": blocks[j]["block"],
                        "dst_block": blocks[i]["block"],
                        "src_lambda": blocks[j]["lambda"],
                        "dst_lambda": blocks[i]["lambda"],
                        "weight": w,
                    }
                )
    combined_edges.sort(key=lambda x: x["weight"], reverse=True)

    lines = []
    lines.append("=" * 80)
    lines.append("LOW BLOCK TRANSITION GRAPH")
    lines.append("=" * 80)
    lines.append(f"low block count: {len(blocks)}")
    lines.append("")

    lines.append("BLOCKS")
    lines.append("-" * 80)
    for b in blocks:
        lines.append(f"block {b['block']:2d}  lambda={b['lambda']:.12f}  dim={b['dim']}")
    lines.append("")

    for s in summaries:
        lines.append("=" * 80)
        lines.append(f"OPERATOR {s['name']}")
        lines.append("=" * 80)
        lines.append("Diagonal block signatures")
        lines.append("-" * 80)
        for b, lab in zip(blocks, s["diag_labels"]):
            lines.append(
                f"block {b['block']:2d}  lambda={b['lambda']:.12f}  dim={b['dim']}  diag={lab}"
            )
        lines.append("")
        lines.append(f"sum diagonal norms   : {s['diag_total']:.6f}")
        lines.append(f"sum offdiag norms    : {s['offdiag_total']:.6f}")
        lines.append(f"max offdiag norm     : {s['max_offdiag']:.6f}")
        lines.append("")
        lines.append("Top transition edges")
        lines.append("-" * 80)
        for e in s["top_edges"]:
            lines.append(
                f"block {e['src_block']:2d} -> block {e['dst_block']:2d}   "
                f"weight={e['weight']:.6f}   "
                f"lambdas=({e['src_lambda']:.12f} -> {e['dst_lambda']:.12f})"
            )
        lines.append("")

    lines.append("=" * 80)
    lines.append("COMBINED TRANSITION GRAPH (F + S + V norm weights)")
    lines.append("=" * 80)
    for e in combined_edges[:30]:
        lines.append(
            f"block {e['src_block']:2d} -> block {e['dst_block']:2d}   "
            f"weight={e['weight']:.6f}   "
            f"lambdas=({e['src_lambda']:.12f} -> {e['dst_lambda']:.12f})"
        )
    lines.append("")

    stem = f"low_block_transition_graph_{args.n:03d}_blocks"
    txt_path = OUT_DIR / f"{stem}.txt"
    json_path = OUT_DIR / f"{stem}.json"

    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload = {
        "blocks": [
            {
                "block": b["block"],
                "lambda": b["lambda"],
                "dim": b["dim"],
            }
            for b in blocks
        ],
        "operators": {
            s["name"]: {
                "diag_labels": {
                    str(blocks[i]["block"]): s["diag_labels"][i]
                    for i in range(len(blocks))
                },
                "norm_matrix": s["norm_matrix"].tolist(),
                "diag_total": s["diag_total"],
                "offdiag_total": s["offdiag_total"],
                "max_offdiag": s["max_offdiag"],
                "top_edges": s["top_edges"],
            }
            for s in summaries
        },
        "combined_norm_matrix": combined.tolist(),
        "combined_top_edges": combined_edges[:50],
    }

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # also keep legacy names in sync for downstream scripts
    legacy_txt = OUT_DIR / "low_block_transition_graph.txt"
    legacy_json = OUT_DIR / "low_block_transition_graph.json"
    legacy_txt.write_text(txt_path.read_text(encoding="utf-8"), encoding="utf-8")
    legacy_json.write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"saved {txt_path.relative_to(ROOT)}")
    print(f"saved {json_path.relative_to(ROOT)}")
    print()

    for s in summaries:
        print("=" * 80)
        print(f"OPERATOR {s['name']}")
        print("=" * 80)
        print(f"sum diagonal norms: {s['diag_total']:.6f}")
        print(f"sum offdiag norms : {s['offdiag_total']:.6f}")
        print(f"max offdiag norm  : {s['max_offdiag']:.6f}")
        print("top edges:")
        for e in s["top_edges"][:10]:
            print(
                f"  block {e['src_block']:2d} -> block {e['dst_block']:2d} "
                f" weight={e['weight']:.6f}"
            )
        print()

    print("=" * 80)
    print("COMBINED TOP EDGES")
    print("=" * 80)
    for e in combined_edges[:15]:
        print(
            f"block {e['src_block']:2d} -> block {e['dst_block']:2d} "
            f"weight={e['weight']:.6f}"
        )

    print("=" * 80)


if __name__ == "__main__":
    main()
