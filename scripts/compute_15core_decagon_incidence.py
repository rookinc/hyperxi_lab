#!/usr/bin/env python3

from __future__ import annotations

import ast
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IN_CORE = ROOT / "reports" / "quotients" / "probe_15core_as_opposite_edge_pairs.txt"
IN_PAIR_DEC = ROOT / "reports" / "pairs" / "pair_decagon_incidence.txt"

OUT_DIR = ROOT / "reports" / "quotients"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_TXT = OUT_DIR / "core15_decagon_incidence.txt"
OUT_JSON = OUT_DIR / "core15_decagon_incidence.json"


def parse_core60_members(path: Path) -> dict[int, list[int]]:
    text = path.read_text(encoding="utf-8")
    out: dict[int, list[int]] = {}

    # Example:
    #  0 -> 30-pair=(0, 9) -> 60-members=[0, 9, 33, 34]
    pat = re.compile(
        r"^\s*(\d+)\s*->\s*30-pair=\([^)]+\)\s*->\s*60-members=\[([0-9,\s]+)\]\s*$"
    )

    in_block = False
    for line in text.splitlines():
        if "15-LAYER VERTICES EXPANDED BACK TO 60-LAYER" in line:
            in_block = True
            continue
        if in_block and line.startswith("15-CORE ADJACENCY"):
            break
        if not in_block:
            continue

        m = pat.match(line)
        if m:
            vid = int(m.group(1))
            members = [int(x.strip()) for x in m.group(2).split(",")]
            out[vid] = members

    if len(out) != 15:
        raise SystemExit(f"Expected 15 expanded core vertices, found {len(out)}")

    return out


def parse_pair_to_decagons(path: Path) -> dict[int, list[int]]:
    text = path.read_text(encoding="utf-8")
    out: dict[int, list[int]] = {}

    # Example:
    # pair  0 -> decagons [0, 1]
    pat = re.compile(r"^\s*pair\s+(\d+)\s*->\s*decagons\s*(\[[^\]]*\])\s*$")

    for line in text.splitlines():
        m = pat.match(line)
        if not m:
            continue
        pid = int(m.group(1))
        decs = ast.literal_eval(m.group(2))
        out[pid] = [int(x) for x in decs]

    if len(out) == 0:
        raise SystemExit("Could not parse any pair -> decagon incidences")

    return out


def parse_core_adjacency(path: Path) -> dict[int, list[int]]:
    text = path.read_text(encoding="utf-8")
    out: dict[int, list[int]] = {}

    pat = re.compile(r"^\s*(\d+)\s*->\s*\[([0-9,\s]+)\]\s*$")

    in_block = False
    for line in text.splitlines():
        if "15-CORE ADJACENCY" in line:
            in_block = True
            continue
        if in_block and line.startswith("ADJACENCY RULE COUNTS BETWEEN 30-PAIRS"):
            break
        if not in_block:
            continue

        m = pat.match(line)
        if m:
            vid = int(m.group(1))
            nbrs = [int(x.strip()) for x in m.group(2).split(",")]
            out[vid] = nbrs

    return out


def main() -> None:
    core60 = parse_core60_members(IN_CORE)
    pair2dec = parse_pair_to_decagons(IN_PAIR_DEC)
    core_adj = parse_core_adjacency(IN_CORE)

    # chamber ids in the 15-core expansion should be exactly the S-pair ids
    missing = []
    for v, members in core60.items():
        for m in members:
            if m not in pair2dec:
                missing.append((v, m))
    if missing:
        raise SystemExit(f"Some expanded 60-members are missing from pair→decagon map: {missing[:10]}")

    core_to_decagons: dict[int, list[int]] = {}
    core_to_member_decagons: dict[int, dict[int, list[int]]] = {}

    for v, members in core60.items():
        member_map = {}
        decs = set()
        for m in members:
            ds = sorted(pair2dec[m])
            member_map[m] = ds
            decs.update(ds)
        core_to_member_decagons[v] = member_map
        core_to_decagons[v] = sorted(decs)

    hist = defaultdict(int)
    signature_classes = defaultdict(list)
    for v, decs in core_to_decagons.items():
        hist[len(decs)] += 1
        signature_classes[tuple(decs)].append(v)

    # edge overlap statistics on the 15-core
    edge_overlaps = []
    for u, nbrs in core_adj.items():
        for v in nbrs:
            if u < v:
                su = set(core_to_decagons[u])
                sv = set(core_to_decagons[v])
                edge_overlaps.append(
                    {
                        "u": u,
                        "v": v,
                        "overlap_size": len(su & sv),
                        "shared_decagons": sorted(su & sv),
                        "u_only": sorted(su - sv),
                        "v_only": sorted(sv - su),
                    }
                )

    nonedge_overlaps = []
    verts = sorted(core60)
    for i, u in enumerate(verts):
        for v in verts[i + 1 :]:
            if v in core_adj.get(u, []):
                continue
            su = set(core_to_decagons[u])
            sv = set(core_to_decagons[v])
            nonedge_overlaps.append(
                {
                    "u": u,
                    "v": v,
                    "overlap_size": len(su & sv),
                    "shared_decagons": sorted(su & sv),
                }
            )

    edge_hist = defaultdict(int)
    for e in edge_overlaps:
        edge_hist[e["overlap_size"]] += 1

    nonedge_hist = defaultdict(int)
    for e in nonedge_overlaps:
        nonedge_hist[e["overlap_size"]] += 1

    payload = {
        "core_to_60_members": core60,
        "core_to_decagons": core_to_decagons,
        "core_to_member_decagons": core_to_member_decagons,
        "signature_classes": {
            str(list(sig)): cls for sig, cls in sorted(signature_classes.items(), key=lambda kv: (len(kv[0]), kv[0]))
        },
        "decagon_count_histogram": dict(sorted(hist.items())),
        "edge_overlap_histogram": dict(sorted(edge_hist.items())),
        "nonedge_overlap_histogram": dict(sorted(nonedge_hist.items())),
        "edge_overlaps": edge_overlaps,
        "nonedge_overlaps": nonedge_overlaps[:100],
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = []
    lines.append("=" * 80)
    lines.append("15-CORE / DECAGON INCIDENCE")
    lines.append("=" * 80)
    lines.append("Assumption used: the 60 S-pair ids are the 60 chamber classes.")
    lines.append("Therefore the 60-members listed for each 15-core vertex can be")
    lines.append("looked up directly in pair_decagon_incidence.txt.")
    lines.append("")

    lines.append("15-CORE VERTEX -> 60-MEMBERS -> DECAGONS")
    lines.append("-" * 80)
    for v in sorted(core60):
        lines.append(f"{v:2d} -> members={core60[v]} -> decagons={core_to_decagons[v]}")
        for m in core60[v]:
            lines.append(f"      chamber/S-pair {m:2d} -> decagons {core_to_member_decagons[v][m]}")
    lines.append("")

    lines.append("HISTOGRAM: NUMBER OF DISTINCT DECAGONS SEEN BY A 15-CORE VERTEX")
    lines.append("-" * 80)
    for k, c in sorted(hist.items()):
        lines.append(f"{k} decagons: {c} core vertices")
    lines.append("")

    lines.append("SIGNATURE CLASSES OF 15-CORE VERTICES BY DECAGON-SET")
    lines.append("-" * 80)
    for sig, cls in sorted(signature_classes.items(), key=lambda kv: (len(kv[0]), kv[0])):
        lines.append(f"decagons={list(sig)} -> core_vertices={cls}")
    lines.append("")

    lines.append("15-CORE EDGE OVERLAP HISTOGRAM (shared decagons)")
    lines.append("-" * 80)
    for k, c in sorted(edge_hist.items()):
        lines.append(f"overlap {k}: {c} edges")
    lines.append("")

    lines.append("15-CORE NONEDGE OVERLAP HISTOGRAM (shared decagons)")
    lines.append("-" * 80)
    for k, c in sorted(nonedge_hist.items()):
        lines.append(f"overlap {k}: {c} nonedges")
    lines.append("")

    lines.append("FIRST 30 EDGE OVERLAP DETAILS")
    lines.append("-" * 80)
    for e in edge_overlaps[:30]:
        lines.append(
            f"{e['u']:2d}-{e['v']:2d}: shared={e['shared_decagons']} "
            f"| u_only={e['u_only']} | v_only={e['v_only']}"
        )
    lines.append("")

    lines.append("INTERPRETATION")
    lines.append("-" * 80)
    lines.append("If every 15-core vertex sees a structured subset of the 12 decagons,")
    lines.append("then the Petersen-derived core sits canonically inside the global")
    lines.append("Petrie transport system.")
    lines.append("If edge-vs-nonedge overlap histograms separate cleanly, the decagon")
    lines.append("incidence may recover the 15-core adjacency rule directly.")
    lines.append("")

    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"saved {OUT_TXT}")
    print(f"saved {OUT_JSON}")
    print()
    print(OUT_TXT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
