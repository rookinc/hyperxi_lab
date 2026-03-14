# Thalean Graph as a 4-Lift of a 15-Vertex Core

Author: Scott Allen Cave
Date: 2026-03-13

This note records a structural observation about the Thalean graph
arising from Petrie transport on the flag space of the dodecahedron.

This is an internal research note and not yet part of the formal paper.

---

MAIN OBSERVATION

The 60-vertex Thalean graph is a regular 4-lift of a 15-vertex base graph.

This was verified computationally.

The lift structure appears through the antipodal quotient tower

60 -> 30 -> 15

where:

- the first antipodal quotient produces a 30-vertex graph
- the second antipodal quotient produces a 15-vertex graph

The 60-vertex graph then reconstructs as a regular 4-cover of this
15-vertex core.

---

CORE GRAPH (15 VERTICES)

Vertices: 15
Edges: 30
Degree: 4
Diameter: 3
Triangles: 10

Shell profile:

(1,4,8,2)

Spectrum:

4^1
2^5
(-1)^4
(-2)^5

Canonical graph6:

Nto`GCJAIAAHPA@CaAg

---

LIFT STRUCTURE

The probe produced the following properties.

Fiber structure:

15 fibers of size 4

fiber size histogram: {4: 15}

No edges occur within a fiber.

Each edge of the 15-vertex base graph lifts to exactly 4 edges in the
60-vertex graph.

edge multiplicity histogram: {4: 30}

Local adjacency pattern for every vertex in the 60-graph:

neighbor-to-fiber pattern: (1,1,1,1)

Thus each vertex connects to exactly one vertex in each of the four
adjacent base fibers.

---

CONSEQUENCE

The Thalean graph is a regular covering graph

G60 -> G15

with covering degree

4.

The 30-vertex graph arises naturally as an intermediate antipodal
quotient.

---

STRUCTURAL SUMMARY

Graph hierarchy:

15-vertex core graph
↓ regular 4-lift
60-vertex Thalean graph
↓ antipodal quotient
30-vertex intermediate graph

Invariant ladder:

Vertices:

15 -> 30 -> 60

Edges:

30 -> 60 -> 120

Triangles:

10 -> 20 -> 40

Degree remains constant (4) at every level.

---

OPEN QUESTIONS

1. Is the 15-vertex core graph catalogued in standard graph tables?
2. Can the 4-lift be described by an explicit voltage assignment?
3. Is the lift induced directly by dodecahedral flag symmetries?
4. Does the same lift structure appear for other regular polyhedra?

