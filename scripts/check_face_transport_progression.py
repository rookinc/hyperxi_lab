#!/usr/bin/env python3
from __future__ import annotations

from collections import defaultdict

from hyperxi.combinatorics.thalions import build_thalions
from hyperxi.combinatorics.transport_scaffold import F, V


def extract_face(flag):
    for name in ("face", "f", "face_id"):
        if hasattr(flag, name):
            return int(getattr(flag, name))
    raise AttributeError("Could not find face attribute on Flag.")


def main():
    thalions = build_thalions()

    print("=" * 80)
    print("FACE TRANSPORT PROGRESSION CHECK")
    print("=" * 80)

    # For each thalion, record the set of faces appearing in its members.
    thalion_faces = {}
    for th in thalions:
        thalion_faces[th.id] = sorted({extract_face(m) for m in th.members})

    print("THALION -> FACE SUPPORT (first 12)")
    print("-" * 80)
    for th_id in sorted(thalion_faces)[:12]:
        print(f"{th_id:2d}: {thalion_faces[th_id]}")
    print()

    # Examine how F and V act on face labels directly at the flag level.
    f_pairs = defaultdict(int)
    v_pairs = defaultdict(int)

    for th in thalions:
        for flag in th.members:
            f0 = extract_face(flag)
            fF = extract_face(F(flag))
            fV = extract_face(V(flag))
            f_pairs[(f0, fF)] += 1
            v_pairs[(f0, fV)] += 1

    print("FACE TRANSITIONS UNDER F")
    print("-" * 80)
    for (a, b), count in sorted(f_pairs.items()):
        print(f"{a:2d} -> {b:2d}   count={count}")
    print()

    print("FACE TRANSITIONS UNDER V")
    print("-" * 80)
    for (a, b), count in sorted(v_pairs.items()):
        print(f"{a:2d} -> {b:2d}   count={count}")
    print()

    # Dominant outgoing map if deterministic by face.
    f_out = defaultdict(set)
    v_out = defaultdict(set)
    for (a, b) in f_pairs:
        f_out[a].add(b)
    for (a, b) in v_pairs:
        v_out[a].add(b)

    print("OUTGOING FACE IMAGE SETS")
    print("-" * 80)
    for a in sorted(set(f_out) | set(v_out)):
        print(
            f"face {a:2d}: "
            f"F->{sorted(f_out.get(a, set()))}   "
            f"V->{sorted(v_out.get(a, set()))}"
        )
    print()

    # Compare against the observed spectral triples.
    triples = [
        [0, 4, 8],
        [1, 5, 9],
        [2, 6, 10],
        [3, 7, 11],
    ]

    print("CHECK TRIPLE STABILITY")
    print("-" * 80)
    for triple in triples:
        triple_set = set(triple)
        f_closed = True
        v_closed = True
        for face in triple:
            if not set(f_out.get(face, set())).issubset(triple_set):
                f_closed = False
            if not set(v_out.get(face, set())).issubset(triple_set):
                v_closed = False
        print(
            f"{triple}: "
            f"F-closed={f_closed}  "
            f"V-closed={v_closed}"
        )

    print()
    print("MOD-4 CLASS VIEW")
    print("-" * 80)
    for r in range(4):
        cls = [x for x in range(12) if x % 4 == r]
        print(f"class {r}: {cls}")

    print("=" * 80)


if __name__ == "__main__":
    main()
