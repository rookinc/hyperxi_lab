from __future__ import annotations

from pathlib import Path
import json

SPEC = Path("spec/petrie_decagon_derived.v1.json")


def main():
    data = json.loads(SPEC.read_text())

    assert data["schema"] == "petrie-decagon-derived.v1"
    assert data["block_intersection_graph"]["vertex_count"] == 12
    assert data["block_intersection_graph"]["edge_count"] == 30
    assert data["block_intersection_graph"]["degree"] == 5
    assert data["block_intersection_graph"]["identified_as"] == "icosahedral graph"

    assert data["chamber_graph"]["vertex_count"] == 60
    assert data["chamber_graph"]["edge_count"] == 120
    assert data["chamber_graph"]["degree"] == 4

    assert data["quotient_graph"]["vertex_count"] == 30
    assert data["quotient_graph"]["edge_count"] == 60
    assert data["quotient_graph"]["degree"] == 4
    assert data["quotient_graph"]["identified_as"] == "L(Dodecahedron)"

    assert data["signed_2_lift"]["positive_edges"] == 40
    assert data["signed_2_lift"]["negative_edges"] == 20
    assert data["signed_2_lift"]["signing_defined_up_to_switching"] is True

    assert data["spectra"]["two_lift_split_verified"] is True
    print("derived spec is structurally valid")


if __name__ == "__main__":
    main()
