from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass, field
from typing import Optional

import networkx as nx

from hyperxi.combinatorics.chamber_graph import build_chamber_graph
from hyperxi.viewer.graph_view import draw_chamber_graph

@dataclass
class ChamberWaveSim:
    G: nx.Graph
    prev: dict[int, float] = field(default_factory=dict)
    curr: dict[int, float] = field(default_factory=dict)
    damping: float = 0.002
    coupling: float = 1.0
    pinned: set[int] = field(default_factory=set)

    def reset(self) -> None:
        self.prev = {v: 0.0 for v in self.G.nodes}
        self.curr = {v: 0.0 for v in self.G.nodes}

    def inject_impulse(self, node: int, amplitude: float = 1.0, clear: bool = False) -> None:
        if clear:
            self.reset()
        if node not in self.G:
            return
        self.curr[node] += amplitude

    def inject_checkerboard(self, amplitude: float = 1.0) -> None:
        self.reset()
        for v in self.G.nodes:
            self.curr[v] = amplitude if (v % 2 == 0) else -amplitude

    def inject_shell_split(self) -> None:
        self.reset()
        for v in self.G.nodes:
            self.curr[v] = 1.0 if v < 30 else -1.0

    def total_energy(self) -> float:
        kinetic = 0.0
        for v in self.G.nodes:
            vel = self.curr[v] - self.prev[v]
            kinetic += vel * vel

        potential = 0.0
        for a, b in self.G.edges:
            diff = self.curr[a] - self.curr[b]
            potential += diff * diff

        return kinetic + 0.5 * self.coupling * potential

    def step(self) -> None:
        nxt: dict[int, float] = {}

        for v in self.G.nodes:
            if v in self.pinned:
                nxt[v] = 0.0
                continue

            deg = self.G.degree[v]
            if deg == 0:
                nxt[v] = self.curr[v]
                continue

            lap = sum(self.curr[u] for u in self.G.neighbors(v)) - deg * self.curr[v]

            nxt[v] = (
                2.0 * self.curr[v]
                - self.prev[v]
                + self.coupling * lap / deg
            )
            nxt[v] *= (1.0 - self.damping)

        for v in self.pinned:
            nxt[v] = 0.0

        self.prev, self.curr = self.curr, nxt


class ChamberWaveLab(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("HyperXi Chamber Wave Lab")
        self.geometry("1200x900")
        self.configure(bg="#dddddd")

        base = build_chamber_graph()
        G = nx.Graph()
        G.add_nodes_from(base.vertices)
        G.add_edges_from(base.edges)

        self.sim = ChamberWaveSim(G)
        self.sim.reset()

        self.color_mode = tk.StringVar(value="side")
        self.layout_mode = tk.StringVar(value="spring")
        self.running = False
        self.after_id: Optional[str] = None
        self.step_ms = 30
        self.face7_twist = tk.DoubleVar(value=0.6283185307179586)

        self.node_pick = tk.IntVar(value=0)
        self.impulse_amp = tk.DoubleVar(value=1.0)
        self.damping = tk.DoubleVar(value=self.sim.damping)
        self.coupling = tk.DoubleVar(value=self.sim.coupling)
        self.show_wave = tk.BooleanVar(value=True)
        self.normalize_view = tk.BooleanVar(value=True)
        self.overlay_shell_colors = tk.BooleanVar(value=True)

        self._build_ui()
        self._bind_events()
        self._redraw()

    def _build_ui(self) -> None:
        outer = tk.Frame(self, bg="#dddddd")
        outer.pack(fill="both", expand=True)

        controls = tk.Frame(outer, bg="#eeeeee", width=300)
        controls.pack(side="left", fill="y")

        self.canvas = tk.Canvas(
            outer,
            bg="#dcdcdc",
            highlightthickness=0,
        )
        self.canvas.pack(side="right", fill="both", expand=True)

        row = 0

        def add_label(text: str) -> None:
            nonlocal row
            tk.Label(
                controls,
                text=text,
                bg="#eeeeee",
                anchor="w",
                font=("Helvetica", 11, "bold"),
            ).grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 4))
            row += 1

        def add_button(text: str, cmd) -> None:
            nonlocal row
            tk.Button(controls, text=text, command=cmd).grid(
                row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=4
            )
            row += 1

        def add_scale(label: str, var, frm: float, to: float, res: float, cmd=None) -> None:
            nonlocal row
            tk.Label(controls, text=label, bg="#eeeeee", anchor="w").grid(
                row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=(8, 0)
            )
            row += 1
            tk.Scale(
                controls,
                variable=var,
                from_=frm,
                to=to,
                resolution=res,
                orient="horizontal",
                bg="#eeeeee",
                highlightthickness=0,
                command=cmd,
            ).grid(row=row, column=0, columnspan=2, sticky="ew", padx=10)
            row += 1

        add_label("Simulation")

        add_button("Play / Pause", self.toggle_running)
        add_button("Single Step", self.step_once)
        add_button("Reset State", self.reset_state)

        add_scale("Damping", self.damping, 0.0, 0.05, 0.001, self._update_params)
        add_scale("Coupling", self.coupling, 0.1, 2.0, 0.01, self._update_params)
        add_scale("Face 7 Twist", self.face7_twist, 0.0, 6.28318, 0.01, self._redraw_from_scale)

        add_label("Injection")

        tk.Label(controls, text="Node", bg="#eeeeee", anchor="w").grid(
            row=row, column=0, sticky="ew", padx=10, pady=(8, 0)
        )
        tk.Entry(controls, textvariable=self.node_pick).grid(
            row=row, column=1, sticky="ew", padx=10, pady=(8, 0)
        )
        row += 1

        tk.Label(controls, text="Amplitude", bg="#eeeeee", anchor="w").grid(
            row=row, column=0, sticky="ew", padx=10, pady=(8, 0)
        )
        tk.Entry(controls, textvariable=self.impulse_amp).grid(
            row=row, column=1, sticky="ew", padx=10, pady=(8, 0)
        )
        row += 1

        add_button("Inject Impulse", self.inject_selected)
        add_button("Shell Split (+/-)", self.inject_shell_split)
        add_button("Checkerboard", self.inject_checkerboard)

        add_label("Display")

        tk.Checkbutton(
            controls,
            text="Show wave overlay",
            variable=self.show_wave,
            bg="#eeeeee",
            command=self._redraw,
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=4)
        row += 1

        tk.Checkbutton(
            controls,
            text="Normalize overlay",
            variable=self.normalize_view,
            bg="#eeeeee",
            command=self._redraw,
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=4)
        row += 1

        tk.Checkbutton(
            controls,
            text="Keep shell colors",
            variable=self.overlay_shell_colors,
            bg="#eeeeee",
            command=self._redraw,
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=10, pady=4)
        row += 1

        tk.Label(controls, text="Color mode", bg="#eeeeee", anchor="w").grid(
            row=row, column=0, sticky="ew", padx=10, pady=(8, 0)
        )
        tk.OptionMenu(controls, self.color_mode, "side", "petrie", command=lambda _: self._redraw()).grid(
            row=row, column=1, sticky="ew", padx=10, pady=(8, 0)
        )
        row += 1

        tk.Label(controls, text="Layout", bg="#eeeeee", anchor="w").grid(
            row=row, column=0, sticky="ew", padx=10, pady=(8, 0)
        )
        tk.OptionMenu(controls, self.layout_mode, "polar", "spring", command=lambda _: self._redraw()).grid(
            row=row, column=1, sticky="ew", padx=10, pady=(8, 0)
        )
        row += 1

        add_label("Readout")

        self.energy_label = tk.Label(
            controls,
            text="Energy: 0.000000",
            bg="#eeeeee",
            anchor="w",
            justify="left",
        )
        self.energy_label.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=4)
        row += 1

        self.max_amp_label = tk.Label(
            controls,
            text="Max |amp|: 0.000000",
            bg="#eeeeee",
            anchor="w",
            justify="left",
        )
        self.max_amp_label.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=4)
        row += 1

        self.help_label = tk.Label(
            controls,
            text="Click a node to inject.\nSpace = play/pause\nS = single step\nR = reset",
            bg="#eeeeee",
            anchor="w",
            justify="left",
        )
        self.help_label.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=(12, 8))
        row += 1

        controls.grid_columnconfigure(0, weight=1)
        controls.grid_columnconfigure(1, weight=1)

    def _bind_events(self) -> None:
        self.canvas.bind("<Configure>", lambda event: self._redraw())
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.bind("<space>", lambda event: self.toggle_running())
        self.bind("s", lambda event: self.step_once())
        self.bind("r", lambda event: self.reset_state())

    def _update_params(self, _value: str | None = None) -> None:
        self.sim.damping = float(self.damping.get())
        self.sim.coupling = float(self.coupling.get())

    def _redraw_from_scale(self, _value: str | None = None) -> None:
        self._redraw()

    def reset_state(self) -> None:
        self.sim.reset()
        self._redraw()

    def inject_selected(self) -> None:
        self.sim.inject_impulse(
            node=int(self.node_pick.get()),
            amplitude=float(self.impulse_amp.get()),
            clear=False,
        )
        self._redraw()

    def inject_shell_split(self) -> None:
        self.sim.inject_shell_split()
        self._redraw()

    def inject_checkerboard(self) -> None:
        self.sim.inject_checkerboard()
        self._redraw()

    def toggle_running(self) -> None:
        self.running = not self.running
        if self.running:
            self._tick()
        elif self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None

    def step_once(self) -> None:
        self._update_params()
        self.sim.step()
        self._redraw()

    def _tick(self) -> None:
        self._update_params()
        self.sim.step()
        self._redraw()
        if self.running:
            self.after_id = self.after(self.step_ms, self._tick)

    def _wave_fill(self, node: int) -> str:
        value = self.sim.curr.get(node, 0.0)
        amps = [abs(v) for v in self.sim.curr.values()]
        max_amp = max(max(amps, default=0.0), 1e-9)

        scale = max_amp if self.normalize_view.get() else 2.0
        x = max(-1.0, min(1.0, value / scale))

        if self.overlay_shell_colors.get():
            if node < 30:
                # blue family
                level = int(150 + 105 * abs(x))
                if x >= 0:
                    return f"#{60:02x}{110:02x}{level:02x}"
                return f"#{20:02x}{70:02x}{max(40, level - 50):02x}"
            else:
                # red family
                level = int(150 + 105 * abs(x))
                if x >= 0:
                    return f"#{level:02x}{90:02x}{90:02x}"
                return f"#{max(60, level - 60):02x}{40:02x}{40:02x}"

        if x >= 0:
            g = int(180 + 75 * x)
            return f"#{255:02x}{g:02x}{g:02x}"
        b = int(180 + 75 * (-x))
        return f"#{g if False else 180:02x}{180:02x}{b:02x}"

    def _wave_radius(self, node: int) -> float:
        value = abs(self.sim.curr.get(node, 0.0))
        amps = [abs(v) for v in self.sim.curr.values()]
        max_amp = max(max(amps, default=0.0), 1e-9)

        scale = max_amp if self.normalize_view.get() else 2.0
        t = min(value / scale, 1.0)
        return 5.0 + 12.0 * t

    def _draw_wave_overlay(self) -> None:
        width = max(int(self.canvas.winfo_width()), 1)
        height = max(int(self.canvas.winfo_height()), 1)

        draw_chamber_graph(
            self.canvas,
            color_mode=self.color_mode.get(),
            layout_mode=self.layout_mode.get(),
            face7_twist=float(self.face7_twist.get()),
        )

        coords = getattr(self.canvas, "_hyperxi_node_coords", None)
        if not isinstance(coords, dict):
            return

        for node, (x, y) in coords.items():
            r = self._wave_radius(node)
            fill = self._wave_fill(node)
            self.canvas.create_oval(
                x - r,
                y - r,
                x + r,
                y + r,
                fill=fill,
                outline="black",
                width=1,
            )

        highlight = int(self.node_pick.get())
        if highlight in coords:
            x, y = coords[highlight]
            self.canvas.create_oval(
                x - 16,
                y - 16,
                x + 16,
                y + 16,
                outline="#222222",
                width=2,
            )

    def _nearest_node(self, x: float, y: float) -> Optional[int]:
        coords = getattr(self.canvas, "_hyperxi_node_coords", None)
        if not isinstance(coords, dict):
            return None

        best_node: Optional[int] = None
        best_d2 = float("inf")

        for node, (nx_, ny_) in coords.items():
            d2 = (x - nx_) ** 2 + (y - ny_) ** 2
            if d2 < best_d2:
                best_d2 = d2
                best_node = node

        if best_d2 <= 30.0 ** 2:
            return best_node
        return None

    def _on_canvas_click(self, event) -> None:
        node = self._nearest_node(event.x, event.y)
        if node is None:
            return
        self.node_pick.set(node)
        self.sim.inject_impulse(node=node, amplitude=float(self.impulse_amp.get()), clear=False)
        self._redraw()

    def _redraw(self) -> None:
        self.canvas.delete("all")

        if self.show_wave.get():
            self._draw_wave_overlay()
        else:
            draw_chamber_graph(
                self.canvas,
                color_mode=self.color_mode.get(),
                layout_mode=self.layout_mode.get(),
                face7_twist=float(self.face7_twist.get()),
            )

        max_amp = max((abs(v) for v in self.sim.curr.values()), default=0.0)
        self.energy_label.config(text=f"Energy: {self.sim.total_energy():.6f}")
        self.max_amp_label.config(text=f"Max |amp|: {max_amp:.6f}")


def main() -> None:
    app = ChamberWaveLab()
    app.mainloop()


if __name__ == "__main__":
    main()
