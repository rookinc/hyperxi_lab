from __future__ import annotations

from pathlib import Path

from hyperxi.viewer.cubic_mode import load_cubic_mode_payload
from hyperxi.viewer.cubic_mode_pil import render_cubic_resonance_image

ROOT = Path(__file__).resolve().parents[3]

PAYLOAD_PATH = (
    ROOT / "reports" / "spectral" / "nodal" / "thalion_cubic_viewer_payload.json"
)

OUT_PNG = (
    ROOT / "reports" / "spectral" / "nodal" / "thalion_cubic_resonance_phase03.png"
)


def main() -> None:
    payload = load_cubic_mode_payload(PAYLOAD_PATH)
    img = render_cubic_resonance_image(
        payload=payload,
        phase_index=3,
        display_mode="faces+slots",
        width=1200,
        height=900,
    )
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT_PNG)
    print(f"saved: {OUT_PNG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
