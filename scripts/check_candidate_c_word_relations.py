#!/usr/bin/env python3

from itertools import product

Face = int
Slot = int
Side = int
Flag = tuple[Face, Slot, Side]

MOD = 5

FACE_CYCLES = {
    0:  [3, 5, 7, 9, 11],
    1:  [2, 4, 6, 8, 10],
    2:  [1, 4, 3, 11, 10],
    4:  [1, 6, 5, 3, 2],
    6:  [1, 8, 7, 5, 4],
    8:  [1, 10, 9, 7, 6],
    10: [1, 2, 11, 9, 8],
    3:  [0, 11, 2, 4, 5],
    5:  [0, 3, 4, 6, 7],
    7:  [0, 5, 6, 8, 9],
    9:  [0, 7, 8, 10, 11],
    11: [0, 9, 10, 2, 3],
}

FACES = sorted(FACE_CYCLES.keys())

EDGE_BACKREF = {}
for f, cyc in FACE_CYCLES.items():
    for k, g in enumerate(cyc):
        j = FACE_CYCLES[g].index(f)
        EDGE_BACKREF[(f, k)] = (g, j)

FLAGS = [(f, k, s) for f in FACES for k in range(5) for s in (0, 1)]

def s0(flag: Flag) -> Flag:
    f, k, side = flag
    return (f, k, 1 - side)

def s1(flag: Flag) -> Flag:
    f, k, side = flag
    if side == 0:
        return (f, (k - 1) % MOD, 1)
    return (f, (k + 1) % MOD, 0)

def s2(flag: Flag) -> Flag:
    f, k, side = flag
    g, j = EDGE_BACKREF[(f, k)]
    return (g, j, 1 - side)

OPS = {"s0": s0, "s1": s1, "s2": s2}

def apply_word(flag: Flag, word):
    x = flag
    for w in word:
        x = OPS[w](x)
    return x

tests = [
    (["s0","s1","s2","s0"], ["s2","s1"], "s0(s1s2)s0 ?= s2s1"),
    (["s0","s2","s1","s0"], ["s1","s2"], "s0(s2s1)s0 ?= s1s2"),
    (["s0","s1","s0"], ["s1"], "s0 s1 s0 ?= s1"),
    (["s0","s2","s0"], ["s2"], "s0 s2 s0 ?= s2"),
]

print("=" * 80)
print("CHECK CANDIDATE-C WORD RELATIONS")
print("=" * 80)

for lhs, rhs, label in tests:
    bad = []
    for x in FLAGS:
        a = apply_word(x, lhs)
        b = apply_word(x, rhs)
        if a != b:
            bad.append((x, a, b))
    print(label)
    print("holds:" if not bad else f"fails on {len(bad)} flags")
    if bad:
        for row in bad[:5]:
            print(" ", row)
    print()
