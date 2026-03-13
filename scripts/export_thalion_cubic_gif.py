#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import tkinter as tk
from PIL import Image, ImageGrab

from hyperxi.viewer.cubic_mode import load_cubic_mode_payload
from hyperxi.viewer.icosahedral_view import draw_cubic_resonance

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_PATH = ROOT / "reports" / "spectral" / "nodal" / "thalion_cubic_viewer_payload.json"
OUT_GIF = ROOT / "reports" / "spectral" / "nodal" / "thalion_cubic_resonance.gif"


def capture_canvas(canvas: tk.Canvas) -> Image.Image:
    canvas.update_idletasks()
    x = canvas.winfo_rootx()
    y = canvas.winfo_rooty()
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    return ImageGrab.grab(bbox=(x, y, x + w, y + h))


def main() -> None:
    payload = load_cubic_mode_payload(PAYLOAD_PATH)

    root = tk.Tk()
    root.withdraw()

    win = tk.Toplevel(root)
    win.title("thalion_cubic_gif_export")
    win.geometry("900x700")

    canvas = tk.Canvas(win, bg="white", width=900, height=700, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    win.update()
    frames: list[Image.Image] = []

    for phase in range(payload.steps):
        canvas.delete("all")
        draw_cubic_resonance(
            canvas,
            payload=payload,
            phase_index=phase,
            display_mode="faces+slots",
        )
        win.update()
        img = capture_canvas(canvas).convert("P", palette=Image.ADAPTIVE)
        frames.append(img)

    if not frames:
        raise RuntimeError("No frames captured.")

    OUT_GIF.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUT_GIF,
        save_all=True,
        append_images=frames[1:],
        duration=180,
        loop=0,
        optimize=False,
    )

    print(f"saved: {OUT_GIF.relative_to(ROOT)}")

    win.destroy()
    root.destroy()


if __name__ == "__main__":
    main()
