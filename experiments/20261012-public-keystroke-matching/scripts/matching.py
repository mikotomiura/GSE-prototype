"""Split, samples, candidates, windows and credit (preregistration, "Candidates, scope and numbers").

All random draws come from the seed formula (seeds.py), so results do not depend on the order of computation.
Details fixed here before any data (listed in notes.md, "Implementation choices"):
- the split permutes the sorted prompt names and takes the first two as one fold;
- the evaluation sample takes 125 writers per prompt from the sorted IDs (all of them if fewer);
- the pool of a prompt is its writers after exclusion, sorted by ID; decoys are drawn from the pool without the
  record's writer (and without B for the negative control);
- a record with fewer than 5 valid window starts for k uses all of them;
- a decoy window starts uniformly among the k-word windows of the decoy text; the stream of a window draw is
  decoys(prompt, writer, N, k, "<start index>:<draw>").
"""
import os

import numpy as np

import seeds
from align_ext import INF
from synthetic_logs import category, record_segments

DRAWS = {10: 20, 100: 20, 1000: 5}
MUTATE = os.environ.get("MAIN_MUTATE", "")


def split_folds(seed, prompts):
    order = sorted(prompts)
    perm = seeds.rng(seed, "split").permutation(len(order))
    a = sorted(order[i] for i in perm[:len(order) // 2])
    b = sorted(order[i] for i in perm[len(order) // 2:])
    return a, b


def eval_sample(seed, writers_by_prompt, per_prompt=125):
    out = {}
    for p, ws in sorted(writers_by_prompt.items()):
        ids = sorted(ws)
        if len(ids) <= per_prompt:
            out[p] = ids
        else:
            pick = seeds.rng(seed, "eval_sample", p).choice(len(ids), per_prompt, replace=False)
            out[p] = sorted(ids[i] for i in pick)
    return out


def draw_decoys(seed, prompt, writer, N, pool, exclude, draw, k=""):
    """N - 1 pool indices without replacement from the pool minus the excluded indices; None when too few."""
    if MUTATE == "decoys_include_true":
        exclude = set()
    allowed = [i for i in range(len(pool)) if i not in exclude]
    if len(allowed) < N - 1:
        return None
    g = seeds.rng(seed, "decoys", prompt, writer, N, k, draw)
    pick = g.choice(len(allowed), N - 1, replace=False)
    return [allowed[i] for i in pick], g


def credit_stats(true_pos, costs):
    """credit (1/m among the minimum), top-5 credit, reciprocal rank (ties at their mean rank), all infinite,
    only the true candidate infinite."""
    costs = np.asarray(costs, dtype=float)
    finite = np.isfinite(costs)
    n = len(costs)
    if MUTATE == "true_index_shift":
        true_pos = (true_pos + 1) % n
    if not finite.any():
        return 1.0 / n, min(5, n) / n, _mean_rr(1, n), True, False
    if not finite[true_pos]:
        return 0.0, 0.0, _mean_rr(int(finite.sum()) + 1, n), False, True
    t = costs[true_pos]
    less = int((costs < t).sum())
    eq = int((costs == t).sum())
    credit = 1.0 / eq if less == 0 else 0.0
    # top-5: the share of the tied block that falls within the first five ranks
    top5 = max(0, min(5, less + eq) - less) / eq
    return credit, top5, _mean_rr(less + 1, less + eq), False, False


def _mean_rr(first, last):
    return float(np.mean([1.0 / r for r in range(first, last + 1)]))


# --- windows -------------------------------------------------------------------------------------------------------

def nonempty_runs(cats):
    """R0 record segments with their rows (segment_rows) and whether they are non-empty (a counted press)."""
    from synthetic_logs import segment_rows
    segs = record_segments(cats)
    rows = segment_rows(cats)
    out = []
    for (v, idx), (a, b) in zip(segs, rows):
        out.append((a, b, len(idx) > 0))
    return out


def window_row_ranges(cats, k):
    """For each start among the non-empty R0 segments, the row range (first, last) of the window that contains k
    non-empty segments (empty segments between them are inside but not counted), and the indices of its first and
    last segments."""
    runs = nonempty_runs(cats)
    ne = [i for i, (_, _, nonempty) in enumerate(runs) if nonempty]
    out = []
    for s in range(len(ne) - k + 1):
        first, last = ne[s], ne[s + k - 1]
        out.append((runs[first][0], runs[last][1], first, last))
    return out


def word_alignment(src, dst):
    """Word edit-distance alignment of src words to dst words: {src index: dst index} for matches and substitutions.
    Among equal costs: match, substitution, deletion, insertion in this order, then the smaller dst position."""
    n, m = len(src), len(dst)
    D = np.zeros((n + 1, m + 1), dtype=np.int64)
    D[:, 0] = np.arange(n + 1)
    D[0, :] = np.arange(m + 1)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i, j] = min(D[i - 1, j - 1] + (src[i - 1] != dst[j - 1]), D[i - 1, j] + 1, D[i, j - 1] + 1)
    out, i, j = {}, n, m
    while i or j:
        if i and j and src[i - 1] == dst[j - 1] and D[i, j] == D[i - 1, j - 1]:
            out[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif i and j and D[i, j] == D[i - 1, j - 1] + 1:
            out[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif i and D[i, j] == D[i - 1, j] + 1:
            i -= 1
        else:
            j -= 1
    return out


def true_window_starts(rows, final, origins, text_words_final, text_words_dist, k):
    """[(row range, first segment, text start word)] of the valid windows: the true window starts at the distributed
    text word holding most surviving characters of the window's first segment. Windows whose first segment has no
    surviving character, whose first word does not map to the distributed text, or that run past its end are left
    out; the counts of each reason are returned."""
    import re
    cats = [category(r["down_event"]) for r in rows]
    spans = [(m.start(), m.end()) for m in re.finditer(r"[A-Za-z0-9]+", final)]
    word_of_char = {}
    for wi, (a, b) in enumerate(spans):
        for c in range(a, b):
            word_of_char[c] = wi
    char_of_row = {o: ci for ci, o in enumerate(origins) if o is not None}
    mapping = None if text_words_final == text_words_dist else word_alignment(text_words_final, text_words_dist)
    segs = record_segments(cats)
    out, reasons = [], {"no surviving character": 0, "not mapped": 0, "past the end": 0}
    for first_row, last_row, seg_i, seg_j in window_row_ranges(cats, k):
        counts = {}
        for r in segs[seg_i][1]:
            ci = char_of_row.get(r)
            if ci is not None and ci in word_of_char:
                counts[word_of_char[ci]] = counts.get(word_of_char[ci], 0) + 1
        if not counts:
            reasons["no surviving character"] += 1
            continue
        top = max(counts.values())
        wf = min(w for w, c in counts.items() if c == top)
        wd = wf if mapping is None else mapping.get(wf)
        if wd is None:
            reasons["not mapped"] += 1
            continue
        if wd + k > len(text_words_dist):
            reasons["past the end"] += 1
            continue
        out.append(((first_row, last_row), (seg_i, seg_j), wd))
    return out, reasons


def pick_window_starts(seed, prompt, writer, k, valid, n=5):
    if len(valid) <= n:
        return list(range(len(valid)))
    return sorted(int(i) for i in seeds.rng(seed, "window_start", prompt, writer, "", k).choice(len(valid), n,
                                                                                                    replace=False))


def decoy_window(g, n_words, k):
    return int(g.integers(0, n_words - k + 1))
