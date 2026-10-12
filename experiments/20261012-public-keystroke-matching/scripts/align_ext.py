"""Wrapper around the template align.py (preregistration.md "揃え"): full-text end, infinity handling, R7 groups.

The template experiments/20261011-g1-copy-self-trial/scripts/align.py implements the window end only. Here:
- end "window": the template align() is called as is, with its module ORDER replaced by the group list and max_group
  set to the cap (R7: 4 or 6), as the preregistration says;
- end "full": the same recurrence and tie rule (strict improvement in group order) with the end fixed at (M, T);
- no path -> cost infinity; credit() gives 1/m among the minimum, and all candidates infinite -> tie among all.
The self-test checks that the full-end recurrence with a free end chooses the same groups as the template.
"""
import hashlib
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.normpath(os.path.join(HERE, "..", "..", "20261011-g1-copy-self-trial", "scripts", "align.py"))
INF = float("inf")
MUTATE = os.environ.get("SYNTH_MUTATE", "")


def _load_template():
    spec = importlib.util.spec_from_file_location("align_template", TEMPLATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


T = _load_template()


def template_sha256():
    with open(TEMPLATE, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def group_cost(x, y, g, lam):
    i0, i1, j0, j1 = g
    return abs(sum(x[i0:i1]) - sum(y[j0:j1])) + lam * (i1 - i0 - 1 + j1 - j0 - 1)


def path_cost(x, y, groups, lam):
    return sum(group_cost(x, y, g, lam) for g in groups)


def _full(x, y, lam, order):
    M, Tn = len(x), len(y)
    cost = [[INF] * (Tn + 1) for _ in range(M + 1)]
    back = [[None] * (Tn + 1) for _ in range(M + 1)]
    cost[0][0] = 0
    px = [0]
    for v in x:
        px.append(px[-1] + v)
    py = [0]
    for v in y:
        py.append(py[-1] + v)
    for i in range(M + 1):
        for j in range(Tn + 1):
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
    return cost, back


def _backtrack(back, i, j):
    groups = []
    while i or j:
        p, q = back[i][j]
        groups.append((i - p, i, j - q, j))
        i, j = i - p, j - q
    groups.reverse()
    return groups


def free_end(x, y, lam, order):
    """The recurrence of _full with the template's window end (used by the self-test against the template)."""
    cost, back = _full(x, y, lam, order)
    M = len(x)
    end_j = None
    for j in range(len(y) + 1):
        if cost[M][j] < INF and (end_j is None or cost[M][j] < cost[M][end_j]):
            end_j = j
    if end_j is None:
        return INF, None
    return cost[M][end_j], _backtrack(back, M, end_j)


def align(x, y, lam, end, groups=None, max_group=3):
    """(cost, groups) with groups [(i0, i1, j0, j1)]; (inf, None) when no path exists."""
    order = list(groups) if groups is not None else list(T.ORDER)
    if end == "full" and MUTATE == "full_as_window":
        end = "window"
    if end == "window":
        saved = T.ORDER
        T.ORDER = tuple(order)
        try:
            g = T.align(x, y, lam, max_group=max_group)
        except ValueError:
            return INF, None
        finally:
            T.ORDER = saved
        return path_cost(x, y, g, lam), g
    if end != "full":
        raise ValueError("end must be window or full")
    order = [(p, q) for p, q in order if p <= max_group and q <= max_group]
    cost, back = _full(x, y, lam, order)
    c = cost[len(x)][len(y)]
    if c == INF:
        return INF, None
    return c, _backtrack(back, len(x), len(y))


def r7_groups(cfg, p):
    """The R7 group list and cap for suppression probability p (config.json alignment.r7_groups)."""
    g = [tuple(v) for v in cfg["alignment"]["r7_groups"][str(p)]]
    if MUTATE == "r7_default_groups":
        g = list(T.ORDER)
    cap = max(max(a, b) for a, b in g)
    return g, cap


def credit(true_index, costs):
    """(credit, all_infinite, only_true_infinite): 1/m when the true candidate is among the m minimum."""
    finite = [c for c in costs if c < INF]
    if not finite:
        return 1.0 / len(costs), True, False
    if costs[true_index] == INF:
        return 0.0, False, True
    m = min(finite)
    winners = [i for i, c in enumerate(costs) if c == m]
    return (1.0 / len(winners) if true_index in winners else 0.0), False, False
