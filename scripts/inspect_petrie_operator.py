from __future__ import annotations

from collections import Counter

import numpy as np

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators
from hyperxi.spectral.operators import LocalOperatorFactory


def cycle_decomposition_for_word(flag_model: FlagModel, gen: CoxeterGenerators, word: str):
    n = flag_model.num_flags()
    seen = [False] * n
    cycles = []

    for start in range(n):
        if seen[start]:
            continue

        cur = start
        cyc = []

        while not seen[cur]:
            seen[cur] = True
            cyc.append(cur)

            state = flag_model.get(cur)
            nxt = gen.apply_word(state, word)
            cur = flag_model.index(nxt)

        cycles.append(tuple(cyc))

    return cycles


def main() -> None:
    fm = FlagModel()
    gen = CoxeterGenerators(fm)
    ops = LocalOperatorFactory(fm, gen)

    U_S = ops.build_U_S()
    U_V = ops.build_U_V()
    U_P = U_S @ U_V   # Petrie operator for word P = SV

    print("=" * 80)
    print("PETRIE OPERATOR INSPECTION")
    print("=" * 80)
    print("Definition: U_P = U_S @ U_V  (word P = SV)")
    print()

    print("Matrix checks:")
    print("  shape:", U_P.shape)
    print("  entries in {0,1}:",
          bool(np.all((U_P == 0) | (U_P == 1))))
    print("  row sums all 1:",
          bool(np.all(U_P.sum(axis=1) == 1)))
    print("  col sums all 1:",
          bool(np.all(U_P.sum(axis=0) == 1)))
    print()

    # Compare matrix action against direct word action
    ok = True
    for j in range(fm.num_flags()):
        state = fm.get(j)
        nxt = gen.apply_word(state, "SV")
        i = fm.index(nxt)
        col = U_P[:, j]
        if col[i] != 1 or int(col.sum()) != 1:
            ok = False
            break
    print("Action matches direct word SV on all flags:", ok)
    print()

    # Cycle decomposition from direct word action
    cycles = cycle_decomposition_for_word(fm, gen, "SV")
    counts = Counter(len(c) for c in cycles)

    print("Cycle structure of P = SV:")
    for k in sorted(counts):
        print(f"  length={k}: count={counts[k]}")
    print(f"  total cycles: {len(cycles)}")
    print()

    # Spectral data for U_P
    eigvals = np.linalg.eigvals(U_P)
    angles = np.angle(eigvals)
    radii = np.abs(eigvals)

    print("Eigenvalue modulus summary:")
    print("  min |lambda|:", radii.min())
    print("  max |lambda|:", radii.max())
    print()

    # Round complex eigenvalues for readable multiplicities
    rounded = []
    for z in eigvals:
        rounded.append(complex(round(z.real, 10), round(z.imag, 10)))
    uniq = Counter(rounded)

    print("Approximate eigenvalue multiplicities for U_P:")
    for z, count in sorted(uniq.items(), key=lambda kv: (kv[0].real, kv[0].imag)):
        print(f"  {z.real:+.10f}{z.imag:+.10f}j  mult={count}")
    print()

    # Compare with 10th roots of unity numerically
    roots10 = [np.exp(2j * np.pi * k / 10) for k in range(10)]
    root_counts = Counter()

    for z in eigvals:
        k_best = min(range(10), key=lambda k: abs(z - roots10[k]))
        root_counts[k_best] += 1

    print("Nearest 10th-root bins:")
    for k in range(10):
        root = roots10[k]
        print(
            f"  k={k}: "
            f"root={root.real:+.10f}{root.imag:+.10f}j  "
            f"count={root_counts[k]}"
        )
    print()

    # Compare to H_loc
    H = ops.build_H_loc()
    H_eigs = np.linalg.eigvalsh(H)

    print("Hamiltonian summary for comparison:")
    print("  dim(H):", H.shape)
    print("  min eig:", H_eigs[0])
    print("  max eig:", H_eigs[-1])
    print("  trace(H):", np.trace(H))
    print()

    print("First few Petrie cycles:")
    for cyc in cycles[:6]:
        print(" ", cyc)


if __name__ == "__main__":
    main()
