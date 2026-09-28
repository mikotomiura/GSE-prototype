#!/usr/bin/env python3
# kit: selftest
"""Closed-set identification (attacker knowledge K2): which of K candidate phrases was typed (standard library only).

  closed_set.py --obs OBS... --plan PLAN... --corpus F --recipes F --config F [--K 10,100,1000] [--seed N] --out F
  closed_set.py --selftest        positive and negative controls on synthetic observations (fast)

Simulation attack. For every candidate phrase the attacker runs the same scenario generator as the experiment
(build_trial of gen/generate_plan.py) to obtain a predicted log, and chooses the candidate whose predicted log is
closest to the observed one. Closeness is the edit distance between category sequences (insertion, deletion,
substitution), plus a penalty for the position and the size of long pauses (PAUSE_MS or longer). Ties are broken
with random.Random(seed).

Attacker knowledge (K2): the candidate set, the scenario, the OS, the typing-speed level, the generator, the recipes
and the configuration. The attacker does not know the typed phrase or the random draws inside the scenario (candidate
index, arrow-key count, thinking pause, inter-key intervals). One stream of random draws is shared by all candidates,
so that differences in draws do not reorder the candidates; this is a design choice available to the attacker.

The attacker receives only the observation (the category and the time of each key row). Trial boundaries are supplied
by the evaluator; the difficulty of locating boundaries is not part of this attack. The typed phrase is taken from the
plan only at evaluation time and is never used for the choice (passing true_index does not change the chosen
candidate). Rows of type ime_shadow are read but not used: their nav and abandon fields are fixed by the intent of the
scenario, not by the phrase, and their dwell time is a function of the key times that the timing feature already uses
(the gain from using it separately has not been measured). The attack code never reads the ground-truth or oracle logs of
the runner; that is the reason the observation reader accepts nothing but the rows of a standalone-logger output.

Scope. The results hold for this attack only. No upper bound on identifiability is claimed: a stronger language model,
boundary estimation or the combination of several trials is not included. Results are reported as measured, including
the case that identification is possible, and including the case that removing a feature does not lower the rate; the
order of the feature sets is not rearranged to fit an expectation. The fixed constants of the attack (PAUSE_MS, TAU_MS,
W_TIME) were chosen as part of the design and are not tuned on results.
"""
import argparse
import hashlib
import json
import math
import os
import random
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_KIT = os.path.dirname(_HERE)
for _p in (_HERE, os.path.join(_KIT, "gen"), os.path.join(_KIT, "analysis")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import generate_plan  # noqa: E402  (public functions: build_trial, trial_rng, validate_plan, load_corpus, load_recipes)
import simulate_obs  # noqa: E402
import stats  # noqa: E402  (Wilson interval)
from simulate_obs import KEYCAT, apply_features, simulate  # noqa: E402

FORMAT = "e2-closed/1"
CATEGORIES = ("alphabetic", "numeric", "punctuation", "sentence_punctuation", "tab", "backspace", "delete", "space",
              "enter", "navigation", "modifier", "function", "escape", "other")

# Feature sets of the removal experiment: name -> (timing, runs). "all" is the full feature set.
FEATURE_SETS = {
    "all": ("exact", "exact"),            # category sequence and times in ms
    "no_time": ("none", "exact"),         # times removed
    "no_runs": ("exact", "count"),        # alphabetic run length removed (count per 1-second window only)
    "bin1s": ("bin1s", "exact"),          # times coarsened to 1-second bins
    "bin1s_count": ("bin1s", "count"),    # 1-second bins and alphabetic count per window only
    "counts_only": ("none", "count"),     # no times; alphabetic keys reduced to one count for the whole trial
}

PAUSE_MS = 600      # intervals shorter than this are treated as typing jitter and ignored (their law does not depend on the phrase)
TAU_MS = 1000       # a difference of this size in the length of a pause gives the largest penalty
W_TIME = 0.5        # weight of the pause penalty (one category mismatch costs 1)


# ---------------------------------------------------------------- random numbers (random() only, stable across versions)

def _sub_seed(seed, *tags):
    h = hashlib.sha256((":".join([str(seed)] + [str(t) for t in tags])).encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big")


def _below(rng, k):
    return min(int(rng.random() * k), k - 1)


def _normal(rng):
    u1 = 1.0 - rng.random()
    u2 = rng.random()
    return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)


# ---------------------------------------------------------------- features -> symbol sequence -> distance

def _normalize(events):
    """Shift the times so that the first row is at 0 (the attacker does not use the absolute start of a trial)."""
    if not events:
        return []
    t0 = events[0][0]
    return [(t - t0, c) for t, c in events]


def _tokens(events, runs):
    """[(t, category)] -> ((category, count, interval since the previous token), ...).
    With runs == "count", the alphabetic rows stamped with the same time form one token."""
    toks = []
    for t, c in events:
        if runs == "count" and c == "alphabetic" and toks and toks[-1][0] == "alphabetic" and toks[-1][2] == t:
            toks[-1][1] += 1
        else:
            toks.append([c, 1, t])
    out = []
    prev = None
    for c, k, t in toks:
        out.append((c, k, 0 if prev is None else max(0, t - prev)))
        prev = t
    return tuple(out)


def _gap(iv):
    return iv if iv >= PAUSE_MS else 0


def _distance(obs, pred):
    """Distance between two token sequences. Insertion or deletion costs the count of the token. Substitution of a
    different category costs the larger count. Two tokens of the same category cost the difference of their counts
    plus the pause penalty (at most W_TIME)."""
    m = len(pred)
    prev = [0.0] * (m + 1)
    for j in range(1, m + 1):
        prev[j] = prev[j - 1] + pred[j - 1][1]
    for oc, on, oiv in obs:
        cur = [prev[0] + on]
        og = _gap(oiv)
        for j in range(1, m + 1):
            pc, pn, piv = pred[j - 1]
            if oc == pc:
                sub = abs(on - pn)
                pg = _gap(piv)
                if og or pg:
                    d = abs(og - pg)
                    sub += W_TIME * (d / TAU_MS if d < TAU_MS else 1.0)
            else:
                sub = on if on > pn else pn
            a = prev[j - 1] + sub
            b = prev[j] + on
            c = cur[j - 1] + pn
            cur.append(a if a <= b and a <= c else (b if b <= c else c))
        prev = cur
    return prev[m]


# ---------------------------------------------------------------- attack

class Predictor(object):
    """Predicted logs of the candidates. One (phrase, scenario, speed) is built once; the random draws depend only on the seed."""

    def __init__(self, recipes, config, os_name, seed):
        self.recipes, self.config, self.os_name, self.seed = recipes, config, os_name, seed
        self._raw = {}
        self._tok = {}

    def raw(self, phrase, scenario, speed):
        key = (phrase["phrase_id"], scenario, speed)
        if key not in self._raw:
            try:
                trial = generate_plan.build_trial(phrase, scenario, speed, self.os_name, self.recipes, self.config,
                                                  generate_plan.trial_rng(self.seed, "attack"), "t00000", 0)
                self._raw[key] = simulate(trial, KEYCAT)
            except ValueError:
                self._raw[key] = None   # the phrase cannot be typed in this scenario (for example, a character outside the kana layout)
        return self._raw[key]

    def tokens(self, phrase, scenario, speed, timing, runs):
        key = (phrase["phrase_id"], scenario, speed, timing, runs)
        if key not in self._tok:
            ev = self.raw(phrase, scenario, speed)
            self._tok[key] = None if ev is None else _tokens(_normalize(apply_features(ev, timing, runs)), runs)
        return self._tok[key]


def _feature_pair(features):
    if isinstance(features, str):
        if features not in FEATURE_SETS:
            raise ValueError("features must be one of %s" % "/".join(sorted(FEATURE_SETS)))
        return FEATURE_SETS[features]
    timing, runs = features
    if timing not in simulate_obs.TIMINGS or runs not in simulate_obs.RUNS:
        raise ValueError("features (timing, runs) is outside the allowed values")
    return timing, runs


def attack(observed, candidates, scenario, os_name, recipes, config, features, seed, speed="mid", true_index=None,
           tie_seed=None, cache=None):
    """Choose the candidate closest to the observation ([(t, category)]).

    candidates: phrases (dicts of a corpus phrase row). features: a name of FEATURE_SETS or a (timing, runs) pair.
    Returns {"chosen": candidate index, "ranking": indices from the closest, "distances": list of distances,
    "rank_of_true": 1-based rank (only when true_index is given, otherwise None)}. true_index is used only to report
    the rank and never for the choice. seed drives the attacker's random draws for the predicted logs; tie_seed drives
    the tie-breaking (default: seed). cache: a Predictor to reuse predicted logs.
    """
    if not candidates:
        raise ValueError("no candidates")
    timing, runs = _feature_pair(features)
    pred = cache if cache is not None else Predictor(recipes, config, os_name, seed)
    obs_tok = _tokens(_normalize(apply_features(list(observed), timing, runs)), runs)
    memo = {}
    dist = []
    for ph in candidates:
        pt = pred.tokens(ph, scenario, speed, timing, runs)
        if pt is None:
            dist.append(float("inf"))
            continue
        if pt not in memo:
            memo[pt] = _distance(obs_tok, pt)
        dist.append(memo[pt])
    rng = random.Random(_sub_seed(seed if tie_seed is None else tie_seed, "tie"))
    keys = [rng.random() for _ in candidates]
    order = sorted(range(len(candidates)), key=lambda i: (dist[i], keys[i]))
    rank = None if true_index is None else order.index(true_index) + 1
    return {"chosen": order[0], "ranking": order, "distances": dist, "rank_of_true": rank}


def _make_candidates(rng, pool, true, K):
    """The typed phrase plus K-1 phrases with other readings, in random order. Returns (candidates, index of the typed phrase)."""
    eligible = [p for p in pool if p["reading"] != true["reading"]]
    if len(eligible) < K - 1:
        raise ValueError("the corpus has too few phrases with distinct readings (K = %d)" % K)
    for i in range(K - 1):
        j = i + _below(rng, len(eligible) - i)
        eligible[i], eligible[j] = eligible[j], eligible[i]
    cands = [true] + eligible[:K - 1]
    for i in range(len(cands) - 1, 0, -1):
        j = _below(rng, i + 1)
        cands[i], cands[j] = cands[j], cands[i]
    return cands, [c["phrase_id"] for c in cands].index(true["phrase_id"])


def _pool_by_reading(corpus):
    seen = set()
    pool = []
    for p in corpus:
        if p["reading"] not in seen:
            seen.add(p["reading"])
            pool.append(p)
    return pool


def evaluate(trials, corpus, K, features_list, seed, recipes, config):
    """For every trial, attack with the typed phrase and K-1 decoys, and return the accuracy for each feature set.

    trials: [{"trial_id", "scenario", "speed", "os", "phrase_id", "observed": [(t, category)]}].
    Returns {feature set: {"acc", "acc_ci" (Wilson 95%), "chance": 1/K, "n", "n_skipped", "mean_rank"}}.
    Trials whose phrase is not in the corpus (synthetic kana strings) are not counted (n_skipped).
    """
    if not isinstance(K, int) or K < 2:
        raise ValueError("K must be an integer of at least 2")
    by_id = dict((p["phrase_id"], p) for p in corpus)
    pool = _pool_by_reading(corpus)
    if len(pool) < K:
        raise ValueError("the corpus has %d distinct readings, fewer than K = %d" % (len(pool), K))
    used = [t for t in trials if t["phrase_id"] in by_id]
    preds = {}
    res = dict((f, {"correct": 0, "ranks": []}) for f in features_list)
    for tr in used:
        tseed = _sub_seed(seed, "trial", tr["trial_id"], K)
        cands, ti = _make_candidates(random.Random(_sub_seed(tseed, "cand")), pool, by_id[tr["phrase_id"]], K)
        if tr["os"] not in preds:
            preds[tr["os"]] = Predictor(recipes, config, tr["os"], seed)
        for f in features_list:
            r = attack(tr["observed"], cands, tr["scenario"], tr["os"], recipes, config, f, seed, speed=tr["speed"],
                       true_index=ti, tie_seed=_sub_seed(tseed, "tie", f), cache=preds[tr["os"]])
            res[f]["correct"] += 1 if r["chosen"] == ti else 0
            res[f]["ranks"].append(r["rank_of_true"])
    out = {}
    n = len(used)
    for f in features_list:
        x = res[f]["correct"]
        lo, hi = stats.wilson(x, n)
        out[f] = {"acc": (x / n) if n else None, "acc_ci": [lo, hi], "chance": 1.0 / K, "n": n,
                  "n_skipped": len(trials) - n, "mean_rank": (sum(res[f]["ranks"]) / n) if n else None}
    return out


# ---------------------------------------------------------------- inputs (publishable logs and plans)

def read_obs(path):
    """Read a standalone-logger output. Returns (list of [(t, category)] for key presses, number of ime_shadow rows).
    Only key rows (press true) and ime_shadow rows are read; any other row type or unknown key is rejected."""
    with open(path, "rb") as f:
        raw = f.read()
    lines = raw.decode("utf-8").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if not lines:
        raise ValueError("empty observation")
    events = []
    shadow = 0
    for ln, line in enumerate(lines, start=1):
        try:
            obj = json.loads(line)
        except ValueError:
            raise ValueError("observation line %d is not JSON" % ln)
        if not isinstance(obj, dict):
            raise ValueError("observation line %d is not an object" % ln)
        if ln == 1:
            if obj.get("type") != "meta" or obj.get("format") != "obs/1":
                raise ValueError("the first observation line is not an obs/1 header")
            continue
        kind = obj.get("type")
        if kind == "key":
            if set(obj) != {"type", "t", "category", "press"} or not isinstance(obj["t"], int) \
                    or isinstance(obj["t"], bool) or obj["category"] not in CATEGORIES or not isinstance(obj["press"], bool):
                raise ValueError("observation line %d: wrong shape for a key row" % ln)
            if obj["press"]:
                events.append((obj["t"], obj["category"]))
        elif kind == "ime_shadow":
            if set(obj) != {"type", "t", "dwell_ms", "nav", "abandon"}:
                raise ValueError("observation line %d: wrong shape for an ime_shadow row" % ln)
            shadow += 1
        else:
            raise ValueError("observation line %d: a row type that is not read" % ln)
    for a, b in zip(events, events[1:]):
        if b[0] < a[0]:
            raise ValueError("key rows are not in ascending time order")
    return events, shadow


def read_plan(path):
    """Read a plan (plan/1). Raises ValueError when the generator's validator rejects it. Returns the rows."""
    with open(path, "rb") as f:
        data = f.read()
    problems = generate_plan.validate_plan(data)
    if problems:
        raise ValueError("the plan is rejected by the plan/1 validator (%d problems, first at line %d [%s])" % (
            len(problems), problems[0][0], problems[0][1]))
    return [json.loads(line) for line in data.decode("utf-8").split("\n") if line]


def expected_categories(trial_row, keycat=KEYCAT):
    return [keycat[s["key"]] for s in trial_row["steps"] if s["down"] and keycat[s["key"]] is not None]


def segment_by_plan(events, rows, markers_in_obs=False, tag=""):
    """Cut the sequence of observed presses into trials in plan order (the evaluator supplies the boundaries).

    The number of presses and the category sequence of every trial must agree with the plan; otherwise ValueError is
    raised, so that a dropped key never shifts later trials silently. When markers_in_obs is true, the presses of the
    block-start markers are skipped. Returns [{"trial_id", "block_id", "scenario", "speed", "phrase_id", "os", "observed"}].
    """
    header = rows[0]
    pos = 0
    out = []
    for r in rows[1:]:
        if r["kind"] == "block":
            if markers_in_obs:
                pos += len(r["marker"])
            continue
        exp = expected_categories(r)
        seg = events[pos:pos + len(exp)]
        if [c for _, c in seg] != exp:
            raise ValueError("trial %s%s: the presses do not match the plan (missing, extra or different keys)" % (
                tag, r["trial_id"]))
        pos += len(exp)
        out.append({"trial_id": tag + r["trial_id"], "block_id": r["block_id"], "scenario": r["scenario"],
                    "speed": r["speed"], "phrase_id": r["phrase_id"], "os": header["os"], "observed": seg})
    if pos != len(events):
        raise ValueError("the observation has %d more presses than the plan" % (len(events) - pos))
    return out


# ---------------------------------------------------------------- CLI

ASSUMPTIONS = [
    "attacker knowledge K2: the candidate set, scenario, OS, typing-speed level, generator, recipes and config",
    "the attacker is given the trial boundaries (evaluator-supplied); boundary detection is not part of this attack",
    "candidates: the typed phrase plus K-1 corpus phrases with distinct readings, drawn per trial",
    "attacker uses common random numbers across candidates; timing feature = positions and sizes of pauses >= pause_ms",
    "results are for this attack only; no claim is made about the upper bound of identifiability",
]


def _sha_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run(obs_paths, plan_paths, corpus_path, recipes_path, config_path, Ks, features_list, seed, markers_in_obs):
    if len(obs_paths) != len(plan_paths):
        raise ValueError("--obs and --plan differ in count (%d and %d)" % (len(obs_paths), len(plan_paths)))
    recipes = generate_plan.load_recipes(recipes_path)
    with open(config_path, "rb") as f:
        try:
            config = json.loads(f.read().decode("utf-8"))
        except ValueError:
            raise ValueError("the configuration is not JSON")
    generate_plan.normalize_config(config)
    corpus = generate_plan.load_corpus(corpus_path)
    trials = []
    n_shadow = 0
    for i, (op, pp) in enumerate(zip(obs_paths, plan_paths)):
        events, sh = read_obs(op)
        n_shadow += sh
        trials.extend(segment_by_plan(events, read_plan(pp), markers_in_obs, tag="s%d-" % i))
    results = {}
    for K in Ks:
        results[str(K)] = evaluate(trials, corpus, K, features_list, seed, recipes, config)
    return {"format": FORMAT, "assumptions": ASSUMPTIONS, "seed": seed, "n_sessions": len(obs_paths),
            "n_trials": len(trials), "n_ime_shadow_rows_unused": n_shadow, "features": dict(
                (f, {"timing": FEATURE_SETS[f][0], "runs": FEATURE_SETS[f][1]}) for f in features_list),
            "params": {"pause_ms": PAUSE_MS, "tau_ms": TAU_MS, "w_time": W_TIME},
            "corpus_sha256": _sha_file(corpus_path), "recipes_sha256": _sha_file(recipes_path),
            "config_sha256": _sha_file(config_path), "results": results}


def render(result):
    return (json.dumps(result, ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf-8")


# ---------------------------------------------------------------- selftest

def _selftest_world(tmp, n_trials, seed, scenarios):
    """Synthetic world: a synthetic corpus of varied length, a configuration, planned trials and observations
    (times perturbed by 30 ms)."""
    recipes_path = os.path.join(_KIT, "gen", "recipes.json")
    recipes = generate_plan.load_recipes(recipes_path)
    kana = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわ"
    rng = random.Random(seed)
    readings = []
    seen = set()
    while len(readings) < 150:
        r = "".join(kana[_below(rng, len(kana))] for _ in range(2 + _below(rng, 13)))   # 2 to 14 characters
        if r not in seen:
            seen.add(r)
            readings.append(r)
    lines = ['{"kind":"header","format":"corpus/1","source":"aozora","tokenizer":"table","dict":"none"}']
    for i, r in enumerate(readings, start=1):
        lines.append(generate_plan.dumps({"kind": "phrase", "phrase_id": "w1-%d-1" % i, "work_id": "w1", "text": "x",
                                          "reading": r, "reading_len": len(r)}))
    corpus_path = os.path.join(tmp, "corpus.jsonl")
    with open(corpus_path, "wb") as f:
        f.write(("\n".join(lines) + "\n").encode("utf-8"))
    cfg = {"n_per_cell_scenario_speed": 6, "block_size": 12,
           "speeds": {"slow": {"iki_median_ms": 300, "iki_sigma": 0.3}, "mid": {"iki_median_ms": 200, "iki_sigma": 0.3},
                      "fast": {"iki_median_ms": 120, "iki_sigma": 0.3}},
           "key_hold_ms": 60, "think_ms": {"min": 200, "max": 2000}, "cand_index_max": 4, "nav_count_max": 3,
           "inter_trial_ms": 1000, "marker": ["f13", "f14", "f13"], "marker_gap_ms": 150, "reset_ime_every_block": True}
    cfg_path = os.path.join(tmp, "cfg.json")
    with open(cfg_path, "wb") as f:
        f.write(json.dumps(cfg, indent=1).encode("utf-8"))
    corpus = generate_plan.load_corpus(corpus_path)
    trials = []
    for i in range(n_trials):
        tid = "t%05d" % (i + 1)
        ph = corpus[_below(rng, len(corpus))]
        sc = scenarios[i % len(scenarios)]
        sp = generate_plan.SPEEDS[(i // len(scenarios)) % 3]
        row = generate_plan.build_trial(ph, sc, sp, "macos", recipes, cfg, generate_plan.trial_rng(seed, tid), tid, 0)
        obs = simulate(row, KEYCAT, t0=_below(rng, 100000))
        jit = []
        for t, c in obs:
            t = int(round(t + 30.0 * _normal(rng)))
            jit.append((max(t, jit[-1][0]) if jit else t, c))
        trials.append({"trial_id": tid, "scenario": sc, "speed": sp, "os": "macos", "phrase_id": ph["phrase_id"],
                       "observed": jit})
    return recipes, cfg, cfg_path, corpus, corpus_path, trials


def selftest():
    fails = []
    n = [0]

    def check(name, cond, detail=""):
        n[0] += 1
        if not cond:
            fails.append(name + (": " + detail if detail else ""))

    def raises(name, fn):
        n[0] += 1
        try:
            fn()
        except ValueError:
            return
        except Exception as e:
            fails.append("%s: a different exception: %r" % (name, e))
            return
        fails.append("%s: no exception was raised" % name)

    tmp = tempfile.mkdtemp(prefix="closed_set_selftest_")
    try:
        recipes, cfg, cfg_path, corpus, corpus_path, trials = _selftest_world(tmp, 150, 20260928,
                                                                              ("S1", "S2", "S3", "S7", "S10"))
        feats = list(FEATURE_SETS)

        # distance, unit checks
        a = (("alphabetic", 1, 0),) * 5 + (("space", 1, 300), ("enter", 1, 100))
        check("distance: identical sequences give 0", _distance(a, a) == 0.0)
        check("distance: one substitution costs 1", _distance(a, a[:-1] + (("escape", 1, 100),)) == 1.0)
        check("distance: one extra row (insertion) costs 1", _distance(a, a[1:]) == 1.0)
        c5 = (("alphabetic", 5, 0), ("space", 1, 300))
        c7 = (("alphabetic", 7, 0), ("space", 1, 300))
        check("distance: a difference in the alphabetic count costs the difference (runs count)", _distance(c5, c7) == 2.0)
        p1 = (("alphabetic", 1, 0), ("space", 1, 0), ("enter", 1, 2000))
        p2 = (("alphabetic", 1, 0), ("space", 1, 0), ("enter", 1, 800))
        check("distance: a mismatch in the size of a long pause never exceeds W_TIME", 0.0 < _distance(p1, p2) <= W_TIME)
        p3 = (("alphabetic", 1, 0), ("space", 1, 0), ("enter", 1, 100))
        p4 = (("alphabetic", 1, 0), ("space", 1, 0), ("enter", 1, 400))
        check("distance: differences among intervals shorter than PAUSE_MS are ignored", _distance(p3, p4) == 0.0)

        # positive control, K = 10 and 40
        for K in (10, 40):
            out = evaluate(trials, corpus, K, feats, 7, recipes, cfg)
            for f in feats:
                check("removal experiment K=%d %s: every trial is counted" % (K, f),
                      out[f]["n"] == len(trials) and out[f]["n_skipped"] == 0)
            r = out["all"]
            print("K=%-3d chance %.3f | " % (K, 1.0 / K) + " ".join("%s=%.3f" % (f, out[f]["acc"]) for f in feats))
            check("全特徴で偶然を超える (all features exceed chance; K=%d, Wilson lower bound above 1/K)" % K,
                  r["acc_ci"][0] > 1.0 / K, "acc %.3f CI %r" % (r["acc"], r["acc_ci"]))
            if K == 10:
                check("全特徴で偶然を超える (all features reach an accuracy of at least 0.5 at K=10)", r["acc"] >= 0.5,
                      "acc %.3f" % r["acc"])
        # The values of the removal experiment are printed as measured (they need not decrease); only their shape is checked.
        out10 = evaluate(trials, corpus, 10, feats, 7, recipes, cfg)
        check("removal experiment: every feature set has acc in [0, 1] and a CI containing acc",
              all(0.0 <= out10[f]["acc"] <= 1.0 and out10[f]["acc_ci"][0] <= out10[f]["acc"] <= out10[f]["acc_ci"][1]
                  for f in feats))

        # negative control: an observation without information
        const = [(0, "alphabetic")] * 8 + [(1600, "space"), (2400, "enter")]
        flat = [dict(t, observed=list(const)) for t in trials]
        for K in (10, 40):
            oc = evaluate(flat, corpus, K, ["all", "no_time"], 7, recipes, cfg)
            for f in ("all", "no_time"):
                x = int(round(oc[f]["acc"] * oc[f]["n"]))
                lo, hi = stats.wilson(x, oc[f]["n"], conf=0.99)
                check("情報の無い観測で偶然水準 (uninformative observation stays at chance; K=%d, %s, 1/K inside the 99%% Wilson interval)"
                      % (K, f), lo <= 1.0 / K <= hi,
                      "acc %.3f interval (%.3f, %.3f) 1/K %.3f" % (oc[f]["acc"], lo, hi, 1.0 / K))
        # negative control 2: observations swapped between trials
        rot = [dict(t, observed=list(trials[(i + 1) % len(trials)]["observed"])) for i, t in enumerate(trials)]
        orr = evaluate(rot, corpus, 10, ["all"], 7, recipes, cfg)["all"]
        xr = int(round(orr["acc"] * orr["n"]))
        lo, hi = stats.wilson(xr, orr["n"], conf=0.99)
        check("情報の無い観測で偶然水準 (observations swapped between trials stay at chance; K=10, 99%% Wilson interval)",
              lo <= 0.1 <= hi, "acc %.3f interval (%.3f, %.3f)" % (orr["acc"], lo, hi))

        # determinism
        b1 = json.dumps(evaluate(trials, corpus, 10, feats, 7, recipes, cfg), sort_keys=True)
        b2 = json.dumps(evaluate(trials, corpus, 10, feats, 7, recipes, cfg), sort_keys=True)
        b3 = json.dumps(evaluate(trials, corpus, 10, feats, 8, recipes, cfg), sort_keys=True)
        check("the same seed gives byte-identical results", b1 == b2)
        check("negative control: a different seed changes the results", b1 != b3)

        # the typed phrase does not influence the choice; ties depend on the seed
        same = True
        for tr in trials[:30]:
            cands, ti = _make_candidates(random.Random(3), _pool_by_reading(corpus),
                                         next(p for p in corpus if p["phrase_id"] == tr["phrase_id"]), 10)
            r0 = attack(tr["observed"], cands, tr["scenario"], "macos", recipes, cfg, "all", 5, speed=tr["speed"])
            r1 = attack(tr["observed"], cands, tr["scenario"], "macos", recipes, cfg, "all", 5, speed=tr["speed"],
                        true_index=ti)
            if r0["chosen"] != r1["chosen"] or r0["ranking"] != r1["ranking"] or r0["rank_of_true"] is not None \
                    or r1["rank_of_true"] is None or r1["ranking"][0] != r1["chosen"]:
                same = False
        check("passing true_index changes neither chosen nor ranking (only rank_of_true is added)", same)
        dup = [corpus[0]] * 6
        picks = set(attack(const, dup, "S1", "macos", recipes, cfg, "all", 5, tie_seed=s)["chosen"] for s in range(40))
        check("ties depend on tie_seed (identical candidates: several are chosen over 40 seeds)", len(picks) > 1)
        check("the same tie_seed gives the same choice",
              attack(const, dup, "S1", "macos", recipes, cfg, "all", 5, tie_seed=9)["chosen"]
              == attack(const, dup, "S1", "macos", recipes, cfg, "all", 5, tie_seed=9)["chosen"])
        raises("empty candidate list", lambda: attack(const, [], "S1", "macos", recipes, cfg, "all", 5))
        raises("unknown feature set", lambda: attack(const, dup, "S1", "macos", recipes, cfg, "nope", 5))
        kana_only = {"phrase_id": "w9-1-1", "work_id": "w9", "text": "", "reading": "がっこう", "reading_len": 4}
        rk = attack(const, [kana_only, corpus[1]], "S12", "macos", recipes, cfg, "all", 5)
        check("a candidate that cannot be typed in the scenario (S12, character outside the kana layout) has distance inf and ranks last",
              rk["distances"][0] == float("inf") and rk["chosen"] == 1)

        # inputs: publishable logs
        good = ['{"type":"meta","format":"obs/1","os":"macos","logger_version":"0.0.0","manifest_sha256":"%s",'
                '"capabilities":{"unconditional":["key"],"threshold_gated":[],"config_gated":["ime_shadow"]}}' % ("0" * 64),
                '{"type":"key","t":100,"category":"alphabetic","press":true}',
                '{"type":"key","t":160,"category":"alphabetic","press":false}',
                '{"type":"ime_shadow","t":300,"dwell_ms":200,"nav":0,"abandon":false}']

        def obs_file(lines, name="o.ndjson"):
            p = os.path.join(tmp, name)
            with open(p, "wb") as f:
                f.write(("\n".join(lines) + "\n").encode("utf-8"))
            return p

        ev, sh = read_obs(obs_file(good))
        check("read_obs takes key presses only (not releases) and counts ime_shadow rows",
              ev == [(100, "alphabetic")] and sh == 1)
        raises("read_obs rejects a row type that is not read", lambda: read_obs(obs_file(good + ['{"type":"sent","t":1}'])))
        raises("read_obs rejects an unknown key in a key row (a raw key code)",
               lambda: read_obs(obs_file(good + ['{"type":"key","t":1,"category":"space","press":true,"vk":32}'])))
        raises("read_obs rejects a category outside the enumeration",
               lambda: read_obs(obs_file(good + ['{"type":"key","t":1,"category":"kana","press":true}'])))
        raises("read_obs rejects a missing header", lambda: read_obs(obs_file(good[1:])))
        raises("read_obs rejects key rows out of time order",
               lambda: read_obs(obs_file(good + ['{"type":"key","t":50,"category":"space","press":true}'])))

        # command line, end to end (plan -> observation -> attack -> JSON)
        rows, _ = generate_plan.plan_rows(corpus, recipes, dict(cfg, scenarios=["S1", "S2", "S3"], n_per_cell_scenario_speed=4),
                                          "macos", 3, "0" * 64, "0" * 64, "0" * 64)
        plan_path = os.path.join(tmp, "plan.jsonl")
        with open(plan_path, "wb") as f:
            f.write(generate_plan.render_plan(rows))
        prng = random.Random(5)
        clock = 1000000
        obs_lines = [good[0]]
        mk_lines = [good[0]]
        for r in rows[1:]:
            if r["kind"] == "block":
                clock += 5000
                for _ in r["marker"]:
                    mk_lines.append('{"type":"key","t":%d,"category":"function","press":true}' % clock)
                    clock += r["marker_gap_ms"]
                continue
            clock += r["gap_before_ms"]
            for t, c in simulate(r, KEYCAT, t0=clock):
                t = int(round(t + 30.0 * _normal(prng)))
                line = '{"type":"key","t":%d,"category":"%s","press":true}' % (t, c)
                obs_lines.append(line)
                mk_lines.append(line)
            clock += r["steps"][-1]["at_ms"] + 2000

        def fix_order(lines):
            out, last = [lines[0]], -1
            for ln in lines[1:]:
                o = json.loads(ln)
                o["t"] = max(o["t"], last)
                last = o["t"]
                out.append(json.dumps(o, separators=(",", ":")))
            return out
        obs_p = obs_file(fix_order(obs_lines), "obs1.ndjson")
        mk_p = obs_file(fix_order(mk_lines), "obs_mk.ndjson")
        out_a, out_b = os.path.join(tmp, "a.json"), os.path.join(tmp, "b.json")
        base = ["--plan", plan_path, "--corpus", corpus_path, "--recipes", os.path.join(_KIT, "gen", "recipes.json"),
                "--config", cfg_path, "--K", "10,40", "--seed", "3"]
        rc_a = main(["--obs", obs_p] + base + ["--out", out_a])
        rc_b = main(["--obs", obs_p] + base + ["--out", out_b])
        check("command line: an end-to-end run exits 0", rc_a == 0 and rc_b == 0, "%r %r" % (rc_a, rc_b))
        if rc_a == 0 and rc_b == 0:
            with open(out_a, "rb") as f1, open(out_b, "rb") as f2:
                ba, bb = f1.read(), f2.read()
            check("command line: the same input gives byte-identical output", ba == bb)
            js = json.loads(ba.decode("utf-8"))
            check("command line: the output holds both K values, every feature set, the assumptions and n",
                  sorted(js["results"]) == ["10", "40"] and set(js["results"]["10"]) == set(feats)
                  and js["n_trials"] == 36 and js["results"]["10"]["all"]["n"] == 36 and len(js["assumptions"]) >= 4
                  and js["n_ime_shadow_rows_unused"] == 0, str(js.get("n_trials")))
            check("command line: the attack works (all features, K=10, accuracy above chance)",
                  js["results"]["10"]["all"]["acc"] > js["results"]["10"]["all"]["chance"], str(js["results"]["10"]["all"]))
        rc_m = main(["--obs", mk_p] + base + ["--out", out_b, "--markers-in-obs"])
        check("command line: --markers-in-obs skips the marker presses and succeeds", rc_m == 0, str(rc_m))
        check("command line: marker presses without --markers-in-obs stop the run (exit 2)",
              main(["--obs", mk_p] + base + ["--out", out_b]) == 2)
        drop = fix_order(obs_lines[:5] + obs_lines[6:])
        check("command line: one missing press stops the run instead of shifting later trials (exit 2)",
              main(["--obs", obs_file(drop, "drop.ndjson")] + base + ["--out", out_b]) == 2)
        check("command line: differing counts of --obs and --plan stop the run (exit 2)",
              main(["--obs", obs_p, obs_p] + base + ["--out", out_b]) == 2)
        check("command line: a corpus too small for K stops the run (exit 2)",
              main(["--obs", obs_p] + [a if a != "10,40" else "1000" for a in base] + ["--out", out_b]) == 2)
        check("command line: no arguments exit 2", main([]) == 2)
    finally:
        for name in os.listdir(tmp):
            os.remove(os.path.join(tmp, name))
        os.rmdir(tmp)

    if fails:
        for f in fails:
            print("FAIL: " + f)
        print("selftest failed: %d of %d checks" % (len(fails), n[0]))
        return 1
    print("selftest OK (%d checks)" % n[0])
    return 0


def main(argv):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Closed-set simulation attack and feature-removal experiment")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--obs", nargs="+", help="standalone-logger outputs (obs/1)")
    ap.add_argument("--plan", nargs="+", help="plans (plan/1), in the same order and number as --obs")
    ap.add_argument("--corpus")
    ap.add_argument("--recipes")
    ap.add_argument("--config")
    ap.add_argument("--K", default="10,100,1000", help="numbers of candidates (comma separated)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--features", default=",".join(FEATURE_SETS), help="feature sets (default: all of them)")
    ap.add_argument("--markers-in-obs", action="store_true",
                    help="the presses of the block-start markers appear in the observation")
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not (args.obs and args.plan and args.corpus and args.recipes and args.config and args.out):
        ap.print_usage(sys.stderr)
        return 2
    try:
        Ks = [int(x) for x in args.K.split(",") if x]
        if not Ks or any(k < 2 for k in Ks):
            raise ValueError("--K must be comma-separated integers of at least 2")
        feats = [x for x in args.features.split(",") if x]
        bad = [x for x in feats if x not in FEATURE_SETS]
        if not feats or bad:
            raise ValueError("--features must be among %s" % "/".join(FEATURE_SETS))
        result = run(args.obs, args.plan, args.corpus, args.recipes, args.config, Ks, feats, args.seed,
                     args.markers_in_obs)
    except (ValueError, OSError) as e:
        print("closed_set.py: %s" % e, file=sys.stderr)
        return 2
    with open(args.out, "wb") as f:
        f.write(render(result))
    print("closed-set identification: %d trials, K = %s, written to %s" % (
        result["n_trials"], ",".join(str(k) for k in Ks), args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
