from __future__ import annotations

from itertools import permutations
from pathlib import Path
import ast
import math

import networkx as nx


DECAGON_FILE = Path("artifacts/cycles/ordered_decagon_pair_cycles.txt")


def load_decagons(path: Path) -> list[tuple[int, ...]]:
    lines = [ln.strip() for ln in path.read_text().splitlines() if ln.strip()]
    decagons = []
    for ln in lines:
        if ln.startswith("(") and ln.endswith(")"):
            obj = ast.literal_eval(ln)
            if isinstance(obj, tuple) and len(obj) == 10 and all(isinstance(x, int) for x in obj):
                decagons.append(obj)
    # de-dup, preserve order
    out = []
    seen = set()
    for cyc in decagons:
        if cyc not in seen:
            seen.add(cyc)
            out.append(cyc)
    return out


def build_pair_graph_from_decagons(decagons: list[tuple[int, ...]]) -> nx.Graph:
    G = nx.Graph()
    for cyc in decagons:
        for v in cyc:
            G.add_node(v)
        n = len(cyc)
        for i in range(n):
            a = cyc[i]
            b = cyc[(i + 1) % n]
            if a != b:
                G.add_edge(a, b)
    return G


def canonical_cycle(cyc: tuple[int, ...]) -> tuple[int, ...]:
    """
    Canonical representative up to cyclic rotation and reversal.
    """
    n = len(cyc)
    rots = [tuple(cyc[i:] + cyc[:i]) for i in range(n)]
    rev = tuple(reversed(cyc))
    rev_rots = [tuple(rev[i:] + rev[:i]) for i in range(n)]
    return min(rots + rev_rots)


def image_cycle(perm: dict[int, int], cyc: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(perm[x] for x in cyc)


def main() -> None:
    if not DECAGON_FILE.exists():
        print(f"missing file: {DECAGON_FILE}")
        return

    decagons = load_decagons(DECAGON_FILE)
    print("=" * 80)
    print("DECAGON ORBIT-STABILIZER REPORT")
    print("=" * 80)
    print(f"decagons loaded: {len(decagons)}")

    G = build_pair_graph_from_decagons(decagons)
    print(f"graph vertices: {G.number_of_nodes()}")
    print(f"graph edges: {G.number_of_edges()}")
    print(f"degree set: {sorted(set(dict(G.degree()).values()))}")

    # Compute automorphisms
    gm = nx.algorithms.isomorphism.GraphMatcher(G, G)
    autos = list(gm.isomorphisms_iter())
    group_order = len(autos)
    print(f"automorphisms found: {group_order}")

    can_decagons = {canonical_cycle(cyc) for cyc in decagons}
    print(f"canonical decagons: {len(can_decagons)}")

    # Orbit of first decagon
    target = decagons[0]
    target_can = canonical_cycle(target)

    orbit = set()
    stabilizer = 0

    for perm in autos:
        img = image_cycle(perm, target)
        img_can = canonical_cycle(img)
        orbit.add(img_can)
        if img_can == target_can:
            stabilizer += 1

    print(f"orbit size of first decagon: {len(orbit)}")
    print(f"stabilizer size of first decagon: {stabilizer}")

    if len(orbit) > 0:
        print(f"orbit-stabilizer check: {group_order} ?= {len(orbit)} * {stabilizer}")
        print(f"holds: {group_order == len(orbit) * stabilizer}")

    print()
    print("INTERPRETATION")
    print("-" * 80)
    if len(orbit) == len(can_decagons):
        print("Automorphism group acts transitively on the decagons.")
    else:
        print("Automorphism group does NOT act transitively on the decagons.")

    if group_order == 60 and stabilizer == 5:
        print("This matches the A5/C5 orbit picture: 60 / 5 = 12.")
    elif group_order > 0:
        print(f"Observed quotient group_order / stabilizer = {group_order / stabilizer:.6g}")

if __name__ == "__main__":
    main()
