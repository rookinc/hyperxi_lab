#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from hyperxi.spectral.operators import LocalOperatorFactory


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "spectral"
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


def block_operator(U: np.ndarray, basis: np.ndarray) -> np.ndarray:
    return basis.T @ U @ basis


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20, help="number of lowest eigenspace blocks to analyze")
    args = ap.parse_args()

    print("=" * 80)
    print("DECOMPOSE GENERATOR SIGN REPRESENTATIONS")
    print("=" * 80)

    ops = LocalOperatorFactory()
    H = ops.build_H_loc().astype(float)
    UF = ops.build_U_F().astype(float)
    US = ops.build_U_S().astype(float)
    UV = ops.build_U_V().astype(float)

    vals, vecs = np.linalg.eigh(H)
    blocks_raw = eigenspace_blocks(vals)

    if args.n <= 0:
        raise SystemExit("--n must be positive")
    if args.n > len(blocks_raw):
        raise SystemExit(f"Requested --n={args.n}, but only {len(blocks_raw)} eigenspace blocks exist")

    rows = []
    for block_id, (lam, idx) in enumerate(blocks_raw[: args.n], start=1):
        basis = np.array(vecs[:, idx], dtype=float)

        F_block = polar_unitary(block_operator(UF, basis))
        S_block = polar_unitary(block_operator(US, basis))
        V_block = polar_unitary(block_operator(UV, basis))

        rows.append(
            {
                "block": block_id,
                "lambda": float(lam),
                "dim": len(idx),
                "F": scalar_sign_label(F_block),
                "S": scalar_sign_label(S_block),
                "V": scalar_sign_label(V_block),
            }
        )

    print(f"{'block':>5} {'lambda':>16} {'dim':>4} {'F':>8} {'S':>8} {'V':>8}")
    print("-" * 60)
    for row in rows:
        print(
            f"{row['block']:5d} "
            f"{row['lambda']:16.12f} "
            f"{row['dim']:4d} "
            f"{row['F']:>8} "
            f"{row['S']:>8} "
            f"{row['V']:>8}"
        )

    txt_lines = []
    txt_lines.append("=" * 80)
    txt_lines.append("DECOMPOSE GENERATOR SIGN REPRESENTATIONS")
    txt_lines.append("=" * 80)
    txt_lines.append(f"block count: {len(rows)}")
    txt_lines.append("")
    txt_lines.append(f"{'block':>5} {'lambda':>16} {'dim':>4} {'F':>8} {'S':>8} {'V':>8}")
    txt_lines.append("-" * 60)
    for row in rows:
        txt_lines.append(
            f"{row['block']:5d} "
            f"{row['lambda']:16.12f} "
            f"{row['dim']:4d} "
            f"{row['F']:>8} "
            f"{row['S']:>8} "
            f"{row['V']:>8}"
        )

    txt_path = OUT_DIR / "generator_sign_reps.txt"
    json_path = OUT_DIR / "generator_sign_reps.json"

    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps({"blocks": rows}, indent=2), encoding="utf-8")

    print("=" * 80)
    print(f"saved {txt_path.relative_to(ROOT)}")
    print(f"saved {json_path.relative_to(ROOT)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
