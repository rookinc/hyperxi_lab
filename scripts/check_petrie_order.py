#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


def perm_matrix_from_word(word: str) -> np.ndarray:
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    n = fm.num_flags()

    # build flag list
    flags = [fm.get(i) for i in range(n)]

    # build lookup map
    index = {f: i for i, f in enumerate(flags)}

    P = np.zeros((n, n), dtype=int)

    for i, x in enumerate(flags):
        y = gen.apply_word(x, word)
        j = index[y]
        P[j, i] = 1

    return P


def main() -> None:
    word = "SV"
    U = perm_matrix_from_word(word)

    n = U.shape[0]
    I = np.eye(n, dtype=int)

    print("=" * 80)
    print("PETRIE OPERATOR ORDER CHECK")
    print("=" * 80)
    print(f"word: {word}")
    print(f"dimension: {n} x {n}")
    print()

    exact_order = None
    cur = I.copy()

    for k in range(1, 21):
        cur = U @ cur
        is_identity = np.array_equal(cur, I)
        print(f"k={k:2d}  identity={is_identity}")

        if is_identity and exact_order is None:
            exact_order = k

    print()
    print("INTERPRETATION")
    print("-" * 80)

    if exact_order is None:
        print("No identity return found up to k=20.")
    else:
        print(f"Smallest k with (SV)^k = I is k={exact_order}.")
        if exact_order == 10:
            print("So the Petrie operator has exact order 10.")
        else:
            print("So the Petrie operator order is not 10.")


if __name__ == "__main__":
    main()

