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
        if not line or not line.lower().startswith("decagon") or ":" not in line:
            continue
        _, rhs = line.split(":", 1)
        cyc = ast.literal_eval(rhs.strip())
        decs.append([int(x) for x in cyc])
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
        if word and all(c in valid for c in word):
            if word not in words:
                words.append(word)
        if len(words) >= limit:
            break

    if not words:
        raise SystemExit("Could not parse candidate words")

    return words


def cycle_hist(cycles):
    h = defaultdict(int)
    for cyc in cycles:
        h[len(cyc)] += 1
    return dict(sorted(h.items()))


def word_flag_permutation(fm, gen, word: str):
    perm = {}
    for i in range(fm.num_flags()):
        perm[i] = fm.index(gen.apply_word(fm.get(i), word))
    return perm


def permutation_cycles(perm: dict[int, int]):
    seen = set()
    out = []
    for start in sorted(perm):
        if start in seen:
            continue
        cur = start
        cyc = []
        while cur not in seen:
            seen.add(cur)
            cyc.append(cur)
            cur = perm[cur]
        out.append(cyc)
    return out


def build_flag_to_pair_and_pair_to_flags(fm, gen):
    permS = word_flag_permutation(fm, gen, "S")
    seen = set()
    flag_to_pair = {}
    pair_to_flags = []
    for i in range(fm.num_flags()):
        if i in seen:
            continue
        j = permS[i]
        orb = tuple(sorted([i, j]))
        pid = len(pair_to_flags)
        pair_to_flags.append(orb)
        for x in orb:
            seen.add(x)
            flag_to_pair[x] = pid
    if len(pair_to_flags) != 60:
        raise SystemExit(f"Expected 60 S-pairs, found {len(pair_to_flags)}")
    return flag_to_pair, pair_to_flags


def pair_to_decagons_map(decagons):
    out = defaultdict(list)
    for d, cyc in enumerate(decagons):
        for p in cyc:
            out[p].append(d)
    bad = {p: ds for p, ds in out.items() if len(ds) != 2}
    if bad:
        raise SystemExit(f"Expected every pair to lie on 2 decagons, got {bad}")
    return {p: sorted(ds) for p, ds in out.items()}


def main():
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    decagons = load_decagons(IN_DEC)
    pair_to_decs = pair_to_decagons_map(decagons)
    flag_to_pair, pair_to_flags = build_flag_to_pair_and_pair_to_flags(fm, gen)
    words = parse_top_words(IN_SPIN, limit=12)

    report = []
    payload = {"words": []}

    report.append("=" * 80)
    report.append("UPSTAIRS ANALYSIS OF -I CANDIDATE WORDS")
    report.append("=" * 80)
    report.append(f"candidate words: {words}")
    report.append("")

    for word in words:
        perm = word_flag_permutation(fm, gen, word)
        cycles = permutation_cycles(perm)

        # How does word act relative to S-pairs?
        split_pairs = []
        preserved_pairs = 0
        swapped_within_pair = 0

        for pid, orb in enumerate(pair_to_flags):
            a, b = orb
            ia, ib = perm[a], perm[b]
            img_pairs = {flag_to_pair[ia], flag_to_pair[ib]}

            if len(img_pairs) == 1:
                qid = next(iter(img_pairs))
                if qid == pid:
                    preserved_pairs += 1
                    if set((ia, ib)) == set((a, b)) and ia != a:
                        swapped_within_pair += 1
                else:
                    split_pairs.append((pid, qid, orb, pair_to_flags[qid], ia, ib))
            else:
                split_pairs.append((pid, tuple(sorted(img_pairs)), orb, None, ia, ib))

        # Flag transport across decagon memberships
        membership_moves = []
        same_dec_membership = 0
        changed_dec_membership = 0

        for pid, orb in enumerate(pair_to_flags):
            a, b = orb
            src_decs = pair_to_decs[pid]
            ia, ib = perm[a], perm[b]
            dst_info = sorted({tuple(pair_to_decs[flag_to_pair[ia]]), tuple(pair_to_decs[flag_to_pair[ib]])})
            src_tuple = tuple(src_decs)
            if len(dst_info) == 1 and dst_info[0] == src_tuple:
                same_dec_membership += 1
            else:
                changed_dec_membership += 1
            membership_moves.append(
                {
                    "pair": pid,
                    "src_decagons": src_decs,
                    "flag_images": [ia, ib],
                    "dst_pair_images": [flag_to_pair[ia], flag_to_pair[ib]],
                    "dst_decagon_sets": [list(x) for x in dst_info],
                }
            )

        report.append("-" * 80)
        report.append(f"WORD {word}")
        report.append("-" * 80)
        report.append(f"flag cycle histogram: {cycle_hist(cycles)}")
        report.append(f"pairs preserved setwise: {preserved_pairs} / 60")
        report.append(f"pairs swapped internally by word: {swapped_within_pair} / 60")
        report.append(f"pairs split across distinct S-pairs: {len(split_pairs)} / 60")
        report.append(f"same decagon-membership set: {same_dec_membership} / 60")
        report.append(f"changed decagon-membership set: {changed_dec_membership} / 60")
        report.append("first 12 membership moves:")
        for row in membership_moves[:12]:
            report.append(
                f"  pair {row['pair']:2d} decs={row['src_decagons']} "
                f"-> flags={row['flag_images']} "
                f"dst_pairs={row['dst_pair_images']} "
                f"dst_dec_sets={row['dst_decagon_sets']}"
            )
        if split_pairs:
            report.append("first 10 split-pair events:")
            for row in split_pairs[:10]:
                report.append(
                    f"  src_pair={row[0]} src_flags={row[2]} -> flag_images=({row[4]}, {row[5]}) target={row[1]}"
                )
        report.append("")

        payload["words"].append(
            {
                "word": word,
                "flag_cycle_histogram": cycle_hist(cycles),
                "pairs_preserved_setwise": preserved_pairs,
                "pairs_swapped_internally": swapped_within_pair,
                "pairs_split_across_distinct_Spairs": len(split_pairs),
                "same_decagon_membership_set": same_dec_membership,
                "changed_decagon_membership_set": changed_dec_membership,
                "first_12_membership_moves": membership_moves[:12],
                "first_10_split_pair_events": [
                    {
                        "src_pair": row[0],
                        "target": row[1],
                        "src_flags": list(row[2]),
                        "flag_images": [row[4], row[5]],
                    }
                    for row in split_pairs[:10]
                ],
            }
        )

    out_txt = OUT_DIR / "minusI_upstairs_action.txt"
    out_json = OUT_DIR / "minusI_upstairs_action.json"
    out_txt.write_text("\n".join(report) + "\n", encoding="utf-8")
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("\n".join(report))
    print(f"saved {out_txt.relative_to(ROOT)}")
    print(f"saved {out_json.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
