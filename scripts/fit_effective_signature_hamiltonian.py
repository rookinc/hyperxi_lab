#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IN_Q = ROOT / "reports" / "spectral" / "signature_transitions" / "signature_transition_quotient.json"
IN_RW = ROOT / "reports" / "spectral" / "signature_transitions" / "signature_random_walk.json"
OUT_DIR = ROOT / "reports" / "spectral" / "signature_transitions"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def fmt_vec(v: np.ndarray) -> str:
    return "[" + ", ".join(f"{x: .6f}" for x in v) + "]"


def main():
    print("=" * 80)
    print("FIT EFFECTIVE SIGNATURE HAMILTONIAN")
    print("=" * 80)

    if not IN_Q.exists():
        raise SystemExit(f"Missing quotient file: {IN_Q}")
    if not IN_RW.exists():
        raise SystemExit(f"Missing random-walk file: {IN_RW}")

    q_payload = json.loads(IN_Q.read_text(encoding="utf-8"))
    rw_payload = json.loads(IN_RW.read_text(encoding="utf-8"))

    signatures = q_payload["signatures"]
    Wdir = np.array(q_payload["directed_quotient_matrix"], dtype=float)
    Wsym = np.array(q_payload["symmetrized_quotient_matrix"], dtype=float)

    P = np.array(rw_payload["transition_matrix"], dtype=float)
    pi = np.array([rw_payload["stationary_distribution"][sig] for sig in signatures], dtype=float)

    n = len(signatures)
    print(f"signature count: {n}")
    print()

    # Effective symmetric adjacency / coupling matrix
    A = Wsym.copy()
    np.fill_diagonal(A, 0.0)

    deg = A.sum(axis=1)
    D = np.diag(deg)

    # Combinatorial and normalized Laplacians
    L = D - A
    with np.errstate(divide="ignore"):
        dinv_sqrt = np.where(deg > 0, 1.0 / np.sqrt(deg), 0.0)
    DinvSqrt = np.diag(dinv_sqrt)
    Lnorm = np.eye(n) - DinvSqrt @ A @ DinvSqrt

    # Simple "Hamiltonian-like" choice:
    # H_eff = -A, so strong couplings lower energy.
    Heff = -A

    evals_H, evecs_H = np.linalg.eigh(Heff)
    evals_L, evecs_L = np.linalg.eigh(L)
    evals_Ln, evecs_Ln = np.linalg.eigh(Lnorm)

    # Compare Heff ground state to sqrt(pi) and pi
    gs = np.abs(evecs_H[:, 0])
    gs = gs / gs.sum()

    sqrt_pi = np.sqrt(pi)
    sqrt_pi = sqrt_pi / np.linalg.norm(sqrt_pi)

    gs_unit = np.abs(evecs_H[:, 0])
    gs_unit = gs_unit / np.linalg.norm(gs_unit)

    overlap_sqrt_pi = float(np.dot(gs_unit, sqrt_pi))
    corr_pi = float(np.corrcoef(gs, pi)[0, 1]) if np.std(gs) > 0 and np.std(pi) > 0 else 0.0

    # Spectral gap of Heff and Laplacians
    gap_H = float(evals_H[1] - evals_H[0]) if n >= 2 else 0.0
    gap_L = float(evals_L[1] - evals_L[0]) if n >= 2 else 0.0
    gap_Ln = float(evals_Ln[1] - evals_Ln[0]) if n >= 2 else 0.0

    print("SIGNATURE ORDER")
    print("-" * 80)
    for i, sig in enumerate(signatures):
        print(f"{i:2d}  {sig}")
    print()

    print("SYMMETRIC COUPLING MATRIX A")
    print("-" * 80)
    header = "idx".ljust(4) + " ".join(f"{i:>11d}" for i in range(n))
    print(header)
    for i in range(n):
        row = f"{i:<4d}" + " ".join(f"{A[i,j]:11.6f}" for j in range(n))
        print(row)
    print()

    print("EFFECTIVE HAMILTONIAN H_eff = -A")
    print("-" * 80)
    print(f"ground energy: {evals_H[0]:.6f}")
    print(f"1st gap      : {gap_H:.6f}")
    print("lowest eigenvalues:")
    for k, lam in enumerate(evals_H[: min(5, n)]):
        print(f"  {k}: {lam:.6f}")
    print()

    print("GROUND-STATE WEIGHT ON SIGNATURES")
    print("-" * 80)
    for sig, w in sorted(zip(signatures, gs), key=lambda x: x[1], reverse=True):
        print(f"{sig:18s}  {w:.6f}")
    print()

    print("STATIONARY DISTRIBUTION")
    print("-" * 80)
    for sig, w in sorted(zip(signatures, pi), key=lambda x: x[1], reverse=True):
        print(f"{sig:18s}  {w:.6f}")
    print()

    print("COMPARISON")
    print("-" * 80)
    print(f"overlap(|gs>, sqrt(pi)) = {overlap_sqrt_pi:.6f}")
    print(f"corr(gs_weights, pi)    = {corr_pi:.6f}")
    print()

    print("COMBINATORIAL LAPLACIAN SPECTRUM")
    print("-" * 80)
    print(f"algebraic connectivity gap: {gap_L:.6f}")
    for k, lam in enumerate(evals_L[: min(5, n)]):
        print(f"  {k}: {lam:.6f}")
    print()

    print("NORMALIZED LAPLACIAN SPECTRUM")
    print("-" * 80)
    print(f"normalized gap: {gap_Ln:.6f}")
    for k, lam in enumerate(evals_Ln[: min(5, n)]):
        print(f"  {k}: {lam:.6f}")
    print()

    print("LOWEST H_eff EIGENVECTORS")
    print("-" * 80)
    for k in range(min(3, n)):
        vec = evecs_H[:, k]
        vec = vec / np.linalg.norm(vec)
        print(f"mode {k}  lambda={evals_H[k]:.6f}")
        for sig, amp in zip(signatures, vec):
            print(f"  {sig:18s}  {amp: .6f}")
        print()

    txt_lines = []
    txt_lines.append("=" * 80)
    txt_lines.append("EFFECTIVE SIGNATURE HAMILTONIAN")
    txt_lines.append("=" * 80)
    txt_lines.append("SIGNATURE ORDER")
    txt_lines.append("-" * 80)
    for i, sig in enumerate(signatures):
        txt_lines.append(f"{i:2d}  {sig}")
    txt_lines.append("")
    txt_lines.append("GROUND-STATE WEIGHT ON SIGNATURES")
    txt_lines.append("-" * 80)
    for sig, w in sorted(zip(signatures, gs), key=lambda x: x[1], reverse=True):
        txt_lines.append(f"{sig:18s}  {w:.6f}")
    txt_lines.append("")
    txt_lines.append("STATIONARY DISTRIBUTION")
    txt_lines.append("-" * 80)
    for sig, w in sorted(zip(signatures, pi), key=lambda x: x[1], reverse=True):
        txt_lines.append(f"{sig:18s}  {w:.6f}")
    txt_lines.append("")
    txt_lines.append("SPECTRAL SUMMARY")
    txt_lines.append("-" * 80)
    txt_lines.append(f"H_eff ground energy: {evals_H[0]:.6f}")
    txt_lines.append(f"H_eff first gap   : {gap_H:.6f}")
    txt_lines.append(f"Laplacian gap     : {gap_L:.6f}")
    txt_lines.append(f"Norm Lap gap      : {gap_Ln:.6f}")
    txt_lines.append(f"overlap(|gs>, sqrt(pi)) = {overlap_sqrt_pi:.6f}")
    txt_lines.append(f"corr(gs_weights, pi)    = {corr_pi:.6f}")
    txt_lines.append("")

    txt_path = OUT_DIR / "effective_signature_hamiltonian.txt"
    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")

    json_payload = {
        "signatures": signatures,
        "symmetric_coupling_matrix": A.tolist(),
        "effective_hamiltonian": Heff.tolist(),
        "heff_eigenvalues": evals_H.tolist(),
        "laplacian_eigenvalues": evals_L.tolist(),
        "normalized_laplacian_eigenvalues": evals_Ln.tolist(),
        "ground_state_weights": {sig: float(w) for sig, w in zip(signatures, gs)},
        "stationary_distribution": {sig: float(w) for sig, w in zip(signatures, pi)},
        "heff_gap": gap_H,
        "laplacian_gap": gap_L,
        "normalized_laplacian_gap": gap_Ln,
        "overlap_gs_sqrt_pi": overlap_sqrt_pi,
        "corr_gs_pi": corr_pi,
    }
    json_path = OUT_DIR / "effective_signature_hamiltonian.json"
    json_path.write_text(json.dumps(json_payload, indent=2), encoding="utf-8")

    print(f"saved {txt_path.relative_to(ROOT)}")
    print(f"saved {json_path.relative_to(ROOT)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
