# Signature Cycle Structure of the Low-Energy Quotient Walk
Date: 2026-03-14

## Purpose

Record the short-cycle structure of the 5-state signature random walk obtained
from the low-energy H_loc transport quotient.

Earlier reductions showed:

1. exact generator-sign labels on low-energy blocks
2. a 5-state signature quotient graph
3. an ergodic random walk with stationary weight concentrated on the pair
   (+I,-I,-I) and (-I,-I,-I)

This note adds the next layer: the quotient dynamics is organized not only by
dominant states, but also by preferred reversible channels and short directed
circulation loops.

---

## Quotient states

The 5 realized signature states are:

- (+I,+I,-I)
- (+I,-I,-I)
- (-I,+I,-I)
- (-I,-I,+I)
- (-I,-I,-I)

These form the low-energy parity manifold extracted from the first 20
eigenspace blocks of H_loc.

---

## Main result

The quotient walk exhibits a small set of dominant 2-cycles, 3-cycles, and
4-cycles. The strongest short loops are concentrated around the same two-state
core identified by the stationary distribution:

- (+I,-I,-I)
- (-I,-I,-I)

The remaining states act as feeder and circulation states attached to this core.

---

## Dominant 2-cycles

Top nonzero 2-cycles:

1. (+I,+I,-I) -> (+I,-I,-I) -> (+I,+I,-I)
   p = 0.234678

2. (-I,-I,+I) -> (-I,-I,-I) -> (-I,-I,+I)
   p = 0.182330

3. (+I,-I,-I) -> (-I,-I,-I) -> (+I,-I,-I)
   p = 0.115447

4. (+I,-I,-I) -> (-I,+I,-I) -> (+I,-I,-I)
   p = 0.101928

5. (-I,+I,-I) -> (-I,-I,+I) -> (-I,+I,-I)
   p = 0.086494

These identify the strongest reversible transport channels in the quotient walk.

---

## Dominant 3-cycles

Top nonzero 3-cycles:

1. (-I,+I,-I) -> (-I,-I,+I) -> (-I,-I,-I) -> (-I,+I,-I)
   p = 0.030708

2. (+I,-I,-I) -> (-I,-I,-I) -> (-I,+I,-I) -> (+I,-I,-I)
   p = 0.026554

3. (-I,+I,-I) -> (-I,-I,-I) -> (-I,-I,+I) -> (-I,+I,-I)
   p = 0.023949

4. (+I,-I,-I) -> (-I,+I,-I) -> (-I,-I,-I) -> (+I,-I,-I)
   p = 0.020665

So the feeder states do not just drain passively into the core. They
participate in genuine directed circulation loops.

---

## Dominant 4-cycles

Top nonzero 4-cycles:

1. (+I,-I,-I) -> (-I,-I,-I) -> (-I,-I,+I) -> (-I,+I,-I) -> (+I,-I,-I)
   p = 0.013637

2. (+I,-I,-I) -> (-I,+I,-I) -> (-I,-I,+I) -> (-I,-I,-I) -> (+I,-I,-I)
   p = 0.013608

These are especially important because they show a coherent circulation around
the low-energy sign manifold, rather than just back-and-forth exchange.

---

## Strongest outgoing edge per state

The strongest directed move from each signature is:

- (+I,+I,-I) -> (+I,-I,-I)    p = 1.000000
- (+I,-I,-I) -> (-I,-I,-I)    p = 0.344075
- (-I,+I,-I) -> (+I,-I,-I)    p = 0.456261
- (-I,-I,+I) -> (-I,-I,-I)    p = 0.677310
- (-I,-I,-I) -> (+I,-I,-I)    p = 0.335529

This makes the core channel

    (+I,-I,-I) <-> (-I,-I,-I)

the central exchange path of the quotient dynamics.

---

## Interpretation

The effective 5-state transport system is best described as:

- a dominant two-state core
- two feeder/circulation states
- one peripheral deterministic feeder state
- a small family of preferred short loops

So the reduced dynamics is not merely a hub-and-spoke system. It is a
low-energy parity manifold with a core exchange channel and attached
circulation loops.

---

## Working picture

A compact description is:

    the low-energy signature quotient supports a dominant two-sector exchange
    channel together with short directed circulation loops through the feeder
    states (-I,+I,-I) and (-I,-I,+I)

This sharpens the earlier stationary-distribution result.

---

## Caution

The current cycle scan shows many near-zero cycles because it also records loops
with vanishing transition products. Those should be suppressed in future runs by
thresholding cycle probabilities.

The nonzero top cycles listed above are the meaningful ones.

---

## Immediate next step

The next practical refinement is:

1. patch the cycle script to suppress zero-probability cycles
2. fit a small effective operator on the 5 signature states

Suggested next script:

    scripts/fit_effective_signature_hamiltonian.py

That would turn the quotient walk into a compact effective model that can be
compared back to the transport algebra.

---

## Working summary

Short version:

    the low-energy signature random walk is organized by a dominant two-state
    core and a small set of nontrivial 3- and 4-cycle circulation loops,
    revealing that the reduced quotient has genuine internal transport
    structure rather than only hub-like flow.

