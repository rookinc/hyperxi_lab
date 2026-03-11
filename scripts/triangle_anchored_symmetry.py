from __future__ import annotations

from collections import Counter, defaultdict
from itertools import permutations

from vertex_connection_model import measured_graph_reindexed


def triangle_set(adj):
    tris = []
    for a in sorted(adj):
        for b in [x for x in adj[a] if x > a]:
            common = adj[a] & adj[b]
            for c in [x for x in common if x > b]:
                tris.append((a, b, c))
    return sorted(tris)


def vertex_signature(adj, v):
    nbrs = sorted(adj[v])

    tri_v = 0
    for i, a in enumerate(nbrs):
        for b in nbrs[i + 1:]:
            if b in adj[a]:
                tri_v += 1

    cn_prof = Counter()
    for u in adj:
        if u == v:
            continue
        cn_prof[len(adj[v] & adj[u])] += 1

    return (
        len(nbrs),
        tri_v,
        tuple(sorted(cn_prof.items())),
    )


def triangle_signature(adj, tri):
    sigs = sorted(vertex_signature(adj, x) for x in tri)
    tri_set = set(tri)
    external_counts = sorted(len(adj[x] - tri_set) for x in tri)
    return (tuple(sigs), tuple(external_counts))


def compatible_candidates(adj, src_tri, dst_tri):
    out = []
    src = list(src_tri)
    dst = list(dst_tri)

    src_sig = [vertex_signature(adj, x) for x in src]
    dst_sig = [vertex_signature(adj, y) for y in dst]

    for perm in permutations(range(3)):
        ok = True
        for i, j in enumerate(perm):
            if src_sig[i] != dst_sig[j]:
                ok = False
                break
        if ok:
            out.append({src[i]: dst[perm[i]] for i in range(3)})
    return out


def extend_by_shells(adj, seed):
    mapping = dict(seed)
    reverse = {v: k for k, v in mapping.items()}

    changed = True
    while changed:
        changed = False

        src_buckets = defaultdict(list)
        dst_buckets = defaultdict(list)

        mapped_src = set(mapping)
        mapped_dst = set(reverse)

        for u in adj:
            if u in mapped_src:
                continue
            key = tuple((m, int(u in adj[m])) for m in sorted(mapped_src))
            src_buckets[key].append(u)

        for v in adj:
            if v in mapped_dst:
                continue
            key = tuple((mapping[m], int(v in adj[mapping[m]])) for m in sorted(mapped_src))
            dst_buckets[key].append(v)

        if sorted((k, len(v)) for k, v in src_buckets.items()) != sorted((k, len(v)) for k, v in dst_buckets.items()):
            return None

        progress = False
        for k in list(src_buckets):
            xs = sorted(src_buckets[k])
            ys = sorted(dst_buckets[k])

            if len(xs) == 1:
                u = xs[0]
                v = ys[0]
                mapping[u] = v
                reverse[v] = u
                changed = True
                progress = True

        if progress:
            continue

        break

    if len(mapping) != len(adj):
        return None

    for u in adj:
        mu = mapping[u]
        if {mapping[w] for w in adj[u]} != adj[mu]:
            return None

    return mapping


def main():
    adj = measured_graph_reindexed()
    tris = triangle_set(adj)

    print("=" * 80)
    print("TRIANGLE-ANCHORED SYMMETRY TEST")
    print("=" * 80)
    print(f"vertices: {len(adj)}")
    print(f"triangles: {len(tris)}")
    print()

    tri_sig_classes = defaultdict(list)
    for t in tris:
        tri_sig_classes[triangle_signature(adj, t)].append(t)

    print("Triangle signature classes")
    print("-" * 80)
    print(f"classes: {len(tri_sig_classes)}")
    for i, (sig, members) in enumerate(sorted(tri_sig_classes.items(), key=lambda kv: (len(kv[1]), kv[1][0]))):
        label = "..." if len(members) > 10 else ""
        print(f"class {i}: size={len(members)} first={members[:10]}{label}")
        print(f"  signature={sig}")

    print()
    root_tri = tris[0]
    print(f"root triangle: {root_tri}")

    root_sig = triangle_signature(adj, root_tri)
    candidates = tri_sig_classes[root_sig]

    print(f"candidate image triangles: {len(candidates)}")
    print()

    successful = 0
    triangle_orbit = set()
    vertex_orbit = set()

    for dst_tri in candidates:
        seeds = compatible_candidates(adj, root_tri, dst_tri)
        for seed in seeds:
            full = extend_by_shells(adj, seed)
            if full is not None:
                successful += 1
                triangle_orbit.add(dst_tri)
                for v in root_tri:
                    vertex_orbit.add(full[v])

    print("Results")
    print("-" * 80)
    print(f"successful triangle-anchored extensions: {successful}")
    print(f"triangle orbit size from successful maps: {len(triangle_orbit)}")
    print(f"vertex orbit sample size from rooted triangle: {len(vertex_orbit)}")
    print(f"triangle orbit sample: {sorted(triangle_orbit)[:12]}{'...' if len(triangle_orbit) > 12 else ''}")
    print(f"vertex orbit sample: {sorted(vertex_orbit)[:20]}{'...' if len(vertex_orbit) > 20 else ''}")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("If many image triangles succeed, the graph likely has a single triangle orbit.")
    print("If the induced image set of root-triangle vertices spreads widely, that supports")
    print("vertex-transitivity under triangle-anchored automorphisms.")


if __name__ == "__main__":
    main()
