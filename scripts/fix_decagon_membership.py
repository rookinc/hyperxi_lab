from pathlib import Path
import ast
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
IN_DEC = ROOT / "reports" / "decagons" / "ordered_decagon_pair_cycles.txt"

pair_to_dec = defaultdict(list)
decagons = []

for raw in IN_DEC.read_text().splitlines():

    line = raw.strip()

    if not line:
        continue

    if not line.lower().startswith("decagon"):
        continue

    if ":" not in line:
        continue

    _, rhs = line.split(":", 1)

    cyc = ast.literal_eval(rhs.strip())
    decagons.append(cyc)

for d, cyc in enumerate(decagons):
    for p in cyc:
        pair_to_dec[p].append(d)

print("total decagons:", len(decagons))
print()

print("pair membership counts")
for p in sorted(pair_to_dec):
    print(p, len(pair_to_dec[p]))
