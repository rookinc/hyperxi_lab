#!/usr/bin/env python3

import json
from pathlib import Path
import argparse
import numpy as np


def norm_edge(u, v):
    return (u, v) if u <= v else (v, u)


def build_signed_M_from_sector_table(sectors, edge_rows, normalize=False):
    edge_to_idx = {
        norm_edge(e["edge"][0], e["edge"][1]): i
        for i, e in enumerate(edge_rows)
    }

    n_edges = len(edge_rows)
    n_sectors = len(sectors)
    M = np.zeros((n_sectors, n_edges), dtype=float)

    for i, sector in enumerate(sectors):
        for e in sector.get("even_edges", []):
            u, v = e
            ne = norm_edge(u, v)
            if ne not in edge_to_idx:
                raise ValueError(f"Sector references unknown edge {ne}")
            M[i, edge_to_idx[ne]] = 1.0

        for e in sector.get("odd_edges", []):
            u, v = e
            ne = norm_edge(u, v)
            if ne not in edge_to_idx:
                raise ValueError(f"Sector references unknown edge {ne}")
            M[i, edge_to_idx[ne]] = -1.0

    if normalize:
        for i in range(n_sectors):
            r = np.linalg.norm(M[i, :])
            if r > 0:
                M[i, :] /= r

    return M


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parity-sector-json", required=True)
    parser.add_argument("--normalize", action="store_true")
    args = parser.parse_args()

    sector_path = Path(args.parity_sector_json)
    edge_path = Path("cocycles/tables/signed_edge_table.json")

    if not sector_path.exists():
        raise SystemExit(f"Missing sector file: {sector_path}")
    if not edge_path.exists():
        raise SystemExit(f"Missing signed edge JSON: {edge_path}")

    sector_data = json.loads(sector_path.read_text(encoding="utf-8"))
    edge_rows = json.loads(edge_path.read_text(encoding="utf-8"))
    sectors = sector_data["sectors"]

    print(f"sectors: {len(sectors)}")
    print(f"edges  : {len(edge_rows)}")
    print(f"normalize: {args.normalize}")

    M = build_signed_M_from_sector_table(sectors, edge_rows, normalize=args.normalize)
    print("M shape:", M.shape)

    K = M.T @ M
    eigvals = np.linalg.eigvalsh(K)

    print("diag(K):")
    print(np.round(np.diag(K), 8))

    print("eigenvalues:")
    print(np.round(np.sort(eigvals), 8))


if __name__ == "__main__":
    main()
