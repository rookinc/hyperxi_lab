#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IN_Q = ROOT / "reports" / "spectral" / "signature_transitions" / "signature_transition_quotient.json"
IN_RW = ROOT / "reports" / "spectral" / "signature_transitions" / "signature_random_walk.json"
IN_H = ROOT / "reports" / "spectral" / "signature_transitions" / "effective_signature_hamiltonian.json"
OUT_DIR = ROOT / "reports" / "spectral" / "signature_transitions"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_sig(sig: str) -> tuple[int, int, int]:
    sig = sig.strip()[1:-1]
    parts = [p.strip() for p in sig.split(",")]
    out = []
    for p in parts:
        if p == "+I":
            out.append(1)
        elif p == "-I":
            out.append(-1)
        else:
            raise ValueError(f"Unexpected signature entry: {p}")
    return tuple(out)  # type: ignore[return-value]


def project(sig: str) -> tuple[float, float]:
    f, s, v = parse_sig(sig)
    x = f + 0.35 * v
    y = s + 0.35 * v
    return x, y


def size_from_weights(values: np.ndarray, base: float = 400.0, scale: float = 2200.0) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if values.max() <= 0:
        return np.full_like(values, base)
    return base + scale * values / values.max()


def colors_from_mode(values: np.ndarray) -> np.ndarray:
    vmax = np.max(np.abs(values))
    if vmax <= 0:
        vmax = 1.0
    return values / vmax


def main():
    if not IN_Q.exists() or not IN_RW.exists() or not IN_H.exists():
        raise SystemExit("Missing one or more input files in reports/spectral/signature_transitions/")

    q_payload = json.loads(IN_Q.read_text(encoding="utf-8"))
    rw_payload = json.loads(IN_RW.read_text(encoding="utf-8"))
    h_payload = json.loads(IN_H.read_text(encoding="utf-8"))

    signatures = q_payload["signatures"]
    A = np.array(q_payload["symmetrized_quotient_matrix"], dtype=float)
    np.fill_diagonal(A, 0.0)

    pi = np.array([rw_payload["stationary_distribution"][sig] for sig in signatures], dtype=float)

    Heff = np.array(h_payload["effective_hamiltonian"], dtype=float)
    evals, evecs = np.linalg.eigh(Heff)

    gs = np.abs(evecs[:, 0])
    gs = gs / gs.sum()

    mode1 = evecs[:, 1] if len(signatures) > 1 else np.zeros(len(signatures))
    mode2 = evecs[:, 2] if len(signatures) > 2 else np.zeros(len(signatures))

    coords = {sig: project(sig) for sig in signatures}
    weights = [A[i, j] for i in range(len(signatures)) for j in range(i + 1, len(signatures)) if A[i, j] > 0]
    wmax = max(weights) if weights else 1.0

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    panels = [
        ("Stationary distribution", pi, "size"),
        ("Ground-state weights", gs, "size"),
        (f"First excited mode (λ={evals[1]:.3f})", mode1, "signed"),
        (f"Second excited mode (λ={evals[2]:.3f})", mode2, "signed"),
    ]

    for ax, (title, vals, kind) in zip(axes.flat, panels):
        # faint cube context
        all_cube = [(f, s, v) for f in (-1, 1) for s in (-1, 1) for v in (-1, 1)]
        faint = [(f + 0.35 * v, s + 0.35 * v) for f, s, v in all_cube]
        ax.scatter([p[0] for p in faint], [p[1] for p in faint], s=40, alpha=0.12)

        # edges
        for i in range(len(signatures)):
            for j in range(i + 1, len(signatures)):
                if A[i, j] <= 0:
                    continue
                xa, ya = coords[signatures[i]]
                xb, yb = coords[signatures[j]]
                lw = 1.0 + 5.0 * (A[i, j] / wmax)
                alpha = 0.20 + 0.60 * (A[i, j] / wmax)
                ax.plot([xa, xb], [ya, yb], linewidth=lw, alpha=alpha, zorder=1)

        xs = np.array([coords[sig][0] for sig in signatures])
        ys = np.array([coords[sig][1] for sig in signatures])

        if kind == "size":
            sizes = size_from_weights(np.asarray(vals, dtype=float))
            ax.scatter(xs, ys, s=sizes, zorder=3)
            for sig, x, y, v in zip(signatures, xs, ys, vals):
                ax.text(x, y + 0.14, f"{sig}\n{v:.3f}", ha="center", va="bottom", fontsize=9)
        else:
            cvals = colors_from_mode(np.asarray(vals, dtype=float))
            sizes = np.full(len(signatures), 900.0)
            sc = ax.scatter(xs, ys, c=cvals, s=sizes, cmap="coolwarm", vmin=-1, vmax=1, zorder=3)
            for sig, x, y, v in zip(signatures, xs, ys, vals):
                ax.text(x, y + 0.14, f"{sig}\n{v:+.3f}", ha="center", va="bottom", fontsize=9)
            fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)

        ax.set_title(title)
        ax.set_xlabel("F + 0.35 V")
        ax.set_ylabel("S + 0.35 V")
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.25)

    fig.suptitle("Signature Quotient: Stationary State and Effective Modes", fontsize=14)
    fig.tight_layout()

    out_png = OUT_DIR / "signature_modes.png"
    fig.savefig(out_png, dpi=220)
    plt.close(fig)

    print(f"saved {out_png.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
