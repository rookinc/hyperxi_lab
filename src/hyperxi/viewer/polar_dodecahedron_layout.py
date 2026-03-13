# src/hyperxi/viewer/polar_dodecahedron_layout.py

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt, cos, sin, pi
from typing import Dict, Iterable, List, Tuple

Vec3 = Tuple[float, float, float]


@dataclass(frozen=True)
class ChamberKey:
    face: int
    slot: int


def _normalize(v: Vec3) -> Vec3:
    x, y, z = v
    n = (x * x + y * y + z * z) ** 0.5
    if n == 0:
        return (0.0, 0.0, 0.0)
    return (x / n, y / n, z / n)


def _add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _scale(v: Vec3, s: float) -> Vec3:
    return (v[0] * s, v[1] * s, v[2] * s)


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _rotate_around_axis(v: Vec3, axis: Vec3, theta: float) -> Vec3:
    """
    Rodrigues rotation formula.
    """
    k = _normalize(axis)
    c = cos(theta)
    s = sin(theta)
    kv = _cross(k, v)
    kk = _dot(k, v)
    return _add(
        _add(_scale(v, c), _scale(kv, s)),
        _scale(k, kk * (1.0 - c)),
    )


def icosahedron_vertices() -> List[Vec3]:
    """
    The 12 vertices of the icosahedron are the 12 face-centers of the dodecahedron.
    Normalized to unit radius.
    """
    phi = (1.0 + sqrt(5.0)) / 2.0
    raw = [
        (0, 1, phi), (0, -1, phi), (0, 1, -phi), (0, -1, -phi),
        (1, phi, 0), (-1, phi, 0), (1, -phi, 0), (-1, -phi, 0),
        (phi, 0, 1), (-phi, 0, 1), (phi, 0, -1), (-phi, 0, -1),
    ]
    return [_normalize(v) for v in raw]


def _choose_face_basis(normal: Vec3) -> Tuple[Vec3, Vec3]:
    """
    Build a stable tangent basis (u, v) for the plane perpendicular to normal.
    """
    n = _normalize(normal)
    trial = (0.0, 0.0, 1.0)
    if abs(_dot(n, trial)) > 0.9:
        trial = (0.0, 1.0, 0.0)
    u = _normalize(_cross(trial, n))
    v = _normalize(_cross(n, u))
    return u, v


def _face_pentagon_positions(center: Vec3, normal: Vec3, r: float, twist: float = 0.0) -> List[Vec3]:
    """
    Five slot positions around a face center.
    """
    u, v = _choose_face_basis(normal)
    pts: List[Vec3] = []
    for k in range(5):
        ang = twist + 2.0 * pi * k / 5.0
        offset = _add(_scale(u, r * cos(ang)), _scale(v, r * sin(ang)))
        pts.append(_add(center, offset))
    return pts


def build_polar_dodecahedron_face_centers(
    shell_radius: float = 3.0,
    shell_gap: float = 3.2,
    face0_pole: int = 0,
    face1_pole: int = 1,
) -> Tuple[List[Vec3], List[Vec3]]:
    """
    Returns two sets of 12 face centers.

    The 'south' shell is oriented so face0_pole points roughly -Z.
    The 'north' shell is oriented so face1_pole points roughly +Z.
    """
    base = icosahedron_vertices()

    target_south = (0.0, 0.0, -1.0)
    target_north = (0.0, 0.0, 1.0)

    def align_shell(points: List[Vec3], pole_index: int, target: Vec3) -> List[Vec3]:
        src = _normalize(points[pole_index])
        tgt = _normalize(target)

        dot = max(-1.0, min(1.0, _dot(src, tgt)))
        if abs(dot - 1.0) < 1e-9:
            aligned = points[:]
        elif abs(dot + 1.0) < 1e-9:
            axis = (1.0, 0.0, 0.0)
            if abs(_dot(src, axis)) > 0.9:
                axis = (0.0, 1.0, 0.0)
            aligned = [_rotate_around_axis(p, axis, pi) for p in points]
        else:
            axis = _cross(src, tgt)
            theta = acos_clamped(dot)
            aligned = [_rotate_around_axis(p, axis, theta) for p in points]
        return aligned

    south = align_shell(base, face0_pole, target_south)
    north = align_shell(base, face1_pole, target_north)

    south = [_add(_scale(p, shell_radius), (0.0, 0.0, -shell_gap / 2.0)) for p in south]
    north = [_add(_scale(p, shell_radius), (0.0, 0.0, shell_gap / 2.0)) for p in north]

    return south, north


def acos_clamped(x: float) -> float:
    from math import acos
    return acos(max(-1.0, min(1.0, x)))


def build_chamber_positions(
    face_slot_keys: Iterable[ChamberKey],
    face_to_shell: Dict[int, int] | None = None,
    shell_radius: float = 3.0,
    shell_gap: float = 3.2,
    slot_radius: float = 0.42,
    face0_pole: int = 0,
    face1_pole: int = 1,
    face7_twist: float = pi / 5.0,
) -> Dict[ChamberKey, Vec3]:
    """
    Assign each (face, slot) chamber to a 3D point.

    face_to_shell:
      0 -> south shell
      1 -> north shell

    By default:
      faces 0..5 on south shell
      faces 6..11 on north shell

    face 7 gets an extra twist so you can directly test the symmetry-breaking hypothesis.
    """
    south_faces, north_faces = build_polar_dodecahedron_face_centers(
        shell_radius=shell_radius,
        shell_gap=shell_gap,
        face0_pole=face0_pole,
        face1_pole=face1_pole,
    )

    if face_to_shell is None:
        face_to_shell = {f: 0 if f < 6 else 1 for f in range(12)}

    positions: Dict[ChamberKey, Vec3] = {}
    cached_face_slots: Dict[Tuple[int, int], List[Vec3]] = {}

    for key in face_slot_keys:
        face = key.face
        slot = key.slot

        shell = face_to_shell.get(face, 0)
        face_center = south_faces[face] if shell == 0 else north_faces[face]

        shell_origin = (0.0, 0.0, -shell_gap / 2.0) if shell == 0 else (0.0, 0.0, shell_gap / 2.0)
        normal = _normalize(_sub(face_center, shell_origin))

        twist = 0.0
        if face == 7:
            twist = face7_twist

        cache_key = (face, shell)
        if cache_key not in cached_face_slots:
            cached_face_slots[cache_key] = _face_pentagon_positions(
                center=face_center,
                normal=normal,
                r=slot_radius,
                twist=twist,
            )

        positions[key] = cached_face_slots[cache_key][slot % 5]

    return positions


def project_xy(positions_3d: Dict[ChamberKey, Vec3], yaw: float = 0.6, pitch: float = -0.45, scale: float = 120.0) -> Dict[ChamberKey, Tuple[float, float]]:
    """
    Simple camera projection to 2D canvas coords.
    """
    out: Dict[ChamberKey, Tuple[float, float]] = {}

    cy, sy = cos(yaw), sin(yaw)
    cx, sx = cos(pitch), sin(pitch)

    for key, (x, y, z) in positions_3d.items():
        # yaw around z
        x1 = cy * x - sy * y
        y1 = sy * x + cy * y
        z1 = z

        # pitch around x
        x2 = x1
        y2 = cx * y1 - sx * z1
        z2 = sx * y1 + cx * z1

        # weak perspective
        d = 10.0
        f = d / (d - z2)
        out[key] = (scale * f * x2, scale * f * y2)

    return out

