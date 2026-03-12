from __future__ import annotations

from pathlib import Path
import hashlib

p = Path("artifacts/census/thalion_graph.g6")
s = p.read_text(encoding="utf-8").strip()
h = hashlib.sha256(s.encode()).hexdigest()
print("graph6:", s)
print("sha256:", h)
