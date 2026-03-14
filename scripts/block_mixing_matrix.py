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
    """
    Matrix for the action from block j into block i:
        B_ij = basis_i^T U basis_j
    """
    return basis_i.T @ U @ basis_j


def fro_norm(M: np.ndarray) -> float:
    return float(np.linalg.norm(M))


def max_abs(M: np.ndarray) -> float:
    return float(np.max(np.abs(M))) if M.size else 0.0


def print_matrix(name: str, M: np.ndarray, width: int = 10) -> None:
    print(name)
    for row in M:
        print(" ".join(f"{x:{width}.3e}" for x in row))
    print()


def main():
    print("=" * 80)
    print("BLOCK MIXING MATRIX")
    print("=" * 80)

    ops = LocalOperatorFactory()

    UF = ops.build_U_F().astype(float)
    US = ops.build_U_S().astype(float)
    UV = ops.build_U_V().astype(float)
    H = ops.build_H_loc().astype(float)

    vals, vecs = np.linalg.eigh(H)
    blocks = eigenspace_blocks(vals)

    # Focus on the low spectrum you have been studying.
    low_blocks = []
    for block_id, (lam, idx) in enumerate(blocks[:20], start=1):
        basis = np.array(vecs[:, idx], dtype=float)
        low_blocks.append(
            {
                "block": block_id,
                "lambda": lam,
                "dim": len(idx),
                "basis": basis,
            }
        )

    n = len(low_blocks)

    print(f"number of low blocks: {n}")
    print()

    for opname, U in (("F", UF), ("S", US), ("V", UV)):
        print("=" * 80)
        print(f"OPERATOR {opname}")
        print("=" * 80)

        norm_mat = np.zeros((n, n), dtype=float)
        max_mat = np.zeros((n, n), dtype=float)

        for i, bi in enumerate(low_blocks):
            for j, bj in enumerate(low_blocks):
                Bij = block_operator(U, bi["basis"], bj["basis"])
                norm_mat[i, j] = fro_norm(Bij)
                max_mat[i, j] = max_abs(Bij)

        print("Frobenius norms ||P_i U P_j||")
        header = "blk ".ljust(5) + " ".join(f"{b['block']:>9d}" for b in low_blocks)
        print(header)
        for i, bi in enumerate(low_blocks):
            row = f"{bi['block']:>3d} ".ljust(5) + " ".join(f"{norm_mat[i,j]:9.3e}" for j in range(n))
            print(row)
        print()

        print("Max-entry norms max|P_i U P_j|")
        print(header)
        for i, bi in enumerate(low_blocks):
            row = f"{bi['block']:>3d} ".ljust(5) + " ".join(f"{max_mat[i,j]:9.3e}" for j in range(n))
            print(row)
        print()

        off_diag = norm_mat.copy()
        np.fill_diagonal(off_diag, 0.0)

        max_off = float(np.max(off_diag))
        where = np.argwhere(np.isclose(off_diag, max_off))
        print(f"largest off-diagonal mixing norm: {max_off:.6e}")
        if where.size:
            for pair in where[:10]:
                i, j = int(pair[0]), int(pair[1])
                print(
                    f"  block {low_blocks[i]['block']} <- {opname} <- block {low_blocks[j]['block']}"
                    f"   (lambdas {low_blocks[i]['lambda']:.12f}, {low_blocks[j]['lambda']:.12f})"
                )
        print()

        # Also summarize by same-eigenvalue vs different-eigenvalue
        same_vals = []
        diff_vals = []
        for i, bi in enumerate(low_blocks):
            for j, bj in enumerate(low_blocks):
                if i == j:
                    continue
                val = norm_mat[i, j]
                if abs(bi["lambda"] - bj["lambda"]) < 1e-8:
                    same_vals.append(val)
                else:
                    diff_vals.append(val)

        same_max = max(same_vals) if same_vals else 0.0
        diff_max = max(diff_vals) if diff_vals else 0.0
        print(f"max off-diagonal mixing within degenerate lambda blocks: {same_max:.6e}")
        print(f"max off-diagonal mixing across different lambda blocks: {diff_max:.6e}")
        print()

    print("=" * 80)
    print("INTERPRETATION GUIDE")
    print("=" * 80)
    print("If off-diagonal norms are numerically ~0, the operator preserves each block.")
    print("If same-lambda off-diagonal norms are nonzero, hidden structure may live inside degenerate sectors.")
    print("If cross-lambda norms are nonzero, the generator does not preserve the H_loc eigenspaces.")
    print("=" * 80)


if __name__ == "__main__":
    main()
