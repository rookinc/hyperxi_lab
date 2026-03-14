# Petersen Graph as Minimal Pentagonal Transport Witness

## Motivation

In the HyperXi transport experiments, the compressed 15-vertex core
graph appears as:

    G_15 ≅ L(Petersen)

This repeatedly emerges when dodecahedral Petrie transport relations
are quotiented and simplified.

This note records a structural interpretation of why the Petersen graph
appears naturally in this context.

---

## Pentagonal Transport Tension

The regular dodecahedron is built entirely from pentagonal faces.
Pentagonal systems exhibit a fundamental transport tension:

- 5-cycles introduce odd closure
- odd cycles prevent bipartite flattening
- recursive transport cannot settle into a flat periodic lattice

This creates a combinatorial analogue of curvature: transport can
circulate locally but cannot globally flatten without conflict.

We refer to this phenomenon informally as **pentagonal transport
frustration**.

---

## The Petersen Graph as a Minimal Witness

The Petersen graph has the following properties:

    vertices: 10
    degree:   3 (cubic)
    girth:    5

It is:

- small
- highly symmetric
- saturated with 5-cycles
- non-planar

Among small cubic graphs, Petersen is the smallest structure that
retains a robust pentagonal cycle structure while resisting reduction
to simpler planar or bipartite transport systems.

For this reason it can be viewed heuristically as a **minimal witness
of pentagonal transport tension**.

---

## Why the Line Graph Appears

The HyperXi transport construction does not operate on raw vertices of
this opposition structure, but on **transport channels between
relations**.

The line graph transformation converts edges of the Petersen skeleton
into vertices representing transport channels:

    Petersen → opposition skeleton
    L(Petersen) → transport-channel skeleton

Thus the 15-core graph records how these transport channels interact.

---

## Structural Ladder Observed in Computation

Experiments reveal the following expansion sequence:

    Petersen skeleton (10 vertices)
        ↓
    L(Petersen) transport core (15 vertices)
        ↓
    signed 2-lift (30 vertices)
        ↓
    chamber / Thalean graph (60 vertices)

Large-scale enumeration of signings on L(Petersen) with 14 negative
edges produced:

    cycle parity states observed: 2^15
    distinct lifted graphs:       1

indicating strong structural rigidity in the lift.

---

## Interpretation

The Petersen graph does not appear to be inserted artificially into
the construction. Instead it emerges as the **irreducible opposition
skeleton of the dodecahedral transport system** once redundant
structure is quotiented away.

The Thalean chamber graph can therefore be interpreted as a canonical
expansion of this skeleton through successive lifting operations.

---

## Status

The statements in this note are structural interpretations supported by
computational evidence. Formal theorems relating Petersen structure to
dodecahedral Petrie transport remain an open direction.

