#!/usr/bin/env python3

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_TXT = ROOT / "reports" / "spectral" / "generator_sign_reps.txt"
OUT_JSON = ROOT / "reports" / "spectral" / "generator_sign_reps.json"

LINE_RE = re.compile(
    r"^\s*(\d+)\s+"
    r"([-+]?\d+\.\d+)\s+"
    r"(\d+)\s+"
    r"([+-]I)\s+"
    r"([+-]I)\s+"
    r"([+-]I)\s*$"
)

def main():
    if not IN_TXT.exists():
        raise SystemExit(f"Missing file: {IN_TXT}")

    rows = []
    for line in IN_TXT.read_text(encoding="utf-8").splitlines():
        m = LINE_RE.match(line)
        if not m:
            continue
        block, lam, dim, F, S, V = m.groups()
        rows.append(
            {
                "block": int(block),
                "lambda": float(lam),
                "dim": int(dim),
                "F": F,
                "S": S,
                "V": V,
            }
        )

    if not rows:
        raise SystemExit(f"No rows parsed from {IN_TXT}")

    OUT_JSON.write_text(json.dumps({"blocks": rows}, indent=2), encoding="utf-8")

    print("=" * 80)
    print("EXPORT GENERATOR SIGN REPS JSON")
    print("=" * 80)
    print(f"rows: {len(rows)}")
    print(f"saved {OUT_JSON.relative_to(ROOT)}")
    print("=" * 80)

if __name__ == "__main__":
    main()
