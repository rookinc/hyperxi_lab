from __future__ import annotations

from dataclasses import dataclass


FACE_COUNT = 12
FACE_SIZE = 5
ORIENTATION_COUNT = 2
FLAG_COUNT = FACE_COUNT * FACE_SIZE * ORIENTATION_COUNT  # 120


@dataclass(frozen=True)
class Flag:
    """
    Minimal scaffold flag.

    face:
        which dodecahedron face chart we are on (0..11)

    slot:
        local position around that face (0..4)

    orient:
        local orientation bit (0 or 1)

    This is a temporary canonical 120-state model for bootstrapping the lab.
    Later, we can replace it with the true (v, e, f) lifted-flag incidence model
    without changing the public API.
    """

    face: int
    slot: int
    orient: int

    def __post_init__(self) -> None:
        if not (0 <= self.face < FACE_COUNT):
            raise ValueError(f"face out of range: {self.face}")
        if not (0 <= self.slot < FACE_SIZE):
            raise ValueError(f"slot out of range: {self.slot}")
        if self.orient not in (0, 1):
            raise ValueError(f"orient must be 0 or 1, got {self.orient}")


def all_flags() -> list[Flag]:
    return [
        Flag(face=face, slot=slot, orient=orient)
        for face in range(FACE_COUNT)
        for slot in range(FACE_SIZE)
        for orient in range(ORIENTATION_COUNT)
    ]


# -------------------------------------------------------------------
# Real dodecahedral face-edge transport tables
# -------------------------------------------------------------------
#
# These are derived from src/hyperxi/geometry/incidences.py.
#
# For each face f and local slot s, the edge
#   (face_vertices[s], face_vertices[(s+1) % 5])
# determines a unique adjacent face and a unique corresponding slot on
# that adjacent face.


FACE_NEIGHBORS: dict[int, tuple[int, int, int, int, int]] = {
    0:  (1, 2, 3, 4, 5),
    1:  (5, 6, 7, 2, 0),
    2:  (1, 7, 8, 3, 0),
    3:  (2, 8, 9, 4, 0),
    4:  (3, 9, 10, 5, 0),
    5:  (4, 10, 6, 1, 0),
    6:  (7, 1, 5, 10, 11),
    7:  (8, 2, 1, 6, 11),
    8:  (9, 3, 2, 7, 11),
    9:  (10, 4, 3, 8, 11),
    10: (6, 5, 4, 9, 11),
    11: (7, 8, 9, 10, 6),
}


FACE_SLOT_MAP: dict[tuple[int, int], int] = {
    (0, 0): 4,
    (0, 1): 4,
    (0, 2): 4,
    (0, 3): 4,
    (0, 4): 4,

    (1, 0): 3,
    (1, 1): 1,
    (1, 2): 2,
    (1, 3): 0,
    (1, 4): 0,

    (2, 0): 3,
    (2, 1): 1,
    (2, 2): 2,
    (2, 3): 0,
    (2, 4): 1,

    (3, 0): 3,
    (3, 1): 1,
    (3, 2): 2,
    (3, 3): 0,
    (3, 4): 2,

    (4, 0): 3,
    (4, 1): 1,
    (4, 2): 2,
    (4, 3): 0,
    (4, 4): 3,

    (5, 0): 3,
    (5, 1): 1,
    (5, 2): 2,
    (5, 3): 0,
    (5, 4): 4,

    (6, 0): 3,
    (6, 1): 1,
    (6, 2): 2,
    (6, 3): 0,
    (6, 4): 4,

    (7, 0): 3,
    (7, 1): 1,
    (7, 2): 2,
    (7, 3): 0,
    (7, 4): 0,

    (8, 0): 3,
    (8, 1): 1,
    (8, 2): 2,
    (8, 3): 0,
    (8, 4): 1,

    (9, 0): 3,
    (9, 1): 1,
    (9, 2): 2,
    (9, 3): 0,
    (9, 4): 2,

    (10, 0): 3,
    (10, 1): 1,
    (10, 2): 2,
    (10, 3): 0,
    (10, 4): 3,

    (11, 0): 4,
    (11, 1): 4,
    (11, 2): 4,
    (11, 3): 4,
    (11, 4): 4,
}


def S(flag: Flag) -> Flag:
    """
    Edge-flip style involution.
    """
    return Flag(flag.face, flag.slot, 1 - flag.orient)


def F(flag: Flag) -> Flag:
    """
    Face-rotation style move.
    """
    step = 1 if flag.orient == 0 else -1
    return Flag(flag.face, (flag.slot + step) % FACE_SIZE, flag.orient)


def V(flag: Flag) -> Flag:
    """
    Cross the local face edge at the current slot into the adjacent face.

    Current scaffold convention:
    - move to the adjacent face across the edge indexed by `slot`
    - land on the corresponding edge-slot of the adjacent face
    - flip the local orientation bit
    """
    next_face = FACE_NEIGHBORS[flag.face][flag.slot]
    next_slot = FACE_SLOT_MAP[(flag.face, flag.slot)]
    return Flag(next_face, next_slot, 1 - flag.orient)


GENERATORS: dict[str, callable] = {
    "S": S,
    "F": F,
    "V": V,
}


def apply_generator(flag: Flag, generator: str) -> Flag:
    try:
        fn = GENERATORS[generator]
    except KeyError as exc:
        raise ValueError(f"unknown generator: {generator}") from exc
    return fn(flag)


def apply_word(flag: Flag, word: str) -> Flag:
    current = flag
    for ch in word:
        current = apply_generator(current, ch)
    return current


def orbit(flag: Flag, word: str, max_steps: int = 10_000) -> list[Flag]:
    """
    Iterate repeated application of a word until the start repeats.

    Returns the cyclic orbit beginning at `flag`.
    """
    if not word:
        raise ValueError("word must be non-empty")

    seen: dict[Flag, int] = {}
    seq: list[Flag] = []

    current = flag
    for _ in range(max_steps):
        if current in seen:
            start = seen[current]
            return seq[start:]
        seen[current] = len(seq)
        seq.append(current)
        current = apply_word(current, word)

    raise RuntimeError("orbit exceeded max_steps; possible non-closing word")


def orbit_length(flag: Flag, word: str) -> int:
    return len(orbit(flag, word))


def cycle_partition(word: str) -> list[list[Flag]]:
    """
    Partition all 120 flags into cycles under repeated application of `word`.
    """
    remaining = set(all_flags())
    cycles: list[list[Flag]] = []

    while remaining:
        seed = next(iter(remaining))
        cyc = orbit(seed, word)
        cycles.append(cyc)
        for item in cyc:
            remaining.discard(item)

    cycles.sort(key=len)
    return cycles


def cycle_lengths(word: str) -> list[int]:
    return [len(cyc) for cyc in cycle_partition(word)]


def summary(word: str) -> list[str]:
    lengths = cycle_lengths(word)
    return [
        f"word: {word}",
        f"flags: {FLAG_COUNT}",
        f"cycles: {len(lengths)}",
        f"cycle lengths: {lengths}",
    ]


def validate_face_tables() -> None:
    for face in range(FACE_COUNT):
        if face not in FACE_NEIGHBORS:
            raise ValueError(f"missing FACE_NEIGHBORS entry for face {face}")
        row = FACE_NEIGHBORS[face]
        if len(row) != FACE_SIZE:
            raise ValueError(f"face {face} must have {FACE_SIZE} neighbor entries")

        for slot in range(FACE_SIZE):
            nbr = row[slot]
            if not (0 <= nbr < FACE_COUNT):
                raise ValueError(f"invalid neighbor {nbr} at face {face} slot {slot}")

            dst_slot = FACE_SLOT_MAP[(face, slot)]
            if not (0 <= dst_slot < FACE_SIZE):
                raise ValueError(
                    f"invalid destination slot {dst_slot} at face {face} slot {slot}"
                )


validate_face_tables()

