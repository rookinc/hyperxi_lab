#!/usr/bin/env python3

import json
from pathlib import Path

ROOTED_JSON = Path("cocycles/tables/rooted_petrie_parity_sector_table.json")
OUTPUT = Path("cocycles/tables/rooted_petrie_transition_sector_table_allplus.json")


def norm_edge(u, v):
    return (u, v) if u <= v else (v, u)


def cycle_to_transitions(cycle):
    n = len(cycle)
    edges = [norm_edge(cycle[i], cycle[(i + 1) % n]) for i in range(n)]
    trans = []
    for i in range(n):
        trans.append((edges[i], edges[(i + 1) % n]))
    return trans


def main():
    rooted = json.loads(ROOTED_JSON.read_text(encoding="utf-8"))["sectors"]
    rows = []

    for row in rooted:
        out = []
        for cyc in row.get("chosen_cycles", []):
            cyc = [int(x) for x in cyc]
            for e1, e2 in cycle_to_transitions(cyc):
                out.append({
                    "from": [e1[0], e1[1]],
                    "to": [e2[0], e2[1]],
                    "parity": 0,
                })
        rows.append({
            "vertex": int(row["vertex"]),
            "transitions": out,
        })

    OUTPUT.write_text(json.dumps({"sectors": rows}, indent=2), encoding="utf-8")
    print(f"saved {OUTPUT}")


if __name__ == "__main__":
    main()
