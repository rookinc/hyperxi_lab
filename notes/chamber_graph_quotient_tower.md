# Chamber Graph Quotient Tower

Date: 2026-03-14
Project: HyperXi Lab

---

## Result

The 60-vertex chamber graph recovered from the true dodecahedral flag incidence model admits a canonical antipodal quotient.

Construction:

- upstairs graph: the 60-vertex chamber graph obtained from the 120 lawful flags by quotienting by S and inducing adjacency by V
- antipodal pairing: vertices paired by unique distance-6 partners

This produces a quotient graph on 30 vertices.

---

## Chamber Graph Invariants

- vertices: 60
- edges: 120
- degree: 4
- triangles: 40
- diameter: 6
- shell profile: (1,4,8,16,24,6,1)

---

## Antipodal Quotient Invariants

- vertices: 30
- edges: 60
- degree: 4
- triangles: 20
- diameter: 5
- shell profile: (1,4,8,12,4,1)

---

## Covering Structure

The antipodal projection is a genuine regular 2-cover.

Observed computationally:

- pair count: 30
- edge multiplicity histogram over quotient edges: {2: 60}
- covering test: True

So every quotient edge lifts to exactly two upstairs edges.

---

## Structural Interpretation

This places the chamber graph in the quotient tower:

60-vertex chamber graph
    ↓ antipodal quotient
30-vertex quartic graph
    ↓ further quotient
15-core

Earlier work identified the 15-core as isomorphic to the line graph of the Petersen graph.

Thus the chamber graph is naturally a two-step binary lift over the Petersen-derived core.

---

## Status

Confirmed computationally via:

scripts/check_chamber_graph_as_4cover_of_15core.py

Next step:

Compare the reconstructed 30-vertex quotient directly against the previously identified 30-layer graph, and verify that its next quotient recovers the known 15-core.

