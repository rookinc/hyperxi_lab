# Petersen Transport Skeleton in the Dodecahedral System

## Observation

The 15-vertex core graph emerging in the HyperXi transport construction is
isomorphic to the line graph of the Petersen graph:

    G_15 ≅ L(Petersen)

Properties:

- vertices: 15
- edges: 30
- degree: 4
- automorphism group: 120

This graph arises naturally when compressing transport relations in the
dodecahedral Petrie decagon system.

---

## Interpretation

The Petersen graph appears to function as the **opposition skeleton** of the
dodecahedral transport geometry.

Process:

    dodecahedron
        ↓
    Petrie decagon system
        ↓
    opposition / transport compression
        ↓
    Petersen skeleton
        ↓
    visible transport graph = L(Petersen)

The line-graph step reflects that the transport structure acts on
**channels between relations**, rather than on primary vertices.

Thus:

    Petersen graph → abstract opposition graph
    L(Petersen)    → transport-channel graph

---

## Structural Ladder

The observed constructions form a natural expansion ladder:

    Petersen skeleton
        ↓
    L(Petersen) (15 vertices)
        ↓
    signed 2-lift (30 vertices)
        ↓
    chamber graph / Thalean graph (60 vertices)

This sequence matches the doubling pattern observed in HyperXi experiments.

---

## Computational Result

Large-scale enumeration of signings of L(Petersen) edges with exactly
14 negative edges yielded:

    cycle parity signatures observed: 2^15 = 32768
    distinct lifted graphs:           1

Thus the signed 2-lift appears **rigid** under this constraint.

Interpretation:

- The 16-dimensional cycle space exhibits one linear constraint
  when restricted to the 14-negative-edge slice.
- Despite large variation in cycle parity assignments,
  the resulting lifted graph is invariant up to isomorphism.

This suggests the lift is **structurally forced** by the symmetry
of the Petersen skeleton.

---

## Research Implication

The Petersen graph is not imported into the construction.  
It emerges as the **irreducible transport skeleton** of the
dodecahedral chamber system.

The Thalean chamber graph can therefore be interpreted as a
canonical expansion of this skeleton.

In summary:

    dodecahedral transport
        ↓
    Petersen opposition skeleton
        ↓
    canonical lifted chamber geometry

