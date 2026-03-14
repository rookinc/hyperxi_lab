#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def load_payload(path):
    payload = json.loads(Path(path).read_text())
    sigs = payload["signatures"]
    P = np.array(payload["transition_matrix"], dtype=float)
    return sigs, P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    args = ap.parse_args()

    sigs, P = load_payload(args.input)

    # generator approximation
    H = P - np.eye(len(P))

    evals, evecs = np.linalg.eig(H)

    print("="*80)
    print("EFFECTIVE SIGNATURE HAMILTONIAN")
    print("="*80)
    print()

    for v in sorted(evals):
        print(f"{v.real:.6f}")

    print()

if __name__ == "__main__":
    main()
