#!/usr/bin/env python3

import json
from pathlib import Path

ROOTED_JSON = Path("cocycles/tables/rooted_petrie_parity_sector_table.json")
OUTPUT = Path("cocycles/tables/rooted_petrie_holonomy_allplus.json")
REPORT = Path("cocycles/tables/rooted_petrie_holonomy_allplus_report.txt")


def main():
    if not ROOTED_JSON.exists():
        raise SystemExit(f"Missing rooted Petrie sector table: {ROOTED_JSON}")

    rooted = json.loads(ROOTED_JSON.read_text(encoding="utf-8"))["sectors"]

    out_rows = []
    root_summary = []

    total_plus = 0
    total_minus = 0

    for row in rooted:
        root = int(row["vertex"])
        chosen_cycles = row.get("chosen_cycles", [])

        plus_count = len(chosen_cycles)
        minus_count = 0
        total_plus += plus_count

        cycle_rows = []
        for j, cyc in enumerate(chosen_cycles):
            cycle_rows.append({
                "local_cycle_id": j,
                "cycle": [int(x) for x in cyc],
                "parity_mod_2": 0,
                "holonomy_sign": 1,
            })

        out_rows.append({
            "vertex": root,
            "cycles": cycle_rows,
        })

        root_summary.append({
            "vertex": root,
            "holonomy_plus": plus_count,
            "holonomy_minus": minus_count,
        })

    out = {
        "summary": {
            "vertices": len(rooted),
            "total_holonomy_plus": total_plus,
            "total_holonomy_minus": total_minus,
        },
        "per_vertex": root_summary,
        "vertices_data": out_rows,
    }

    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    report = []
    report.append("ROOTED PETRIE HOLONOMY ALL-PLUS REPORT")
    report.append("=" * 60)
    report.append(f"vertices: {len(rooted)}")
    report.append(f"total holonomy +1: {total_plus}")
    report.append(f"total holonomy -1: {total_minus}")
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"saved {OUTPUT}")
    print(f"saved {REPORT}")


if __name__ == "__main__":
    main()
