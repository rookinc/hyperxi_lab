#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators

WORDS = [
    "FFF",
    "SFFS",
    "FFFSS",
    "FFSSF",
    "FSSFF",
    "SSFFF",
    "VSVVS",
    "VFFSV",
    "FFFV",
    "FSVS",
    "SFFSV",
    "SVFF",
]


def word_permutation(fm: FlagModel, gen: CoxeterGenerators, word: str) -> list[int]:
    perm = []
    for i in range(fm.num_flags()):
        state = fm.get(i)
        nxt = gen.apply_word(state, word)
        perm.append(fm.index(nxt))
    return perm


def cycle_histogram(perm: list[int]) -> dict[int, int]:
    n = len(perm)
    seen = [False] * n
    hist = Counter()

    for i in range(n):
        if seen[i]:
            continue

        j = i
        length = 0
        while not seen[j]:
            seen[j] = True
            j = perm[j]
            length += 1

        hist[length] += 1

    return dict(sorted(hist.items()))


def analyze_s_pairs(perm: list[int]) -> tuple[int, int, int]:
    pairs = [(i, i + 1) for i in range(0, len(perm), 2)]

    preserved = 0
    swapped = 0
    split = 0

    for a, b in pairs:
        pa = perm[a]
        pb = perm[b]

        pair_a = pa // 2
        pair_b = pb // 2

        if pair_a == pair_b:
            if pa == b and pb == a:
                swapped += 1
            else:
                preserved += 1
        else:
            split += 1

    return preserved, swapped, split


def main():
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    families = defaultdict(list)

    print()
    print("=" * 80)
    print("MINUS-I TRANSPORT FAMILY CLASSIFICATION")
    print("=" * 80)

    for word in WORDS:
        perm = word_permutation(fm, gen, word)
        hist = cycle_histogram(perm)
        preserved, swapped, split = analyze_s_pairs(perm)

        signature = (
            tuple(sorted(hist.items())),
            preserved,
            swapped,
            split,
            tuple(perm[:20]),  # enough to distinguish same-cycle but different action
        )
        families[signature].append(word)

        print()
        print(f"WORD: {word}")
        print(f"cycle histogram: {hist}")
        print(f"pairs preserved: {preserved}")
        print(f"pairs swapped:   {swapped}")
        print(f"pairs split:     {split}")

    print()
    print("=" * 80)
    print("FAMILY GROUPING")
    print("=" * 80)

    for i, (sig, words) in enumerate(families.items(), start=1):
        hist_items, preserved, swapped, split, _prefix = sig
        print()
        print(f"Family {i}")
        print(f"cycle histogram: {dict(hist_items)}")
        print(f"pairs preserved: {preserved}")
        print(f"pairs swapped:   {swapped}")
        print(f"pairs split:     {split}")
        print(f"words: {words}")

    print()
    print("Done.")
    print()


if __name__ == "__main__":
    main()
