from __future__ import annotations

from collections import Counter, defaultdict, deque
from typing import Dict, Set, Tuple

import numpy as np

from vertex_connection_model import measured_graph_reindexed
from reconstruct_vertex_connection import pair_to_edge_sheet


def bfs_distances(adj, s):
    dist = {s: 0}
    q = deque([s])
    while q:
        v = q.popleft()
        for w in adj[v]:
            if w not in dist:
                dist[w] = dist[v] + 1
                q.append(w)
    return dist


def all_distances(adj):
    return {v: bfs_distances(adj, v) for v in adj}


def edge_set(adj):
    out = set()
    for u in adj:
        for v in adj[u]:
            if u < v:
                out.add((u, v))
    return out


def triangle_count(adj):
    total = 0
    for a in sorted(adj):
        for b in [x for x in adj[a] if x > a]:
            common = adj[a] & adj[b]
            for c in [x for x in common if x > b]:
                total += 1
    return total


def adjacency_matrix(adj):
    nodes = sorted(adj)
    idx = {v: i for i, v in enumerate(nodes)}
    A = np.zeros((len(nodes), len(nodes)), dtype=int)
    for v in nodes:
        for w in adj[v]:
            A[idx[v], idx[w]] = 1
    return A


def eigen_mults(adj):
    vals = np.linalg.eigvals(adjacency_matrix(adj))
    vals = [round(float(np.real_if_close(v)), 6) for v in vals]
    return Counter(vals)


def shell_classes(adj):
    dist = all_distances(adj)
    sigs = {}
    for v in adj:
        c = Counter(dist[v].values())
        sigs[v] = tuple(c[k] for k in sorted(c))
    return Counter(sigs.values())


def build_base_data():
    """
    Returns:
      edges30: list of 30 base edges
      chamber_meta: node -> (base_edge, sheet)
      cover_fibers: base_edge -> [two chamber nodes]
    """
    p2es = pair_to_edge_sheet()
    edges30 = sorted({e for e, _ in p2es.values()})
    edge_to_idx = {e: i for i, e in enumerate(edges30)}

    chamber_meta = {}
    cover_fibers = defaultdict(list)

    for pair_id, (e, s) in p2es.items():
        node = 2 * edge_to_idx[e] + s
        chamber_meta[node] = (e, s)
        cover_fibers[e].append(node)

    for e in cover_fibers:
        cover_fibers[e] = sorted(cover_fibers[e])

    return edges30, chamber_meta, dict(cover_fibers)


def build_line_graph_icosahedron(edges30):
    """
    30-vertex line graph of the icosahedron:
      vertices = icosahedron edges
      adjacency = share one endpoint
    """
    adj = {e: set() for e in edges30}
    for a in edges30:
        sa = set(a)
        for b in edges30:
            if a == b:
                continue
            if len(sa & set(b)) == 1:
                adj[a].add(b)
    return adj


def chamber_cover_quotient(chamber_adj, chamber_meta):
    """
    Quotient chamber graph by forgetting the sheet bit:
      60 chamber states -> 30 base edges
    """
    qadj = defaultdict(set)
    for u in chamber_adj:
        eu, _ = chamber_meta[u]
        for v in chamber_adj[u]:
            ev, _ = chamber_meta[v]
            if eu != ev:
                qadj[eu].add(ev)
                qadj[ev].add(eu)
    return {k: set(v) for k, v in qadj.items()}


def check_regular_cover(chamber_adj, chamber_meta, base_adj):
    """
    For each chamber node x over base edge e, compare its neighbors over each
    adjacent base vertex f in base_adj[e]. In a 2-cover, for each adjacent
    base vertex there should be exactly one lifted neighbor over that fiber.
    """
    ok = True
    bad = []

    for x in sorted(chamber_adj):
        ex, sx = chamber_meta[x]
        projected = defaultdict(list)
        for y in chamber_adj[x]:
            ey, sy = chamber_meta[y]
            if ey != ex:
                projected[ey].append(y)

        if set(projected) != set(base_adj[ex]):
            ok = False
            bad.append(("missing-or-extra-base-neighbors", x, ex, sorted(projected), sorted(base_adj[ex])))
            if len(bad) >= 10:
                break

        for ey in base_adj[ex]:
            if len(projected[ey]) != 1:
                ok = False
                bad.append(("fiber-multiplicity", x, ex, ey, len(projected[ey]), projected[ey]))
                if len(bad) >= 10:
                    break
        if len(bad) >= 10:
            break

    return ok, bad


def opposition_matching_on_base(chamber_adj, chamber_meta):
    """
    Recover the 15 opposition pairs from the chamber distance-5 (4,4) relation.
    """
    dist = all_distances(chamber_adj)
    rel = defaultdict(set)

    for x in chamber_adj:
        for y in chamber_adj:
            if x >= y:
                continue
            if dist[x][y] != 5:
                continue
            counts = Counter(dist[x][z] for z in chamber_adj[y])
            prof = tuple(sorted((k, counts[k]) for k in counts))
            if prof == ((4, 4),):
                rel[x].add(y)
                rel[y].add(x)

    seen = set()
    pairs = []
    for v in sorted(rel):
        if v in seen:
            continue
        stack = [v]
        comp = []
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.append(x)
            stack.extend(rel[x])

        base_edges = sorted({chamber_meta[x][0] for x in comp})
        if len(base_edges) == 2:
            pairs.append(tuple(base_edges))

    return sorted(pairs)


def quotient_by_opposition(base_adj, opposition_pairs):
    orbit_of = {}
    for e, f in opposition_pairs:
        orb = tuple(sorted((e, f)))
        orbit_of[e] = orb
        orbit_of[f] = orb

    qadj = defaultdict(set)
    for e in base_adj:
        E = orbit_of[e]
        for f in base_adj[e]:
            F = orbit_of[f]
            if E != F:
                qadj[E].add(F)
                qadj[F].add(E)

    return {k: set(v) for k, v in qadj.items()}


def srg_parameters(adj):
    """
    If strongly regular, returns (v,k,lambda,mu). Otherwise returns None with profiles.
    """
    nodes = sorted(adj)
    v = len(nodes)
    degs = {len(adj[x]) for x in nodes}
    if len(degs) != 1:
        return None, {"degree_set": sorted(degs)}
    k = next(iter(degs))

    lambda_vals = Counter()
    mu_vals = Counter()
    for i, x in enumerate(nodes):
        for y in nodes[i + 1:]:
            c = len(adj[x] & adj[y])
            if y in adj[x]:
                lambda_vals[c] += 1
            else:
                mu_vals[c] += 1

    if len(lambda_vals) == 1 and len(mu_vals) == 1:
        lam = next(iter(lambda_vals))
        mu = next(iter(mu_vals))
        return (v, k, lam, mu), None

    return None, {"lambda_profile": dict(lambda_vals), "mu_profile": dict(mu_vals)}


def main():
    chamber_adj = measured_graph_reindexed()
    edges30, chamber_meta, cover_fibers = build_base_data()
    line30 = build_line_graph_icosahedron(edges30)
    quot30 = chamber_cover_quotient(chamber_adj, chamber_meta)

    print("=" * 80)
    print("COVER AND BASE IDENTIFICATION CHECK")
    print("=" * 80)

    print("30-vertex quotient from chamber graph")
    print("-" * 80)
    print(f"vertices: {len(quot30)}")
    print(f"edges: {len(edge_set(quot30))}")
    print(f"degree set: {sorted({len(quot30[v]) for v in quot30})}")
    print(f"triangles: {triangle_count(quot30)}")
    print(f"shell classes: {dict(shell_classes(quot30))}")
    print("eigenvalue multiplicities:")
    for val, mult in sorted(eigen_mults(quot30).items()):
        print(f"  {val:>10}: {mult}")
    print()

    print("30-vertex line graph of the icosahedron")
    print("-" * 80)
    print(f"vertices: {len(line30)}")
    print(f"edges: {len(edge_set(line30))}")
    print(f"degree set: {sorted({len(line30[v]) for v in line30})}")
    print(f"triangles: {triangle_count(line30)}")
    print(f"shell classes: {dict(shell_classes(line30))}")
    print("eigenvalue multiplicities:")
    for val, mult in sorted(eigen_mults(line30).items()):
        print(f"  {val:>10}: {mult}")
    print()

    same_edge_set = edge_set(quot30) == edge_set(line30)
    print("quotient equals line graph of icosahedron:", same_edge_set)
    if not same_edge_set:
        only_q = sorted(edge_set(quot30) - edge_set(line30))[:10]
        only_l = sorted(edge_set(line30) - edge_set(quot30))[:10]
        print("first quotient-only edges:", only_q)
        print("first line-graph-only edges:", only_l)
    print()

    cover_ok, cover_bad = check_regular_cover(chamber_adj, chamber_meta, quot30)
    print("regular 2-cover check (60 -> 30):", cover_ok)
    if not cover_ok:
        print("first cover issues:")
        for item in cover_bad:
            print(" ", item)
    print()

    opposition_pairs = opposition_matching_on_base(chamber_adj, chamber_meta)
    q15 = quotient_by_opposition(quot30, opposition_pairs)

    print("15-vertex opposition quotient")
    print("-" * 80)
    print(f"vertices: {len(q15)}")
    print(f"edges: {len(edge_set(q15))}")
    print(f"degree set: {sorted({len(q15[v]) for v in q15})}")
    print(f"triangles: {triangle_count(q15)}")
    print(f"shell classes: {dict(shell_classes(q15))}")
    print("eigenvalue multiplicities:")
    for val, mult in sorted(eigen_mults(q15).items()):
        print(f"  {val:>10}: {mult}")

    params, extra = srg_parameters(q15)
    print()
    if params is not None:
        print("strongly regular identification:", params)
    else:
        print("not strongly regular from common-neighbor test")
        print(extra)

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("If the 30-vertex quotient equals the line graph of the icosahedron")
    print("and the 60-vertex chamber graph is a regular 2-cover of it, then")
    print("the chamber graph sits naturally as a signed/double lift of L(Icosahedron).")
    print("If the 15-vertex quotient is strongly regular with parameters (15,8,4,4),")
    print("then the opposition relation collapses to a classical known object.")


if __name__ == "__main__":
    main()
