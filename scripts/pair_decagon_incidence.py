from __future__ import annotations

from collections import defaultdict

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


def main() -> None:
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    s_pairs = cycle_decomposition(fm, gen, "S")
    sv_decagons = cycle_decomposition(fm, gen, "SV")

    print("=" * 80)
    print("PAIR / DECAGON INCIDENCE")
    print("=" * 80)
    print(f"S-pairs:    {len(s_pairs)}")
    print(f"SV-decagons:{len(sv_decagons)}")
    print()

    # map flag -> pair id
    flag_to_pair = {}
    for pid, pair in enumerate(s_pairs):
        for x in pair:
            flag_to_pair[x] = pid

    # map flag -> decagon id
    flag_to_decagon = {}
    for did, dec in enumerate(sv_decagons):
        for x in dec:
            flag_to_decagon[x] = did

    # incidence: each decagon contains which pairs?
    decagon_to_pairs = defaultdict(list)
    pair_to_decagons = defaultdict(set)

    for x in range(fm.num_flags()):
        pid = flag_to_pair[x]
        did = flag_to_decagon[x]
        decagon_to_pairs[did].append(pid)
        pair_to_decagons[pid].add(did)

    print("Decagon -> pair incidence")
    print("-" * 80)
    for did in range(len(sv_decagons)):
        pairs = decagon_to_pairs[did]
        unique_pairs = sorted(set(pairs))
        print(f"decagon {did:2d}:")
        print(f"  raw pair labels:   {pairs}")
        print(f"  unique pair ids:   {unique_pairs}")
        print(f"  number of pairs:   {len(unique_pairs)}")
        print()

    print("=" * 80)
    print("PAIR PARTICIPATION COUNTS")
    print("=" * 80)

    counts = defaultdict(int)
    for pid, decs in pair_to_decagons.items():
        counts[len(decs)] += 1

    for k in sorted(counts):
        print(f"pairs belonging to {k} decagons: {counts[k]}")

    print()
    print("First 20 pair -> decagon incidences")
    print("-" * 80)
    for pid in range(min(20, len(s_pairs))):
        print(f"pair {pid:2d} -> decagons {sorted(pair_to_decagons[pid])}")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("If each pair belongs to exactly one decagon, the circulation partition")
    print("simply refines the binary distinction layer.")
    print("If pairs belong to multiple decagons, then local distinctions are reused")
    print("across multiple circulation channels.")
    print("That would mean the global transport structure braids the local splits.")
    print()


if __name__ == "__main__":
    main()
