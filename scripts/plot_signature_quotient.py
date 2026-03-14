#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = ROOT / "reports" / "spectral" / "signature_transitions" / "signature_transition_quotient.json"
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


def main():
    if not IN_PATH.exists():
        raise SystemExit(f"Missing input file: {IN_PATH}")

    payload = json.loads(IN_PATH.read_text(encoding="utf-8"))

    signatures = payload["signatures"]
    top_pairs = payload["top_symmetrized_pairs"]

    coords3 = {sig: parse_sig(sig) for sig in signatures}

    # 2D projection chosen for readability:
    # x = F + 0.35*V
    # y = S + 0.35*V
    coords2 = {}
    for sig, (f, s, v) in coords3.items():
        x = f + 0.35 * v
        y = s + 0.35 * v
        coords2[sig] = (x, y)

    weights = [p["weight"] for p in top_pairs if p["weight"] > 0]
    wmax = max(weights) if weights else 1.0

    fig, ax = plt.subplots(figsize=(8, 7))

    # draw faint cube corners for context
    all_cube = [(f, s, v) for f in (-1, 1) for s in (-1, 1) for v in (-1, 1)]
    faint_points = []
    for f, s, v in all_cube:
        x = f + 0.35 * v
        y = s + 0.35 * v
        faint_points.append((x, y))

    ax.scatter(
        [p[0] for p in faint_points],
        [p[1] for p in faint_points],
        s=50,
        alpha=0.18,
    )

    # draw only nonzero quotient edges
    for pair in top_pairs:
        w = float(pair["weight"])
        if w <= 0:
            continue
        a = pair["sig_a"]
        b = pair["sig_b"]
        xa, ya = coords2[a]
        xb, yb = coords2[b]

        linewidth = 1.0 + 5.0 * (w / wmax)
        alpha = 0.25 + 0.65 * (w / wmax)

        ax.plot([xa, xb], [ya, yb], linewidth=linewidth, alpha=alpha)

        mx, my = (xa + xb) / 2.0, (ya + yb) / 2.0
        ax.text(mx, my, f"{w:.1f}", fontsize=8, ha="center", va="center")

    # draw observed signature nodes
    for sig in signatures:
        x, y = coords2[sig]
        ax.scatter([x], [y], s=220, zorder=3)
        ax.text(x, y + 0.12, sig, fontsize=10, ha="center")

    ax.set_title("Low-Energy Signature Transition Quotient")
    ax.set_xlabel("F + 0.35 V")
    ax.set_ylabel("S + 0.35 V")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.25)

    out_png = OUT_DIR / "signature_transition_quotient.png"
    fig.tight_layout()
    fig.savefig(out_png, dpi=200)
    plt.close(fig)

    print(f"saved {out_png.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
