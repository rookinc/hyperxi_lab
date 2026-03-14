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


def projected_action(W: np.ndarray, basis: np.ndarray) -> np.ndarray:
    return basis.T @ W @ basis


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


def commutator_norm(A: np.ndarray, B: np.ndarray) -> float:
    return float(np.linalg.norm(A @ B - B @ A))


def summarize_matrix(U: np.ndarray) -> str:
    label = scalar_sign_label(U)
    if label != "non-scalar":
        return label
    eig = np.linalg.eigvals(U)
    eig_str = ",".join(f"{x.real:+.3f}{x.imag:+.3f}i" for x in eig[: min(4, len(eig))])
    return f"eig[{eig_str}]"


def main():
    print("=" * 80)
    print("CHECK BLOCKWISE COMMUTATORS")
    print("=" * 80)

    ops = LocalOperatorFactory()

    UF = ops.build_U_F().astype(float)
    US = ops.build_U_S().astype(float)
    UV = ops.build_U_V().astype(float)
    H = ops.build_H_loc().astype(float)

    vals, vecs = np.linalg.eigh(H)
    blocks = eigenspace_blocks(vals)

    header = (
        f"{'block':>5}  {'lambda':>16}  {'dim':>3}  "
        f"{'F':>10}  {'S':>10}  {'V':>10}  "
        f"{'||[F,S]||':>10}  {'||[F,V]||':>10}  {'||[S,V]||':>10}"
    )
    print(header)
    print("-" * len(header))

    for block_id, (lam, idx) in enumerate(blocks[:20], start=1):
        basis = np.array(vecs[:, idx], dtype=float)

        PF = polar_unitary(projected_action(UF, basis))
        PS = polar_unitary(projected_action(US, basis))
        PV = polar_unitary(projected_action(UV, basis))

        labelF = scalar_sign_label(PF)
        labelS = scalar_sign_label(PS)
        labelV = scalar_sign_label(PV)

        cFS = commutator_norm(PF, PS)
        cFV = commutator_norm(PF, PV)
        cSV = commutator_norm(PS, PV)

        print(
            f"{block_id:5d}  {lam:16.12f}  {len(idx):3d}  "
            f"{labelF:>10}  {labelS:>10}  {labelV:>10}  "
            f"{cFS:10.3e}  {cFV:10.3e}  {cSV:10.3e}"
        )

    print()
    print("DETAILS FOR NON-SCALAR BLOCKS")
    print("-" * 80)

    for block_id, (lam, idx) in enumerate(blocks[:20], start=1):
        basis = np.array(vecs[:, idx], dtype=float)

        PF = polar_unitary(projected_action(UF, basis))
        PS = polar_unitary(projected_action(US, basis))
        PV = polar_unitary(projected_action(UV, basis))

        labels = [scalar_sign_label(PF), scalar_sign_label(PS), scalar_sign_label(PV)]
        if all(lbl != "non-scalar" for lbl in labels):
            continue

        print(f"\nblock {block_id}  lambda={lam:.12f}  dim={len(idx)}")
        print("F:", summarize_matrix(PF))
        print(np.round(PF, 6))
        print("S:", summarize_matrix(PS))
        print(np.round(PS, 6))
        print("V:", summarize_matrix(PV))
        print(np.round(PV, 6))
        print(
            "commutators:",
            f"||[F,S]||={commutator_norm(PF, PS):.6e}",
            f"||[F,V]||={commutator_norm(PF, PV):.6e}",
            f"||[S,V]||={commutator_norm(PS, PV):.6e}",
        )

    print("=" * 80)


if __name__ == "__main__":
    main()
