#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


def summarize(path: Path) -> None:
    print(f"\n=== {path} ===")
    if not path.exists():
        print("missing")
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"not valid json: {e}")
        return

    print(f"type: {type(data).__name__}")
    if isinstance(data, dict):
        print(f"keys: {list(data.keys())[:20]}")
        for k, v in list(data.items())[:5]:
            print(f"  {k}: {type(v).__name__}")
    elif isinstance(data, list):
        print(f"length: {len(data)}")
        if data:
            first = data[0]
            print(f"first item type: {type(first).__name__}")
            if isinstance(first, dict):
                print(f"first item keys: {list(first.keys())[:20]}")
                print(f"first item preview: {first}")
            else:
                print(f"first item: {first}")


def main() -> None:
    root = Path("cocycles/tables")
    candidates = [
        root / "signed_edge_table.json",
        root / "transport_spec_summary.json",
        root / "minimal_cocycle_support_table.json",
        root / "sector_inner_products_table.json",
        root / "parity_sector_table.json",
    ]
    for p in candidates:
        summarize(p)


if __name__ == "__main__":
    main()
