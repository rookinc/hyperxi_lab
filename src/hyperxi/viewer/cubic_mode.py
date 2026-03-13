from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CubicModePayload:
    raw: dict[str, Any]

    @property
    def eigenvalue(self) -> float:
        return float(self.raw["eigenvalue"])

    @property
    def steps(self) -> int:
        return int(self.raw["steps"])

    @property
    def frames(self) -> list[dict[str, Any]]:
        return list(self.raw["frames"])

    @property
    def face_class_groups(self) -> dict[str, list[int]]:
        return {k: list(v) for k, v in self.raw["face_class_groups"].items()}

    @property
    def face_slot_nodes(self) -> dict[str, list[int]]:
        return {k: list(v) for k, v in self.raw["face_slot_nodes"].items()}

    def frame(self, phase_index: int) -> dict[str, Any]:
        return self.frames[phase_index % self.steps]


def load_cubic_mode_payload(path: str | Path) -> CubicModePayload:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return CubicModePayload(raw=raw)
