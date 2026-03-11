from pathlib import Path
import re

ART = Path("artifacts")

FILES = {
    "walk_hash": ART / "invariants" / "base_graph_walk_hash.txt",
    "distance_tests": ART / "invariants" / "distance_regular_tests.txt",
    "intersection_array": ART / "invariants" / "intersection_array_candidate.txt",
    "spectrum": ART / "spectra" / "spectrum_local.txt",
}

def read_file(path):
    if not path.exists():
        return None
    return path.read_text()

def extract_numbers(text):
    return re.findall(r"[0-9]+", text)

print("=" * 80)
print("GRAPH FINGERPRINT SUMMARY")
print("=" * 80)

for name, path in FILES.items():
    print()
    print(f"[{name}]")
    print("-" * 40)

    text = read_file(path)

    if text is None:
        print("missing artifact:", path)
        continue

    lines = text.splitlines()

    # print first useful lines
    for line in lines[:20]:
        print(line)

print()
print("=" * 80)
print("Fingerprint scan complete.")
