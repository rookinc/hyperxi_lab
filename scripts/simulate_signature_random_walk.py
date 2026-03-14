#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = ROOT / "reports" / "spectral" / "signature_transitions" / "signature_transition_quotient.json"
OUT_DIR = ROOT / "reports" / "spectral" / "signature_transitions"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("=" * 80)
    print("SIMULATE SIGNATURE RANDOM WALK")
    print("=" * 80)

    if not IN_PATH.exists():
        raise SystemExit(f"Missing input file: {IN_PATH}")

    payload = json.loads(IN_PATH.read_text(encoding="utf-8"))
    signatures = payload["signatures"]
    W = np.array(payload["directed_quotient_matrix"], dtype=float)

    n = len(signatures)
    print(f"signature count: {n}")
    print()

    row_sums = W.sum(axis=1)
    P = np.zeros_like(W)

    for i in range(n):
        if row_sums[i] > 0:
            P[i, :] = W[i, :] / row_sums[i]
        else:
            P[i, i] = 1.0

    print("ROW-NORMALIZED TRANSITION MATRIX P")
    print("-" * 80)
    header = "sig".ljust(18) + " ".join(f"{sig:>18s}" for sig in signatures)
    print(header)
    for i, sig in enumerate(signatures):
        row = sig.ljust(18) + " ".join(f"{P[i,j]:18.6f}" for j in range(n))
        print(row)
    print()

    # stationary distribution from left eigenvector of eigenvalue 1
    evals, evecs = np.linalg.eig(P.T)
    idx = int(np.argmin(np.abs(evals - 1.0)))
    v = np.real(evecs[:, idx])
    v = np.abs(v)
    if v.sum() == 0:
        raise RuntimeError("Failed to compute stationary distribution.")
    pi = v / v.sum()

    print("STATIONARY DISTRIBUTION")
    print("-" * 80)
    ranking = sorted(
        [(signatures[i], float(pi[i])) for i in range(n)],
        key=lambda x: x[1],
        reverse=True,
    )
    for sig, prob in ranking:
        print(f"{sig:18s}  {prob:.6f}")
    print()

    # simple power iteration from each basis state
    steps = 25
    print(f"POWER ITERATION TRAJECTORIES ({steps} steps)")
    print("-" * 80)
    for start in range(n):
        x = np.zeros(n, dtype=float)
        x[start] = 1.0
        for _ in range(steps):
            x = x @ P
        print(f"start {signatures[start]:18s} -> " + " ".join(f"{x[i]:.4f}" for i in range(n)))
    print()

    # detect strongest directed probability moves
    edges = []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if P[i, j] > 0:
                edges.append(
                    {
                        "src": signatures[i],
                        "dst": signatures[j],
                        "prob": float(P[i, j]),
                    }
                )
    edges.sort(key=lambda x: x["prob"], reverse=True)

    print("TOP DIRECTED TRANSITION PROBABILITIES")
    print("-" * 80)
    for e in edges[:15]:
        print(f"{e['src']:18s} -> {e['dst']:18s}   p={e['prob']:.6f}")
    print()

    # two-step return and mixing glimpse
    P2 = P @ P
    print("TWO-STEP RETURN PROBABILITIES")
    print("-" * 80)
    for i, sig in enumerate(signatures):
        print(f"{sig:18s}  P^2[i,i]={P2[i,i]:.6f}")
    print()

    txt_lines = []
    txt_lines.append("=" * 80)
    txt_lines.append("SIGNATURE RANDOM WALK")
    txt_lines.append("=" * 80)
    txt_lines.append(f"signature count: {n}")
    txt_lines.append("")
    txt_lines.append("STATIONARY DISTRIBUTION")
    txt_lines.append("-" * 80)
    for sig, prob in ranking:
        txt_lines.append(f"{sig:18s}  {prob:.6f}")
    txt_lines.append("")
    txt_lines.append("TOP DIRECTED TRANSITION PROBABILITIES")
    txt_lines.append("-" * 80)
    for e in edges[:20]:
        txt_lines.append(f"{e['src']:18s} -> {e['dst']:18s}   p={e['prob']:.6f}")
    txt_lines.append("")
    txt_lines.append("TWO-STEP RETURN PROBABILITIES")
    txt_lines.append("-" * 80)
    for i, sig in enumerate(signatures):
        txt_lines.append(f"{sig:18s}  P^2[i,i]={P2[i,i]:.6f}")
    txt_lines.append("")

    txt_path = OUT_DIR / "signature_random_walk.txt"
    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")

    json_path = OUT_DIR / "signature_random_walk.json"
    json_path.write_text(
        json.dumps(
            {
                "signatures": signatures,
                "transition_matrix": P.tolist(),
                "stationary_distribution": {signatures[i]: float(pi[i]) for i in range(n)},
                "top_directed_edges": edges[:20],
                "two_step_return_probabilities": {signatures[i]: float(P2[i, i]) for i in range(n)},
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"saved {txt_path.relative_to(ROOT)}")
    print(f"saved {json_path.relative_to(ROOT)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
