# Effective Signature Operator for the Low-Energy Quotient
Date: 2026-03-14

## Purpose

Record the discovery that the 5-state low-energy signature quotient admits a
compact effective operator description whose ground state closely matches the
stationary distribution of the quotient random walk.

This note synthesizes the previous reductions:

1. low H_loc eigenspace blocks carry exact generator-sign labels
2. these blocks collapse to a 5-state signature quotient
3. the quotient supports an ergodic random walk with a dominant two-state core
4. the quotient also admits a symmetric effective coupling operator

The key new result is that the spectral ground state of the effective operator
almost coincides with the dynamical stationary state of the quotient walk.

---

## Effective model

Let A be the symmetrized coupling matrix on the 5 observed sign sectors, and
define the effective Hamiltonian-like operator

    H_eff = -A

This choice makes strong couplings energetically favorable.

For the signature ordering

0. (+I,+I,-I)
1. (+I,-I,-I)
2. (-I,+I,-I)
3. (-I,-I,+I)
4. (-I,-I,-I)

the symmetric coupling matrix is:

    [ 0.000000  12.709022   0.000000   0.000000   0.000000 ]
    [12.709022   0.000000  12.946266   0.000000  17.574404 ]
    [ 0.000000  12.946266   0.000000   6.901026   8.340223 ]
    [ 0.000000   0.000000   6.901026   0.000000  12.605363 ]
    [ 0.000000  17.574404   8.340223  12.605363   0.000000 ]

---

## Main spectral result

The effective Hamiltonian has eigenvalues:

- -32.024265
-  -7.033483
-   4.525392
-   9.008382
-  25.523973

So the ground energy is

    E0 = -32.024265

with first gap

    Δ = 24.990782

This is a large separation, indicating a clearly dominant collective mode.

---

## Ground-state weights

The effective ground-state weights on the signatures are:

- (+I,-I,-I) : 0.271557
- (-I,-I,-I) : 0.262166
- (-I,+I,-I) : 0.210050
- (-I,-I,+I) : 0.148458
- (+I,+I,-I) : 0.107769

This reproduces the same hierarchy already seen dynamically:

- dominant core:
  - (+I,-I,-I)
  - (-I,-I,-I)

- secondary feeder:
  - (-I,+I,-I)

- weaker feeder:
  - (-I,-I,+I)

- peripheral state:
  - (+I,+I,-I)

---

## Comparison to stationary distribution

The stationary distribution of the quotient random walk was:

- (+I,-I,-I) : 0.318163
- (-I,-I,-I) : 0.313011
- (-I,+I,-I) : 0.165530
- (-I,-I,+I) : 0.128631
- (+I,+I,-I) : 0.074666

Comparison metrics:

- overlap(|gs>, sqrt(pi)) = 0.997218
- corr(gs_weights, pi)    = 0.966954

This is the strongest compression result so far in the branch.

It means the effective spectral ground state and the dynamical stationary state
are essentially the same reduced object.

---

## Interpretation

The 5-state parity manifold has a coherent dual description:

1. dynamical description
   - stationary transport on the quotient walk

2. spectral description
   - ground state of the effective operator H_eff = -A

Since these two views nearly coincide, the quotient is not merely a visual or
combinatorial reduction. It behaves like a genuine effective low-energy model.

---

## Laplacian diagnostics

The quotient graph also has:

- combinatorial Laplacian gap: 10.917204
- normalized Laplacian gap   : 0.639442

So the graph is:

- connected
- well mixed
- nontrivial
- spectrally structured

This supports the conclusion that the quotient has real internal organization.

---

## Lowest modes

The ground mode of H_eff is broadly positive across all states, with strongest
support on the core pair:

- (+I,-I,-I)
- (-I,-I,-I)

The first excited mode separates the peripheral / feeder structure from the core,
and the second excited mode begins to resolve contrasts among feeder sectors.

So the effective operator appears to encode not only the stationary core, but
also a meaningful hierarchy of internal deformations of the quotient state space.

---

## Best current statement

A compact summary is:

    the low-energy signature quotient admits a compact effective Hamiltonian
    whose ground state almost exactly matches the stationary distribution of
    the quotient random walk, indicating that the reduced parity manifold has
    a coherent spectral-dynamical description

This is one of the clearest results obtained in the project so far.

---

## Why this matters

This upgrades the quotient from an interesting reduced graph to a usable model
candidate.

The branch now has:

1. exact sign sectors
2. a 5-state quotient manifold
3. ergodic quotient dynamics
4. short-cycle circulation structure
5. an effective operator with a matching ground state

That is a substantial compression of the original transport algebra.

---

## Immediate next step

The next natural move is mode visualization.

Suggested script:

    scripts/plot_signature_modes.py

This should display on the 5-node quotient graph:

- stationary distribution
- effective ground-state weights
- first excited mode
- second excited mode

That will make the mode structure visually legible and help identify whether
the excited states correspond to core-vs-feeder splitting, parity splitting,
or circulation structure.

---

## Working summary

Short version:

    the effective 5x5 signature operator captures the same dominant low-energy
    structure as the quotient random walk, with a ground state concentrated on
    the same two-sector core and nearly identical to the stationary transport
    distribution.

