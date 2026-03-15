#!/usr/bin/env python3
"""
Check the conjugation identity:

    S (F V) S  ==  V F

on all 120 flags of the dodecahedron flag model.

In the code:
    S = edge flip
    F = face rotation
    V = vertex rotation
"""

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators

def main():

    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    print("=" * 72)
    print("CHECK WORD CONJUGATION")
    print("=" * 72)

    failures = []

    for i in range(fm.num_flags()):
        x = fm.get(i)

        lhs = gen.S(gen.F(gen.V(gen.S(x))))   # S (F V) S
        rhs = gen.V(gen.F(x))                 # V F

        if lhs != rhs:
            failures.append((x, lhs, rhs))

    print("flags checked:", fm.num_flags())

    if not failures:
        print("identity holds on all flags:")
        print("    S (F V) S = V F")
    else:
        print("FAILED on", len(failures), "flags")
        for f in failures[:10]:
            print(f)

if __name__ == "__main__":
    main()
