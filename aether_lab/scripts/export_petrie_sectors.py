#!/usr/bin/env python3

import json
from pathlib import Path

SIGNED_EDGE_JSON = Path("cocycles/tables/signed_edge_table.json")
PETRIE_JSON = Path("cocycles/tables/petrie_cycles.json")
OUTPUT = Path("cocycles/tables/petrie_parity_sector_table.json")


def norm(u, v):
    return (u, v) if u <= v else (v, u)


def load_signed_edges():
    data = json.loads(SIGNED_EDGE_JSON.read_text())
    eps = {}
    for row in data:
        u, v = int(row["edge"][0]), int(row["edge"][1])
        eps[norm(u, v)] = int(row["epsilon"])
    return eps


def main():
    eps = load_signed_edges()
    cycles = json.loads(PETRIE_JSON.read_text())["cycles"]

    sectors = []
    for i, cyc in enumerate(cycles):
        even_edges = []
        odd_edges = []

        for j in range(len(cyc)):
            u = cyc[j]
            v = cyc[(j + 1) % len(cyc)]
            e = norm(u, v)

            if eps[e] == 0:
                even_edges.append(list(e))
            else:
                odd_edges.append(list(e))

        sectors.append({
            "cycle_id": i,
            "even_edges": even_edges,
            "odd_edges": odd_edges,
        })

    OUTPUT.write_text(json.dumps({"sectors": sectors}, indent=2))

    print(f"saved {OUTPUT}")
    print(f"sectors: {len(sectors)}")
    print(f"sector size: {len(sectors[0]['even_edges']) + len(sectors[0]['odd_edges']) if sectors else 0}")


if __name__ == "__main__":
    main()
