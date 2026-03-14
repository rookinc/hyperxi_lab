#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators

SEEDS = ["FFF", "FFFV", "VFFSV", "SVFF"]


# ------------------------------------------------------------
# permutation utilities
# ------------------------------------------------------------

def compose(p, q):
    return tuple(p[q[i]] for i in range(len(p)))


def inverse(p):
    inv = [0] * len(p)
    for i, j in enumerate(p):
        inv[j] = i
    return tuple(inv)


def cycle_histogram(p):
    n = len(p)
    seen = [False]*n
    hist = {}
    for i in range(n):
        if seen[i]:
            continue
        j=i
        L=0
        while not seen[j]:
            seen[j]=True
            j=p[j]
            L+=1
        hist[L]=hist.get(L,0)+1
    return dict(sorted(hist.items()))


# ------------------------------------------------------------
# build permutation from word
# ------------------------------------------------------------

def word_perm(fm, gen, word):
    out=[]
    for i in range(fm.num_flags()):
        state=fm.get(i)
        nxt=gen.apply_word(state,word)
        out.append(fm.index(nxt))
    return tuple(out)


# ------------------------------------------------------------
# grow subgroup
# ------------------------------------------------------------

def grow_subgroup(fm, gen):

    seeds={w:word_perm(fm,gen,w) for w in SEEDS}

    gens=[]
    for p in seeds.values():
        gens.append(p)
        gens.append(inverse(p))

    ident=tuple(range(fm.num_flags()))
    seen={ident}
    frontier=[ident]

    while frontier:
        new=[]
        for g in gens:
            for h in frontier:
                x=compose(g,h)
                if x not in seen:
                    seen.add(x)
                    new.append(x)
        frontier=new

    return list(seen)


# ------------------------------------------------------------
# center
# ------------------------------------------------------------

def compute_center(group):

    center=[]

    for g in group:

        ok=True
        for h in group:

            if compose(g,h)!=compose(h,g):
                ok=False
                break

        if ok:
            center.append(g)

    return center


# ------------------------------------------------------------
# conjugacy classes
# ------------------------------------------------------------

def conjugacy_classes(group):

    unused=set(group)
    classes=[]

    while unused:

        g=unused.pop()

        cl=set()

        for h in group:

            conj=compose(h,compose(g,inverse(h)))
            cl.add(conj)

        classes.append(cl)
        unused-=cl

    return classes


# ------------------------------------------------------------
# main
# ------------------------------------------------------------

def main():

    print("="*80)
    print("TRANSPORT SUBGROUP STRUCTURE ANALYSIS")
    print("="*80)

    fm=FlagModel()
    gen=CoxeterGenerators(fm)

    group=grow_subgroup(fm,gen)

    print("group size:",len(group))
    print()

    center=compute_center(group)

    print("CENTER")
    print("-"*80)
    print("size:",len(center))

    for c in center:
        print("cycle:",cycle_histogram(c))

    print()

    classes=conjugacy_classes(group)

    print("CONJUGACY CLASSES")
    print("-"*80)

    for cl in classes:
        rep=next(iter(cl))
        print(
            "size:",len(cl),
            "cycle:",cycle_histogram(rep)
        )

    print()

    print("total classes:",len(classes))


if __name__=="__main__":
    main()

