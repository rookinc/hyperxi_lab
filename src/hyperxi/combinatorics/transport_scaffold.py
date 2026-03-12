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
    Vertex-rotation style move.

    Temporary scaffold rule:
    - toggles orientation
    - advances to a neighboring face chart in a deterministic way
    """
    next_face = (flag.face + flag.slot + 1) % FACE_COUNT
    return Flag(next_face, flag.slot, 1 - flag.orient)


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
