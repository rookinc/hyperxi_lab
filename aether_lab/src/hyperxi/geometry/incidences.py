from __future__ import annotations

class DodecahedronIncidence:
    """
    Simple combinatorial dodecahedron.

    20 vertices
    30 edges
    12 faces
    """

    def __init__(self):

        self.faces = {
            0:  (0, 1, 2, 3, 4),
            1:  (0, 5, 10, 6, 1),
            2:  (1, 6, 11, 7, 2),
            3:  (2, 7, 12, 8, 3),
            4:  (3, 8, 13, 9, 4),
            5:  (4, 9, 14, 5, 0),
            6:  (15, 10, 5, 14, 19),
            7:  (16, 11, 6, 10, 15),
            8:  (17, 12, 7, 11, 16),
            9:  (18, 13, 8, 12, 17),
            10: (19, 14, 9, 13, 18),
            11: (15, 16, 17, 18, 19),
        }

        self.vertices = list(range(20))

    def summary(self):

        return {
            "vertices": 20,
            "faces": 12,
        }


if __name__ == "__main__":

    inc = DodecahedronIncidence()

    print("Dodecahedron loaded")
    print(inc.summary())
