from __future__ import annotations

from collections import defaultdict

from vertex_connection_model import measured_graph_reindexed


def local_signature(adj, v):
    nbrs = sorted(adj[v])
    deg = len(nbrs)

    # count edges among neighbors
    nn_edges = 0
    for i, a in enumerate(nbrs):
        for b in nbrs[i + 1:]:
            if b in adj[a]:
                nn_edges += 1

    # common-neighbor profile against non-neighbors
    cn_profile = defaultdict(int)
    for u in adj:
        if u == v or u in adj[v]:
            continue
        c = len(adj[v] & adj[u])
        cn_profile[c] += 1

    return (
        deg,
        nn_edges,
        tuple(sorted(cn_profile.items())),
    )


def refine_vertex_partition(adj):
    """
    Simple Weisfeiler-Lehman style refinement.
    Returns a dict: color_key -> sorted list of vertices.
    """
    colors = {v: local_signature(adj, v) for v in adj}

    while True:
        new_colors = {}
        for v in adj:
            nbr_colors = tuple(sorted(colors[n] for n in adj[v]))
            new_colors[v] = (colors[v], nbr_colors)

        if new_colors == colors:
            break
        colors = new_colors

    classes = defaultdict(list)
    for v, c in colors.items():
        classes[c].append(v)

    for c in classes:
        classes[c].sort()

    return classes


def edge_signature(adj, u, v):
    nu = adj[u] - {v}
    nv = adj[v] - {u}
    common = nu & nv
    only_u = nu - nv
    only_v = nv - nu

    cross_profile = defaultdict(int)
    for a in only_u:
        for b in only_v:
            cross_profile[len(adj[a] & adj[b])] += 1

    return (
        len(common),
        len(only_u),
        len(only_v),
        tuple(sorted(cross_profile.items())),
    )


def edge_classes(adj):
    classes = defaultdict(list)
    for u in sorted(adj):
        for v in sorted(adj[u]):
            if u < v:
                sig = edge_signature(adj, u, v)
                classes[sig].append((u, v))
    return classes


def main():
    adj = measured_graph_reindexed()

    print("=" * 80)
    print("AUTOMORPHISM ORBIT TEST")
    print("=" * 80)

    vclasses = refine_vertex_partition(adj)

    print("Vertex orbit candidates")
    print("-" * 80)
    print(f"classes: {len(vclasses)}")
    for i, (sig, verts) in enumerate(sorted(vclasses.items(), key=lambda kv: (len(kv[1]), kv[1][0]))):
        label = "..." if len(verts) > 12 else ""
        print(f"class {i}: size={len(verts)} verts={verts[:12]}{label}")
        print(f"  signature={sig}")

    print()
    eclasses = edge_classes(adj)

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
