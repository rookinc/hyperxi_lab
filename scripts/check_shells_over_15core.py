from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

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
        raise FileNotFoundError("Could not find partition JSON.")
    print(f"loading partition from: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    fibers = try_extract_partition(data)
    if fibers is None:
        raise ValueError("Could not recognize a 15x4 fiber partition.")
    return fibers

def build_vertex_to_fiber(fibers):
    v2f = {}
    for i, fiber in enumerate(fibers):
        for v in fiber:
            if v in v2f:
                raise ValueError(f"vertex {v} occurs in multiple fibers")
            v2f[v] = i
    return v2f

def build_fiber_multigraph(G60, v2f):
    H = nx.MultiGraph()
    H.add_nodes_from(range(15))

    intra = 0
    inter_counts = Counter()

    for u, v in G60.edges():
        fu, fv = v2f[u], v2f[v]
        if fu == fv:
            intra += 1
        else:
            a, b = sorted((fu, fv))
            H.add_edge(a, b)
            inter_counts[(a, b)] += 1

    print(f"fiber multigraph: |V|={H.number_of_nodes()} |E|={H.number_of_edges()}")
    print(f"intra-fiber edges: {intra}")
    print(f"distinct unordered fiber pairs with edges: {len(inter_counts)}")
    return H, inter_counts

def collapse_to_simple_core(inter_counts):
    C = nx.Graph()
    C.add_nodes_from(range(15))
    for (a, b), m in inter_counts.items():
        if m > 0:
            C.add_edge(a, b, multiplicity=m)
    print(f"collapsed simple core: |V|={C.number_of_nodes()} |E|={C.number_of_edges()}")
    return C

def shell_projection_signature(G60, C, v2f, root):
    dist60 = nx.single_source_shortest_path_length(G60, root)
    root_fiber = v2f[root]
    dist15 = nx.single_source_shortest_path_length(C, root_fiber)

    max60 = max(dist60.values())
    sig = []

    for k in range(max60 + 1):
        verts = [v for v, d in dist60.items() if d == k]
        base_count = Counter(dist15[v2f[v]] for v in verts)
        sig.append(tuple(sorted(base_count.items())))

    shell = tuple(sum(cnt for _, cnt in layer) for layer in sig)
    return shell, tuple(sig)

def main():
    G60 = load_g60()
    fibers = load_partition()
    v2f = build_vertex_to_fiber(fibers)
    Hmulti, inter_counts = build_fiber_multigraph(G60, v2f)
    C = collapse_to_simple_core(inter_counts)

    print("\nedge multiplicity distribution on the collapsed 15-core:")
    mult_dist = Counter(inter_counts.values())
    for m in sorted(mult_dist):
        print(f"  multiplicity {m}: {mult_dist[m]} edges")

    print("\n15-core distance profile:")
    if nx.is_connected(C):
        root = 0
        d = nx.single_source_shortest_path_length(C, root)
        prof = Counter(d.values())
        print(" ", tuple(prof[i] for i in range(max(prof) + 1)))
    else:
        print("  core is not connected")

    sigs = Counter()
    shells = Counter()

    for r in G60.nodes():
        shell, sig = shell_projection_signature(G60, C, v2f, r)
        shells[shell] += 1
        sigs[sig] += 1

    print("\nG60 shell profiles:")
    for shell, mult in shells.items():
        print(f"  {shell} x{mult}")

    print(f"\ndistinct projection signatures: {len(sigs)}")
    for i, (sig, mult) in enumerate(sigs.items(), start=1):
        print(f"\nprojection signature #{i} multiplicity {mult}")
        for layer_idx, layer in enumerate(sig):
            print(f"  layer {layer_idx}: {layer}")
        if i >= 3:
            break

    out = {
        "edge_multiplicity_distribution": {str(k): v for k, v in mult_dist.items()},
        "g60_shell_profiles": {str(k): v for k, v in shells.items()},
        "num_projection_signatures": len(sigs),
        "projection_signatures": [
            {
                "multiplicity": mult,
                "layers": [list(map(list, layer)) for layer in sig],
            }
            for sig, mult in sigs.items()
        ],
    }

    out_path = ROOT / "reports" / "check_shells_over_15core.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nsaved {out_path}")

if __name__ == "__main__":
    main()
