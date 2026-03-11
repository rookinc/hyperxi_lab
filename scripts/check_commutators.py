from __future__ import annotations

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


def equal_as_actions(flag_model: FlagModel, gen: CoxeterGenerators, a: str, b: str) -> bool:
    for start in range(flag_model.num_flags()):
        state = flag_model.get(start)
        if gen.apply_word(state, a) != gen.apply_word(state, b):
            return False
    return True


def main() -> None:
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    print("=" * 80)
    print("LOCAL COMMUTATOR CHECKS")
    print("=" * 80)

    pairs = [("S", "F"), ("S", "V"), ("F", "V")]

    for a, b in pairs:
        ab = a + b
        ba = b + a
        comm = a + b + a + b
        print()
        print(f"{a} vs {b}")
        print("-" * 80)
        print(f"{ab} = {ba}: {equal_as_actions(fm, gen, ab, ba)}")
        print(f"{comm} = id: {equal_as_actions(fm, gen, comm, '')}")


if __name__ == "__main__":
    main()
