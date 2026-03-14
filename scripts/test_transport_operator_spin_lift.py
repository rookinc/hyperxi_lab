#!/usr/bin/env python3

"""
Search for spin-like behavior in low eigenspaces of the exact local transport Hamiltonian.

Strategy
--------
1. Build H_loc on the 120-flag space using LocalOperatorFactory
2. Compute low eigenspace blocks of H_loc
3. Build transport word operators from F, S, V
4. Project each word operator into each low eigenspace
5. Look for blocks where the projected action is close to:
   - -I   (spinorial sign flip)
   - order-4 behavior
   - nontrivial 2D / 3D internal rotation

This is a search script.
"""

from __future__ import annotations

import itertools
import numpy as np

from hyperxi.spectral.operators import LocalOperatorFactory


# ------------------------------------------------------------
# helpers
# ------------------------------------------------------------

def eigenspace_blocks(vals: np.ndarray, tol: float = 1e-8):
    blocks = []
    used = np.zeros(len(vals), dtype=bool)

    for i, v in enumerate(vals):
        if used[i]:
            continue
        idx = [j for j, w in enumerate(vals) if abs(w - v) <= tol]
        for j in idx:
            used[j] = True
        blocks.append((float(v), idx))

    return blocks


def build_word_operator(word: str, UF: np.ndarray, US: np.ndarray, UV: np.ndarray) -> np.ndarray:
    mats = {"F": UF, "S": US, "V": UV}
    W = np.eye(UF.shape[0], dtype=float)
    for ch in word:
        W = mats[ch] @ W
    return W


def projected_action(W: np.ndarray, basis: np.ndarray) -> np.ndarray:
    return basis.T @ W @ basis


def polar_unitary(M: np.ndarray) -> np.ndarray:
    U, _, Vt = np.linalg.svd(M)
    return U @ Vt


def dist_to_identity(M: np.ndarray) -> float:
    I = np.eye(M.shape[0], dtype=complex if np.iscomplexobj(M) else float)
    return float(np.linalg.norm(M - I))


def dist_to_neg_identity(M: np.ndarray) -> float:
    I = np.eye(M.shape[0], dtype=complex if np.iscomplexobj(M) else float)
    return float(np.linalg.norm(M + I))


def classify_unitary(U: np.ndarray) -> str:
    dI = dist_to_identity(U)
    dN = dist_to_neg_identity(U)
    d2I = dist_to_identity(U @ U)
    d4I = dist_to_identity(U @ U @ U @ U)

    if dN < 0.2:
        return "near_-I"
    if d2I < 0.2 and dI > 0.2:
        return "near_order_2"
    if d4I < 0.2 and d2I > 0.2:
        return "near_order_4"
    return "generic"


def generate_words(max_len: int = 5) -> list[str]:
    alphabet = "FSV"
    out = []
    for L in range(1, max_len + 1):
        for tup in itertools.product(alphabet, repeat=L):
            out.append("".join(tup))

    # helpful hand-picked words up front
    preferred = [
        "F", "S", "V",
        "FS", "SF", "FV", "VF", "SV", "VS",
        "FSV", "FVS", "SFV", "SVF", "VFS", "VSF",
        "FSFV", "FVSV", "FSVF", "SVFS", "VFSV",
        "FSFS", "FVFV", "SVSV",
    ]

    final = []
    seen = set()
    for w in preferred + out:
        if w not in seen:
            seen.add(w)
            final.append(w)
    return final


# ------------------------------------------------------------
# main
# ------------------------------------------------------------

def main():
    print("=" * 80)
    print("TRANSPORT OPERATOR SPIN-LIFT SEARCH")
    print("=" * 80)

    ops = LocalOperatorFactory()

    UF = ops.build_U_F().astype(float)
    US = ops.build_U_S().astype(float)
    UV = ops.build_U_V().astype(float)
    H = ops.build_H_loc().astype(float)

    vals, vecs = np.linalg.eigh(H)
    blocks = eigenspace_blocks(vals)

    print("dim(H):", H.shape)
    print("eigenspace blocks:", len(blocks))
    print()

    words = generate_words(max_len=5)
    print("word count:", len(words))
    print()

    results = []

    # ignore the uniform / trivial extremes; scan first ~12 blocks
    for block_id, (lam, idx) in enumerate(blocks[:12], start=1):
        mult = len(idx)
        basis = np.array(vecs[:, idx], dtype=float)

        if mult < 2 or mult > 4:
            continue

        print("-" * 80)
        print(f"block {block_id}")
        print("eigenvalue:", lam)
        print("multiplicity:", mult)

        best = None

        for word in words:
            W = build_word_operator(word, UF, US, UV)
            M = projected_action(W, basis)
            U = polar_unitary(M)

            dI = dist_to_identity(U)
            dN = dist_to_neg_identity(U)
            d2I = dist_to_identity(U @ U)
            d4I = dist_to_identity(U @ U @ U @ U)
            eig = np.linalg.eigvals(U)
            cls = classify_unitary(U)

            row = {
                "block": block_id,
                "lambda": lam,
                "mult": mult,
                "word": word,
                "class": cls,
                "dI": dI,
                "dN": dN,
                "d2I": d2I,
                "d4I": d4I,
                "eig": eig,
                "U": U,
            }
            results.append(row)

            score = (dN, d4I, d2I)
            if best is None or score < best[0]:
                best = (score, row)

        assert best is not None
        row = best[1]
        print("best word:", row["word"])
        print("class:", row["class"])
        print("||U - I||   =", round(row["dI"], 6))
        print("||U + I||   =", round(row["dN"], 6))
        print("||U^2 - I|| =", round(row["d2I"], 6))
        print("||U^4 - I|| =", round(row["d4I"], 6))
        print("eig(U):", np.round(row["eig"], 6))
        print("U:")
        print(np.round(row["U"], 6))
        print()

    print("=" * 80)
    print("GLOBAL RANKING BY CLOSENESS TO -I")
    print("=" * 80)
    ranked = sorted(results, key=lambda r: (r["dN"], r["d4I"], r["d2I"]))[:20]

    for r in ranked:
        print(
            f"block={r['block']:2d} "
            f"lambda={r['lambda']:.12f} "
            f"mult={r['mult']} "
            f"word={r['word']:<5s} "
            f"class={r['class']:<14s} "
            f"||U+I||={r['dN']:.6f} "
            f"||U^2-I||={r['d2I']:.6f} "
            f"||U^4-I||={r['d4I']:.6f}"
        )

    print("=" * 80)


if __name__ == "__main__":
    main()
