#!/usr/bin/env python3

import json
from pathlib import Path

SIGNED_EDGE_JSON = Path("cocycles/tables/signed_edge_table.json")
ROOTED_JSON = Path("cocycles/tables/rooted_petrie_parity_sector_table.json")
OUTPUT = Path("cocycles/tables/rooted_petrie_holonomy.json")
REPORT = Path("cocycles/tables/rooted_petrie_holonomy_report.txt")


def norm_edge(u, v):
    return (u, v) if u <= v else (v, u)


def load_eps():
    data = json.loads(SIGNED_EDGE_JSON.read_text(encoding="utf-8"))
    eps = {}
    for row in data:
        u, v = int(row["edge"][0]), int(row["edge"][1])
        eps[norm_edge(u, v)] = int(row["epsilon"])
    return eps


def cycle_edges(cycle):
    n = len(cycle)
    return [norm_edge(int(cycle[i]), int(cycle[(i + 1) % n])) for i in range(n)]


def main():
    if not SIGNED_EDGE_JSON.exists():
        raise SystemExit(f"Missing signed edge table: {SIGNED_EDGE_JSON}")
    if not ROOTED_JSON.exists():
        raise SystemExit(f"Missing rooted Petrie sector table: {ROOTED_JSON}")

    eps = load_eps()
    rooted = json.loads(ROOTED_JSON.read_text(encoding="utf-8"))["sectors"]

    out_rows = []
    root_summary = []

    total_plus = 0
    total_minus = 0

    for row in rooted:
        root = int(row["vertex"])
        chosen_cycles = row.get("chosen_cycles", [])

        plus_count = 0
        minus_count = 0
        cycle_rows = []

        for j, cyc in enumerate(chosen_cycles):
            edges = cycle_edges(cyc)
            parity = sum(eps[e] for e in edges) % 2
            sign = 1 if parity == 0 else -1

            if sign == 1:
                plus_count += 1
                total_plus += 1
            else:
                minus_count += 1
                total_minus += 1

            cycle_rows.append({
                "local_cycle_id": j,
                "cycle": [int(x) for x in cyc],
                "parity_mod_2": int(parity),
                "holonomy_sign": int(sign),
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

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    report = []
    report.append("ROOTED PETRIE HOLONOMY REPORT")
    report.append("=" * 60)
    report.append(f"vertices: {len(rooted)}")
    report.append(f"total holonomy +1: {total_plus}")
    report.append(f"total holonomy -1: {total_minus}")
    report.append("")
    report.append("PER VERTEX")
    report.append("-" * 60)
    for row in root_summary:
        report.append(
            f"v={row['vertex']}: +1={row['holonomy_plus']}  -1={row['holonomy_minus']}"
        )

    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"saved {OUTPUT}")
    print(f"saved {REPORT}")
    print(f"total holonomy +1: {total_plus}")
    print(f"total holonomy -1: {total_minus}")


if __name__ == "__main__":
    main()
