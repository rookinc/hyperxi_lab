import itertools
import networkx as nx
from collections import Counter

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


def build_chambers():
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    owner = {}
    classes = []
    seen = set()

    for i in range(fm.num_flags()):
        if i in seen:
            continue

        j = fm.index(gen.S(fm.get(i)))
        pair = tuple(sorted((i, j)))
        cid = len(classes)
        classes.append(pair)

        for x in pair:
            seen.add(x)
            owner[x] = cid

    return fm, gen, classes, owner


def chamber_graph(fm, gen, classes, owner):
    G = nx.Graph()
    G.add_nodes_from(range(len(classes)))

    for cid, pair in enumerate(classes):
        for idx in pair:
            x = fm.get(idx)

            for move in (gen.F, gen.V):
                y = move(x)
                did = owner[fm.index(y)]

                if did != cid:
                    a, b = sorted((cid, did))
                    G.add_edge(a, b)

    return G


def chamber_word_map(fm, gen, classes, owner, word):
    mapping = {}
    bad = []

    for cid, pair in enumerate(classes):

        imgs = set()

        for idx in pair:
            x = fm.get(idx)
            y = gen.apply_word(x, word)
            imgs.add(owner[fm.index(y)])

        if len(imgs) != 1:
            bad.append((cid, sorted(imgs)))
        else:
            mapping[cid] = next(iter(imgs))

    return mapping, bad


def square_map(m):
    return {k: m[m[k]] for k in m}


fm, gen, classes, owner = build_chambers()

G = chamber_graph(fm, gen, classes, owner)
dist = dict(nx.all_pairs_shortest_path_length(G))

alphabet = "FV"
candidates = []

for L in range(1, 9):
    for tup in itertools.product(alphabet, repeat=L):

        w = "".join(tup)

        m, bad = chamber_word_map(fm, gen, classes, owner, w)

        if bad:
            continue

        if len(set(m.values())) != len(m):
            continue

        sq = square_map(m)

        is_involution = all(sq[k] == k for k in sq)
        fixed = sum(1 for k in m if m[k] == k)

        dists = Counter(dist[k][m[k]] for k in m)

        if is_involution:
            candidates.append((w, fixed, dict(sorted(dists.items()))))


print("=" * 80)
print("CHAMBER WORD INVOLUTION SEARCH")
print("=" * 80)

print("chambers:", len(classes))
print("edges:", G.number_of_edges())

print()
print("word   fixed   distance_hist")
print("-" * 80)

for w, fixed, dists in candidates:
    print(f"{w:8s} {fixed:5d}   {dists}")

print()
print("PROMISING WORDS (fixed-point-free, single distance)")
print("-" * 80)

for w, fixed, dists in candidates:
    if fixed == 0 and len(dists) == 1:
        print(f"{w:8s} {dists}")
