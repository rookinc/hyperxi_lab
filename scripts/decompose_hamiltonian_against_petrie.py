from __future__ import annotations

import numpy as np

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators
from hyperxi.spectral.operators import LocalOperatorFactory


def main() -> None:
    fm = FlagModel()
    gen = CoxeterGenerators(fm)
    ops = LocalOperatorFactory(fm, gen)

    # Build generators
    U_S = ops.build_U_S()
    U_V = ops.build_U_V()

    # Correct Petrie operator: SV
    U_P = U_V @ U_S

    # Local Hamiltonian
    H = ops.build_H_loc()

    print("=" * 80)
    print("PETRIE / HAMILTONIAN DECOMPOSITION")
    print("=" * 80)
    print()

    # Diagonalize Petrie operator
    eigvals_P, eigvecs_P = np.linalg.eig(U_P)

    # Sort by phase
    order = np.argsort(np.angle(eigvals_P))
    eigvals_P = eigvals_P[order]
    eigvecs_P = eigvecs_P[:, order]

    print("Petrie eigenvalues (sorted by phase):")
    for z in eigvals_P[:20]:
        print(f"{z.real:+.10f}{z.imag:+.10f}j")
    print()

    # Transform Hamiltonian into Petrie eigenbasis
    V = eigvecs_P
    V_inv = np.linalg.inv(V)

    H_petrie = V_inv @ H @ V

    print("Hamiltonian in Petrie basis:")
    print("matrix shape:", H_petrie.shape)
    print()

    # Measure off-diagonal energy
    offdiag = np.copy(H_petrie)
    np.fill_diagonal(offdiag, 0)

    print("Total off-diagonal magnitude:",
          float(np.sum(np.abs(offdiag))))
    print()

    # Diagonal entries
    diag = np.real(np.diag(H_petrie))

    print("First 20 diagonal entries:")
    for x in diag[:20]:
        print(x)

    print()

    # Eigenvalues of H for reference
    eig_H = np.linalg.eigvalsh(H)

    print("Hamiltonian eigenvalue summary:")
    print("min:", eig_H[0])
    print("max:", eig_H[-1])
    print("trace:", np.trace(H))


if __name__ == "__main__":
    main()
