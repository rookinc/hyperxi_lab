# Low-Block Parity Adjacency in the H_loc Transport Network
Date: 2026-03-14

## Purpose

Record the discovery that the low-energy block-transition network of the exact
local transport Hamiltonian is organized by parity adjacency in generator-sign
space.

This note builds on three prior observations:

1. low eigenspace blocks of H_loc carry exact generator-sign labels
2. primitive transport generators induce strong cross-block mixing
3. the resulting low-energy sector forms a weighted transport network

The new result is that the strongest reciprocal couplings are biased toward
pairs of blocks whose sign signatures differ by exactly one generator flip.

---

## Setup

For the first 20 eigenspace blocks of H_loc, each block was labeled by the
exact scalar action of the primitive generators:

    (F, S, V) ∈ {+I, -I}^3

This yields a discrete sign signature for each low block.

A weighted transition network was then built by summing the block-to-block
coupling norms induced by F, S, and V.

For each pair of blocks, the sign-signature Hamming distance was computed:

- distance 0 = same signature
- distance 1 = one generator sign differs
- distance 2 = two generator signs differ
- distance 3 = all three differ

---

## Main result

The low-block transition graph is biased toward parity-adjacent couplings.

More precisely, the strongest two-way couplings tend to connect block pairs
whose sign signatures differ by one bit.

This means the reduced low-energy transport network is not random: it is
organized by a discrete adjacency relation in sign space.

---

## Quantitative summary

Average symmetrized pair weights by signature Hamming distance:

- hamming = 0 : mean 0.266427, max 5.572495
- hamming = 1 : mean 0.556837, max 7.420306
- hamming = 2 : mean 0.374477, max 6.901026
- hamming = 3 : mean 0.000000, max 0.000000

The largest mean occurs at Hamming distance 1.

Thus, on average, the strongest low-energy partnerings are between blocks whose
generator-sign signatures differ by exactly one sign.

---

## Strong parity-adjacent partner pairs

Examples of strong Hamming-1 couplings:

### 1. blocks 6 and 19

    sym = 7.420306
    signatures:
        (-I, -I, -I) <-> (-I, -I, +I)

Only V changes sign.

---

### 2. blocks 10 and 20

    sym = 6.480588
    signatures:
        (+I, -I, -I) <-> (+I, +I, -I)

Only S changes sign.

---

### 3. blocks 11 and 18

    sym = 6.228434
    signatures:
        (+I, -I, -I) <-> (+I, +I, -I)

Only S changes sign.

---

### 4. blocks 1 and 8

    sym = 4.281185
    signatures:
        (-I, -I, -I) <-> (-I, +I, -I)

Only S changes sign.

---

### 5. blocks 3 and 7

    sym = 4.059037
    signatures:
        (-I, -I, -I) <-> (-I, +I, -I)

Only S changes sign.

---

## Interpretation

The low-energy transport structure behaves like a weighted graph on sign
characters of the primitive transport generators.

Each low block carries a signature in sign space, and the transport couplings
preferentially connect nearby signatures, especially one-sign-apart signatures.

A compact statement is:

    the low-energy transport algebra induces a parity-labeled transition
    graph with a nearest-neighbor bias in sign space

This is the first clear evidence that the reduced low-energy sector has a
coherent internal combinatorial geometry.

---

## Important nuance

The structure is not purely nearest-neighbor.

There are also strong Hamming-2 couplings, for example:

- blocks 5 <-> 15
- blocks 8 <-> 14

So the reduced transport graph is not a perfect cube graph or a strict
single-bit-flip graph.

However, the average coupling strength is clearly highest at Hamming distance 1,
and many of the strongest reciprocal couplings are parity-adjacent.

Thus parity adjacency is the dominant tendency, even if it is not the whole
story.

---

## What this means for the branch

The current reduced picture is now:

1. low H_loc blocks carry exact generator-sign labels
2. the primitive generators strongly couple different blocks
3. the strongest couplings are biased toward one-sign-apart blocks

So the emergent object is not an isolated set of sign sectors, but a coupled
internal-state network with a discrete parity geometry.

This is substantially more structured than the earlier chamber-holonomy story.

---

## Caution

This is not yet a spinor construction or an electron model.

What has been found is:

- a low-energy parity-labeled block network
- exact sign labels on blocks
- strong transport couplings between blocks
- an adjacency bias toward one-bit signature changes

What has not yet been shown is:

- a true SU(2) spin representation
- a double-cover construction
- a physical identification with electron spin or charge

So the correct present description is:

    low-block parity adjacency in the transport algebra

not yet a finished particle model.

---

## Immediate next step

The next natural move is to quotient the low-block transition graph by
signature class.

That means:

- merge blocks with the same sign signature
- sum transition weights between signature classes
- inspect the resulting signature-level graph

Suggested next script:

    scripts/build_signature_transition_quotient.py

This should reveal whether the low-energy internal geometry collapses to a
small canonical graph on the observed sign sectors.

---

## Working summary

Short version:

    the low-energy block-transition network of H_loc is organized by parity
    adjacency, with strongest couplings biased toward blocks whose generator
    sign signatures differ by one bit.

This is one of the clearest structural results obtained so far in the branch.

