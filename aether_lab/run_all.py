import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
LOCAL_SRC = BASE / "src"

env = os.environ.copy()
env["PYTHONPATH"] = str(LOCAL_SRC)

SCRIPTS = [
    "scripts/prove_thalean_graph_identity.py",
    "scripts/check_15core_vs_linegraph_petersen.py",
    "scripts/check_30_to_15_quotient.py",
    "scripts/export_core_incidence_matrix.py",
    "scripts/verify_core_polynomial_identity.py",
    "scripts/verify_core_sector_symmetry.py",
    "scripts/test_centered_sector_module.py",
    "scripts/analyze_centered_sector_angles.py",
    "scripts/export_g15_signed_lift_table.py",
]

for script in SCRIPTS:
    print(f"\n=== RUNNING {script} ===\n")
    result = subprocess.run([sys.executable, script], env=env)
    if result.returncode != 0:
        print(f"FAILED: {script}")
        sys.exit(1)

print("\nALL CHECKS PASSED\n")
