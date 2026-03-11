from __future__ import annotations

from collections import Counter
import numpy as np


def load_operator_matrix():
    """
    Load the local transport operator from the HyperXi package.
    """
    from hyperxi.spectral.operators import LocalOperatorFactory

    ops = LocalOperatorFactory()
    M = ops.build_H_loc()
    return np.array(M, dtype=float)


def format_bool(x: bool) -> str:
    return "yes" if x else "no"


def is_symmetric(M: np.ndarray, tol: float = 1e-9) -> bool:
    return np.allclose(M, M.T, atol=tol, rtol=0.0)


def is_integer_valued(M: np.ndarray, tol: float = 1e-9) -> bool:
    return np.allclose(M, np.round(M), atol=tol, rtol=0.0)


def row_sum_profile(M: np.ndarray):
    row_sums = M.sum(axis=1)
    rounded = [round(float(x), 9) for x in row_sums]
    return Counter(rounded)


def nonzero_stats(M: np.ndarray, tol: float = 1e-12):
    nz = np.count_nonzero(np.abs(M) > tol)
    total = M.size
    density = nz / total if total else 0.0
    return nz, total, density


def support_graph_components(M: np.ndarray, tol: float = 1e-12):
    n = M.shape[0]
    adj = [[] for _ in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            if abs(M[i, j]) > tol or abs(M[j, i]) > tol:
                adj[i].append(j)
                adj[j].append(i)

    seen = [False] * n
    comps = 0

    for start in range(n):
        if seen[start]:
            continue
        comps += 1
        stack = [start]
        seen[start] = True
        while stack:
            v = stack.pop()
            for w in adj[v]:
                if not seen[w]:
                    seen[w] = True
                    stack.append(w)

    return comps


def eigen_summary(M: np.ndarray, places: int = 9):
    vals = np.linalg.eigvals(M)
    vals_real = []
    max_imag = 0.0

    for z in vals:
        max_imag = max(max_imag, abs(float(np.imag(z))))
        vals_real.append(float(np.real(z)))

    counts = Counter(round(v, places) for v in vals_real)
    grouped = sorted(counts.items(), key=lambda kv: kv[0], reverse=True)
    return vals, max_imag, grouped


def main():
    print("=" * 80)
    print("OPERATOR PROVENANCE REPORT")
    print("=" * 80)
    print()

    print("operator source: hyperxi.spectral.operators.LocalOperatorFactory")
    print("constructor: LocalOperatorFactory().build_H_loc(a_F=1, a_S=1, a_V=1)")
    print()

    M = load_operator_matrix()

    if M.ndim != 2:
        print("operator is not 2-dimensional")
        print(f"ndim = {M.ndim}")
        return

    n, m = M.shape
    print(f"dimension: {n} x {m}")
    print(f"square: {format_bool(n == m)}")
    print(f"symmetric: {format_bool(is_symmetric(M))}")
    print(f"integer-valued: {format_bool(is_integer_valued(M))}")
    print(f"trace: {float(np.trace(M)):.12f}")

    try:
        rank = int(np.linalg.matrix_rank(M))
        print(f"rank: {rank}")
    except Exception as e:
        print(f"rank: unavailable ({e})")

    nz, total, density = nonzero_stats(M)
    print(f"nonzero entries: {nz} / {total}")
    print(f"density: {density:.12f}")

    print()
    print("-" * 80)
    print("ROW SUM PROFILE")
    print("-" * 80)
    rs = row_sum_profile(M)
    for val, count in sorted(rs.items()):
        print(f"{val: .9f}    count = {count}")

    print()
    print("-" * 80)
    print("SUPPORT GRAPH")
    print("-" * 80)
    try:
        comps = support_graph_components(M)
        print(f"connected components in undirected support graph: {comps}")
    except Exception as e:
        print(f"support graph analysis unavailable: {e}")

    print()
    print("-" * 80)
    print("SPECTRAL SUMMARY")
    print("-" * 80)
    try:
        vals, max_imag, grouped = eigen_summary(M)
        print(f"eigenvalues counted: {len(vals)}")
        print(f"max imaginary leakage: {max_imag:.12e}")
        print(f"distinct rounded eigenvalues: {len(grouped)}")
        print()
        for eig, mult in grouped:
            print(f"{eig: .9f}    multiplicity = {mult}")
    except Exception as e:
        print(f"spectral analysis unavailable: {e}")

    print()
    print("Report complete.")


if __name__ == "__main__":
    main()
