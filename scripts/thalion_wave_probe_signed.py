#!/usr/bin/env python3
"""
thalion_wave_probe_signed.py

Wave propagation on the signed 2-lift structure of the Thalean graph.

State space:
    30 quotient vertices x 2 sheets

Wave equation:
    Psi[t+1] - 2 Psi[t] + Psi[t-1] = -c^2 L_signed Psi[t]

where the signed transport operator is built from:
    + preserve edges -> identity on sheet
    - swap edges     -> flip on sheet

Expected input:
    artifacts/reports/recovered_signing.txt

Outputs:
    artifacts/reports/thalion_wave_probe_signed.txt
    artifacts/reports/thalion_wave_signed_shell_energy.txt
"""

from __future__ import annotations

from pathlib import Path
from collections import Counter, defaultdict
import math
import re

import numpy as np
import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
SIGN_PATH = ROOT / "artifacts" / "reports" / "recovered_signing.txt"
REPORT_PATH = ROOT / "artifacts" / "reports" / "thalion_wave_probe_signed.txt"
SHELL_PATH = ROOT / "artifacts" / "reports" / "thalion_wave_signed_shell_energy.txt"


EDGE_RE = re.compile(
    r"^\s*(\d+)-\s*(\d+)\s+sign=([+-]1)\s+"
)


def parse_signed_base_graph(path: Path) -> tuple[nx.Graph, dict[tuple[int, int], int]]:
    g = nx.Graph()
    signs: dict[tuple[int, int], int] = {}

    for line in path.read_text(encoding="utf-8").splitlines():
        m = EDGE_RE.match(line)
        if not m:
            continue
        u = int(m.group(1))
        v = int(m.group(2))
        s = 1 if m.group(3) == "+1" else -1
        a, b = sorted((u, v))
        g.add_edge(a, b, sign=s)
        signs[(a, b)] = s

    return g, signs


def build_signed_operator(
    base: nx.Graph,
    signs: dict[tuple[int, int], int],
) -> tuple[np.ndarray, np.ndarray]:
    n = base.number_of_nodes()
    if sorted(base.nodes()) != list(range(n)):
        raise ValueError("Base graph vertices are expected to be 0..n-1")

    # Ordering:
    # index 2*v     = sheet 0 at base vertex v
    # index 2*v + 1 = sheet 1 at base vertex v
    size = 2 * n
    a = np.zeros((size, size), dtype=float)

    for u, v in base.edges():
        key = tuple(sorted((u, v)))
        s = signs[key]

        if s == 1:
            # preserve sheet
            a[2 * u, 2 * v] = 1.0
            a[2 * v, 2 * u] = 1.0
            a[2 * u + 1, 2 * v + 1] = 1.0
            a[2 * v + 1, 2 * u + 1] = 1.0
        else:
            # swap sheet
            a[2 * u, 2 * v + 1] = 1.0
            a[2 * v + 1, 2 * u] = 1.0
            a[2 * u + 1, 2 * v] = 1.0
            a[2 * v, 2 * u + 1] = 1.0

    degs = [d for _, d in base.degree()]
    degree_set = sorted(set(degs))
    if degree_set != [4]:
        raise ValueError(f"Expected 4-regular base graph, got degree set {degree_set}")

    l = 4.0 * np.eye(size) - a
    return a, l


def shell_map(base: nx.Graph, root: int) -> dict[int, list[int]]:
    lengths = nx.single_source_shortest_path_length(base, root)
    shells: dict[int, list[int]] = defaultdict(list)
    for v, dist in lengths.items():
        shells[dist].append(v)
    return dict(sorted(shells.items()))


def shell_signature(shells: dict[int, list[int]]) -> list[int]:
    return [len(shells[r]) for r in sorted(shells)]


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
    start_base_vertex: int,
    start_sheet: int = 0,
    steps: int = 18,
    c2: float = 0.5,
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    n2 = l.shape[0]
    psi0 = np.zeros(n2, dtype=float)
    idx = 2 * start_base_vertex + start_sheet
    psi0[idx] = 1.0

    psi_prev = psi0.copy()
    psi_curr = psi0.copy()

    states = [psi0.copy()]
    deltas = [np.zeros(n2, dtype=float)]

    for _ in range(steps):
        psi_next = 2.0 * psi_curr - psi_prev - c2 * (l @ psi_curr)
        delta = psi_next - psi_curr
        states.append(psi_next.copy())
        deltas.append(delta.copy())
        psi_prev, psi_curr = psi_curr, psi_next

    return states, deltas


def split_sheet_energy(psi: np.ndarray) -> tuple[float, float]:
    e0 = float(np.sum(np.abs(psi[0::2]) ** 2))
    e1 = float(np.sum(np.abs(psi[1::2]) ** 2))
    return e0, e1


def shell_sheet_energies(
    states: list[np.ndarray],
    shells: dict[int, list[int]],
) -> list[dict[int, tuple[float, float]]]:
    rows: list[dict[int, tuple[float, float]]] = []
    for psi in states:
        row: dict[int, tuple[float, float]] = {}
        for r, verts in shells.items():
            idx0 = [2 * v for v in verts]
            idx1 = [2 * v + 1 for v in verts]
            e0 = float(np.sum(np.abs(psi[idx0]) ** 2))
            e1 = float(np.sum(np.abs(psi[idx1]) ** 2))
            row[r] = (e0, e1)
        rows.append(row)
    return rows


def energy_like(states: list[np.ndarray], deltas: list[np.ndarray], l: np.ndarray, c2: float) -> list[float]:
    vals = []
    for psi, dpsi in zip(states, deltas):
        kinetic = float(np.dot(dpsi, dpsi))
        potential = float(c2 * np.dot(psi, l @ psi))
        vals.append(0.5 * (kinetic + potential))
    return vals


def write_shell_report(
    shell_rows: list[dict[int, tuple[float, float]]],
    shells: dict[int, list[int]],
) -> None:
    radii = sorted(shells)
    with SHELL_PATH.open("w", encoding="utf-8") as f:
        header = ["t"]
        for r in radii:
            header.extend([f"r{r}_s0", f"r{r}_s1"])
        f.write(" ".join(header) + "\n")

        for t, row in enumerate(shell_rows):
            vals = [str(t)]
            for r in radii:
                e0, e1 = row[r]
                vals.extend([f"{e0:.8f}", f"{e1:.8f}"])
            f.write(" ".join(vals) + "\n")


def main() -> None:
    base, signs = parse_signed_base_graph(SIGN_PATH)
    a, l = build_signed_operator(base, signs)

    sign_hist = Counter(signs.values())

    start_base_vertex = 0
    start_sheet = 0
    steps = 18
    c2 = 0.5

    shells = shell_map(base, start_base_vertex)
    sig = shell_signature(shells)

    states, deltas = evolve_wave(
        l,
        start_base_vertex=start_base_vertex,
        start_sheet=start_sheet,
        steps=steps,
        c2=c2,
    )
    shell_rows = shell_sheet_energies(states, shells)
    energy_rows = energy_like(states, deltas, l, c2)
    modes = modal_frequencies(a, c2)

    write_shell_report(shell_rows, shells)

    lines: list[str] = []
    lines.append("=" * 80)
    lines.append("THALION SIGNED WAVE PROBE")
    lines.append("=" * 80)
    lines.append(f"sign path: {SIGN_PATH}")
    lines.append(f"base vertices: {base.number_of_nodes()}")
    lines.append(f"base edges: {base.number_of_edges()}")
    lines.append(f"base degree set: {sorted(set(dict(base.degree()).values()))}")
    lines.append(f"sign histogram: {{'+1': {sign_hist[1]}, '-1': {sign_hist[-1]}}}")
    lines.append("")
    lines.append(f"lifted state dimension: {a.shape[0]}")
    lines.append(f"start base vertex: {start_base_vertex}")
    lines.append(f"start sheet: {start_sheet}")
    lines.append(f"steps: {steps}")
    lines.append(f"c^2: {c2}")
    lines.append("")
    lines.append("BASE SHELL STRUCTURE FROM START VERTEX")
    lines.append("-" * 80)
    lines.append(f"{sig}")
    lines.append("")
    lines.append("MODAL FREQUENCIES OF SIGNED OPERATOR")
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
    lines.append("TOTAL SHEET ENERGY")
    lines.append("-" * 80)
    for t, psi in enumerate(states):
        e0, e1 = split_sheet_energy(psi)
        imb = e0 - e1
        lines.append(f"t={t:2d}  sheet0={e0:.8f}  sheet1={e1:.8f}  imbalance={imb:.8f}")
    lines.append("")
    lines.append("SHELL ENERGY BY SHEET")
    lines.append("-" * 80)
    radii = sorted(shells)
    header = "t  " + "  ".join(f"r={r}[s0,s1]" for r in radii)
    lines.append(header)
    for t, row in enumerate(shell_rows):
        parts = []
        for r in radii:
            e0, e1 = row[r]
            parts.append(f"({e0:.6f},{e1:.6f})")
        lines.append(f"{t:2d}  " + "  ".join(parts))
    lines.append("")
    lines.append("INTERPRETATION")
    lines.append("-" * 80)
    lines.append("Watch for oscillatory transfer between the two sheets.")
    lines.append("If sheet energy alternates or beats coherently, the signed")
    lines.append("monodromy is dynamically active rather than merely combinatorial.")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
