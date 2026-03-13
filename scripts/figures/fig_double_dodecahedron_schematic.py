from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUTDIR = ROOT / "paper" / "thalean-paper" / "figures" / "generated"


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


def all_edges(faces: Iterable[list[int]]) -> list[tuple[int, int]]:
    edge_set: set[tuple[int, int]] = set()
    for face in faces:
        edge_set.update(face_edges(face))
    return sorted(edge_set)


EDGES = all_edges(FACES)


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


def transform_vertices(
    vertices: np.ndarray,
    rot: np.ndarray,
    translate: np.ndarray,
) -> np.ndarray:
    return vertices @ rot.T + translate


def project_points(points3d: np.ndarray, camera: float = 9.0, scale: float = 2.6) -> np.ndarray:
    z = points3d[:, 2]
    factor = camera / (camera - z)
    x2 = scale * factor * points3d[:, 0]
    y2 = scale * factor * points3d[:, 1]
    return np.column_stack([x2, y2])


def polygon_depth(face: list[int], vertices3d: np.ndarray) -> float:
    return float(np.mean(vertices3d[np.array(face), 2]))


def draw_dodecahedron(
    ax: plt.Axes,
    vertices3d: np.ndarray,
    highlight_face_idx: int | None = None,
    face_alpha: float = 0.14,
    edge_lw: float = 1.1,
) -> np.ndarray:
    pts2 = project_points(vertices3d)

    face_order = sorted(range(len(FACES)), key=lambda i: polygon_depth(FACES[i], vertices3d))

    for i in face_order:
        face = FACES[i]
        poly_xy = pts2[np.array(face)]

        is_highlight = i == highlight_face_idx
        patch = Polygon(
            poly_xy,
            closed=True,
            fill=True,
            facecolor=("0.55" if is_highlight else "0.88"),
            edgecolor="black",
            linewidth=(1.6 if is_highlight else 0.7),
            alpha=(0.38 if is_highlight else face_alpha),
            joinstyle="round",
        )
        ax.add_patch(patch)

    for a, b in EDGES:
        xa, ya = pts2[a]
        xb, yb = pts2[b]
        ax.plot([xa, xb], [ya, yb], color="black", linewidth=edge_lw, alpha=0.9, zorder=4)

    return pts2


def face_center_2d(face_idx: int, pts2: np.ndarray) -> np.ndarray:
    face = np.array(FACES[face_idx])
    return np.mean(pts2[face], axis=0)


def draw_face_bridge(
    ax: plt.Axes,
    pts2_left: np.ndarray,
    pts2_right: np.ndarray,
    left_face_idx: int,
    right_face_idx: int,
) -> None:
    left_face = FACES[left_face_idx]
    right_face = FACES[right_face_idx]

    for lv, rv in zip(left_face, right_face):
        x1, y1 = pts2_left[lv]
        x2, y2 = pts2_right[rv]
        ax.plot([x1, x2], [y1, y2], color="0.15", linewidth=1.5, alpha=0.85, zorder=6)

    c1 = face_center_2d(left_face_idx, pts2_left)
    c2 = face_center_2d(right_face_idx, pts2_right)
    ax.plot([c1[0], c2[0]], [c1[1], c2[1]], color="black", linewidth=2.2, alpha=0.95, zorder=7)


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    # Tuned for a clean "two dodecahedra with faces connected" paper schematic.
    rot_left = rotation_matrix_z(-0.18) @ rotation_matrix_y(0.78) @ rotation_matrix_x(-0.28)
    rot_right = rotation_matrix_z(0.18) @ rotation_matrix_y(-0.78) @ rotation_matrix_x(-0.28)

    left_translate = np.array([-2.55, 0.0, 0.0])
    right_translate = np.array([2.55, 0.0, 0.0])

    left_vertices = transform_vertices(VERTICES, rot_left, left_translate)
    right_vertices = transform_vertices(VERTICES, rot_right, right_translate)

    # Chosen for a pleasing inward-facing bridge.
    left_face_idx = 9
    right_face_idx = 2

    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.set_aspect("equal")
    ax.axis("off")

    pts2_left = draw_dodecahedron(ax, left_vertices, highlight_face_idx=left_face_idx)
    pts2_right = draw_dodecahedron(ax, right_vertices, highlight_face_idx=right_face_idx)

    draw_face_bridge(ax, pts2_left, pts2_right, left_face_idx, right_face_idx)

    ax.set_title("Schematic double-dodecahedron view of the Thalean graph", fontsize=15, pad=12)

    pdf_path = OUTDIR / "double_dodecahedron_schematic.pdf"
    png_path = OUTDIR / "double_dodecahedron_schematic.png"

    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, bbox_inches="tight", dpi=220)
    plt.close(fig)

    print(f"Wrote: {pdf_path}")
    print(f"Wrote: {png_path}")


if __name__ == "__main__":
    main()
