# Signature Transition Quotient of the Low-Energy H_loc Sector
Date: 2026-03-14

## Purpose

Record the quotient-level structure obtained by collapsing the first 20
low-energy eigenspace blocks of the exact local transport Hamiltonian H_loc by
their generator-sign signatures.

This note summarizes the discovery that the reduced low-energy transport system
forms a sparse, local graph in sign space, with dominant couplings along
one-bit parity adjacencies and no observed three-bit jumps.

---

## Background

Earlier analysis established three facts:

1. the first 20 eigenspace blocks of H_loc carry exact generator-sign labels
2. the primitive transport generators F, S, and V strongly mix distinct blocks
3. the strongest blockwise couplings are biased toward pairs whose signatures
   differ by one sign flip

The next natural step was to quotient the low-block network by signature class.

That means:

- merge blocks with the same sign signature
- sum transition weights between signature classes
- inspect the reduced signature-level transport graph

---

## Observed signature classes

The first 20 low-energy blocks realize only 5 sign signatures:

- (+I,+I,-I)
- (+I,-I,-I)
- (-I,+I,-I)
- (-I,-I,+I)
- (-I,-I,-I)

Thus the low-energy sector occupies only a subset of the full sign cube
{±1}^3.

Observed block groupings:

- (+I,+I,-I) : blocks [18, 20]
- (+I,-I,-I) : blocks [10, 11, 12, 13, 14, 16, 17]
- (-I,+I,-I) : blocks [5, 7, 8]
- (-I,-I,+I) : blocks [15, 19]
- (-I,-I,-I) : blocks [1, 2, 3, 4, 6, 9]

---

## Main quotient result

The signature-level quotient graph is highly local in sign space.

Top symmetrized signature couplings:

- (+I,-I,-I) <-> (-I,-I,-I)   weight 17.574404   hamming 1
- (+I,-I,-I) <-> (-I,+I,-I)   weight 12.946266   hamming 2
- (+I,+I,-I) <-> (+I,-I,-I)   weight 12.709022   hamming 1
- (-I,-I,+I) <-> (-I,-I,-I)   weight 12.605363   hamming 1
- (-I,+I,-I) <-> (-I,-I,-I)   weight  8.340223   hamming 1
- (-I,+I,-I) <-> (-I,-I,+I)   weight  6.901026   hamming 2

No hamming-3 coupling was observed.

---

## Quantitative summary by Hamming distance

Signature-pair weights grouped by sign-distance:

- hamming = 1 : count 5, mean 10.245802, max 17.574404
- hamming = 2 : count 4, mean  4.961823, max 12.946266
- hamming = 3 : count 1, mean  0.000000, max  0.000000

So the quotient graph is dominated by one-bit adjacency.

This is stronger than the earlier block-pair result, because the same tendency
survives after quotienting away within-signature multiplicities.

---

## Structural interpretation

The low-energy transport sector behaves like a sparse local graph on the
observed subset of sign-space vertices.

The signature

    (-I,-I,-I)

acts as a strong hub, with dominant couplings to its one-bit neighbors:

- (+I,-I,-I)
- (-I,+I,-I)
- (-I,-I,+I)

This is exactly the local adjacency pattern expected in a cube-like sign
geometry.

However, the observed quotient is not the full cube. Only 5 signature classes
appear, and some Hamming-2 couplings are still present. So the structure is
better described as a **truncated local cube** or **partial sign complex**.

---

## Most important conclusion

A clean compressed statement is:

    the low-energy signature quotient of H_loc forms a sparse local graph in
    generator-sign space, with dominant transport along one-bit parity
    adjacencies and no observed three-bit jumps.

This is one of the clearest emergent combinatorial structures found so far in
the branch.

---

## Why this matters

This quotient is significant because it is:

- reduced
- stable
- interpretable
- tied directly to the primitive transport generators

It is no longer just a collection of spectral facts. It is an emergent internal
transition geometry for the low-energy sector.

That makes it a much better candidate for future effective modeling than raw
chamber holonomy or isolated transport words.

---

## Caution

This is not yet a spinor or electron model.

What has been shown:

- exact sign signatures on low-energy blocks
- strong transport couplings between those blocks
- nearest-neighbor bias in sign space
- a reduced signature-level transition graph

What has not been shown:

- SU(2) spin structure
- a double-cover representation
- physically calibrated particle observables

So the right current language is:

    low-energy signature transition quotient

not yet a completed particle theory.

---

## Immediate next move

The next useful step is visualization.

Suggested script:

    scripts/plot_signature_quotient.py

This should place the observed sign signatures at their cube coordinates in
{±1}^3 and draw weighted edges for the quotient couplings. That will make the
internal low-energy geometry visually legible.

---

## Working summary

Short version:

    the first 20 low-energy blocks of H_loc collapse to 5 observed
    generator-sign classes, and the resulting quotient graph is locally
    organized by one-bit parity adjacency, with no direct three-bit jumps.

