from __future__ import annotations

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


def relation_holds(flag_model: FlagModel, gen: CoxeterGenerators, lhs: str, rhs: str) -> bool:
    for start in range(flag_model.num_flags()):
        state = flag_model.get(start)
        a = gen.apply_word(state, lhs)
        b = gen.apply_word(state, rhs)
        if a != b:
            return False
    return True


def main() -> None:
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    print("=" * 80)
    print("LOCAL FLAG ALGEBRA RELATION REPORT")
    print("=" * 80)

    words = ["S", "F", "V", "SF", "FS", "FV", "VF", "SV", "VS", "FSV", "SVF", "VFS"]
    for w in words:
        print(f"order({w}) = {word_order(fm, gen, w)}")

    print()
    print("Named relations:")
    checks = [
        ("SS", ""),
        ("FFFFF", ""),
        ("VVV", ""),
        ("SFSF", ""),
        ("FVFV", ""),
        ("SV" * 10, ""),
        ("VS" * 10, ""),
    ]

    for lhs, rhs in checks:
        ok = relation_holds(fm, gen, lhs, rhs)
        label = rhs if rhs else "id"
        print(f"{lhs} = {label}: {ok}")

    print()
    print("Conjugacy-style comparisons:")
    pairs = [
        ("SF", "FS"),
        ("FV", "VF"),
        ("SV", "VS"),
        ("FSV", "SVF"),
        ("SVF", "VFS"),
    ]
    for a, b in pairs:
        print(f"{a} = {b}: {relation_holds(fm, gen, a, b)}")


if __name__ == "__main__":
    main()
