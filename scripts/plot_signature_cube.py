#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "reports" / "spectral" / "signature_transitions" / "signature_transition_quotient_032_blocks.json"
DEFAULT_OUT = ROOT / "reports" / "spectral" / "signature_transitions" / "signature_cube_032_blocks.png"


def parse_sig(sig: str) -> tuple[int, int, int]:
    s = sig.strip().strip("()")
    a, b, c = [x.strip() for x in s.split(",")]
    return tuple(1 if x == "+I" else -1 for x in (a, b, c))


def hamming(sig_a: str, sig_b: str) -> int:
    a = parse_sig(sig_a)
    b = parse_sig(sig_b)
    return sum(int(x != y) for x, y in zip(a, b))


def load_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_coords(signatures: list[str]) -> dict[str, tuple[float, float]]:
    # Simple oblique projection from (F,S,V) cube to plane
    coords = {}
    for sig in signatures:
        f, s, v = parse_sig(sig)
        x = f + 0.35 * v
        y = s + 0.35 * v
        coords[sig] = (x, y)
    return coords


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--threshold", type=float, default=0.0, help="Hide directed edges with weight below this value")
    ap.add_argument("--top", type=int, default=0, help="If > 0, only draw the top-N directed edges by weight")
    args = ap.parse_args()

    payload = load_payload(args.input)
    sigs = payload["signatures"]
    M = np.array(payload["directed_quotient_matrix"], dtype=float)
    pi = payload.get("stationary_distribution", {})
    coords = build_coords(sigs)

    edges = []
    n = len(sigs)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            w = float(M[i, j])
            if w <= args.threshold:
                continue
            edges.append((w, i, j))

    edges.sort(reverse=True)
    if args.top > 0:
        edges = edges[: args.top]

    fig, ax = plt.subplots(figsize=(10, 8))

    # Draw cube edges first: connect signatures differing by one sign flip
    for i, sa in enumerate(sigs):
        xa, ya = coords[sa]
        for j in range(i + 1, n):
            sb = sigs[j]
            xb, yb = coords[sb]
            if hamming(sa, sb) == 1:
                ax.plot([xa, xb], [ya, yb], linewidth=1.2, alpha=0.22)

    # Draw transport edges
    if edges:
        max_w = max(w for w, _, _ in edges)
    else:
        max_w = 1.0

    for w, i, j in edges:
        sa = sigs[i]
        sb = sigs[j]
        xa, ya = coords[sa]
        xb, yb = coords[sb]

        dx = xb - xa
        dy = yb - ya
        norm = (dx * dx + dy * dy) ** 0.5
        if norm == 0:
            continue

        # shrink arrow away from node centers
        shrink = 0.12
        x0 = xa + shrink * dx / norm
        y0 = ya + shrink * dy / norm
        x1 = xb - shrink * dx / norm
        y1 = yb - shrink * dy / norm

        lw = 1.0 + 5.0 * (w / max_w)
        alpha = 0.18 + 0.65 * (w / max_w)

        ax.annotate(
            "",
            xy=(x1, y1),
            xytext=(x0, y0),
            arrowprops=dict(arrowstyle="->", lw=lw, alpha=alpha),
            zorder=2,
        )

        mx = (x0 + x1) / 2.0
        my = (y0 + y1) / 2.0
        ax.text(mx, my, f"{w:.1f}", fontsize=8, ha="center", va="center")

    # Draw all 8 cube positions faintly, even if absent
    all_sigs = [
        f"({' +I' if f > 0 else '-I'},{' +I' if s > 0 else '-I'},{' +I' if v > 0 else '-I'})".replace(" ", "")
        for f in (-1, 1) for s in (-1, 1) for v in (-1, 1)
    ]
    all_coords = build_coords(all_sigs)
    observed = set(sigs)

    for sig in all_sigs:
        x, y = all_coords[sig]
        if sig in observed:
            continue
        ax.scatter([x], [y], s=90, alpha=0.15, zorder=1)

    # Draw observed nodes
    for sig in sigs:
        x, y = coords[sig]
        size = 300 + 3200 * float(pi.get(sig, 0.0))
        ax.scatter([x], [y], s=size, zorder=3)
        label = f"{sig}\n{pi.get(sig, 0.0):.3f}"
        ax.text(x, y + 0.13, label, fontsize=10, ha="center")

    ax.set_title("Signature Cube with Weighted Quotient Transport")
    ax.set_xlabel("F + 0.35 V")
    ax.set_ylabel("S + 0.35 V")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.25)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(args.output, dpi=200)
    plt.close(fig)

    print(f"saved {args.output}")


if __name__ == "__main__":
    main()
