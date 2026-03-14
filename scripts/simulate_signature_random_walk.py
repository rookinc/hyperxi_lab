#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np


def load_payload(path: Path):
    payload = json.loads(path.read_text())
    sigs = payload["signatures"]
    P = np.array(payload["transition_matrix"], dtype=float)
    return sigs, P


def simulate(P, steps, start):
    n = P.shape[0]
    state = start
    counts = np.zeros(n, dtype=int)

    for _ in range(steps):
        counts[state] += 1
        probs = P[state]
        state = random.choices(range(n), weights=probs)[0]

    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--steps", type=int, default=200000)
    args = ap.parse_args()

    sigs, P = load_payload(Path(args.input))

    start = 0
    counts = simulate(P, args.steps, start)

    freqs = counts / counts.sum()

    print("="*80)
    print("SIGNATURE RANDOM WALK")
    print("="*80)
    print()

    for s, f in sorted(zip(sigs, freqs), key=lambda x: x[1], reverse=True):
        print(f"{s:18s} {f:.6f}")

    print()

if __name__ == "__main__":
    main()
