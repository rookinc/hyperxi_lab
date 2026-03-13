#!/usr/bin/env python3
"""
flag_chamber_graph.py

Build the dodecahedron's 120-flag space using a face-slot-endpoint model,
quotient by endpoint flip to obtain 60 chambers, then derive several
candidate downstairs chamber graphs from the upstairs involutions s0,s1,s2.

This is a verification / exploration scaffold, not yet a claim that any
particular candidate exactly equals the discovered HyperXi graph.

Usage:
    python3 scripts/flag_chamber_graph.py
"""

from __future__ import annotations

from collections import deque
from itertools import combinations
from typing import Callable, Dict, Iterable, List, Set, Tuple

Face = int
Slot = int
Side = int  # 0 or 1
Flag = Tuple[Face, Slot, Side]
Chamber = Tuple[Face, Slot]

MOD = 5

# ---------------------------------------------------------------------
# Face neighbor cycles
# ---------------------------------------------------------------------
# The k-th slot of face f is the edge shared with FACE_CYCLES[f][k].
# Cycles are chosen consistently with the earlier chat derivation.

FACE_CYCLES: Dict[Face, List[Face]] = {
    0:  [3, 5, 7, 9, 11],
    1:  [2, 4, 6, 8, 10],
    2:  [1, 4, 3, 11, 10],
    4:  [1, 6, 5, 3, 2],
    6:  [1, 8, 7, 5, 4],
    8:  [1, 10, 9, 7, 6],
    10: [1, 2, 11, 9, 8],
    3:  [0, 11, 2, 4, 5],
    5:  [0, 3, 4, 6, 7],
    7:  [0, 5, 6, 8, 9],
    9:  [0, 7, 8, 10, 11],
    11: [0, 9, 10, 2, 3],
}

FACES = sorted(FACE_CYCLES.keys())

# Reverse lookup: for each shared edge (f, k), what slot j on the adjacent face g points back to f?
EDGE_BACKREF: Dict[Tuple[Face, Slot], Tuple[Face, Slot]] = {}
for f, cyc in FACE_CYCLES.items():
    for k, g in enumerate(cyc):
        try:
            j = FACE_CYCLES[g].index(f)
        except ValueError as exc:
            raise RuntimeError(f"Inconsistent face cycles: face {g} does not point back to {f}") from exc
        EDGE_BACKREF[(f, k)] = (g, j)

# ---------------------------------------------------------------------
# Upstairs flag operators
# ---------------------------------------------------------------------
# A flag is represented as (face, slot, side)
#
# For face f and slot k:
#   - the chamber is the face-edge incidence (f, k)
#   - there are two upstairs flags over that chamber, one at each endpoint
#
# side = 0 corresponds to the endpoint between slots (k-1, k)
# side = 1 corresponds to the endpoint between slots (k, k+1)

def mod5(x: int) -> int:
    return x % MOD


def chamber_of(flag: Flag) -> Chamber:
    f, k, _ = flag
    return (f, k)


def s0(flag: Flag) -> Flag:
    """Endpoint flip along the same face-edge incidence."""
    f, k, side = flag
    return (f, k, 1 - side)


def s1(flag: Flag) -> Flag:
    """
    Face-corner turn: keep (vertex, face), switch to the other face-edge
    at that vertex.

    If side=0, endpoint is between slots (k-1, k), so the other slot is k-1.
    If side=1, endpoint is between slots (k, k+1), so the other slot is k+1.
    """
    f, k, side = flag
    if side == 0:
        return (f, mod5(k - 1), 1)
    else:
        return (f, mod5(k + 1), 0)


def s2(flag: Flag) -> Flag:
    """
    Edge-face swap: cross the current edge to the adjacent face, preserving
    the same vertex.

    Because the shared edge is traversed with opposite face orientation,
    side flips when crossing.
    """
    f, k, side = flag
    g, j = EDGE_BACKREF[(f, k)]
    return (g, j, 1 - side)


OPS: Dict[str, Callable[[Flag], Flag]] = {
    "s0": s0,
    "s1": s1,
    "s2": s2,
}


def apply_word(flag: Flag, word: Iterable[str]) -> Flag:
    x = flag
    for op_name in word:
        x = OPS[op_name](x)
    return x


# ---------------------------------------------------------------------
# Chamber set and human-readable labels
# ---------------------------------------------------------------------

CHAMBERS: List[Chamber] = [(f, k) for f in FACES for k in range(5)]


def chamber_label(ch: Chamber) -> str:
    f, k = ch
    g = FACE_CYCLES[f][k]
    return f"({f}|edge->{g})"


# ---------------------------------------------------------------------
# Downstairs move families derived from the upstairs operators
# ---------------------------------------------------------------------

def reps(ch: Chamber) -> Tuple[Flag, Flag]:
    f, k = ch
    return (f, k, 0), (f, k, 1)


def same_face_turns(ch: Chamber) -> Set[Chamber]:
    """
    Downstairs image of s1 from both endpoint representatives.
    This yields the two adjacent slots on the same face.
    """
    out = {chamber_of(s1(r)) for r in reps(ch)}
    if len(out) != 2:
        raise RuntimeError(f"Expected 2 same-face turns for {ch}, got {out}")
    return out


def pure_cross(ch: Chamber) -> Set[Chamber]:
    """
    Downstairs image of s2 from either representative.
    Both reps should land on the same chamber after quotienting.
    """
    out = {chamber_of(s2(r)) for r in reps(ch)}
    if len(out) != 1:
        raise RuntimeError(f"Expected unique pure cross for {ch}, got {out}")
    return out


def branch(ch: Chamber, word: Iterable[str]) -> Set[Chamber]:
    """
    Apply an upstairs word to both representatives of a chamber, then quotient.
    For some words this yields a 2-valued branching move downstairs.
    """
    return {chamber_of(apply_word(r, word)) for r in reps(ch)}


# Named move families
def move_RR(ch: Chamber) -> Set[Chamber]:
    return same_face_turns(ch)


def move_T(ch: Chamber) -> Set[Chamber]:
    return pure_cross(ch)


def move_s2s1(ch: Chamber) -> Set[Chamber]:
    # "turn then cross" downstairs branching
    return branch(ch, ["s1", "s2"])


def move_s1s2(ch: Chamber) -> Set[Chamber]:
    # "cross then turn" downstairs branching
    return branch(ch, ["s2", "s1"])


MOVE_FAMILIES: Dict[str, Callable[[Chamber], Set[Chamber]]] = {
    "RR": move_RR,
    "T": move_T,
    "s2s1": move_s2s1,
    "s1s2": move_s1s2,
}

# ---------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------

def build_graph(move_names: List[str]) -> Dict[Chamber, Set[Chamber]]:
    """
    Build an undirected graph by symmetrizing the selected downstairs move families.
    """
    adj: Dict[Chamber, Set[Chamber]] = {ch: set() for ch in CHAMBERS}

    for ch in CHAMBERS:
        for name in move_names:
            nbrs = MOVE_FAMILIES[name](ch)
            for nb in nbrs:
                if nb == ch:
                    continue
                adj[ch].add(nb)
                adj[nb].add(ch)

    return adj


# ---------------------------------------------------------------------
# Graph invariants
# ---------------------------------------------------------------------

def edge_count(adj: Dict[Chamber, Set[Chamber]]) -> int:
    return sum(len(v) for v in adj.values()) // 2


def degree_set(adj: Dict[Chamber, Set[Chamber]]) -> List[int]:
    return sorted(set(len(v) for v in adj.values()))


def bfs_distances(adj: Dict[Chamber, Set[Chamber]], src: Chamber) -> Dict[Chamber, int]:
    dist = {src: 0}
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def is_connected(adj: Dict[Chamber, Set[Chamber]]) -> bool:
    if not adj:
        return True
    start = next(iter(adj))
    return len(bfs_distances(adj, start)) == len(adj)


def diameter(adj: Dict[Chamber, Set[Chamber]]) -> int | None:
    if not is_connected(adj):
        return None
    diam = 0
    for ch in adj:
        d = bfs_distances(adj, ch)
        diam = max(diam, max(d.values()))
    return diam


def shell_profile(adj: Dict[Chamber, Set[Chamber]], src: Chamber) -> List[int]:
    dist = bfs_distances(adj, src)
    maxd = max(dist.values())
    return [sum(1 for x in dist.values() if x == d) for d in range(maxd + 1)]


def triangle_count(adj: Dict[Chamber, Set[Chamber]]) -> int:
    nodes = list(adj.keys())
    idx = {u: i for i, u in enumerate(nodes)}
    count = 0
    for u in nodes:
        for v in adj[u]:
            if idx[v] <= idx[u]:
                continue
            common = adj[u].intersection(adj[v])
            for w in common:
                if idx[w] > idx[v]:
                    count += 1
    return count


def print_graph_report(name: str, adj: Dict[Chamber, Set[Chamber]]) -> None:
    print("=" * 80)
    print(name)
    print("=" * 80)
    print(f"vertices:   {len(adj)}")
    print(f"edges:      {edge_count(adj)}")
    print(f"degree set: {degree_set(adj)}")
    print(f"connected:  {is_connected(adj)}")
    print(f"triangles:  {triangle_count(adj)}")
    print(f"diameter:   {diameter(adj)}")
    print()

    samples = [
        (7, 0),  # face 7 axial
        (7, 1),  # face 7 circulation
        (7, 2),  # face 7 bridge
    ]
    print("sample shell profiles:")
    for ch in samples:
        prof = shell_profile(adj, ch)
        print(f"  {chamber_label(ch):>14} -> {prof}")
    print()

    print("sample local neighborhoods:")
    for ch in samples:
        nbs = sorted(adj[ch])
        labels = ", ".join(chamber_label(x) for x in nbs)
        print(f"  {chamber_label(ch):>14} -> {labels}")
    print()


# ---------------------------------------------------------------------
# Sanity checks on upstairs structure
# ---------------------------------------------------------------------

def run_sanity_checks() -> None:
    # 120 flags
    all_flags = [(f, k, side) for f in FACES for k in range(5) for side in (0, 1)]
    assert len(all_flags) == 120

    # Involutions
    for fl in all_flags:
        assert s0(s0(fl)) == fl
        assert s1(s1(fl)) == fl
        assert s2(s2(fl)) == fl

    # Chamber quotient size
    chamber_orbits = {}
    for fl in all_flags:
        orbit = tuple(sorted([fl, s0(fl)]))
        chamber_orbits[orbit] = True
    assert len(chamber_orbits) == 60

    # Each chamber has two same-face turns and one pure cross
    for ch in CHAMBERS:
        assert len(same_face_turns(ch)) == 2
        assert len(pure_cross(ch)) == 1


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:
    run_sanity_checks()

    print("=" * 80)
    print("HYPERXI FLAG-TO-CHAMBER EXPLORATION")
    print("=" * 80)
    print("120 upstairs flags built from (face, slot, endpoint-side)")
    print("60 downstairs chambers built by quotienting endpoint flip")
    print()

    candidates = {
        "BASE_CHAMBER_GRAPH = RR + T": ["RR", "T"],
        "CANDIDATE_A = RR + s2s1": ["RR", "s2s1"],
        "CANDIDATE_B = RR + s1s2": ["RR", "s1s2"],
        "CANDIDATE_C = s2s1 + s1s2": ["s2s1", "s1s2"],
        "CANDIDATE_D = RR + T + s2s1 + s1s2": ["RR", "T", "s2s1", "s1s2"],
    }

    for name, moves in candidates.items():
        adj = build_graph(moves)
        print_graph_report(name, adj)

    print("=" * 80)
    print("NOTES")
    print("=" * 80)
    print("* RR means the two same-face turns (clockwise/counterclockwise on a face).")
    print("* T means pure crossing across the current edge into the adjacent face.")
    print("* s2s1 and s1s2 are the two short composite upstairs words, projected")
    print("  downstairs by applying them to both endpoint representatives and")
    print("  then quotienting.")
    print("* The right match, if any, is the one whose invariants line up with your")
    print("  observed 60-vertex graph.")
    print()

if __name__ == "__main__":
    main()
