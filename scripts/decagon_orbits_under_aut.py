from __future__ import annotations

from pathlib import Path
import ast
import networkx as nx

DECAGON_FILE = Path("artifacts/cycles/ordered_decagon_pair_cycles.txt")


def load_decagons(path: Path):
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line.startswith("decagon") or ":" not in line:
            continue
        payload = line.split(":", 1)[1].strip()
        obj = ast.literal_eval(payload)
        if isinstance(obj, list) and len(obj) == 10:
            out.append(tuple(int(x) for x in obj))
    return out


def build_graph(decagons):
    G = nx.Graph()
    for cyc in decagons:
        n = len(cyc)
        for i in range(n):
            G.add_edge(cyc[i], cyc[(i + 1) % n])
    return G


def canonical_cycle(cyc: tuple[int, ...]) -> tuple[int, ...]:
    n = len(cyc)
    rots = [tuple(cyc[i:] + cyc[:i]) for i in range(n)]
    rev = tuple(reversed(cyc))
    rev_rots = [tuple(rev[i:] + rev[:i]) for i in range(n)]
    return min(rots + rev_rots)


def image_cycle(perm: dict[int, int], cyc: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(perm[x] for x in cyc)


def main():
    decagons = load_decagons(DECAGON_FILE)
    print("=" * 80)
    print("DECAGON ORBITS UNDER CHAMBER GRAPH AUTOMORPHISMS")
    print("=" * 80)
    print("decagons loaded:", len(decagons))

    if not decagons:
        print("No decagons loaded.")
        return

    G = build_graph(decagons)
    print("graph vertices:", G.number_of_nodes())
    print("graph edges:", G.number_of_edges())

    gm = nx.algorithms.isomorphism.GraphMatcher(G, G)
    autos = list(gm.isomorphisms_iter())
    group_order = len(autos)
    print("automorphisms found:", group_order)

    canon_decagons = [canonical_cycle(c) for c in decagons]
    canon_set = sorted(set(canon_decagons))
    print("distinct decagons up to rotation/reversal:", len(canon_set))

    seen = set()
    orbits = []

    for cyc in canon_set:
        if cyc in seen:
            continue
        orb = set()
        for perm in autos:
            img = image_cycle(perm, cyc)
            orb.add(canonical_cycle(img))
        seen.update(orb)
        orbits.append(sorted(orb))

    print()
    print("=" * 80)
    print("DECAGON ORBIT DATA")
    print("=" * 80)
    print("number of decagon orbits:", len(orbits))
    print("orbit sizes:", [len(o) for o in orbits])

    for i, orb in enumerate(orbits):
        print(f"orbit {i:2d}: size={len(orb)}")
        for cyc in orb[:5]:
            print("   ", cyc)
        if len(orb) > 5:
            print("    ...")

    target = canon_set[0]
    target_orbit = set()
    stabilizer = 0
    for perm in autos:
        img = canonical_cycle(image_cycle(perm, target))
        target_orbit.add(img)
        if img == target:
            stabilizer += 1

    print()
    print("=" * 80)
    print("ORBIT-STABILIZER CHECK")
    print("=" * 80)
    print("orbit size of first decagon:", len(target_orbit))
    print("stabilizer size of first decagon:", stabilizer)
    print("group order:", group_order)
    print("orbit * stabilizer:", len(target_orbit) * stabilizer)
    print("check:", group_order == len(target_orbit) * stabilizer)

    if len(orbits) == 1 and len(target_orbit) == 12:
        print()
        print("INTERPRETATION")
        print("-" * 80)
        print("The automorphism group acts transitively on the 12 decagons.")
        print("This supports the idea that the decagons form a single")
        print("face-like symmetry orbit in the chamber graph.")

if __name__ == "__main__":
    main()
