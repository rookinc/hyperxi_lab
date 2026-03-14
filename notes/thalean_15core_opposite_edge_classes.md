# Thalean Graph: 15-Core as Opposite-Edge Compatibility Graph

Date: 2026-03-13

## Reduction Ladder

The Thalean graph hierarchy discovered in the HyperXi transport system is:

60 → 30 → 15

- G60 : Thalean chamber graph
- G30 : antipodal quotient
- G15 : second antipodal quotient

Properties:

G60  
- vertices: 60  
- edges: 120  
- degree: 4  
- triangles: 40  
- diameter: 6  

G30  
- vertices: 30  
- edges: 60  
- degree: 4  

G15  
- vertices: 15  
- edges: 30  
- degree: 4  
- triangles: 10  
- diameter: 3  

## Structural Interpretation

The reductions correspond naturally to geometric compression of the dodecahedral edge system:

60 : edge–face chamber states  
30 : edges  
15 : opposite-edge classes  

Each vertex of the 30-layer represents a pair of 60-vertices:

(v, a(v))

Each vertex of the 15-layer represents a pair of 30-vertices:

(e, e')

which corresponds to two opposite edges of the dodecahedral edge graph.

## Adjacency Rule in the 15-Core

The probe `probe_15core_as_opposite_edge_pairs.py` reveals a clean rule:

For two 15-vertices

(A, B) and (C, D)

adjacency occurs **iff exactly two cross-adjacencies exist between the underlying 30-vertices**.

Empirical result:

edges_between histogram:
2 → 30 edges

nonedges histogram:
0 → 75 pairs

So the rule is exactly:

(A,B) ~ (C,D)
iff
two of {A,B} are adjacent to two of {C,D} in G30.

## Interpretation

Thus the 15-vertex graph is a **compatibility graph on opposite-edge classes** of the 30-vertex edge graph.

The hierarchy becomes:

dodecahedron
↓
edge-face chambers (60)
↓
edges (30)
↓
opposite-edge classes (15)

## Symmetry

Automorphism structure discovered earlier:

Aut(G60) = V4 ⋊ S5  
|Aut(G60)| = 480  

with:

V4 : fiber symmetry of the 4-lift  
S5 : symmetry acting on the 15-core  

The induced action on the 15 vertices is exactly S5.

## Summary

The Thalean graph can be understood as:

• a V4-fibered lift of a 15-vertex compatibility graph  
• whose vertices represent opposite-edge classes of the dodecahedral edge system  
• with adjacency inherited from the edge-adjacency structure of the 30-vertex layer.

This explains the entire reduction ladder:

60 → 30 → 15

as successive compression of chamber, edge, and opposite-edge structure.
