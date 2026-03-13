#!/usr/bin/env python3
from __future__ import annotations

import sympy as sp

from hyperxi.combinatorics.thalions import build_thalions
from hyperxi.combinatorics.transport_scaffold import F, V


def build_flag_index():
    thalions = build_thalions()

    owner = {}
    flags = []
    seen = set()

    for th in thalions:
        for member in th.members:
            if member not in seen:
                seen.add(member)
                flags.append(member)
            owner[member] = th.id

    flags = sorted(flags, key=lambda x: repr(x))
    idx = {flag: i for i, flag in enumerate(flags)}
    return flags, idx, owner


def permutation_matrix(flags, idx, op):
    n = len(flags)
    M = sp.zeros(n, n)
    for f in flags:
        i = idx[f]
        g = op(f)
        j = idx[g]
        M[j, i] = 1
    return M


def factor_charpoly(name, M, x):
    print("=" * 80)
    print(name)
    print("=" * 80)
    print("size:", M.shape)
    print("computing characteristic polynomial...")
    poly = M.charpoly(x).as_expr()
    print("factoring...")
    fac = sp.factor(poly)
    print(fac)
    print()


def main():
    x = sp.symbols("x")

    flags, idx, owner = build_flag_index()

    print("=" * 80)
    print("THALION TRANSPORT ALGEBRA PROBE")
    print("=" * 80)
    print(f"flag count: {len(flags)}")
    print()

    MF = permutation_matrix(flags, idx, F)
    MV = permutation_matrix(flags, idx, V)

    factor_charpoly("F", MF, x)
    factor_charpoly("V", MV, x)
    factor_charpoly("F + V", MF + MV, x)
    factor_charpoly("FV", MF * MV, x)
    factor_charpoly("VF", MV * MF, x)

    target = x**3 + x**2 - 7*x - 2
    print("=" * 80)
    print("TARGET CUBIC")
    print("=" * 80)
    print(target)
    print("=" * 80)


if __name__ == "__main__":
    main()
