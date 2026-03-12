from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR = ROOT / "spec"
OUTFILE = SPEC_DIR / "petrie_decagon_derived.v2.json"


def main() -> None:
    spec = {
        "spec_version": "2.0.0",
        "object_name": "Petrie-Twisted Chamber Graph",
        "status": "structurally_identified",
        "summary": (
            "A 60-vertex tetravalent arc-transitive chamber graph derived from "
            "the ordered Petrie decagon system, realized as a nontrivial signed "
            "regular 2-cover of a 30-vertex quotient graph."
        ),
        "source": {
            "cell_geometry": "dodecahedron",
            "base_vertex_system": "12-vertex Petrie support graph",
            "construction": "ordered Petrie decagon adjacency union"
        },
        "chamber_graph": {
            "vertices": 60,
            "edges": 120,
            "degree": 4,
            "triangles": 40,
            "connected": True,
            "automorphism_order": 480,
            "vertex_transitive": True,
            "edge_transitive": True,
            "arc_transitive": True
        },
        "quotient_graph": {
            "vertices": 30,
            "edges": 60,
            "degree": 4,
            "triangles": 20,
            "connected": True,
            "regular_2_cover_base": True,
            "shell_class_histogram": [
                {
                    "shells": [1, 4, 8, 8, 8, 1],
                    "count": 30
                }
            ]
        },
        "opposition_quotient": {
            "vertices": 15,
            "edges": 30,
            "degree": 4,
            "triangles": 10,
            "strongly_regular": False,
            "shell_class_histogram": [
                {
                    "shells": [1, 4, 8, 2],
                    "count": 15
                }
            ],
            "common_neighbor_test": {
                "lambda_profile": {"1": 30},
                "mu_profile": {"0": 15, "1": 60}
            }
        },
        "signed_cover": {
            "is_nontrivial": True,
            "sign_histogram": {
                "+1": 40,
                "-1": 20
            },
            "transition_patterns": {
                "preserve": {
                    "pattern": [[0, 0], [1, 1]],
                    "count": 40,
                    "meaning": "sheet preserved"
                },
                "swap": {
                    "pattern": [[0, 1], [1, 0]],
                    "count": 20,
                    "meaning": "sheet swapped"
                }
            }
        },
        "construction_model": {
            "fiber_type": "2-sheet edge fiber",
            "local_rule": "Petrie preserve/swap vertex coupling",
            "global_interpretation": "signed regular 2-cover"
        },
        "negative_identifications": {
            "is_oriented_edge_arc_graph_of_icosahedron": False,
            "is_plain_z2_voltage_lift_of_icosahedral_arc_graph": False,
            "quotient_is_line_graph_of_icosahedron": False
        },
        "files": {
            "primary_cycle_source": "artifacts/cycles/ordered_decagon_pair_cycles.txt",
            "spec_schema": "spec/petrie_decagon_derived_schema.v2.json"
        },
        "evidence": {
            "reports": [
                "artifacts/invariants/chamber_graph_aut_order.txt",
                "artifacts/reports/chamber_graph_arc_orbits.txt",
                "artifacts/invariants/check_cover_and_base_identification.txt",
                "artifacts/reports/recovered_signing.txt",
                "artifacts/reports/reconstruct_vertex_connection.txt",
                "artifacts/reports/test_arc_graph_model_rerun.txt",
                "artifacts/reports/test_z2_voltage_lift_rerun.txt"
            ]
        }
    }

    SPEC_DIR.mkdir(parents=True, exist_ok=True)
    OUTFILE.write_text(json.dumps(spec, indent=2) + "\\n", encoding="utf-8")
    print(f"wrote {OUTFILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
