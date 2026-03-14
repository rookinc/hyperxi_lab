#!/usr/bin/env python3

from __future__ import annotations

import itertools
import json
from math import prod
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = ROOT / "reports" / "spectral" / "signature_transitions" / "signature_random_walk.json"
OUT_DIR = ROOT / "reports" / "spectral" / "signature_transitions"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def canonical_cycle(nodes: tuple[int, ...]) -> tuple[int, ...]:
    """
    Put a simple directed cycle into a canonical representative up to cyclic rotation.
    We do not identify reversal, since direction matters for Markov flow.
    """
    rots = [nodes[i:] + nodes[:i] for i in range(len(nodes))]
    return min(rots)


def cycle_probability(P: np.ndarray, cyc: tuple[int, ...]) -> float:
    n = len(cyc)
    return prod(P[cyc[i], cyc[(i + 1) % n]] for i in range(n))


def main():
    print("=" * 80)
    print("FIND SIGNATURE CYCLES")
    print("=" * 80)

    if not IN_PATH.exists():
        raise SystemExit(f"Missing input file: {IN_PATH}")

    payload = json.loads(IN_PATH.read_text(encoding="utf-8"))
    signatures = payload["signatures"]
    P = np.array(payload["transition_matrix"], dtype=float)

    n = len(signatures)
    print(f"signature count: {n}")
    print()

    all_cycles = {2: [], 3: [], 4: [], 5: []}
    seen = {2: set(), 3: set(), 4: set(), 5: set()}

    for L in [2, 3, 4, 5]:
        for cyc in itertools.permutations(range(n), L):
            can = canonical_cycle(cyc)
            if can in seen[L]:
                continue
            seen[L].add(can)

            p = cycle_probability(P, cyc)
            if p <= 0:
                continue

            entry = {
                "indices": list(cyc),
                "states": [signatures[i] for i in cyc],
                "probability": float(p),
                "mean_edge_probability": float(p ** (1.0 / L)),
            }
            all_cycles[L].append(entry)

        all_cycles[L].sort(key=lambda x: x["probability"], reverse=True)

    print("TOP 2-CYCLES")
    print("-" * 80)
    for c in all_cycles[2][:10]:
        a, b = c["states"]
        print(
            f"{a} -> {b} -> {a}   "
            f"p={c['probability']:.6f}   "
            f"geom_mean={c['mean_edge_probability']:.6f}"
        )
    print()

    print("TOP 3-CYCLES")
    print("-" * 80)
    for c in all_cycles[3][:10]:
        s = " -> ".join(c["states"] + [c["states"][0]])
        print(
            f"{s}   p={c['probability']:.6f}   "
            f"geom_mean={c['mean_edge_probability']:.6f}"
        )
    print()

    print("TOP 4-CYCLES")
    print("-" * 80)
    for c in all_cycles[4][:10]:
        s = " -> ".join(c["states"] + [c["states"][0]])
        print(
            f"{s}   p={c['probability']:.6f}   "
            f"geom_mean={c['mean_edge_probability']:.6f}"
        )
    print()

    print("TOP 5-CYCLES")
    print("-" * 80)
    for c in all_cycles[5][:10]:
        s = " -> ".join(c["states"] + [c["states"][0]])
        print(
            f"{s}   p={c['probability']:.6f}   "
            f"geom_mean={c['mean_edge_probability']:.6f}"
        )
    print()

    # strongest outgoing edge per state
    print("STRONGEST OUTGOING EDGE PER SIGNATURE")
    print("-" * 80)
    strongest = []
    for i, sig in enumerate(signatures):
        row = P[i].copy()
        row[i] = -1.0
        j = int(np.argmax(row))
        strongest.append(
            {
                "src": sig,
                "dst": signatures[j],
                "probability": float(P[i, j]),
            }
        )
        print(f"{sig:18s} -> {signatures[j]:18s}   p={P[i,j]:.6f}")
    print()

    txt_lines = []
    txt_lines.append("=" * 80)
    txt_lines.append("SIGNATURE CYCLES")
    txt_lines.append("=" * 80)

    for L in [2, 3, 4, 5]:
        txt_lines.append(f"TOP {L}-CYCLES")
        txt_lines.append("-" * 80)
        for c in all_cycles[L][:15]:
            s = " -> ".join(c["states"] + [c["states"][0]])
            txt_lines.append(
                f"{s}   p={c['probability']:.6f}   geom_mean={c['mean_edge_probability']:.6f}"
            )
        txt_lines.append("")

    txt_lines.append("STRONGEST OUTGOING EDGE PER SIGNATURE")
    txt_lines.append("-" * 80)
    for e in strongest:
        txt_lines.append(
            f"{e['src']:18s} -> {e['dst']:18s}   p={e['probability']:.6f}"
        )
    txt_lines.append("")

    txt_path = OUT_DIR / "signature_cycles.txt"
    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")

    json_path = OUT_DIR / "signature_cycles.json"
    json_path.write_text(
        json.dumps(
            {
                "signatures": signatures,
                "top_cycles": {str(L): all_cycles[L][:20] for L in [2, 3, 4, 5]},
                "strongest_outgoing": strongest,
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
