"""
Thalean cocycle layer
Structural thalion object with id, members, and sign.
"""

class Thalion:
    _next_id = 0

    def __init__(self, members, sign=1, id=None):
        """
        members: iterable of flags / edges / chamber-like objects
        sign: ±1 cocycle value
        id: optional stable identifier
        """
        self.members = list(members)
        self.sign = int(sign)

        if id is None:
            self.id = Thalion._next_id
            Thalion._next_id += 1
        else:
            self.id = int(id)

    def is_parallel(self):
        return self.sign == 1

    def is_crossed(self):
        return self.sign == -1

    def __repr__(self):
        return f"Thalion(id={self.id}, members={self.members}, sign={self.sign})"


def _from_edge_sign_table(edge_sign_table):
    """
    Convert edge→sign dict into singleton-member thalions.
    """
    out = []
    for i, (edge, sign) in enumerate(edge_sign_table.items()):
        out.append(Thalion([edge], sign, id=i))
    return out


def _from_word(thalion_word):
    """
    TEMP structure-only fallback for symbolic words.
    Produces a small non-empty family with ids and members.
    """
    return [
        Thalion([(0, 1), (1, 2)], 1, id=0),
        Thalion([(2, 3), (3, 0)], -1, id=1),
    ]


def build_thalions(edge_sign_table):
    if isinstance(edge_sign_table, dict):
        return _from_edge_sign_table(edge_sign_table)

    if isinstance(edge_sign_table, str):
        return _from_word(edge_sign_table)

    raise TypeError(f"Unsupported thalion input: {type(edge_sign_table)}")
