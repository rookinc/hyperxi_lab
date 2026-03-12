from __future__ import annotations

from dataclasses import dataclass

from .thalions import Thalion, build_thalions
from .transport_scaffold import F, V, Flag


@dataclass(frozen=True)
class ChamberGraph:
    vertices: tuple[int, ...]
    edges: tuple[tuple[int, int], ...]

    def vertex_count(self) -> int:
        return len(self.vertices)

    def edge_count(self) -> int:
        return len(self.edges)

    def degree_map(self) -> dict[int, int]:
        deg = {v: 0 for v in self.vertices}
        for a, b in self.edges:
            deg[a] += 1
            deg[b] += 1
        return deg

    def degree_set(self) -> list[int]:
        return sorted(set(self.degree_map().values()))


def _flag_to_thalion_map(thalions: list[Thalion]) -> dict[Flag, int]:
    out: dict[Flag, int] = {}
    for th in thalions:
        for member in th.members:
            out[member] = th.id
    return out


def build_chamber_graph() -> ChamberGraph:
    thalions = build_thalions()
    owner = _flag_to_thalion_map(thalions)

    edge_set: set[tuple[int, int]] = set()

    for th in thalions:
        src = th.id
        for flag in th.members:
            for move in (F, V):
                image = move(flag)
                dst = owner[image]
                if dst == src:
                    continue
                a, b = sorted((src, dst))
                edge_set.add((a, b))

    vertices = tuple(th.id for th in thalions)
    edges = tuple(sorted(edge_set))
    return ChamberGraph(vertices=vertices, edges=edges)


def summary() -> list[str]:
    g = build_chamber_graph()
    return [
        f"vertices: {g.vertex_count()}",
        f"edges: {g.edge_count()}",
        f"degree set: {g.degree_set()}",
    ]
