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

OUT_TXT = OUT_DIR / "core15_to_decagons.txt"
OUT_JSON = OUT_DIR / "core15_to_decagons.json"


def parse_core60_members(path: Path) -> dict[int, list[int]]:
    text = path.read_text(encoding="utf-8")
    out: dict[int, list[int]] = {}

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

    if len(out) != 15:
        raise SystemExit(f"Expected 15 core adjacency rows, found {len(out)}")

    return out


def parse_pair_to_decagons(path: Path) -> dict[int, list[int]]:
    text = path.read_text(encoding="utf-8")
    out: dict[int, list[int]] = {}

    # parse from the full decagon blocks, not just the “first 20”
    dec_pat = re.compile(r"^\s*decagon\s+(\d+):\s*$")
    list_pat = re.compile(r"^\s*unique pair ids:\s*(\[[^\]]*\])\s*$")

    current_dec = None
    for line in text.splitlines():
        m = dec_pat.match(line)
        if m:
            current_dec = int(m.group(1))
            continue

        m = list_pat.match(line)
        if m and current_dec is not None:
            pairs = ast.literal_eval(m.group(1))
            for pid in pairs:
                out.setdefault(int(pid), []).append(current_dec)
            current_dec = None

    if len(out) != 60:
        raise SystemExit(f"Expected 60 pair ids, found {len(out)}")

    for pid in sorted(out):
        out[pid] = sorted(out[pid])

    return out


def main():
    core60 = parse_core60_members(IN_CORE)
    core_adj = parse_core_adjacency(IN_CORE)
    pair2dec = parse_pair_to_decagons(IN_PAIR_DEC)

    missing = []
    for v, members in core60.items():
        for m in members:
            if m not in pair2dec:
                missing.append((v, m))
    if missing:
        raise SystemExit(f"Missing chamber/pair ids in decagon map: {missing[:20]}")

    core_to_decagons: dict[int, list[int]] = {}
    core_member_decagons: dict[int, dict[int, list[int]]] = {}

    for v in sorted(core60):
        decs = set()
        member_map = {}
        for m in core60[v]:
            ds = pair2dec[m]
            member_map[m] = ds
            decs.update(ds)
        core_member_decagons[v] = member_map
        core_to_decagons[v] = sorted(decs)

    hist = defaultdict(int)
    sig_classes = defaultdict(list)
    for v, ds in core_to_decagons.items():
        hist[len(ds)] += 1
        sig_classes[tuple(ds)].append(v)

    edge_hist = defaultdict(int)
    edge_details = []
    for u, nbrs in core_adj.items():
        for v in nbrs:
            if u < v:
                su = set(core_to_decagons[u])
                sv = set(core_to_decagons[v])
                shared = sorted(su & sv)
                edge_hist[len(shared)] += 1
                edge_details.append(
                    {
                        "u": u,
                        "v": v,
                        "shared": shared,
                        "u_only": sorted(su - sv),
                        "v_only": sorted(sv - su),
                    }
                )

    nonedge_hist = defaultdict(int)
    verts = sorted(core_to_decagons)
    for i, u in enumerate(verts):
        for v in verts[i + 1 :]:
            if v in core_adj[u]:
                continue
            su = set(core_to_decagons[u])
            sv = set(core_to_decagons[v])
            nonedge_hist[len(su & sv)] += 1

    payload = {
        "core_to_60_members": core60,
        "core_to_decagons": core_to_decagons,
        "core_member_decagons": core_member_decagons,
        "signature_classes": {str(list(k)): v for k, v in sig_classes.items()},
        "decagon_count_histogram": dict(sorted(hist.items())),
        "edge_overlap_histogram": dict(sorted(edge_hist.items())),
        "nonedge_overlap_histogram": dict(sorted(nonedge_hist.items())),
        "edge_details": edge_details,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = []
    lines.append("=" * 80)
    lines.append("15-CORE → DECAGON INCIDENCE")
    lines.append("=" * 80)
    lines.append("Using the confirmed identity chamber_id == S_pair_id.")
    lines.append("")

    lines.append("CORE VERTEX TO DECAGONS")
    lines.append("-" * 80)
    for v in sorted(core_to_decagons):
        lines.append(f"{v:2d} -> members={core60[v]} -> decagons={core_to_decagons[v]}")
        for m in core60[v]:
            lines.append(f"      {m:2d} -> {pair2dec[m]}")
    lines.append("")

    lines.append("HISTOGRAM: DISTINCT DECAGONS PER 15-CORE VERTEX")
    lines.append("-" * 80)
    for k, c in sorted(hist.items()):
        lines.append(f"{k} decagons: {c} vertices")
    lines.append("")

    lines.append("SIGNATURE CLASSES")
    lines.append("-" * 80)
    for sig, cls in sorted(sig_classes.items(), key=lambda kv: (len(kv[0]), kv[0])):
        lines.append(f"{list(sig)} -> {cls}")
    lines.append("")

    lines.append("EDGE OVERLAP HISTOGRAM")
    lines.append("-" * 80)
    for k, c in sorted(edge_hist.items()):
        lines.append(f"shared {k}: {c} edges")
    lines.append("")

    lines.append("NONEDGE OVERLAP HISTOGRAM")
    lines.append("-" * 80)
    for k, c in sorted(nonedge_hist.items()):
        lines.append(f"shared {k}: {c} nonedges")
    lines.append("")

    lines.append("FIRST 30 EDGE DETAILS")
    lines.append("-" * 80)
    for e in edge_details[:30]:
        lines.append(
            f"{e['u']:2d}-{e['v']:2d}: shared={e['shared']} | "
            f"u_only={e['u_only']} | v_only={e['v_only']}"
        )
    lines.append("")

    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"saved {OUT_TXT}")
    print(f"saved {OUT_JSON}")
    print()
    print(OUT_TXT.read_text(encoding='utf-8'))


if __name__ == "__main__":
    main()
