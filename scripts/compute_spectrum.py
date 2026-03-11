from __future__ import annotations

import numpy as np

from hyperxi.spectral.operators import LocalOperatorFactory


def main() -> None:
    ops = LocalOperatorFactory()

    H = ops.build_H_loc()
    eigvals = np.linalg.eigvalsh(H)

    print("=" * 80)
    print("HYPERXI LOCAL TRANSPORT HAMILTONIAN SPECTRUM")
    print("=" * 80)
    print(f"matrix shape: {H.shape}")
    print(f"trace(H): {np.trace(H)}")
    print(f"min eigenvalue: {eigvals[0]}")
    print(f"max eigenvalue: {eigvals[-1]}")
    print()

    print("Eigenvalues:")
    for i, val in enumerate(eigvals):
        print(f"{i:3d}: {val:.12f}")

    unique_vals, counts = np.unique(np.round(eigvals, 10), return_counts=True)

    print()
    print("=" * 80)
    print("APPROXIMATE MULTIPLICITIES (rounded to 1e-10)")
    print("=" * 80)
    for val, count in zip(unique_vals, counts):
        print(f"{val: .10f}  multiplicity={count}")


if __name__ == "__main__":
    main()
