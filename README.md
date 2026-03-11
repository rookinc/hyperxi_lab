# hyperxi_lab

Computational and structural study of transport-derived finite graphs
arising from the lifted flag geometry of the hyperbolic honeycomb {5,3,4}.

This repository contains analysis tools, invariant computations,
and structural experiments for the HyperXi transport system.

The project investigates a finite chamber graph that emerges from
transport dynamics on the lifted flag space of the {5,3,4} lattice.

Current investigations include:

• identification of a 60-vertex transport graph  
• quotient structures yielding a 30-vertex base graph  
• automorphism-sensitive invariants  
• distance-regularity diagnostics  
• Petrie / decagon / pair-fiber structure  
• spectral and cycle decomposition experiments  

---

## Repository Layout

src/hyperxi/  
Core reusable Python package for geometry, transport operators,
and spectral analysis.

scripts/  
Executable analysis scripts that compute invariants, spectra,
cycle decompositions, and identification fingerprints.

artifacts/  
Generated analysis outputs.

Subdirectories include:

artifacts/invariants/  
Graph fingerprints and automorphism-sensitive invariants.

artifacts/cycles/  
Cycle structure and Petrie-type transport experiments.

artifacts/spectra/  
Spectral analysis outputs.

artifacts/reports/  
Miscellaneous structural diagnostics.

notes/  
Theory notes and intermediate reasoning.

paper/  
Workspace for the formal research paper.

---

## Key Scripts

Important entrypoints for reproducing the core analysis:

scripts/graph_identification_report.py  
scripts/base_graph_walk_hash.py  
scripts/distance_regular_tests.py  
scripts/intersection_array_candidate.py  
scripts/automorphism_sensitive_invariants.py  

---

## Example Usage

Run a report and capture the artifact:

python3 scripts/graph_identification_report.py \
  | tee artifacts/invariants/graph_identification_report.txt

Compute walk-hash fingerprint:

python3 scripts/base_graph_walk_hash.py \
  | tee artifacts/invariants/base_graph_walk_hash.txt

Distance-regular diagnostics:

python3 scripts/distance_regular_tests.py \
  | tee artifacts/invariants/distance_regular_tests.txt

---

## Status

The project is currently focused on identifying the structural class
of the transport graph and its base quotient, including automorphism
structure and intersection-array behavior.

Further work will connect these results to transport dynamics and
symbolic growth models on the {5,3,4} hyperbolic honeycomb.

