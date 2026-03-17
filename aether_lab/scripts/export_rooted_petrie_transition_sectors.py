#!/usr/bin/env python3

import json
from pathlib import Path

SIGNED_EDGE_JSON = Path("cocycles/tables/signed_edge_table.json")
ROOTED_JSON = Path("cocycles/tables/rooted_petrie_parity_sector_table.json")
OUTPUT = Path("cocycles/tables/rooted_petrie_transition_sector_table.json")
REPORT = Path("cocycles/tables/rooted_petrie_transition_sector_table_report.txt")


def norm_edge(u, v):
    return (u, v) if u <= v else (v, u)


def load_eps():
    data = json.loads(SIGNED_EDGE_JSON.read_text(encoding="utf-8"))
    eps = {}
    for row in data:
        u, v = int(row["edge"][0]), int(row["edge"][1])
        eps[norm_edge(u, v)] = int(row["epsilon"])
    return eps


def cycle_to_transitions(cycle):
    n = len(cycle)
    edges = [norm_edge(cycle[i], cycle[(i + 1) % n]) for i in range(n)]
    trans = []
    for i in range(n):
        trans.append((edges[i], edges[(i + 1) % n]))
    return trans


def main():
    if not SIGNED_EDGE_JSON.exists():
        raise SystemExit(f"Missing signed edge table: {SIGNED_EDGE_JSON}")
    if not ROOTED_JSON.exists():
        raise SystemExit(f"Missing rooted Petrie sector table: {ROOTED_JSON}")

    eps = load_eps()
    rooted = json.loads(ROOTED_JSON.read_text(encoding="utf-8"))["sectors"]

    all_transitions = set()
    sector_rows = []

    for row in rooted:
        root = int(row["vertex"])
        chosen_cycles = row.get("chosen_cycles", [])
        signed_transitions = []

        for cyc in chosen_cycles:
            cyc = [int(x) for x in cyc]
            for e1, e2 in cycle_to_transitions(cyc):
                # sign transition by parity change across consecutive edges
                s = eps[e1] ^ eps[e2]
                signed_transitions.append({
                    "from": [e1[0], e1[1]],
                    "to": [e2[0], e2[1]],
                    "parity": int(s),
                })
                all_transitions.add((e1, e2))

        sector_rows.append({
            "vertex": root,
            "transitions": signed_transitions,
        })

    out = {
        "transition_count": len(all_transitions),
        "sectors": sector_rows,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    report = []
    report.append("ROOTED PETRIE TRANSITION SECTOR EXPORT")
    report.append("=" * 60)
    report.append(f"vertices: {len(sector_rows)}")
    report.append(f"distinct transitions: {len(all_transitions)}")
    report.append(f"avg transitions per sector: {sum(len(r['transitions']) for r in sector_rows)/len(sector_rows):.4f}")
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"saved {OUTPUT}")
    print(f"saved {REPORT}")
    print(f"distinct transitions: {len(all_transitions)}")


if __name__ == "__main__":
    main()
