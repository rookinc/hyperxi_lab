from __future__ import annotations

import sys
from pathlib import Path
from collections import defaultdict

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUTDIR = ROOT / "paper" / "thalean-paper" / "figures" / "generated"

# Allow imports from scripts/
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from vertex_connection_model import measured_graph_reindexed
from reconstruct_vertex_connection import pair_to_edge_sheet


PHI = 1.61803398875

VERTICES = np.array(
    [
        [-1.0, -1.0, -1.0],
        [-1.0, -1.0, 1.0],
        [-1.0, 1.0, -1.0],
        [-1.0, 1.0, 1.0],
        [1.0, -1.0, -1.0],
        [1.0, -1.0, 1.0],
        [1.0, 1.0, -1.0],
        [1.0, 1.0, 1.0],
        [0.0, -1.0 / PHI, -PHI],
        [0.0, -1.0 / PHI, PHI],
        [0.0, 1.0 / PHI, -PHI],
        [0.0, 1.0 / PHI, PHI],
        [-1.0 / PHI, -PHI, 0.0],
        [-1.0 / PHI, PHI, 0.0],
        [1.0 / PHI, -PHI, 0.0],
        [1.0 / PHI, PHI, 0.0],
        [-PHI, 0.0, -1.0 / PHI],
        [PHI, 0.0, -1.0 / PHI],
        [-PHI, 0.0, 1.0 / PHI],
        [PHI, 0.0, 1.0 / PHI],
    ],
    dtype=float,
)

FACES = [
    [0, 8, 4, 14, 12],
    [0, 8, 10, 2, 16],
    [0, 12, 1, 18, 16],
    [1, 9, 5, 14, 12],
    [1, 9, 11, 3, 18],
    [2, 10, 6, 15, 13],
    [2, 13, 3, 18, 16],
    [3, 11, 7, 15, 13],
    [4, 8, 10, 6, 17],
    [4, 14, 5, 19, 17],
    [5, 9, 11, 7, 19],
    [6, 15, 7, 19, 17],
]


def face_edges(face: list[int]) -> list[tuple[int, int]]:
    n = len(face)
    return [tuple(sorted((face[i], face[(i + 1) % n]))) for i in range(n)]


def all_edges(faces: list[list[int]]) -> list[tuple[int, int]]:
    edge_set: set[tuple[int, int]] = set()
    for face in faces:
        edge_set.update(face_edges(face))
    return sorted(edge_set)


DODEC_EDGES = all_edges(FACES)


def rotation_matrix_x(theta: float) -> np.ndarray:
    c, s = np.cos(theta), np.sin(theta)
    return np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, c, -s],
            [0.0, s, c],
        ]
    )


def rotation_matrix_y(theta: float) -> np.ndarray:
    c, s = np.cos(theta), np.sin(theta)
    return np.array(
        [
            [c, 0.0, s],
            [0.0, 1.0, 0.0],
            [-s, 0.0, c],
        ]
    )


def rotation_matrix_z(theta: float) -> np.ndarray:
    c, s = np.cos(theta), np.sin(theta)
    return np.array(
        [
            [c, -s, 0.0],
            [s, c, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )


def transform_vertices(vertices: np.ndarray, rot: np.ndarray, translate: np.ndarray) -> np.ndarray:
    return vertices @ rot.T + translate


def project_points(points3d: np.ndarray, camera: float = 9.0, scale: float = 2.6) -> np.ndarray:
    z = points3d[:, 2]
    factor = camera / (camera - z)
    x2 = scale * factor * points3d[:, 0]
    y2 = scale * factor * points3d[:, 1]
    return np.column_stack([x2, y2])


def polygon_depth(face: list[int], vertices3d: np.ndarray) -> float:
    return float(np.mean(vertices3d[np.array(face), 2]))


def draw_dodeca_shell(ax, vertices3d: np.ndarray, face_alpha: float = 0.10) -> np.ndarray:
    pts2 = project_points(vertices3d)
    face_order = sorted(range(len(FACES)), key=lambda i: polygon_depth(FACES[i], vertices3d))

    for i in face_order:
        poly_xy = pts2[np.array(FACES[i])]
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

    for a, b in DODEC_EDGES:
        xa, ya = pts2[a]
        xb, yb = pts2[b]
        ax.plot([xa, xb], [ya, yb], color="black", linewidth=0.9, alpha=0.8, zorder=2)

    return pts2


def edge_midpoint_positions(vertices3d: np.ndarray) -> dict[tuple[int, int], np.ndarray]:
    pos = {}
    for e in DODEC_EDGES:
        a, b = e
        pos[e] = 0.5 * (vertices3d[a] + vertices3d[b])
    return pos


def projected_edge_midpoints(vertices3d: np.ndarray) -> dict[tuple[int, int], np.ndarray]:
    mids3 = edge_midpoint_positions(vertices3d)
    keys = list(sorted(mids3))
    arr3 = np.array([mids3[k] for k in keys])
    arr2 = project_points(arr3)
    return {k: arr2[i] for i, k in enumerate(keys)}


def chamber_positions() -> dict[int, np.ndarray]:
    p2es = pair_to_edge_sheet()

    rot_left = rotation_matrix_z(-0.18) @ rotation_matrix_y(0.78) @ rotation_matrix_x(-0.28)
    rot_right = rotation_matrix_z(0.18) @ rotation_matrix_y(-0.78) @ rotation_matrix_x(-0.28)

    left_translate = np.array([-2.55, 0.0, 0.0])
    right_translate = np.array([2.55, 0.0, 0.0])

    left_vertices = transform_vertices(VERTICES, rot_left, left_translate)
    right_vertices = transform_vertices(VERTICES, rot_right, right_translate)

    left_mid2 = projected_edge_midpoints(left_vertices)
    right_mid2 = projected_edge_midpoints(right_vertices)

    pos = {}
    for node, (edge, sheet) in p2es.items():
        pos[node] = left_mid2[edge] if sheet == 0 else right_mid2[edge]

    return pos, left_vertices, right_vertices


def partition_edges(adj: dict[int, set[int]]) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    internal = []
    cross = []

    for u in sorted(adj):
        for v in sorted(adj[u]):
            if u < v:
                if (u % 2) == (v % 2):
                    internal.append((u, v))
                else:
                    cross.append((u, v))

    return internal, cross


def draw_chamber_graph_polyhedral() -> tuple[Path, Path]:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    adj = measured_graph_reindexed()
    pos, left_vertices, right_vertices = chamber_positions()
    internal_edges, cross_edges = partition_edges(adj)

    fig, ax = plt.subplots(figsize=(12.4, 6.4))
    ax.set_aspect("equal")
    ax.axis("off")

    draw_dodeca_shell(ax, left_vertices, face_alpha=0.10)
    draw_dodeca_shell(ax, right_vertices, face_alpha=0.10)

    # Draw true chamber-graph edges
    for u, v in internal_edges:
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        ax.plot([x1, x2], [y1, y2], color="0.20", linewidth=1.2, alpha=0.95, zorder=4)

    for u, v in cross_edges:
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        ax.plot([x1, x2], [y1, y2], color="0.35", linewidth=1.0, alpha=0.65, zorder=3)

    xs = [pos[v][0] for v in sorted(pos)]
    ys = [pos[v][1] for v in sorted(pos)]

    ax.scatter(xs, ys, s=28, facecolors="white", edgecolors="black", linewidths=0.8, zorder=5)

    pdf_path = OUTDIR / "thalean_graph_polyhedral.pdf"
    png_path = OUTDIR / "thalean_graph_polyhedral.png"

    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, bbox_inches="tight", dpi=240)
    plt.close(fig)

    return pdf_path, png_path


def main() -> None:
    pdf_path, png_path = draw_chamber_graph_polyhedral()
    print(f"Wrote: {pdf_path}")
    print(f"Wrote: {png_path}")


if __name__ == "__main__":
    main()
