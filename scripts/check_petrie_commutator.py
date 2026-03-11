from __future__ import annotations

import numpy as np

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators
from hyperxi.spectral.operators import LocalOperatorFactory


def main() -> None:
    fm = FlagModel()
    gen = CoxeterGenerators(fm)
    ops = LocalOperatorFactory(fm, gen)

    U_S = ops.build_U_S()
    U_V = ops.build_U_V()
    U_P = U_V @ U_S   # word SV

    H = ops.build_H_loc()

    C = H @ U_P - U_P @ H

    print("=" * 80)
    print("PETRIE / HAMILTONIAN COMMUTATOR")
    print("=" * 80)
    print("Checking [H, U_P] = H U_P - U_P H")
    print()

    print("Shape:", C.shape)
    print("Zero exactly:", np.array_equal(C, np.zeros_like(C)))
    print("Max abs entry:", float(np.max(np.abs(C))))
    print("Frobenius norm:", float(np.linalg.norm(C)))
    print("Trace:", np.trace(C))
    print()

    nz = np.argwhere(np.abs(C) > 1e-9)
    print("Nonzero entry count (>|1e-9|):", len(nz))

    print()
    print("First 20 nonzero entries:")
    for i, (r, c) in enumerate(nz[:20]):
        print(f"  ({r}, {c}) -> {C[r, c]}")


if __name__ == "__main__":
    main()
