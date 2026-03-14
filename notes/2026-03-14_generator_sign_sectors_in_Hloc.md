# Generator Sign Sectors in the Low Spectrum of H_loc
Date: 2026-03-14

## Purpose

Record the discovery that low eigenspaces of the exact local transport
Hamiltonian organize into repeated generator-sign sectors.

This note summarizes the result that, on many low spectral blocks, the
primitive transport generators

- F
- S
- V

act blockwise as exact scalar signs:

    +I  or  -I

This is stronger than the earlier observation that certain transport words act
as exact sign flips. It shows that the sign structure is already present at the
level of the primitive generator action.

---

## Setup

The operator under study is the exact local transport Hamiltonian on the
120-flag space:

    H_loc = a_F (U_F + U_F^T) + a_S U_S + a_V (U_V + U_V^T)

Using the low eigenspace blocks of H_loc, the projected action of each
primitive generator was computed blockwise and reduced to its polar unitary
factor.

For each low block E, the signatures

    F|_E, S|_E, V|_E

were classified as +I or -I whenever exact scalar behavior occurred.

---

## Main result

The low spectrum of H_loc decomposes into repeated sign sectors.

Observed generator-sign signatures include:

- (-I, -I, -I)
- (-I, +I, -I)
- (+I, -I, -I)
- (-I, -I, +I)
- (+I, +I, -I)

Thus many low eigenspaces are not merely invariant under the generator action;
they realize exact scalar sign representations of the transport generators.

---

## Concrete table

Low-block signatures observed:

| block | lambda | dim | F | S | V |
|------:|-------:|----:|---|---|---|
| 1  | -3.604098602642 | 5 | -I | -I | -I |
| 2  | -3.503750202148 | 3 | -I | -I | -I |
| 3  | -3.465216171088 | 5 | -I | -I | -I |
| 4  | -3.041788781337 | 4 | -I | -I | -I |
| 5  | -2.048548180684 | 3 | -I | +I | -I |
| 6  | -1.872276212853 | 4 | -I | -I | -I |
| 7  | -1.611941594255 | 5 | -I | +I | -I |
| 8  | -1.585267861491 | 5 | -I | +I | -I |
| 9  | -1.370325945476 | 4 | -I | -I | -I |
| 10 | -1.190400513396 | 3 | +I | -I | -I |
| 11 | -1.131769504959 | 3 | +I | -I | -I |
| 12 | -1.108775539292 | 4 | +I | -I | -I |
| 13 | -1.000000000000 | 5 | +I | -I | -I |
| 14 | -0.717106616535 | 5 | +I | -I | -I |
| 15 | -0.407667082239 | 3 | -I | -I | +I |
| 16 | -0.126518469421 | 3 | +I | -I | -I |
| 17 |  0.278637824610 | 5 | +I | -I | -I |
| 18 |  0.498198463082 | 3 | +I | +I | -I |
| 19 |  0.796815115870 | 4 | -I | -I | +I |
| 20 |  0.901071116910 | 3 | +I | +I | -I |

---

## Structural families

Several repeated sign families appear.

### Family A — fully odd sectors

Signature:

    (F, S, V) = (-I, -I, -I)

Examples:

- blocks 1, 2, 3, 4, 6, 9

These are maximally sign-flipped sectors.

---

### Family B — F and V odd, S even

Signature:

    (F, S, V) = (-I, +I, -I)

Examples:

- blocks 5, 7, 8

---

### Family C — S and V odd, F even

Signature:

    (F, S, V) = (+I, -I, -I)

Examples:

- blocks 10, 11, 12, 13, 14, 16, 17

This is one of the most persistent low-energy families.

---

### Family D — F and S odd, V even

Signature:

    (F, S, V) = (-I, -I, +I)

Examples:

- blocks 15, 19

---

### Family E — only V odd

Signature:

    (F, S, V) = (+I, +I, -I)

Examples:

- blocks 18, 20

---

## Interpretation

The low eigenspaces of H_loc behave like discrete sign sectors of the transport
algebra.

A compact way to say this is:

    low spectral blocks realize generator-sign representations

with

    F|_E, S|_E, V|_E ∈ {+I, -I}

for many low blocks E.

This means the earlier exact sign-flip words are not accidental. They arise
because the low spectral decomposition already carries primitive sign structure.

---

## Why this matters

This is the strongest algebraic result so far in the branch.

Earlier results showed:

- chamber-cycle holonomy gives small SO(3)-type rotations
- transport-word scans produce exact -I on some low blocks

The present result goes further:

- the primitive generators themselves act as exact signs on many low blocks
- the low spectrum decomposes into repeated parity-like sectors
- the transport algebra therefore has a structured low-energy sign
  representation theory

This is more electron-adjacent than the chamber-holonomy story, because exact
sign behavior appears directly in the transport algebra.

---

## Important caution

This is not yet a complete spin-1/2 construction.

What has been shown:

- exact scalar sign action of F, S, V on many low blocks
- repeated low-energy sign families
- exact sign-flip words explained by primitive sign structure

What has not yet been shown:

- a full double-cover construction
- an irreducible complex spinor sector
- a direct physical interpretation as electron spin
- coupling to charge or mass observables

So this should presently be described as:

    generator sign sectors in the low spectrum of H_loc

rather than a finished fermion model.

---

## Immediate next question

Are these blocks merely scalar sign-character sectors, or is there deeper
residual structure underneath?

That leads to the next test:

    scripts/check_blockwise_commutators.py

which should verify whether the projected generator actions:

- commute blockwise
- remain scalar signs exactly
- or contain hidden noncommutative residual structure beyond the sign layer

---

## Working summary

Current picture:

1. chamber-cycle holonomy produces small rotational transport
2. transport-word scans show exact sign flips
3. blockwise generator analysis reveals repeated low-energy sign sectors

Short version:

    the low spectrum of H_loc decomposes into coherent generator-sign sectors,
    making the transport algebra the strongest current source of proto-spin
    structure in the HyperXi branch.

