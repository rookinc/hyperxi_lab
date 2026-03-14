#!/usr/bin/env python3

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

PAIR_DECAGON = REPORTS / "pairs" / "pair_decagon_incidence.txt"
DECAGON_GRAPH = REPORTS / "decagons" / "decagon_intersection_graph.txt"
CORE_REPORT = REPORTS / "quotients" / "check_15core_vs_linegraph_petersen.txt"
OUT_TXT = REPORTS / "spectral" / "signature_transitions" / "candidate_27_extension.txt"
OUT_JSON = REPORTS / "spectral" / "signature_transitions" / "candidate_27_extension.json"


def parse_pair_decagon_incidence(path: Path):
    if not path.exists():
        raise SystemExit(f"Missing required file: {path}")

    text = path.read_text(encoding="utf-8")
    pair_to_decagons: dict[int, set[int]] = defaultdict(set)

    # tolerant patterns:
    # "pair 7: [0, 3, 9]"
    # "pair 7 -> decagons 0 3 9"
    for line in text.splitlines():
        m = re.search(r"pair\s+(\d+).*?\[([0-9,\s]+)\]", line, re.I)
        if m:
            p = int(m.group(1))
            vals = [int(x) for x in re.findall(r"\d+", m.group(2))]
            pair_to_decagons[p].update(vals)
            continue

        m = re.search(r"pair\s+(\d+).*?decagons?\s*[:=]?\s*(.*)$", line, re.I)
        if m:
            p = int(m.group(1))
            vals = [int(x) for x in re.findall(r"\d+", m.group(2))]
            if vals:
                pair_to_decagons[p].update(vals)

    if not pair_to_decagons:
        raise SystemExit("Could not parse any pair→decagon incidences")

    return {k: sorted(v) for k, v in sorted(pair_to_decagons.items())}


def parse_decagon_graph(path: Path):
    if not path.exists():
        raise SystemExit(f"Missing required file: {path}")

    text = path.read_text(encoding="utf-8")
    adj: dict[int, set[int]] = defaultdict(set)

    # tolerant patterns:
    # "0: 1 4 7"
    # "(0,1)"
    # "0 -- 1"
    for line in text.splitlines():
        m = re.match(r"\s*(\d+)\s*:\s*(.*)$", line)
        if m:
            a = int(m.group(1))
            bs = [int(x) for x in re.findall(r"\d+", m.group(2))]
            for b in bs:
                if a != b:
                    adj[a].add(b)
                    adj[b].add(a)
            continue

        m = re.search(r"\(?\s*(\d+)\s*[, -]+\s*(\d+)\s*\)?", line)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a != b:
                adj[a].add(b)
                adj[b].add(a)

    return {k: sorted(v) for k, v in sorted(adj.items())}


def parse_core_size(path: Path):
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    m = re.search(r"RECOVERED 15-CORE.*?vertices:\s*(\d+)", text, re.S)
    if m:
        return int(m.group(1))
    return None


def build_combined_structure(pair_to_decagons: dict[int, list[int]], decagon_adj: dict[int, list[int]]):
    pair_nodes = sorted(pair_to_decagons.keys())
    decagon_nodes = sorted(decagon_adj.keys())

    if len(decagon_nodes) == 0:
        # infer from incidences if adjacency file didn't parse
        seen = set()
        for ds in pair_to_decagons.values():
            seen.update(ds)
        decagon_nodes = sorted(seen)

    pair_pair_overlap = {}
    for i, a in enumerate(pair_nodes):
        sa = set(pair_to_decagons[a])
        for b in pair_nodes[i + 1 :]:
            sb = set(pair_to_decagons[b])
            inter = sorted(sa & sb)
            if inter:
                pair_pair_overlap[(a, b)] = inter

    pair_decagon_edges = []
    for p in pair_nodes:
        for d in pair_to_decagons[p]:
            pair_decagon_edges.append((p, d))

    decagon_edges = []
    for a in decagon_nodes:
        for b in decagon_adj.get(a, []):
            if a < b:
                decagon_edges.append((a, b))

    return {
        "pair_nodes": pair_nodes,
        "decagon_nodes": decagon_nodes,
        "pair_pair_overlap": {f"{a}-{b}": v for (a, b), v in pair_pair_overlap.items()},
        "pair_decagon_edges": pair_decagon_edges,
        "decagon_edges": decagon_edges,
    }


def summarize(payload: dict, core_size: int | None):
    pair_nodes = payload["pair_nodes"]
    decagon_nodes = payload["decagon_nodes"]
    pair_decagon_edges = payload["pair_decagon_edges"]
    pair_pair_overlap = payload["pair_pair_overlap"]
    decagon_edges = payload["decagon_edges"]

    lines = []
    lines.append("=" * 80)
    lines.append("CANDIDATE 27-EXTENSION FROM PETERSEN CORE")
    lines.append("=" * 80)
    lines.append(f"pair-like core node count   : {len(pair_nodes)}")
    lines.append(f"decagon/face-like node count: {len(decagon_nodes)}")
    lines.append(f"total candidate object count: {len(pair_nodes) + len(decagon_nodes)}")
    if core_size is not None:
        lines.append(f"reported recovered core size: {core_size}")
    lines.append("")

    lines.append("INTERPRETATION")
    lines.append("-" * 80)
    if len(pair_nodes) == 15 and len(decagon_nodes) == 12:
        lines.append("The object count matches a natural 15 + 12 = 27 split.")
    else:
        lines.append("The object count does not exactly match 15 + 12 = 27.")
    lines.append("")

    lines.append("PAIR → DECAGON INCIDENCE DEGREES")
    lines.append("-" * 80)
    degs = defaultdict(int)
    for p, _d in pair_decagon_edges:
        degs[p] += 1
    for p in pair_nodes:
        lines.append(f"pair {p:2d}  degree_to_decagons = {degs[p]}")
    lines.append("")

    lines.append("DECAGON DEGREES FROM PAIRS")
    lines.append("-" * 80)
    rev = defaultdict(int)
    for _p, d in pair_decagon_edges:
        rev[d] += 1
    for d in decagon_nodes:
        lines.append(f"decagon {d:2d}  degree_from_pairs = {rev[d]}")
    lines.append("")

    lines.append("PAIR–PAIR OVERLAPS VIA SHARED DECAGONS")
    lines.append("-" * 80)
    shown = 0
    for k, v in sorted(pair_pair_overlap.items()):
        lines.append(f"pairs {k}  shared_decagons={v}")
        shown += 1
        if shown >= 30:
            break
    if shown == 0:
        lines.append("(none found)")
    lines.append("")

    lines.append("DECAGON–DECAGON ADJACENCY")
    lines.append("-" * 80)
    for a, b in decagon_edges[:30]:
        lines.append(f"{a} -- {b}")
    if not decagon_edges:
        lines.append("(none parsed)")
    lines.append("")

    lines.append("PROVISIONAL READ")
    lines.append("-" * 80)
    if len(pair_nodes) == 15 and len(decagon_nodes) == 12:
        lines.append(
            "A canonical 27-object candidate is present: 15 pair/core objects plus 12 decagon objects."
        )
        lines.append(
            "This does not prove exceptional symmetry, but it establishes the minimal combinatorial scaffold "
            "needed to test a 27-state incidence interpretation."
        )
    else:
        lines.append(
            "The current parse did not recover an exact 27-object system. The incidence files may need a more specific parser."
        )
    lines.append("")

    return "\n".join(lines) + "\n"


def main():
    pair_to_decagons = parse_pair_decagon_incidence(PAIR_DECAGON)
    decagon_adj = parse_decagon_graph(DECAGON_GRAPH)
    core_size = parse_core_size(CORE_REPORT)

    payload = build_combined_structure(pair_to_decagons, decagon_adj)

    OUT_TXT.parent.mkdir(parents=True, exist_ok=True)
    OUT_TXT.write_text(summarize(payload, core_size), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"saved {OUT_TXT}")
    print(f"saved {OUT_JSON}")
    print()
    print(OUT_TXT.read_text(encoding='utf-8'))


if __name__ == "__main__":
    main()
