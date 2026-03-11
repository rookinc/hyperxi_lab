from __future__ import annotations

import numpy as np

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators
from hyperxi.spectral.operators import LocalOperatorFactory


def main() -> None:
    fm = FlagModel()
    gen = CoxeterGenerators(fm)
    ops = LocalOperatorFactory(fm, gen)

    print("=" * 80)
    print("PETRIE OPERATOR INSPECTION")
    print("=" * 80)

    U_S = ops.build_U_S()
    U_V = ops.build_U_V()

    # Correct composition for word SV
    U_P = U_V @ U_S

    print("Definition: U_P = U_V @ U_S  (word P = SV)")
    print()

    print("Matrix checks:")
    print("  shape:", U_P.shape)
    print("  entries in {0,1}:", np.all((U_P == 0) | (U_P == 1)))
    print("  row sums all 1:", np.all(U_P.sum(axis=1) == 1))
    print("  col sums all 1:", np.all(U_P.sum(axis=0) == 1))
    print()

    # eigenvalues
    eigvals = np.linalg.eigvals(U_P)

    mags = np.abs(eigvals)

    print("Eigenvalue modulus summary:")
    print("  min |lambda|:", mags.min())
    print("  max |lambda|:", mags.max())
    print()

    roots = np.exp(2j * np.pi * np.arange(10) / 10)

    print("Nearest 10th-root bins:")
    for k, r in enumerate(roots):
        count = np.sum(np.isclose(eigvals, r, atol=1e-6))
        print(f"  k={k}: root={r.real:+.10f}{r.imag:+.10f}j  count={count}")


if __name__ == "__main__":
    main()
