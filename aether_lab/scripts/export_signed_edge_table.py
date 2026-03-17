#!/usr/bin/env python3

import json
from pathlib import Path

INPUT = Path("aether_lab/data/reports/quotients/g15_edge_sign_table.json")
OUTPUT = Path("cocycles/tables/signed_edge_table.json")


def main():
    if not INPUT.exists():
        raise SystemExit(f"Missing input: {INPUT}")

    data = json.loads(INPUT.read_text(encoding="utf-8"))

    if isinstance(data, dict):
        if "edge_rows" in data:
            rows = data["edge_rows"]
        elif "edges" in data:
            rows = data["edges"]
        else:
            raise SystemExit(f"Unknown JSON schema, keys: {list(data.keys())}")
    else:
        rows = data

    out = []
    for row in rows:
        if "edge" in row:
            u, v = row["edge"]
        elif "u" in row and "v" in row:
            u, v = row["u"], row["v"]
        else:
            raise SystemExit(f"Unrecognized row format: {row}")

        if "epsilon" in row:
            eps = int(row["epsilon"])
        elif "eps" in row:
            eps = int(row["eps"])
        elif "sign" in row:
            sign = int(row["sign"])
            eps = 0 if sign == 1 else 1
        elif "sigma" in row:
            sig = int(row["sigma"])
            eps = 0 if sig == 1 else 1
        else:
            raise SystemExit(f"Missing sign/epsilon in row: {row}")

        out.append({
            "edge": [int(u), int(v)],
            "epsilon": eps,
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"saved {OUTPUT}")
    print(f"edges processed: {len(out)}")


if __name__ == "__main__":
    main()
