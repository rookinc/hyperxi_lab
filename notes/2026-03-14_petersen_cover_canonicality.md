# Petersen Skeleton and Canonical Lift Hypothesis
Scott Allen Cave
HyperXi Lab — CoRI
2026-03-14

## Context

In the HyperXi transport study of the dodecahedral flag space, several layers of structure have appeared repeatedly:

1. dodecahedral chamber transport
2. a 15-vertex quotient ("15-core")
3. identification of this core with L(Petersen)
4. a 30-vertex signed 2-lift
5. the 60-vertex Thalean chamber graph

The purpose of this note is to record a computational observation suggesting that the intermediate signed lift may be **canonical** rather than an arbitrary choice.

---

## Computation performed

We enumerated signings of the 30 edges of

    G = L(Petersen)

with exactly:

    14 negative edges
    16 positive edges

Total search space:

    C(30,14) = 145,422,675 signings

For each signing:

1. compute cycle parity signature (Z₂)
2. construct the signed 2-lift
3. compute the WL hash of the lifted graph

---

## Empirical result (millions of samples)

Across millions of tested signings:

distinct_lift_hashes = 1

while

cycle_signatures ≈ 32768 = 2^15

Thus:

- many distinct parity configurations
- a single lifted graph

This suggests that the signed lifts in this slice collapse to **one isomorphism class**.

---

## Interpretation

The result indicates that the sign assignment behaves more like a **coordinate system on a fixed cover** than a generator of different graphs.

In other words:

many micro signings
→ same lifted geometry

This strongly hints that the relevant 30-vertex lift is **intrinsically determined by the Petersen skeleton**, not by the specific signing.

---

## Transport tower picture

The emerging structural ladder becomes:

dodecahedron
→ Petrie transport system
→ 15-core
≅ L(Petersen)
→ canonical signed 2-lift (30 vertices)
→ Thalean chamber graph (60 vertices)

Thus the Petersen line graph appears to function as a **compressed transport skeleton**, while the lift restores the twist degrees of freedom required for chamber transport.

---

## Hypothesis

The 30-vertex lift observed in the Thalean construction is the **canonical nontrivial cover of L(Petersen) compatible with dodecahedral Petrie transport**.

If true, then:

- the signing data is not fundamental
- the cover itself is geometrically forced

---

## Connection to recursive emergence

This structure mirrors a broader pattern appearing in the Spirelica framework:

many micro configurations
→ constrained macro geometry

In both cases the observable structure emerges only after quotienting or cumulative composition.

---

## Next tests

1. Derive the signing directly from Petrie transport.
2. Compare the resulting cover with the lift class observed in the rigidity experiment.
3. Attempt a theoretical explanation via:
   - switching equivalence classes
   - automorphism group of L(Petersen)
   - Z₂ cycle cohomology

If the Petrie-derived signing lies in the same lift class, the Thalean graph may represent a **forced geometric expansion of the Petersen skeleton**.

---

## Status

Current evidence: computational (millions of samples)

Next step: structural explanation.

