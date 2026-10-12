"""Alignment of record segments x with text segments y by dynamic programming (preregistration.md, "揃え").

A group is p record segments <-> q text segments, (p, q) in ORDER, cost |sum x - sum y| + lam * (p - 1 + q - 1).
The path starts at (0, 0) and uses every record segment; the text may end early. Among equal costs the earlier
group type in ORDER wins at every step (strict improvement replaces), and at the end the smallest text position.
"""

ORDER = ((1, 1), (2, 1), (1, 2), (3, 1), (1, 3))


def align(x, y, lam, max_group=3):
    """[(i0, i1, j0, j1)] groups: record x[i0:i1] <-> text y[j0:j1]. Raises ValueError when no path exists."""
    order = [(p, q) for p, q in ORDER if p <= max_group and q <= max_group]
    M, T = len(x), len(y)
    if any(v < 0 for v in y):
        raise ValueError("align: the text has an invalid segment")
    INF = float("inf")
    cost = [[INF] * (T + 1) for _ in range(M + 1)]
    back = [[None] * (T + 1) for _ in range(M + 1)]
    cost[0][0] = 0
    px = [0]
    for v in x:
        px.append(px[-1] + v)
    py = [0]
    for v in y:
        py.append(py[-1] + v)
    for i in range(M + 1):
        for j in range(T + 1):
            if i == 0 and j == 0:
                continue
            best, arg = INF, None
            for p, q in order:
                i0, j0 = i - p, j - q
                if i0 < 0 or j0 < 0 or cost[i0][j0] == INF:
                    continue
                c = cost[i0][j0] + abs((px[i] - px[i0]) - (py[j] - py[j0])) + lam * (p - 1 + q - 1)
                if c < best:
                    best, arg = c, (p, q)
            cost[i][j] = best
            back[i][j] = arg
    end_j = None
    for j in range(T + 1):
        if cost[M][j] < INF and (end_j is None or cost[M][j] < cost[M][end_j]):
            end_j = j
    if end_j is None:
        raise ValueError("align: no path (the record is longer than the text allows)")
    groups = []
    i, j = M, end_j
    while i or j:
        p, q = back[i][j]
        groups.append((i - p, i, j - q, j))
        i, j = i - p, j - q
    groups.reverse()
    return groups


def start_map(groups):
    """For each record segment index, the text index of the first text segment of its group."""
    m = {}
    for i0, i1, j0, j1 in groups:
        for i in range(i0, i1):
            m[i] = j0
    return m
