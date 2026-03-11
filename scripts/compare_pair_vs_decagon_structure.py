from __future__ import annotations

from collections import Counter

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


def cycle_decomposition(flag_model: FlagModel, gen: CoxeterGenerators, word: str):
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
            nxt = gen.apply_word(state, word)
            cur = flag_model.index(nxt)

        cycles.append(tuple(cyc))

    return cycles


def summarize_cycle(flag_model: FlagModel, cycle: tuple[int, ...]):
    faces = [flag_model.get(i).face for i in cycle]
    edges = [flag_model.get(i).edge for i in cycle]
    vertices = [flag_model.get(i).vertex for i in cycle]

    return {
        "length": len(cycle),
        "distinct_faces": len(set(faces)),
        "distinct_edges": len(set(edges)),
        "distinct_vertices": len(set(vertices)),
        "faces": faces,
        "edges": edges,
        "vertices": vertices,
    }


def main() -> None:
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    tests = {
        "S": "edge-flip pair structure",
        "SV": "Petrie decagon structure",
    }

    print("=" * 80)
    print("PAIR vs DECAGON STRUCTURE")
    print("=" * 80)

    for word, label in tests.items():
        cycles = cycle_decomposition(fm, gen, word)
        counts = Counter(len(c) for c in cycles)

        print()
        print(f"WORD = {word}")
        print(f"INTERPRETATION = {label}")
        print("-" * 80)
        print("cycle length counts:")
        for k in sorted(counts):
            print(f"  length={k}: count={counts[k]}")
        print(f"total cycles: {len(cycles)}")

        if cycles:
            print()
            print("first few cycle summaries:")
            for cyc in cycles[:6]:
                info = summarize_cycle(fm, cyc)
                print(
                    f"  cycle={cyc} | "
                    f"len={info['length']} | "
                    f"faces={info['distinct_faces']} | "
                    f"edges={info['distinct_edges']} | "
                    f"verts={info['distinct_vertices']}"
                )

    print()
    print("=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print("S  gives 60 local pairs (pure edge distinction).")
    print("SV gives 12 decagons (global skew circulation / Petrie structure).")
    print()
    print("If the important organization is pairing, the geometry is emphasizing")
    print("local binary distinction.")
    print("If the important organization is decagons, the geometry is emphasizing")
    print("global circulation.")
    print()
    print("HyperXi currently shows that both exist exactly, but only the decagon")
    print("structure traverses the whole dodecahedral chamber space in long skew loops.")


if __name__ == "__main__":
    main()
