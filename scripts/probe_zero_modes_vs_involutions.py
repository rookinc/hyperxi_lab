from __future__ import annotations

import json
from pathlib import Path
from collections import Counter

import numpy as np
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]

G60_CANDIDATES = [
    ROOT / "reports" / "true_quotients" / "true_chamber_graph.g6",
    ROOT / "artifacts" / "census" / "thalean_graph.g6",
]

PARTITION_CANDIDATES = [
    ROOT / "reports" / "true_quotients" / "compare_v4_quotient_to_canonical_dodecahedral_15core.json",
    ROOT / "reports" / "true_quotients" / "export_v4_cover_certificate.json",
]

AUT_TXT_CANDIDATES = [
    ROOT / "notes" / "thalean_s5_symmetry.md",
    ROOT / "reports" / "automorphisms" / "probe_antipode_automorphisms.txt",
    ROOT / "reports" / "pairs" / "thalean_antipode_check.txt",
    ROOT / "reports" / "pairs" / "thalean_antipode_vs_sheet.txt",
]

def find_existing(paths):
    for p in paths:
        if p.exists():
            return p
    return None

def load_g60() -> nx.Graph:
    path = find_existing(G60_CANDIDATES)
    if path is None:
        raise FileNotFoundError("Could not find G60 .g6 file.")
    print(f"loading G60 from: {path}")
    G = nx.read_graph6(path)
    print(f"G60: |V|={G.number_of_nodes()} |E|={G.number_of_edges()}")
    return G

def try_extract_partition(data):
    candidates = []

    if isinstance(data, dict):
        for key in ["fibers", "fiber_partition", "v4_fibers", "orbits", "blocks", "partition", "classes"]:
            if key in data and isinstance(data[key], list):
                candidates.append(data[key])
        for _, v in data.items():
            if isinstance(v, dict):
                for kk in ["fibers", "fiber_partition", "v4_fibers", "orbits", "blocks", "partition", "classes"]:
                    if kk in v and isinstance(v[kk], list):
                        candidates.append(v[kk])
    elif isinstance(data, list):
        candidates.append(data)

    for cand in candidates:
        if len(cand) == 15 and all(isinstance(x, list) and len(x) == 4 for x in cand):
            return cand
    return None

def load_partition():
    path = find_existing(PARTITION_CANDIDATES)
    if path is None:
        return None
    print(f"loading partition from: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    fibers = try_extract_partition(data)
    return fibers

def orthonormal_zero_basis(A: np.ndarray, tol: float = 1e-9):
    eigvals, eigvecs = np.linalg.eigh(A)
    zero_idx = [i for i, lam in enumerate(eigvals) if abs(lam) < tol]
    return eigvals, eigvecs[:, zero_idx]

def permutation_matrix_from_map(mapping: dict[int, int], n: int) -> np.ndarray:
    P = np.zeros((n, n), dtype=float)
    for i in range(n):
        P[mapping[i], i] = 1.0
    return P

def find_aut_from_pairing(G: nx.Graph, pairing: list[tuple[int, int]]):
    """
    Build an involution from explicit pairs plus fixed points if any.
    Verify automorphism.
    """
    mapping = {i: i for i in G.nodes()}
    for a, b in pairing:
        mapping[a] = b
        mapping[b] = a
    H = nx.relabel_nodes(G, mapping, copy=True)
    if nx.is_isomorphic(G, H, node_match=None, edge_match=None):
        # This only checks graph iso, not that mapping itself preserves edges.
        ok = True
        for u, v in G.edges():
            mu, mv = mapping[u], mapping[v]
            if not G.has_edge(mu, mv):
                ok = False
                break
        if ok:
            return mapping
    return None

def candidate_pairs_from_zero_report(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    counts = Counter()
    for row in data.get("basis", []):
        tops = row.get("top_support", [])
        # look at strongest few entries; collect pair co-occurrence heuristic
        inds = [int(t[0]) for t in tops[:6]]
        for i in range(0, len(inds)-1, 2):
            a, b = sorted((inds[i], inds[i+1]))
            counts[(a, b)] += 1
    return counts

def build_candidate_involutions(G: nx.Graph, fibers):
    cands = {}

    # 1) within-fiber swaps, all 3 nontrivial perfect matchings per 4-set
    if fibers is not None:
        def add_mapping(name, pairing):
            mapping = {i: i for i in G.nodes()}
            for a, b in pairing:
                mapping[a] = b
                mapping[b] = a
            ok = True
            for u, v in G.edges():
                if not G.has_edge(mapping[u], mapping[v]):
                    ok = False
                    break
            if ok:
                cands[name] = mapping

        # three canonical pairings on each 4-fiber in listed order
        pairings = {
            "fiber_swap_01_23": lambda f: [(f[0], f[1]), (f[2], f[3])],
            "fiber_swap_02_13": lambda f: [(f[0], f[2]), (f[1], f[3])],
            "fiber_swap_03_12": lambda f: [(f[0], f[3]), (f[1], f[2])],
        }
        for name, fn in pairings.items():
            pairing = []
            for fiber in fibers:
                pairing.extend(fn(fiber))
            add_mapping(name, pairing)

    # 2) heuristic pairing from zero-mode dominant entries
    zero_report = ROOT / "reports" / "probe_zero_eigenspace.json"
    if zero_report.exists():
        counts = candidate_pairs_from_zero_report(zero_report)
        strong = [p for p, c in counts.items() if c >= 2]
        used = set()
        pairing = []
        for a, b in strong:
            if a in used or b in used:
                continue
            pairing.append((a, b))
            used.add(a)
            used.add(b)
        if pairing:
            mapping = find_aut_from_pairing(G, pairing)
            if mapping is not None:
                cands["zero_support_pairing"] = mapping

    return cands

def analyze_involution_on_zero_space(Z: np.ndarray, mapping: dict[int, int]):
    n = Z.shape[0]
    P = permutation_matrix_from_map(mapping, n)

    # action on zero space
    M = Z.T @ P @ Z
    evals, _ = np.linalg.eigh(M)

    # measure closeness to involution eigenvalues ±1
    near_plus = int(np.sum(np.abs(evals - 1) < 1e-6))
    near_minus = int(np.sum(np.abs(evals + 1) < 1e-6))

    # per-basis overlaps
    overlaps = []
    for j in range(Z.shape[1]):
        v = Z[:, j]
        Pv = P @ v
        overlaps.append(float(v @ Pv))

    return {
        "matrix_on_zero_space": M.tolist(),
        "eigenvalues_on_zero_space": [float(x) for x in evals],
        "near_plus_1": near_plus,
        "near_minus_1": near_minus,
        "basis_self_overlaps": overlaps,
    }

def main():
    G = load_g60()
    fibers = load_partition()

    A = nx.to_numpy_array(G, dtype=float)
    eigvals, Z = orthonormal_zero_basis(A)
    print(f"zero eigenspace dimension = {Z.shape[1]}")

    cands = build_candidate_involutions(G, fibers)
    print(f"\nfound {len(cands)} candidate involutions")
    for name in cands:
        print(" ", name)

    out = {}
    for name, mapping in cands.items():
        print(f"\n=== testing {name} ===")
        rep = analyze_involution_on_zero_space(Z, mapping)
        print("eigenvalues on zero space:")
        print(" ", [round(x, 6) for x in rep["eigenvalues_on_zero_space"]])
        print(f"near +1: {rep['near_plus_1']}   near -1: {rep['near_minus_1']}")
        print("basis self-overlaps:")
        print(" ", [round(x, 6) for x in rep["basis_self_overlaps"]])
        out[name] = rep

    out_path = ROOT / "reports" / "probe_zero_modes_vs_involutions.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nsaved {out_path}")

if __name__ == "__main__":
    main()
