from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUTDIR = ROOT / "paper" / "thalean-paper" / "figures" / "generated"

SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from vertex_connection_model import BASE_ADJ, base_edges, measured_graph_reindexed, pair_to_edge_sheet


PHI = (1.0 + np.sqrt(5.0)) / 2.0

ICOSA_VERTICES = np.array(
    [
        [-1,  PHI, 0],
        [ 1,  PHI, 0],
        [-1, -PHI, 0],
        [ 1, -PHI, 0],
        [0, -1,  PHI],
        [0,  1,  PHI],
        [0, -1, -PHI],
        [0,  1, -PHI],
        [ PHI, 0, -1],
        [ PHI, 0,  1],
        [-PHI, 0, -1],
        [-PHI, 0,  1],
    ],
    dtype=float,
)

BASE_EDGES = base_edges()


def build_icosa_faces() -> list[list[int]]:
    nbr = {v: set(BASE_ADJ[v]) for v in BASE_ADJ}
    faces = set()
    for a in BASE_ADJ:
        for b in BASE_ADJ[a]:
            if b <= a:
                continue
            common = nbr[a] & nbr[b]
            for c in common:
                if c > b:
                    faces.add(tuple(sorted((a, b, c))))
    return [list(f) for f in sorted(faces)]


ICOSA_FACES = build_icosa_faces()


def rotation_matrix_x(theta: float) -> np.ndarray:
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=float)


def rotation_matrix_y(theta: float) -> np.ndarray:
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=float)


def rotation_matrix_z(theta: float) -> np.ndarray:
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=float)


def transform_vertices(vertices: np.ndarray, rot: np.ndarray, translate: np.ndarray) -> np.ndarray:
    return vertices @ rot.T + translate


def project_points(points3d: np.ndarray, camera: float = 10.0, scale: float = 2.2) -> np.ndarray:
    z = points3d[:, 2]
    factor = camera / (camera - z)
    x2 = scale * factor * points3d[:, 0]
    y2 = scale * factor * points3d[:, 1]
    return np.column_stack([x2, y2])


def polygon_depth(face: list[int], vertices3d: np.ndarray) -> float:
    return float(np.mean(vertices3d[np.array(face), 2]))


def draw_icosa_shell(ax, vertices3d: np.ndarray, face_alpha: float = 0.10) -> np.ndarray:
    pts2 = project_points(vertices3d)
    order = sorted(range(len(ICOSA_FACES)), key=lambda i: polygon_depth(ICOSA_FACES[i], vertices3d))

    for i in order:
        poly_xy = pts2[np.array(ICOSA_FACES[i])]
        patch = Polygon(
            poly_xy,
            closed=True,
            fill=True,
            facecolor="0.92",
            edgecolor="black",
            linewidth=0.6,
            alpha=face_alpha,
            joinstyle="round",
            zorder=1,
        )
        ax.add_patch(patch)

    for a, b in BASE_EDGES:
        xa, ya = pts2[a]
        xb, yb = pts2[b]
        ax.plot([xa, xb], [ya, yb], color="black", linewidth=0.9, alpha=0.8, zorder=2)

    return pts2


def projected_edge_midpoints(vertices3d: np.ndarray) -> dict[tuple[int, int], np.ndarray]:
    mids = {}
    for e in BASE_EDGES:
        a, b = e
        mid3 = 0.5 * (vertices3d[a] + vertices3d[b])
        mids[e] = mid3
    keys = sorted(mids)
    arr3 = np.array([mids[k] for k in keys])
    arr2 = project_points(arr3)
    return {k: arr2[i] for i, k in enumerate(keys)}


def chamber_positions():
    p2es = pair_to_edge_sheet()

    rot_left = rotation_matrix_z(-0.18) @ rotation_matrix_y(0.88) @ rotation_matrix_x(-0.20)
    rot_right = rotation_matrix_z(0.18) @ rotation_matrix_y(-0.88) @ rotation_matrix_x(-0.20)

    left_translate = np.array([-2.9, 0.0, 0.0])
    right_translate = np.array([2.9, 0.0, 0.0])

    left_vertices = transform_vertices(ICOSA_VERTICES, rot_left, left_translate)
    right_vertices = transform_vertices(ICOSA_VERTICES, rot_right, right_translate)

    left_mid2 = projected_edge_midpoints(left_vertices)
    right_mid2 = projected_edge_midpoints(right_vertices)

    pos = {}
    for node, (edge, sheet) in p2es.items():
        pos[node] = left_mid2[edge] if sheet == 0 else right_mid2[edge]

    return pos, left_vertices, right_vertices


def partition_edges(adj: dict[int, set[int]]) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    internal = []
    cross = []
    p2es = pair_to_edge_sheet()

    node_sheet = {}
    for node, (_, sheet) in p2es.items():
        node_sheet[node] = sheet

    for u in sorted(adj):
        for v in sorted(adj[u]):
            if u < v:
                if node_sheet[u] == node_sheet[v]:
                    internal.append((u, v))
                else:
                    cross.append((u, v))

    return internal, cross


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    adj = measured_graph_reindexed()
    pos, left_vertices, right_vertices = chamber_positions()
    internal_edges, cross_edges = partition_edges(adj)

    fig, ax = plt.subplots(figsize=(12.0, 6.2))
    ax.set_aspect("equal")
    ax.axis("off")

    draw_icosa_shell(ax, left_vertices, face_alpha=0.10)
    draw_icosa_shell(ax, right_vertices, face_alpha=0.10)

    # internal edges darker
    for u, v in internal_edges:
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        ax.plot([x1, x2], [y1, y2],
                color="black",
                linewidth=1.6,
                alpha=1.0,
                zorder=4)

    # cross-sheet edges very faint
    for u, v in cross_edges:
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        ax.plot([x1, x2], [y1, y2],
                color="gray",
                linewidth=0.6,
                alpha=0.25,
                zorder=3)

    xs = [pos[v][0] for v in sorted(pos)]
    ys = [pos[v][1] for v in sorted(pos)]
    ax.scatter(xs, ys, s=26, facecolors="white", edgecolors="black", linewidths=0.8, zorder=5)

    pdf_path = OUTDIR / "thalean_graph_double_icosahedron.pdf"
    png_path = OUTDIR / "thalean_graph_double_icosahedron.png"

    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, bbox_inches="tight", dpi=240)
    plt.close(fig)

    print(f"Wrote: {pdf_path}")
    print(f"Wrote: {png_path}")


if __name__ == "__main__":
    main()
