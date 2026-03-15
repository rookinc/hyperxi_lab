from __future__ import annotations

from collections import defaultdict, Counter
from pathlib import Path
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = [
    ROOT / "reports" / "true_quotients" / "true_chamber_graph.g6",
    ROOT / "artifacts" / "census" / "thalean_graph.g6",
]

def load_graph() -> nx.Graph:
    for path in CANDIDATES:
        if path.exists():
            print(f"loading: {path}")
            return nx.read_graph6(path)
    raise FileNotFoundError("Could not find Thalean graph .g6")

def distance_layers(G: nx.Graph, root):
    dist = nx.single_source_shortest_path_length(G, root)
    layers = defaultdict(list)
    for v, d in dist.items():
        layers[d].append(v)
    return dist, layers

def analyze_root(G: nx.Graph, root):
    dist, layers = distance_layers(G, root)
    D = max(dist.values())

    a = {}
    b = {}
    c = {}

    for i in range(D + 1):
        vals_a = []
        vals_b = []
        vals_c = []

        for v in layers[i]:
            na = nb = nc = 0
            for w in G.neighbors(v):
                j = dist[w]
                if j == i - 1:
                    nc += 1
                elif j == i:
                    na += 1
                elif j == i + 1:
                    nb += 1
                else:
                    raise RuntimeError(
                        f"bad edge jump from distance {i} to {j} at vertex {v}"
                    )
            vals_a.append(na)
            vals_b.append(nb)
            vals_c.append(nc)

        a[i] = Counter(vals_a)
        b[i] = Counter(vals_b)
        c[i] = Counter(vals_c)

    return D, a, b, c, tuple(len(layers[i]) for i in range(D + 1))

def main():
    G = load_graph()
    print(f"|V|={G.number_of_nodes()} |E|={G.number_of_edges()}")
    print(f"degree set={sorted(set(dict(G.degree()).values()))}")
    print(f"connected={nx.is_connected(G)}")

    roots = list(G.nodes())
    root_data = {}
    shell_profiles = Counter()

    for r in roots:
        D, a, b, c, shell = analyze_root(G, r)
        root_data[r] = (D, a, b, c, shell)
        shell_profiles[shell] += 1

    print(f"\ndistinct shell profiles: {len(shell_profiles)}")
    for shell, mult in shell_profiles.items():
        print(f"  {shell} x{mult}")

    sigs = Counter()
    for r, (D, a, b, c, shell) in root_data.items():
        sig = (
            D,
            tuple(tuple(sorted(a[i].items())) for i in range(D + 1)),
            tuple(tuple(sorted(b[i].items())) for i in range(D + 1)),
            tuple(tuple(sorted(c[i].items())) for i in range(D + 1)),
        )
        sigs[sig] += 1

    print(f"\ndistinct intersection signatures: {len(sigs)}")

    if len(sigs) == 1:
        print("\nGraph appears distance-regular.")
        sig = next(iter(sigs))
        D, a_sig, b_sig, c_sig = sig

        print(f"diameter = {D}")
        print("\nintersection data by layer:")
        for i in range(D + 1):
            print(f"layer {i}:")
            print(f"  a_{i} = {a_sig[i]}")
            print(f"  b_{i} = {b_sig[i]}")
            print(f"  c_{i} = {c_sig[i]}")

        # if each is single-valued, print classical intersection array
        single_a = all(len(dict(a_sig[i])) == 1 for i in range(D + 1))
        single_b = all(len(dict(b_sig[i])) == 1 for i in range(D + 1))
        single_c = all(len(dict(c_sig[i])) == 1 for i in range(D + 1))

        if single_a and single_b and single_c:
            b_arr = []
            c_arr = []
            for i in range(D):
                b_arr.append(next(iter(dict(b_sig[i]).keys())))
            for i in range(1, D + 1):
                c_arr.append(next(iter(dict(c_sig[i]).keys())))
            print("\nintersection array:")
            print(f"  b = {b_arr}")
            print(f"  c = {c_arr}")
        else:
            print("\nThe graph has a uniform signature, but some layers are not single-valued.")
    else:
        print("\nGraph is NOT distance-regular.")
        print("Representative signatures:\n")
        shown = 0
        for sig, mult in sigs.items():
            D, a_sig, b_sig, c_sig = sig
            print(f"signature multiplicity {mult}")
            print(f"diameter = {D}")
            for i in range(D + 1):
                print(f"layer {i}: a_{i}={a_sig[i]}  b_{i}={b_sig[i]}  c_{i}={c_sig[i]}")
            print()
            shown += 1
            if shown >= 3:
                break

if __name__ == "__main__":
    main()
