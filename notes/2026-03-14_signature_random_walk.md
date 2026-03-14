# Signature Random Walk on the Low-Energy Transport Quotient
Date: 2026-03-14

## Purpose

Record the Markov dynamics of the low-energy signature-transition quotient.

Earlier work produced a 5-state quotient graph by collapsing the first 20
eigenspace blocks of H_loc according to their exact generator-sign signatures.
The quotient graph showed strong locality in sign space and dominant one-bit
parity couplings.

This note records the next result: the quotient graph is not only geometric,
but dynamically coherent. Its normalized transport defines an ergodic random
walk with a stable stationary distribution concentrated on a dominant two-state
core.

---

## Quotient states

The observed low-energy sign sectors are:

- (+I,+I,-I)
- (+I,-I,-I)
- (-I,+I,-I)
- (-I,-I,+I)
- (-I,-I,-I)

These form a sparse subset of the sign cube {±1}^3.

---

## Transition matrix

The row-normalized transition matrix is:

    (+I,+I,-I) -> (+I,-I,-I) with probability 1.000000

    (+I,-I,-I) distributes into:
        (+I,+I,-I)  0.234678
        (+I,-I,-I)  0.197849
        (-I,+I,-I)  0.223398
        (-I,-I,-I)  0.344075

    (-I,+I,-I) distributes into:
        (+I,-I,-I)  0.456261
        (-I,-I,+I)  0.268042
        (-I,-I,-I)  0.275697

    (-I,-I,+I) distributes into:
        (-I,+I,-I)  0.322690
        (-I,-I,-I)  0.677310

    (-I,-I,-I) distributes into:
        (+I,-I,-I)  0.335529
        (-I,+I,-I)  0.169147
        (-I,-I,+I)  0.269198
        (-I,-I,-I)  0.226126

---

## Main result

The random walk has a unique stable stationary distribution:

- (+I,-I,-I) : 0.318163
- (-I,-I,-I) : 0.313011
- (-I,+I,-I) : 0.165530
- (-I,-I,+I) : 0.128631
- (+I,+I,-I) : 0.074666

So the long-time dynamics is concentrated primarily on the pair:

- (+I,-I,-I)
- (-I,-I,-I)

These two states together carry about 63.1% of the stationary weight.

---

## Interpretation

This means the quotient graph has:

- a geometric hub structure in raw edge weights
- but a dynamical core pair in normalized transport

The state (-I,-I,-I) was the strongest raw hub in the signature graph, but
after normalization the long-time transport is shared almost equally with
(+I,-I,-I).

Thus the correct reduced dynamical picture is not a single-center hub, but a
two-sector attractor core with side feeder states.

---

## Dominant directed transitions

Largest directed transition probabilities:

1. (+I,+I,-I) -> (+I,-I,-I)   p = 1.000000
2. (-I,-I,+I) -> (-I,-I,-I)   p = 0.677310
3. (-I,+I,-I) -> (+I,-I,-I)   p = 0.456261
4. (+I,-I,-I) -> (-I,-I,-I)   p = 0.344075
5. (-I,-I,-I) -> (+I,-I,-I)   p = 0.335529

The dominant mutual channel is therefore:

    (+I,-I,-I) <-> (-I,-I,-I)

This is the most important transition pair in the reduced dynamics.

---

## Power iteration result

Starting from any of the 5 signature states, the power iteration converges to
the same limiting distribution.

Thus the quotient-level transport is:

- connected
- ergodic
- dynamically stable

This is important because it shows the quotient is not just a static reduction,
but a coherent effective dynamical system.

---

## Two-step return probabilities

Computed diagonal entries of P^2:

- (+I,+I,-I) : 0.234678
- (+I,-I,-I) : 0.491197
- (-I,+I,-I) : 0.235056
- (-I,-I,+I) : 0.268825
- (-I,-I,-I) : 0.395544

The largest two-step return probability occurs at (+I,-I,-I), followed by
(-I,-I,-I). This reinforces the identification of these two states as the
dominant transport basin.

---

## Best reduced picture so far

The low-energy system now has three coherent layers:

1. sign geometry
   - low blocks carry exact generator-sign labels

2. signature quotient graph
   - the system compresses to 5 realized sign sectors
   - couplings are local in sign space

3. quotient dynamics
   - the Markov walk is ergodic
   - long-time transport concentrates on a two-state core

This is the strongest effective reduction obtained so far in the branch.

---

## Working interpretation

A compact statement is:

    the low-energy transport quotient defines an ergodic 5-state parity
    manifold whose stationary dynamics is concentrated on the adjacent pair
    (+I,-I,-I) and (-I,-I,-I), with the remaining signatures acting as feeder
    states into that core transport basin

---

## Caution

This is still not an electron model.

What has been shown is:

- a 5-state low-energy quotient
- local parity-adjacent transport
- an ergodic random walk
- a dominant two-sector stationary core

What has not yet been shown is:

- spinorial double-cover structure
- physical charge interpretation
- correspondence with known particle observables

So the correct current language is:

    effective low-energy parity transport manifold

not yet a physical particle identification.

---

## Immediate next step

The next natural move is to detect dominant circulation patterns and short
cycles in the signature random walk.

Suggested next script:

    scripts/find_signature_cycles.py

This will identify whether the two-state core is embedded in larger preferred
loops and whether the feeder states participate in a canonical circulation
pattern.

---

## Working summary

Short version:

    the low-energy signature quotient is an ergodic 5-state random walk whose
    stationary measure is concentrated on the adjacent pair (+I,-I,-I) and
    (-I,-I,-I), revealing a dominant two-sector core inside the parity-adjacent
    low-energy transport graph.

