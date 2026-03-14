from __future__ import annotations

import tkinter as tk
from pathlib import Path
from PIL import ImageTk

from hyperxi.viewer.cubic_mode import load_cubic_mode_payload
from hyperxi.viewer.cubic_mode_pil import render_cubic_resonance_image

PAYLOAD_PATH = Path("reports/spectral/nodal/thalion_cubic_viewer_payload.json")


class CubicModeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HyperXi Cubic Mode")

        self.payload = load_cubic_mode_payload(PAYLOAD_PATH)
        self.phase_index = 0
        self.display_mode = "faces+slots"

        self.label = tk.Label(root)
        self.label.pack(padx=12, pady=12)

        controls = tk.Frame(root)
        controls.pack(pady=(0, 12))

        tk.Button(controls, text="Prev", command=self.prev_frame).pack(side=tk.LEFT, padx=4)
        tk.Button(controls, text="Next", command=self.next_frame).pack(side=tk.LEFT, padx=4)
        tk.Button(controls, text="Toggle Mode", command=self.toggle_mode).pack(side=tk.LEFT, padx=4)

        self.status = tk.Label(root, text="")
        self.status.pack(pady=(0, 12))

        self.refresh()

    def refresh(self) -> None:
        img = render_cubic_resonance_image(
            self.payload,
            self.phase_index,
            display_mode=self.display_mode,
            width=900,
            height=700,
        )
        self.photo = ImageTk.PhotoImage(img)
        self.label.configure(image=self.photo)
        self.status.configure(
            text=f"phase {self.phase_index + 1}/{self.payload.steps}   mode={self.display_mode}   eigenvalue={self.payload.eigenvalue}"
        )

    def next_frame(self) -> None:
        self.phase_index = (self.phase_index + 1) % self.payload.steps
        self.refresh()

    def prev_frame(self) -> None:
        self.phase_index = (self.phase_index - 1) % self.payload.steps
        self.refresh()

    def toggle_mode(self) -> None:
        if self.display_mode == "faces+slots":
            self.display_mode = "faces"
        elif self.display_mode == "faces":
            self.display_mode = "classes"
        else:
            self.display_mode = "faces+slots"
        self.refresh()


def main() -> None:
    root = tk.Tk()
    app = CubicModeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
