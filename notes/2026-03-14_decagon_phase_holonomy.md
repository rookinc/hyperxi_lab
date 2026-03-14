# Decagon Phase Holonomy Test on the -2 Transport Sector

## Goal

Test whether the strongly Petrie-resonant `-2` eigenspace of the 60-vertex
pair transport graph exhibits **spinorial half-turn behavior** on the natural
10-cycles (the Petrie decagons).

This was done using a **U(1) proxy holonomy test**:

- choose the best `-2` eigenvector for target harmonic `k`
- infer edge phases from its decagon progression
- multiply the induced phase around each 10-cycle
- compare the resulting holonomy to `+1` and `-1`

This is not yet a full `SU(2)` lift, but it is a valid bridge test.

---

## Input / Script

Input transport structure:

    reports/decagons/ordered_decagon_pair_cycles.txt

Script used:

    scripts/test_decagon_phase_holonomy.py

Output:

    reports/spectral/transport_modes/decagon_phase_holonomy.txt
    reports/spectral/transport_modes/decagon_phase_holonomy.json

---

## Graph Being Tested

The underlying pair transport graph has:

- vertices: **60**
- edges: **120**
- degree set: **[4]**

This is the Petrie transport graph derived from ordered decagon cycles.

---

## Harmonic k = 5

Best `-2` mode tested:

- mode column: **18**
- eigenvalue: **-2**
- score: **0.094468**

Observed loop holonomy on **all 12 decagons**:

    H = +1

Summary:

- mean distance to `+1`: **0**
- mean distance to `-1`: **2**

### Interpretation

The strongest alternating 10-cycle harmonic in the `-2` sector is
**strictly scalar** under this proxy test.

It does **not** behave like a spin-1/2 loop phase.

---

## Harmonic k = 4

Best `-2` mode tested:

- mode column: **10**
- eigenvalue: **-2**
- score: **0.060700**

Observed holonomy:

- 10 decagons returned exactly `+1`
- 2 decagons returned a nontrivial phase
- the sector remained much closer to `+1` than to `-1`

Summary:

- mean distance to `+1`: **0.195928**
- mean distance to `-1`: **1.936339**

### Interpretation

This mode is again **oscillatory but scalar**.
It shows nontrivial phase structure on a small subset of decagons,
but not half-turn holonomy.

---

## Main Conclusion

The `-2` Petrie-resonant transport sector is:

- globally distributed
- highly oscillatory on 10-cycles
- strongly structured by decagon harmonics
- **not spinorial in the present scalar/U(1) proxy model**

So the current scalar transport layer does **not** yet realize
electron-style half-turn behavior.

---

## Consequence

The missing ingredient is not more scalar spectral analysis.

The missing ingredient is a **genuine lift**, such as:

1. an explicit `SU(2)` edge transport law
2. a signed / double-cover transport graph
3. a chamber-plus-internal-orientation state space

Only then can Petrie loop holonomy distinguish `2π` from `4π`.

---

## Result Status

This is a strong negative result:

> The scalar Petrie transport sector alone does not yield spinorial
> half-turn holonomy.

That substantially narrows the search space for any electron-like
interpretation of the system.

---

## Next Step

Move from proxy phase tests to a genuine spin-lift computation using:

    scripts/test_transport_operator_spin_lift.py
    scripts/test_spin_lift_candidate.py
    scripts/scan_low_eigenspaces_for_spin_lift.py

