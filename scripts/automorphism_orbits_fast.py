from __future__ import annotations

from collections import Counter, defaultdict

from vertex_connection_model import measured_graph_reindexed


def vertex_signature(adj, v):
    nbrs = adj[v]

    # triangles through v
    tri_v = 0
    nbr_list = sorted(nbrs)
    for i, a in enumerate(nbr_list):
        for b in nbr_list[i + 1:]:
            if b in adj[a]:
                tri_v += 1

    # common-neighbor profile vs all other vertices
    prof = Counter()
    for u in adj:
        if u == v:
            continue
        prof[len(adj[v] & adj[u])] += 1

    return (
        len(nbrs),
        tri_v,
        tuple(sorted(prof.items())),
    )


def edge_signature(adj, u, v):
    nu = adj[u] - {v}
    nv = adj[v] - {u}
    common = nu & nv
    only_u = nu - nv
    only_v = nv - nu

    cross = Counter()
    for a in only_u:
        for b in only_v:
            cross[len(adj[a] & adj[b])] += 1

    return (
        len(common),
        len(only_u),
        len(only_v),
        tuple(sorted(cross.items())),
    )


def main():
    adj = measured_graph_reindexed()

    print("=" * 80)
    print("FAST AUTOMORPHISM ORBIT TEST")
    print("=" * 80)

    vclasses = defaultdict(list)
    for v in sorted(adj):
        vclasses[vertex_signature(adj, v)].append(v)

    print("Vertex orbit candidates")
    print("-" * 80)
    print(f"classes: {len(vclasses)}")
    for i, (sig, verts) in enumerate(sorted(vclasses.items(), key=lambda kv: (len(kv[1]), kv[1][0]))):
        label = "..." if len(verts) > 12 else ""
        print(f"class {i}: size={len(verts)} verts={verts[:12]}{label}")
        print(f"  signature={sig}")

    print()

    eclasses = defaultdict(list)
    for u in sorted(adj):
        for v in sorted(adj[u]):
            if u < v:
                eclasses[edge_signature(adj, u, v)].append((u, v))

    print("Edge orbit candidates")
    print("-" * 80)
    print(f"classes: {len(eclasses)}")
    for i, (sig, edges) in enumerate(sorted(eclasses.items(), key=lambda kv: (len(kv[1]), kv[1][0]))):
        label = "..." if len(edges) > 10 else ""
        print(f"class {i}: size={len(edges)} first_edges={edges[:10]}{label}")
        print(f"  signature={sig}")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("1 vertex class -> strong evidence of vertex-transitivity")
    print("1 edge class   -> strong evidence of edge-transitivity")


if __name__ == "__main__":
    main()
