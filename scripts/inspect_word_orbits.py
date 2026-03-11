from __future__ import annotations

from collections import Counter

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


def orbit_period(flag_model: FlagModel, gen: CoxeterGenerators, start: int, word: str, max_steps: int = 500):
    seen = [start]
    cur = start

    for _ in range(max_steps):
        state = flag_model.get(cur)
        nxt = gen.apply_word(state, word)
        cur = flag_model.index(nxt)
        seen.append(cur)
        if cur == start:
            return len(seen) - 1, tuple(seen[:-1])

    return None, tuple(seen)


def main() -> None:
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    words = [
        "FS",
        "SF",
        "FV",
        "VF",
        "SV",
        "VS",
        "FSV",
        "FVS",
        "SFV",
        "SVF",
        "VFS",
        "VSF",
    ]

    print("=" * 80)
    print("WORD ORBIT INSPECTION")
    print("=" * 80)

    for word in words:
        buckets = Counter()
        examples = {}

        for start in range(fm.num_flags()):
            period, orbit = orbit_period(fm, gen, start, word)
            if period is None:
                buckets["open"] += 1
            else:
                buckets[period] += 1
                examples.setdefault(period, orbit)

        print()
        print(f"WORD = {word}")
        print("-" * 80)
        for k in sorted(buckets, key=lambda x: (isinstance(x, str), x)):
            print(f"  period={k}: count={buckets[k]}")

        print("  examples:")
        shown = 0
        for k in sorted(examples):
            print(f"    period={k}: {examples[k]}")
            shown += 1
            if shown >= 5:
                break


if __name__ == "__main__":
    main()
