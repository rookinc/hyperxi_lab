from __future__ import annotations

from typing import Tuple

from ..geometry.flags import Flag, FlagModel


class GeneratorError(ValueError):
    """Raised when a generator cannot be applied lawfully."""


class CoxeterGenerators:
    """
    Local flag-action generators on the 120 flags of a single dodecahedron.

    State:
        Flag(vertex, edge, face)

    Generators:
    - S = edge flip
    - F = face rotation
    - V = vertex rotation
    """

    def __init__(self, flag_model: FlagModel) -> None:
        self.fm = flag_model
        self.inc = flag_model.inc

    # ------------------------------------------------------------------
    # Basic helpers
    # ------------------------------------------------------------------

    def _edge_vertices(self, edge_id: int) -> Tuple[int, int]:
        return self.fm.edges[edge_id]

    def _other_vertex_on_edge(self, edge_id: int, vertex: int) -> int:
        a, b = self._edge_vertices(edge_id)
        if vertex == a:
            return b
        if vertex == b:
            return a
        raise GeneratorError(f"Vertex {vertex} is not incident to edge {edge_id}.")

    def _face_vertices(self, face_id: int) -> Tuple[int, int, int, int, int]:
        return self.inc.faces[face_id]

    def _edge_id_from_vertices(self, u: int, v: int) -> int:
        key = tuple(sorted((u, v)))
        try:
            return self.fm.edge_lookup[key]
        except KeyError as exc:
            raise GeneratorError(f"No edge exists between vertices {u} and {v}.") from exc

    def _incident_edges_at_vertex_in_face(self, vertex: int, face: int) -> Tuple[int, int]:
        verts = self._face_vertices(face)
        if vertex not in verts:
            raise GeneratorError(f"Vertex {vertex} is not on face {face}.")
        i = verts.index(vertex)
        prev_v = verts[(i - 1) % 5]
        next_v = verts[(i + 1) % 5]
        e_prev = self._edge_id_from_vertices(prev_v, vertex)
        e_next = self._edge_id_from_vertices(vertex, next_v)
        return e_prev, e_next

    def _other_edge_at_vertex_in_face(self, vertex: int, edge: int, face: int) -> int:
        e0, e1 = self._incident_edges_at_vertex_in_face(vertex, face)
        if edge == e0:
            return e1
        if edge == e1:
            return e0
        raise GeneratorError(
            f"Edge {edge} is not one of the two face-boundary edges at vertex {vertex} on face {face}."
        )

    def _face_edge_ids(self, face_id: int) -> Tuple[int, int, int, int, int]:
        verts = self._face_vertices(face_id)
        out = []
        for i in range(5):
            out.append(self._edge_id_from_vertices(verts[i], verts[(i + 1) % 5]))
        return tuple(out)

    def _other_face_on_edge(self, edge_id: int, face_id: int) -> int:
        containing = [f for f in self.inc.faces if edge_id in self._face_edge_ids(f)]
        if face_id not in containing:
            raise GeneratorError(f"Face {face_id} does not contain edge {edge_id}.")
        if len(containing) != 2:
            raise GeneratorError(
                f"Edge {edge_id} is incident to {len(containing)} faces, expected 2."
            )
        return containing[1] if containing[0] == face_id else containing[0]

    # ------------------------------------------------------------------
    # Lawfulness
    # ------------------------------------------------------------------

    def is_legal(self, flag: Flag) -> bool:
        a, b = self._edge_vertices(flag.edge)
        if flag.vertex not in (a, b):
            return False
        verts = self._face_vertices(flag.face)
        if flag.vertex not in verts:
            return False
        if flag.edge not in self._face_edge_ids(flag.face):
            return False
        return True

    def require_legal(self, flag: Flag) -> None:
        if not self.is_legal(flag):
            raise GeneratorError(f"Illegal flag: {flag}")

    # ------------------------------------------------------------------
    # S = edge flip
    # ------------------------------------------------------------------

    def S(self, flag: Flag) -> Flag:
        """
        Swap the endpoint on the same edge, preserving face and edge.
        """
        self.require_legal(flag)
        out = Flag(
            vertex=self._other_vertex_on_edge(flag.edge, flag.vertex),
            edge=flag.edge,
            face=flag.face,
        )
        self.require_legal(out)
        return out

    # ------------------------------------------------------------------
    # F = face rotation
    # ------------------------------------------------------------------

    def F(self, flag: Flag) -> Flag:
        """
        Rotate one step along the face boundary.

        If the current flag is (v_i, e_i, f), then:
            F(v_i, e_i, f) = (v_{i+1}, e_{i+1}, f)

        If the current flag is (v_{i+1}, e_i, f), then:
            F(v_{i+1}, e_i, f) = (v_i, e_{i-1}, f)
        """
        self.require_legal(flag)

        verts = self._face_vertices(flag.face)
        a, b = self._edge_vertices(flag.edge)
        i = verts.index(flag.vertex)
        prev_v = verts[(i - 1) % 5]
        next_v = verts[(i + 1) % 5]

        if {flag.vertex, next_v} == {a, b}:
            new_vertex = next_v
            new_next = verts[(i + 2) % 5]
            new_edge = self._edge_id_from_vertices(new_vertex, new_next)
        elif {prev_v, flag.vertex} == {a, b}:
            new_vertex = prev_v
            new_prev = verts[(i - 2) % 5]
            new_edge = self._edge_id_from_vertices(new_prev, new_vertex)
        else:
            raise GeneratorError(
                f"Edge {flag.edge} is not one of the two boundary edges at vertex {flag.vertex} on face {flag.face}."
            )

        out = Flag(vertex=new_vertex, edge=new_edge, face=flag.face)
        self.require_legal(out)
        return out

    # ------------------------------------------------------------------
    # V = vertex rotation
    # ------------------------------------------------------------------

    def V(self, flag: Flag) -> Flag:
        """
        Rotate one step around the current vertex.

        Procedure:
            1) inside the current face, switch to the other edge incident to the same vertex
            2) across that new edge, pivot to the unique other face containing it
        """
        self.require_legal(flag)

        new_edge = self._other_edge_at_vertex_in_face(flag.vertex, flag.edge, flag.face)
        new_face = self._other_face_on_edge(new_edge, flag.face)

        out = Flag(vertex=flag.vertex, edge=new_edge, face=new_face)
        self.require_legal(out)
        return out

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------

    def apply(self, flag: Flag, move: str) -> Flag:
        if move == "S":
            return self.S(flag)
        if move == "F":
            return self.F(flag)
        if move == "V":
            return self.V(flag)
        raise GeneratorError(f"Unknown move {move!r}")

    def apply_word(self, flag: Flag, word: str) -> Flag:
        cur = flag
        for ch in word:
            cur = self.apply(cur, ch)
        return cur


if __name__ == "__main__":
    fm = FlagModel()
    gen = CoxeterGenerators(fm)

    x0 = fm.get(0)
    print("x0 =", x0)
    print("S(x0) =", gen.S(x0))
    print("F(x0) =", gen.F(x0))
    print("V(x0) =", gen.V(x0))

    # sanity
    assert gen.S(gen.S(x0)) == x0

    for i in range(fm.num_flags()):
        x = fm.get(i)
        assert gen.is_legal(x)
        assert gen.is_legal(gen.S(x))
        assert gen.is_legal(gen.F(x))
        assert gen.is_legal(gen.V(x))

    print("All local generator lawfulness checks passed.")
