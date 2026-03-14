#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from collections import Counter, deque

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators

SEEDS = ["FFF", "FFFV", "VFFSV", "SVFF"]


def word_perm(fm: FlagModel, gen: CoxeterGenerators, word: str) -> tuple[int, ...]:
    out = []
    for i in range(fm.num_flags()):
        state = fm.get(i)
        nxt = gen.apply_word(state, word)
        out.append(fm.index(nxt))
    return tuple(out)


def compose(p: tuple[int, ...], q: tuple[int, ...]) -> tuple[int, ...]:
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


def order_of_perm(p: tuple[int, ...], max_order: int = 120) -> int | None:
    ident = tuple(range(len(p)))
    cur = p
    for k in range(1, max_order + 1):
        if cur == ident:
            return k
        cur = compose(p, cur)
    return None


def shortlex_word(a: str, b: str) -> str:
    if not a:
        return b
    if not b:
        return a
    return a if (len(a), a) <= (len(b), b) else b


def main():
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    ident = tuple(range(fm.num_flags()))
    seed_perms = {w: word_perm(fm, gen, w) for w in SEEDS}

    generators = {}
    for w, p in seed_perms.items():
        generators[w] = p
        generators[w + "^-1"] = inverse(p)

    seen: dict[tuple[int, ...], str] = {ident: "I"}
    q = deque([ident])

    while q:
        cur = q.popleft()
        cur_word = seen[cur]

        for gname, gperm in generators.items():
            nxt = compose(gperm, cur)
            cand = gname if cur_word == "I" else f"{gname}·{cur_word}"

            if nxt not in seen:
                seen[nxt] = cand
                q.append(nxt)
            else:
                seen[nxt] = shortlex_word(seen[nxt], cand)

    elems = list(seen.items())

    print("=" * 80)
    print("MINUS-I TRANSPORT SUBGROUP GROWTH")
    print("=" * 80)
    print(f"seed words: {SEEDS}")
    print(f"subgroup size: {len(elems)}")
    print()

    order_hist = Counter()
    cycle_hist_hist = Counter()

    annotated = []
    for perm, word in elems:
        o = order_of_perm(perm)
        ch = tuple(sorted(cycle_histogram(perm).items()))
        order_hist[o] += 1
        cycle_hist_hist[ch] += 1
        annotated.append((word, perm, o, ch))

    print("ORDER HISTOGRAM")
    print("-" * 80)
    for k in sorted(order_hist, key=lambda x: (x is None, x)):
        print(f"order {k}: {order_hist[k]}")
    print()

    print("CYCLE HISTOGRAM CLASSES")
    print("-" * 80)
    for ch, count in cycle_hist_hist.most_common():
        print(f"{dict(ch)} : {count}")
    print()

    print("FIRST 25 ELEMENTS")
    print("-" * 80)
    annotated.sort(key=lambda t: (len(t[0]), t[0]))
    for word, _perm, o, ch in annotated[:25]:
        print(f"{word}")
        print(f"  order={o}")
        print(f"  cycles={dict(ch)}")
    print()

    out = ROOT / "reports" / "spectral" / "transport_modes" / "minusI_transport_subgroup.txt"
    lines = []
    lines.append("=" * 80)
    lines.append("MINUS-I TRANSPORT SUBGROUP GROWTH")
    lines.append("=" * 80)
    lines.append(f"seed words: {SEEDS}")
    lines.append(f"subgroup size: {len(elems)}")
    lines.append("")
    lines.append("ORDER HISTOGRAM")
    lines.append("-" * 80)
    for k in sorted(order_hist, key=lambda x: (x is None, x)):
        lines.append(f"order {k}: {order_hist[k]}")
    lines.append("")
    lines.append("CYCLE HISTOGRAM CLASSES")
    lines.append("-" * 80)
    for ch, count in cycle_hist_hist.most_common():
        lines.append(f"{dict(ch)} : {count}")
    lines.append("")
    lines.append("FIRST 50 ELEMENTS")
    lines.append("-" * 80)
    for word, _perm, o, ch in annotated[:50]:
        lines.append(f"{word}")
        lines.append(f"  order={o}")
        lines.append(f"  cycles={dict(ch)}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"saved {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
