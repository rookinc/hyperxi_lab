#!/usr/bin/env python3
from __future__ import annotations

import ast
import cmath
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
            raise SystemExit(f"Expected 10-cycle, got {len(cyc)}")
        decagons.append(cyc)
    if len(decagons) != 12:
        raise SystemExit(f"Expected 12 decagons, got {len(decagons)}")
    return decagons


def build_graph(decagons: list[list[int]]) -> nx.Graph:
    G = nx.Graph()
    for cyc in decagons:
        for i in range(10):
            a = cyc[i]
            b = cyc[(i + 1) % 10]
            G.add_edge(a, b)
    return G


def adjacency_data(G: nx.Graph):
    nodes = sorted(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    A = np.zeros((len(nodes), len(nodes)), dtype=float)
    for u, v in G.edges():
        i = idx[u]
        j = idx[v]
        A[i, j] = 1.0
        A[j, i] = 1.0
    vals, vecs = np.linalg.eigh(A)
    return nodes, idx, A, vals, vecs


def cycle_fourier_component(values: np.ndarray, k: int) -> complex:
    """
    Fourier coefficient on C10 with harmonic k.
    """
    n = len(values)
    coeff = 0j
    for j, x in enumerate(values):
        coeff += x * cmath.exp(-2j * cmath.pi * k * j / n)
    return coeff / n


def best_mode_for_harmonic(decagons, idx, vals, vecs, eig_target=-2.0, harmonic_k=5, tol=1e-8):
    target_cols = [i for i, lam in enumerate(vals) if abs(lam - eig_target) <= tol]
    if not target_cols:
        raise SystemExit(f"No eigenvalue near {eig_target}")

    best = None
    for col in target_cols:
        vec = vecs[:, col].copy()
        score = 0.0
        per_dec = []
        for cyc in decagons:
            arr = np.array([vec[idx[v]] for v in cyc], dtype=float)
            c = cycle_fourier_component(arr, harmonic_k)
            p = abs(c) ** 2
            score += p
            per_dec.append(p)
        if best is None or score > best["score"]:
            best = {
                "col": col,
                "lambda": float(vals[col]),
                "vec": vec,
                "score": float(score),
                "per_decagon_power": per_dec,
            }
    return best


def phase_edge_transport_from_mode(decagons, idx, vec, harmonic_k):
    """
    For each directed edge along each decagon, infer a U(1) transport phase
    from the target harmonic progression exp(2πik/10).

    If vec[b] ≈ phase * vec[a], then phase ~ vec[b]/vec[a].
    We compare that to the ideal harmonic step ω_k.
    """
    omega = cmath.exp(2j * cmath.pi * harmonic_k / 10.0)

    directed_phases = {}
    samples = []

    for d, cyc in enumerate(decagons):
        for i in range(10):
            a = cyc[i]
            b = cyc[(i + 1) % 10]
            va = complex(vec[idx[a]])
            vb = complex(vec[idx[b]])

            if abs(va) < 1e-10 or abs(vb) < 1e-10:
                phase = 1.0 + 0j
            else:
                raw = vb / va
                raw /= abs(raw)
                # compare to ideal harmonic step
                phase = raw / omega
                if abs(phase) > 1e-10:
                    phase /= abs(phase)
                else:
                    phase = 1.0 + 0j

            directed_phases[(a, b)] = phase
            directed_phases[(b, a)] = phase.conjugate()
            samples.append((d, a, b, phase))

    return directed_phases, samples


def holonomy_on_cycle(cycle, directed_phases):
    h = 1.0 + 0j
    for i in range(len(cycle)):
        a = cycle[i]
        b = cycle[(i + 1) % len(cycle)]
        h *= directed_phases[(a, b)]
    return h


def main():
    decagons = load_decagons(IN_PATH)
    G = build_graph(decagons)
    nodes, idx, A, vals, vecs = adjacency_data(G)

    # Test both dominant harmonics seen in the resonance report
    harmonic_tests = [4, 5]
    results = []

    for k in harmonic_tests:
        best = best_mode_for_harmonic(decagons, idx, vals, vecs, eig_target=-2.0, harmonic_k=k)
        vec = best["vec"]
        if vec[np.argmax(np.abs(vec))] < 0:
            vec = -vec

        directed_phases, samples = phase_edge_transport_from_mode(decagons, idx, vec, k)

        holonomies = []
        for d, cyc in enumerate(decagons):
            h = holonomy_on_cycle(cyc, directed_phases)
            holonomies.append(
                {
                    "decagon": d,
                    "holonomy_real": float(h.real),
                    "holonomy_imag": float(h.imag),
                    "abs": float(abs(h)),
                    "phase_angle": float(cmath.phase(h)),
                    "distance_to_plus1": float(abs(h - 1)),
                    "distance_to_minus1": float(abs(h + 1)),
                }
            )

        mean_plus = float(np.mean([x["distance_to_plus1"] for x in holonomies]))
        mean_minus = float(np.mean([x["distance_to_minus1"] for x in holonomies]))

        results.append(
            {
                "harmonic_k": k,
                "mode_column": int(best["col"]),
                "eigenvalue": float(best["lambda"]),
                "score": float(best["score"]),
                "holonomies": holonomies,
                "mean_distance_to_plus1": mean_plus,
                "mean_distance_to_minus1": mean_minus,
            }
        )

    txt_lines = []
    txt_lines.append("=" * 80)
    txt_lines.append("DECOGON PHASE HOLONOMY TEST")
    txt_lines.append("=" * 80)
    txt_lines.append(f"graph vertices: {G.number_of_nodes()}")
    txt_lines.append(f"graph edges: {G.number_of_edges()}")
    txt_lines.append(f"degree set: {sorted({d for _, d in G.degree()})}")
    txt_lines.append("")

    for r in results:
        txt_lines.append("-" * 80)
        txt_lines.append(
            f"harmonic k={r['harmonic_k']}  "
            f"mode_column={r['mode_column']}  "
            f"eigenvalue={r['eigenvalue']:.6f}  "
            f"score={r['score']:.6f}"
        )
        txt_lines.append(
            f"mean distance to +1: {r['mean_distance_to_plus1']:.6f}"
        )
        txt_lines.append(
            f"mean distance to -1: {r['mean_distance_to_minus1']:.6f}"
        )
        txt_lines.append("per-decagon holonomy:")
        for h in r["holonomies"]:
            txt_lines.append(
                f"  dec {h['decagon']:2d}: "
                f"H=({h['holonomy_real']:+.6f}{h['holonomy_imag']:+.6f}i) "
                f"|H|={h['abs']:.6f} "
                f"arg={h['phase_angle']:.6f} "
                f"d(+1)={h['distance_to_plus1']:.6f} "
                f"d(-1)={h['distance_to_minus1']:.6f}"
            )
        txt_lines.append("")

    txt_lines.append("INTERPRETATION")
    txt_lines.append("-" * 80)
    txt_lines.append("If mean distance to -1 is much smaller than to +1, the tested")
    txt_lines.append("harmonic sector behaves like a spinorial half-turn around Petrie loops.")
    txt_lines.append("If mean distance to +1 is smaller, the sector is oscillatory but scalar.")
    txt_lines.append("This is a U(1) proxy test; a full SU(2) lift is the next refinement.")
    txt_lines.append("")

    out_txt = OUT_DIR / "decagon_phase_holonomy.txt"
    out_json = OUT_DIR / "decagon_phase_holonomy.json"

    out_txt.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("\n".join(txt_lines))
    print(f"saved {out_txt.relative_to(ROOT)}")
    print(f"saved {out_json.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
