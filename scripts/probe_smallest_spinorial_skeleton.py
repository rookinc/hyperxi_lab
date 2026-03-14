#!/usr/bin/env python3

from collections import Counter
import itertools
import networkx as nx


def canonical_cycle(cyc):
    n = len(cyc)
    rots = [tuple(cyc[i:] + cyc[:i]) for i in range(n)]
    rev = list(reversed(cyc))
    rots += [tuple(rev[i:] + rev[:i]) for i in range(n)]
    return min(rots)


def simple_cycles_length_k(G, k):
    DG = nx.DiGraph()
    DG.add_edges_from((u, v) for u, v in G.edges())
    DG.add_edges_from((v, u) for u, v in G.edges())
    out = set()
    for cyc in nx.simple_cycles(DG):
        if len(cyc) == k:
            out.add(canonical_cycle(list(cyc)))
    return sorted(out)


def all_edge_signings(G):
    edges = sorted(tuple(sorted(e)) for e in G.edges())
    m = len(edges)
    for bits in range(1 << m):
        sign = {}
        for i, e in enumerate(edges):
            sign[e] = (bits >> i) & 1
        yield sign


def pentagon_parity_data(G, sign):
    pentagons = simple_cycles_length_k(G, 5)
    odd = []
    even = []
    for cyc in pentagons:
        parity = 0
        cyc_edges = []
        for i in range(5):
            e = tuple(sorted((cyc[i], cyc[(i + 1) % 5])))
            parity ^= sign[e]
            cyc_edges.append(e)
        if parity:
            odd.append((cyc, cyc_edges))
        else:
            even.append((cyc, cyc_edges))
    return pentagons, odd, even


def odd_pentagon_uniformity(G, odd):
    if not odd:
        return None

    vcount = Counter()
    ecount = Counter()
    inter = Counter()

    for cyc, edges in odd:
        for v in cyc:
            vcount[v] += 1
        for e in edges:
            ecount[e] += 1

    for i in range(len(odd)):
        A = set(odd[i][0])
        for j in range(i + 1, len(odd)):
            B = set(odd[j][0])
            inter[len(A & B)] += 1

    return {
        "num_odd": len(odd),
        "vertex_hist": Counter(vcount.values()),
        "edge_hist": Counter(ecount.values()),
        "intersection_hist": inter,
    }


def has_spinorial_signature(G, max_signings=200000):
    """
    Look for a signing with:
    - at least one odd 5-cycle and one even 5-cycle
    - odd pentagons forming a uniform incidence system
    """
    edges = list(G.edges())
    if len(edges) > 20:
        return None

    checked = 0
    for sign in all_edge_signings(G):
        checked += 1
        if checked > max_signings:
            break

        pentagons, odd, even = pentagon_parity_data(G, sign)
        if not pentagons:
            continue
        if not odd or not even:
            continue

        data = odd_pentagon_uniformity(G, odd)
        if data is None:
            continue

        # A loose version of your pattern:
        # all vertices in odd pentagon support have same incidence
        # all odd pentagon edges used once
        vh = data["vertex_hist"]
        eh = data["edge_hist"]

        if len(vh) == 1 and eh == Counter({1: len(set(e for _, es in odd for e in es))}):
            return {
                "sign": sign,
                "pentagons": pentagons,
                "odd": odd,
                "even": even,
                "data": data,
                "checked": checked,
            }

    return None


def candidate_graphs():
    out = []

    # Small named highly symmetric graphs
    out.append(("petersen", nx.petersen_graph()))
    out.append(("dodecahedral", nx.dodecahedral_graph()))
    out.append(("desargues", nx.desargues_graph()))
    out.append(("heawood", nx.heawood_graph()))
    out.append(("cubical", nx.cubical_graph()))
    out.append(("tetrahedral", nx.tetrahedral_graph()))
    out.append(("octahedral", nx.octahedral_graph()))
    out.append(("icosahedral", nx.icosahedral_graph()))

    # Some line graphs of small regular graphs
    smalls = [
        ("K4", nx.complete_graph(4)),
        ("K5", nx.complete_graph(5)),
        ("petersen", nx.petersen_graph()),
        ("cubical", nx.cubical_graph()),
    ]
    for name, G in smalls:
        out.append((f"line_{name}", nx.line_graph(G)))

    # Remove duplicates by graph6
    seen = set()
    uniq = []
    for name, G in out:
        H = nx.convert_node_labels_to_integers(G)
        g6 = nx.to_graph6_bytes(H, header=False).decode().strip()
        if g6 not in seen:
            seen.add(g6)
            uniq.append((name, H))
    return uniq


def main():
    print("=" * 80)
    print("PROBE SMALLEST SPINORIAL SKELETON")
    print("=" * 80)

    cands = candidate_graphs()
    print("candidate graphs:", [name for name, _ in cands])

    for name, G in cands:
        print()
        print("-" * 80)
        print(name)
        print("-" * 80)
        print("vertices:", G.number_of_nodes())
        print("edges:", G.number_of_edges())
        print("degree set:", sorted(set(dict(G.degree()).values())))

        pent = simple_cycles_length_k(G, 5)
        print("5-cycles:", len(pent))

        result = has_spinorial_signature(G)
        if result is None:
            print("spinorial-style odd/even pentagon split: not found")
            continue

        print("spinorial-style odd/even pentagon split: FOUND")
        print("signings checked:", result["checked"])
        print("odd pentagons:", len(result["odd"]))
        print("even pentagons:", len(result["even"]))
        print("odd vertex incidence histogram:", dict(result["data"]["vertex_hist"]))
        print("odd edge incidence histogram:", dict(result["data"]["edge_hist"]))
        print("odd pentagon pair intersections:", dict(result["data"]["intersection_hist"]))

        # print first few odd cycles
        print("sample odd pentagons:")
        for cyc, edges in result["odd"][:6]:
            print(" ", cyc, edges)


if __name__ == "__main__":
    main()
