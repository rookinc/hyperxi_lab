#!/usr/bin/env python3

import itertools
from collections import Counter
import networkx as nx

D = nx.dodecahedral_graph()
L = nx.line_graph(D)

# --------------------------------------------------
# Find Petrie cycles (length-10 zig-zag cycles)
# --------------------------------------------------

def petrie_cycles(G):

    cycles=set()

    for start in G.nodes():
        for n1 in G[start]:
            stack=[(start,n1,[start,n1])]

            while stack:
                prev,cur,path=stack.pop()

                if len(path)==10:
                    if start in G[cur]:
                        cyc=tuple(path)
                        rots=[]
                        for k in range(10):
                            rots.append(tuple(cyc[k:]+cyc[:k]))
                        rev=list(reversed(cyc))
                        for k in range(10):
                            rots.append(tuple(rev[k:]+rev[:k]))
                        cycles.add(min(rots))
                    continue

                for nxt in G[cur]:
                    if nxt==prev: 
                        continue
                    if nxt in path: 
                        continue
                    stack.append((cur,nxt,path+[nxt]))

    return list(cycles)

petries=petrie_cycles(D)

print("Petrie cycles found:",len(petries))

# --------------------------------------------------
# Edge membership in Petrie
# --------------------------------------------------

def edge_in_petrie(p,e):

    u,v=e

    for i in range(len(p)):
        a=p[i]
        b=p[(i+1)%len(p)]
        if {a,b}=={u,v}:
            return True

    return False


# --------------------------------------------------
# opposite edges
# --------------------------------------------------

dist=dict(nx.all_pairs_shortest_path_length(L))
diam=nx.diameter(L)

pairs=[]
seen=set()

for e in L.nodes():

    if e in seen:
        continue

    far=[f for f,d in dist[e].items() if d==diam][0]

    pairs.append((e,far))

    seen.add(e)
    seen.add(far)

pairs=list(set(tuple(sorted(p)) for p in pairs))

# --------------------------------------------------
# build G15
# --------------------------------------------------

G15=nx.Graph()
G15.add_nodes_from(range(len(pairs)))

for i,j in itertools.combinations(range(len(pairs)),2):

    A=pairs[i]
    B=pairs[j]

    edges_between=0

    for e in A:
        for f in B:
            if L.has_edge(e,f):
                edges_between+=1

    if edges_between==2:
        G15.add_edge(i,j)

print("G15 edges:",G15.number_of_edges())

# --------------------------------------------------
# classify
# --------------------------------------------------

hist=Counter()

for i,j in G15.edges():

    A=pairs[i]
    B=pairs[j]

    locals=[]

    for e in A:
        for f in B:
            if L.has_edge(e,f):
                locals.append((e,f))

    # two local edges
    (e1,f1),(e2,f2)=locals

    petrie_sets=[]

    for p in petries:

        if edge_in_petrie(p,e1) and edge_in_petrie(p,f1):
            petrie_sets.append("same")

        if edge_in_petrie(p,e2) and edge_in_petrie(p,f2):
            petrie_sets.append("same")

    if petrie_sets:
        hist["same_petrie"]+=1
    else:
        hist["different_petrie"]+=1

print()
print("PETRIE RELATION HISTOGRAM")
print(hist)
