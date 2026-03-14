# Pair Transport Graph — Low Spectral Modes

## Context

We constructed the **pair transport graph** induced by ordered Petrie decagon
cycles on the HyperXi chamber structure.

Vertices correspond to **S-pairs**, and edges correspond to consecutive
transport along Petrie decagon cycles.

The graph is extracted from:

    reports/decagons/ordered_decagon_pair_cycles.txt

and analyzed via:

    scripts/plot_low_transport_mode.py

---

## Transport Graph Invariants

Observed graph properties:

- vertices: **60**
- edges: **120**
- degree set: **[4]**
- diameter: **6**

Shell profile from vertex 0:

    (1, 4, 8, 16, 24, 6, 1)

This confirms the transport structure is a **4-regular connected graph**
with moderate diameter and strong symmetry.

---

## Spectral Structure

Low eigenmodes of the adjacency operator were examined.

Example modes:

### Mode index 2

Eigenvalue:

    -2

Largest amplitudes:

    node 25 : +0.305204
    node 18 : +0.243997
    node 45 : +0.235943
    node 51 : -0.229251
    node 29 : +0.226891
    node 5  : -0.226891
    node 21 : -0.217408

### Mode index 3

Eigenvalue:

    -2

Largest amplitudes:

    node 23 : +0.423165
    node 3  : -0.362734
    node 52 : -0.280508
    node 22 : +0.251619
    node 33 : +0.236035

---

## Key Observation

The eigenvalue **-2 has multiplicity >1**, producing a degenerate
eigenspace of low transport modes.

Individual eigenvectors therefore do **not represent unique physical
patterns**; instead they are coordinate choices inside the shared
eigenspace.

The invariant object is the **entire -2 eigenspace**.

---

## Interpretation

These modes appear **extended across the graph** rather than localized.

This suggests that the pair transport geometry naturally supports
distributed interference patterns rather than point-localized states.

In physical language:

    the structure behaves like a standing wave on the transport manifold.

---

## Output Artifacts

Generated files:

    reports/spectral/transport_modes/transport_mode_02.txt
    reports/spectral/transport_modes/transport_mode_02.png
    reports/spectral/transport_modes/transport_mode_03.txt
    reports/spectral/transport_modes/transport_mode_03.png

---

## Next Steps

Important invariant diagnostics:

1. Compute the projector onto the -2 eigenspace
2. Measure vertex participation density
3. Study generator action restricted to this eigenspace
4. Analyze nodal partitions induced by the full mode family

These will reveal the canonical structure of the transport sector.

