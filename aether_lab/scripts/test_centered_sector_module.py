from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT_TXT = ROOT / "reports" / "quotients" / "test_centered_sector_module.txt"
OUT_JSON = ROOT / "reports" / "quotients" / "test_centered_sector_module.json"


def build_lp_reference():
    P = nx.petersen_graph()
    L = nx.line_graph(P)

    nodes = sorted(tuple(sorted(x)) for x in L.nodes())
    edge_to_id = {n: i for i, n in enumerate(nodes)}

    G = nx.Graph()
    G.add_nodes_from(range(len(nodes)))
    for a, b in L.edges():
        ia = edge_to_id[tuple(sorted(a))]
        ib = edge_to_id[tuple(sorted(b))]
        G.add_edge(ia, ib)

    return G


def rooted_orientation(G: nx.Graph, root: int) -> nx.DiGraph:
    D = nx.DiGraph()
    D.add_nodes_from(G.nodes())
    dist = nx.single_source_shortest_path_length(G, root)

    for u, v in G.edges():
        du = dist[u]
        dv = dist[v]

        if du == 0 and dv == 1:
            D.add_edge(u, v)
        elif dv == 0 and du == 1:
            D.add_edge(v, u)
        elif du == 1 and dv == 1:
            a, b = sorted((u, v))
            D.add_edge(a, b)
        elif du == 1 and dv == 2:
            D.add_edge(u, v)
        elif dv == 1 and du == 2:
            D.add_edge(v, u)

    return D


def transport_sector_edges(G: nx.Graph, root: int) -> set[tuple[int, int]]:
    D = rooted_orientation(G, root)
    reached = {root: 0}
    frontier = [root]

    while frontier:
        nxt = []
        for u in frontier:
            if reached[u] == 2:
                continue
            for v in D.successors(u):
                if v not in reached:
                    reached[v] = reached[u] + 1
                    nxt.append(v)
        frontier = nxt

    edges = set()
    for u in reached:
        if reached[u] == 2:
            continue
        for v in D.successors(u):
            if v in reached and reached[v] <= 2:
                edges.add(tuple(sorted((u, v))))
    return edges


def eig_groups(vals, tol=1e-9):
    vals = sorted(float(v) for v in vals)
    groups = []
    for v in vals:
        if not groups or abs(v - groups[-1][0]) > tol:
            groups.append([v, 1])
        else:
            groups[-1][1] += 1
    return [(round(v, 10), m) for v, m in groups]


def main():
    G = build_lp_reference()
    roots = list(G.nodes())
    core_edges = sorted(tuple(sorted(e)) for e in G.edges())
    edge_index = {e: i for i, e in enumerate(core_edges)}

    sectors = {r: transport_sector_edges(G, r) for r in roots}

    M = np.zeros((len(roots), len(core_edges)), dtype=float)
    for r in roots:
        for e in sectors[r]:
            M[r, edge_index[e]] = 1.0

    A = nx.to_numpy_array(G, nodelist=roots, dtype=float)

    # Centered incidence matrix
    mean = 7.0 / 15.0
    Mc = M - mean * np.ones_like(M)

    Gc = Mc @ Mc.T

    # Spectra
    A_vals, A_vecs = np.linalg.eigh(A)
    Gc_vals, Gc_vecs = np.linalg.eigh(Gc)

    # Rank checks
    rank_M = int(np.linalg.matrix_rank(M))
    rank_Mc = int(np.linalg.matrix_rank(Mc))

    # Test whether all centered rows sum to zero
    centered_row_sums = Mc.sum(axis=1)

    # Project the row-space basis of Mc onto eigenspaces of A
    # We look at how the row Gram eigenvectors align with A-eigenspaces.
    eigspace_dims = {}
    for lam in sorted(set(round(float(x), 10) for x in A_vals)):
        eigspace_dims[str(lam)] = int(sum(abs(round(float(x), 10) - lam) < 1e-9 for x in A_vals))

    # Basis for row-space of Mc via SVD
    U, S, Vt = np.linalg.svd(Mc, full_matrices=False)
    rowspace_basis = U[:, S > 1e-9]

    # For each adjacency eigenspace, compute projected dimension
    adjacency_eigenspace_projected_dims = {}
    for lam in sorted(set(round(float(x), 10) for x in A_vals)):
        mask = np.array([abs(round(float(x), 10) - lam) < 1e-9 for x in A_vals])
        E = A_vecs[:, mask]
        # Project row-space basis into this eigenspace
        proj = E @ (E.T @ rowspace_basis)
        dim = np.linalg.matrix_rank(proj, tol=1e-8)
        adjacency_eigenspace_projected_dims[str(lam)] = int(dim)

    lines = []
    lines.append("=" * 80)
    lines.append("TEST CENTERED SECTOR MODULE")
    lines.append("=" * 80)
    lines.append("")
    lines.append("BASIC DATA")
    lines.append("-" * 80)
    lines.append(f"M shape: {M.shape}")
    lines.append(f"rank(M): {rank_M}")
    lines.append(f"rank(M_centered): {rank_Mc}")
    lines.append(f"center value used: {mean}")
    lines.append("")
    lines.append("CENTERED ROW SUMS")
    lines.append("-" * 80)
    lines.append(" ".join(f"{x:.10f}" for x in centered_row_sums))
    lines.append("")
    lines.append("SPECTRUM OF A")
    lines.append("-" * 80)
    for val, mult in eig_groups(A_vals):
        lines.append(f"{val}: mult {mult}")
    lines.append("")
    lines.append("SPECTRUM OF M_centered M_centered^T")
    lines.append("-" * 80)
    for val, mult in eig_groups(Gc_vals):
        lines.append(f"{val}: mult {mult}")
    lines.append("")
    lines.append("PROJECTED ROW-SPACE DIMENSIONS INSIDE A-EIGENSPACES")
    lines.append("-" * 80)
    for lam, dim in adjacency_eigenspace_projected_dims.items():
        lines.append(f"eigenvalue {lam}: projected dim {dim}")
    lines.append("")

    payload = {
        "rank_M": rank_M,
        "rank_M_centered": rank_Mc,
        "center_value": mean,
        "centered_row_sums": [float(x) for x in centered_row_sums],
        "A_spectrum": [{"value": v, "mult": m} for v, m in eig_groups(A_vals)],
        "McMcT_spectrum": [{"value": v, "mult": m} for v, m in eig_groups(Gc_vals)],
        "adjacency_eigenspace_projected_dims": adjacency_eigenspace_projected_dims,
    }

    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("\n".join(lines))
    print(f"saved {OUT_TXT}")
    print(f"saved {OUT_JSON}")


if __name__ == "__main__":
    main()
