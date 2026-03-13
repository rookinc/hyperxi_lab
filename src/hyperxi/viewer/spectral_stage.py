from __future__ import annotations

import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import networkx as nx
import numpy as np


# Allow importing from project-root scripts/ when launched from package code
ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from vertex_connection_model import measured_graph_reindexed  # type: ignore


def build_nx_graph() -> nx.Graph:
    adj = measured_graph_reindexed()
    g = nx.Graph()
    for u, nbrs in adj.items():
        g.add_node(u)
        for v in nbrs:
            if u < v:
                g.add_edge(u, v)
    return g


def adjacency_matrix(g: nx.Graph) -> tuple[np.ndarray, list[int]]:
    nodes = sorted(g.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    a = np.zeros((len(nodes), len(nodes)), dtype=float)
    for u, v in g.edges():
        i = idx[u]
        j = idx[v]
        a[i, j] = 1.0
        a[j, i] = 1.0
    return a, nodes


def spectral_embedding_3d(g: nx.Graph) -> tuple[dict[int, np.ndarray], np.ndarray]:
    a, nodes = adjacency_matrix(g)
    vals, vecs = np.linalg.eigh(a)
    order = np.argsort(vals)[::-1]
    vals = vals[order]
    vecs = vecs[:, order]

    # Skip principal eigenvector, use next three coordinates
    x = vecs[:, 1:4].copy()
    norms = np.linalg.norm(x, axis=1)
    max_norm = float(np.max(norms))
    if max_norm > 0:
        x /= max_norm

    pos3 = {nodes[i]: x[i] for i in range(len(nodes))}
    return pos3, vals


class SpectralStage(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("HyperXi Spectral Stage")
        self.geometry("1200x860")
        self.minsize(980, 720)

        self.graph = build_nx_graph()
        self.pos3, self.evals = spectral_embedding_3d(self.graph)
        self.nodes = sorted(self.graph.nodes())

        self.lower_nodes = [v for v in self.nodes if self.pos3[v][2] < 0]
        self.upper_nodes = [v for v in self.nodes if self.pos3[v][2] >= 0]

        self.edge_alpha = tk.DoubleVar(value=0.55)
        self.edge_width = tk.DoubleVar(value=0.9)
        self.node_size = tk.DoubleVar(value=42.0)
        self.elev = tk.DoubleVar(value=22.0)
        self.azim = tk.DoubleVar(value=38.0)
        self.show_axes = tk.BooleanVar(value=True)
        self.two_tone = tk.BooleanVar(value=True)

        self._build_ui()
        self.redraw()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self, padding=8)
        outer.pack(fill="both", expand=True)

        controls = ttk.Frame(outer)
        controls.pack(side="left", fill="y", padx=(0, 10))

        stage = ttk.Frame(outer)
        stage.pack(side="right", fill="both", expand=True)

        ttk.Label(controls, text="3D Stage", font=("TkDefaultFont", 14, "bold")).pack(
            anchor="w", pady=(0, 8)
        )

        info = (
            f"Vertices: {self.graph.number_of_nodes()}\n"
            f"Edges: {self.graph.number_of_edges()}\n"
            f"Degree set: {sorted(set(dict(self.graph.degree()).values()))}\n"
            f"Top eigenvalues:\n"
            + "\n".join(f"  {x:.6f}" for x in self.evals[:6])
        )
        ttk.Label(controls, text=info, justify="left").pack(anchor="w", pady=(0, 14))

        self._add_slider(controls, "Elevation", self.elev, 0.0, 90.0)
        self._add_slider(controls, "Azimuth", self.azim, 0.0, 360.0)
        self._add_slider(controls, "Edge alpha", self.edge_alpha, 0.05, 1.0)
        self._add_slider(controls, "Edge width", self.edge_width, 0.2, 2.5)
        self._add_slider(controls, "Node size", self.node_size, 10.0, 100.0)

        ttk.Checkbutton(
            controls,
            text="Show guide axes",
            variable=self.show_axes,
            command=self.redraw,
        ).pack(anchor="w", pady=(8, 2))

        ttk.Checkbutton(
            controls,
            text="Two-tone z split",
            variable=self.two_tone,
            command=self.redraw,
        ).pack(anchor="w", pady=(2, 10))

        ttk.Button(controls, text="Reset view", command=self.reset_view).pack(
            fill="x", pady=(8, 4)
        )
        ttk.Button(controls, text="Screen grab PNG", command=self.save_png).pack(
            fill="x", pady=4
        )
        ttk.Button(controls, text="Quit", command=self.destroy).pack(fill="x", pady=4)

        self.fig = plt.Figure(figsize=(8.6, 8.0), dpi=100)
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.canvas = FigureCanvasTkAgg(self.fig, master=stage)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _add_slider(
        self,
        parent: ttk.Frame,
        label: str,
        var: tk.DoubleVar,
        minval: float,
        maxval: float,
    ) -> None:
        ttk.Label(parent, text=label).pack(anchor="w")
        scale = ttk.Scale(
            parent,
            from_=minval,
            to=maxval,
            variable=var,
            orient="horizontal",
            command=lambda _evt=None: self.redraw(),
        )
        scale.pack(fill="x", pady=(0, 8))

    def reset_view(self) -> None:
        self.elev.set(22.0)
        self.azim.set(38.0)
        self.edge_alpha.set(0.55)
        self.edge_width.set(0.9)
        self.node_size.set(42.0)
        self.show_axes.set(True)
        self.two_tone.set(True)
        self.redraw()

    def redraw(self) -> None:
        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.view_init(elev=self.elev.get(), azim=self.azim.get())

        edge_alpha = float(self.edge_alpha.get())
        edge_width = float(self.edge_width.get())
        node_size = float(self.node_size.get())

        for u, v in self.graph.edges():
            x1, y1, z1 = self.pos3[u]
            x2, y2, z2 = self.pos3[v]
            self.ax.plot(
                [x1, x2],
                [y1, y2],
                [z1, z2],
                linewidth=edge_width,
                alpha=edge_alpha,
                color="0.30",
                zorder=1,
            )

        if self.two_tone.get():
            xs0 = [self.pos3[v][0] for v in self.lower_nodes]
            ys0 = [self.pos3[v][1] for v in self.lower_nodes]
            zs0 = [self.pos3[v][2] for v in self.lower_nodes]

            xs1 = [self.pos3[v][0] for v in self.upper_nodes]
            ys1 = [self.pos3[v][1] for v in self.upper_nodes]
            zs1 = [self.pos3[v][2] for v in self.upper_nodes]

            self.ax.scatter(
                xs0, ys0, zs0,
                s=node_size,
                edgecolors="black",
                facecolors="0.80",
                linewidths=0.8,
                depthshade=False,
            )
            self.ax.scatter(
                xs1, ys1, zs1,
                s=node_size,
                edgecolors="black",
                facecolors="white",
                linewidths=0.9,
                depthshade=False,
            )
        else:
            xs = [self.pos3[v][0] for v in self.nodes]
            ys = [self.pos3[v][1] for v in self.nodes]
            zs = [self.pos3[v][2] for v in self.nodes]
            self.ax.scatter(
                xs, ys, zs,
                s=node_size,
                edgecolors="black",
                facecolors="white",
                linewidths=0.9,
                depthshade=False,
            )

        if self.show_axes.get():
            self.ax.plot([-1.15, 1.15], [0.0, 0.0], [0.0, 0.0], linewidth=0.6, alpha=0.20, color="0.4")
            self.ax.plot([0.0, 0.0], [-1.15, 1.15], [0.0, 0.0], linewidth=0.6, alpha=0.20, color="0.4")
            self.ax.plot([0.0, 0.0], [0.0, 0.0], [-1.15, 1.15], linewidth=0.6, alpha=0.20, color="0.4")

        limit = 1.08
        self.ax.set_xlim(-limit, limit)
        self.ax.set_ylim(-limit, limit)
        self.ax.set_zlim(-limit, limit)

        self.canvas.draw_idle()

    def save_png(self) -> None:
        default_dir = ROOT / "paper" / "thalean-paper" / "figures" / "generated"
        default_dir.mkdir(parents=True, exist_ok=True)
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Save spectral stage screenshot",
            initialdir=str(default_dir),
            initialfile="thalean_graph_stage_capture.png",
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
        )
        if not path:
            return

        try:
            self.fig.savefig(path, bbox_inches="tight", dpi=260)
        except Exception as exc:
            messagebox.showerror("Save failed", str(exc), parent=self)
            return

        messagebox.showinfo("Saved", f"Saved screenshot to:\n{path}", parent=self)


def main() -> None:
    app = SpectralStage()
    app.mainloop()


if __name__ == "__main__":
    main()
