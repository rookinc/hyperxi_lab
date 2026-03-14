#!/usr/bin/env python3

import itertools
from collections import Counter
import networkx as nx

D = nx.dodecahedral_graph()
L = nx.line_graph(D)

# find faces
def find_faces(G):
    faces=set()
    for start in G.nodes():
        stack=[(start,[start])]
        while stack:
            v,path=stack.pop()
            if len(path)==5:
                if start in G[v]:
                    cyc=path[:]
                    rots=[]
                    for k in range(5):
                        rots.append(tuple(cyc[k:]+cyc[:k]))
                    rev=list(reversed(cyc))
                    for k in range(5):
                        rots.append(tuple(rev[k:]+rev[:k]))
                    faces.add(min(rots))
                continue
            for w in G[v]:
                if w==start and len(path)<5: continue
                if w in path: continue
                stack.append((w,path+[w]))
    return list(faces)

faces=find_faces(D)

def edge_in_face(face,e):
    u,v=e
    for i in range(5):
        a,b=face[i],face[(i+1)%5]
        if set((a,b))==set((u,v)):
            return True
    return False

# opposite edges
dist=dict(nx.all_pairs_shortest_path_length(L))
diam=nx.diameter(L)

pairs=[]
seen=set()

for e in L.nodes():
    if e in seen: continue
    far=[f for f,d in dist[e].items() if d==diam]
    f=far[0]
    pairs.append((e,f))
    seen.add(e)
    seen.add(f)

pairs=list(set(tuple(sorted(p)) for p in pairs))

# compatibility graph
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

face_relation=Counter()

for i,j in G15.edges():
    A=pairs[i]
    B=pairs[j]

    same_face=False

    for e in A:
        for f in B:
            for face in faces:
                if edge_in_face(face,e) and edge_in_face(face,f):
                    same_face=True

    face_relation[same_face]+=1

print("face relation histogram:",face_relation)
