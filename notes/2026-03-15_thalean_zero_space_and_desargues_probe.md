# Thalean Graph — Structural Notes
Date: 2026-03-15

Context
-------
We are studying the graph:

G60 = true_chamber_graph.g6

Properties measured so far:

|V| = 60
|E| = 90
degree = 3 (cubic)

connected = True
bipartite = False
girth = 6
4-cycles = 0

So the graph is a **cubic girth-6 graph** with no triangles or squares.

This means locally the graph behaves like a 3-regular tree until length-6 closure.

That already makes it structurally rigid.

---

Metric expansion
----------------

Shell profile from any vertex:

(1,3,6,11,15,18,6)

Total = 60

So the graph is metrically homogeneous (all vertices share the same expansion).

This strongly suggests vertex-transitivity or near-transitivity.

The geometry behaves like a genuine transport manifold rather than an arbitrary construction.

---

Quotient structure
------------------

Earlier computation established:

G60 → G30 → G15

with

G15 ≅ L(Petersen)

So the Petersen graph appears in the deepest quotient.

However projection tests showed:

each vertex has a unique projection signature to the quotient.

Therefore the quotient does NOT determine the metric.

Conclusion:

The Petersen structure is a **symmetry shadow**, not the primary geometry.

The real geometry lives on the 60-vertex graph.

---

Spectrum
--------

Adjacency spectrum:

largest eigenvalue = 3
smallest eigenvalue ≈ −2.842235679

Important eigenvalues include:

±2
±1.618033988750
−0.618033988750

These belong to the field:

Q(√5)

This is the algebraic field underlying icosahedral/dodecahedral symmetry.

So the spectral algebra matches the dodecahedral origin of the construction.

---

Kernel of adjacency
-------------------

Dimension:

dim ker(A) = 10

This means there exist 10 independent vectors v with:

A v = 0

Interpretation:

balanced transport states where every vertex sees zero neighbor sum.

These are global equilibrium modes.

Important observation:

None of these modes are fiber-internal.

Every basis vector spreads across all 60 vertices.

Therefore the kernel is a **global structural sector**.

---

Automorphism action on kernel
------------------------------

Probing automorphisms on the zero space gave eigenvalues:

±1
exp(±2πi/5)
exp(±2πi/3)

So the zero eigenspace carries clean symmetry representations.

Observed structure strongly suggests:

kernel ≅ 5 ⊕ 5

(two 5-dimensional symmetry modules).

These are likely irreducible modules under the S5 symmetry backbone.

---

Automorphism structure
----------------------

Earlier measurements indicated:

Aut(G60) ≈ V4 ⋊ S5

So the S5 group appears naturally.

This is consistent with dodecahedral/Petersen combinatorics.

---

Hierarchy hypothesis
--------------------

Current working structural ladder:

Petersen (10 vertices)
        ↓
Desargues (20 vertices)
        ↓
Thalean transport lift (60 vertices)

Note:

60 = 3 × 20

This suggests the Thalean graph could be a 3-sheet lift of Desargues
with broken bipartite symmetry.

The automorphism orders are also suggestive:

|Aut(Desargues)| = 240
|Aut(Thalean)|  = 480

exactly double.

This supports the hypothesis that the Thalean graph is related to
a Desargues-derived structure.

---

Key open test
-------------

Check if the graph contains Desargues subgraphs.

Specifically:

Search for 20-vertex induced subgraphs isomorphic to Desargues.

If found, that would confirm a structural relationship.

Pseudo-script idea:

for each 20-vertex subset:
    check isomorphism with Desargues graph

This may require pruning heuristics because brute force is large.

---

Interpretation
--------------

The Thalean graph appears to be:

• cubic
• girth-6
• spectrally algebraic (√5 field)
• symmetry controlled
• with a 10-dimensional balanced sector

This combination is extremely uncommon among cubic graphs.

The structure looks more like a **transport geometry** than a random graph.

---

Open questions
--------------

1. What local generators produce the graph?
2. Does the Desargues relation hold?
3. What exactly is the representation carried by the kernel?
4. Is there a direct geometric interpretation of the zero modes?

---

Working interpretation

The Thalean graph is likely a **symmetry-controlled cubic transport manifold**
arising from dodecahedral flag transport.

The Petersen graph appears only as a quotient shadow.

The true geometry resides in the 60-vertex structure.

