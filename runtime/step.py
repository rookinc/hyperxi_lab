def step(state, edge, sign):
    """
    state: (vertex, sheet)
    edge: (u, v)
    sign: +1 or -1

    returns next state
    """
    v, sheet = state

    if v not in edge:
        return state

    u, w = edge

    next_vertex = w if v == u else u

    if sign == -1:
        next_sheet = -sheet
    else:
        next_sheet = sheet

    return (next_vertex, next_sheet)
