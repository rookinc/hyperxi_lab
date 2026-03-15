# Cubic Transport Probe
Date: 2026-03-15

We want to reconnect the cubic

    64x^3 + 64x^2 + 7x - 9 = 0

to the Thalean transport system.

The real root is

    x ≈ 0.290442704136390

Hypothesis: the cubic is the minimal polynomial of a compressed transport
operator in the Thalean system.

Candidate operators:

1. G60 adjacency
2. G30 signed lift adjacency
3. G15 adjacency (L(Petersen))
4. chamber transport operator
5. Petrie / decagon holonomy operator
6. first excited eigenspace transport operator

Test strategy:

Compute

    P(T) = 64T^3 + 64T^2 + 7T - 9I

and measure

    ||P(T)||

for each operator.

If the cubic is structural, one of these spaces should nearly annihilate.

Relevant scripts already present in the repo:

    compute_spectrum.py
    chamber_low_modes.py
    inspect_petrie_operator.py
    thalion_eigenvalue_minpoly_guess.py
    scan_low_eigenspaces_for_spin_lift.py

Tomorrow tasks:

1. export adjacency matrices for G60, G30, G15
2. compute spectra
3. check if cubic divides the characteristic polynomial
4. check if cubic annihilates low-mode subspaces

Possible interpretations if confirmed:

• minimal polynomial of Petrie transport
• phase law for decagon holonomy
• compressed eigenvalue recursion across quotient tower
• transport density law

