#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict

from hyperxi.combinatorics.thalions import build_thalions
from hyperxi.combinatorics.transport_scaffold import F, V


TARGET = 2.8210234486509136

FACE_CLASS = {
    0: 0, 4: 0, 8: 0,
    1: 1, 5: 1, 9: 1,
    2: 2, 6: 2, 10: 2,
    3: 3, 7: 3, 11: 3,
}


def extract_face(flag):
    for name in ("face", "f", "face_id"):
        if hasattr(flag, name):
            return int(getattr(flag, name))
    raise AttributeError("Could not find face attribute on Flag.")


def extract_edge(flag):
    for name in ("edge", "e", "edge_id"):
        if hasattr(flag, name):
            return int(getattr(flag, name))
    return None


def extract_vertex(flag):
    for name in ("vertex", "v", "vertex_id"):
        if hasattr(flag, name):
            return int(getattr(flag, name))
    return None


def build_flag_index():
    thalions = build_thalions()

    flags = []
    seen = set()

    for th in thalions:
        for f in th.members:
            if f not in seen:
                seen.add(f)
                flags.append(f)

    flags = sorted(flags, key=lambda x: repr(x))
    idx = {f: i for i, f in enumerate(flags)}
    return flags, idx


def permutation_matrix(flags, idx, op):
    import numpy as np

    n = len(flags)
    M = np.zeros((n, n))
    for f in flags:
        i = idx[f]
        g = op(f)
        j = idx[g]
        M[j, i] = 1.0
    return M


def build_face_slot_orders():
    thalions = build_thalions()
    face_buckets = defaultdict(list)

    for th in thalions:
        members = list(th.members)
        if not members:
            continue
        face = extract_face(members[0])
        m0 = members[0]
        edge = extract_edge(m0)
        vertex = extract_vertex(m0)
        key = (
            edge if edge is not None else 10**9,
            vertex if vertex is not None else 10**9,
            th.id,
        )
        face_buckets[face].append((key, th.id))

    face_slot_nodes = {}
    for face in sorted(face_buckets):
        items = sorted(face_buckets[face])
        face_slot_nodes[face] = [th_id for _, th_id in items]
    return face_slot_nodes


def main():
    import numpy as np

    flags, idx = build_flag_index()

    PF = permutation_matrix(flags, idx, F)
    PV = permutation_matrix(flags, idx, V)
    A = PF + PF.T + PV + PV.T

    vals, vecs = np.linalg.eigh(A)
    i = np.argmin(np.abs(vals - TARGET))
    lam = float(vals[i])
    vec = vecs[:, i]
    vec = vec / np.max(np.abs(vec))

    # Aggregate by face directly from flags
    face_vals = defaultdict(list)
    for f, v in zip(flags, vec):
        face_vals[extract_face(f)].append(float(v))

    face_avg = {face: sum(vs) / len(vs) for face, vs in sorted(face_vals.items())}

    # Aggregate by face class
    class_vals = defaultdict(list)
    for face, val in face_avg.items():
        class_vals[FACE_CLASS[face]].append(val)
    class_avg = {cls: sum(vs) / len(vs) for cls, vs in sorted(class_vals.items())}

    # Face-slot layer from thalion ids if possible
    face_slot_nodes = build_face_slot_orders()

    out = {
        "eigenvalue": lam,
        "face_avg": {str(k): v for k, v in face_avg.items()},
        "class_avg": {str(k): v for k, v in class_avg.items()},
        "face_slot_nodes": {str(k): v for k, v in face_slot_nodes.items()},
    }

    path = "reports/spectral/nodal/thalion_cubic_mode_layers.json"
    with open(path, "w") as fp:
        json.dump(out, fp, indent=2)

    print("saved:", path)


if __name__ == "__main__":
    main()
