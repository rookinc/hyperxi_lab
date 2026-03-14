#!/usr/bin/env python3
from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from hyperxi.combinatorics.chamber_graph import build_chamber_graph
from hyperxi.combinatorics.thalions import build_thalions
from hyperxi.spectral.occupancy import (
    chamber_adjacency_matrix,
    chamber_laplacian_matrix,
    eig_sorted,
    mode_density,
    normalize_weights_max1,
    normalize_weights_sum1,
    shifted_laplacian,
    weighted_adjacency,
)


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "spectral" / "occupancy"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FACE_CLASS = {
    0: 0, 4: 0, 8: 0,
    1: 1, 5: 1, 9: 1,
    2: 2, 6: 2, 10: 2,
    3: 3, 7: 3, 11: 3,
}


def extract_face(flag):
    for name in ("face", "f", "face_id"):
        if hasattr(flag, name):
            return int(getattr(flag, name))
    raise AttributeError("Could not find face attribute on Flag.")


def load_graph() -> nx.Graph:
    raw = build_chamber_graph()
    G = nx.Graph()
    G.add_nodes_from(raw.vertices)
    G.add_edges_from(raw.edges)
    return G


def adjacency_spectrum(G: nx.Graph) -> tuple[list[int], np.ndarray, np.ndarray]:
    nodes, A = chamber_adjacency_matrix(G)
    eigvals, eigvecs = eig_sorted(A)
    return nodes, eigvals, eigvecs


def multiplicity_block(eigvals: np.ndarray, idx: int, tol: float = 1e-8) -> list[int]:
    target = eigvals[idx]
    return [j for j, val in enumerate(eigvals) if abs(val - target) <= tol]


def thalion_face_and_class_maps():
    thalions = build_thalions()
    th_face = {}
    th_class = {}

    for th in thalions:
        faces = sorted({extract_face(m) for m in th.members})
        if len(faces) != 1:
            raise RuntimeError(
                f"Expected one face per thalion, got thalion {th.id} on faces {faces}"
            )
        face = faces[0]
        th_face[th.id] = face
        th_class[th.id] = FACE_CLASS[face]

    return th_face, th_class


def class_profile_from_mode(
    nodes: list[int],
    vec: np.ndarray,
    th_class: dict[int, int],
) -> np.ndarray:
    sums = defaultdict(float)
    counts = defaultdict(int)

    for i, th in enumerate(nodes):
        cls = th_class[th]
        sums[cls] += float(vec[i])
        counts[cls] += 1

    out = np.zeros(4, dtype=float)
    for cls in range(4):
        out[cls] = sums[cls] / max(1, counts[cls])
    return out


def weights_from_class_profile(
    nodes: list[int],
    th_class: dict[int, int],
    class_profile: np.ndarray,
) -> np.ndarray:
    w = np.zeros(len(nodes), dtype=float)
    for i, th in enumerate(nodes):
        w[i] = class_profile[th_class[th]]
    return w


def save_node_plot(
    G: nx.Graph,
    values: np.ndarray,
    outpath: Path,
    title: str,
    seed: int = 42,
) -> None:
    pos = nx.spring_layout(G, seed=seed)
    vmax = float(np.max(np.abs(values))) or 1.0

    plt.figure(figsize=(8, 8))
    nx.draw_networkx_edges(G, pos, alpha=0.25, width=1.0)
    nodes_artist = nx.draw_networkx_nodes(
        G,
        pos,
        node_color=values,
        cmap="coolwarm",
        vmin=-vmax,
        vmax=vmax,
        node_size=140,
        linewidths=0.5,
        edgecolors="black",
    )
    plt.colorbar(nodes_artist, shrink=0.8)
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(outpath, dpi=180)
    plt.close()


def main() -> None:
    print("=" * 80)
    print("CHAMBER OCCUPANCY MODE ANALYSIS")
    print("=" * 80)

    G = load_graph()
    nodes, eigvals, eigvecs = adjacency_spectrum(G)
    _, A = chamber_adjacency_matrix(G)
    _, L = chamber_laplacian_matrix(G)
    th_face, th_class = thalion_face_and_class_maps()

    block1 = multiplicity_block(eigvals, 1)
    if len(block1) < 2:
        raise RuntimeError("Expected a 2D first excited block.")

    v1 = eigvecs[:, block1[0]].copy()
    v2 = eigvecs[:, block1[1]].copy()

    for vec in (v1, v2):
        anchor = int(np.argmax(np.abs(vec)))
        if vec[anchor] < 0:
            vec *= -1.0

    # Occupancy seed 1: squared density of mode 1
    w_mode = normalize_weights_sum1(mode_density(v1))

    # Occupancy seed 2: 12-phase average over the first excited 2-plane,
    # compressed to the 4 face classes, then lifted back to thalions.
    class_accum = np.zeros(4, dtype=float)
    for k in range(12):
        theta = 2.0 * math.pi * k / 12.0
        vec = math.cos(theta) * v1 + math.sin(theta) * v2
        class_accum += np.abs(class_profile_from_mode(nodes, vec, th_class))

    class_accum /= 12.0
    class_accum = normalize_weights_max1(class_accum)
    w_class = weights_from_class_profile(nodes, th_class, class_accum)
    w_class = normalize_weights_sum1(w_class)

    # Operators
    A_mode = weighted_adjacency(A, w_mode)
    A_class = weighted_adjacency(A, w_class)

    H_mode = A + diagonal_from_weights(w_mode, mu=1.0)
    H_class = A + diagonal_from_weights(w_class, mu=1.0)

    L_mode = shifted_laplacian(L, w_mode, mu=1.0)
    L_class = shifted_laplacian(L, w_class, mu=1.0)

    # Spectra
    A_eigs, _ = eig_sorted(A)
    A_mode_eigs, _ = eig_sorted(A_mode)
    A_class_eigs, _ = eig_sorted(A_class)
    H_mode_eigs, _ = eig_sorted(H_mode)
    H_class_eigs, _ = eig_sorted(H_class)

    L_eigs_asc = np.sort(np.linalg.eigvalsh(L))
    L_mode_eigs_asc = np.sort(np.linalg.eigvalsh(L_mode))
    L_class_eigs_asc = np.sort(np.linalg.eigvalsh(L_class))

    report = []
    report.append("=" * 80)
    report.append("CHAMBER OCCUPANCY MODE ANALYSIS")
    report.append("=" * 80)
    report.append(f"vertices: {G.number_of_nodes()}")
    report.append(f"edges:    {G.number_of_edges()}")
    report.append("")

    report.append("BASE ADJACENCY TOP 10")
    report.append("-" * 80)
    for i, val in enumerate(A_eigs[:10]):
        report.append(f"{i:2d}: {val:.9f}")
    report.append("")

    report.append("FIRST EXCITED BLOCK")
    report.append("-" * 80)
    report.append(f"lambda_1 = {eigvals[1]:.9f}")
    report.append(f"indices   = {block1}")
    report.append("")

    report.append("CLASS OCCUPANCY PROFILE")
    report.append("-" * 80)
    for cls in range(4):
        report.append(f"class C{cls}: {class_accum[cls]:.9f}")
    report.append("")

    report.append("WEIGHT STATS")
    report.append("-" * 80)
    report.append(
        f"mode-density weights: min={w_mode.min():.9e} max={w_mode.max():.9e} sum={w_mode.sum():.9f}"
    )
    report.append(
        f"class-profile weights: min={w_class.min():.9e} max={w_class.max():.9e} sum={w_class.sum():.9f}"
    )
    report.append("")

    def add_spectrum_block(title: str, eigs: np.ndarray, top: int = 10) -> None:
        report.append(title)
        report.append("-" * 80)
        for i, val in enumerate(eigs[:top]):
            report.append(f"{i:2d}: {val:.9f}")
        report.append("")

    def add_lap_block(title: str, eigs: np.ndarray, top: int = 10) -> None:
        report.append(title)
        report.append("-" * 80)
        for i, val in enumerate(eigs[:top]):
            report.append(f"{i:2d}: {val:.9f}")
        report.append("")

    add_spectrum_block("WEIGHTED ADJACENCY (MODE DENSITY) TOP 10", A_mode_eigs)
    add_spectrum_block("WEIGHTED ADJACENCY (CLASS PROFILE) TOP 10", A_class_eigs)
    add_spectrum_block("SHIFTED H = A + O (MODE DENSITY) TOP 10", H_mode_eigs)
    add_spectrum_block("SHIFTED H = A + O (CLASS PROFILE) TOP 10", H_class_eigs)

    add_lap_block("BASE LAPLACIAN LOW 10", L_eigs_asc[:10])
    add_lap_block("SHIFTED LAPLACIAN L + O (MODE DENSITY) LOW 10", L_mode_eigs_asc[:10])
    add_lap_block("SHIFTED LAPLACIAN L + O (CLASS PROFILE) LOW 10", L_class_eigs_asc[:10])

    txt_path = OUT_DIR / "chamber_occupancy_modes.txt"
    txt_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    save_node_plot(
        G,
        w_mode,
        OUT_DIR / "occupancy_mode_density.png",
        "Occupancy seed from |v1|^2",
    )
    save_node_plot(
        G,
        w_class,
        OUT_DIR / "occupancy_class_profile.png",
        "Occupancy seed from first excited face-class profile",
    )

    print(f"saved report: {txt_path.relative_to(ROOT)}")
    print(f"saved image : {(OUT_DIR / 'occupancy_mode_density.png').relative_to(ROOT)}")
    print(f"saved image : {(OUT_DIR / 'occupancy_class_profile.png').relative_to(ROOT)}")
    print("=" * 80)


def diagonal_from_weights(weights: np.ndarray, mu: float = 1.0) -> np.ndarray:
    return mu * np.diag(np.asarray(weights, dtype=float))


if __name__ == "__main__":
    main()
