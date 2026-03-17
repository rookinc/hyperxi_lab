from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
OUT_TXT = ROOT / "reports" / "quotients" / "verify_core_sector_symmetry.txt"
OUT_JSON = ROOT / "reports" / "quotients" / "verify_core_sector_symmetry.json"


def build_lp_reference():
    P = nx.petersen_graph()
    L = nx.line_graph(P)

    nodes = sorted(tuple(sorted(x)) for x in L.nodes())
    edge_to_id = {n: i for i, n in enumerate(nodes)}
    id_to_edge = {i: n for i, n in enumerate(nodes)}

    G = nx.Graph()
    G.add_nodes_from(range(len(nodes)))
    for a, b in L.edges():
        ia = edge_to_id[tuple(sorted(a))]
        ib = edge_to_id[tuple(sorted(b))]
        G.add_edge(ia, ib)

    return G, id_to_edge


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


def apply_perm_to_edge(edge: tuple[int, int], perm: dict[int, int]) -> tuple[int, int]:
    u, v = edge
    return tuple(sorted((perm[u], perm[v])))


def apply_perm_to_sector(sector: set[tuple[int, int]], perm: dict[int, int]) -> frozenset[tuple[int, int]]:
    return frozenset(apply_perm_to_edge(e, perm) for e in sector)


def main():
    G, id_to_edge = build_lp_reference()
    sectors = {r: frozenset(transport_sector_edges(G, r)) for r in G.nodes()}
    sector_to_root = {sec: r for r, sec in sectors.items()}

    gm = nx.algorithms.isomorphism.GraphMatcher(G, G)
    automorphisms = list(gm.isomorphisms_iter())

    lines = []
    lines.append("=" * 80)
    lines.append("VERIFY CORE SECTOR SYMMETRY")
    lines.append("=" * 80)
    lines.append("")
    lines.append("CORE SUMMARY")
    lines.append("-" * 80)
    lines.append(f"|V|={G.number_of_nodes()} |E|={G.number_of_edges()}")
    lines.append(f"sector size set: {sorted({len(sectors[r]) for r in sectors})}")
    lines.append(f"automorphism count: {len(automorphisms)}")
    lines.append("")

    all_ok = True
    root_image_hist = defaultdict(int)
    sector_image_hist = defaultdict(int)
    samples = []

    for i, perm in enumerate(automorphisms):
        # test vertex-root equivariance:
        # does perm(T_r) = T_{perm(r)} for all roots?
        ok = True
        for r in G.nodes():
            img_sector = apply_perm_to_sector(sectors[r], perm)
            target_root = perm[r]
            expected_sector = sectors[target_root]
            if img_sector != expected_sector:
                ok = False
                all_ok = False
                samples.append({
                    "automorphism_index": i,
                    "root": r,
                    "perm_root": target_root,
                    "img_sector_size": len(img_sector),
                    "expected_sector_size": len(expected_sector),
                })
                break

        if ok:
            # pick root 0 as sample
            root_image_hist[perm[0]] += 1
            img0 = apply_perm_to_sector(sectors[0], perm)
            sector_image_hist[sector_to_root[img0]] += 1

    lines.append("EQUIVARIANCE TEST")
    lines.append("-" * 80)
    lines.append(f"all automorphisms preserve the sector family equivariantly: {all_ok}")
    lines.append("")

    lines.append("IMAGE DISTRIBUTION OF ROOT 0")
    lines.append("-" * 80)
    for r in sorted(root_image_hist):
        lines.append(f"root 0 -> {r}: {root_image_hist[r]}")
    lines.append("")

    lines.append("IMAGE DISTRIBUTION OF SECTOR T_0")
    lines.append("-" * 80)
    for r in sorted(sector_image_hist):
        lines.append(f"T_0 -> T_{r}: {sector_image_hist[r]}")
    lines.append("")

    if samples:
        lines.append("FIRST FAILURES")
        lines.append("-" * 80)
        for s in samples[:10]:
            lines.append(json.dumps(s))
        lines.append("")

    payload = {
        "automorphism_count": len(automorphisms),
        "equivariant_preservation": all_ok,
        "root0_image_histogram": dict(sorted(root_image_hist.items())),
        "T0_image_histogram": dict(sorted(sector_image_hist.items())),
        "sample_failures": samples[:10],
    }

    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("\n".join(lines))
    print(f"saved {OUT_TXT}")
    print(f"saved {OUT_JSON}")


if __name__ == "__main__":
    main()
