#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FACE_PATH = ROOT / "reports" / "spectral" / "nodal" / "thalion_cubic_face_animation.json"
SLOT_PATH = ROOT / "reports" / "spectral" / "nodal" / "thalion_cubic_slot_animation.json"
OUT_PATH = ROOT / "reports" / "spectral" / "nodal" / "thalion_cubic_viewer_payload.json"


def main():
    with open(FACE_PATH, "r", encoding="utf-8") as f:
        face_data = json.load(f)

    with open(SLOT_PATH, "r", encoding="utf-8") as f:
        slot_data = json.load(f)

    if face_data["steps"] != slot_data["steps"]:
        raise RuntimeError(
            f"Step mismatch: face={face_data['steps']} slot={slot_data['steps']}"
        )

    face_frames = {frame["phase_index"]: frame for frame in face_data["frames"]}
    slot_frames = {frame["phase_index"]: frame for frame in slot_data["frames"]}

    steps = face_data["steps"]
    frames = []

    for k in range(steps):
        if k not in face_frames or k not in slot_frames:
            raise RuntimeError(f"Missing phase {k} in one of the inputs")

        ff = face_frames[k]
        sf = slot_frames[k]

        frames.append({
            "phase_index": k,
            "theta": ff["theta"],
            "face_avg": ff["face_avg"],
            "class_avg": ff["class_avg"],
            "face_slot_values": sf["face_slot_values"],
        })

    payload = {
        "name": "thalion_cubic_viewer_payload",
        "object": "single_thalion_internal_60_vertex_graph",
        "eigenvalue": face_data["eigenvalue"],
        "steps": steps,
        "face_class_groups": face_data["face_class_groups"],
        "face_slot_nodes": slot_data["face_slot_nodes"],
        "color_hint": {
            "negative": "blue",
            "zero": "white",
            "positive": "red",
            "intensity": "abs(value)",
        },
        "frames": frames,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"saved: {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
