from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from .incidences import DodecahedronIncidence

VertexId = int
EdgeId = int
FaceId = int


@dataclass(frozen=True)
class Flag:
    vertex: VertexId
    edge: EdgeId
    face: FaceId


class FlagModel:
    """
    Constructs the 120 local flags of a dodecahedron.

    Count:
        12 faces × 5 edges-per-face × 2 endpoints = 120 flags
    """

    def __init__(self):
        self.inc = DodecahedronIncidence()

        self.edges: List[Tuple[VertexId, VertexId]] = []
        self.edge_lookup: Dict[Tuple[int, int], int] = {}

        self.flags: List[Flag] = []
        self.flag_index: Dict[Flag, int] = {}

        self._build_edges()
        self._build_flags()

    def _build_edges(self) -> None:
        edge_set = set()

        for verts in self.inc.faces.values():
            for i in range(5):
                a = verts[i]
                b = verts[(i + 1) % 5]
                edge_set.add(tuple(sorted((a, b))))

        self.edges = sorted(edge_set)

        for i, e in enumerate(self.edges):
            self.edge_lookup[e] = i

        assert len(self.edges) == 30

    def _build_flags(self) -> None:
        idx = 0

        for face, verts in self.inc.faces.items():
            for i in range(5):
                v0 = verts[i]
                v1 = verts[(i + 1) % 5]

                edge = tuple(sorted((v0, v1)))
                edge_id = self.edge_lookup[edge]

                for v in edge:
                    flag = Flag(vertex=v, edge=edge_id, face=face)
                    self.flags.append(flag)
                    self.flag_index[flag] = idx
                    idx += 1

        assert len(self.flags) == 120

    def num_flags(self) -> int:
        return len(self.flags)

    def index(self, flag: Flag) -> int:
        return self.flag_index[flag]

    def get(self, i: int) -> Flag:
        return self.flags[i]


if __name__ == "__main__":
    fm = FlagModel()
    print("Flags:", fm.num_flags())
    print("Edges:", len(fm.edges))
    print("First 10 flags:")
    for i in range(10):
        print(i, fm.get(i))
