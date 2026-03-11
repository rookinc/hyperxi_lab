from __future__ import annotations

import numpy as np

from hyperxi.spectral.operators import LocalOperatorFactory


def main() -> None:
    ops = LocalOperatorFactory()

    U_F = ops.build_U_F()
    U_S = ops.build_U_S()
    U_V = ops.build_U_V()
    H = ops.build_H_loc()

    print("=" * 80)
    print("LOCAL OPERATOR INSPECTION")
    print("=" * 80)

    print("Permutation checks:")
    print("  U_F:", ops.validate_permutation_matrix(U_F))
    print("  U_S:", ops.validate_permutation_matrix(U_S))
    print("  U_V:", ops.validate_permutation_matrix(U_V))
    print()

    print("Involution / transpose checks:")
    print("  U_S^2 == I:", np.array_equal(U_S @ U_S, np.eye(U_S.shape[0], dtype=int)))
    print("  U_F.T @ U_F == I:", np.array_equal(U_F.T @ U_F, np.eye(U_F.shape[0], dtype=int)))
    print("  U_V.T @ U_V == I:", np.array_equal(U_V.T @ U_V, np.eye(U_V.shape[0], dtype=int)))
    print()

    print("Hamiltonian checks:")
    print("  H symmetric:", np.allclose(H, H.T))
    print("  trace(H):", np.trace(H))
    print("  row-sum min/max:", H.sum(axis=1).min(), H.sum(axis=1).max())
    print()

    eigvals = np.linalg.eigvalsh(H)
    print("Spectral summary:")
    print("  min eig:", eigvals[0])
    print("  max eig:", eigvals[-1])
    print("  spectral radius:", np.max(np.abs(eigvals)))
    print()

    rounded, counts = np.unique(np.round(eigvals, 10), return_counts=True)
    print("Multiplicity profile:")
    for val, count in zip(rounded, counts):
        print(f"  {val: .10f}  mult={count}")


if __name__ == "__main__":
    main()
