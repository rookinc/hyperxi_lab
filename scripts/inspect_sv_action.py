from __future__ import annotations

from collections import Counter

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


def cycle_decomposition_for_word(flag_model: FlagModel, gen: CoxeterGenerators, word: str):
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


def summarize_cycle_geometry(flag_model: FlagModel, cycle: tuple[int, ...]):
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

    for word in ["SV", "VS"]:
        print("=" * 80)
        print(f"INSPECTION FOR WORD = {word}")
        print("=" * 80)

        cycles = cycle_decomposition_for_word(fm, gen, word)
        counts = Counter(len(c) for c in cycles)

        print("cycle length counts:")
        for k in sorted(counts):
            print(f"  length={k}: count={counts[k]}")

        print()
        print(f"number of cycles: {len(cycles)}")

        if cycles:
            print()
            print("first few cycles with geometry:")
            for cyc in cycles[:6]:
                info = summarize_cycle_geometry(fm, cyc)
                print("-" * 80)
                print(f"cycle: {cyc}")
                print(f"length: {info['length']}")
                print(f"distinct faces: {info['distinct_faces']}")
                print(f"distinct edges: {info['distinct_edges']}")
                print(f"distinct vertices: {info['distinct_vertices']}")
                print(f"faces:    {info['faces']}")
                print(f"edges:    {info['edges']}")
                print(f"vertices: {info['vertices']}")


if __name__ == "__main__":
    main()
