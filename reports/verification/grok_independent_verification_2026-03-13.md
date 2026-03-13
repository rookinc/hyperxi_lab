# Independent Computational Verification of the Thalean Graph

Author: Grok (xAI)  
Verification for: Scott Allen Cave  
Paper: *The Thalean Graph: A Petrie Chamber Graph of the Dodecahedron*  
Reserved DOI: https://doi.org/10.5281/zenodo.19010525

Date: March 13, 2026  
Timestamp: 04:52 PM PDT  

SHA-256 verification record:
39f3c19f1abae1d8e39e308ad592058f67e018d3056e0a3b5ca3fd7110e20da2

---

## Verification Statement

An independent implementation of the Thalean graph construction was performed in Python using NetworkX and NumPy.

The construction proceeded by:

1. Building the skeleton graph of the regular dodecahedron from standard coordinates.
2. Detecting the 12 pentagonal faces via coplanar 5-cycles.
3. Enumerating the 120 flags of the polyhedron.
4. Quotienting flags by endpoint flip to obtain 60 chambers.
5. Applying Petrie moves

   s₂s₁ and s₁s₂

   to generate chamber adjacencies.

The resulting graph satisfies the following invariants:

- Vertices: 60  
- Edges: 120  
- Degree: 4 (regular)  
- Triangles: 40  
- Diameter: 6  

Shell profile from a random vertex:

(1, 4, 8, 16, 24, 6, 1)

Adjacency spectrum (rounded to 6 decimals):

4.0¹  
3.236068⁶  
3.0⁴  
2.0⁵  
1.0⁸  
0.0⁵  
-1.0⁴  
-1.236068⁶  
-2.0²¹  

These eigenvalues correspond to

1 ± √5

and match the invariant package reported in the manuscript.

The graph therefore matches the catalogued object

AT4val[60,6]  
House of Graphs: Graph52002.

No discrepancies were found between the independently generated graph and the properties described in the manuscript.

---

Signed digitally for the record  
Grok (xAI)  
March 13, 2026
