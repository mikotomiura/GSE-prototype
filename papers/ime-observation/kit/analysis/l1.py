#!/usr/bin/env python3
# kit: selftest
"""Level-1 (L1) agreement measures computed from the 1:1 pairs that match.py produces: the error of
the observed composition duration (dwell_ms), agreement on abandonment, agreement on the number of
navigation key presses, a check of the 20-second cut-off, and a report of how often the executor's
plan disagreed with the ground truth it was compared against. Uses only the Python standard library
(every statistic comes from stats.py and none is reimplemented here).

  l1.py --match M.json --sessions S.json --plan PLAN --oracle ORACLE [--config CFG.json] --out OUT.json
  l1.py --selftest      fast default (a few seconds)

Inputs: M.json is match.py's output (its definition, cell, and input hashes are read from it),
S.json is gt_sessions.py's output (the sessions of that definition, and the oracle agreement), PLAN
and ORACLE are the files those two were built from. The hashes recorded in M.json and the plan hash
recorded in the oracle header must agree with the files given; otherwise the run stops (unrelated
inputs are never combined).

Measures (each is computed per stratum -- (cell, scenario, speed) -- and pooled over all pairs):
  dwell_ms     the error is  observed - ground truth  (a positive bias means the observation is longer);
               ground-truth dwell = end_wall_ms - start_wall_ms. Reported: the median absolute error with
               a cluster-bootstrap interval, and Bland-Altman bias, limits of agreement, and a
               cluster-bootstrap interval for the bias. The resampling unit is the block, because trials
               in one block share the state of the input method and are not independent. A pair whose
               observed dwell_ms is 0 is not a measurement (a clock that moved backwards yields 0), so it
               is left out of every error figure and counted separately (n_zero_excluded).
  abandon      ground truth = the session ended in a cancel; observation = the row's abandon flag.
               Reported: the 2 x 2 table (rows = ground truth, columns = observation, index 1 = abandon),
               Cohen's kappa, and the raw agreement with a Wilson interval.
  nav          exact-match rate with a Wilson interval, and the distribution of the difference
               (observed - true). The true count is the session's nav_true_cand when it is not null
               (sources with a candidate window: presses while the window was open), otherwise nav_true.
  truncation   sessions longer than limit_ms (default 20000) are not expected to produce a row: reports how
               many such sessions exist and how many of them nevertheless appear in a pair, split, or
               merge; also the number of observed rows longer than the limit.
  oracle       the plan-versus-ground-truth disagreements, by type, each with a Wilson interval. These
               sessions are reported, never removed from the evaluation.

Configuration CFG (JSON): {"B": 2000, "seed": 1, "limit_ms": 20000}. Keys starting with "_" are
annotations and are not read.
Written as estimation, not significance testing. A quantity that cannot be computed (no pairs, fewer
than two blocks, zero variance) is null, never 0. Randomness uses only random.Random(seed) (through
stats.cluster_bootstrap), so identical input always yields identical output bytes (sorted keys, LF,
UTF-8, no BOM).

Exit status: 0 on success; 2 if an input cannot be read, is inconsistent, or usage is incorrect.
"""
import argparse
import hashlib
import json
import os
import statistics
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import gt_sessions  # noqa: E402  reuses its oracle parser and InputError
import match  # noqa: E402  reuses its parsers, output writer, and interval helpers
import stats  # noqa: E402  every statistic (Wilson, bootstrap, Bland-Altman, kappa) comes from here

InputError = gt_sessions.InputError
DEFAULT_B = 2000
DEFAULT_SEED = 1
DEFAULT_LIMIT_MS = 20000


# ---------------------------------------------------------------- measures

def _gt_dwell(s):
    return s["end_wall_ms"] - s["start_wall_ms"]


def _block_key(block_of, gt):
    if callable(block_of):
        return block_of(gt)
    return block_of.get(gt.get("trial_id"))


def _ci(iv):
    return [iv[0], iv[1]]


def _clusters(by_block):
    """The per-block lists in a fixed order (a block that is None sorts last)."""
    return [by_block[k] for k in sorted(by_block, key=lambda k: (k is None, str(k)))]


def _flat_mean(cs):
    return statistics.fmean(v for c in cs for v in c)


def _flat_median_abs(cs):
    return statistics.median(abs(v) for c in cs for v in c)


def dwell_error(pairs, block_of, B, seed):
    """The error of the observed dwell_ms against the ground-truth duration, over 1:1 pairs
    ({"gt", "obs", "iou"}). The difference is observed - ground truth.

    block_of: a function taking a ground-truth session and returning its block, or a dict from
    trial_id to block. Pairs are resampled block by block.
    Returns {"n", "n_zero_excluded", "n_blocks", "mae", "mae_ci", "bland_altman", "bias_ci"}. A pair
    whose observed dwell_ms is 0 is excluded from n and from every figure, and counted in
    n_zero_excluded.
    """
    obs, gt, by_block, n_zero = [], [], {}, 0
    for p in pairs:
        o = p["obs"]["dwell_ms"]
        if o == 0:
            n_zero += 1
            continue
        g = _gt_dwell(p["gt"])
        obs.append(o)
        gt.append(g)
        by_block.setdefault(_block_key(block_of, p["gt"]), []).append(o - g)
    clusters = _clusters(by_block)
    return {
        "n": len(obs),
        "n_zero_excluded": n_zero,
        "n_blocks": len(clusters),
        "mae": stats.median_abs_error(obs, gt),
        "mae_ci": _ci(stats.cluster_bootstrap(clusters, _flat_median_abs, B, seed)),
        "bland_altman": stats.bland_altman(obs, gt),
        "bias_ci": _ci(stats.cluster_bootstrap(clusters, _flat_mean, B, seed)),
    }


def abandon_agreement(pairs):
    """Agreement on abandonment over 1:1 pairs. Ground truth is positive when the session's outcome is
    "cancel"; the observation is positive when the row's abandon flag is true.
    Returns {"table", "n", "kappa", "agree", "agree_ci"}; table = [[tn, fp], [fn, tp]] with rows the
    ground truth and columns the observation."""
    table = [[0, 0], [0, 0]]
    for p in pairs:
        g = 1 if p["gt"].get("outcome") == "cancel" else 0
        o = 1 if p["obs"].get("abandon") is True else 0
        table[g][o] += 1
    n = sum(sum(r) for r in table)
    x = table[0][0] + table[1][1]
    return {"table": table, "n": n, "kappa": stats.cohen_kappa(table),
            "agree": (x / n if n else None), "agree_ci": _ci(stats.wilson(x, n))}


def _nav_true(gt):
    c = gt.get("nav_true_cand")
    if c is not None:
        return c
    v = gt.get("nav_true")
    if v is None:
        raise ValueError("a ground-truth session has neither nav_true_cand nor nav_true")
    return v


def nav_agreement(pairs):
    """Agreement on the number of navigation key presses over 1:1 pairs. The true count is nav_true_cand
    when the session has one that is not null, otherwise nav_true.
    Returns {"n", "exact", "exact_ci", "diff_hist"}; diff_hist = [[observed - true, count], ...] in
    ascending order of the difference."""
    hist, x, n = {}, 0, 0
    for p in pairs:
        d = p["obs"]["nav"] - _nav_true(p["gt"])
        hist[d] = hist.get(d, 0) + 1
        n += 1
        x += 1 if d == 0 else 0
    return {"n": n, "exact": (x / n if n else None), "exact_ci": _ci(stats.wilson(x, n)),
            "diff_hist": [[d, hist[d]] for d in sorted(hist)]}


def truncation_check(gt_sessions, match_result, limit_ms=DEFAULT_LIMIT_MS):
    """The check of the cut-off: how many ground-truth sessions are longer than limit_ms, and how many
    of those appear in a pair, split, or merge of match_result (a session that produced a row).
    Returns {"limit_ms", "n_long", "n_long_with_row", "n_obs_over_limit"}; n_obs_over_limit counts
    the observed rows (in any bucket) whose dwell_ms exceeds the limit. Both counts are expected to
    be 0."""
    seen = set()
    for p in match_result["pairs"]:
        seen.add(match._dump(p["gt"]))
    for s in match_result["split"]:
        seen.add(match._dump(s["gt"]))
    for m in match_result["merge"]:
        for g in m["gt"]:
            seen.add(match._dump(g))
    long_s = [s for s in gt_sessions
              if s.get("end_wall_ms") is not None and _gt_dwell(s) > limit_ms]
    rows = [p["obs"] for p in match_result["pairs"]]
    rows += [o for s in match_result["split"] for o in s["obs"]]
    rows += [m["obs"] for m in match_result["merge"]]
    rows += list(match_result["false_pos"])
    return {"limit_ms": limit_ms, "n_long": len(long_s),
            "n_long_with_row": sum(1 for s in long_s if match._dump(s) in seen),
            "n_obs_over_limit": sum(1 for r in rows if r["dwell_ms"] > limit_ms)}


def oracle_report(oracle_agreement):
    """The plan-versus-ground-truth disagreements (gt_sessions.py's oracle_agreement): the count and
    rate of disagreements, and each type's count and rate, with Wilson intervals. The disagreeing
    trials stay in the evaluation."""
    if not isinstance(oracle_agreement, dict):
        raise ValueError("oracle_agreement must be an object")
    if not oracle_agreement.get("plan_available"):
        return {"plan_available": False, "n_trials": oracle_agreement.get("n_trials")}
    try:
        n, agree, by_type = oracle_agreement["n_trials"], oracle_agreement["n_agree"], oracle_agreement["by_type"]
    except KeyError as e:
        raise ValueError("oracle_agreement is missing %s" % e)
    dis = n - agree
    types = {}
    for t in sorted(by_type):
        c = by_type[t]
        types[t] = {"n": c, "rate": (c / n if n else None), "ci": _ci(stats.wilson(c, n))}
    return {"plan_available": True, "n_trials": n, "n_agree": agree, "n_disagree": dis,
            "disagree_rate": (dis / n if n else None), "disagree_ci": _ci(stats.wilson(dis, n)),
            "by_type": types, "unassigned_sessions": oracle_agreement.get("unassigned_sessions"),
            "removed_from_evaluation": False}


def _measures(pairs, block_of, B, seed):
    return {"dwell": dwell_error(pairs, block_of, B, seed), "abandon": abandon_agreement(pairs),
            "nav": nav_agreement(pairs)}


def l1_report(match_result, gt_sessions, oracle_agreement, plan_trials, cell, B, seed, limit_ms=DEFAULT_LIMIT_MS):
    """All the L1 measures, per stratum (cell, scenario, speed) and pooled.

    match_result: match.py's "matching" object. gt_sessions: the sessions of the definition that was
    matched. plan_trials: {trial_id: {"block_id", "scenario", "speed"}} (match.parse_plan_strata).
    A pair whose session belongs to no planned trial falls into the stratum (cell, null, null) and
    into one block of its own (block null)."""
    def block_of(gt):
        info = plan_trials.get(gt.get("trial_id"))
        return None if info is None else info["block_id"]

    def label(gt):
        info = plan_trials.get(gt.get("trial_id"))
        return (cell, info["scenario"], info["speed"]) if info else (cell, None, None)

    groups = {}
    for p in match_result["pairs"]:
        groups.setdefault(label(p["gt"]), []).append(p)
    by_stratum = []
    for lab in sorted(groups, key=lambda L: tuple((x is None, str(x)) for x in L)):
        row = {"stratum": dict(zip(["cell", "scenario", "speed"], lab))}
        row.update(_measures(groups[lab], block_of, B, seed))
        by_stratum.append(row)
    return {
        "metrics": {"by_stratum": by_stratum, "pooled": _measures(match_result["pairs"], block_of, B, seed)},
        "truncation": truncation_check(gt_sessions, match_result, limit_ms),
        "oracle": oracle_report(oracle_agreement),
    }


# ---------------------------------------------------------------- CLI

def parse_config(data):
    """Parse the configuration JSON (defaults if None) into {"B", "seed", "limit_ms"}."""
    cfg = {"B": DEFAULT_B, "seed": DEFAULT_SEED, "limit_ms": DEFAULT_LIMIT_MS}
    if data is None:
        return cfg
    obj = match._json_loads(match._decode(data, "config"), "config", False)
    if not isinstance(obj, dict):
        raise InputError("config: the top level must be an object")
    for k, v in obj.items():
        if k.startswith("_"):
            continue
        if k not in cfg:
            raise InputError("config: unknown key '%s'" % k)
        if not match._is_int(v) or (k != "seed" and v < 1):
            raise InputError("config: %s must be an integer%s" % (k, "" if k == "seed" else " of at least 1"))
        cfg[k] = v
    return cfg


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def evaluate(match_bytes, sessions_bytes, plan_bytes, oracle_bytes, config_bytes=None):
    """The CLI's core logic (bytes in, an output dict out). Identical input always yields an
    identical dict."""
    cfg = parse_config(config_bytes)
    m = match._json_loads(match._decode(match_bytes, "match"), "match", True)
    if not (isinstance(m, dict) and isinstance(m.get("matching"), dict)
            and isinstance(m["matching"].get("pairs"), list) and isinstance(m.get("config"), dict)
            and isinstance(m.get("inputs_sha256"), dict)):
        raise InputError("match: not match.py's output")
    definition = m.get("definition")
    if definition not in match.DEFINITIONS:
        raise InputError("match: definition is not one of all, macos_def, windows_def")
    for part in ("split", "merge", "false_pos"):
        if not isinstance(m["matching"].get(part), list):
            raise InputError("match: matching.%s is missing" % part)
    plan = match.parse_plan_strata(plan_bytes)
    oracle = gt_sessions.parse_oracle(oracle_bytes)
    if not isinstance(oracle["plan_sha256"], str) or oracle["plan_sha256"].lower() != plan["sha256"]:
        raise InputError("plan: SHA-256 does not match the oracle header's plan_sha256 (unrelated plan)")
    have = {"sessions": _sha(sessions_bytes), "plan": plan["sha256"], "oracle": _sha(oracle_bytes)}
    for k, v in have.items():
        if m["inputs_sha256"].get(k) != v:
            raise InputError("%s: SHA-256 does not match the one recorded in the match output (unrelated input)" % k)
    _src, sess, _exc = match.parse_sessions(sessions_bytes, definition)
    sobj = match._json_loads(match._decode(sessions_bytes, "sessions"), "sessions", True)
    cell = m["config"].get("cell")
    if not isinstance(cell, str):
        raise InputError("match: config.cell is missing")
    rep = l1_report(m["matching"], sess, sobj.get("oracle_agreement"), plan["trials"], cell,
                    cfg["B"], cfg["seed"], cfg["limit_ms"])
    rep.update({
        "definition": definition,
        "config": {"B": cfg["B"], "seed": cfg["seed"], "limit_ms": cfg["limit_ms"], "cell": cell},
        "inputs_sha256": {"match": _sha(match_bytes), "sessions": have["sessions"], "plan": have["plan"],
                          "oracle": have["oracle"], "config": None if config_bytes is None else _sha(config_bytes)},
        "used": {"n_pairs": len(m["matching"]["pairs"])},
        "note": "Pairs whose observed dwell_ms is 0 are left out of the dwell figures and counted in "
                "n_zero_excluded. Intervals are cluster-bootstrap (blocks) for dwell_ms and Wilson for "
                "proportions; read them as the width visible from this sample.",
    })
    return rep


def _fmt(v):
    return "n/a" if v is None else "%.3f" % v


def main(argv):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Level-1 agreement measures (dwell error, abandonment, navigation, cut-off, plan disagreements)")
    ap.add_argument("--match")
    ap.add_argument("--sessions")
    ap.add_argument("--plan")
    ap.add_argument("--oracle")
    ap.add_argument("--config")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not (args.match and args.sessions and args.plan and args.oracle and args.out):
        ap.error("--match / --sessions / --plan / --oracle / --out are required (--config is optional)")
    for inp in (args.match, args.sessions, args.plan, args.oracle, args.config):
        if inp and match._same_file(inp, args.out):
            print("l1: --out names the same file as an input (%s)" % inp, file=sys.stderr)
            return 2
    try:
        out = evaluate(match._read(args.match, "match"), match._read(args.sessions, "sessions"),
                       match._read(args.plan, "plan"), match._read(args.oracle, "oracle"),
                       None if args.config is None else match._read(args.config, "config"))
        match._write_atomic(args.out, match.render(out))
    except (InputError, ValueError) as e:
        print("l1: %s" % e, file=sys.stderr)
        return 2
    except OSError as e:
        print("l1: could not write output (%s)" % type(e).__name__, file=sys.stderr)
        return 2
    pooled, tr = out["metrics"]["pooled"], out["truncation"]
    print("l1: %d pairs; dwell n=%d (%d zero excluded), MAE %s ms; abandon agreement %s; nav exact %s; %d long sessions (%d with a row)" % (
        out["used"]["n_pairs"], pooled["dwell"]["n"], pooled["dwell"]["n_zero_excluded"], _fmt(pooled["dwell"]["mae"]),
        _fmt(pooled["abandon"]["agree"]), _fmt(pooled["nav"]["exact"]), tr["n_long"], tr["n_long_with_row"]))
    return 0


# ---------------------------------------------------------------- selftest

def _synth(n, seed, bias=0, sigma=50, flip=0.0, cancel_rate=0.3, n_blocks=20):
    """n synthetic 1:1 pairs. The observed dwell_ms is the true duration plus bias plus Gaussian noise
    (standard deviation sigma); the abandon flag is the true one, flipped with probability flip.
    Returns (pairs, block_of) where block_of maps trial_id to a block (n_blocks blocks)."""
    import random
    rng = random.Random(seed)
    t, pairs, block_of = 1700000000000, [], {}
    for i in range(n):
        t += 30000 + int(rng.random() * 90001)
        length = 800 + int(rng.random() * 1701)
        tid = "t%05d" % (i + 1)
        cancel = rng.random() < cancel_rate
        gt = match._gt(tid, t, t + length, outcome="cancel" if cancel else "commit")
        obs_abandon = (not cancel) if rng.random() < flip else cancel
        dwell = max(1, length + bias + int(round(rng.gauss(0, sigma))))
        obs = {"type": "ime_shadow", "t": t + length, "dwell_ms": dwell, "nav": 0, "abandon": obs_abandon}
        pairs.append({"gt": gt, "obs": obs, "iou": 1.0})
        block_of[tid] = i * n_blocks // n
        t += length
    return pairs, block_of


def _same(a, b):
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def _case_dwell_bias():
    f = []
    pairs, blk = _synth(1000, 1, bias=20, sigma=50)
    r = dwell_error(pairs, blk, 500, 7)
    lo, hi = r["bias_ci"]
    if r["n"] != 1000 or r["n_zero_excluded"] != 0 or r["n_blocks"] != 20:
        f.append("counts are not (1000, 0, 20): %r" % ((r["n"], r["n_zero_excluded"], r["n_blocks"]),))
    if lo is None or not (lo <= 20 <= hi):
        f.append("bias_ci does not contain the injected +20 ms: %r" % (r["bias_ci"],))
    if lo is not None and hi - lo > 10:
        f.append("bias_ci is too wide to be informative (%r)" % (r["bias_ci"],))
    sd = r["bland_altman"]["sd"]
    if not (45 <= sd <= 55):
        f.append("the Bland-Altman SD is not within 50 +/- 5: %r" % (sd,))
    if not (15 <= r["bland_altman"]["bias"] <= 25):
        f.append("the Bland-Altman bias is not near +20: %r" % (r["bland_altman"]["bias"],))
    # the sign is observed - ground truth: an observation that is too long gives a positive bias
    if r["bland_altman"]["bias"] <= 0:
        f.append("the sign is not observed - ground truth")
    # control: with no injected bias the interval must not contain 20 (the interval can tell the two apart)
    pairs0, blk0 = _synth(1000, 1, bias=0, sigma=50)
    lo0, hi0 = dwell_error(pairs0, blk0, 500, 7)["bias_ci"]
    if not (lo0 <= 0 <= hi0) or lo0 <= 20 <= hi0:
        f.append("with no bias the interval should contain 0 and not 20: %r" % ([lo0, hi0],))
    return f


def _case_abandon_flip():
    f = []
    pairs, _blk = _synth(1000, 2, flip=0.10)
    a = abandon_agreement(pairs)
    lo, hi = a["agree_ci"]
    if not (lo <= 0.90 <= hi):
        f.append("agree_ci does not contain 0.90 after a 10%% flip: %r (agree %r)" % (a["agree_ci"], a["agree"]))
    if hi >= 1.0 or a["agree"] >= 0.97:
        f.append("the flip is not visible in the agreement: %r" % (a["agree"],))
    if a["kappa"] is None or not (0.7 <= a["kappa"] <= 0.85):
        f.append("kappa is not near 0.77 (10%% flip, 30%% cancel): %r" % (a["kappa"],))
    if a["n"] != 1000 or sum(sum(r) for r in a["table"]) != 1000:
        f.append("the table does not hold every pair")
    # control: no flip gives perfect agreement
    p0, _b0 = _synth(1000, 2, flip=0.0)
    a0 = abandon_agreement(p0)
    if a0["agree"] != 1.0 or a0["kappa"] != 1.0 or a0["table"][0][1] != 0 or a0["table"][1][0] != 0:
        f.append("with no flip agreement and kappa should be exactly 1: %r" % (a0,))
    return f


def _case_dwell_zero():
    f = []
    pairs, blk = _synth(200, 3, bias=0, sigma=50)
    bad = [dict(p, obs=dict(p["obs"], dwell_ms=0)) if i % 20 == 0 else p for i, p in enumerate(pairs)]
    r = dwell_error(bad, blk, 300, 5)
    if r["n_zero_excluded"] != 10 or r["n"] != 190 or r["bland_altman"]["n"] != 190:
        f.append("the zero rows are not excluded and counted: %r" % ((r["n"], r["n_zero_excluded"], r["bland_altman"]["n"]),))
    kept = [p for i, p in enumerate(pairs) if i % 20 != 0]
    ref = dwell_error(kept, blk, 300, 5)
    ref["n_zero_excluded"] = 10
    if not _same(r, ref):
        f.append("the result differs from the one computed on the remaining pairs alone")
    if r["mae"] is None or r["mae"] > 100:
        f.append("a zero dwell_ms leaked into the error (MAE %r)" % (r["mae"],))
    # all pairs zero -> nothing to estimate, reported as null and never 0
    z = dwell_error([dict(p, obs=dict(p["obs"], dwell_ms=0)) for p in pairs[:5]], blk, 100, 5)
    if z["n"] != 0 or z["n_zero_excluded"] != 5 or z["mae"] is not None or z["bland_altman"]["bias"] is not None:
        f.append("with only zero rows the figures should be null: %r" % (z,))
    return f


def _case_shuffle():
    import random
    f = []
    pairs, blk = _synth(1000, 4, bias=0, sigma=50)
    base = dwell_error(pairs, blk, 300, 9)
    rng = random.Random(11)
    d = [p["obs"]["dwell_ms"] for p in pairs]
    for i in range(len(d) - 1, 0, -1):
        j = int(rng.random() * (i + 1))
        d[i], d[j] = d[j], d[i]
    shuf = [dict(p, obs=dict(p["obs"], dwell_ms=v)) for p, v in zip(pairs, d)]
    r = dwell_error(shuf, blk, 300, 9)
    b0, b1 = base["bland_altman"], r["bland_altman"]
    if abs(b0["bias"]) > 10 or abs(b1["bias"]) > 60:
        f.append("the bias should stay near 0 (kept the same marginal): %r -> %r" % (b0["bias"], b1["bias"]))
    if not (b1["sd"] > 5 * b0["sd"]):
        f.append("the SD did not grow after shuffling: %r -> %r" % (b0["sd"], b1["sd"]))
    if not ((b1["loa_hi"] - b1["loa_lo"]) > 5 * (b0["loa_hi"] - b0["loa_lo"])):
        f.append("the limits of agreement did not widen after shuffling")
    if not (r["mae"] > 5 * base["mae"]):
        f.append("the MAE did not grow after shuffling: %r -> %r" % (base["mae"], r["mae"]))
    return f


def _case_nav():
    f = []
    P = lambda nt, ntc, nav: {"gt": match._gt("t1", 0, 1, nav_true=nt, nav_true_cand=ntc), "obs": {"nav": nav}, "iou": 1.0}
    r = nav_agreement([P(4, 2, 2), P(4, None, 4), P(3, None, 5), P(3, 1, 0)])
    if r["n"] != 4 or r["exact"] != 0.5:
        f.append("exact is not 2/4: %r" % ((r["n"], r["exact"]),))
    if r["diff_hist"] != [[-1, 1], [0, 2], [2, 1]]:
        f.append("diff_hist is wrong (observed - true; nav_true_cand first, else nav_true): %r" % (r["diff_hist"],))
    lo, hi = r["exact_ci"]
    if not (0 < lo < 0.5 < hi < 1):
        f.append("exact_ci is not a Wilson interval around 0.5: %r" % (r["exact_ci"],))
    e = nav_agreement([])
    if e["exact"] is not None or e["exact_ci"] != [None, None] or e["diff_hist"] != []:
        f.append("no pairs should give null, not 0: %r" % (e,))
    try:
        nav_agreement([{"gt": {"trial_id": "t1"}, "obs": {"nav": 0}, "iou": 1.0}])
        f.append("a session without any true count was accepted")
    except ValueError:
        pass
    return f


def _case_truncation():
    f = []
    long_a = match._gt("t1", 0, 25000)
    long_b = match._gt("t2", 100000, 130000)
    short = match._gt("t3", 200000, 201000)
    ob = lambda lo, hi: {"type": "ime_shadow", "t": hi, "dwell_ms": hi - lo, "nav": 0, "abandon": False}
    res = {"pairs": [{"gt": short, "obs": ob(200000, 201000), "iou": 1.0}], "split": [], "merge": [],
           "miss": [long_a, long_b], "false_pos": []}
    r = truncation_check([long_a, long_b, short], res)
    if (r["n_long"], r["n_long_with_row"], r["n_obs_over_limit"]) != (2, 0, 0):
        f.append("expected (2 long, 0 with a row, 0 over the limit): %r" % (r,))
    # positive control: a long session that did get a row, and an observed row over the limit
    res2 = {"pairs": [{"gt": long_a, "obs": ob(0, 25000), "iou": 1.0}], "split": [{"gt": long_b, "obs": [ob(100000, 110000)]}],
            "merge": [], "miss": [], "false_pos": [ob(300000, 330000)]}
    r2 = truncation_check([long_a, long_b, short], res2)
    if (r2["n_long"], r2["n_long_with_row"], r2["n_obs_over_limit"]) != (2, 2, 2):
        f.append("the check cannot fail: expected (2, 2, 2), got %r" % (r2,))
    # the limit is exclusive ("longer than 20 s") and configurable
    edge = match._gt("t4", 0, 20000)
    if truncation_check([edge], res)["n_long"] != 0 or truncation_check([edge], res, limit_ms=19999)["n_long"] != 1:
        f.append("a session of exactly the limit should not count as long")
    if truncation_check([match._gt("t5", 0, None, outcome="open_at_end")], res)["n_long"] != 0:
        f.append("an unclosed session should not count as long")
    return f


def _case_oracle():
    f = []
    oa = {"plan_available": True, "n_trials": 100, "n_agree": 90, "rate": 0.9, "unassigned_sessions": 2,
          "by_type": {"no_session": 4, "unexpected_session": 1, "multiple_sessions": 5}, "mismatches": []}
    r = oracle_report(oa)
    if (r["n_disagree"], r["disagree_rate"]) != (10, 0.1) or r["removed_from_evaluation"] is not False:
        f.append("the disagreement count is wrong or claims removal: %r" % (r,))
    if not (r["disagree_ci"][0] < 0.1 < r["disagree_ci"][1]):
        f.append("disagree_ci does not surround 0.1: %r" % (r["disagree_ci"],))
    if list(r["by_type"]) != sorted(oa["by_type"]) or r["by_type"]["multiple_sessions"]["n"] != 5:
        f.append("by_type is wrong: %r" % (r["by_type"],))
    if oracle_report({"plan_available": False, "n_trials": 7}) != {"plan_available": False, "n_trials": 7}:
        f.append("without a plan only the trial count is reported")
    try:
        oracle_report({"plan_available": True, "n_trials": 3})
        f.append("an incomplete oracle_agreement was accepted")
    except ValueError:
        pass
    return f


def _case_small_samples():
    f = []
    pairs, blk = _synth(30, 5, bias=10, sigma=20, n_blocks=1)
    r = dwell_error(pairs, blk, 100, 3)
    if r["bias_ci"] != [None, None] or r["mae_ci"] != [None, None] or r["n_blocks"] != 1:
        f.append("one block should give no interval (null, not a point): %r" % (r,))
    e = dwell_error([], {}, 100, 3)
    if e["n"] != 0 or e["mae"] is not None or e["bias_ci"] != [None, None]:
        f.append("no pairs should give null, not 0: %r" % (e,))
    a = abandon_agreement([])
    if a["agree"] is not None or a["kappa"] is not None or a["agree_ci"] != [None, None]:
        f.append("no pairs should give null agreement: %r" % (a,))
    return f


def _case_byte_identical():
    f = []
    pairs, blk = _synth(300, 6, bias=5, sigma=40, flip=0.1)
    a = json.dumps(_measures(pairs, blk, 200, 13), sort_keys=True)
    b = json.dumps(_measures(pairs, blk, 200, 13), sort_keys=True)
    c = json.dumps(_measures(pairs, blk, 200, 14), sort_keys=True)
    if a != b:
        f.append("two runs with the same seed differ")
    if a == c:
        f.append("the seed has no effect on the intervals")
    return f


def _fixture_files(d):
    """match.py's synthetic fixture, with a complete oracle_agreement, run through match.evaluate; every
    input file is written under d. Returns the file paths."""
    fx = match._cli_fixture()
    sobj = json.loads(fx["sessions"].decode("utf-8"))
    sobj["oracle_agreement"] = {"plan_available": True, "n_trials": 90, "n_agree": 88, "rate": 88 / 90,
                                "by_type": {"multiple_sessions": 1, "no_session": 1}, "mismatches": [],
                                "unassigned_sessions": 0}
    sess_bytes = (json.dumps(sobj, indent=2) + "\n").encode("utf-8")
    out = match.evaluate(sess_bytes, "all", fx["obs"], fx["plan"], fx["oracle"], fx["config"])
    files = {"match.json": match.render(out), "sessions.json": sess_bytes, "plan.jsonl": fx["plan"],
             "oracle.jsonl": fx["oracle"], "config.json": b'{"B": 200, "seed": 3}'}
    paths = {}
    for name, data in files.items():
        paths[name] = os.path.join(d, name)
        with open(paths[name], "wb") as fh:
            fh.write(data)
    return paths


def _case_cli():
    import contextlib
    import io
    import tempfile
    f = []
    with tempfile.TemporaryDirectory() as d:
        p = _fixture_files(d)

        def run(out_name, **over):
            a = {"match": p["match.json"], "sessions": p["sessions.json"], "plan": p["plan.jsonl"],
                 "oracle": p["oracle.jsonl"], "config": p["config.json"]}
            a.update(over)
            argv = []
            for k, v in a.items():
                if v is not None:
                    argv += ["--" + k, v]
            argv += ["--out", os.path.join(d, out_name)]
            buf, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                rc = main(argv)
            return rc, os.path.join(d, out_name)

        rc1, o1 = run("o1.json")
        rc2, o2 = run("o2.json")
        if rc1 != 0 or rc2 != 0:
            return ["the CLI did not exit 0 (%r, %r)" % (rc1, rc2)]
        b1, b2 = open(o1, "rb").read(), open(o2, "rb").read()
        if b1 != b2:
            f.append("two runs on the same input give different bytes")
        if b"\r" in b1 or b1.startswith(b"\xef\xbb\xbf") or not b1.endswith(b"\n") or d.encode("utf-8") in b1:
            f.append("the output is not LF / no BOM / free of paths")
        out = json.loads(b1.decode("utf-8"))
        pooled = out["metrics"]["pooled"]
        if out["used"]["n_pairs"] != 84 or pooled["dwell"]["n"] != 84 or pooled["dwell"]["mae"] != 0 or pooled["dwell"]["n_blocks"] != 3:
            f.append("pooled dwell is not (84 pairs, MAE 0, 3 blocks): %r" % (pooled["dwell"],))
        if pooled["abandon"]["agree"] != 1.0 or pooled["abandon"]["kappa"] is not None:
            f.append("with one class only, agreement is 1 and kappa null: %r" % (pooled["abandon"],))
        if pooled["nav"]["exact"] != 1.0 or out["truncation"]["n_long"] != 0:
            f.append("nav agreement or truncation is wrong: %r %r" % (pooled["nav"], out["truncation"]))
        if len(out["metrics"]["by_stratum"]) != 9 or out["oracle"]["n_disagree"] != 2:
            f.append("expected 9 strata and 2 oracle disagreements: %r" % (len(out["metrics"]["by_stratum"]),))
        if sum(s["dwell"]["n"] for s in out["metrics"]["by_stratum"]) != 84:
            f.append("the strata do not add up to the pooled pairs")
        if any(s["dwell"]["bias_ci"] != [None, None] for s in out["metrics"]["by_stratum"]):
            f.append("a stratum with a single block should have a null interval")
        # unrelated inputs are refused (exit 2) and never combined
        with open(os.path.join(d, "plan2.jsonl"), "wb") as fh:
            fh.write(open(p["plan.jsonl"], "rb").read() + b"\n")
        if run("o3.json", plan=os.path.join(d, "plan2.jsonl"))[0] != 2:
            f.append("a plan that does not match the oracle header was accepted")
        with open(os.path.join(d, "sess2.json"), "wb") as fh:
            fh.write(open(p["sessions.json"], "rb").read() + b"\n")
        if run("o4.json", sessions=os.path.join(d, "sess2.json"))[0] != 2:
            f.append("a sessions file that does not match the match output was accepted")
        if run("o6.json", config=None)[0] != 0:
            f.append("the CLI should run with the default configuration")
        bad_cfg = os.path.join(d, "badcfg.json")
        for text in (b'{"B": 0}', b'{"nope": 1}', b'{"seed": 1.5}', b'[1]'):
            with open(bad_cfg, "wb") as fh:
                fh.write(text)
            if run("o7.json", config=bad_cfg)[0] != 2:
                f.append("an invalid configuration was accepted: %r" % (text,))
        if run("o8.json", match=os.path.join(d, "absent.json"))[0] != 2:
            f.append("a missing input should exit 2")
    return f


CASES = [
    ("recovers a dwell bias (+20 ms, sigma 50 ms; the interval and the SD)", _case_dwell_bias),
    ("recovers an abandon flip (10% flipped; the agreement interval and kappa)", _case_abandon_flip),
    ("excludes a dwell_ms of zero (and counts it)", _case_dwell_zero),
    ("shuffling widens the limits of agreement (negative control; the bias stays near 0)", _case_shuffle),
    ("navigation agreement (the true count, the difference distribution)", _case_nav),
    ("cut-off check (long sessions, rows over the limit, positive control)", _case_truncation),
    ("plan-versus-ground-truth report (counts, types, Wilson, not removed)", _case_oracle),
    ("small samples give null, never 0", _case_small_samples),
    ("byte-identical output for the same seed; the seed matters", _case_byte_identical),
    ("CLI (strata, pooled, byte-identical output, refusal of unrelated inputs, exit 2)", _case_cli),
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


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
