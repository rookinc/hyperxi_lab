#!/usr/bin/env python3
from __future__ import annotations

import json
import numpy as np
import sympy as sp

from hyperxi.combinatorics.thalions import build_thalions
from hyperxi.combinatorics.transport_scaffold import F, V


TARGET = 2.8210234486509136


def build_flag_index():
    thalions = build_thalions()

    flags = []
    seen = set()

    for th in thalions:
        for f in th.members:
            if f not in seen:
                seen.add(f)
                flags.append(f)

    flags = sorted(flags, key=lambda x: repr(x))
    idx = {f: i for i, f in enumerate(flags)}

    return flags, idx


def permutation_matrix(flags, idx, op):
    n = len(flags)
    M = np.zeros((n, n))

    for f in flags:
        i = idx[f]
        g = op(f)
        j = idx[g]
        M[j, i] = 1.0

    return M


def main():
    print("=" * 80)
    print("EXTRACT THALION CUBIC MODE")
    print("=" * 80)

    flags, idx = build_flag_index()

    print("flags:", len(flags))

    PF = permutation_matrix(flags, idx, F)
    PV = permutation_matrix(flags, idx, V)

    A = PF + PF.T + PV + PV.T

    print("computing eigen decomposition...")

    vals, vecs = np.linalg.eigh(A)

    # find closest eigenvalue
    i = np.argmin(np.abs(vals - TARGET))

    lam = vals[i]
    vec = vecs[:, i]

    print("target eigenvalue:", lam)

    # normalize
    vec = vec / np.max(np.abs(vec))

    data = []

    for f, v in zip(flags, vec):
        data.append({
            "flag": repr(f),
            "value": float(v)
        })

    out = {
        "eigenvalue": float(lam),
        "mode": data
    }

    path = "reports/spectral/nodal/thalion_cubic_mode.json"

    with open(path, "w") as fp:
        json.dump(out, fp, indent=2)

    print("saved:", path)


if __name__ == "__main__":
    main()
