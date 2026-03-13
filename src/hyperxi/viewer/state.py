from __future__ import annotations

from pathlib import Path

from hyperxi.combinatorics.transport_scaffold import (
    FACE_COUNT,
    FACE_SIZE,
    FLAG_COUNT,
)

from .cubic_mode import CubicModePayload, load_cubic_mode_payload


class HyperXiState:
    """
    Minimal lab state describing the core HyperXi system.
    """

    def __init__(self) -> None:
        self.cell_name = "dodecahedron"
        self.face_count = FACE_COUNT
        self.face_size = FACE_SIZE
        self.flags = FLAG_COUNT
        self.thalions = 60
        self.chamber_degree = 4
        self.default_word = "FSF"
        self.petrie_word = "SV"
        self.thalion_word = "FSF"

        self.cubic_mode_enabled = False
        self.cubic_display_mode = "faces"   # faces | classes | faces+slots
        self.cubic_phase_index = 0
        self.cubic_payload_path = str(
            Path(__file__).resolve().parents[3]
            / "reports"
            / "spectral"
            / "nodal"
            / "thalion_cubic_viewer_payload.json"
        )
        self.cubic_payload: CubicModePayload | None = None

    def load_cubic_payload(self) -> None:
        path = Path(self.cubic_payload_path)
        if path.exists():
            self.cubic_payload = load_cubic_mode_payload(path)
        else:
            self.cubic_payload = None

    def summary(self) -> list[str]:
        lines = [
            f"cell: {self.cell_name}",
            f"faces: {self.face_count}",
            f"face size: {self.face_size}",
            f"flags: {self.flags}",
            f"thalions: {self.thalions}",
            f"chamber graph degree: {self.chamber_degree}",
            f"default word: {self.default_word}",
            f"petrie word: {self.petrie_word}",
            f"thalion word: {self.thalion_word}",
        ]
        if self.cubic_payload is not None:
            lines.append(f"cubic resonance payload: loaded (steps={self.cubic_payload.steps})")
        else:
            lines.append("cubic resonance payload: not loaded")
        return lines
