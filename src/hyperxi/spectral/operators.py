from __future__ import annotations

import numpy as np

from ..geometry.flags import FlagModel
from ..transport.coxeter_generators import CoxeterGenerators


class LocalOperatorFactory:
    """
    Build exact local transport operators on the 120-flag space.
    """

    def __init__(
        self,
        flag_model: FlagModel | None = None,
        generators: CoxeterGenerators | None = None,
    ) -> None:
        self.flag_model = flag_model or FlagModel()
        self.generators = generators or CoxeterGenerators(self.flag_model)

    def _perm_matrix(self, move: str) -> np.ndarray:
        n = self.flag_model.num_flags()
        M = np.zeros((n, n), dtype=int)

        for j in range(n):
            state = self.flag_model.get(j)
            nxt = self.generators.apply(state, move)
            i = self.flag_model.index(nxt)
            M[i, j] = 1

        return M

    def build_U_F(self) -> np.ndarray:
        return self._perm_matrix("F")

    def build_U_S(self) -> np.ndarray:
        return self._perm_matrix("S")

    def build_U_V(self) -> np.ndarray:
        return self._perm_matrix("V")

    def build_H_loc(
        self,
        a_F: float = 1.0,
        a_S: float = 1.0,
        a_V: float = 1.0,
    ) -> np.ndarray:
        """
        Hermitian local transport Hamiltonian:

            H_loc = a_F (U_F + U_F^{-1})
                  + a_S U_S
                  + a_V (U_V + U_V^{-1})

        Since U_F and U_V are permutation matrices:
            U_F^{-1} = U_F.T
            U_V^{-1} = U_V.T
        """
        U_F = self.build_U_F().astype(float)
        U_S = self.build_U_S().astype(float)
        U_V = self.build_U_V().astype(float)

        H = a_F * (U_F + U_F.T) + a_S * U_S + a_V * (U_V + U_V.T)
        return H

    def validate_permutation_matrix(self, M: np.ndarray) -> bool:
        """
        Check if matrix is a permutation matrix.
        """
        if M.ndim != 2 or M.shape[0] != M.shape[1]:
            return False

        row_sums = M.sum(axis=1)
        col_sums = M.sum(axis=0)

        return bool(
            np.all((M == 0) | (M == 1))
            and np.all(row_sums == 1)
            and np.all(col_sums == 1)
        )


if __name__ == "__main__":
    ops = LocalOperatorFactory()

    U_F = ops.build_U_F()
    U_S = ops.build_U_S()
    U_V = ops.build_U_V()

    print("U_F permutation:", ops.validate_permutation_matrix(U_F))
    print("U_S permutation:", ops.validate_permutation_matrix(U_S))
    print("U_V permutation:", ops.validate_permutation_matrix(U_V))

    H = ops.build_H_loc()
    eigvals = np.linalg.eigvalsh(H)

    print("dim(H) =", H.shape)
    print("min eig =", eigvals[0])
    print("max eig =", eigvals[-1])
    print("trace(H) =", np.trace(H))
