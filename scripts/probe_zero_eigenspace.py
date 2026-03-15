from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

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
        for key in [
            "fibers",
            "fiber_partition",
            "v4_fibers",
            "orbits",
            "blocks",
            "partition",
            "classes",
        ]:
            if key in data and isinstance(data[key], list):
                candidates.append(data[key])

        for _, v in data.items():
            if isinstance(v, dict):
                for kk in [
                    "fibers",
                    "fiber_partition",
                    "v4_fibers",
                    "orbits",
                    "blocks",
                    "partition",
                    "classes",
                ]:
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
        print("no partition JSON found; continuing without fiber analysis")
        return None
    print(f"loading partition from: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    fibers = try_extract_partition(data)
    if fibers is None:
        print("could not recognize 15x4 partition; continuing without fiber analysis")
        return None
    return fibers


def fiber_maps(fibers):
    v2f = {}
    for i, fiber in enumerate(fibers):
        for v in fiber:
            v2f[v] = i
    return v2f


def orthonormal_zero_basis(A: np.ndarray, tol: float = 1e-9):
    eigvals, eigvecs = np.linalg.eigh(A)
    zero_idx = [i for i, lam in enumerate(eigvals) if abs(lam) < tol]
    Z = eigvecs[:, zero_idx]
    return eigvals, Z


def nodal_summary(vec: np.ndarray, eps: float = 1e-8):
    pos = np.sum(vec > eps)
    neg = np.sum(vec < -eps)
    zer = np.sum(np.abs(vec) <= eps)
    return {"pos": int(pos), "neg": int(neg), "zeroish": int(zer)}


def support_summary(vec: np.ndarray, topk: int = 12):
    order = np.argsort(-np.abs(vec))
    return [(int(i), float(vec[i])) for i in order[:topk]]


def fiber_projection(vec: np.ndarray, fibers):
    means = []
    sums = []
    l2s = []
    sign_patterns = []
    for fiber in fibers:
        vals = np.array([vec[v] for v in fiber], dtype=float)
        means.append(float(np.mean(vals)))
        sums.append(float(np.sum(vals)))
        l2s.append(float(np.linalg.norm(vals)))
        signs = tuple(int(np.sign(v)) if abs(v) > 1e-8 else 0 for v in vals)
        sign_patterns.append(signs)
    return {
        "means": means,
        "sums": sums,
        "l2s": l2s,
        "sign_patterns": sign_patterns,
    }


def core_vector_from_fibers(vec: np.ndarray, fibers):
    return np.array([np.sum([vec[v] for v in fiber]) for fiber in fibers], dtype=float)


def analyze_zero_basis(G: nx.Graph, Z: np.ndarray, fibers=None):
    print(f"\nzero eigenspace dimension = {Z.shape[1]}")

    rows = []

    for j in range(Z.shape[1]):
        vec = Z[:, j].copy()

        # normalize sign for stable display
        idx = int(np.argmax(np.abs(vec)))
        if vec[idx] < 0:
            vec = -vec

        row = {
            "basis_index": j,
            "norm": float(np.linalg.norm(vec)),
            "nodal": nodal_summary(vec),
            "top_support": support_summary(vec),
        }

        if fibers is not None:
            proj = fiber_projection(vec, fibers)
            core = core_vector_from_fibers(vec, fibers)

            row["fiber_sum_l2"] = float(np.linalg.norm(proj["sums"]))
            row["fiber_mean_l2"] = float(np.linalg.norm(proj["means"]))
            row["core_support_count"] = int(np.sum(np.abs(core) > 1e-8))
            row["zero_on_each_fiber"] = bool(np.all(np.abs(core) <= 1e-8))

            pattern_counts = Counter(proj["sign_patterns"])
            row["fiber_sign_pattern_counts"] = {
                str(k): int(v) for k, v in pattern_counts.most_common()
            }
            row["fiber_sums"] = [float(x) for x in proj["sums"]]
            row["core_vector"] = [float(x) for x in core]

        rows.append(row)

    return rows


def summarize_rows(rows, fibers_present: bool):
    print("\nBasis summaries")
    print("----------------")
    for row in rows:
        j = row["basis_index"]
        nodal = row["nodal"]
        print(
            f"basis {j:2d}: "
            f"pos={nodal['pos']:2d} neg={nodal['neg']:2d} zeroish={nodal['zeroish']:2d}"
        )
        if fibers_present:
            print(
                f"          fiber_sum_l2={row['fiber_sum_l2']:.6g} "
                f"core_support={row['core_support_count']:2d} "
                f"zero_on_each_fiber={row['zero_on_each_fiber']}"
            )
        print(f"          top support: {row['top_support'][:6]}")

    if fibers_present:
        zero_each = sum(1 for r in rows if r["zero_on_each_fiber"])
        print(f"\nzero modes with exact zero sum on every fiber: {zero_each} / {len(rows)}")

        best = sorted(rows, key=lambda r: r["fiber_sum_l2"])
        print("\nmost fiber-internal basis vectors:")
        for r in best[:5]:
            print(
                f"  basis {r['basis_index']}: fiber_sum_l2={r['fiber_sum_l2']:.6g}, "
                f"core_support={r['core_support_count']}"
            )

        worst = sorted(rows, key=lambda r: r["fiber_sum_l2"], reverse=True)
        print("\nmost core-visible basis vectors:")
        for r in worst[:5]:
            print(
                f"  basis {r['basis_index']}: fiber_sum_l2={r['fiber_sum_l2']:.6g}, "
                f"core_support={r['core_support_count']}"
            )


def save_report(eigvals, rows):
    out = {
        "zero_eigenvalue_multiplicity": len([x for x in eigvals if abs(x) < 1e-9]),
        "basis": rows,
    }
    out_path = ROOT / "reports" / "probe_zero_eigenspace.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nsaved {out_path}")


def main():
    G = load_g60()
    fibers = load_partition()

    A = nx.to_numpy_array(G, dtype=float)
    eigvals, Z = orthonormal_zero_basis(A)

    rows = analyze_zero_basis(G, Z, fibers=fibers)
    summarize_rows(rows, fibers_present=(fibers is not None))
    save_report(eigvals, rows)


if __name__ == "__main__":
    main()
