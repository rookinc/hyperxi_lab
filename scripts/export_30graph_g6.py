#!/usr/bin/env python3

import networkx as nx
from load_thalean_graph import load_spec, build_graph

def load_thalean_graph():
    return build_graph(load_spec())

def antipode_map(G):
    dist = dict(nx.all_pairs_shortest_path_length(G))
    diam = nx.diameter(G)

    a = {}
    for v in G.nodes():
        far = [u for u,d in dist[v].items() if d == diam]
        a[v] = far[0]

    return a

def quotient(G,a):

    seen=set()
    classes=[]
    cls={}

    for v in sorted(G.nodes()):

        if v in seen:
            continue

        pair=(v,a[v])
        seen.update(pair)

        idx=len(classes)
        classes.append(pair)

        for x in pair:
            cls[x]=idx

    Q=nx.Graph()
    Q.add_nodes_from(range(len(classes)))

    for u,v in G.edges():
        cu,cv=cls[u],cls[v]
        if cu!=cv:
            Q.add_edge(cu,cv)

    return Q

def main():

    G60=load_thalean_graph()

    a=antipode_map(G60)

    G30=quotient(G60,a)

    print("GRAPH6")
    print(nx.to_graph6_bytes(G30,header=False).decode().strip())

if __name__=="__main__":
    main()

