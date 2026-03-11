from __future__ import annotations

import math
from collections import Counter, defaultdict
from itertools import combinations

import networkx as nx
import numpy as np


# ============================================================
# Canonical candidates
# ============================================================

def build_base_graph() -> nx.Graph:
    """
    30-vertex candidate:
      line graph of the dodecahedral graph
    """
    G0 = nx.dodecahedral_graph()
    G = nx.line_graph(G0)
    return nx.convert_node_labels_to_integers(G, ordering="sorted")


def build_quotient_graph() -> nx.Graph:
    """
    15-vertex candidate:
      line graph of the Petersen graph
    """
    G0 = nx.petersen_graph()
    G = nx.line_graph(G0)
    return nx.convert_node_labels_to_integers(G, ordering="sorted")


# ============================================================
# Basic helpers
# ============================================================

def adjacency_matrix_int(G: nx.Graph) -> np.ndarray:
    return nx.to_numpy_array(G, dtype=np.int64)


def shell_profile(G: nx.Graph, root: int) -> tuple[int, ...]:
    d = nx.single_source_shortest_path_length(G, root)
    maxdist = max(d.values())
    return tuple(sum(1 for v in G if d[v] == i) for i in range(maxdist + 1))


def all_shell_profiles(G: nx.Graph) -> dict[int, tuple[int, ...]]:
    return {v: shell_profile(G, v) for v in G.nodes()}


def wl_vertex_colors(G: nx.Graph) -> dict[int, int]:
    """
    Simple 1-dimensional Weisfeiler-Lehman refinement.
    """
    colors = {v: G.degree[v] for v in G.nodes()}
    while True:
        sigs = {}
        for v in G.nodes():
            nbr_colors = tuple(sorted(colors[u] for u in G.neighbors(v)))
            sigs[v] = (colors[v], nbr_colors)
        uniq = {sig: i for i, sig in enumerate(sorted(set(sigs.values())))}
        new_colors = {v: uniq[sigs[v]] for v in G.nodes()}
        if new_colors == colors:
            break
        colors = new_colors
    return colors


def rooted_closed_walk_signature(G: nx.Graph, kmax: int = 10) -> dict[int, tuple[int, ...]]:
    A = adjacency_matrix_int(G)
    n = A.shape[0]
    Ak = np.eye(n, dtype=object)
    out = {i: [] for i in range(n)}
    for _k in range(1, kmax + 1):
        Ak = Ak @ A
        diag = np.diag(Ak)
        for i in range(n):
            out[i].append(int(diag[i]))
    return {i: tuple(vals) for i, vals in out.items()}


def graph_spectrum(G: nx.Graph, tol: float = 1e-8) -> list[tuple[float, int]]:
    A = nx.to_numpy_array(G, dtype=float)
    vals = np.linalg.eigvalsh(A)
    vals = np.round(vals, 6)
    counts = Counter(vals.tolist())
    return sorted(((ev, mult) for ev, mult in counts.items()), key=lambda x: -x[0])


def walk_traces(G: nx.Graph, kmax: int = 10) -> list[int]:
    A = adjacency_matrix_int(G)
    Ak = np.eye(A.shape[0], dtype=object)
    traces = []
    for _k in range(1, kmax + 1):
        Ak = Ak @ A
        traces.append(int(np.trace(Ak)))
    return traces


def triangles_of_graph(G: nx.Graph) -> list[tuple[int, int, int]]:
    tris = set()
    for u in G.nodes():
        Nu = set(G.neighbors(u))
        for v in Nu:
            if v <= u:
                continue
            common = Nu & set(G.neighbors(v))
            for w in common:
                if w <= v:
                    continue
                tris.add(tuple(sorted((u, v, w))))
    return sorted(tris)


def common_neighbor_profiles(G: nx.Graph) -> dict[str, Counter]:
    adj = Counter()
    nonadj = Counter()
    by_distance = defaultdict(Counter)

    dist = dict(nx.all_pairs_shortest_path_length(G))

    for u, v in combinations(G.nodes(), 2):
        c = len(list(nx.common_neighbors(G, u, v)))
        if G.has_edge(u, v):
            adj[c] += 1
        else:
            nonadj[c] += 1
        by_distance[dist[u][v]][c] += 1

    return {
        "adjacent": adj,
        "nonadjacent": nonadj,
        "by_distance": by_distance,
    }


def vertex_signature_classes(G: nx.Graph) -> dict[tuple, list[int]]:
    shells = all_shell_profiles(G)
    wl = wl_vertex_colors(G)
    rw = rooted_closed_walk_signature(G, kmax=10)

    classes = defaultdict(list)
    for v in G.nodes():
        sig = (
            shells[v],
            wl[v],
            rw[v],
        )
        classes[sig].append(v)
    return dict(classes)


def edge_signature_classes(G: nx.Graph) -> dict[tuple, list[tuple[int, int]]]:
    shells = all_shell_profiles(G)
    wl = wl_vertex_colors(G)

    classes = defaultdict(list)
    for u, v in G.edges():
        cn = len(list(nx.common_neighbors(G, u, v)))
        sig = (
            tuple(sorted((wl[u], wl[v]))),
            tuple(sorted((shells[u], shells[v]))),
            cn,
        )
        classes[sig].append(tuple(sorted((u, v))))
    return dict(classes)


def triangle_signature_classes(G: nx.Graph) -> dict[tuple, list[tuple[int, int, int]]]:
    shells = all_shell_profiles(G)
    wl = wl_vertex_colors(G)

    classes = defaultdict(list)
    for tri in triangles_of_graph(G):
        u, v, w = tri
        edge_cn = []
        for a, b in ((u, v), (u, w), (v, w)):
            edge_cn.append(len(list(nx.common_neighbors(G, a, b))))
        sig = (
            tuple(sorted((wl[u], wl[v], wl[w]))),
            tuple(sorted((shells[u], shells[v], shells[w]))),
            tuple(sorted(edge_cn)),
        )
        classes[sig].append(tri)
    return dict(classes)


def shell_classes(G: nx.Graph) -> dict[tuple[int, ...], list[int]]:
    out = defaultdict(list)
    for v, shp in all_shell_profiles(G).items():
        out[shp].append(v)
    return dict(out)


def print_counter(counter: Counter, indent: str = "  ") -> None:
    for k in sorted(counter):
        print(f"{indent}{k}: {counter[k]}")


def summarize_graph(name: str, G: nx.Graph) -> None:
    print("=" * 80)
    print(name.upper())
    print("=" * 80)

    n = G.number_of_nodes()
    m = G.number_of_edges()
    degrees = sorted(set(dict(G.degree()).values()))
    diam = nx.diameter(G)
    tri_count = sum(nx.triangles(G).values()) // 3

    print(f"vertices: {n}")
    print(f"edges: {m}")
    print(f"degree set: {degrees}")
    print(f"diameter: {diam}")
    print(f"triangles: {tri_count}")
    print()

    print("shell classes:")
    sc = shell_classes(G)
    for shp, verts in sorted(sc.items(), key=lambda x: (len(x[0]), x[0])):
        print(f"  {shp}  x{len(verts)}")
    print()

    vclasses = vertex_signature_classes(G)
    eclasses = edge_signature_classes(G)
    tclasses = triangle_signature_classes(G)

    print(f"vertex-signature classes: {len(vclasses)}")
    for i, (_sig, verts) in enumerate(sorted(vclasses.items(), key=lambda x: (len(x[1]), x[0])), 1):
        print(f"  class {i}: size={len(verts)}")
    print()

    print(f"edge-signature classes: {len(eclasses)}")
    for i, (_sig, edges) in enumerate(sorted(eclasses.items(), key=lambda x: (len(x[1]), x[0])), 1):
        print(f"  class {i}: size={len(edges)}")
    print()

    print(f"triangle-signature classes: {len(tclasses)}")
    for i, (_sig, tris) in enumerate(sorted(tclasses.items(), key=lambda x: (len(x[1]), x[0])), 1):
        print(f"  class {i}: size={len(tris)}")
    print()

    print("common-neighbor profile (adjacent pairs):")
    cnp = common_neighbor_profiles(G)
    print_counter(cnp["adjacent"])
    print()

    print("common-neighbor profile (nonadjacent pairs):")
    print_counter(cnp["nonadjacent"])
    print()

    print("common-neighbor profile by distance:")
    for d in sorted(cnp["by_distance"]):
        print(f"  distance {d}:")
        print_counter(cnp["by_distance"][d], indent="    ")
    print()

    print("spectrum:")
    for ev, mult in graph_spectrum(G):
        print(f"  {ev:g} x{mult}")
    print()

    print("walk traces:")
    traces = walk_traces(G, kmax=10)
    for k, tr in enumerate(traces, 1):
        print(f"  tr(A^{k}) = {tr}")
    print()


def known_family_checks(base: nx.Graph, quotient: nx.Graph) -> None:
    print("=" * 80)
    print("KNOWN FAMILY CHECKS")
    print("=" * 80)

    dodec_line = nx.convert_node_labels_to_integers(
        nx.line_graph(nx.dodecahedral_graph()),
        ordering="sorted",
    )
    petersen_line = nx.convert_node_labels_to_integers(
        nx.line_graph(nx.petersen_graph()),
        ordering="sorted",
    )

    gm_base = nx.is_isomorphic(base, dodec_line)
    gm_quot = nx.is_isomorphic(quotient, petersen_line)

    print(f"base graph isomorphic to line_graph(dodecahedral_graph): {gm_base}")
    print(f"quotient graph isomorphic to line_graph(petersen_graph): {gm_quot}")
    print()

    if gm_base:
        print("Interpretation: the 30-vertex base graph is the line graph of the dodecahedron.")
    if gm_quot:
        print("Interpretation: the 15-vertex quotient graph is the line graph of the Petersen graph.")
    print()


def cover_check(base: nx.Graph, quotient: nx.Graph) -> None:
    """
    This is not a full generic regular-cover proof.
    It simply reports the structural relationship expected from:
      L(dodecahedron) -> L(Petersen)
    """
    print("=" * 80)
    print("COVER INTERPRETATION")
    print("=" * 80)
    print("Expected structural picture:")
    print("  dodecahedral graph  --(2-cover)-->  Petersen graph")
    print("  line graph thereof  --(2-cover)-->  line graph thereof")
    print()
    print("So if the family checks above pass, the 30-vertex base graph is the natural")
    print("2-cover of the 15-vertex quotient graph induced by the antipodal cover")
    print("dodecahedron -> Petersen.")
    print()


def main() -> None:
    base = build_base_graph()
    quotient = build_quotient_graph()

    summarize_graph("30-vertex base graph", base)
    summarize_graph("15-vertex quotient graph", quotient)
    known_family_checks(base, quotient)
    cover_check(base, quotient)


if __name__ == "__main__":
    main()
