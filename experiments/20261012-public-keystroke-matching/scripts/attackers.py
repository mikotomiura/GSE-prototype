"""Attackers A0, A1, A1', A2, A2-b and A3 (preregistration, "Attackers"; config.json attackers).

Every attacker returns a cost per candidate (lower is better; A3 returns the negative score). Candidates are given
as Cand objects built once per text. Details the preregistration leaves open are fixed here, before any data, and
listed in notes.md ("Implementation choices"):
- an interval is the difference of press times; its log uses max(interval, 1 ms);
- A3 (except R3-u and R7): a record segment without BackSpace is paired with the letters and digits of the text
  words of its alignment group; when a group has several record segments, each takes the characters that follow
  those of the earlier segments of the group; intervals are taken between consecutive counted presses of the segment;
  every such interval of the record is scored, and an interval without a character pair in the candidate (the
  candidate's characters run out) takes the value of all intervals, so that every candidate has the same number of
  terms (otherwise a sum of log-likelihoods favours candidates that cover fewer intervals);
- A3 on R3-t: the probability that the interval lies in (d - w, d + w), where d is the difference of rounded times;
- the character-pair table of A3 comes from consecutive character presses of the training logs in R0 (only modifier
  and navigation presses may lie between them; a shortcut, BackSpace, Delete, mouse or other press breaks the chain);
- the length term of A3 on R3-u: add-one smoothing over the integers from the training minimum - 50 to the maximum
  + 50, and the same smoothed mass for a value outside that range;
- A3 on R7: the characters of a group are shared among its record segments in proportion to their values; every
  record segment with two or more remaining presses is scored, a share below one character as one character.
"""
import math
import os
import re

import numpy as np
from sklearn.linear_model import LogisticRegression

import align_vec
from align_ext import INF
from replay import a1_r2, a1_text, a1prime, lengths_of_items
from synthetic_logs import CHAR_CATS, MOD_CATS, NAV_CATS, SEP_CATS, category, record_segments, shortcut_flags, word_lengths

LAM = 8
MUTATE = os.environ.get("MAIN_MUTATE", "")
APPLICABLE = {
    "A0": None,  # all forms
    "A1": ("R0", "R1", "R2", "R5", "R6"),
    "A1p": ("R3", "R3-t", "R7"),
    "A2": ("R2", "R3", "R3-t", "R4", "R7"),
    "A2b": ("R3-u",),
    "A3": ("R0", "R1", "R2", "R3", "R3-t", "R3-u", "R5", "R6", "R7"),
}
TYPE_OF = {"letter": "L", "digit": "D", "space": "S", "punctuation": "P", "enter": "E"}


def applies(attacker, base):
    forms = APPLICABLE[attacker]
    return forms is None or base in forms


class Cand:
    """A candidate text: word lengths (letters and digits), the words, the character count and the text."""

    def __init__(self, text):
        self.text = text.replace("\r\n", "\n")
        self.spans = [(m.start(), m.end()) for m in re.finditer(r"[A-Za-z0-9]+", self.text)]
        self.words = [self.text[a:b] for a, b in self.spans]
        self.lens = [len(w) for w in self.words]
        self.alnum = sum(self.lens)
        self.nchars = len(self.text)
        self.starts = np.concatenate([[0], np.cumsum(self.lens)]).astype(np.int64)
        self._codes = {}

    def codes(self, table):
        """The letters and digits of the words, concatenated, as character codes of the table (kept per table: the
        codes index that table's vocabulary)."""
        c = self._codes.get(0 if MUTATE == "cand_codes_shared" else id(table))
        if c is None:
            c = self._codes[0 if MUTATE == "cand_codes_shared" else id(table)] = table.encode("".join(self.words))
        return c


class WindowCand:
    """k words of a candidate text from word s: the same fields as Cand, sharing the parent's character codes. The
    window text runs from the first word to the end of the last word plus the character that follows it."""

    def __init__(self, parent, s, k):
        a, end = parent.spans[s][0], parent.spans[s + k - 1][1]
        self.text = parent.text[a:end + 1 if end < len(parent.text) else end]
        self.words = parent.words[s:s + k]
        self.lens = parent.lens[s:s + k]
        self.alnum = sum(self.lens)
        self.nchars = len(self.text)
        self.starts = parent.starts[s:s + k + 1] - parent.starts[s]
        self.parent, self.s, self.k = parent, s, k

    def codes(self, table):
        c = self.parent.codes(table)
        return c[self.parent.starts[self.s]:self.parent.starts[self.s + self.k]]


def char_type(c):
    if c.isalpha():
        return "L"
    if c.isdigit():
        return "D"
    if c == " ":
        return "S"
    if c == "\n":
        return "E"
    return "P"


def norm_char(c):
    return c.lower()


def log_iv(d):
    return math.log(max(d, 1))


# --- A0 -----------------------------------------------------------------------------------------------------------

def a0_record(rel):
    """Letter and digit presses - BackSpace presses (the segment rule; R3-u: char presses; R7: x 1/(1 - p);
    R4: the sum of the released values)."""
    if rel.base == "R4":
        return float(sum(rel.values))
    v = float(sum(x for x, _ in record_segments(rel.cats(), merge_char=(rel.base == "R3-u"))))
    if rel.base == "R7":
        v = v / (1 - rel.p)
    return v


def a0_text(c, rel):
    if rel.base == "R3-u":
        return float(c.nchars)
    if rel.base == "R4":
        return float(sum(v // rel.p for v in c.lens))
    return float(c.alnum)


def a0_costs(rel, cands):
    r = a0_record(rel)
    return np.array([abs(r - a0_text(c, rel)) for c in cands])


# --- A1, A1', A2 --------------------------------------------------------------------------------------------------

def _groups(rel, cfg):
    if rel.base == "R7":
        g = [tuple(v) for v in cfg["alignment"]["r7_groups"][str(rel.p)]]
        return g, max(max(a, b) for a, b in g)
    return None, 3


def text_values(c, rel):
    if rel.base == "R4":
        return [v // rel.p for v in c.lens]
    if rel.base == "R7":
        return [(1 - rel.p) * v for v in c.lens]
    return c.lens


def a1_lengths(rel):
    if rel.base in ("R0", "R1", "R5", "R6"):
        return word_lengths(a1_text(rel.rows))
    if rel.base == "R2":
        return lengths_of_items(a1_r2(rel.cats(), [r["cursor_position"] for r in rel.rows]))
    return lengths_of_items(a1prime(rel.cats()))


def record_values(rel):
    if rel.base == "R4":
        return list(rel.values)
    return [v for v, _ in record_segments(rel.cats())]


def align_costs(x, rel, cands, cfg, end="full", lam=LAM, memo=None):
    """Alignment costs; memo (a dict per record and candidate list) reuses the result for the same record values
    and text transformation (for example R3 and R3-t, which differ only in times)."""
    key = (tuple(x), rel.base if rel.base in ("R4", "R7") else "", rel.p if rel.base in ("R4", "R7") else None,
           end, lam)
    if memo is not None and key in memo:
        return memo[key]
    groups, cap = _groups(rel, cfg)
    out = align_vec.costs(x, [text_values(c, rel) for c in cands], lam, end, groups, cap)
    if memo is not None:
        memo[key] = out
    return out


# --- A2-b ---------------------------------------------------------------------------------------------------------

def _press_features(times, i):
    """Log intervals to the previous and next press and two presses before and after (None when missing)."""
    n = len(times)

    def iv(a, b):
        return log_iv(times[b] - times[a]) if 0 <= a < n and 0 <= b < n else None

    return [iv(i - 1, i), iv(i, i + 1), iv(i - 2, i - 1), iv(i + 1, i + 2)]


class BoundaryModel:
    """Logistic regression on R3-u char presses: is the char a separator (space, punctuation, Enter)?
    config.json attackers.A2b: L2, C = 1.0, lbfgs, max_iter 1000, no class weight, threshold 0.5; features
    standardised with the training mean and SD; a missing interval is filled with the training median."""

    def __init__(self, train_pairs, cfg):
        X, y = [], []
        for r0_rows, r3u in train_pairs:
            cats = r3u.cats()
            sc = shortcut_flags(cats)
            times = r3u.times()
            for i, c in enumerate(cats):
                if c == "char" and not sc[i]:
                    X.append(_press_features(times, i))
                    y.append(category(r0_rows[i]["down_event"]) in SEP_CATS)
        cols = list(zip(*X)) if X else [[]] * 4
        self.median = [float(np.median([v for v in col if v is not None])) for col in cols]
        F = self._fill(X)
        self.mean = F.mean(axis=0)
        self.sd = F.std(axis=0)
        self.sd[self.sd == 0] = 1.0
        self.clf = LogisticRegression(penalty="l2", C=1.0, solver="lbfgs", max_iter=1000, class_weight=None)
        self.clf.fit((F - self.mean) / self.sd, np.array(y, dtype=int))

    def _fill(self, X):
        return np.array([[self.median[j] if v is None else v for j, v in enumerate(row)] for row in X], dtype=float)

    def segments(self, rel):
        cats = rel.cats()
        sc = shortcut_flags(cats)
        times = rel.times()
        idx = [i for i, c in enumerate(cats) if c == "char" and not sc[i]]
        sep = set()
        if idx:
            F = self._fill([_press_features(times, i) for i in idx])
            p = self.clf.predict_proba((F - self.mean) / self.sd)[:, 1]
            sep = {i for i, pi in zip(idx, p) if pi >= 0.5}
        segs, v, rows, counted = [], 0, [], False
        for i, c in enumerate(cats):
            if sc[i]:
                continue
            if c == "char" and i in sep:
                segs.append((v, rows))
                v, rows, counted = 0, [], False
            elif c == "char":
                v += 1
                rows.append(i)
                counted = True
            elif c == "backspace":
                v -= 1
                rows.append(i)
                counted = True
        if counted:
            segs.append((v, rows))
        return segs


# --- A3 -----------------------------------------------------------------------------------------------------------

def char_chain(cats, keys):
    """Pairs (row a, row b) of consecutive character presses: only modifier and navigation presses between them;
    a shortcut, BackSpace, Delete, mouse or other press breaks the chain. keys: the pressed keys (R0) or None."""
    sc = shortcut_flags(cats)
    pairs, last = [], None
    for i, c in enumerate(cats):
        if c in MOD_CATS or c in NAV_CATS:
            continue
        if (c in CHAR_CATS or c == "char") and not sc[i]:
            if last is not None:
                pairs.append((last, i))
            last = i
        else:
            last = None
    return pairs


def key_char(k):
    return {"Space": " ", "Enter": "\n"}.get(k, k)


class DigraphTable:
    """Mean and variance of log intervals per character pair, with fallbacks to the character-type pair and to all
    intervals when fewer than min_count (config.json attackers.A3.min_digraph_count = 20)."""

    def __init__(self, train_r0_rows, min_count=20):
        by_pair, by_type, allv = {}, {}, []
        for rows in train_r0_rows:
            cats = [category(r["down_event"]) for r in rows]
            for a, b in char_chain(cats, None):
                ca, cb = norm_char(key_char(rows[a]["down_event"])), norm_char(key_char(rows[b]["down_event"]))
                v = log_iv(rows[b]["down_time"] - rows[a]["down_time"])
                by_pair.setdefault((ca, cb), []).append(v)
                by_type.setdefault((char_type(ca), char_type(cb)), []).append(v)
                allv.append(v)
        self.min_count = min_count
        self.all = _mv(allv)
        self.type = {k: _mv(v) for k, v in by_type.items() if len(v) >= min_count}
        self.pair = {k: _mv(v) for k, v in by_pair.items() if len(v) >= min_count}
        self.vocab, self._mats = {}, None

    def encode(self, s):
        """Character codes (an index per distinct normalised character); new characters extend the vocabulary."""
        out = np.empty(len(s), dtype=np.int64)
        for i, c in enumerate(s):
            c = norm_char(c)
            k = self.vocab.get(c)
            if k is None:
                k = self.vocab[c] = len(self.vocab)
                self._mats = None
            out[i] = k
        return out

    def matrices(self):
        """(MU, VAR) over the vocabulary: params(a, b) for every pair of codes."""
        if self._mats is None:
            chars = sorted(self.vocab, key=self.vocab.get)
            n = len(chars)
            MU, VAR = np.empty((n, n)), np.empty((n, n))
            for a in chars:
                for b in chars:
                    MU[self.vocab[a], self.vocab[b]], VAR[self.vocab[a], self.vocab[b]] = self.params(a, b)
            self._mats = (MU, VAR)
        return self._mats

    def params(self, a, b):
        a, b = norm_char(a), norm_char(b)
        if (a, b) in self.pair:
            return self.pair[(a, b)]
        t = (char_type(a), char_type(b))
        if t in self.type:
            return self.type[t]
        return self.all

    def loglik(self, a, b, d, w=None):
        """a, b: the characters; None for an interval without a character pair (the value of all intervals)."""
        mu, var = self.all if a is None else self.params(a, b)
        sd = math.sqrt(var)
        if w is None:
            x = log_iv(d)
            return -0.5 * math.log(2 * math.pi * var) - (x - mu) ** 2 / (2 * var)
        lo, hi = d - w, d + w
        p = _ncdf((math.log(hi) - mu) / sd) - (_ncdf((math.log(lo) - mu) / sd) if lo > 0 else 0.0)
        return math.log(max(p, 1e-300))


def _mv(v):
    a = np.array(v, dtype=float)
    var = float(a.var()) if len(a) > 1 else 0.0
    return float(a.mean()) if len(a) else 0.0, max(var, 1e-6)


def _ncdf(z):
    return 0.5 * math.erfc(-z / math.sqrt(2))


def segment_presses(cats, merge_char=False):
    """Per record segment: (value, counted letter/digit rows in order, has BackSpace)."""
    out = []
    for v, idx in record_segments(cats, merge_char=merge_char):
        has_bs = any(cats[i] == "backspace" for i in idx)
        out.append((v, [i for i in idx if cats[i] != "backspace"], has_bs))
    return out


def a3_segment_score(table, segs, times, groups, cand, w=None):
    """(sum, number) of log-likelihoods of the intervals of record segments without BackSpace under the character
    pairs of the aligned text (A3 on forms with a category column, on the A2 alignment)."""
    total, n = 0.0, 0
    for i0, i1, j0, j1 in groups:
        chars = "".join(cand.words[j0:j1])
        off = 0
        for s in range(i0, i1):
            v, rows, has_bs = segs[s]
            if not has_bs:
                for t in range(1, len(rows)):
                    d = times[rows[t]] - times[rows[t - 1]]
                    if off + t < len(chars):
                        total += table.loglik(chars[off + t - 1], chars[off + t], d, w)
                    elif MUTATE == "a3_skip_missing":
                        break
                    else:
                        total += table.loglik(None, None, d, w)
                    n += 1
            off += max(v, 0)
    return total, n


class SegPrep:
    """The record side of A3: for each interval of a segment without BackSpace, its segment and position t, and the
    interval (raw and log)."""

    def __init__(self, segs, times):
        self.values = np.array([max(v, 0) for v, _, _ in segs], dtype=np.int64)
        seg, t, d = [], [], []
        for s, (v, rows, has_bs) in enumerate(segs):
            if not has_bs:
                for k in range(1, len(rows)):
                    seg.append(s)
                    t.append(k)
                    d.append(times[rows[k]] - times[rows[k - 1]])
        self.seg = np.array(seg, dtype=np.int64)
        self.t = np.array(t, dtype=np.int64)
        self.d = np.array(d, dtype=float)
        self.logd = np.log(np.maximum(self.d, 1))


_ERFC = np.frompyfunc(math.erfc, 1, 1)


def _ncdf_vec(z):
    return 0.5 * _ERFC(-z / math.sqrt(2)).astype(float)


def _loglik_vec(mu, var, prep, w):
    if w is None:
        return -0.5 * np.log(2 * np.pi * var) - (prep.logd - mu) ** 2 / (2 * var)
    sd = np.sqrt(var)
    lo, hi = prep.d - w, prep.d + w
    up = _ncdf_vec((np.log(hi) - mu) / sd)
    low = np.zeros(len(lo))
    pos = lo > 0
    if pos.any():
        low[pos] = _ncdf_vec((np.log(lo[pos]) - mu[pos]) / sd[pos])
    return np.log(np.maximum(up - low, 1e-300))


def a3_scores(table, prep, cands, groups_list, w=None):
    """(sum, number) per candidate, vectorised over the intervals; equals a3_segment_score (checked in the
    self-test). A candidate without groups gives (nan, 0)."""
    S = len(prep.values)
    out_sum = np.full(len(cands), np.nan)
    out_n = np.zeros(len(cands), dtype=np.int64)
    for c, (cand, groups) in enumerate(zip(cands, groups_list)):
        if groups is None:
            continue
        codes = cand.codes(table)
        MU, VAR = table.matrices()
        gstart, gend, off = np.zeros(S, np.int64), np.zeros(S, np.int64), np.zeros(S, np.int64)
        for i0, i1, j0, j1 in groups:
            o = 0
            for s in range(i0, i1):
                gstart[s], gend[s], off[s] = cand.starts[j0], cand.starts[j1], o
                o += prep.values[s]
        pos = gstart[prep.seg] + off[prep.seg] + prep.t
        valid = pos < gend[prep.seg]
        mu = np.full(len(pos), table.all[0])
        var = np.full(len(pos), table.all[1])
        if valid.any():
            a, b = codes[pos[valid] - 1], codes[pos[valid]]
            mu[valid], var[valid] = MU[a, b], VAR[a, b]
        ll = _loglik_vec(mu, var, prep, w)
        if MUTATE == "a3_skip_missing":
            ll = ll[valid]
        out_sum[c], out_n[c] = float(ll.sum()), len(ll)
    return out_sum, out_n


def a3_costs(rel, cands, table, end="full", cache=None):
    """A3 on R0, R1, R2, R3, R3-t, R5 and R6: the A2 alignment, then the summed interval log-likelihood (cost is the
    negative). Candidates without a path get infinite cost. cache keeps the record side across calls."""
    if cache is not None and "a3" in cache:
        x, prep = cache["a3"]
    else:
        segs = segment_presses(rel.cats())
        x, prep = [v for v, _, _ in segs], SegPrep(segs, rel.times())
        if cache is not None:
            cache["a3"] = (x, prep)
    w = rel.p if rel.base == "R3-t" else None
    out = np.full(len(cands), INF)
    for s in range(0, len(cands), 100):
        chunk = cands[s:s + 100]
        al = align_vec.align_many(x, [c.lens for c in chunk], LAM, end)
        sc, _ = a3_scores(table, prep, chunk, [g for _, g in al], w)
        ok = ~np.isnan(sc)
        part = out[s:s + len(chunk)]
        part[ok] = sc[ok] if MUTATE == "a3_sign" else -sc[ok]
    return out


class LengthTerm:
    """A3 on R3-u: the distribution of (replayed char count - text character count) on training logs in R3-u."""

    def __init__(self, diffs):
        self.n = len(diffs)
        self.lo, self.hi = min(diffs) - 50, max(diffs) + 50
        self.K = self.hi - self.lo + 1
        self.count = {}
        for d in diffs:
            self.count[d] = self.count.get(d, 0) + 1

    def loglik(self, d):
        c = self.count.get(d, 0) if self.lo <= d <= self.hi else 0
        return math.log((c + 1) / (self.n + self.K))


def r3u_replay(rel):
    return a1prime(rel.cats(), uncertain_home_end=True)


def a3_r3u_scores(rel, cands, table, length):
    """(sum version, mean version, length only) scores per candidate; costs are their negatives."""
    cats = rel.cats()
    times = rel.times()
    items = r3u_replay(rel)
    chain = set(char_chain(cats, None))
    n = len(items)
    out = []
    for c in cands:
        terms = []
        m = min(n, c.nchars)
        for t in range(1, m):
            a, b = items[t - 1][1], items[t][1]
            if (a, b) in chain:
                terms.append(table.loglik(c.text[t - 1], c.text[t], times[b] - times[a]))
        ls = length.loglik(n - c.nchars)
        s = sum(terms)
        mean = s / len(terms) if terms else 0.0
        out.append((s + ls, mean + ls, ls))
    return out


class R7Duration:
    """A3 on R7: log segment duration regressed on the log character count of the aligned text, estimated on
    training logs with the same suppression, aligned to their own texts by the same alignment."""

    def __init__(self, pairs):
        X = np.array([math.log(c) for c, _ in pairs])
        Y = np.array([math.log(max(d, 1)) for _, d in pairs])
        A = np.vstack([np.ones_like(X), X]).T
        coef, *_ = np.linalg.lstsq(A, Y, rcond=None)
        self.a, self.b = float(coef[0]), float(coef[1])
        r = Y - A @ coef
        self.var = max(float(r.var()), 1e-6)

    def loglik(self, chars, dur):
        x = math.log(max(dur, 1))
        mu = self.a + self.b * math.log(chars)
        return -0.5 * math.log(2 * math.pi * self.var) - (x - mu) ** 2 / (2 * self.var)


def r7_segment_pairs(segs, times, groups, cand):
    """(characters allotted to the segment, duration from its first to last remaining press) per record segment."""
    out = []
    for i0, i1, j0, j1 in groups:
        chars = sum(cand.lens[j0:j1])
        vals = [max(segs[s][0], 0) for s in range(i0, i1)]
        tot = sum(vals)
        for s, v in zip(range(i0, i1), vals):
            rows = segs[s][1]
            share = chars * (v / tot) if tot else chars / (i1 - i0)
            if len(rows) >= 2:
                out.append((max(share, 1.0), times[rows[-1]] - times[rows[0]]))
    return out


def r7_alignments(rel, cands, cfg, end="full"):
    groups, cap = _groups(rel, cfg)
    cats = rel.cats()
    segs = [(v, idx) for v, idx in record_segments(cats)]
    x = [v for v, _ in segs]
    out = []
    for s in range(0, len(cands), 100):
        chunk = cands[s:s + 100]
        out.extend(align_vec.align_many(x, [text_values(c, rel) for c in chunk], LAM, end, groups, cap))
    return segs, out


def a3_r7_costs(rel, cands, model, cfg, end="full"):
    segs, al = r7_alignments(rel, cands, cfg, end)
    times = rel.times()
    out = np.full(len(cands), INF)
    for k, (cost, groups) in enumerate(al):
        if groups is not None:
            out[k] = -sum(model.loglik(c, d) for c, d in r7_segment_pairs(segs, times, groups, cands[k]))
    return out
