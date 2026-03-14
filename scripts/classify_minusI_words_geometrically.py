#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from collections import defaultdict
from pathlib import Path

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators

ROOT = Path(__file__).resolve().parents[1]
IN_SPIN = ROOT / "reports" / "spectral" / "transport_operator_spin_lift.txt"
IN_DEC = ROOT / "reports" / "decagons" / "ordered_decagon_pair_cycles.txt"
OUT_DIR = ROOT / "reports" / "spectral" / "transport_modes"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_decagons(path: Path):
    decs = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if not line.lower().startswith("decagon"):
            continue
        if ":" not in line:
            continue
        _, rhs = line.split(":", 1)
        cyc = ast.literal_eval(rhs.strip())
        cyc = [int(x) for x in cyc]
        if len(cyc) != 10:
            raise SystemExit(f"Expected decagon length 10, got {len(cyc)}")
        decs.append(cyc)
    if len(decs) != 12:
        raise SystemExit(f"Expected 12 decagons, found {len(decs)}")
    return decs


def parse_top_words(path: Path, limit: int = 12):
    valid = set("SFV")
    words = []

    for raw in path.read_text(encoding="utf-8").splitlines():
        if "word=" not in raw:
            continue

        try:
            part = raw.split("word=", 1)[1]
            word = part.split()[0].strip()
        except Exception:
            continue

        if not word:
            continue

        if all(c in valid for c in word):
            if word not in words:
                words.append(word)

        if len(words) >= limit:
            break

    if not words:
        raise SystemExit("Could not parse candidate words")

    return words


def cycle_decomposition(fm, gen, word):
    n = fm.num_flags()
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

            state = fm.get(cur)
            nxt = gen.apply_word(state, word)
            cur = fm.index(nxt)

        cycles.append(tuple(cyc))

    return cycles


def s_pair_partition(fm, gen):
    cycles = cycle_decomposition(fm, gen, "S")
    flag_to_pair = {}

    for pid, cyc in enumerate(cycles):
        for x in cyc:
            flag_to_pair[x] = pid

    return flag_to_pair


def pair_to_decagons_map(decagons):
    pair_to_decs = defaultdict(list)

    for d, cyc in enumerate(decagons):
        for p in cyc:
            pair_to_decs[p].append(d)

    return pair_to_decs


def induced_pair_permutation(fm, gen, word, flag_to_pair):
    pair_map = defaultdict(set)

    for flag, pid in flag_to_pair.items():
        nxt = fm.index(gen.apply_word(fm.get(flag), word))
        pair_map[pid].add(flag_to_pair[nxt])

    out = {}
    for pid, images in pair_map.items():
        if len(images) != 1:
            raise SystemExit(
                f"Word {word} does not induce a well-defined map on pairs for pair {pid}: {images}"
            )
        out[pid] = next(iter(images))

    return out


def permutation_cycles(perm):
    seen = set()
    cycles = []

    for start in sorted(perm):
        if start in seen:
            continue

        cur = start
        cyc = []

        while cur not in seen:
            seen.add(cur)
            cyc.append(cur)
            cur = perm[cur]

        cycles.append(cyc)

    return cycles


def cycle_hist(cycles):
    h = defaultdict(int)
    for c in cycles:
        h[len(c)] += 1
    return dict(sorted(h.items()))


def main():
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    decagons = load_decagons(IN_DEC)
    pair_to_decs = pair_to_decagons_map(decagons)
    flag_to_pair = s_pair_partition(fm, gen)
    words = parse_top_words(IN_SPIN, limit=12)

    report = []
    payload = {"words": []}

    report.append("=" * 80)
    report.append("GEOMETRIC CLASSIFICATION OF -I WORDS")
    report.append("=" * 80)
    report.append(f"candidate words: {words}")
    report.append("")

    for word in words:
        flag_cycles = cycle_decomposition(fm, gen, word)
        pair_perm = induced_pair_permutation(fm, gen, word, flag_to_pair)
        pair_cycles = permutation_cycles(pair_perm)

        fixed_pairs = sum(1 for p, q in pair_perm.items() if p == q)

        report.append("-" * 80)
        report.append(f"WORD {word}")
        report.append("-" * 80)
        report.append(f"flag cycle histogram: {cycle_hist(flag_cycles)}")
        report.append(f"pair cycle histogram: {cycle_hist(pair_cycles)}")
        report.append(f"pairs fixed: {fixed_pairs} / 60")
        report.append("first 12 pair images:")
        for p in range(12):
            q = pair_perm[p]
            report.append(
                f"  pair {p:2d} -> {q:2d}   decagons {pair_to_decs[p]} -> {pair_to_decs[q]}"
            )
        report.append("")

        payload["words"].append(
            {
                "word": word,
                "flag_cycle_histogram": cycle_hist(flag_cycles),
                "pair_cycle_histogram": cycle_hist(pair_cycles),
                "pairs_fixed": fixed_pairs,
                "first_12_pair_images": [
                    {
                        "pair": p,
                        "image": pair_perm[p],
                        "src_decagons": pair_to_decs[p],
                        "dst_decagons": pair_to_decs[pair_perm[p]],
                    }
                    for p in range(12)
                ],
            }
        )

    out_txt = OUT_DIR / "minusI_word_geometric_classification.txt"
    out_json = OUT_DIR / "minusI_word_geometric_classification.json"

    out_txt.write_text("\n".join(report) + "\n", encoding="utf-8")
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("\n".join(report))
    print(f"saved {out_txt.relative_to(ROOT)}")
    print(f"saved {out_json.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
