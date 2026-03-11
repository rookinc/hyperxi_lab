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

