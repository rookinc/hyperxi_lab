# HyperXi Lab Log
## 2026-03-13
### Petersen Core and Transport Holonomy

This note summarizes the full chain of discoveries made today in the HyperXi Lab exploration of the Thalean transport system derived from dodecahedral chamber transport.

The purpose of this document is to preserve the logical thread of the investigation so that work can resume tomorrow without reconstructing intermediate reasoning.

---------------------------------------------------------------------

# 1. Initial Objective

The working hypothesis was that the chamber transport system derived from Petrie transport on the dodecahedron produces a nontrivial combinatorial structure that might encode a discrete analogue of spinorial holonomy.

The central objects under study are the graphs:

G60  — chamber graph
G30  — transport lift
G15  — quotient core

with the covering tower

G60 → G30 → G15

---------------------------------------------------------------------

# 2. Recovery of the 15-core

Computational probes confirmed:

vertices: 15
edges: 30
degree: 4

Further analysis showed:

G15 ≅ L(Petersen)

i.e.

the 15-vertex core is the **line graph of the Petersen graph**.

This identification is canonical and arises naturally from the opposite-edge pairing structure of the dodecahedron.

---------------------------------------------------------------------

# 3. Structure of the 15-core

Properties of G15:

• 15 vertices  
• 30 edges  
• degree 4  
• exactly 12 pentagonal cycles  

Under the identification

G15 ≅ L(Petersen)

these 12 pentagons correspond exactly to the 12 five-cycles of the Petersen graph.

Thus the canonical cycle structure of G15 is inherited from Petersen geometry.

---------------------------------------------------------------------

# 4. Transport Lift

The next layer in the construction is

G30 → G15

which is a **signed 2-lift**.

The induced signing on the 30 edges of G15 is:

16 positive
14 negative

This signing arises directly from the geometric transport rule inherited from the dodecahedral chamber system.

---------------------------------------------------------------------

# 5. Pentagon Holonomy

The 12 pentagons of G15 were classified using the transport sign.

Result:

6 odd pentagons
6 even pentagons

Parity is defined by the XOR of edge signs along the cycle.

Interpretation:

even cycle → trivial lift
odd cycle  → sheet swap

Thus traversal of an odd pentagon produces a nontrivial lift holonomy.

Two traversals return to the starting sheet.

This is the discrete analogue of the familiar

2π / 4π spinorial phenomenon.

---------------------------------------------------------------------

# 6. Key Structural Insight

The transport signing does **not create the pentagons**.

Instead it **polarizes the canonical Petersen pentagon system**.

Thus:

12 Petersen pentagons
↓
6 even
6 odd

Only the odd pentagons carry nontrivial holonomy.

---------------------------------------------------------------------

# 7. Full Covering Tower

The discovered structure can now be summarized as

G60  chamber graph
│
│ V₄ lift
│
G30  signed transport lift
│
│ 2-lift
│
G15 ≅ L(Petersen)

This forms the combinatorial skeleton of the Thalean transport model.

---------------------------------------------------------------------

# 8. Interpretation

The key object is not merely the graph L(Petersen) itself, but the pair

(L(Petersen), σ_transport)

where σ_transport is the ℤ₂ connection induced by chamber transport.

The spinorial behaviour arises from the holonomy of this connection.

---------------------------------------------------------------------

# 9. Small Graph Probe

A probe over several small candidate graphs was performed to test whether this phenomenon appears generically.

Candidates tested included:

Petersen
dodecahedral
desargues
heawood
cubical
tetrahedral
octahedral
icosahedral
line_K4
line_K5
line_petersen
line_cubical

Result:

No generic graph exhibited the same odd/even pentagon structure under arbitrary edge signings.

Conclusion:

The phenomenon is **not intrinsic to the bare graph**.

It is **transport-induced**.

---------------------------------------------------------------------

# 10. Final Structural Result

The Thalean transport system produces a distinguished signed Petersen line graph with nontrivial pentagonal holonomy.

In particular:

• G15 is canonically L(Petersen)
• the transport lift induces a ℤ₂ connection on G15
• the 12 Petersen pentagons split into 6 odd and 6 even cycles
• the odd pentagons carry the nontrivial holonomy

This completes the structural identification of the core combinatorics of the model.

---------------------------------------------------------------------

# 11. Status

Mathematically the discrete transport model is now internally coherent.

It provides:

• a canonical core graph  
• a nontrivial lift  
• a natural holonomy structure  

Whether this has physical interpretation remains an open question.

---------------------------------------------------------------------

# 12. Possible Next Steps

Potential directions for further investigation:

1. Formalize the transport sign as a cohomology class on L(Petersen)

2. Characterize the automorphism group of the signed graph

3. Investigate whether the six odd pentagons generate the full holonomy group

4. Study the relationship between the chamber graph G60 and known regular covers

5. Explore whether similar structures appear in other Platonic chamber systems

---------------------------------------------------------------------

# End of Log
