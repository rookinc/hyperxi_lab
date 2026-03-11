import os
from pathlib import Path

ROOT = Path(".")
ART = ROOT / "artifacts"
SCRIPTS = ROOT / "scripts"

def section(title):
    print("=" * 80)
    print(title)
    print("=" * 80)

def list_files(path):
    if not path.exists():
        return []
    return sorted([p.name for p in path.iterdir() if p.is_file()])

def count_files(path):
    if not path.exists():
        return 0
    return len(list(path.iterdir()))

section("HYPERXI LAB REPOSITORY STATUS")

section("Scripts")
scripts = list_files(SCRIPTS)
for s in scripts:
    print(" -", s)
print()
print("total scripts:", len(scripts))

section("Artifacts")

for sub in ["invariants", "cycles", "spectra", "reports"]:
    p = ART / sub
    files = list_files(p)
    print(f"{sub}: {len(files)} files")
    for f in files[:10]:
        print("  -", f)
    if len(files) > 10:
        print("  ...")

section("Notes")
notes = list_files(ROOT / "notes")
for n in notes:
    print(" -", n)

section("Summary")

total_artifacts = sum(
    count_files(ART / d)
    for d in ["invariants", "cycles", "spectra", "reports"]
)

print("total scripts:", len(scripts))
print("total artifacts:", total_artifacts)

print()
print("Repository scan complete.")
