#!/usr/bin/env python3

import json
from pathlib import Path
import argparse
import numpy as np


def norm_edge(u, v):
    return (u, v) if u <= v else (v, u)


def load_transition_matrix(path, normalize=False):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    sectors = data["sectors"]

    transition_set = set()
    for row in sectors:
        for t in row["transitions"]:
            e1 = norm_edge(t["from"][0], t["from"][1])
            e2 = norm_edge(t["to"][0], t["to"][1])
            transition_set.add((e1, e2))

    transitions = sorted(transition_set)
    idx = {tr: i for i, tr in enumerate(transitions)}

    M = np.zeros((len(sectors), len(transitions)), dtype=float)

    for i, row in enumerate(sectors):
        for t in row["transitions"]:
            e1 = norm_edge(t["from"][0], t["from"][1])
            e2 = norm_edge(t["to"][0], t["to"][1])
            j = idx[(e1, e2)]
            sign = -1.0 if int(t["parity"]) == 1 else 1.0
            M[i, j] += sign

    if normalize:
        for i in range(M.shape[0]):
            r = np.linalg.norm(M[i, :])
            if r > 0:
                M[i, :] /= r

    return M, transitions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--transition-json", required=True)
    parser.add_argument("--normalize", action="store_true")
    args = parser.parse_args()

    M, transitions = load_transition_matrix(args.transition_json, normalize=args.normalize)

    print(f"sectors: {M.shape[0]}")
    print(f"transitions: {M.shape[1]}")
    print(f"normalize: {args.normalize}")

    G = M @ M.T
    eigvals = np.linalg.eigvalsh(G)

    print("row norms:")
    print(np.round(np.linalg.norm(M, axis=1), 8))

    print("eigenvalues:")
    print(np.round(np.sort(eigvals), 8))


if __name__ == "__main__":
    main()
