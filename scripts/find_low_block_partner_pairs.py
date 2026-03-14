#!/usr/bin/env python3

from __future__ import annotations

import numpy as np

from hyperxi.spectral.operators import LocalOperatorFactory


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


def hamming_signature_distance(sig_a: tuple[str, str, str], sig_b: tuple[str, str, str]) -> int:
    return sum(a != b for a, b in zip(sig_a, sig_b))


def signature_str(sig: tuple[str, str, str]) -> str:
    return f"({sig[0]},{sig[1]},{sig[2]})"


def main():
    print("=" * 80)
    print("FIND LOW BLOCK PARTNER PAIRS")
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
            }
        )

    n = len(blocks)

    # Directed norm matrices
    MF = np.zeros((n, n), dtype=float)
    MS = np.zeros((n, n), dtype=float)
    MV = np.zeros((n, n), dtype=float)

    for i, bi in enumerate(blocks):
        for j, bj in enumerate(blocks):
            MF[i, j] = fro_norm(block_operator(UF, bi["basis"], bj["basis"]))
            MS[i, j] = fro_norm(block_operator(US, bi["basis"], bj["basis"]))
            MV[i, j] = fro_norm(block_operator(UV, bi["basis"], bj["basis"]))

    # Remove diagonal for partner analysis
    np.fill_diagonal(MF, 0.0)
    np.fill_diagonal(MS, 0.0)
    np.fill_diagonal(MV, 0.0)

    # Combined directed and symmetrized partner weight
    MD = MF + MS + MV
    MSYM = MD + MD.T

    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            bij = float(MD[i, j])
            bji = float(MD[j, i])
            sym = float(MSYM[i, j])

            sig_i = blocks[i]["signature"]
            sig_j = blocks[j]["signature"]

            pairs.append(
                {
                    "i": i,
                    "j": j,
                    "block_i": blocks[i]["block"],
                    "block_j": blocks[j]["block"],
                    "lambda_i": blocks[i]["lambda"],
                    "lambda_j": blocks[j]["lambda"],
                    "dim_i": blocks[i]["dim"],
                    "dim_j": blocks[j]["dim"],
                    "sig_i": sig_i,
                    "sig_j": sig_j,
                    "sig_i_str": signature_str(sig_i),
                    "sig_j_str": signature_str(sig_j),
                    "hamming": hamming_signature_distance(sig_i, sig_j),
                    "w_ij": bij,
                    "w_ji": bji,
                    "sym_weight": sym,
                    "balance": min(bij, bji) / max(bij, bji) if max(bij, bji) > 0 else 0.0,
                }
            )

    pairs.sort(key=lambda x: (x["sym_weight"], x["balance"]), reverse=True)

    print("TOP 25 PARTNER PAIRS BY SYMMETRIZED WEIGHT")
    print("-" * 80)
    for p in pairs[:25]:
        print(
            f"blocks {p['block_i']:2d} <-> {p['block_j']:2d}   "
            f"sym={p['sym_weight']:.6f}   "
            f"dir=({p['w_ij']:.6f},{p['w_ji']:.6f})   "
            f"balance={p['balance']:.3f}   "
            f"hamming={p['hamming']}   "
            f"{p['sig_i_str']} <-> {p['sig_j_str']}"
        )

    print()
    print("TOP 15 MOST BALANCED STRONG PAIRS")
    print("-" * 80)
    balanced = [p for p in pairs if p["sym_weight"] > 1.0]
    balanced.sort(key=lambda x: (x["balance"], x["sym_weight"]), reverse=True)
    for p in balanced[:15]:
        print(
            f"blocks {p['block_i']:2d} <-> {p['block_j']:2d}   "
            f"sym={p['sym_weight']:.6f}   "
            f"dir=({p['w_ij']:.6f},{p['w_ji']:.6f})   "
            f"balance={p['balance']:.3f}   "
            f"hamming={p['hamming']}   "
            f"{p['sig_i_str']} <-> {p['sig_j_str']}"
        )

    print()
    print("SUMMARY BY SIGNATURE HAMMING DISTANCE")
    print("-" * 80)
    for h in range(4):
        sub = [p["sym_weight"] for p in pairs if p["hamming"] == h]
        if sub:
            print(
                f"hamming={h}   count={len(sub):3d}   "
                f"mean={np.mean(sub):.6f}   max={np.max(sub):.6f}"
            )

    print()
    print("TOP 10 PAIRS WITH HAMMING DISTANCE 0")
    print("-" * 80)
    same = [p for p in pairs if p["hamming"] == 0]
    for p in same[:10]:
        print(
            f"blocks {p['block_i']:2d} <-> {p['block_j']:2d}   "
            f"sym={p['sym_weight']:.6f}   "
            f"dir=({p['w_ij']:.6f},{p['w_ji']:.6f})   "
            f"{p['sig_i_str']}"
        )

    print()
    print("TOP 10 PAIRS WITH HAMMING DISTANCE 1")
    print("-" * 80)
    one = [p for p in pairs if p["hamming"] == 1]
    for p in one[:10]:
        print(
            f"blocks {p['block_i']:2d} <-> {p['block_j']:2d}   "
            f"sym={p['sym_weight']:.6f}   "
            f"dir=({p['w_ij']:.6f},{p['w_ji']:.6f})   "
            f"{p['sig_i_str']} <-> {p['sig_j_str']}"
        )

    print()
    print("TOP 10 PAIRS WITH HAMMING DISTANCE 2 OR 3")
    print("-" * 80)
    far = [p for p in pairs if p["hamming"] >= 2]
    for p in far[:10]:
        print(
            f"blocks {p['block_i']:2d} <-> {p['block_j']:2d}   "
            f"sym={p['sym_weight']:.6f}   "
            f"dir=({p['w_ij']:.6f},{p['w_ji']:.6f})   "
            f"{p['sig_i_str']} <-> {p['sig_j_str']}"
        )

    print()
    print("=" * 80)
    print("INTERPRETATION GUIDE")
    print("=" * 80)
    print("High symmetrized weight = strong two-way partnership.")
    print("High balance = nearly reciprocal coupling.")
    print("Hamming distance compares sign signatures blockwise.")
    print("If strongest pairs cluster at hamming=1, the low block graph is parity-adjacent.")
    print("If strongest pairs cluster at hamming=0, partnering preserves sign sector.")
    print("=" * 80)


if __name__ == "__main__":
    main()
