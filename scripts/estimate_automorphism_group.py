from __future__ import annotations

from collections import Counter, defaultdict, deque
from itertools import permutations

from vertex_connection_model import measured_graph_reindexed


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


def vertex_signature(adj, dist, v):
    counts = Counter(dist[v].values())

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
        len(adj[v]),
        tri_v,
        tuple(counts[k] for k in sorted(counts)),
        tuple(sorted(cn_prof.items())),
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


def neighbor_bijections(adj, dist, root, image):
    """
    Candidate bijections between N(root) and N(image) preserving local edge pattern
    and distance-to-shell profile.
    """
    n1 = sorted(adj[root])
    n2 = sorted(adj[image])

    def local_key(x, center):
        return (
            tuple(sorted(dist[center][z] for z in adj[x] if z != center)),
            sum(1 for y in adj[x] if y in adj[center]),
        )

    buckets1 = defaultdict(list)
    buckets2 = defaultdict(list)

    for x in n1:
        buckets1[local_key(x, root)].append(x)
    for y in n2:
        buckets2[local_key(y, image)].append(y)

    if sorted((k, len(v)) for k, v in buckets1.items()) != sorted((k, len(v)) for k, v in buckets2.items()):
        return []

    parts = []
    for k in sorted(buckets1):
        a = buckets1[k]
        b = buckets2[k]
        parts.append((a, b))

    maps = [{}]
    for a_list, b_list in parts:
        new_maps = []
        for p in permutations(b_list):
            for m in maps:
                mm = dict(m)
                ok = True
                for a, b in zip(a_list, p):
                    mm[a] = b
                # preserve adjacency among neighbors
                for i, a in enumerate(a_list):
                    for c in a_list[i + 1:]:
                        if (c in adj[a]) != (mm[c] in adj[mm[a]]):
                            ok = False
                            break
                    if not ok:
                        break
                if ok:
                    new_maps.append(mm)
        maps = new_maps

    return maps


def extend_isomorphism(adj, dist, seed_map):
    """
    BFS extension from a seeded partial map.
    Returns full map or None.
    """
    mapping = dict(seed_map)
    reverse = {v: k for k, v in mapping.items()}
    q = deque(mapping.keys())

    while q:
        x = q.popleft()
        y = mapping[x]

        nx = sorted(adj[x])
        ny = sorted(adj[y])

        # Unmapped neighbors must match by local invariants relative to mapped vertices
        unm_x = [u for u in nx if u not in mapping]
        unm_y = [v for v in ny if v not in reverse]

        if len(unm_x) != len(unm_y):
            return None

        if not unm_x:
            continue

        def neigh_key(u, src):
            linked = []
            for z in adj[u]:
                if z in mapping:
                    linked.append((dist[src][z], mapping[z]))
            linked.sort()
            return tuple(linked)

        bx = defaultdict(list)
        by = defaultdict(list)
        for u in unm_x:
            bx[neigh_key(u, x)].append(u)
        for v in unm_y:
            by[neigh_key(v, y)].append(v)

        if sorted((k, len(v)) for k, v in bx.items()) != sorted((k, len(v)) for k, v in by.items()):
            return None

        for k in bx:
            xs = bx[k]
            ys = by[k]
            if len(xs) == 1:
                u = xs[0]
                v = ys[0]
                mapping[u] = v
                reverse[v] = u
                q.append(u)
            else:
                # small ambiguity; try adjacency-preserving order
                found = False
                for perm in permutations(ys):
                    trial = {}
                    ok = True
                    for u, v in zip(xs, perm):
                        trial[u] = v
                    # preserve adjacency inside block
                    for i, u in enumerate(xs):
                        for w in xs[i + 1:]:
                            if (w in adj[u]) != (trial[w] in adj[trial[u]]):
                                ok = False
                                break
                        if not ok:
                            break
                    if ok:
                        for u, v in trial.items():
                            mapping[u] = v
                            reverse[v] = u
                            q.append(u)
                        found = True
                        break
                if not found:
                    return None

    # final verification
    if len(mapping) != len(adj):
        return None

    for u in adj:
        mu = mapping[u]
        image_neighbors = {mapping[v] for v in adj[u]}
        if image_neighbors != adj[mu]:
            return None

    return mapping


def main():
    adj = measured_graph_reindexed()
    dist = all_distances(adj)

    print("=" * 80)
    print("AUTOMORPHISM GROUP ESTIMATOR")
    print("=" * 80)

    sigs = {v: vertex_signature(adj, dist, v) for v in adj}
    sig_classes = defaultdict(list)
    for v, s in sigs.items():
        sig_classes[s].append(v)

    print("vertex signature classes:", len(sig_classes))
    for i, verts in enumerate(sig_classes.values()):
        print(f"  class {i}: size={len(verts)}")

    root = min(adj)
    root_sig = sigs[root]
    candidates = sorted(sig_classes[root_sig])

    print()
    print(f"root vertex: {root}")
    print(f"candidate images for root: {len(candidates)}")

    automorphisms = []
    failed_root = 0
    failed_neighbor = 0

    for image in candidates:
        nb_maps = neighbor_bijections(adj, dist, root, image)
        if not nb_maps:
            failed_root += 1
            continue

        for nm in nb_maps:
            seed = {root: image}
            seed.update(nm)
            full = extend_isomorphism(adj, dist, seed)
            if full is not None:
                automorphisms.append(full)
            else:
                failed_neighbor += 1

    # deduplicate
    uniq = {}
    for m in automorphisms:
        key = tuple(m[v] for v in sorted(adj))
        uniq[key] = m

    automorphisms = list(uniq.values())

    print(f"successful automorphisms found: {len(automorphisms)}")
    print(f"failed root-image attempts: {failed_root}")
    print(f"failed neighbor-seeding attempts: {failed_neighbor}")

    if automorphisms:
        images_of_root = sorted({m[root] for m in automorphisms})
        print(f"orbit size of root under found automorphisms: {len(images_of_root)}")
        print(f"root orbit sample: {images_of_root[:20]}{'...' if len(images_of_root) > 20 else ''}")

        # edge orbit sample
        e0 = tuple(sorted((0, min(adj[0]))))
        edge_images = set()
        for m in automorphisms:
            a, b = e0
            x = tuple(sorted((m[a], m[b])))
            edge_images.add(x)
        print(f"sample edge orbit size from found automorphisms: {len(edge_images)}")

        # group size divisibility clues
        print()
        print("group size divisibility clues")
        print("-" * 80)
        print(f"found subgroup order: {len(automorphisms)}")
        for n in [12, 20, 30, 60, 120]:
            if len(automorphisms) % n == 0:
                print(f"  divisible by {n}")

    print()
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print("This is a constructive automorphism search, not just an invariant test.")
    print("If the root orbit reaches all 60 vertices, that is direct evidence of")
    print("vertex-transitivity. Large subgroup sizes divisible by 60 or 120 would")
    print("support an icosahedral symmetry origin.")


if __name__ == "__main__":
    main()
