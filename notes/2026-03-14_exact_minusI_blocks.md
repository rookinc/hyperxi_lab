# Exact -I Actions in the Transport Operator Algebra

## Goal

Determine whether the full transport operator algebra contains genuine
spin-lift style sign sectors not visible in the scalar Petrie graph alone.

Script used:

    scripts/test_transport_operator_spin_lift.py

---

## Main Result

Several eigenspace blocks admit words whose restricted action is exactly `-I`.

Examples:

- block 5,  eigenvalue -2.048548..., multiplicity 3, word `VFFSV`
- block 10, eigenvalue -1.190400..., multiplicity 3, word `FFF`
- block 11, eigenvalue -1.131769..., multiplicity 3, word `FV`

For these cases:

    ||U + I||   = 0
    ||U^2 - I|| = 0

so the operator acts exactly as a central sign on the block.

---

## Interpretation

This is stronger than the earlier scalar U(1) decagon-phase test.

That earlier test showed:

- the scalar Petrie `-2` sector is oscillatory
- but loop holonomy remained scalar (`+1`)

The present result shows:

- the full transport algebra contains exact `-I` actions
- these sign sectors live at the operator/block level
- they are not visible in the coarse scalar decagon proxy

So the system contains genuine sign-lift structure.

---

## What is and is not established

Established:

- exact `-I` actions occur on multiple low-dimensional eigenspace blocks
- the transport algebra therefore supports central sign sectors

Not yet established:

- that these words correspond to geometrically meaningful closed loops
- that any one of these sectors is the correct physical electron analogue
- that a full SU(2) spin transport law has been constructed

---

## Next Step

Geometrically classify the top `-I` words.

For each leading candidate word:

1. compute its action on chambers
2. compute its action on S-pairs
3. test whether it closes a meaningful Petrie / quotient loop
4. determine whether the `-I` is local, global, or gauge-like

