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


def word_perm(fm: FlagModel, gen: CoxeterGenerators, word: str) -> tuple[int, ...]:
    out = []
    for i in range(fm.num_flags()):
        state = fm.get(i)
        nxt = gen.apply_word(state, word)
        out.append(fm.index(nxt))
    return tuple(out)


def compose(p: tuple[int, ...], q: tuple[int, ...]) -> tuple[int, ...]:
    # first q then p
    return tuple(p[q[i]] for i in range(len(p)))


def inverse(p: tuple[int, ...]) -> tuple[int, ...]:
    inv = [0] * len(p)
    for i, j in enumerate(p):
        inv[j] = i
    return tuple(inv)


def cycle_histogram(perm: tuple[int, ...]) -> dict[int, int]:
    n = len(perm)
    seen = [False] * n
    hist = Counter()
    for i in range(n):
        if seen[i]:
            continue
        j = i
        L = 0
        while not seen[j]:
            seen[j] = True
            j = perm[j]
            L += 1
        hist[L] += 1
    return dict(sorted(hist.items()))


def order_of_perm(p: tuple[int, ...], max_order: int = 60) -> int | None:
    cur = p
    ident = tuple(range(len(p)))
    for k in range(1, max_order + 1):
        if cur == ident:
            return k
        cur = compose(p, cur)
    return None


def main():
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    perms = {w: word_perm(fm, gen, w) for w in WORDS}

    families = defaultdict(list)
    for w, p in perms.items():
        sig = (tuple(sorted(cycle_histogram(p).items())), p[:20])
        families[sig].append(w)

    reps = []
    print("=" * 80)
    print("MINUS-I FAMILY ALGEBRA")
    print("=" * 80)
    print()

    for i, (sig, words) in enumerate(families.items(), start=1):
        rep = min(words, key=lambda s: (len(s), s))
        reps.append(rep)
        p = perms[rep]
        print(f"Family {i}")
        print(f"  representative: {rep}")
        print(f"  members: {words}")
        print(f"  cycle histogram: {cycle_histogram(p)}")
        print(f"  permutation order: {order_of_perm(p)}")
        print()

    print("=" * 80)
    print("REPRESENTATIVE COMPOSITION TABLE")
    print("=" * 80)
    print()

    rep_perms = {r: perms[r] for r in reps}
    rep_set = set(reps)

    for a in reps:
        for b in reps:
            c = compose(rep_perms[a], rep_perms[b])
            match = None
            for name, p in rep_perms.items():
                if c == p:
                    match = name
                    break
            print(f"{a:5s} * {b:5s} -> {match if match else 'new'}")
        print()

    print("=" * 80)
    print("INVERSE MATCHES")
    print("=" * 80)
    print()

    for a in reps:
        ia = inverse(rep_perms[a])
        match = None
        for name, p in rep_perms.items():
            if ia == p:
                match = name
                break
        print(f"{a:5s}^-1 -> {match if match else 'new'}")


if __name__ == "__main__":
    main()
