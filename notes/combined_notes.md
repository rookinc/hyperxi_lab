

---
# 2026-03-13_petersen_spinorial_transport.md
---

# HyperXi Lab Log
## 2026-03-13
### Petersen Core and Transport Holonomy

This note summarizes the full chain of discoveries made today in the HyperXi Lab exploration of the Thalean transport system derived from dodecahedral chamber transport.

The purpose of this document is to preserve the logical thread of the investigation so that work can resume tomorrow without reconstructing intermediate reasoning.

---------------------------------------------------------------------

# 1. Initial Objective

The working hypothesis was that the chamber transport system derived from Petrie transport on the dodecahedron produces a nontrivial combinatorial structure that might encode a discrete analogue of spinorial holonomy.

The central objects under study are the graphs:

G60  — chamber graph
G30  — transport lift
G15  — quotient core

with the covering tower

G60 → G30 → G15

---------------------------------------------------------------------

# 2. Recovery of the 15-core

Computational probes confirmed:

vertices: 15
edges: 30
degree: 4

Further analysis showed:

G15 ≅ L(Petersen)

i.e.

the 15-vertex core is the **line graph of the Petersen graph**.

This identification is canonical and arises naturally from the opposite-edge pairing structure of the dodecahedron.

---------------------------------------------------------------------

# 3. Structure of the 15-core

Properties of G15:

• 15 vertices  
• 30 edges  
• degree 4  
• exactly 12 pentagonal cycles  

Under the identification

G15 ≅ L(Petersen)

these 12 pentagons correspond exactly to the 12 five-cycles of the Petersen graph.

Thus the canonical cycle structure of G15 is inherited from Petersen geometry.

---------------------------------------------------------------------

# 4. Transport Lift

The next layer in the construction is

G30 → G15

which is a **signed 2-lift**.

The induced signing on the 30 edges of G15 is:

16 positive
14 negative

This signing arises directly from the geometric transport rule inherited from the dodecahedral chamber system.

---------------------------------------------------------------------

# 5. Pentagon Holonomy

The 12 pentagons of G15 were classified using the transport sign.

Result:

6 odd pentagons
6 even pentagons

Parity is defined by the XOR of edge signs along the cycle.

Interpretation:

even cycle → trivial lift
odd cycle  → sheet swap

Thus traversal of an odd pentagon produces a nontrivial lift holonomy.

Two traversals return to the starting sheet.

This is the discrete analogue of the familiar

2π / 4π spinorial phenomenon.

---------------------------------------------------------------------

# 6. Key Structural Insight

The transport signing does **not create the pentagons**.

Instead it **polarizes the canonical Petersen pentagon system**.

Thus:

12 Petersen pentagons
↓
6 even
6 odd

Only the odd pentagons carry nontrivial holonomy.

---------------------------------------------------------------------

# 7. Full Covering Tower

The discovered structure can now be summarized as

G60  chamber graph
│
│ V₄ lift
│
G30  signed transport lift
│
│ 2-lift
│
G15 ≅ L(Petersen)

This forms the combinatorial skeleton of the Thalean transport model.

---------------------------------------------------------------------

# 8. Interpretation

The key object is not merely the graph L(Petersen) itself, but the pair

(L(Petersen), σ_transport)

where σ_transport is the ℤ₂ connection induced by chamber transport.

The spinorial behaviour arises from the holonomy of this connection.

---------------------------------------------------------------------

# 9. Small Graph Probe

A probe over several small candidate graphs was performed to test whether this phenomenon appears generically.

Candidates tested included:

Petersen
dodecahedral
desargues
heawood
cubical
tetrahedral
octahedral
icosahedral
line_K4
line_K5
line_petersen
line_cubical

Result:

No generic graph exhibited the same odd/even pentagon structure under arbitrary edge signings.

Conclusion:

The phenomenon is **not intrinsic to the bare graph**.

It is **transport-induced**.

---------------------------------------------------------------------

# 10. Final Structural Result

The Thalean transport system produces a distinguished signed Petersen line graph with nontrivial pentagonal holonomy.

In particular:

• G15 is canonically L(Petersen)
• the transport lift induces a ℤ₂ connection on G15
• the 12 Petersen pentagons split into 6 odd and 6 even cycles
• the odd pentagons carry the nontrivial holonomy

This completes the structural identification of the core combinatorics of the model.

---------------------------------------------------------------------

# 11. Status

Mathematically the discrete transport model is now internally coherent.

It provides:

• a canonical core graph  
• a nontrivial lift  
• a natural holonomy structure  

Whether this has physical interpretation remains an open question.

---------------------------------------------------------------------

# 12. Possible Next Steps

Potential directions for further investigation:

1. Formalize the transport sign as a cohomology class on L(Petersen)

2. Characterize the automorphism group of the signed graph

3. Investigate whether the six odd pentagons generate the full holonomy group

4. Study the relationship between the chamber graph G60 and known regular covers

5. Explore whether similar structures appear in other Platonic chamber systems

---------------------------------------------------------------------

# End of Log


---
# 2026-03-14_chamber_holonomy_on_first_excited_eigenspace.md
---

# Chamber Holonomy on the First Excited Eigenspace
Date: 2026-03-14

## Purpose

Record the first successful eigenspace-level holonomy measurements on the
60-vertex chamber graph.

This note summarizes the result that geometrically meaningful loops act on the
first excited Laplacian eigenspace by small but coherent rotations.

---

## Graph and spectral sector

The graph under study is the 60-vertex chamber graph used in the HyperXi
transport branch.

Observed basic statistics in this probe:

- vertices: 60
- edges: 90

Using the graph Laplacian, the first excited eigenvalue is

    λ₁ = 0.24340174613993118

with multiplicity

    3

So the first excited sector is a 3-dimensional real eigenspace.

---

## Method

For each loop γ in the chamber graph:

1. build the vertex permutation operator induced by transport around γ
2. project that operator to the first excited eigenspace
3. take the polar decomposition of the projected matrix
4. retain the orthogonal factor Q(γ)

This isolates the pure rotational part of loop transport from leakage out of
the eigenspace.

The resulting orthogonal holonomy matrices were then analyzed by:

- determinant
- trace
- eigenvalues
- effective SO(3) rotation angle

---

## Main result

For all tested geometrically meaningful loops, the orthogonal holonomy lies in
an SO(3)-type rotational class:

- det(Q) = +1
- eigenvalues are of the form

      e^{+iθ}, e^{-iθ}, 1

Thus the first excited chamber sector carries a nontrivial rotational holonomy.

This is not a trivial return map and not a sign-flip law. It is a genuine
internal rotation on the low-mode sector.

---

## Pentagon holonomy

Simple 5-cycles were enumerated and tested.

Summary:

- count: 12
- mean angle: 1.169969°
- min angle: 0.104712°
- max angle: 2.573420°
- std dev: 0.841868°

Interpretation:

Pentagonal loops induce small but coherent internal rotations on the first
excited eigenspace.

---

## Decagon holonomy

Simple 10-cycles were enumerated and tested.

Summary:

- count: 30
- mean angle: 3.548580°
- min angle: 1.269552°
- max angle: 7.161066°
- std dev: 1.430544°

Interpretation:

10-cycles induce larger rotations than 5-cycles, suggesting cumulative phase
build-up with loop scale.

---

## Interpretation

The low-mode sector of the chamber graph behaves like a discrete internal fiber
with loop-dependent rotational holonomy.

In compact form:

    loop γ  →  Q(γ) ∈ SO(3)

This is evidence for a genuine internal connection structure on the chamber
substrate.

What has been observed so far is therefore closer to:

- discrete gauge holonomy
- parallel transport on a mode bundle
- rotational connection on a low-dimensional spectral sector

than to a direct spin-1/2 sign-flip law.

---

## What this does NOT yet show

This result does not yet establish:

- a spinorial double-cover law
- ψ → -ψ after one loop
- ψ → ψ after two loops
- an electron-like mode

So the current result should be interpreted as a precursor structure, not a
particle model.

---

## Research significance

This is the first clear evidence in the branch that:

1. the rigid chamber substrate supports a nontrivial internal mode bundle
2. geometrically meaningful loops act coherently on that bundle
3. the induced action is rotational and loop-dependent

This strengthens the idea that the HyperXi chamber system may support
particle-like transport structures at the spectral level.

---

## Next step

The natural next question is whether this SO(3)-type holonomy lifts to a
spinorial double cover.

That suggests the next probe:

    scripts/test_double_cover_holonomy.py

or equivalent work on whether the observed chamber holonomy admits a natural
SU(2)-like lift.



---
# 2026-03-14_decagon_phase_holonomy.md
---

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



---
# 2026-03-14_effective_signature_operator.md
---

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



---
# 2026-03-14_electron_program.md
---

# Toward an Electron Model from the HyperXi Transport System

This document records a staged research program for exploring whether
electron-like behavior can emerge from the HyperXi chamber transport
substrate.

The goal is not to immediately reproduce the Standard Model electron,
but to determine whether the chamber transport geometry supports
stable particle-like excitations with spinorial behavior.

---

# Stage 0 — Establish the Transport Substrate

Current observations:

    dodecahedral Petrie transport
        ↓
    15-core ≅ L(Petersen)
        ↓
    rigid signed 2-lift (30)
        ↓
    Thalean chamber graph (60)

Computational experiments suggest:

- large variation in signing choices
- collapse to a single lifted graph

This suggests the substrate may possess a **canonical transport geometry**.

Success condition:

    the transport ladder is structurally forced,
    not an artifact of arbitrary encoding.

---

# Stage 1 — Identify Candidate Particle Modes

Goal:

Find distinguished eigenmodes of the chamber graph that could represent
stable excitations.

Tests:

- compute adjacency eigenvectors
- compute Laplacian eigenvectors
- analyze multiplicity structure
- visualize nodal patterns
- test robustness under graph symmetries

Desired properties:

- low eigenvalue
- geometric coherence
- stability across construction variants

Deliverable:

    notes/candidate_chamber_modes.md

---

# Stage 2 — Spinorial Transport Test

Goal:

Determine whether chamber modes exhibit **spinor-like monodromy**.

Procedure:

1. choose a fundamental loop (Petrie loop or chamber cycle)
2. transport the mode along the loop
3. compare initial and final phase

Possible outcomes:

    ψ →  ψ   (ordinary transport)
    ψ → -ψ   (spinor transport)
    ψ → rotation in mode space

A true spinorial signal would show:

    ψ → -ψ after one loop
    ψ →  ψ after two loops

Deliverable script:

    scripts/test_mode_spinorial_monodromy.py

---

# Stage 3 — Mass-like Invariant

Goal:

Define a scalar quantity that measures the cost of sustaining
a given excitation.

Possible candidates:

- Laplacian eigenvalue
- adjacency spectral position
- recurrence cost under transport
- closure energy of chamber cycles

Interpretation:

    mass ≈ persistence cost of the excitation.

Deliverable:

    ranked list of candidate modes with scalar invariants.

---

# Stage 4 — Charge-like Asymmetry

Goal:

Identify a binary or signed invariant that behaves like charge.

Possible sources:

- orientation of transport cycles
- sheet selection in the signed lift
- chirality of chamber circulation
- parity sector of transport relations

Desired property:

    conserved under transport evolution.

Deliverable:

    notes/chamber_charge_probe.md

---

# Stage 5 — Localization Analysis

Goal:

Determine whether candidate modes behave like:

- localized knots
- delocalized standing waves
- hybrid resonances

Tests:

- inverse participation ratio
- nodal support analysis
- perturbation of individual chambers

Deliverable:

    chamber_mode_localization_metrics.py

---

# Stage 6 — Perturbation Response

Goal:

Observe how candidate modes respond to perturbations.

Possible perturbations:

- modify transport weights
- bias specific chamber classes
- introduce occupancy field

Desired behavior:

    coherent response consistent with particle-like excitation.

Deliverable:

    chamber_mode_occupancy_response.py

---

# Working Hypothesis

The electron may correspond not to a vertex or region of the graph,
but to a **stable spinorial resonance of the lifted chamber transport
manifold**.

Success criteria for an electron-like candidate:

1. distinguished stable mode
2. spinorial transport signature
3. robust scalar invariant (mass proxy)

If all three are observed, the chamber transport substrate becomes
a serious candidate for supporting particle-like excitations.



---
# 2026-03-14_exact_minusI_blocks.md
---

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



---
# 2026-03-14_extended_signature_quotient_32blocks.md
---

# Extended Signature Quotient on the Lowest 32 Eigenspace Blocks

## Summary

Extending the signature-transition quotient from the lowest 20 eigenspace blocks to the lowest 32 eigenspace blocks enlarges the observed signature alphabet from 5 classes to 8 classes.

The 20-block quotient was therefore a low-energy truncation, not the full signature quotient presently visible in the local transport algebra.

## Input data

The extension was built from:

- `reports/spectral/generator_sign_reps.json`
- `reports/spectral/block_transitions/low_block_transition_graph_032_blocks.json`

using:

- `scripts/decompose_generator_sign_reps.py --n 32`
- `scripts/build_low_block_transition_graph.py --n 32`
- `scripts/extend_signature_quotient_to_n_blocks.py --n 32`

## Observed signature classes

The lowest 32 eigenspace blocks split into the following 8 signature sectors:

- `(+I,+I,+I)` blocks = `[25, 26, 27, 30, 31, 32]`
- `(+I,+I,-I)` blocks = `[18, 20, 23, 24]`
- `(+I,-I,+I)` blocks = `[28, 29]`
- `(+I,-I,-I)` blocks = `[10, 11, 12, 13, 14, 16, 17]`
- `(-I,+I,+I)` blocks = `[21, 22]`
- `(-I,+I,-I)` blocks = `[5, 7, 8]`
- `(-I,-I,+I)` blocks = `[15, 19]`
- `(-I,-I,-I)` blocks = `[1, 2, 3, 4, 6, 9]`

## Main structural conclusion

The earlier 5-sector quotient captured only the lowest-signature front of the transport algebra.

Once blocks 21 through 32 are included, three additional sectors appear:

- `(+I,+I,+I)`
- `(+I,-I,+I)`
- `(-I,+I,+I)`

This shows that the signature flow is not exhausted by the low-energy parity-adjacent picture.

## Stationary distribution

The 32-block quotient gives the following stationary weights:

- `(+I,-I,-I)` = `0.244137`
- `(-I,-I,-I)` = `0.192399`
- `(+I,+I,+I)` = `0.184696`
- `(+I,+I,-I)` = `0.116029`
- `(-I,+I,-I)` = `0.106012`
- `(-I,+I,+I)` = `0.061523`
- `(-I,-I,+I)` = `0.060332`
- `(+I,-I,+I)` = `0.034873`

## Interpretation

Two earlier low sectors remain dominant:

- `(+I,-I,-I)`
- `(-I,-I,-I)`

But the fully positive sector `(+I,+I,+I)` now appears as a major reservoir, with stationary weight comparable to the strongest negative sectors.

This is the key conceptual upgrade from the 20-block quotient:
the fully positive signature sector is not peripheral once the quotient is extended.

## Strongest outgoing transitions

The strongest outgoing edge from each signature sector is:

- `(+I,+I,+I) -> (+I,-I,-I)` with `p = 0.297319`
- `(+I,+I,-I) -> (+I,-I,-I)` with `p = 0.250559`
- `(+I,-I,+I) -> (+I,+I,-I)` with `p = 0.231752`
- `(+I,-I,-I) -> (+I,+I,+I)` with `p = 0.188336`
- `(-I,+I,+I) -> (+I,-I,-I)` with `p = 0.298126`
- `(-I,+I,-I) -> (+I,-I,-I)` with `p = 0.213145`
- `(-I,-I,+I) -> (-I,-I,-I)` with `p = 0.325713`
- `(-I,-I,-I) -> (+I,+I,+I)` with `p = 0.158543`

## Reading of the flow

At the 32-block level, the quotient is better described as a multi-basin signature flow network than as a simple parity-adjacency skeleton.

The dominant qualitative features are:

1. `(+I,-I,-I)` acts as a major receiving sector.
2. `(-I,-I,-I)` remains a strong anchor sector.
3. `(+I,+I,+I)` becomes a substantial high-signature reservoir.
4. `(+I,-I,+I)` remains comparatively light and sparse.

## Provisional meaning

The low-energy quotient was real, but incomplete.

The extended quotient suggests that transport reorganizes across a broader signed sector geometry in which positive-positive-positive blocks participate strongly in the long-run flow. This means the local transport algebra is not merely splitting into “negative core plus adjacent corrections,” but into a richer directed ecology of signature sectors.

## Immediate next step

Run the same three companion analyses on the 32-block quotient:

- random walk
- cycle extraction
- effective Hamiltonian fit

using:

- `signature_transition_quotient_032_blocks.json`

This will show whether the 8-sector system inherits the same dominant cycle architecture as the 5-sector quotient, or whether new metastable loops emerge once the higher positive sectors are admitted.


---
# 2026-03-14_generator_sign_sectors_in_Hloc.md
---

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



---
# 2026-03-14_low_block_parity_adjacency.md
---

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



---
# 2026-03-14_minusI_upstairs_families.md
---

# 2026-03-14 — Minus-I Upstairs Families

## Result

The `-I` candidate words found from the low-eigenspace transport search do **not** descend to the 60-state S-pair quotient.

Instead, they act as genuine **upstairs transport symmetries** on the full 120-flag cover.

This is the strongest spinorial signal obtained so far.

---

## Core observation

For every tested `-I` candidate word:

- pairs preserved setwise: `0 / 60`
- pairs swapped internally: `0 / 60`
- pairs split across distinct S-pairs: `60 / 60`
- same decagon-membership set: `0 / 60`
- changed decagon-membership set: `60 / 60`

So the `-I` action is not a symmetry of the 60-pair graph.

It belongs only to the 120-flag cover.

---

## Interpretation

This is exactly the behavior expected of a spinorial layer:

- the 60-pair graph behaves like a geometric base space
- the 120-flag graph behaves like a double cover
- the `-I` sector acts upstairs but does not descend downstairs

In plain language:

> the sign-carrying transport symmetry lives on the cover, not on the visible quotient.

This is the clearest indication yet that the HyperXi transport system contains a nontrivial spinor-style structure.

---

## Geometric families of `-I` words

### Family A — 5-cycle upstairs rotor

Words:
- `FFF`
- `SFFS`
- `FFFSS`
- `FFSSF`
- `FSSFF`
- `SSFFF`
- `VSVVS`

Observed action:
- flag cycle histogram: `{5: 24}`
- identical upstairs transport pattern across all tested diagnostics
- complete S-pair splitting
- complete decagon-membership change

Interpretation:
A canonical 5-cycle rotor on the 120-flag cover.

This family appears to represent one stable upstairs transport class.

---

### Family B — 6-cycle upstairs rotor

Words:
- `VFFSV`
- `SVFF`

Observed action:
- flag cycle histogram: `{6: 20}`
- complete S-pair splitting
- complete decagon-membership change

Interpretation:
A distinct 6-cycle rotor class on the 120-flag cover.

This is not equivalent to Family A.

---

### Family C — second 5-cycle upstairs rotor

Words:
- `FFFV`
- `FSVS`
- `SFFSV`

Observed action:
- flag cycle histogram: `{5: 24}`
- complete S-pair splitting
- complete decagon-membership change
- transport pattern distinct from Family A

Interpretation:
A second 5-cycle rotor class, different from the canonical `FFF` family.

So the `-I` sector already separates into multiple nontrivial upstairs geometric classes.

---

## Strong statement now justified

We can now say:

> The `-I` transport sector in HyperXi is not a gauge-trivial artifact of the 60-state quotient.
> It is an upstairs symmetry of the 120-flag double cover, and it appears in multiple geometric rotor families.

That is a mathematically meaningful spinorial signal.

---

## What this suggests physically

This does **not** yet prove a physical electron model.

But it does show the right structural skeleton:

1. a base geometry
2. a double cover
3. a non-descending `-I` action
4. closed transport classes upstairs

That is the same kind of architecture one expects from spinor behavior.

The current evidence suggests:

> electron-like spin, if it emerges in this framework, will not live on the visible pair graph itself.
> It will live in the upstairs transport state whose observable shadow projects to the downstairs graph.

---

## Immediate next question

The next thing to test is whether these upstairs rotor families correspond to recognizable algebraic classes in the transport word system.

In particular:

- are these words equivalent under known transport relations?
- do the 5-cycle families correspond to one canonical generator class plus harmless relabelings?
- is the 6-cycle family fundamentally different or derivable from the same core rotor?

If yes, then the `-I` sector can be organized as a genuine transport algebra rather than a loose list of words.

---

## Working summary

Current best summary sentence:

> HyperXi now exhibits a nontrivial `-I` transport sector on the 120-flag cover that completely splits the 60-state S-pair quotient and organizes into distinct upstairs rotor families of cycle types `{5:24}` and `{6:20}`.



---
# 2026-03-14_pair_transport_low_modes.md
---

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



---
# 2026-03-14_petersen_cover_canonicality.md
---

# Petersen Skeleton and Canonical Lift Hypothesis
Scott Allen Cave
HyperXi Lab — CoRI
2026-03-14

## Context

In the HyperXi transport study of the dodecahedral flag space, several layers of structure have appeared repeatedly:

1. dodecahedral chamber transport
2. a 15-vertex quotient ("15-core")
3. identification of this core with L(Petersen)
4. a 30-vertex signed 2-lift
5. the 60-vertex Thalean chamber graph

The purpose of this note is to record a computational observation suggesting that the intermediate signed lift may be **canonical** rather than an arbitrary choice.

---

## Computation performed

We enumerated signings of the 30 edges of

    G = L(Petersen)

with exactly:

    14 negative edges
    16 positive edges

Total search space:

    C(30,14) = 145,422,675 signings

For each signing:

1. compute cycle parity signature (Z₂)
2. construct the signed 2-lift
3. compute the WL hash of the lifted graph

---

## Empirical result (millions of samples)

Across millions of tested signings:

distinct_lift_hashes = 1

while

cycle_signatures ≈ 32768 = 2^15

Thus:

- many distinct parity configurations
- a single lifted graph

This suggests that the signed lifts in this slice collapse to **one isomorphism class**.

---

## Interpretation

The result indicates that the sign assignment behaves more like a **coordinate system on a fixed cover** than a generator of different graphs.

In other words:

many micro signings
→ same lifted geometry

This strongly hints that the relevant 30-vertex lift is **intrinsically determined by the Petersen skeleton**, not by the specific signing.

---

## Transport tower picture

The emerging structural ladder becomes:

dodecahedron
→ Petrie transport system
→ 15-core
≅ L(Petersen)
→ canonical signed 2-lift (30 vertices)
→ Thalean chamber graph (60 vertices)

Thus the Petersen line graph appears to function as a **compressed transport skeleton**, while the lift restores the twist degrees of freedom required for chamber transport.

---

## Hypothesis

The 30-vertex lift observed in the Thalean construction is the **canonical nontrivial cover of L(Petersen) compatible with dodecahedral Petrie transport**.

If true, then:

- the signing data is not fundamental
- the cover itself is geometrically forced

---

## Connection to recursive emergence

This structure mirrors a broader pattern appearing in the Spirelica framework:

many micro configurations
→ constrained macro geometry

In both cases the observable structure emerges only after quotienting or cumulative composition.

---

## Next tests

1. Derive the signing directly from Petrie transport.
2. Compare the resulting cover with the lift class observed in the rigidity experiment.
3. Attempt a theoretical explanation via:
   - switching equivalence classes
   - automorphism group of L(Petersen)
   - Z₂ cycle cohomology

If the Petrie-derived signing lies in the same lift class, the Thalean graph may represent a **forced geometric expansion of the Petersen skeleton**.

---

## Status

Current evidence: computational (millions of samples)

Next step: structural explanation.



---
# 2026-03-14_planck_4density_occupancy_scaling.md
---

# Planck 4-Density Occupancy Scaling
Date: 2026-03-14

## Purpose

Record the current information-density ansatz and the resulting occupancy
scaling for particles and coherent masses.

## Postulate

Assume a maximal lawful information density of

\[
\rho_I^{\max} = 1 \text{ bit} / l_P^4.
\]

Interpretation: the primitive bookkeeping unit is a spacetime 4-cell, not
a purely spatial voxel.

## Coherent occupancy model

For mass \(M\), coherence length \(L\), and coherence time \(L/c\), define

\[
f_{\mathrm{occ}}(M,L)
=
\frac{Mc^2(L/c)/\hbar}{L^4/l_P^4}.
\]

This becomes

\[
f_{\mathrm{occ}}(M,L)
=
\frac{M}{m_P}\left(\frac{l_P}{L}\right)^3.
\]

This is the central scaling law.

## Reduced Compton specialization

For reduced Compton coherence,

\[
L = \bar{\lambda}_C = \frac{\hbar}{Mc},
\]

so

\[
L = l_P \frac{m_P}{M}.
\]

Substituting into the general law gives

\[
f_{\mathrm{occ}}
=
\frac{M}{m_P}
\left(\frac{l_P}{l_P(m_P/M)}\right)^3
=
\frac{M}{m_P}\left(\frac{M}{m_P}\right)^3
=
\left(\frac{M}{m_P}\right)^4.
\]

Thus

\[
\boxed{
f_{\mathrm{occ}} = \left(\frac{M}{m_P}\right)^4
}
\]

for one reduced Compton cycle.

## Consequences

### Electron

\[
f_{\mathrm{occ},e} \sim \left(\frac{m_e}{m_P}\right)^4 \approx 3.07\times 10^{-90}.
\]

### Proton

\[
f_{\mathrm{occ},p} \sim \left(\frac{m_p}{m_P}\right)^4 \approx 3.49\times 10^{-77}.
\]

### Ratio

\[
\frac{f_{\mathrm{occ},p}}{f_{\mathrm{occ},e}}
=
\left(\frac{m_p}{m_e}\right)^4
\approx 1.14\times 10^{13}.
\]

So the proton is about 13 orders of magnitude denser than the electron under
this bookkeeping, even though the mass ratio is only about 1836.

### Planck mass

\[
f_{\mathrm{occ}}(m_P)=1.
\]

So the Planck mass is the natural unit-occupancy threshold in this model.

## Interpretation

Under this ansatz:

- an electron is an extremely sparse recursive occupancy pattern,
- a proton is still sparse, but vastly denser,
- a Planck-mass reduced-Compton-scale object is order-one occupied.

This motivates the interpretation:

> mass measures 4-volume compression of one action quantum.

## Threshold coherence scale for general mass

Setting \(f_{\mathrm{occ}}=1\) gives

\[
L_\ast(M)=l_P\left(\frac{M}{m_P}\right)^{1/3}.
\]

This is the coherence length required for a mass \(M\) to reach unit occupancy.

## Working interpretation

The ansatz appears to separate three regimes:

1. ordinary matter: deeply sub-saturation,
2. Planck frontier: order-one occupancy,
3. beyond-Planck compression: geometry likely cannot ignore occupancy.

This may provide a route toward an information-density interpretation of
gravitational response.


---
# 2026-03-14_planck_frontier_three_scale_braid.md
---

# Planck Frontier as a Three-Scale Braid
Date: 2026-03-14

## Purpose

Record the three characteristic length scales arising from the current
information-density ansatz and compare their crossing masses.

## Ansatz

Assume a maximal lawful information density of

\[
\rho_I^{\max} = 1 \text{ bit} / l_P^4
\]

with \(l_P\) the Planck length, interpreted as a spacetime 4-cell scale.

For a coherent mass \(M\) spread over spatial scale \(L\) and time \(L/c\),
define the occupancy

\[
f_{\mathrm{occ}}(M,L)
=
\frac{Mc^2(L/c)/\hbar}{L^4/l_P^4}.
\]

This simplifies to

\[
f_{\mathrm{occ}}(M,L)
=
\frac{M}{m_P}\left(\frac{l_P}{L}\right)^3
\]

using \(\hbar/(m_P c)=l_P\).

## Unit-occupancy coherence scale

Setting \(f_{\mathrm{occ}}=1\) gives the threshold coherence scale

\[
L_\ast(M)=l_P\left(\frac{M}{m_P}\right)^{1/3}.
\]

## Three scales

Let

\[
x := \frac{M}{m_P}.
\]

Then the three comparison scales are:

### Reduced Compton wavelength

\[
\bar{\lambda}_C(M)=\frac{\hbar}{Mc}=l_P x^{-1}.
\]

### Occupancy-threshold coherence scale

\[
L_\ast(M)=l_P x^{1/3}.
\]

### Schwarzschild radius

\[
R_s(M)=\frac{2GM}{c^2}=2l_P x.
\]

## Pairwise crossings

### Compton = occupancy

\[
\bar{\lambda}_C = L_\ast
\iff
l_P x^{-1} = l_P x^{1/3}
\iff
x=1.
\]

Therefore

\[
M = m_P,
\qquad
\bar{\lambda}_C = L_\ast = l_P.
\]

### Compton = Schwarzschild

\[
\bar{\lambda}_C = R_s
\iff
l_P x^{-1} = 2 l_P x
\iff
x = \frac{1}{\sqrt{2}}.
\]

Therefore

\[
M = \frac{m_P}{\sqrt{2}},
\qquad
\bar{\lambda}_C = R_s = \sqrt{2}\, l_P.
\]

### Occupancy = Schwarzschild

\[
L_\ast = R_s
\iff
l_P x^{1/3} = 2 l_P x
\iff
x = \frac{1}{2\sqrt{2}}.
\]

Therefore

\[
M = \frac{m_P}{2\sqrt{2}},
\qquad
L_\ast = R_s = \frac{l_P}{\sqrt{2}}.
\]

## Conclusion

The three scales do not meet at a single point. Instead they cross across a
narrow Planck-scale mass band:

\[
\frac{m_P}{2\sqrt{2}}
<
\frac{m_P}{\sqrt{2}}
<
m_P.
\]

This suggests that the “Planck frontier” is not a single threshold but a
three-scale braid in which:

1. occupancy threshold crosses Schwarzschild first,
2. Compton crosses Schwarzschild second,
3. Compton meets occupancy at the top end, at \(M=m_P\).

## Ordering by mass regime

For \(0 < x < 1/(2\sqrt{2})\):

\[
\bar{\lambda}_C > L_\ast > R_s.
\]

For \(1/(2\sqrt{2}) < x < 1/\sqrt{2}\):

\[
\bar{\lambda}_C > R_s > L_\ast.
\]

For \(1/\sqrt{2} < x < 1\):

\[
R_s > \bar{\lambda}_C > L_\ast.
\]

For \(x > 1\):

\[
R_s > L_\ast > \bar{\lambda}_C.
\]

## Working interpretation

This provides a possible bridge between:

- quantum localization scale,
- recursive information-density threshold,
- gravitational collapse scale.

The Planck mass is then interpreted not as a single magic point, but as the
upper end of a short transition ladder.


---
# 2026-03-14_recursive_density_bridge.md
---

# Recursive Density Bridge
Date: 2026-03-14

Related notes:

- `2026-03-14_planck_4density_occupancy_scaling.md`
- `2026-03-14_planck_frontier_three_scale_braid.md`

Related HyperXi themes:

- Thalean transport as admissible routing manifold
- occupancy threshold as recursive density constraint
- Planck frontier as braid of Compton / occupancy / Schwarzschild scales

Status:

- heuristic
- algebraically tidy
- not yet tied to a HyperXi operator or chamber observable


---
# 2026-03-14_signature_cycle_structure.md
---

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



---
# 2026-03-14_signature_random_walk.md
---

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



---
# 2026-03-14_signature_transition_quotient.md
---

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



---
# 2026-03-14_transport_algebra_exact_sign_flip_sectors.md
---

# Exact Sign-Flip Sectors in the Local Transport Algebra
Date: 2026-03-14

## Purpose

Record the first exact sign-flip result found in the HyperXi branch.

This note summarizes the discovery that low eigenspaces of the exact local
transport Hamiltonian on the 120-flag space admit transport words whose
projected action is exactly

    -I

on those eigenspaces.

This is stronger and more particle-relevant than the earlier chamber-cycle
holonomy results, which only exhibited small SO(3)-type rotations.

---

## Setup

The operator under study is the exact local transport Hamiltonian

    H_loc = a_F (U_F + U_F^T) + a_S U_S + a_V (U_V + U_V^T)

built from the primitive transport generators:

- F
- S
- V

acting on the 120-flag space.

The search procedure was:

1. diagonalize H_loc
2. decompose its spectrum into eigenspace blocks
3. generate short transport words in {F,S,V}
4. project each word operator into low eigenspaces
5. take the polar unitary/orthogonal factor
6. test whether the induced action equals -I exactly

---

## Main result

Exact sign-flip sectors exist in the transport algebra.

More precisely, there are low eigenspace blocks E such that for certain short
transport words w,

    w|_E = -I

exactly.

In these cases:

- ||U + I|| = 0
- ||U^2 - I|| = 0

so the projected action is an exact sign flip.

This is the first exact sign-flip behavior observed in the branch.

---

## Strongest discovery

The shortest exact sign-flip words are already length 1:

- F
- S
- V

So the sign-flip behavior is not a rare high-order artifact of long composed
words. It is already present in the primitive generator action.

Observed full-space orders:

- F has order 5
- S has order 2
- V has order 3

Yet each of these can act as -I on substantial families of low eigenspaces.

This means the sign-flip behavior is a genuine representation-theoretic feature
of the transport algebra.

---

## Comparison with chamber holonomy

Earlier chamber-graph analysis showed:

- small but coherent SO(3)-type holonomy on low Laplacian eigenspaces
- formal SU(2) half-angle lifts
- no sector close to -I

So the chamber-cycle route gave:

    loop holonomy ≈ small rotation

but not

    spinorial sign flip

By contrast, the transport-word search on H_loc yields exact sign flips.

Interpretation:

The spin-like structure appears more naturally in the **transport algebra**
than in chamber-cycle holonomy alone.

---

## Structural interpretation

The local transport algebra appears to carry nontrivial sign/projective
representations on low eigenspaces.

A concise statement is:

    primitive transport generators can act as exact -I
    on selected low spectral sectors.

This suggests that proto-spin structure is encoded in the algebra of transport
operators themselves, not merely in graph-theoretic loop geometry.

---

## Why this matters

This is the first result in the branch that is genuinely more electron-adjacent
than metaphorical.

Reasons:

1. the sign flip is exact
2. it occurs on low spectral sectors
3. it is generated by short lawful transport words
4. the primitive generators themselves participate

This does not yet produce an electron model, but it does identify the first
place in the project where a mathematically sharp spin-like behavior appears.

---

## Important caution

This is not yet a full spin-1/2 theorem.

What has been shown is:

- exact -I on selected real eigenspaces
- under specific transport words

What has not yet been shown is:

- a full double-cover construction
- an SU(2) irreducible spinor sector
- a physical identification with electron spin
- a mass/charge interpretation

So this should be described as:

    exact sign-flip sectors in the transport algebra

not yet as a completed spinor model.

---

## Notable observation

The fact that generators of different full-space orders behave this way is
especially suggestive:

- F: order 5 on the full flag space
- S: order 2 on the full flag space
- V: order 3 on the full flag space

yet each can induce exact -I on selected eigenspaces.

This indicates that the spectral sectors are not merely inheriting raw
generator order, but are realizing a reduced/sign-sensitive representation of
the transport algebra.

---

## Immediate next step

The natural next analysis is to classify the generator action block by block.

That means building, for each low eigenspace E, the signatures:

    F|_E
    S|_E
    V|_E

and recording whether each acts as:

- +I
- -I
- reflection-like
- more general finite-order action

This should make it possible to identify coherent families of low blocks with
shared sign behavior.

Suggested next script:

    scripts/decompose_generator_sign_reps.py

---

## Working summary

Current picture:

1. chamber-cycle holonomy gives small SO(3)-type rotations
2. transport-word action on H_loc gives exact sign flips
3. therefore the more promising route to spin-like structure is the
   transport algebra, not raw loop holonomy alone

Short version:

    exact sign-flip sectors exist in the local transport algebra,
    and these are the strongest proto-spin candidates yet found in
    the HyperXi branch.



---
# chamber_graph_from_true_flag_transport.md
---

# Chamber Graph from True Flag Transport

Date: 2026-03-14
Project: HyperXi Lab

---

## Result

The 60-vertex chamber graph studied in the HyperXi experiments is recovered directly from the true dodecahedral flag incidence model.

Construction:

Upstairs space:
- 120 lawful flags (vertex, edge, face)

Generators:
- S = edge flip
- F = face rotation
- V = vertex rotation

Quotient:
- quotient word: S

This partitions the 120 flags into 60 two-element classes.

Adjacency rule downstairs:
- apply generator V and project to the S-classes.

---

## Resulting Graph

The resulting graph has invariants:

vertices: 60  
edges: 120  
degree: 4  
triangles: 40  
diameter: 6  
shell profile: (1,4,8,16,24,6,1)

This matches exactly the chamber graph observed in earlier transport experiments.

---

## Equivalent Move Presentations

Several generator words produce the same graph:

V  
VV  
FFV  
FVF  
SV  
VS  

The simplest canonical construction is:

quotient: S  
adjacency: V

---

## Interpretation

The chamber graph is the visible quotient of the 120-flag dodecahedral transport system.

Structure:

120 flag transport space  
        ↓ quotient by S  
60 chamber graph  

Edges correspond to vertex-rotation transport across the dodecahedron.

---

## Relation to Transport Symmetry

Earlier experiments identified a 120-element transport subgroup acting on the flag space with:

- center of order 2
- central involution of cycle type {2:60}

This central involution pairs the two flags in each S-class.

Thus the chamber graph can be interpreted as the central quotient of the flag transport system.

---

## Status

Confirmed computationally via:

scripts/rebuild_true_thalion_quotient.py  
scripts/search_true_quotient_move_sets.py

Next step:

Test whether the discovered 120-element transport subgroup projects onto the automorphism group of the chamber graph with kernel equal to the central involution.



---
# chamber_graph_quotient_tower.md
---

# Chamber Graph Quotient Tower

Date: 2026-03-14
Project: HyperXi Lab

---

## Result

The 60-vertex chamber graph recovered from the true dodecahedral flag incidence model admits a canonical antipodal quotient.

Construction:

- upstairs graph: the 60-vertex chamber graph obtained from the 120 lawful flags by quotienting by S and inducing adjacency by V
- antipodal pairing: vertices paired by unique distance-6 partners

This produces a quotient graph on 30 vertices.

---

## Chamber Graph Invariants

- vertices: 60
- edges: 120
- degree: 4
- triangles: 40
- diameter: 6
- shell profile: (1,4,8,16,24,6,1)

---

## Antipodal Quotient Invariants

- vertices: 30
- edges: 60
- degree: 4
- triangles: 20
- diameter: 5
- shell profile: (1,4,8,12,4,1)

---

## Covering Structure

The antipodal projection is a genuine regular 2-cover.

Observed computationally:

- pair count: 30
- edge multiplicity histogram over quotient edges: {2: 60}
- covering test: True

So every quotient edge lifts to exactly two upstairs edges.

---

## Structural Interpretation

This places the chamber graph in the quotient tower:

60-vertex chamber graph
    ↓ antipodal quotient
30-vertex quartic graph
    ↓ further quotient
15-core

Earlier work identified the 15-core as isomorphic to the line graph of the Petersen graph.

Thus the chamber graph is naturally a two-step binary lift over the Petersen-derived core.

---

## Status

Confirmed computationally via:

scripts/check_chamber_graph_as_4cover_of_15core.py

Next step:

Compare the reconstructed 30-vertex quotient directly against the previously identified 30-layer graph, and verify that its next quotient recovers the known 15-core.



---
# local_petrie_theorem.md
---

# Local Petrie Structure of the HyperXi Flag Model

This note records the verified local algebra and transport structure on the
120 lifted flags of a single dodecahedral cell used in the HyperXi simulator.

The results are computationally verified in the repository scripts and form
the foundation for future multi-cell transport and spectral analysis.

---

# 1. Local Flag Space

A single dodecahedron contains:

- 20 vertices
- 30 edges
- 12 faces

The lifted chamber space consists of the triples

    (vertex, edge, face)

with incidence compatibility.

Total number of flags:

    |Flags| = 120

This is the standard chamber set for the Coxeter structure of the dodecahedron.

---

# 2. Generator Operators

Three local transport generators act on the flag space.

S — vertex flip across the current edge  
F — face continuation around the face  
V — cell/face transition across the edge  

Their verified orders are:

    order(S) = 2
    order(F) = 5
    order(V) = 3

---

# 3. Mixed Relations

The generators satisfy the following relations:

    (SF)^2 = 1
    (FV)^2 = 1
    (SV)^10 = 1

while remaining noncommutative:

    SF ≠ FS
    FV ≠ VF
    SV ≠ VS

These relations generate the full 120-state chamber action.

---

# 4. Petrie Operator

Define the Petrie transport word

    P = SV

Its action decomposes the flag space into

    12 disjoint cycles of length 10

Each cycle traverses:

- 10 distinct faces
- 10 distinct edges
- 10 distinct vertices

Thus P corresponds exactly to the **Petrie decagons** of the dodecahedron.

---

# 5. Petrie Spectrum

Let U_P be the permutation matrix of P.

Its spectrum is:

    λ_k = exp(2π i k / 10)

for k = 0,...,9.

Each eigenvalue appears with multiplicity:

    multiplicity = 12

Thus

    U_P ≅ 12 · C₁₀

in cycle structure.

---

# 6. Local Hamiltonian

The Hermitian local transport Hamiltonian is

    H_loc = (U_F + U_F^{-1}) + U_S + (U_V + U_V^{-1})

Properties:

    trace(H_loc) = 0
    max eigenvalue = 5
    min eigenvalue ≈ -3.604

---

# 7. Petrie Non-Symmetry

The Petrie operator does not commute with the Hamiltonian:

    [H_loc, U_P] ≠ 0

Empirically:

    max |entry| = 1
    Frobenius norm ≈ 34.64
    nonzero entries = 1200

Thus Petrie transport is an exact geometric transport mode but not a conserved
symmetry of the current Hamiltonian.

---

# 8. Interpretation

The chamber transport algebra therefore has two distinct layers:

1. Exact geometric transport cycles (Petrie decagons)
2. A Hamiltonian that mixes those transport modes

This indicates that the natural spectral decomposition of the local system
is not aligned with Petrie transport.

The observed eigenvalue multiplicities (1,3,4,5) suggest the Hamiltonian
instead organizes along irreducible representations of the dodecahedral
rotation symmetry.

---

# 9. Next Directions

Possible next steps include:

• symmetry decomposition of H_loc under the icosahedral rotation group  
• multi-cell transport on the {5,3,4} honeycomb  
• cone-type reduction for large-scale transport dynamics  

These directions connect the present local algebra to the broader HyperXi
transport program.



---
# petersen_pentagonal_curvature.md
---

# Petersen Graph as Minimal Pentagonal Transport Witness

## Motivation

In the HyperXi transport experiments, the compressed 15-vertex core
graph appears as:

    G_15 ≅ L(Petersen)

This repeatedly emerges when dodecahedral Petrie transport relations
are quotiented and simplified.

This note records a structural interpretation of why the Petersen graph
appears naturally in this context.

---

## Pentagonal Transport Tension

The regular dodecahedron is built entirely from pentagonal faces.
Pentagonal systems exhibit a fundamental transport tension:

- 5-cycles introduce odd closure
- odd cycles prevent bipartite flattening
- recursive transport cannot settle into a flat periodic lattice

This creates a combinatorial analogue of curvature: transport can
circulate locally but cannot globally flatten without conflict.

We refer to this phenomenon informally as **pentagonal transport
frustration**.

---

## The Petersen Graph as a Minimal Witness

The Petersen graph has the following properties:

    vertices: 10
    degree:   3 (cubic)
    girth:    5

It is:

- small
- highly symmetric
- saturated with 5-cycles
- non-planar

Among small cubic graphs, Petersen is the smallest structure that
retains a robust pentagonal cycle structure while resisting reduction
to simpler planar or bipartite transport systems.

For this reason it can be viewed heuristically as a **minimal witness
of pentagonal transport tension**.

---

## Why the Line Graph Appears

The HyperXi transport construction does not operate on raw vertices of
this opposition structure, but on **transport channels between
relations**.

The line graph transformation converts edges of the Petersen skeleton
into vertices representing transport channels:

    Petersen → opposition skeleton
    L(Petersen) → transport-channel skeleton

Thus the 15-core graph records how these transport channels interact.

---

## Structural Ladder Observed in Computation

Experiments reveal the following expansion sequence:

    Petersen skeleton (10 vertices)
        ↓
    L(Petersen) transport core (15 vertices)
        ↓
    signed 2-lift (30 vertices)
        ↓
    chamber / Thalean graph (60 vertices)

Large-scale enumeration of signings on L(Petersen) with 14 negative
edges produced:

    cycle parity states observed: 2^15
    distinct lifted graphs:       1

indicating strong structural rigidity in the lift.

---

## Interpretation

The Petersen graph does not appear to be inserted artificially into
the construction. Instead it emerges as the **irreducible opposition
skeleton of the dodecahedral transport system** once redundant
structure is quotiented away.

The Thalean chamber graph can therefore be interpreted as a canonical
expansion of this skeleton through successive lifting operations.

---

## Status

The statements in this note are structural interpretations supported by
computational evidence. Formal theorems relating Petersen structure to
dodecahedral Petrie transport remain an open direction.



---
# petersen_transport_skeleton.md
---

# Petersen Transport Skeleton in the Dodecahedral System

## Observation

The 15-vertex core graph emerging in the HyperXi transport construction is
isomorphic to the line graph of the Petersen graph:

    G_15 ≅ L(Petersen)

Properties:

- vertices: 15
- edges: 30
- degree: 4
- automorphism group: 120

This graph arises naturally when compressing transport relations in the
dodecahedral Petrie decagon system.

---

## Interpretation

The Petersen graph appears to function as the **opposition skeleton** of the
dodecahedral transport geometry.

Process:

    dodecahedron
        ↓
    Petrie decagon system
        ↓
    opposition / transport compression
        ↓
    Petersen skeleton
        ↓
    visible transport graph = L(Petersen)

The line-graph step reflects that the transport structure acts on
**channels between relations**, rather than on primary vertices.

Thus:

    Petersen graph → abstract opposition graph
    L(Petersen)    → transport-channel graph

---

## Structural Ladder

The observed constructions form a natural expansion ladder:

    Petersen skeleton
        ↓
    L(Petersen) (15 vertices)
        ↓
    signed 2-lift (30 vertices)
        ↓
    chamber graph / Thalean graph (60 vertices)

This sequence matches the doubling pattern observed in HyperXi experiments.

---

## Computational Result

Large-scale enumeration of signings of L(Petersen) edges with exactly
14 negative edges yielded:

    cycle parity signatures observed: 2^15 = 32768
    distinct lifted graphs:           1

Thus the signed 2-lift appears **rigid** under this constraint.

Interpretation:

- The 16-dimensional cycle space exhibits one linear constraint
  when restricted to the 14-negative-edge slice.
- Despite large variation in cycle parity assignments,
  the resulting lifted graph is invariant up to isomorphism.

This suggests the lift is **structurally forced** by the symmetry
of the Petersen skeleton.

---

## Research Implication

The Petersen graph is not imported into the construction.  
It emerges as the **irreducible transport skeleton** of the
dodecahedral chamber system.

The Thalean chamber graph can therefore be interpreted as a
canonical expansion of this skeleton.

In summary:

    dodecahedral transport
        ↓
    Petersen opposition skeleton
        ↓
    canonical lifted chamber geometry



---
# thalean_15core_canonical_dodecahedron.md
---

# Thalean 15-Core as a Canonical Dodecahedral Object

Date: 2026-03-13

The 15-vertex core of the Thalean graph is isomorphic to the graph built
directly from the canonical dodecahedron by:

1. taking the 15 opposite-edge classes of the dodecahedron,
2. creating one vertex for each opposite-edge class,
3. declaring two such vertices adjacent iff there are exactly two
   cross-adjacencies between the underlying edge pairs in the
   dodecahedral edge graph.

This proves that the 15-core is a native polyhedral object of the
dodecahedron, not merely a quotient artifact of the Thalean graph.

Thus the Thalean graph is a regular V4-lift of a canonical
15-vertex dodecahedral compatibility graph.


---
# thalean_15core_direct_recovery.md
---

# Thalean 15-Core Direct Recovery

Date: 2026-03-13

The 15-vertex core of the Thalean graph can be recovered directly from
the 30-vertex edge layer by:

1. pairing 30-layer vertices into opposite-edge classes
2. creating one 15-core vertex for each opposite-edge pair
3. declaring two 15-core vertices adjacent iff there are exactly two
   cross-adjacencies between the corresponding 30-layer pairs

This direct construction yields a graph isomorphic to the 15-core
obtained by the second antipodal quotient of the Thalean graph.

Thus the 15-core is a native geometric compatibility graph of the
dodecahedral edge system, not merely a quotient artifact.


---
# thalean_15core_is_linegraph_of_petersen.md
---

# Thalean 15-Core = Line Graph of the Petersen Graph

Date: 2026-03-13

The recovered 15-vertex core of the Thalean graph is isomorphic to the
line graph of the Petersen graph.

Thus the 15-core has two equivalent descriptions:

1. the compatibility graph on opposite-edge classes of the dodecahedron
2. the line graph of the Petersen graph

This explains its parameters:

- 15 vertices
- 30 edges
- 4-regular
- spectrum 4^1, 2^5, (-1)^4, (-2)^5
- automorphism group S5

Accordingly, the Thalean graph sits above a Petersen-derived core:

L(Petersen) = G15
   ↓ signed 2-lift
G30
   ↓ binary/V4 chamber lift
G60 = Thalean graph


---
# thalean_15core_opposite_edge_classes.md
---

# Thalean Graph: 15-Core as Opposite-Edge Compatibility Graph

Date: 2026-03-13

## Reduction Ladder

The Thalean graph hierarchy discovered in the HyperXi transport system is:

60 → 30 → 15

- G60 : Thalean chamber graph
- G30 : antipodal quotient
- G15 : second antipodal quotient

Properties:

G60  
- vertices: 60  
- edges: 120  
- degree: 4  
- triangles: 40  
- diameter: 6  

G30  
- vertices: 30  
- edges: 60  
- degree: 4  

G15  
- vertices: 15  
- edges: 30  
- degree: 4  
- triangles: 10  
- diameter: 3  

## Structural Interpretation

The reductions correspond naturally to geometric compression of the dodecahedral edge system:

60 : edge–face chamber states  
30 : edges  
15 : opposite-edge classes  

Each vertex of the 30-layer represents a pair of 60-vertices:

(v, a(v))

Each vertex of the 15-layer represents a pair of 30-vertices:

(e, e')

which corresponds to two opposite edges of the dodecahedral edge graph.

## Adjacency Rule in the 15-Core

The probe `probe_15core_as_opposite_edge_pairs.py` reveals a clean rule:

For two 15-vertices

(A, B) and (C, D)

adjacency occurs **iff exactly two cross-adjacencies exist between the underlying 30-vertices**.

Empirical result:

edges_between histogram:
2 → 30 edges

nonedges histogram:
0 → 75 pairs

So the rule is exactly:

(A,B) ~ (C,D)
iff
two of {A,B} are adjacent to two of {C,D} in G30.

## Interpretation

Thus the 15-vertex graph is a **compatibility graph on opposite-edge classes** of the 30-vertex edge graph.

The hierarchy becomes:

dodecahedron
↓
edge-face chambers (60)
↓
edges (30)
↓
opposite-edge classes (15)

## Symmetry

Automorphism structure discovered earlier:

Aut(G60) = V4 ⋊ S5  
|Aut(G60)| = 480  

with:

V4 : fiber symmetry of the 4-lift  
S5 : symmetry acting on the 15-core  

The induced action on the 15 vertices is exactly S5.

## Summary

The Thalean graph can be understood as:

• a V4-fibered lift of a 15-vertex compatibility graph  
• whose vertices represent opposite-edge classes of the dodecahedral edge system  
• with adjacency inherited from the edge-adjacency structure of the 30-vertex layer.

This explains the entire reduction ladder:

60 → 30 → 15

as successive compression of chamber, edge, and opposite-edge structure.


---
# thalean_4lift_core.md
---

# Thalean Graph as a 4-Lift of a 15-Vertex Core

Author: Scott Allen Cave
Date: 2026-03-13

This note records a structural observation about the Thalean graph
arising from Petrie transport on the flag space of the dodecahedron.

This is an internal research note and not yet part of the formal paper.

---

MAIN OBSERVATION

The 60-vertex Thalean graph is a regular 4-lift of a 15-vertex base graph.

This was verified computationally.

The lift structure appears through the antipodal quotient tower

60 -> 30 -> 15

where:

- the first antipodal quotient produces a 30-vertex graph
- the second antipodal quotient produces a 15-vertex graph

The 60-vertex graph then reconstructs as a regular 4-cover of this
15-vertex core.

---

CORE GRAPH (15 VERTICES)

Vertices: 15
Edges: 30
Degree: 4
Diameter: 3
Triangles: 10

Shell profile:

(1,4,8,2)

Spectrum:

4^1
2^5
(-1)^4
(-2)^5

Canonical graph6:

Nto`GCJAIAAHPA@CaAg

---

LIFT STRUCTURE

The probe produced the following properties.

Fiber structure:

15 fibers of size 4

fiber size histogram: {4: 15}

No edges occur within a fiber.

Each edge of the 15-vertex base graph lifts to exactly 4 edges in the
60-vertex graph.

edge multiplicity histogram: {4: 30}

Local adjacency pattern for every vertex in the 60-graph:

neighbor-to-fiber pattern: (1,1,1,1)

Thus each vertex connects to exactly one vertex in each of the four
adjacent base fibers.

---

CONSEQUENCE

The Thalean graph is a regular covering graph

G60 -> G15

with covering degree

4.

The 30-vertex graph arises naturally as an intermediate antipodal
quotient.

---

STRUCTURAL SUMMARY

Graph hierarchy:

15-vertex core graph
↓ regular 4-lift
60-vertex Thalean graph
↓ antipodal quotient
30-vertex intermediate graph

Invariant ladder:

Vertices:

15 -> 30 -> 60

Edges:

30 -> 60 -> 120

Triangles:

10 -> 20 -> 40

Degree remains constant (4) at every level.

---

OPEN QUESTIONS

1. Is the 15-vertex core graph catalogued in standard graph tables?
2. Can the 4-lift be described by an explicit voltage assignment?
3. Is the lift induced directly by dodecahedral flag symmetries?
4. Does the same lift structure appear for other regular polyhedra?



---
# thalean_meaning_of_b.md
---

# Geometric Meaning of the Second Involution b

Date: 2026-03-13

Probe results for the second involution b on the 60-vertex Thalean graph:

- b has no fixed points
- b commutes with the antipode involution a
- b always changes the 30-layer class
- b always preserves the 15-layer fiber

Therefore b is the involution that swaps the two 30-layer representatives
inside a fixed 15-layer opposite-edge class.

Thus each 15-core vertex lifts to four 60-layer states:

{v, a(v), b(v), a(b(v))}

with interpretation:

- a : swap chamber antipodes inside one 30-layer class
- b : swap the two opposite-edge representatives inside one 15-core class
- ab: do both

So the Thalean graph is a regular V4-cover of the 15-core with fiber
decomposition:

(opposite-edge class) × Z2 × Z2


---
# thalean_s5_symmetry.md
---

# Thalean Graph S5 Symmetry Backbone

Date: 2026-03-13

The 60-vertex Thalean graph has automorphism group of size 480.

A pair of commuting fixed-point-free involutions generates a V4 fiber
kernel on the 60 vertices, producing 15 fibers of size 4.

The induced action on these 15 fibers has:

- order 120
- exact S5 element-order distribution
- equality with the full automorphism group of the 15-vertex core graph

Thus the symmetry of the Thalean graph factors cleanly as a 4-element
fiber kernel over an S5-symmetric 15-vertex core.

In summary:

Aut(G60) = V4 ⋊ S5   (strong computational evidence)

with

|Aut(G60)| = 4 × 120 = 480.


---
# thalean_transport_hierarchy.md
---

# Thalean Transport Hierarchy (White-Room Note)

Author: Scott Allen Cave  
Date: 2026-03-13  

This note records an interpretive structure observed in the Thalean graph
arising from Petrie transport on the flag space of the dodecahedron.

This is not part of the formal paper; it is an internal structural
interpretation.

---

# Observed Quotient Tower

The Thalean graph admits successive antipodal quotients:

60 → 30 → 15

Layer summaries:

60-graph
vertices: 60
edges: 120
degree: 4
triangles: 40
diameter: 6
shell profile:
(1,4,8,16,24,6,1)

30-graph (first antipodal quotient)
vertices: 30
edges: 60
degree: 4
triangles: 20
diameter: 5
shell profile:
(1,4,8,12,4,1)

15-graph (second antipodal quotient)
vertices: 15
edges: 30
degree: 4
triangles: 10
diameter: 3
shell profile:
(1,4,8,2)

At each stage

vertices halve  
edges halve  
triangle counts halve

while the degree remains constant.

---

# Structural Interpretation

The Thalean graph encodes Petrie transport between edge–face incidences
(chambers) of the dodecahedron.

The successive quotients appear to remove binary distinctions:

60 layer
    full chamber transport state
    (edge–face incidence)

30 layer
    chamber class modulo global opposition

15 layer
    compressed transport archetype

Thus the transport system admits a hierarchy of binary collapses
while preserving the same local adjacency law.

---

# White-Room Law

The chamber transport system of the dodecahedron contains successive
involutive dualities whose quotients produce the cascade

60 → 30 → 15

with 4-regular adjacency preserved at every level.

---

# Spectral Simplification

Spectra compress along the hierarchy.

60 layer
contains √5 structure

30 layer
integer spectrum

15 layer
integer spectrum with only four eigenvalues

This suggests progressive removal of geometric degrees of freedom.

---

# Open Questions

1. Is the 15-vertex graph catalogued?
2. Is the quotient tower induced directly by Coxeter relations?
3. Does the hierarchy appear in other regular polyhedra?
4. Is there a geometric interpretation of the 15-layer?



---
# thalean_two_involutions.md
---

# Thalean Graph Two-Involution Structure

Date: 2026-03-13

The 60-vertex Thalean graph admits two commuting fixed-point-free involutions:

- a: the antipode map
- b: a second automorphism of order 2

These satisfy:

- a^2 = id
- b^2 = id
- ab = ba

The group <a,b> therefore has four elements and acts on the 60 vertices
with exactly 15 orbits of size 4.

Each orbit has the form

{v, a(v), b(v), a(b(v))}.

These 15 four-element orbits are exactly the fibers of the regular
4-cover from the Thalean graph to the 15-vertex core graph.

Thus the 15-vertex core is the quotient

G_15 = G_60 / <a,b>.

This gives a concrete two-bit structural decomposition of the Thalean graph.


---
# transport_spin_cover_discovery.md
---

# Transport Spin Cover Discovery

Date: 2026-03-14  
Project: HyperXi Lab

---

## Result

The transport operators on the 120-flag space generate a **finite subgroup of size 120**.

This subgroup was discovered by seeding the generator search with words that act as **exact −I operators** in low eigenspaces of the local transport Hamiltonian.

Seed words:

- FFF
- FFFV
- VFFSV
- SVFF

Growing the subgroup generated by these permutations produced:

Group size: **120**

---

## Order Spectrum

Element orders:

1 : 1  
2 : 31  
3 : 20  
5 : 24  
6 : 20  
10 : 24  

Cycle structures:

{1:120} : 1  
{2:60} : 31  
{3:40} : 20  
{5:24} : 24  
{6:20} : 20  
{10:12} : 24  

This spectrum is highly structured and consistent with a finite symmetry group rather than a random generated semigroup.

---

## Center

The group center has size **2**.

Central elements:

identity  
cycle structure {1:120}

central involution  
cycle structure {2:60}

The nontrivial central element:

- has order 2
- pairs all 120 flags into 60 disjoint swaps
- commutes with all transport elements

---

## Interpretation

The existence of a nontrivial central involution indicates that the transport group is a **double cover** of a smaller observable symmetry.

In particular:

120-flag transport space  
↓ quotient by central involution  
60-pair observable chamber graph

Thus the chamber graph can be interpreted as the **central quotient of the flag transport group**.

---

## Physical Interpretation (Hypothesis)

The discovered structure is strongly suggestive of a **spinorial transport layer**:

- the observable graph lives on 60 chambers
- the full transport algebra acts on 120 flags
- the central involution represents a global sign degree of freedom
- this sign disappears when passing to the observable quotient

This is exactly the algebraic architecture expected for a **spin lift**.

Important: this is a structural analogy, not a physical claim.

---

## Status

Confirmed computationally via:

scripts:

- grow_minusI_transport_subgroup.py
- analyze_transport_subgroup_structure.py

Next step:

identify the abstract group isomorphism class of the 120-element transport group.

