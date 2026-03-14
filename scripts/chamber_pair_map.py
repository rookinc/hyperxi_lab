from __future__ import annotations

from collections import defaultdict
from hyperxi.geometry.flags import FlagModel
from hyperxi.transport.coxeter_generators import CoxeterGenerators


def cycle_decomposition(fm, gen, word):
    n = fm.num_flags()
    seen = [False]*n
    cycles=[]

    for start in range(n):
        if seen[start]:
            continue

        cur=start
        cyc=[]

        while not seen[cur]:
            seen[cur]=True
            cyc.append(cur)

            state=fm.get(cur)
            nxt=gen.apply_word(state,word)
            cur=fm.index(nxt)

        cycles.append(tuple(cyc))

    return cycles


def main():

    fm=FlagModel()
    gen=CoxeterGenerators(fm)

    s_pairs=cycle_decomposition(fm,gen,"S")

    # chamber partition via s0
    chambers=[]
    seen=set()

    for i in range(fm.num_flags()):
        if i in seen:
            continue
        j=fm.index(gen.apply_word(fm.get(i),"s0"))
        chambers.append((i,j))
        seen.add(i)
        seen.add(j)

    flag_to_pair={}
    for pid,pair in enumerate(s_pairs):
        for x in pair:
            flag_to_pair[x]=pid

    chamber_to_pairs=defaultdict(set)

    for cid,(a,b) in enumerate(chambers):
        chamber_to_pairs[cid].add(flag_to_pair[a])
        chamber_to_pairs[cid].add(flag_to_pair[b])

    print("="*80)
    print("CHAMBER → S-PAIR INCIDENCE")
    print("="*80)

    for cid in range(20):
        print(cid,"->",sorted(chamber_to_pairs[cid]))


if __name__=="__main__":
    main()
