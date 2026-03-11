from __future__ import annotations

from collections import Counter

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


def cycle_decomposition(flag_model: FlagModel, gen: CoxeterGenerators, move: str):
    n = flag_model.num_flags()
    seen = [False] * n
    cycles = []

    for start in range(n):
        if seen[start]:
            continue

        cur = start
        cyc = []

        while not seen[cur]:
            seen[cur] = True
            cyc.append(cur)

            state = flag_model.get(cur)
            nxt = gen.apply(state, move)
            cur = flag_model.index(nxt)

        cycles.append(tuple(cyc))

    return cycles


def main() -> None:
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    print("=" * 80)
    print("GENERATOR CYCLE INSPECTION")
    print("=" * 80)

    for move in ["S", "F", "V"]:
        cycles = cycle_decomposition(fm, gen, move)
        lengths = sorted(len(c) for c in cycles)
        counts = Counter(lengths)

        print()
        print(f"Move {move}")
        print("-" * 80)
        print(f"number of cycles: {len(cycles)}")
        print("cycle length counts:")
        for k in sorted(counts):
            print(f"  length={k}: count={counts[k]}")

        print("first few cycles:")
        for cyc in cycles[:10]:
            print(f"  len={len(cyc)}  {cyc}")


if __name__ == "__main__":
    main()
