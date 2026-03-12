#!/usr/bin/env python3
"""
thalion_wave_probe.py

Discrete wave propagation on the Thalion graph.

Wave equation:
    psi[t+1] - 2 psi[t] + psi[t-1] = -c^2 L psi[t]
where
    L = d I - A
and d = 4 for the Thalion graph.

This script:
- loads the Thalion graph from artifacts/census/thalion_graph.g6
- evolves a pulse from a chosen start vertex
- reports shell-by-shell energy over time
- reports total energy-like diagnostics
- reports modal frequencies from the adjacency spectrum

Usage:
    python3 scripts/thalion_wave_probe.py | tee artifacts/reports/thalion_wave_probe.txt
"""

from __future__ import annotations

from pathlib import Path
from collections import Counter, defaultdict

import math
import numpy as np
import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
G6_PATH = ROOT / "artifacts" / "census" / "thalion_graph.g6"
REPORT_PATH = ROOT / "artifacts" / "reports" / "thalion_wave_probe.txt"
SHELL_PATH = ROOT / "artifacts" / "reports" / "thalion_wave_shell_energy.txt"


def load_graph() -> nx.Graph:
    data = G6_PATH.read_text(encoding="utf-8").strip()
    g = nx.from_graph6_bytes(data.encode("ascii"))
    return nx.convert_node_labels_to_integers(g)


def adjacency_and_laplacian(g: nx.Graph) -> tuple[np.ndarray, np.ndarray]:
    a = nx.to_numpy_array(g, dtype=float)
    degs = [d for _, d in g.degree()]
    degree_set = sorted(set(degs))
    if degree_set != [4]:
        raise ValueError(f"Expected 4-regular graph, got degree set {degree_set}")
    l = 4.0 * np.eye(g.number_of_nodes()) - a
    return a, l


def shell_map(g: nx.Graph, root: int) -> dict[int, list[int]]:
    lengths = nx.single_source_shortest_path_length(g, root)
    shells: dict[int, list[int]] = defaultdict(list)
    for v, dist in lengths.items():
        shells[dist].append(v)
    return dict(sorted(shells.items()))


def shell_signature(shells: dict[int, list[int]]) -> list[int]:
    return [len(shells[k]) for k in sorted(shells)]


def modal_frequencies(a: np.ndarray, c2: float) -> list[tuple[float, int, float | None]]:
    vals = np.linalg.eigvalsh(a)
    rounded = np.round(vals, 6)
    counts = Counter(float(x) for x in rounded)

    out = []
    for lam in sorted(counts):
        arg = 1.0 - 0.5 * c2 * (4.0 - lam)
        omega = math.acos(arg) if -1.0 <= arg <= 1.0 else None
        out.append((lam, counts[lam], omega))
    return out


def evolve_wave(
    l: np.ndarray,
    start_vertex: int,
    steps: int = 18,
    c2: float = 0.5,
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    n = l.shape[0]
    psi0 = np.zeros(n, dtype=float)
    psi0[start_vertex] = 1.0

    # zero initial velocity
    psi_prev = psi0.copy()
    psi_curr = psi0.copy()

    states = [psi0.copy()]
    deltas = [np.zeros(n, dtype=float)]

    for _ in range(steps):
        psi_next = 2.0 * psi_curr - psi_prev - c2 * (l @ psi_curr)
        delta = psi_next - psi_curr
        states.append(psi_next.copy())
        deltas.append(delta.copy())
        psi_prev, psi_curr = psi_curr, psi_next

    return states, deltas


def shell_energies(states: list[np.ndarray], shells: dict[int, list[int]]) -> list[dict[int, float]]:
    out: list[dict[int, float]] = []
    for psi in states:
        row: dict[int, float] = {}
        for r, verts in shells.items():
            row[r] = float(np.sum(np.abs(psi[verts]) ** 2))
        out.append(row)
    return out


def energy_like(states: list[np.ndarray], deltas: list[np.ndarray], l: np.ndarray, c2: float) -> list[float]:
    vals = []
    for psi, dpsi in zip(states, deltas):
        kinetic = float(np.dot(dpsi, dpsi))
        potential = float(c2 * np.dot(psi, l @ psi))
        vals.append(0.5 * (kinetic + potential))
    return vals


def write_shell_report(
    shell_energy_rows: list[dict[int, float]],
    shells: dict[int, list[int]],
) -> None:
    radii = sorted(shells)
    with SHELL_PATH.open("w", encoding="utf-8") as f:
        f.write("t " + " ".join(f"r{r}" for r in radii) + "\n")
        for t, row in enumerate(shell_energy_rows):
            f.write(
                str(t) + " " + " ".join(f"{row[r]:.8f}" for r in radii) + "\n"
            )


def main() -> None:
    g = load_graph()
    a, l = adjacency_and_laplacian(g)

    start_vertex = 0
    steps = 18
    c2 = 0.5

    shells = shell_map(g, start_vertex)
    sig = shell_signature(shells)

    states, deltas = evolve_wave(l, start_vertex=start_vertex, steps=steps, c2=c2)
    shell_rows = shell_energies(states, shells)
    energy_rows = energy_like(states, deltas, l, c2)
    modes = modal_frequencies(a, c2)

    write_shell_report(shell_rows, shells)

    lines: list[str] = []
    lines.append("=" * 80)
    lines.append("THALION WAVE PROBE")
    lines.append("=" * 80)
    lines.append(f"graph path: {G6_PATH}")
    lines.append(f"vertices: {g.number_of_nodes()}")
    lines.append(f"edges: {g.number_of_edges()}")
    lines.append(f"degree set: {sorted(set(dict(g.degree()).values()))}")
    lines.append("")
    lines.append(f"start vertex: {start_vertex}")
    lines.append(f"steps: {steps}")
    lines.append(f"c^2: {c2}")
    lines.append("")
    lines.append("SHELL STRUCTURE FROM START VERTEX")
    lines.append("-" * 80)
    lines.append(f"{sig}")
    lines.append("")
    lines.append("MODAL FREQUENCIES")
    lines.append("-" * 80)
    lines.append("lambda        mult    omega")
    for lam, mult, omega in modes:
        omega_str = f"{omega:.8f}" if omega is not None else "unstable"
        lines.append(f"{lam:>8.6f}    {mult:>4d}    {omega_str}")
    lines.append("")
    lines.append("ENERGY-LIKE DIAGNOSTIC")
    lines.append("-" * 80)
    for t, e in enumerate(energy_rows):
        lines.append(f"t={t:2d}  E={e:.8f}")
    lines.append("")
    lines.append("SHELL ENERGY BY TIME")
    lines.append("-" * 80)
    radii = sorted(shells)
    header = "t  " + "  ".join(f"r={r}" for r in radii)
    lines.append(header)
    for t, row in enumerate(shell_rows):
        vals = "  ".join(f"{row[r]:.6f}" for r in radii)
        lines.append(f"{t:2d}  {vals}")
    lines.append("")
    lines.append("INTERPRETATION")
    lines.append("-" * 80)
    lines.append("Track whether energy initially expands shell-by-shell and then")
    lines.append("reconverges due to compact closure. Compare breathing patterns")
    lines.append("against the known shell profile (1,4,8,16,24,6,1).")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
