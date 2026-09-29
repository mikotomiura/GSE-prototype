#!/usr/bin/env python3
# kit: selftest
"""Level-2 agreement: do the aggregate quantities a writing researcher would actually compute agree
between the ground truth and the observation? Uses only the Python standard library (Bland-Altman,
ICC and the cluster bootstrap are imported from stats.py and are not reimplemented here).

  l2.py --match M.json --sessions S.json --obs OBS --plan PLAN --oracle ORACLE [--config CFG.json] --out OUT.json
  l2.py --selftest      fast default (a few seconds)

Why this level exists: a per-session agreement (level 1) can be high while the remaining errors are
concentrated in one condition, and then every aggregate is biased systematically. This level
computes the aggregates from both sides and compares them.

Text (the unit of aggregation). Inside one block of the plan, in plan order, every consecutive run
of `text_size_trials` trials forms one text; a remainder shorter than that is dropped and its size
is reported. Every trial of a text must have the same speed (the plan builds blocks of one speed),
otherwise the input is rejected: a plan that mixes speeds inside a text is never handled silently.
The stratum of a text is therefore its speed (slow / mid / fast).

Measures, computed per text from both sides (a session is a conversion):
  n_conversions   the number of sessions in the text
  mean_dwell_ms   the mean dwell of the sessions (ground truth: end - start; observation: dwell_ms)
  abandon_rate    the fraction of sessions that were cancelled (ground truth: outcome == "cancel";
                  observation: abandon)
  dwell_fraction  the total dwell divided by the duration of the text (the first trial begin to the
                  last trial end in the oracle log)
A measure that cannot be computed for a text (no session, zero duration) is None, never 0.

Inputs. --match is match.py's output. The kept ground-truth sessions and the kept observation rows
are read from its "matching" section (so the exclusions and the clock correction that were applied
there apply here unchanged). --sessions / --obs / --plan / --oracle are the files that match.py was
run on; their SHA-256 hashes must equal the ones recorded in --match, so a matching result can never
be combined with other data. An observation row is attributed to the trial (in the oracle log) it
overlaps most, exactly as match.py attributes rows to strata; a session or row that belongs to no
trial of any text is counted under "outside_texts" and is not used.

Agreement. The sign of every difference is observation minus ground truth. For each measure:
  bland_altman   bias and limits of agreement of the per-text differences
  icc21          ICC(2,1) (absolute agreement) over the texts, columns = (ground truth, observation)
  icc21_ci       a 95% percentile interval that resamples the blocks (the texts of one block are one
                 cluster); [null, null] when it cannot be computed (fewer than two blocks, or a
                 resample whose ICC is undefined)

Mixture. A synthetic input has no natural mixing ratio, so the primary estimates are per stratum.
"mixtures" in the configuration name weightings of the speeds; for each, the bias of a measure is
the weighted mean of the per-stratum mean differences (weights are normalised, a stratum with weight
zero is not needed, and a needed stratum without data gives null). If a bias moves between
weightings, the error is concentrated in some strata.

Configuration (JSON, every key optional): {"text_size_trials": 8, "B": 2000, "seed": 1,
"mixtures": {"<name>": {"slow": w, "mid": w, "fast": w}}}. Keys starting with "_" are ignored.

The output never includes a path, and identical input always yields identical output bytes.
Exit status: 0 on success; 2 if an input cannot be read or usage is incorrect.
"""
import argparse
import contextlib
import hashlib
import io
import json
import math
import os
import random
import statistics
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import gt_sessions  # noqa: E402  the oracle parser and InputError
import match  # noqa: E402  the interval geometry, trial attribution and file helpers
import stats  # noqa: E402  Bland-Altman, ICC and the cluster bootstrap live there

InputError = gt_sessions.InputError
SPEEDS = match.SPEEDS
MEASURES = ("mean_dwell_ms", "n_conversions", "abandon_rate", "dwell_fraction")
DEFAULT_MIXTURES = {
    "slow_heavy": {"slow": 0.6, "mid": 0.3, "fast": 0.1},
    "uniform": {"slow": 1, "mid": 1, "fast": 1},
    "fast_heavy": {"slow": 0.1, "mid": 0.3, "fast": 0.6},
}


def _is_int(v):
    return type(v) is int


# ---------------------------------------------------------------- texts

def text_layout(plan, oracle, text_size):
    """Bundle the trials of the plan into texts. plan is match.parse_plan_strata's output, oracle is
    gt_sessions.parse_oracle's output. Returns {"texts": [...], "dropped_trials": {block_id: n}}.

    Each text is {"text_id", "block_id", "speed", "trial_ids", "begin_wall_ms", "end_wall_ms",
    "duration_ms"}. Texts follow the plan order inside a block; the blocks are visited in the order
    of their first trial. Raises InputError when a text mixes speeds or a trial of a text is missing
    from the oracle log, and ValueError when text_size is not a positive integer.
    """
    if not _is_int(text_size) or text_size < 1:
        raise ValueError("text_size_trials must be an integer of at least 1")
    windows = dict((t["trial_id"], t) for t in oracle["trials"])
    by_block = {}
    for tid, info in plan["trials"].items():
        by_block.setdefault(info["block_id"], []).append(tid)
    texts, dropped = [], {}
    for block_id, tids in by_block.items():
        n_full = len(tids) // text_size
        dropped[block_id] = len(tids) - n_full * text_size
        for k in range(n_full):
            chunk = tids[k * text_size:(k + 1) * text_size]
            speeds = sorted(set(plan["trials"][t]["speed"] for t in chunk))
            if len(speeds) != 1:
                raise InputError("plan: block %s text %d mixes speeds (%s); a text must have one speed" % (
                    block_id, k, ", ".join(speeds)))
            missing = [t for t in chunk if t not in windows]
            if missing:
                raise InputError("oracle: trial %s of block %s text %d is not in the oracle log" % (
                    missing[0], block_id, k))
            begin = min(windows[t]["begin_wall_ms"] for t in chunk)
            end = max(windows[t]["end_wall_ms"] for t in chunk)
            texts.append({"text_id": "b%s.%d" % (block_id, k), "block_id": block_id, "speed": speeds[0],
                          "trial_ids": chunk, "begin_wall_ms": begin, "end_wall_ms": end,
                          "duration_ms": end - begin})
    return {"texts": texts, "dropped_trials": dropped}


def texts(plan, oracle, text_size):
    """The list of texts of text_layout() (the dropped remainder is reported by text_layout)."""
    return text_layout(plan, oracle, text_size)["texts"]


def attach_trials(obs_rows, oracle, obs_end_offset_ms=0):
    """Copies of the observation rows with a "trial_id" (None when the row overlaps no trial). The
    trial is the one with the greatest overlap, as in match.py's stratum assignment."""
    trials = sorted(oracle["trials"], key=lambda t: (t["begin_wall_ms"], t["end_wall_ms"]))
    begins = [t["begin_wall_ms"] for t in trials]
    out = []
    for i, r in enumerate(obs_rows):
        lo, hi = match.obs_interval(r, obs_end_offset_ms, "obs_rows[%d]" % i)
        out.append(dict(r, trial_id=match._assign_trial(lo, hi, trials, begins)))
    return out


# ---------------------------------------------------------------- aggregation

def aggregate(texts, sessions, obs_rows, side, obs_end_offset_ms=0):
    """The four measures for every text, from one side. side is "gt" (sessions are ground-truth
    sessions, obs_rows is ignored) or "obs" (obs_rows are observation rows carrying a "trial_id",
    see attach_trials; sessions is ignored). Returns {"texts": [...], "n_outside_texts": n}, the
    texts in the order given, each {"text_id", "block_id", "speed", "duration_ms", <MEASURES>}.
    A record whose trial belongs to no text is counted in n_outside_texts and not used.
    obs_end_offset_ms is accepted for symmetry with the pipeline and does not change the measures
    (the dwell of an observation is its dwell_ms)."""
    if side == "gt":
        records = list(sessions)
    elif side == "obs":
        records = list(obs_rows)
    else:
        raise ValueError('side must be "gt" or "obs"')
    index = {}
    for i, t in enumerate(texts):
        for tid in t["trial_ids"]:
            index[tid] = i
    dwells = [[] for _ in texts]
    cancels = [0] * len(texts)
    outside = 0
    for n, r in enumerate(records):
        i = index.get(r.get("trial_id"))
        if i is None:
            outside += 1
            continue
        if side == "gt":
            lo, hi = match.gt_interval(r, "sessions[%d]" % n)
            dwell, cancelled = hi - lo, r.get("outcome") == "cancel"
            if r.get("outcome") not in ("commit", "cancel"):
                raise ValueError("sessions[%d]: outcome must be commit or cancel here" % n)
        else:
            dwell, cancelled = r.get("dwell_ms"), r.get("abandon")
            if not _is_int(dwell) or dwell < 0 or type(cancelled) is not bool:
                raise ValueError("obs_rows[%d]: dwell_ms / abandon has the wrong type" % n)
        dwells[i].append(dwell)
        cancels[i] += 1 if cancelled else 0
    out = []
    for i, t in enumerate(texts):
        n = len(dwells[i])
        total = sum(dwells[i])
        out.append({
            "text_id": t["text_id"], "block_id": t["block_id"], "speed": t["speed"],
            "duration_ms": t["duration_ms"],
            "n_conversions": n,
            "mean_dwell_ms": total / n if n else None,
            "abandon_rate": cancels[i] / n if n else None,
            "dwell_fraction": total / t["duration_ms"] if t["duration_ms"] > 0 else None,
        })
    return {"texts": out, "n_outside_texts": outside}


def _check_aligned(gt_agg, obs_agg):
    g = [t["text_id"] for t in gt_agg["texts"]]
    o = [t["text_id"] for t in obs_agg["texts"]]
    if g != o:
        raise ValueError("the ground-truth and observation aggregates are not over the same texts")


# ---------------------------------------------------------------- agreement

def _icc_interval(rows, B, seed):
    """A block-level bootstrap interval for ICC(2,1); (None, None) when it cannot be computed."""
    blocks = {}
    for block_id, g, o in rows:
        blocks.setdefault(block_id, []).append((g, o))
    clusters = [blocks[b] for b in sorted(blocks)]

    def stat(sample):
        matrix = [[g, o] for c in sample for (g, o) in c]
        if len(matrix) < 2:
            return None
        return stats.icc(matrix, "2,1")

    try:
        return stats.cluster_bootstrap(clusters, stat, B, seed)
    except ValueError:  # a resample with an undefined ICC: the interval is not computable
        return (None, None)


def agreement(gt_agg, obs_agg, B, seed):
    """{measure: {"n", "bland_altman", "icc21", "icc21_ci"}} over the texts where both sides have
    the measure. The difference is observation minus ground truth. icc21 is None when it cannot be
    computed (fewer than two texts, or no variation at all)."""
    if not _is_int(B) or B < 1:
        raise ValueError("B must be an integer of at least 1")
    if not _is_int(seed):
        raise ValueError("seed must be an integer")
    _check_aligned(gt_agg, obs_agg)
    out = {}
    for m in MEASURES:
        rows = [(g["block_id"], g[m], o[m]) for g, o in zip(gt_agg["texts"], obs_agg["texts"])
                if g[m] is not None and o[m] is not None]
        ba = stats.bland_altman([o for _b, _g, o in rows], [g for _b, g, _o in rows])
        value, ci = None, (None, None)
        if len(rows) >= 2:
            value = stats.icc([[g, o] for _b, g, o in rows], "2,1")
            if value is not None:
                ci = _icc_interval(rows, B, seed)
        out[m] = {"n": len(rows), "bland_altman": ba, "icc21": value, "icc21_ci": [ci[0], ci[1]]}
    return out


# ---------------------------------------------------------------- mixtures

def stratify(gt_agg, obs_agg):
    """{speed: [{"text_id", "gt": {measure: v}, "obs": {measure: v}}]} for the speeds that have texts."""
    _check_aligned(gt_agg, obs_agg)
    out = {}
    for g, o in zip(gt_agg["texts"], obs_agg["texts"]):
        out.setdefault(g["speed"], []).append({
            "text_id": g["text_id"],
            "gt": dict((m, g[m]) for m in MEASURES),
            "obs": dict((m, o[m]) for m in MEASURES)})
    return out


def _norm_weights(w, name):
    if not isinstance(w, dict) or not w:
        raise ValueError("mixture %s: the weights must be a non-empty object" % name)
    for k, v in w.items():
        if k not in SPEEDS:
            raise ValueError("mixture %s: unknown stratum %r (expected %s)" % (name, k, ", ".join(SPEEDS)))
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0:
            raise ValueError("mixture %s: a weight must be a finite non-negative number" % name)
    total = sum(w.get(s, 0) for s in SPEEDS)
    if total <= 0:
        raise ValueError("mixture %s: the weights sum to zero" % name)
    return dict((s, w.get(s, 0) / total) for s in SPEEDS)


def mixture_bias(texts_by_stratum, mixtures):
    """The bias (observation minus ground truth) of every measure under each weighting of the strata.

    texts_by_stratum is stratify()'s output; mixtures is {name: {stratum: weight}}. Returns
    {"by_stratum": {speed: {measure: {"bias", "n"}}}, "mixtures": {name: {"weights", "bias":
    {measure: value}}}}. A stratum's bias is the mean per-text difference over the texts where both
    sides have the measure. A mixture's bias is the normalised-weight sum of the strata biases; it is
    None when a stratum with positive weight has no data for the measure."""
    for s in texts_by_stratum:
        if s not in SPEEDS:
            raise ValueError("unknown stratum %r" % (s,))
    by_stratum = {}
    for s in SPEEDS:
        if s not in texts_by_stratum:
            continue
        by_stratum[s] = {}
        for m in MEASURES:
            diffs = [t["obs"][m] - t["gt"][m] for t in texts_by_stratum[s]
                     if t["obs"][m] is not None and t["gt"][m] is not None]
            by_stratum[s][m] = {"bias": statistics.fmean(diffs) if diffs else None, "n": len(diffs)}
    out = {}
    for name in sorted(mixtures):
        w = _norm_weights(mixtures[name], name)
        bias = {}
        for m in MEASURES:
            total, ok = 0.0, True
            for s in SPEEDS:
                if w[s] == 0:
                    continue
                b = by_stratum.get(s, {}).get(m, {}).get("bias")
                if b is None:
                    ok = False
                    break
                total += w[s] * b
            bias[m] = total if ok else None
        out[name] = {"weights": w, "bias": bias}
    return {"by_stratum": by_stratum, "mixtures": out}


# ---------------------------------------------------------------- pipeline

def parse_config(data):
    """Parse the configuration JSON (defaults if None) into {"text_size_trials", "B", "seed", "mixtures"}."""
    cfg = {"text_size_trials": 8, "B": 2000, "seed": 1, "mixtures": dict(DEFAULT_MIXTURES)}
    if data is None:
        return cfg
    obj = match._json_loads(match._decode(data, "config"), "config", True)
    if not isinstance(obj, dict):
        raise InputError("config: the top level must be an object")
    for k, v in obj.items():
        if k.startswith("_"):
            continue
        if k in ("text_size_trials", "B"):
            if not _is_int(v) or v < 1:
                raise InputError("config: %s must be an integer of at least 1" % k)
            cfg[k] = v
        elif k == "seed":
            if not _is_int(v):
                raise InputError("config: seed must be an integer")
            cfg[k] = v
        elif k == "mixtures":
            if not isinstance(v, dict) or not v:
                raise InputError("config: mixtures must be a non-empty object")
            for name, w in v.items():
                try:
                    _norm_weights(w, name)
                except ValueError as e:
                    raise InputError("config: %s" % e)
            cfg[k] = v
        else:
            raise InputError("config: unknown key '%s'" % k)
    return cfg


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def evaluate(match_bytes, sessions_bytes, obs_bytes, plan_bytes, oracle_bytes, config_bytes=None):
    """The CLI's core logic (bytes in, an output dict out). Identical input always yields an
    identical dict."""
    cfg = parse_config(config_bytes)
    mo = match._json_loads(match._decode(match_bytes, "match"), "match", True)
    need = isinstance(mo, dict) and isinstance(mo.get("matching"), dict) and isinstance(mo.get("inputs_sha256"), dict) \
        and isinstance(mo.get("config"), dict) and _is_int(mo["config"].get("obs_end_offset_ms")) \
        and all(isinstance(mo["matching"].get(k), list) for k in ("pairs", "split", "merge", "miss", "false_pos"))
    if not need:
        raise InputError("match: not match.py's output (missing matching / inputs_sha256 / config)")
    for name, data in (("sessions", sessions_bytes), ("obs", obs_bytes), ("plan", plan_bytes), ("oracle", oracle_bytes)):
        if mo["inputs_sha256"].get(name) != _sha(data):
            raise InputError("%s: SHA-256 does not match the one recorded in the match result (another data set)" % name)
    plan = match.parse_plan_strata(plan_bytes)
    oracle = gt_sessions.parse_oracle(oracle_bytes)
    want = oracle["plan_sha256"]
    if not isinstance(want, str) or want.lower() != plan["sha256"]:
        raise InputError("plan: SHA-256 does not match the oracle header's plan_sha256 (unrelated plan)")

    m = mo["matching"]
    gt = [p["gt"] for p in m["pairs"]] + [p["gt"] for p in m["split"]] + \
        [g for p in m["merge"] for g in p["gt"]] + list(m["miss"])
    obs = [p["obs"] for p in m["pairs"]] + [o for p in m["split"] for o in p["obs"]] + \
        [p["obs"] for p in m["merge"]] + list(m["false_pos"])
    off = mo["config"]["obs_end_offset_ms"]
    obs = attach_trials(obs, oracle, off)

    layout = text_layout(plan, oracle, cfg["text_size_trials"])
    tx = layout["texts"]
    gt_agg = aggregate(tx, gt, None, "gt")
    obs_agg = aggregate(tx, None, obs, "obs")
    by_speed = {}
    for t in tx:
        by_speed[t["speed"]] = by_speed.get(t["speed"], 0) + 1
    return {
        "definition": mo.get("definition"),
        "config": {"text_size_trials": cfg["text_size_trials"], "B": cfg["B"], "seed": cfg["seed"],
                   "mixtures": cfg["mixtures"], "obs_end_offset_ms": off},
        "inputs_sha256": {"match": _sha(match_bytes), "sessions": _sha(sessions_bytes), "obs": _sha(obs_bytes),
                          "plan": plan["sha256"], "oracle": _sha(oracle_bytes),
                          "config": None if config_bytes is None else _sha(config_bytes)},
        "texts": {"n": len(tx), "n_by_speed": dict((s, by_speed[s]) for s in SPEEDS if s in by_speed),
                  "dropped_trials_by_block": dict((str(b), n) for b, n in layout["dropped_trials"].items())},
        "outside_texts": {"gt": gt_agg["n_outside_texts"], "obs": obs_agg["n_outside_texts"]},
        "aggregate": {"gt": gt_agg["texts"], "obs": obs_agg["texts"]},
        "agreement": agreement(gt_agg, obs_agg, cfg["B"], cfg["seed"]),
        "mixture_bias": mixture_bias(stratify(gt_agg, obs_agg), cfg["mixtures"]),
        "note": "a synthetic input has no natural mixing proportion; read the per-stratum biases as the "
                "primary estimates and each mixture as a sensitivity check of the aggregate bias",
    }


def render(out):
    """Render the output bytes (LF line endings, UTF-8, no BOM, keys in a fixed sorted order)."""
    return match.render(out)


# ---------------------------------------------------------------- selftest

T0 = 1700000000000
BASE_DWELL = {"slow": 1400, "mid": 1000, "fast": 700}


def _world(n_blocks=6, per_block=32):
    """A synthetic plan, oracle windows and ground-truth sessions. Blocks alternate slow / mid / fast;
    the number of sessions per trial, the dwell and the cancel pattern vary from text to text (a
    text is 8 consecutive trials), so that every measure has real variation between texts."""
    plan_trials, windows, gt = {}, [], []
    idx = 0
    for b in range(n_blocks):
        sp = SPEEDS[b % 3]
        for k in range(per_block):
            tid = "t%05d" % (idx + 1)
            plan_trials[tid] = {"block_id": b, "scenario": "S%d" % (k % 3 + 1), "speed": sp}
            begin = T0 + idx * 20000
            windows.append({"trial_id": tid, "begin_wall_ms": begin, "end_wall_ms": begin + 12000})
            text_no = idx // 8
            extra = (text_no * 5) % 8
            for j in range(2 if (idx % 8) < extra else 1):
                d = BASE_DWELL[sp] + 30 * (text_no % 4) + (idx * 37) % 200 + 25 * j
                lo = begin + 500 + j * 5000
                cancel = (idx * 11 + j) % (3 + text_no % 5) == 0
                gt.append(match._gt(tid, lo, lo + d, outcome="cancel" if cancel else "commit"))
            idx += 1
    return {"plan": {"trials": plan_trials}, "oracle": {"trials": windows}, "gt": gt}


def _obs_from(gt, dwell_delta=None, keep=None):
    """Observation rows for the ground-truth sessions (each row ends where its session ends)."""
    rows = []
    for i, s in enumerate(gt):
        if keep is not None and not keep(i, s):
            continue
        d = s["end_wall_ms"] - s["start_wall_ms"] + (dwell_delta(i, s) if dwell_delta else 0)
        rows.append(match._ob(s["end_wall_ms"] - d, s["end_wall_ms"], abandon=(s["outcome"] == "cancel")))
    return rows


def _aggs(w, obs, size=8):
    tx = texts(w["plan"], w["oracle"], size)
    return tx, aggregate(tx, w["gt"], None, "gt"), aggregate(tx, None, attach_trials(obs, w["oracle"]), "obs")


def _permuted(agg, seed):
    """The same aggregate with the per-text values permuted among the texts (ids stay in place)."""
    rng = random.Random(seed)
    order = list(range(len(agg["texts"])))
    for i in range(len(order) - 1, 0, -1):
        j = int(rng.random() * (i + 1))
        order[i], order[j] = order[j], order[i]
    keep = ("text_id", "block_id", "speed", "duration_ms")
    out = []
    for i, t in enumerate(agg["texts"]):
        src = agg["texts"][order[i]]
        row = dict((k, t[k]) for k in keep)
        row.update((m, src[m]) for m in MEASURES)
        out.append(row)
    return {"texts": out, "n_outside_texts": agg["n_outside_texts"]}


def _case_layout():
    f = []
    plan_trials, windows = {}, []
    for b in range(3):
        for k in range(20):
            tid = "t%05d" % (b * 20 + k + 1)
            plan_trials[tid] = {"block_id": b, "scenario": "S1", "speed": SPEEDS[b]}
            windows.append({"trial_id": tid, "begin_wall_ms": T0 + (b * 20 + k) * 1000, "end_wall_ms": T0 + (b * 20 + k) * 1000 + 800})
    plan, oracle = {"trials": plan_trials}, {"trials": windows}
    lay = text_layout(plan, oracle, 8)
    tx = lay["texts"]
    if len(tx) != 6 or lay["dropped_trials"] != {0: 4, 1: 4, 2: 4}:
        f.append("20 trials per block at size 8 should give 2 texts per block and 4 dropped trials per block: %d texts, %r" % (
            len(tx), lay["dropped_trials"]))
    else:
        if tx[1]["trial_ids"] != ["t%05d" % k for k in range(9, 17)]:
            f.append("the second text of block 0 is not trials 9..16 in plan order: %r" % tx[1]["trial_ids"])
        used = set(t for x in tx for t in x["trial_ids"])
        if "t00017" in used or "t00020" in used:
            f.append("the dropped remainder (trials 17..20 of block 0) is inside a text")
        if [x["speed"] for x in tx] != ["slow", "slow", "mid", "mid", "fast", "fast"]:
            f.append("a text does not carry its block's speed: %r" % [x["speed"] for x in tx])
        if tx[0]["begin_wall_ms"] != T0 or tx[0]["end_wall_ms"] != T0 + 7000 + 800 or tx[0]["duration_ms"] != 7800:
            f.append("a text's time is not the first trial begin to the last trial end: %r" % tx[0])
    if len(text_layout(plan, oracle, 20)["texts"]) != 3 or len(text_layout(plan, oracle, 21)["texts"]) != 0 or \
            text_layout(plan, oracle, 21)["dropped_trials"] != {0: 20, 1: 20, 2: 20}:
        f.append("a text size equal to the block gives 1 text per block; a larger one gives none and drops all trials")
    # plan order (not id order) and interleaved blocks are respected
    shuffled = {}
    for tid in sorted(plan_trials, reverse=True):
        shuffled[tid] = plan_trials[tid]
    lay2 = text_layout({"trials": shuffled}, oracle, 8)
    if lay2["texts"][0]["trial_ids"][0] != "t00060" or lay2["texts"][0]["block_id"] != 2:
        f.append("texts do not follow the plan order: %r" % lay2["texts"][0])
    # sessions and rows in dropped trials are not counted (and are reported as outside the texts)
    gt = [match._gt("t00001", T0 + 100, T0 + 500), match._gt("t00018", T0 + 17000 + 100, T0 + 17000 + 500)]
    agg = aggregate(tx, gt, None, "gt")
    if agg["n_outside_texts"] != 1 or agg["texts"][0]["n_conversions"] != 1 or sum(t["n_conversions"] for t in agg["texts"]) != 1:
        f.append("a session in a dropped trial is counted: %r" % agg["n_outside_texts"])
    if agg["texts"][1]["mean_dwell_ms"] is not None or agg["texts"][1]["abandon_rate"] is not None or \
            agg["texts"][1]["n_conversions"] != 0:
        f.append("a text without sessions must have n_conversions 0 and the other measures None")
    # errors, not silent handling
    mixed = dict((t, dict(i)) for t, i in plan_trials.items())
    mixed["t00003"]["speed"] = "fast"
    for name, fn in (("a text with mixed speeds", lambda: text_layout({"trials": mixed}, oracle, 8)),
                     ("a trial missing from the oracle", lambda: text_layout(plan, {"trials": windows[1:]}, 8))):
        try:
            fn()
            f.append("%s was accepted" % name)
        except InputError:
            pass
    for bad in (0, -1, 1.5, True, "8"):
        try:
            text_layout(plan, oracle, bad)
            f.append("text size %r was accepted" % (bad,))
        except ValueError:
            pass
    return f


def _case_definitions():
    f = []
    plan = {"trials": dict(("t%05d" % (k + 1), {"block_id": 0, "scenario": "S1", "speed": "slow"}) for k in range(4))}
    oracle = {"trials": [{"trial_id": "t%05d" % (k + 1), "begin_wall_ms": T0 + k * 10000, "end_wall_ms": T0 + k * 10000 + 5000} for k in range(4)]}
    tx = texts(plan, oracle, 4)
    gt = [match._gt("t00001", T0 + 100, T0 + 1100), match._gt("t00002", T0 + 10100, T0 + 12100, outcome="cancel"),
          match._gt("t00004", T0 + 30100, T0 + 30600)]
    a = aggregate(tx, gt, None, "gt")["texts"][0]
    # dwell 1000, 2000, 500 -> mean 1166.67; 1 of 3 cancelled; text time = 35000 - 0 ms
    if a["n_conversions"] != 3 or abs(a["mean_dwell_ms"] - 3500 / 3) > 1e-9 or abs(a["abandon_rate"] - 1 / 3) > 1e-12 or \
            abs(a["dwell_fraction"] - 3500 / 35000) > 1e-12:
        f.append("the ground-truth measures are wrong: %r" % (a,))
    obs = attach_trials([match._ob(T0 + 100, T0 + 1100), match._ob(T0 + 10100, T0 + 12100, abandon=True),
                         match._ob(T0 + 30100, T0 + 30600), match._ob(T0 - 9000, T0 - 8000)], oracle)
    ob = aggregate(tx, None, obs, "obs")
    if ob["n_outside_texts"] != 1 or ob["texts"][0]["n_conversions"] != 3 or \
            abs(ob["texts"][0]["abandon_rate"] - 1 / 3) > 1e-12 or abs(ob["texts"][0]["mean_dwell_ms"] - 3500 / 3) > 1e-9:
        f.append("the observation measures (or the attribution to trials) are wrong: %r" % (ob,))
    # a text of zero duration cannot give a time fraction
    z = aggregate([{"text_id": "z", "block_id": 0, "speed": "slow", "trial_ids": ["t00001"], "duration_ms": 0}], gt, None, "gt")
    if z["texts"][0]["dwell_fraction"] is not None:
        f.append("a zero-duration text must give dwell_fraction None")
    for name, fn in (("an unknown side", lambda: aggregate(tx, gt, None, "both")),
                     ("an open ground-truth session", lambda: aggregate(tx, [match._gt("t00001", T0, None, outcome="open_at_end")], None, "gt")),
                     ("a non-integer dwell", lambda: aggregate(tx, None, [{"trial_id": "t00001", "dwell_ms": 1.5, "abandon": False}], "obs"))):
        try:
            fn()
            f.append("%s was accepted" % name)
        except ValueError:
            pass
    return f


def _case_recovery():
    """A dwell bias of about +50 ms appears in the mean conversion time and nowhere else."""
    f = []
    w = _world()
    jitter = lambda i, s: 50 + ((i * 13) % 5 - 2) * 10
    _tx, g, o = _aggs(w, _obs_from(w["gt"], dwell_delta=jitter))
    ag = agreement(g, o, 200, 1)
    ba = ag["mean_dwell_ms"]["bland_altman"]
    if not (40 < ba["bias"] < 60 and ba["loa_lo"] <= 50 <= ba["loa_hi"]):
        f.append("the dwell bias of +50 ms is not recovered by the mean conversion time: %r" % (ba,))
    for m in ("n_conversions", "abandon_rate"):
        b = ag[m]["bland_altman"]
        if b["bias"] != 0 or b["sd"] != 0:
            f.append("the dwell bias leaks into %s: %r" % (m, b))
    if not (0.0 < ag["dwell_fraction"]["bland_altman"]["bias"] < 0.2):
        f.append("the dwell bias does not raise the time fraction: %r" % (ag["dwell_fraction"]["bland_altman"],))
    # the sign is observation minus ground truth: a negative bias flips it
    _tx, g2, o2 = _aggs(w, _obs_from(w["gt"], dwell_delta=lambda i, s: -50))
    if abs(agreement(g2, o2, 50, 1)["mean_dwell_ms"]["bland_altman"]["bias"] + 50) > 1e-9:
        f.append("a dwell of 50 ms too short does not give a bias of -50 (the sign is observation minus ground truth)")
    if ag["mean_dwell_ms"]["n"] != 24:
        f.append("the recovery world should have 24 texts: %d" % ag["mean_dwell_ms"]["n"])
    return f


def _case_perfect_and_shuffle():
    """Perfect agreement gives ICC(2,1) = 1; shuffling the observations among the texts drops it."""
    f = []
    w = _world()
    _tx, g, o = _aggs(w, _obs_from(w["gt"]))
    ag = agreement(g, o, 200, 1)
    for m in MEASURES:
        v = ag[m]["icc21"]
        if v is None or abs(v - 1.0) > 1e-9:
            f.append("perfect agreement does not give ICC(2,1) = 1 for %s: %r" % (m, v))
        b = ag[m]["bland_altman"]
        if b["bias"] != 0 or b["sd"] != 0:
            f.append("perfect agreement does not give a zero Bland-Altman bias and sd for %s: %r" % (m, b))
    lo, hi = ag["mean_dwell_ms"]["icc21_ci"]
    if lo is None or not (lo <= 1.0 + 1e-9 and hi >= 1.0 - 1e-9):
        f.append("the ICC interval does not contain the ICC under perfect agreement: %r" % (ag["mean_dwell_ms"]["icc21_ci"],))
    # negative control: values permuted among the texts. A single permutation can land on either side
    # of 0 by chance (24 texts), so many seeds are drawn: the ICC must average about 0 and never
    # approach 1.
    vals = []
    for seed in range(1, 21):
        sh = agreement(g, _permuted(o, seed), 10, 1)
        for m in MEASURES:
            if sh[m]["icc21"] is None:
                f.append("the shuffled ICC of %s is undefined" % m)
            else:
                vals.append(sh[m]["icc21"])
    if vals and (max(vals) > 0.6 or abs(sum(vals) / len(vals)) > 0.15):
        f.append("shuffling the observations among texts leaves the ICC far from 0 (largest %.3f, mean %.3f)" % (
            max(vals), sum(vals) / len(vals)))
    return f


def _case_mixture():
    """Misses confined to the fast stratum make the aggregate bias larger under a fast-heavy mixture."""
    f = []
    w = _world()
    fast_tids = set(t for t, i in w["plan"]["trials"].items() if i["speed"] == "fast")
    keep = lambda i, s: not (s["trial_id"] in fast_tids and i % 2 == 0)
    _tx, g, o = _aggs(w, _obs_from(w["gt"], keep=keep))
    mb = mixture_bias(stratify(g, o), DEFAULT_MIXTURES)
    st = mb["by_stratum"]
    b = dict((s, st[s]["n_conversions"]["bias"]) for s in SPEEDS)
    if b["slow"] != 0 or b["mid"] != 0 or not b["fast"] < -3:
        f.append("the misses are not confined to the fast stratum (per-stratum n_conversions bias): %r" % (b,))
    got = dict((n, mb["mixtures"][n]["bias"]["n_conversions"]) for n in DEFAULT_MIXTURES)
    if not (abs(got["fast_heavy"]) > abs(got["uniform"]) > abs(got["slow_heavy"]) > 0):
        f.append("the bias does not grow from slow-heavy to uniform to fast-heavy: %r" % (got,))
    for name, wt in (("fast_heavy", 0.6), ("uniform", 1 / 3), ("slow_heavy", 0.1)):
        if abs(got[name] - wt * b["fast"]) > 1e-9:
            f.append("%s is not the weighted mean of the strata biases: %r vs %r" % (name, got[name], wt * b["fast"]))
    # the same texts without misses: no mixture moves the bias
    _tx2, g2, o2 = _aggs(w, _obs_from(w["gt"]))
    clean = mixture_bias(stratify(g2, o2), DEFAULT_MIXTURES)
    if any(clean["mixtures"][n]["bias"]["n_conversions"] != 0 for n in DEFAULT_MIXTURES):
        f.append("a mixture moved the bias although the observation is exact")
    # weights are normalised; zero-weight strata are not needed; a needed empty stratum gives None
    half = mixture_bias(stratify(g, o), {"x": {"fast": 3}, "y": {"fast": 1, "slow": 0}})
    if half["mixtures"]["x"]["weights"] != {"slow": 0.0, "mid": 0.0, "fast": 1.0} or \
            half["mixtures"]["x"]["bias"] != half["mixtures"]["y"]["bias"]:
        f.append("weights are not normalised / a zero weight changes the result")
    only_slow = mixture_bias({"slow": stratify(g, o)["slow"]}, {"fast_only": {"fast": 1}, "slow_only": {"slow": 1}})
    if only_slow["mixtures"]["fast_only"]["bias"]["n_conversions"] is not None or \
            only_slow["mixtures"]["slow_only"]["bias"]["n_conversions"] != 0:
        f.append("a needed stratum without data must give None (and an available one a value)")
    for name, fn in (("a negative weight", lambda: mixture_bias({}, {"a": {"slow": -1, "fast": 2}})),
                     ("all-zero weights", lambda: mixture_bias({}, {"a": {"slow": 0}})),
                     ("an unknown stratum in the weights", lambda: mixture_bias({}, {"a": {"medium": 1}})),
                     ("an unknown stratum in the texts", lambda: mixture_bias({"medium": []}, {"a": {"slow": 1}})),
                     ("a boolean weight", lambda: mixture_bias({}, {"a": {"slow": True}}))):
        try:
            fn()
            f.append("%s was accepted" % name)
        except ValueError:
            pass
    return f


def _case_seed_and_bytes():
    f = []
    w = _world()
    jitter = lambda i, s: 50 + ((i * 13) % 5 - 2) * 10
    _tx, g, o = _aggs(w, _obs_from(w["gt"], dwell_delta=jitter, keep=lambda i, s: i % 9 != 0))
    state = random.getstate()
    a = agreement(g, o, 300, 7)
    b = agreement(g, o, 300, 7)
    c = agreement(g, o, 300, 8)
    if random.getstate() != state:
        f.append("the global random state was touched")
    ja, jb = json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True)
    if ja != jb:
        f.append("the same seed does not give byte-identical output")
    if a == c:
        f.append("a different seed gives the same intervals (the seed has no effect)")
    if any(a[m]["icc21_ci"][0] is None for m in MEASURES):
        f.append("an ICC interval is missing in a well-behaved world: %r" % ([a[m]["icc21_ci"] for m in MEASURES],))
    # the intervals bracket the point estimate loosely and are ordered
    for m in MEASURES:
        lo, hi = a[m]["icc21_ci"]
        if lo is not None and not lo <= hi:
            f.append("the ICC interval of %s is not ordered" % m)
    # not computable cases are None, never 0
    one_block = _world(n_blocks=1, per_block=32)
    _t, g1, o1 = _aggs(one_block, _obs_from(one_block["gt"], dwell_delta=jitter))
    r = agreement(g1, o1, 50, 1)["mean_dwell_ms"]
    if r["icc21"] is None or r["icc21_ci"] != [None, None]:
        f.append("one block gives an ICC but no block-level interval: %r" % (r,))
    single = _world(n_blocks=1, per_block=8)
    _t, g3, o3 = _aggs(single, _obs_from(single["gt"]))
    s = agreement(g3, o3, 50, 1)["mean_dwell_ms"]
    if s["icc21"] is not None or s["icc21_ci"] != [None, None] or s["bland_altman"]["sd"] is not None:
        f.append("a single text must give no ICC, no interval and no limits of agreement: %r" % (s,))
    for bad in (dict(B=0, seed=1), dict(B=10, seed="a"), dict(B=True, seed=1)):
        try:
            agreement(g, o, **bad)
            f.append("agreement accepted %r" % (bad,))
        except ValueError:
            pass
    try:
        agreement(g, _permuted_ids(o), 10, 1)
        f.append("aggregates over different texts were compared")
    except ValueError:
        pass
    return f


def _permuted_ids(agg):
    texts_ = [dict(t) for t in agg["texts"]]
    texts_[0]["text_id"], texts_[1]["text_id"] = texts_[1]["text_id"], texts_[0]["text_id"]
    return {"texts": texts_, "n_outside_texts": agg["n_outside_texts"]}


def _jl(rows):
    return match._jl(rows)


def _case_cli():
    f = []
    fx = match._cli_fixture()
    mbytes = match.render(match.evaluate(fx["sessions"], "all", fx["obs"], fx["plan"], fx["oracle"], fx["config"]))
    cfg = json.dumps({"B": 100, "seed": 3}).encode("utf-8")
    out = evaluate(mbytes, fx["sessions"], fx["obs"], fx["plan"], fx["oracle"], cfg)
    if out["texts"] != {"n": 9, "n_by_speed": {"slow": 3, "mid": 3, "fast": 3},
                        "dropped_trials_by_block": {"0": 6, "1": 6, "2": 6}}:
        f.append("the text counts or the dropped trials are wrong: %r" % (out["texts"],))
    if out["outside_texts"]["obs"] < 1 or out["outside_texts"]["gt"] < 1:
        f.append("records in dropped trials / outside every trial are not reported: %r" % (out["outside_texts"],))
    if any(t["n_conversions"] < 1 for t in out["aggregate"]["gt"]):
        f.append("a text of the fixture has no ground-truth sessions")
    if out["agreement"]["n_conversions"]["n"] != 9 or out["definition"] != "all":
        f.append("the agreement is not over the 9 texts")
    if set(out["mixture_bias"]["mixtures"]) != set(DEFAULT_MIXTURES):
        f.append("the default mixtures are not reported")
    with tempfile.TemporaryDirectory() as d:
        paths = {}
        for k, data in (("match", mbytes), ("sessions", fx["sessions"]), ("obs", fx["obs"]), ("plan", fx["plan"]),
                        ("oracle", fx["oracle"]), ("config", cfg)):
            paths[k] = os.path.join(d, k + ".dat")
            with open(paths[k], "wb") as fh:
                fh.write(data)

        def run(out_name, **over):
            a = dict(match=paths["match"], sessions=paths["sessions"], obs=paths["obs"], plan=paths["plan"],
                     oracle=paths["oracle"], config=paths["config"], out=os.path.join(d, out_name))
            a.update(over)
            argv = []
            for k, v in a.items():
                if v is not None:
                    argv += ["--" + k, v]
            buf, err = io.StringIO(), io.StringIO()
            try:
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                    rc = main(argv)
            except SystemExit as e:
                rc = e.code
            return rc, err.getvalue()

        rc1, _ = run("o1.json")
        rc2, _ = run("o2.json")
        if rc1 != 0 or rc2 != 0:
            f.append("the CLI does not exit 0: %r %r" % (rc1, rc2))
        else:
            b1, b2 = open(os.path.join(d, "o1.json"), "rb").read(), open(os.path.join(d, "o2.json"), "rb").read()
            if b1 != b2 or b1 != render(out):
                f.append("the CLI's output is not byte-identical across two runs, or differs from evaluate's")
            if b"\r" in b1 or b1.startswith(b"\xef\xbb\xbf") or d.encode("utf-8") in b1:
                f.append("the output contains a CR, a BOM, or an input path")
            sub = subprocess.run([sys.executable, os.path.abspath(__file__), "--match", paths["match"],
                                  "--sessions", paths["sessions"], "--obs", paths["obs"], "--plan", paths["plan"],
                                  "--oracle", paths["oracle"], "--config", paths["config"],
                                  "--out", os.path.join(d, "o3.json")], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if sub.returncode != 0 or open(os.path.join(d, "o3.json"), "rb").read() != b1:
                f.append("the CLI run as a subprocess does not exit 0, or is not byte-identical: %r" % sub.stderr[-200:])

        def rc_of(name, want, **over):
            rc, err = run(name, **over)
            if rc != want or "Traceback" in err:
                f.append("%s: exit %r (expected %d) %s" % (name, rc, want, err[-120:]))

        # a result cannot be combined with other data: every input is bound by its hash
        for key in ("sessions", "obs", "plan", "oracle"):
            tampered = os.path.join(d, "t_" + key + ".dat")
            with open(tampered, "wb") as fh:
                fh.write(open(paths[key], "rb").read() + b"\n")
            rc_of("h_%s.json" % key, 2, **{key: tampered})
        rc_of("e1.json", 2, out=paths["obs"])
        rc_of("e2.json", 2, match=os.path.join(d, "no-such-file"))
        rc_of("e3.json", 2, match=paths["sessions"])
        bad_cfg = os.path.join(d, "bad_cfg.json")
        for body in ({"text_size": 8}, {"text_size_trials": 0}, {"B": 0}, {"seed": 1.5}, {"mixtures": {}},
                     {"mixtures": {"a": {"medium": 1}}}, {"mixtures": {"a": {"slow": 0}}}):
            with open(bad_cfg, "wb") as fh:
                fh.write(json.dumps(body).encode("utf-8"))
            rc_of("c.json", 2, config=bad_cfg)
        # a configuration that changes the text size changes the texts
        big = os.path.join(d, "big.json")
        with open(big, "wb") as fh:
            fh.write(json.dumps({"B": 50, "text_size_trials": 15}).encode("utf-8"))
        rc_of("big_out.json", 0, config=big)
        if os.path.exists(os.path.join(d, "big_out.json")):
            o = json.loads(open(os.path.join(d, "big_out.json"), "rb").read().decode("utf-8"))
            if o["texts"]["n"] != 6 or o["texts"]["dropped_trials_by_block"] != {"0": 0, "1": 0, "2": 0}:
                f.append("text_size_trials in the configuration does not change the texts: %r" % (o["texts"],))
        rc_of("no_cfg.json", 0, config=None)
    return f


CASES = [
    ("texts (bundling in plan order, dropped remainder counted, one speed per text, errors)", _case_layout),
    ("measure definitions (both sides, attribution to trials, None when not computable)", _case_definitions),
    ("recovery: a dwell bias appears in the mean conversion time only", _case_recovery),
    ("perfect agreement gives ICC 1; shuffling lowers the ICC (negative control)", _case_perfect_and_shuffle),
    ("positive control: the bias moves with the mixture ratio", _case_mixture),
    ("same seed gives byte-identical results; not computable cases are None", _case_seed_and_bytes),
    ("CLI (hash binding, byte-identical output, exit 2)", _case_cli),
]


def selftest():
    bad = 0
    for name, fn in CASES:
        try:
            fails = fn()
        except Exception as e:  # an unexpected exception counts as a failure
            fails = ["exception %s: %s" % (type(e).__name__, e)]
        if fails:
            bad += 1
            print("  ❌ " + name)
            for m in fails:
                print("     FAIL " + m)
        else:
            print("  ✅ " + name)
    if bad:
        print("selftest failed %d / %d" % (bad, len(CASES)))
        return 1
    print("selftest OK (%d cases)" % len(CASES))
    return 0


# ---------------------------------------------------------------- CLI

def main(argv):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Level-2 agreement of text-level aggregates (ground truth against observation)")
    ap.add_argument("--match")
    ap.add_argument("--sessions")
    ap.add_argument("--obs")
    ap.add_argument("--plan")
    ap.add_argument("--oracle")
    ap.add_argument("--config")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not (args.match and args.sessions and args.obs and args.plan and args.oracle and args.out):
        ap.error("--match / --sessions / --obs / --plan / --oracle / --out are required (--config is optional)")
    for inp in (args.match, args.sessions, args.obs, args.plan, args.oracle, args.config):
        if inp and match._same_file(inp, args.out):
            print("l2: --out names the same file as an input (%s)" % inp, file=sys.stderr)
            return 2
    try:
        out = evaluate(match._read(args.match, "match"), match._read(args.sessions, "sessions"),
                       match._read(args.obs, "obs"), match._read(args.plan, "plan"),
                       match._read(args.oracle, "oracle"),
                       None if args.config is None else match._read(args.config, "config"))
        match._write_atomic(args.out, render(out))
    except (InputError, ValueError) as e:
        print("l2: %s" % e, file=sys.stderr)
        return 2
    except OSError as e:
        print("l2: could not write output (%s)" % type(e).__name__, file=sys.stderr)
        return 2
    print("l2: %d texts (%s); ICC(2,1) mean dwell %s, conversions %s" % (
        out["texts"]["n"], ", ".join("%s %d" % (s, n) for s, n in out["texts"]["n_by_speed"].items()),
        _fmt(out["agreement"]["mean_dwell_ms"]["icc21"]), _fmt(out["agreement"]["n_conversions"]["icc21"])))
    return 0


def _fmt(v):
    return "n/a" if v is None else "%.3f" % v


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
