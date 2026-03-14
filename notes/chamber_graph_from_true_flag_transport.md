# Chamber Graph from True Flag Transport

Date: 2026-03-14
Project: HyperXi Lab

---

## Result

The 60-vertex chamber graph studied in the HyperXi experiments is recovered directly from the true dodecahedral flag incidence model.

Construction:

Upstairs space:
- 120 lawful flags (vertex, edge, face)

Generators:
- S = edge flip
- F = face rotation
- V = vertex rotation

Quotient:
- quotient word: S

This partitions the 120 flags into 60 two-element classes.

Adjacency rule downstairs:
- apply generator V and project to the S-classes.

---

## Resulting Graph

The resulting graph has invariants:

vertices: 60  
edges: 120  
degree: 4  
triangles: 40  
diameter: 6  
shell profile: (1,4,8,16,24,6,1)

This matches exactly the chamber graph observed in earlier transport experiments.

---

## Equivalent Move Presentations

Several generator words produce the same graph:

V  
VV  
FFV  
FVF  
SV  
VS  

The simplest canonical construction is:

quotient: S  
adjacency: V

---

## Interpretation

The chamber graph is the visible quotient of the 120-flag dodecahedral transport system.

Structure:

120 flag transport space  
        ↓ quotient by S  
60 chamber graph  

Edges correspond to vertex-rotation transport across the dodecahedron.

---

## Relation to Transport Symmetry

Earlier experiments identified a 120-element transport subgroup acting on the flag space with:

- center of order 2
- central involution of cycle type {2:60}

This central involution pairs the two flags in each S-class.

Thus the chamber graph can be interpreted as the central quotient of the flag transport system.

---

## Status

Confirmed computationally via:

scripts/rebuild_true_thalion_quotient.py  
scripts/search_true_quotient_move_sets.py

Next step:

Test whether the discovered 120-element transport subgroup projects onto the automorphism group of the chamber graph with kernel equal to the central involution.

