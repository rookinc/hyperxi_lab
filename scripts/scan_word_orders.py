from __future__ import annotations

from itertools import product

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


def word_order(flag_model: FlagModel, gen: CoxeterGenerators, word: str, max_power: int = 60):
    for k in range(1, max_power + 1):
        ok = True
        for start in range(flag_model.num_flags()):
            state = flag_model.get(start)
            cur = state
            for _ in range(k):
                cur = gen.apply_word(cur, word)
            if cur != state:
                ok = False
                break
        if ok:
            return k
    return None


def main() -> None:
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    alphabet = ["S", "F", "V"]

    print("=" * 80)
    print("WORD ORDER SCAN")
    print("=" * 80)

    for length in [1, 2, 3, 4]:
        print()
        print(f"WORDS OF LENGTH {length}")
        print("-" * 80)

        for tup in product(alphabet, repeat=length):
            word = "".join(tup)
            order = word_order(fm, gen, word, max_power=60)
            print(f"{word:4s} -> order {order}")


if __name__ == "__main__":
    main()
