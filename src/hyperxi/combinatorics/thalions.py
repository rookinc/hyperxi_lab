from __future__ import annotations

from dataclasses import dataclass

from .transport_scaffold import Flag, cycle_partition


@dataclass(frozen=True)
class Thalion:
    """
    Prototype quotient object.

    In the scaffold model, a thalion is represented as a 2-element orbit
    under the involutive word FSF.
    """

    id: int
    members: tuple[Flag, Flag]


def build_thalions(word: str = "FSF") -> list[Thalion]:
    cycles = cycle_partition(word)

    thalions: list[Thalion] = []
    for idx, cyc in enumerate(cycles):
        if len(cyc) != 2:
            raise ValueError(
                f"prototype thalion quotient expects 2-cycles, got cycle of length {len(cyc)}"
            )

        members = tuple(sorted(cyc, key=lambda f: (f.face, f.slot, f.orient)))
        thalions.append(Thalion(id=idx, members=(members[0], members[1])))

    return thalions


def summary(word: str = "FSF") -> list[str]:
    thalions = build_thalions(word)
    sizes = sorted({len(t.members) for t in thalions})

    return [
        f"quotient word: {word}",
        f"thalions: {len(thalions)}",
        f"member sizes: {sizes}",
    ]
