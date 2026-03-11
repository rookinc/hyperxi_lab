from pathlib import Path
from collections import Counter
import re

SPECTRUM_FILE = Path("artifacts/spectra/spectrum_local.txt")

def parse_numbers(text: str):
    vals = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # Accept lines like:
        # 1: -3.604098602642
        # -3.604098602642
        m = re.search(r'(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*$', line)
        if m:
            try:
                vals.append(float(m.group(1)))
            except ValueError:
                pass
    return vals

def rounded_key(x: float, places: int = 12):
    return round(x, places)

def main():
    print("=" * 80)
    print("SPECTRAL MULTIPLICITY REPORT")
    print("=" * 80)

    if not SPECTRUM_FILE.exists():
        print(f"missing artifact: {SPECTRUM_FILE}")
        print()
        print("expected an input file containing one eigenvalue per line")
        return

    text = SPECTRUM_FILE.read_text()
    vals = parse_numbers(text)

    if not vals:
        print(f"no eigenvalues parsed from: {SPECTRUM_FILE}")
        return

    counts = Counter(rounded_key(v, 12) for v in vals)
    grouped = sorted(counts.items(), key=lambda kv: kv[0], reverse=True)

    print(f"source file: {SPECTRUM_FILE}")
    print(f"total eigenvalues read: {len(vals)}")
    print(f"distinct eigenvalues: {len(grouped)}")
    print()

    print("-" * 80)
    print("DISTINCT EIGENVALUES WITH MULTIPLICITIES")
    print("-" * 80)
    for eig, mult in grouped:
        print(f"{eig: .12f}    multiplicity = {mult}")

    print()
    print("-" * 80)
    print("MULTIPLICITY PROFILE")
    print("-" * 80)

    mult_profile = Counter(mult for _, mult in grouped)
    for mult, freq in sorted(mult_profile.items()):
        print(f"multiplicity {mult}: {freq} eigenvalue(s)")

    print()
    print("-" * 80)
    print("BASIC SANITY CHECKS")
    print("-" * 80)
    print(f"sum of multiplicities = {sum(counts.values())}")
    print(f"max eigenvalue         = {max(vals):.12f}")
    print(f"min eigenvalue         = {min(vals):.12f}")

    print()
    print("Spectral scan complete.")

if __name__ == "__main__":
    main()
