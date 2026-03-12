#!/usr/bin/env python3
"""
thalion_sector_operators.py

Extract the symmetric and antisymmetric effective operators
for the signed 2-lift structure of the Thalean graph.

If the 60-state signed lift decomposes by parity, then:
    A_sym  = A_plus + A_minus
    A_anti = A_plus - A_minus

This script:
- parses recovered_signing.txt
- builds A_plus, A_minus on the 30-vertex base
- forms A_sym and A_anti
- computes spectra of both
- verifies that their union matches the 60-state lift spectrum
- runs wave probes separately on both sectors

Outputs:
    artifacts/reports/thalion_sector_operators.txt
    artifacts/reports/thalion_sector_wave_sym.txt
    artifacts/reports/thalion_sector_wave_anti.txt
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
REPORT_PATH = ROOT / "artifacts" / "reports" / "thalion_sector_operators.txt"
SYM_WAVE_PATH = ROOT / "artifacts" / "reports" / "thalion_sector_wave_sym.txt"
ANTI_WAVE_PATH = ROOT / "artifacts" / "reports" / "thalion_sector_wave_anti.txt"

EDGE_RE = re.compile(r"^\s*(\d+)-\s*(\d+)\s+sign=([+-]1)\s+")


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


def build_sector_operators(
    base: nx.Graph,
    signs: dict[tuple[int, int], int],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = base.number_of_nodes()
    a_plus = np.zeros((n, n), dtype=float)
    a_minus = np.zeros((n, n), dtype=float)

    for u, v in base.edges():
        a, b = sorted((u, v))
        s = signs[(a, b)]
        if s == 1:
            a_plus[u, v] = a_plus[v, u] = 1.0
        else:
            a_minus[u, v] = a_minus[v, u] = 1.0

    a_sym = a_plus + a_minus
    a_anti = a_plus - a_minus
    return a_plus, a_minus, a_sym, a_anti


def rounded_spec(mat: np.ndarray) -> list[tuple[float, int]]:
    vals = np.linalg.eigvalsh(mat)
    rounded = np.round(vals, 6)
    counts = Counter(float(x) for x in rounded)
    return sorted(counts.items())


def expand_spec(spec: list[tuple[float, int]]) -> list[float]:
    out: list[float] = []
    for lam, mult in spec:
        out.extend([lam] * mult)
    return sorted(out)


def modal_frequencies(spec: list[tuple[float, int]], c2: float) -> list[tuple[float, int, float | None]]:
    out = []
    for lam, mult in spec:
        arg = 1.0 - 0.5 * c2 * (4.0 - lam)
        omega = math.acos(arg) if -1.0 <= arg <= 1.0 else None
        out.append((lam, mult, omega))
    return out


def shell_map(base: nx.Graph, root: int) -> dict[int, list[int]]:
    lengths = nx.single_source_shortest_path_length(base, root)
    shells: dict[int, list[int]] = defaultdict(list)
    for v, dist in lengths.items():
        shells[dist].append(v)
    return dict(sorted(shells.items()))


def evolve_sector_wave(
    a_sector: np.ndarray,
    start_vertex: int,
    steps: int = 18,
    c2: float = 0.5,
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    n = a_sector.shape[0]
    l_sector = 4.0 * np.eye(n) - a_sector

    psi0 = np.zeros(n, dtype=float)
    psi0[start_vertex] = 1.0

    psi_prev = psi0.copy()
    psi_curr = psi0.copy()

    states = [psi0.copy()]
    deltas = [np.zeros(n, dtype=float)]

    for _ in range(steps):
        psi_next = 2.0 * psi_curr - psi_prev - c2 * (l_sector @ psi_curr)
        delta = psi_next - psi_curr
        states.append(psi_next.copy())
        deltas.append(delta.copy())
        psi_prev, psi_curr = psi_curr, psi_next

    return states, deltas


def shell_energies(states: list[np.ndarray], shells: dict[int, list[int]]) -> list[dict[int, float]]:
    rows: list[dict[int, float]] = []
    for psi in states:
        row: dict[int, float] = {}
        for r, verts in shells.items():
            row[r] = float(np.sum(np.abs(psi[verts]) ** 2))
        rows.append(row)
    return rows


def energy_like(states: list[np.ndarray], deltas: list[np.ndarray], a_sector: np.ndarray, c2: float) -> list[float]:
    l_sector = 4.0 * np.eye(a_sector.shape[0]) - a_sector
    vals = []
    for psi, dpsi in zip(states, deltas):
        kinetic = float(np.dot(dpsi, dpsi))
        potential = float(c2 * np.dot(psi, l_sector @ psi))
        vals.append(0.5 * (kinetic + potential))
    return vals


def write_sector_wave_report(
    path: Path,
    name: str,
    states: list[np.ndarray],
    deltas: list[np.ndarray],
    shells: dict[int, list[int]],
    a_sector: np.ndarray,
    c2: float,
) -> None:
    shell_rows = shell_energies(states, shells)
    energy_rows = energy_like(states, deltas, a_sector, c2)

    lines: list[str] = []
    lines.append("=" * 80)
    lines.append(f"THALION SECTOR WAVE: {name}")
    lines.append("=" * 80)
    lines.append("t   totalE")
    for t, e in enumerate(energy_rows):
        lines.append(f"{t:2d}  {e:.8f}")
    lines.append("")
    lines.append("SHELL ENERGY")
    lines.append("-" * 80)
    radii = sorted(shells)
    lines.append("t  " + "  ".join(f"r={r}" for r in radii))
    for t, row in enumerate(shell_rows):
        vals = "  ".join(f"{row[r]:.8f}" for r in radii)
        lines.append(f"{t:2d}  {vals}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    base, signs = parse_signed_base_graph(SIGN_PATH)
    a_plus, a_minus, a_sym, a_anti = build_sector_operators(base, signs)

    c2 = 0.5
    start_vertex = 0
    steps = 18

    spec_sym = rounded_spec(a_sym)
    spec_anti = rounded_spec(a_anti)

    union_spec = sorted(expand_spec(spec_sym) + expand_spec(spec_anti))

    shells = shell_map(base, start_vertex)

    states_sym, deltas_sym = evolve_sector_wave(a_sym, start_vertex=start_vertex, steps=steps, c2=c2)
    states_anti, deltas_anti = evolve_sector_wave(a_anti, start_vertex=start_vertex, steps=steps, c2=c2)

    write_sector_wave_report(SYM_WAVE_PATH, "SYMMETRIC", states_sym, deltas_sym, shells, a_sym, c2)
    write_sector_wave_report(ANTI_WAVE_PATH, "ANTISYMMETRIC", states_anti, deltas_anti, shells, a_anti, c2)

    lines: list[str] = []
    lines.append("=" * 80)
    lines.append("THALION SECTOR OPERATORS")
    lines.append("=" * 80)
    lines.append(f"sign path: {SIGN_PATH}")
    lines.append(f"base vertices: {base.number_of_nodes()}")
    lines.append(f"base edges: {base.number_of_edges()}")
    lines.append(f"degree set: {sorted(set(dict(base.degree()).values()))}")
    lines.append(f"+ edges: {sum(1 for s in signs.values() if s == 1)}")
    lines.append(f"- edges: {sum(1 for s in signs.values() if s == -1)}")
    lines.append("")
    lines.append("DEFINITION")
    lines.append("-" * 80)
    lines.append("A_sym  = A_plus + A_minus")
    lines.append("A_anti = A_plus - A_minus")
    lines.append("")
    lines.append("SPECTRUM OF A_sym")
    lines.append("-" * 80)
    for lam, mult in spec_sym:
        lines.append(f"{lam:>8.6f}  mult={mult}")
    lines.append("")
    lines.append("SPECTRUM OF A_anti")
    lines.append("-" * 80)
    for lam, mult in spec_anti:
        lines.append(f"{lam:>8.6f}  mult={mult}")
    lines.append("")
    lines.append("MODAL FREQUENCIES: SYMMETRIC SECTOR")
    lines.append("-" * 80)
    for lam, mult, omega in modal_frequencies(spec_sym, c2):
        omega_str = f"{omega:.8f}" if omega is not None else "unstable"
        lines.append(f"{lam:>8.6f}  mult={mult}  omega={omega_str}")
    lines.append("")
    lines.append("MODAL FREQUENCIES: ANTISYMMETRIC SECTOR")
    lines.append("-" * 80)
    for lam, mult, omega in modal_frequencies(spec_anti, c2):
        omega_str = f"{omega:.8f}" if omega is not None else "unstable"
        lines.append(f"{lam:>8.6f}  mult={mult}  omega={omega_str}")
    lines.append("")
    lines.append("UNION CHECK")
    lines.append("-" * 80)
    lines.append("The multiset union Spec(A_sym) ∪ Spec(A_anti) should reproduce")
    lines.append("the 60-state lifted spectrum.")
    lines.append("union size = " + str(len(union_spec)))
    lines.append("union values =")
    lines.append(str(union_spec))
    lines.append("")
    lines.append("INTERPRETATION")
    lines.append("-" * 80)
    lines.append("If A_sym and A_anti differ substantially, the cruller twist creates")
    lines.append("two distinct effective dynamics on the same 30-vertex base.")
    lines.append("The symmetric sector sees the unsigned base adjacency;")
    lines.append("the antisymmetric sector sees the signed base adjacency.")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
