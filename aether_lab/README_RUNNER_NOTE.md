The script scripts/check_graph52002_invariants.py is excluded from run_all.py.

Reason:
- it depends on the legacy hyperxi transport kernel
- that kernel expects full flag objects with attributes such as .orient
- the current aether_lab migration is artifact-first, not full transport-state reconstruction

Current runner scope:
- verify imported canonical graph artifacts
- verify quotient/core structure
- verify sector incidence identity
- verify sector symmetry and centered module
- export signed lift data

Future re-enable condition:
- migrate real flag/state transport objects into aether_lab
- or rewrite check_graph52002_invariants.py to consume imported .g6 artifacts directly
