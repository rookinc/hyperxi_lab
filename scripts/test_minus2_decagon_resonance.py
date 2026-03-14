#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from pathlib import Path

import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = ROOT / "reports" / "decagons" / "ordered_decagon_pair_cycles.txt"
OUT_DIR = ROOT / "reports" / "spectral" / "transport_modes"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_decagons(path: Path) -> list[list[int]]:
    decagons: list[list[int]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line.lower().startswith("decagon"):
            continue
        if ":" not in line:
            continue
        _, rhs = line.split(":", 1)
        rhs = rhs.strip()
        if not rhs.startswith("["):
            continue
        cyc = ast.literal_eval(rhs)
        cyc = [int(x) for x in cyc]
        if len(cyc) != 10:
            raise SystemExit(f"Expected decagon length 10, got {len(cyc)} in {cyc}")
        decagons.append(cyc)
    if len(decagons) != 12:
        raise SystemExit(f"Expected 12 decagons, got {len(decagons)}")
    return decagons


def build_pair_graph(decagons: list[list[int]]) -> nx.Graph:
    G = nx.Graph()
    for cyc in decagons:
        n = len(cyc)
        for i in range(n):
            a = cyc[i]
            b = cyc[(i + 1) % n]
            G.add_edge(a, b)
    return G


def adjacency_matrix(G: nx.Graph):
    nodes = sorted(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    A = np.zeros((len(nodes), len(nodes)), dtype=float)
    for u, v in G.edges():
        i = idx[u]
        j = idx[v]
        A[i, j] = 1.0
        A[j, i] = 1.0
    return nodes, idx, A


def dft_powers_on_cycle(values: np.ndarray) -> list[float]:
    """
    Returns normalized Fourier power on harmonics k=0..5 for a 10-cycle.
    Combines k and 10-k implicitly by only reporting 0..5.
    """
    fft = np.fft.fft(values)
    powers = []
    total = float(np.sum(np.abs(fft) ** 2))
    if total <= 1e-15:
        return [0.0] * 6

    for k in range(6):
        if k == 0 or k == 5:
            p = float(np.abs(fft[k]) ** 2)
        else:
            p = float(np.abs(fft[k]) ** 2 + np.abs(fft[10 - k]) ** 2)
        powers.append(p / total)
    return powers


def main():
    decagons = load_decagons(IN_PATH)
    G = build_pair_graph(decagons)
    nodes, idx, A = adjacency_matrix(G)

    vals, vecs = np.linalg.eigh(A)
    tol = 1e-8
    minus2_idx = [i for i, lam in enumerate(vals) if abs(lam + 2.0) <= tol]
    if not minus2_idx:
        raise SystemExit("No eigenvalue -2 found.")

    minus2_vecs = vecs[:, minus2_idx]
    projector = minus2_vecs @ minus2_vecs.T
    vertex_density = np.diag(projector)

    # Per-decagon projector density
    decagon_density = []
    for d, cyc in enumerate(decagons):
        s = float(sum(vertex_density[idx[v]] for v in cyc))
        decagon_density.append((d, s))

    # Fourier analysis of each basis vector on each decagon
    harmonic_accum = np.zeros(6, dtype=float)
    detailed = []

    for local_mode, col in enumerate(minus2_idx):
        vec = vecs[:, col]
        if vec[np.argmax(np.abs(vec))] < 0:
            vec = -vec

        mode_decagon_data = []
        for d, cyc in enumerate(decagons):
            arr = np.array([vec[idx[v]] for v in cyc], dtype=float)
            powers = dft_powers_on_cycle(arr)
            harmonic_accum += np.array(powers)
            mode_decagon_data.append(
                {
                    "decagon": d,
                    "cycle_values": [float(x) for x in arr],
                    "harmonic_powers_k0_to_k5": [float(x) for x in powers],
                    "dominant_k": int(np.argmax(powers)),
                }
            )

        detailed.append(
            {
                "mode_column": int(col),
                "eigenvalue": float(vals[col]),
                "per_decagon": mode_decagon_data,
            }
        )

    if len(minus2_idx) * len(decagons) > 0:
        harmonic_accum /= (len(minus2_idx) * len(decagons))

    txt_lines = []
    txt_lines.append("=" * 80)
    txt_lines.append("MINUS-2 DECAGON RESONANCE TEST")
    txt_lines.append("=" * 80)
    txt_lines.append(f"graph vertices: {G.number_of_nodes()}")
    txt_lines.append(f"graph edges: {G.number_of_edges()}")
    txt_lines.append(f"degree set: {sorted({d for _, d in G.degree()})}")
    txt_lines.append(f"minus2 multiplicity: {len(minus2_idx)}")
    txt_lines.append("")

    txt_lines.append("DECOGON PROJECTOR DENSITY")
    txt_lines.append("-" * 80)
    for d, s in sorted(decagon_density, key=lambda x: x[1], reverse=True):
        txt_lines.append(f"decagon {d:2d}: {s:.6f}")
    txt_lines.append("")

    txt_lines.append("AVERAGE HARMONIC POWER ON C10")
    txt_lines.append("-" * 80)
    for k, p in enumerate(harmonic_accum):
        txt_lines.append(f"k={k}: {p:.6f}")
    txt_lines.append("")

    txt_lines.append("DOMINANT HARMONIC PER MODE / DECAGON")
    txt_lines.append("-" * 80)
    for mode in detailed:
        txt_lines.append(f"mode column {mode['mode_column']}  eigenvalue={mode['eigenvalue']:.6f}")
        counts = {k: 0 for k in range(6)}
        for row in mode["per_decagon"]:
            counts[row["dominant_k"]] += 1
        txt_lines.append("  " + ", ".join(f"k={k}:{counts[k]}" for k in range(6)))
    txt_lines.append("")

    out_txt = OUT_DIR / "minus2_decagon_resonance.txt"
    out_json = OUT_DIR / "minus2_decagon_resonance.json"
    out_txt.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    out_json.write_text(
        json.dumps(
            {
                "minus2_multiplicity": len(minus2_idx),
                "decagon_projector_density": [{"decagon": d, "density": s} for d, s in decagon_density],
                "average_harmonic_power_k0_to_k5": [float(x) for x in harmonic_accum],
                "detailed": detailed,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n".join(txt_lines))
    print(f"saved {out_txt.relative_to(ROOT)}")
    print(f"saved {out_json.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
