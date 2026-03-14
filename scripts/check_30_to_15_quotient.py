import networkx as nx
from itertools import combinations

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


def build_chamber_graph():
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    owner = {}
    classes = []
    seen = set()

    for i in range(fm.num_flags()):
        if i in seen:
            continue
        j = fm.index(gen.S(fm.get(i)))
        cyc = tuple(sorted((i, j)))
        cid = len(classes)
        classes.append(cyc)

        for x in cyc:
            seen.add(x)
            owner[x] = cid

    edges = set()

    for cyc in classes:
        src = owner[cyc[0]]

        for flag_idx in cyc:
            dst_flag = gen.V(fm.get(flag_idx))
            dst = owner[fm.index(dst_flag)]

            if dst != src:
                a, b = sorted((src, dst))
                edges.add((a, b))

    G = nx.Graph()
    G.add_nodes_from(range(len(classes)))
    G.add_edges_from(edges)

    return G


def antipodal_pairs(G):
    dist = dict(nx.all_pairs_shortest_path_length(G))
    diam = nx.diameter(G)

    pairs = []
    used = set()

    for u in G.nodes():
        if u in used:
            continue

        far = [v for v, d in dist[u].items() if d == diam]

        if len(far) == 1:
            v = far[0]
            pairs.append((u, v))
            used.add(u)
            used.add(v)

    return pairs


def quotient_graph(G, pairs):
    owner = {}

    for i, (a, b) in enumerate(pairs):
        owner[a] = i
        owner[b] = i

    Q = nx.Graph()
    Q.add_nodes_from(range(len(pairs)))

    for u, v in G.edges():
        a = owner[u]
        b = owner[v]

        if a != b:
            Q.add_edge(a, b)

    return Q


def main():

    G60 = build_chamber_graph()

    pairs = antipodal_pairs(G60)

    G30 = quotient_graph(G60, pairs)

    print("G30")
    print("vertices:", G30.number_of_nodes())
    print("edges:", G30.number_of_edges())
    print("degree set:", sorted(set(dict(G30.degree()).values())))
    print("triangles:", sum(nx.triangles(G30).values()) // 3)
    print("diameter:", nx.diameter(G30))

    # attempt second quotient

    dist = dict(nx.all_pairs_shortest_path_length(G30))
    diam = nx.diameter(G30)

    pairs2 = []
    used = set()

    for u in G30.nodes():
        if u in used:
            continue

        far = [v for v, d in dist[u].items() if d == diam]

        if len(far) == 1:
            v = far[0]
            pairs2.append((u, v))
            used.add(u)
            used.add(v)

    if len(pairs2) == 15:

        G15 = quotient_graph(G30, pairs2)

        print()
        print("G15 candidate")
        print("vertices:", G15.number_of_nodes())
        print("edges:", G15.number_of_edges())
        print("degree set:", sorted(set(dict(G15.degree()).values())))

        P = nx.petersen_graph()
        LP = nx.line_graph(P)

        print()
        print("Isomorphic to L(Petersen):", nx.is_isomorphic(G15, LP))


if __name__ == "__main__":
    main()
