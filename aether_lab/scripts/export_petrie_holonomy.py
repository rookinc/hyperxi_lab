#!/usr/bin/env python3

import json
from pathlib import Path

SIGNED_EDGE_JSON = Path("cocycles/tables/signed_edge_table.json")
PETRIE_JSON = Path("cocycles/tables/petrie_cycles.json")
OUTPUT = Path("cocycles/tables/petrie_holonomy.json")
REPORT = Path("cocycles/tables/petrie_holonomy_report.txt")


def norm_edge(u, v):
    return (u, v) if u <= v else (v, u)


def load_eps():
    data = json.loads(SIGNED_EDGE_JSON.read_text(encoding="utf-8"))
    eps = {}
    for row in data:
        u, v = int(row["edge"][0]), int(row["edge"][1])
        eps[norm_edge(u, v)] = int(row["epsilon"])
    return eps


def load_cycles():
    data = json.loads(PETRIE_JSON.read_text(encoding="utf-8"))
    return data["cycles"] if isinstance(data, dict) and "cycles" in data else data


def cycle_edges(cycle):
    n = len(cycle)
    return [norm_edge(int(cycle[i]), int(cycle[(i + 1) % n])) for i in range(n)]


def main():
    if not SIGNED_EDGE_JSON.exists():
        raise SystemExit(f"Missing signed edge table: {SIGNED_EDGE_JSON}")
    if not PETRIE_JSON.exists():
        raise SystemExit(f"Missing Petrie cycles file: {PETRIE_JSON}")

    eps = load_eps()
    cycles = load_cycles()

    rows = []
    plus_count = 0
    minus_count = 0

    for i, cyc in enumerate(cycles):
        edges = cycle_edges(cyc)
        parity = sum(eps[e] for e in edges) % 2
        sign = 1 if parity == 0 else -1
        if sign == 1:
            plus_count += 1
        else:
            minus_count += 1

        rows.append({
            "cycle_id": i,
            "cycle": [int(x) for x in cyc],
            "edges": [[e[0], e[1]] for e in edges],
            "parity_mod_2": int(parity),
            "holonomy_sign": int(sign),
        })

    out = {
        "summary": {
            "num_cycles": len(rows),
            "holonomy_plus": plus_count,
            "holonomy_minus": minus_count,
        },
        "cycles": rows,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    report = []
    report.append("PETRIE HOLONOMY REPORT")
    report.append("=" * 60)
    report.append(f"num cycles: {len(rows)}")
    report.append(f"holonomy +1: {plus_count}")
    report.append(f"holonomy -1: {minus_count}")
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"saved {OUTPUT}")
    print(f"saved {REPORT}")
    print(f"holonomy +1: {plus_count}")
    print(f"holonomy -1: {minus_count}")


if __name__ == "__main__":
    main()
