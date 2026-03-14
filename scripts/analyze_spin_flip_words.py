#!/usr/bin/env python3

"""
Analyze transport words that act as exact sign flips on low H_loc eigenspaces.

This script:
1. builds the exact local transport Hamiltonian H_loc on the 120-flag space
2. computes eigenspace blocks of H_loc
3. scans short words in {F,S,V}
4. finds words whose projected action on a block is exactly -I
5. reports:
   - shortest spin-flip words
   - full-space order of each word operator
   - which blocks each word flips
   - grouped equivalence by full operator matrix

This is the right next step after discovering exact -I actions in low sectors.
"""

from __future__ import annotations

import itertools
from collections import defaultdict

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


def dist_to_neg_identity(M: np.ndarray) -> float:
    I = np.eye(M.shape[0], dtype=float)
    return float(np.linalg.norm(M + I))


def dist_to_identity(M: np.ndarray) -> float:
    I = np.eye(M.shape[0], dtype=float)
    return float(np.linalg.norm(M - I))


def is_neg_identity(M: np.ndarray, tol: float = 1e-8) -> bool:
    I = np.eye(M.shape[0], dtype=float)
    return np.allclose(M, -I, atol=tol)


def matrix_key(W: np.ndarray) -> bytes:
    return np.round(W, 8).astype(np.int8).tobytes()


def operator_order(W: np.ndarray, max_order: int = 64, tol: float = 1e-8) -> int | None:
    I = np.eye(W.shape[0], dtype=float)
    P = np.eye(W.shape[0], dtype=float)

    for k in range(1, max_order + 1):
        P = W @ P
        if np.allclose(P, I, atol=tol):
            return k
    return None


def generate_words(max_len: int = 5) -> list[str]:
    alphabet = "FSV"
    out = []
    for L in range(1, max_len + 1):
        for tup in itertools.product(alphabet, repeat=L):
            out.append("".join(tup))

    preferred = [
        "F", "S", "V",
        "FF", "FS", "FV", "SF", "SS", "SV", "VF", "VS", "VV",
        "FFF", "FFS", "FFV", "FSF", "FSS", "FSV", "FVF", "FVS", "FVV",
        "SFF", "SFS", "SFV", "SSF", "SSV", "SVF", "SVS", "SVV",
        "VFF", "VFS", "VFV", "VSF", "VSS", "VSV", "VVF", "VVS",
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
    print("ANALYZE SPIN-FLIP WORDS")
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

    block_bases = []
    for block_id, (lam, idx) in enumerate(blocks, start=1):
        block_bases.append({
            "block": block_id,
            "lambda": lam,
            "mult": len(idx),
            "basis": np.array(vecs[:, idx], dtype=float),
        })

    exact_hits = []
    word_to_blocks: dict[str, list[dict]] = defaultdict(list)
    operator_groups: dict[bytes, list[str]] = defaultdict(list)
    operator_orders: dict[str, int | None] = {}

    for word in words:
        W = build_word_operator(word, UF, US, UV)
        operator_groups[matrix_key(W)].append(word)
        operator_orders[word] = operator_order(W, max_order=64)

        for info in block_bases[:16]:
            mult = info["mult"]
            if mult < 2 or mult > 6:
                continue

            M = projected_action(W, info["basis"])
            U = polar_unitary(M)

            if is_neg_identity(U):
                hit = {
                    "word": word,
                    "block": info["block"],
                    "lambda": info["lambda"],
                    "mult": mult,
                    "order": operator_orders[word],
                    "U": U,
                }
                exact_hits.append(hit)
                word_to_blocks[word].append(hit)

    print("=" * 80)
    print("EXACT -I HITS")
    print("=" * 80)

    if not exact_hits:
        print("No exact -I hits found.")
        print("=" * 80)
        return

    # shortest words first, then block id
    exact_hits.sort(key=lambda h: (len(h["word"]), h["word"], h["block"]))

    for hit in exact_hits:
        print(
            f"word={hit['word']:<5s} "
            f"len={len(hit['word'])} "
            f"block={hit['block']:2d} "
            f"lambda={hit['lambda']:.12f} "
            f"mult={hit['mult']} "
            f"full_order={hit['order']}"
        )

    print()
    print("=" * 80)
    print("WORDS GROUPED BY FLIPPED BLOCKS")
    print("=" * 80)

    grouped_by_signature: dict[tuple[int, ...], list[str]] = defaultdict(list)
    for word, hits in word_to_blocks.items():
        sig = tuple(sorted(h["block"] for h in hits))
        grouped_by_signature[sig].append(word)

    for sig in sorted(grouped_by_signature, key=lambda s: (len(s), s)):
        ws = sorted(grouped_by_signature[sig], key=lambda w: (len(w), w))
        print(f"blocks={sig}  words={ws}")

    print()
    print("=" * 80)
    print("SHORTEST EXACT SPIN-FLIP WORDS")
    print("=" * 80)

    min_len = min(len(h["word"]) for h in exact_hits)
    shortest = sorted({h["word"] for h in exact_hits if len(h["word"]) == min_len})
    for w in shortest:
        print(
            f"word={w:<5s} "
            f"len={len(w)} "
            f"full_order={operator_orders[w]} "
            f"blocks={[h['block'] for h in word_to_blocks[w]]}"
        )

    print()
    print("=" * 80)
    print("OPERATOR-EQUIVALENT WORD CLASSES")
    print("=" * 80)

    classes = [sorted(v, key=lambda w: (len(w), w)) for v in operator_groups.values() if len(v) > 1]
    classes.sort(key=lambda c: (len(c[0]), c[0]))

    for cls in classes[:50]:
        sample = cls[0]
        print(
            f"rep={sample:<5s} "
            f"order={operator_orders[sample]} "
            f"class_size={len(cls)} "
            f"words={cls}"
        )

    print()
    print("=" * 80)
    print("BEST SUMMARY")
    print("=" * 80)
    print("Exact sign-flip sectors exist in the transport algebra.")
    print("These are better spin candidates than chamber-cycle holonomy alone.")
    print("=" * 80)


if __name__ == "__main__":
    main()
