#!/usr/bin/env python3
"""
thalion_wave_probe_parity.py

Parity-resolved wave probe on the signed 2-lift model of the Thalion graph.

Initial conditions:
    1) localized on sheet 0
    2) symmetric   : (1,  1)/sqrt(2)
    3) antisymmetric: (1, -1)/sqrt(2)

Wave equation:
    Psi[t+1] - 2 Psi[t] + Psi[t-1] = -c^2 L_signed Psi[t]

Outputs:
    artifacts/reports/thalion_wave_probe_parity.txt
    artifacts/reports/thalion_wave_parity_shell_energy_<seed>.txt
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
REPORT_PATH = ROOT / "artifacts" / "reports" / "thalion_wave_probe_parity.txt"

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


def build_signed_operator(
    base: nx.Graph,
    signs: dict[tuple[int, int], int],
) -> tuple[np.ndarray, np.ndarray]:
    n = base.number_of_nodes()
    size = 2 * n
    a = np.zeros((size, size), dtype=float)

    for u, v in base.edges():
        key = tuple(sorted((u, v)))
        s = signs[key]

        if s == 1:
            a[2 * u, 2 * v] = 1.0
            a[2 * v, 2 * u] = 1.0
            a[2 * u + 1, 2 * v + 1] = 1.0
            a[2 * v + 1, 2 * u + 1] = 1.0
        else:
            a[2 * u, 2 * v + 1] = 1.0
            a[2 * v + 1, 2 * u] = 1.0
            a[2 * u + 1, 2 * v] = 1.0
            a[2 * v, 2 * u + 1] = 1.0

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


def evolve_wave(
    l: np.ndarray,
    psi0: np.ndarray,
    steps: int = 18,
    c2: float = 0.5,
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    psi_prev = psi0.copy()
    psi_curr = psi0.copy()

    states = [psi0.copy()]
    deltas = [np.zeros_like(psi0)]

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


def split_parity_energy(psi: np.ndarray) -> tuple[float, float]:
    """
    For each base vertex v:
      symmetric component   s_v = (a_v + b_v)/sqrt(2)
      antisymmetric comp    d_v = (a_v - b_v)/sqrt(2)
    """
    a = psi[0::2]
    b = psi[1::2]
    s = (a + b) / math.sqrt(2.0)
    d = (a - b) / math.sqrt(2.0)
    es = float(np.sum(np.abs(s) ** 2))
    ed = float(np.sum(np.abs(d) ** 2))
    return es, ed


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
    name: str,
    shell_rows: list[dict[int, tuple[float, float]]],
    shells: dict[int, list[int]],
) -> None:
    path = ROOT / "artifacts" / "reports" / f"thalion_wave_parity_shell_energy_{name}.txt"
    radii = sorted(shells)
    with path.open("w", encoding="utf-8") as f:
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


def parity_mode_summary(a: np.ndarray) -> list[tuple[float, int, int, int]]:
    """
    For each eigenvalue bucket, count how many eigenvectors are predominantly:
      symmetric, antisymmetric, mixed
    under the sheet exchange decomposition.
    """
    vals, vecs = np.linalg.eigh(a)
    rounded = np.round(vals, 6)

    buckets: dict[float, list[int]] = defaultdict(list)
    for i, lam in enumerate(rounded):
        buckets[float(lam)].append(i)

    summary = []
    for lam in sorted(buckets):
        sym = 0
        anti = 0
        mixed = 0

        for idx in buckets[lam]:
            v = vecs[:, idx]
            s_e, a_e = split_parity_energy(v)
            total = s_e + a_e
            if total == 0:
                mixed += 1
                continue
            rs = s_e / total
            ra = a_e / total
            if rs > 0.95:
                sym += 1
            elif ra > 0.95:
                anti += 1
            else:
                mixed += 1

        summary.append((lam, len(buckets[lam]), sym, anti, mixed))
    return summary


def make_seed_localized(n: int, base_vertex: int = 0) -> np.ndarray:
    psi = np.zeros(2 * n, dtype=float)
    psi[2 * base_vertex] = 1.0
    return psi


def make_seed_symmetric(n: int, base_vertex: int = 0) -> np.ndarray:
    psi = np.zeros(2 * n, dtype=float)
    psi[2 * base_vertex] = 1.0 / math.sqrt(2.0)
    psi[2 * base_vertex + 1] = 1.0 / math.sqrt(2.0)
    return psi


def make_seed_antisymmetric(n: int, base_vertex: int = 0) -> np.ndarray:
    psi = np.zeros(2 * n, dtype=float)
    psi[2 * base_vertex] = 1.0 / math.sqrt(2.0)
    psi[2 * base_vertex + 1] = -1.0 / math.sqrt(2.0)
    return psi


def overlap_with_seed(states: list[np.ndarray], seed: np.ndarray) -> list[float]:
    seed_norm = float(np.dot(seed, seed))
    if seed_norm == 0:
        return [0.0 for _ in states]
    return [float(np.dot(psi, seed)) / seed_norm for psi in states]


def main() -> None:
    base, signs = parse_signed_base_graph(SIGN_PATH)
    a, l = build_signed_operator(base, signs)

    n = base.number_of_nodes()
    start_base_vertex = 0
    steps = 18
    c2 = 0.5

    shells = shell_map(base, start_base_vertex)
    sig = shell_signature(shells)

    seeds = {
        "localized": make_seed_localized(n, start_base_vertex),
        "symmetric": make_seed_symmetric(n, start_base_vertex),
        "antisymmetric": make_seed_antisymmetric(n, start_base_vertex),
    }

    modes = modal_frequencies(a, c2)
    parity_modes = parity_mode_summary(a)

    lines: list[str] = []
    lines.append("=" * 80)
    lines.append("THALION PARITY WAVE PROBE")
    lines.append("=" * 80)
    lines.append(f"sign path: {SIGN_PATH}")
    lines.append(f"base vertices: {base.number_of_nodes()}")
    lines.append(f"base edges: {base.number_of_edges()}")
    lines.append(f"base degree set: {sorted(set(dict(base.degree()).values()))}")
    lines.append(f"shell structure from start vertex: {sig}")
    lines.append(f"steps: {steps}")
    lines.append(f"c^2: {c2}")
    lines.append("")
    lines.append("MODAL FREQUENCIES")
    lines.append("-" * 80)
    lines.append("lambda        mult    omega")
    for lam, mult, omega in modes:
        omega_str = f"{omega:.8f}" if omega is not None else "unstable"
        lines.append(f"{lam:>8.6f}    {mult:>4d}    {omega_str}")
    lines.append("")
    lines.append("MODE PARITY SUMMARY")
    lines.append("-" * 80)
    lines.append("lambda        mult    sym    anti   mixed")
    for lam, mult, sym, anti, mixed in parity_modes:
        lines.append(f"{lam:>8.6f}    {mult:>4d}    {sym:>4d}   {anti:>4d}   {mixed:>4d}")

    for name, seed in seeds.items():
        states, deltas = evolve_wave(l, seed, steps=steps, c2=c2)
        shell_rows = shell_sheet_energies(states, shells)
        energy_rows = energy_like(states, deltas, l, c2)
        overlaps = overlap_with_seed(states, seed)

        write_shell_report(name, shell_rows, shells)

        lines.append("")
        lines.append("=" * 80)
        lines.append(f"SEED: {name.upper()}")
        lines.append("=" * 80)
        lines.append("t   totalE      sheet0      sheet1      sym         anti        overlap")
        for t, psi in enumerate(states):
            e0, e1 = split_sheet_energy(psi)
            es, ea = split_parity_energy(psi)
            ov = overlaps[t]
            lines.append(
                f"{t:2d}  {energy_rows[t]:.8f}  {e0:.8f}  {e1:.8f}  {es:.8f}  {ea:.8f}  {ov:.8f}"
            )

        lines.append("")
        lines.append("SHELL ENERGY BY SHEET")
        lines.append("-" * 80)
        radii = sorted(shells)
        header = "t  " + "  ".join(f"r={r}[s0,s1]" for r in radii)
        lines.append(header)
        for t, row in enumerate(shell_rows):
            parts = []
            for r in radii:
                s0, s1 = row[r]
                parts.append(f"({s0:.6f},{s1:.6f})")
            lines.append(f"{t:2d}  " + "  ".join(parts))

    lines.append("")
    lines.append("INTERPRETATION")
    lines.append("-" * 80)
    lines.append("The symmetric and antisymmetric seeds test whether the signed")
    lines.append("cruller twist naturally decomposes the dynamics into parity sectors.")
    lines.append("A clean sector separation suggests an internal binary mode structure.")
    lines.append("The localized seed shows how a generic pulse mixes those sectors.")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
