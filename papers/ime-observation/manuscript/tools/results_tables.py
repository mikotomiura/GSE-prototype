#!/usr/bin/env python3
"""Generate the result tables and the values quoted in the text of the manuscript from the result files.

  python3 manuscript/tools/results_tables.py --results experiment/results --out manuscript/generated
  python3 manuscript/tools/results_tables.py --results experiment/results --out manuscript/generated --check
  python3 manuscript/tools/results_tables.py --selftest

Every number of the results that the manuscript states is copied by this script from the result files of
`kit/analysis/pipeline.py` (questions 1 to 3), `kit/e2/closed_set.py` (question 4) and `kit/e3/summarize_e3.py`
(question 5); none is typed by hand. The script reads the cells of the macOS analysis from the top of the results
directory and the Windows cell from its subdirectory `windows`, and the corrected analysis of deviation D10 from
`d10/macos` and `d10/windows`; a cell whose files are absent is reported as not measured. It writes:

- values.json: every value with its full precision and its source (file and path inside the file);
- values.tex: the formatted values, read in the text with the macro \\rv{<key>} that main.tex defines;
- table-detection.tex: detection per cell and speed (the range of the per-scenario intervals);
- table-session.tex: per-session agreement per cell and speed;
- table-text-agreement.tex: per-text agreement of the four measures of section 4.6 per cell and speed (primary scope);
- text-agreement.tex: for the supplement, per-text agreement over all trials, pooled over speeds and in the three
  mixtures of section 6.7 (whose weights are checked), and the per-trial differences per scenario and speed;
- table-closed-set.tex: the near-chance judgement of section 6.8 per cell, set and K, and the recommendation;
- table-open-set.tex: the open-set reconstruction per cell, attacker (K0, K1, K1+) and knowledge of the length;
- table-cost.tex: runtime cost per system and condition (sections 6.10 and 10.9);
- detection-strata.tex: the per-stratum detection of every cell, with the merge rate of the corrected analysis of
  deviation D10 next to the registered one, for the supplement (a cell that was not measured is stated as such);
- closed-set-all.tex: every feature set at every K per cell, with the raw accuracy per speed and scenario, for the
  supplement.

Question 4 (section 6.8, and section 10.7 for Windows): a feature set is near chance at K when the upper end of the
Wilson interval of its reported accuracy (the maximum over the set and the sets derivable from it) is at most 2/K; it
is near chance for the rule when it is so at K = 10 and K = 100. The recommendation is the most detailed of no_time and
counts_only that is near chance in both macOS cells, else none; without both macOS cells it is not decided. The
Windows judgement of the same set is its qualification and never changes it. The closed-set files must be those of
deviation D8 (every trial of S12 left out). Question 5: a condition is quoted only when its status is measured, and on
Windows a working condition whose every CPU sample is zero is insufficient (section 10.9).

The values of the abstract follow the rule fixed in outline.md before the results ("Rule for the abstract"): for
recall and precision, the range from the lowest lower end to the highest upper end of the Wilson intervals of the
strata that keep at least MIN_TRIALS trials in the scope, with the number of strata left out, the fractions of trials
set aside by the scope and by carry-over, and the same range over all trials; for the dwell error, the range of the
per-speed intervals of the bias. Proportions are printed with three decimals and durations in whole milliseconds
(Python's rounding of the binary value); values.json keeps the unrounded values.

With --check nothing is written: the files that would be written are compared with those in the output directory and
the script exits 1 when any differs, so that a table cannot drift from the result files.

Standard library only.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile

MIN_TRIALS = 30
PRIMARY_COMPARISON = "gt_obs"
PRIMARY_SCOPE = "under_limit"
SCOPES = ("under_limit", "all_trials")
SPEEDS = ("slow", "mid", "fast")
FILES = ("e1_detection.json", "e1_l1.json", "e1_l2.json")
# The labels of the three cells of the measurement (experiment/data.md and experiment/data.windows.md).
EXPECTED_CELLS = ("macos-standard-live-on", "macos-standard-live-off", "windows-msime-tsf")
MACOS_CELLS = EXPECTED_CELLS[:2]
WINDOWS_CELL = EXPECTED_CELLS[2]
# Question 4 (section 6.8 of the pre-registration). The feature sets of the closed set, from the most detailed; the
# rule considers only the two sets that keep no time, the most detailed first (counts_only is a coarsening of
# no_time), and only K = 10 and K = 100 (K = 1,000 is descriptive).
CLOSED_SET_SETS = ("all", "no_runs", "bin1s", "bin1s_count", "no_time", "counts_only")
RULE_SETS = ("no_time", "counts_only")
RULE_KS = (10, 100)
CLOSED_SET_KS = (10, 100, 1000)
# Deviation D8: the closed set leaves out every trial of this scenario in every cell.
CLOSED_SET_SKIPPED = "S12"
# The open set (section 6.8): the attackers as (split, model, label); K1+ is K1 with the corpus split by phrase.
OPEN_SET_ATTACKERS = (("work", "K0", "K0"), ("work", "K1", "K1"), ("phrase", "K1", "K1+"),
                      ("phrase", "K0", "K0 (split by phrase)"))
OPEN_SET_LENGTHS = (("count", "number of segments"), ("true", "true length"))
# Question 5 (sections 6.10 and 10.9): one summary file per system, one block per condition.
E3_CONDITIONS = ("idle", "working")
E3_FILES = (("", "macos", "e3_macos.txt"), ("windows", "windows", "e3_windows.txt"))
# Question 3 (sections 4.6 and 6.7): the four per-text measures in the order of section 4.6, with their labels and
# whether the measure is a duration in milliseconds; the three mixtures of speeds with their weights (slow, mid, fast).
L2_MEASURES = (("conversions_per_trial", "Conversions per trial", False),
               ("mean_dwell_ms", "Mean conversion time (ms)", True),
               ("abandon_rate", "Abandonment rate", False),
               ("dwell_fraction", "Fraction of time converting", False))
L2_MIXTURES = (("slow_heavy", "0.6/0.3/0.1", (0.6, 0.3, 0.1)), ("uniform", "equal", (1 / 3.0, 1 / 3.0, 1 / 3.0)),
               ("fast_heavy", "0.1/0.3/0.6", (0.1, 0.3, 0.6)))
# The three views of the per-trial differences (section 6.7); the last two need the layers of the prediction (macOS).
L2_VIEWS = (("per_trial", "every trial of the scope"),
            ("per_trial_uncontaminated", "trials in neither carry layer (for reweighting)"),
            ("per_trial_layer_none", "trials of the layer none (diagnostic)"))
L2_TRIAL_MEASURES = (("n_conversions", "Conversions", False), ("dwell_sum_ms", "Summed conversion time (ms)", True),
                     ("n_cancelled", "Cancelled conversions", False))
# Deviation D10: the corrected analysis of questions 1 to 3, per system.
D10_DIRS = {"macos": os.path.join("d10", "macos"), "windows": os.path.join("d10", "windows")}
GENERATED_NOTE = "% Generated by manuscript/tools/results_tables.py from the result files; do not edit by hand.\n"


# ---------------------------------------------------------------- reading


def load(path):
    with open(path, "rb") as f:
        return json.loads(f.read().decode("utf-8"))


def find_cells(results_dir):
    """[(directory, file prefix for the source, cell label, system)] for every cell whose three files exist."""
    found = []
    for sub, system in (("", "macos"), ("windows", "windows")):
        d = os.path.join(results_dir, sub) if sub else results_dir
        if not all(os.path.isfile(os.path.join(d, f)) for f in FILES):
            continue
        det = load(os.path.join(d, "e1_detection.json"))
        for label in sorted(det["cells"]):
            found.append((d, (sub + "/") if sub else "", label, system))
    return found


def definition_of(system):
    """The session definition that the analysis uses for a cell of this system (experiment/notes.md)."""
    return "windows_def" if system == "windows" else "macos_def"


def stratum_key(st):
    return (st["scenario"], st["speed"])


def scenario_order(name):
    return int(name[1:]) if name[1:].isdigit() else 10 ** 6


class Cell(object):
    """The values of one cell, read from its three result files, with the source of each value."""

    def __init__(self, directory, prefix, label, system):
        self.label, self.system = label, system
        self.directory, self.prefix = directory, prefix
        self.definition = definition_of(system)
        self.src = {}
        docs = {}
        for f in FILES:
            docs[f] = load(os.path.join(directory, f))
            self.src[f] = prefix + f
        for f in FILES:
            prim = docs[f].get("primary") or {}
            if prim.get("comparison") != PRIMARY_COMPARISON or prim.get("scope") != PRIMARY_SCOPE:
                raise ValueError("%s: the primary comparison and scope are not %s under %s" % (
                    self.src[f], PRIMARY_COMPARISON, PRIMARY_SCOPE))
        self.det, self.l1, self.l2 = (docs[f]["cells"][label][self.definition][PRIMARY_COMPARISON] for f in FILES)
        for name, block in (("e1_detection.json", self.det), ("e1_l1.json", self.l1), ("e1_l2.json", self.l2)):
            for scope in SCOPES:
                if not block.get(scope):
                    raise ValueError("%s: no %s under %s for cell %s" % (self.src[name], scope, self.definition, label))

    def path(self, f, *keys):
        return "%s:cells/%s/%s/%s/%s" % (self.src[f], self.label, self.definition, PRIMARY_COMPARISON,
                                         "/".join(str(k) for k in keys))

    def kept_trials(self, scope):
        """{(scenario, speed): trials kept in the scope}, from the per-trial records of level 2, and the totals."""
        pt = self.l2[scope]["per_trial"]
        kept, total = {}, 0
        for st in pt["by_stratum"]:
            k = stratum_key(st["stratum"])
            kept[k] = st["n_trials"]
            tnu = st["trials_not_used"]
            total += st["n_trials"] + tnu["excluded"] + tnu["not_run"] + tnu["out_of_scope"]
        if sum(kept.values()) != pt["n_trials"]:
            raise ValueError("%s: the per-stratum trials do not add up to n_trials" % self.path("e1_l2.json", scope))
        return kept, total, pt["trials_not_used"]

    def detection_strata(self, scope):
        """{(scenario, speed): stratum entry of e1_detection.json} (the row of presses outside the trials is left out)."""
        out = {}
        for st in self.det[scope]["metrics"]["by_stratum"]:
            if st["stratum"] in (None, "all") or st["stratum"].get("scenario") is None:
                continue
            out[stratum_key(st["stratum"])] = st
        return out

    def speed_sessions(self, scope):
        return dict((st["stratum"]["speed"], st) for st in self.l1[scope]["metrics"]["by_speed"])


# ---------------------------------------------------------------- values


NO_VALUE = "--"


def fmt_p(x):
    """A proportion; NO_VALUE when the result file holds no value (no denominator, or deviation D10)."""
    return NO_VALUE if x is None else "%.3f" % x


def est_ci(value, lo, hi, fmt=None):
    """An estimate with its interval; the estimate alone when the interval has no value, NO_VALUE without estimate."""
    fmt = fmt or fmt_p
    if value is None:
        return NO_VALUE
    if lo is None or hi is None:
        return fmt(value)
    return "%s [%s, %s]" % (fmt(value), fmt(lo), fmt(hi))


def fmt_ms(x):
    if x is None:
        return NO_VALUE
    s = "{:,}".format(int(round(x)))
    return "$-$" + s[1:] if s.startswith("-") else s


def fmt_pct(x):
    return "%.1f\\%%" % (100.0 * x)


def fmt_int(n):
    return "{:,}".format(n).replace(",", "{,}")


def interval_range(entries):
    """(lowest lower end, highest upper end) of entries {"lo", "hi"}."""
    return min(e["lo"] for e in entries), max(e["hi"] for e in entries)


def strata_in_range(kept, strata, keys, measure):
    """The strata of keys that enter the range of a measure: at least MIN_TRIALS trials kept in the scope and an
    interval of the measure in the result file. The rule leaves out, per measure, the strata with fewer trials or with
    no value, so a stratum without a value of precision (no session row) still enters the range of recall."""
    return [k for k in keys if kept[k] >= MIN_TRIALS and k in strata and strata[k][measure]["lo"] is not None
            and strata[k][measure]["hi"] is not None]


def abstract_values(cell):
    """The values of items (i) and (ii) of the rule for the abstract, with their sources."""
    vals = {}
    for scope in SCOPES:
        kept, total, not_used = cell.kept_trials(scope)
        strata = cell.detection_strata(scope)
        design = sorted(kept, key=lambda k: (scenario_order(k[0]), SPEEDS.index(k[1])))
        tag = "primary" if scope == PRIMARY_SCOPE else "all"
        for m in ("recall", "precision"):
            used = strata_in_range(kept, strata, design, m)
            if used:
                lo, hi = interval_range([strata[k][m] for k in used])
                vals["%s.%s.%s.range" % (cell.label, tag, m)] = {
                    "text": "%s--%s" % (fmt_p(lo), fmt_p(hi)), "value": [lo, hi],
                    "source": cell.path("e1_detection.json", scope, "metrics/by_stratum/*", m, "lo|hi")}
            vals["%s.%s.%s.strata.used" % (cell.label, tag, m)] = {
                "text": str(len(used)), "value": len(used),
                "source": cell.path("e1_l2.json", scope, "per_trial/by_stratum")}
            vals["%s.%s.%s.strata.left" % (cell.label, tag, m)] = {
                "text": str(len(design) - len(used)), "value": len(design) - len(used),
                "source": cell.path("e1_l2.json", scope, "per_trial/by_stratum")}
        if scope == PRIMARY_SCOPE:
            out_of_scope = not_used["out_of_scope"]
            carry = cell.det[scope]["excluded"]["trials"]["by_type"].get("carry_over", 0)
            vals["%s.trials.total" % cell.label] = {
                "text": fmt_int(total), "value": total, "source": cell.path("e1_l2.json", scope, "per_trial")}
            vals["%s.scope.setaside" % cell.label] = {
                "text": "%s of %s trials (%s)" % (fmt_int(out_of_scope), fmt_int(total),
                                                  fmt_pct(float(out_of_scope) / total)),
                "value": [out_of_scope, total],
                "source": cell.path("e1_l2.json", scope, "per_trial/trials_not_used/out_of_scope")}
            vals["%s.carryover" % cell.label] = {
                "text": "%s of %s trials (%s)" % (fmt_int(carry), fmt_int(total), fmt_pct(float(carry) / total)),
                "value": [carry, total],
                "source": cell.path("e1_detection.json", scope, "excluded/trials/by_type/carry_over")}
        sp = cell.speed_sessions(scope)
        cis = [sp[s]["dwell"]["bias_ci"] for s in SPEEDS if s in sp and sp[s]["dwell"]["bias_ci"][0] is not None]
        if cis:
            lo, hi = min(c[0] for c in cis), max(c[1] for c in cis)
            vals["%s.%s.dwellbias.range" % (cell.label, tag)] = {
                "text": "%s to %s~ms" % (fmt_ms(lo), fmt_ms(hi)), "value": [lo, hi],
                "source": cell.path("e1_l1.json", scope, "metrics/by_speed/*/dwell/bias_ci")}
    return vals


# ---------------------------------------------------------------- question 4: closed set and the recommendation


def closed_set_name(label):
    return "e2_closed_set_%s.json" % label


def read_closed_set(cell):
    """The closed-set result of a cell, or None when its file is absent. The file must be the analysis of deviation
    D8 (every trial of S12 left out) and hold every feature set at every K with the chance level 1/K."""
    p = os.path.join(cell.directory, closed_set_name(cell.label))
    if not os.path.isfile(p):
        return None
    doc = load(p)
    src = cell.prefix + closed_set_name(cell.label)
    if CLOSED_SET_SKIPPED not in (doc.get("skipped_scenarios") or {}):
        raise ValueError("%s: %s is not left out (deviation D8)" % (src, CLOSED_SET_SKIPPED))
    for K in CLOSED_SET_KS:
        for f in CLOSED_SET_SETS:
            r = (doc.get("results") or {}).get(str(K), {}).get(f)
            if r is None:
                raise ValueError("%s: no result for K = %d and the feature set %s" % (src, K, f))
            if abs(r["chance"] - 1.0 / K) > 1e-12:
                raise ValueError("%s: the chance level of K = %d is not 1/K" % (src, K))
    return doc


def near_chance_at(r, K):
    """Section 6.8: the accuracy (the maximum over the set and its coarsenings) is near chance at K when the upper end
    of its 95% Wilson interval is at most 2/K. None when the result has no interval (no scored trial)."""
    hi = r["acc_ci"][1] if r.get("n") else None
    if hi is None:
        return None
    return hi <= 2.0 / K


def near_chance(doc, f):
    """Near chance at both K = 10 and K = 100 (True / False), or None when either has no value."""
    judged = [near_chance_at(doc["results"][str(K)][f], K) for K in RULE_KS]
    if any(j is None for j in judged):
        return None
    return all(judged)


def recommend(docs):
    """The recommendation of section 6.8, from the two macOS cells only: the most detailed of RULE_SETS that is near
    chance in both cells. {"status": "recommended" | "none" | "not decided", "set": name or None}. Without both macOS
    cells the condition cannot be checked and nothing is recommended."""
    if any(docs.get(c) is None for c in MACOS_CELLS):
        return {"status": "not decided", "set": None}
    for f in RULE_SETS:
        if all(near_chance(docs[c], f) is True for c in MACOS_CELLS):
            return {"status": "recommended", "set": f}
    return {"status": "none", "set": None}


def yes_no(j):
    return NO_VALUE if j is None else ("yes" if j else "no")


def closed_set_values(cells, docs):
    """Values of question 4: the recommendation (item iii of the rule for the abstract), the Windows judgement as its
    qualification, and per cell the accuracy and the judgement of the two sets of the rule."""
    vals = {}
    rec = recommend(docs)
    macos_src = ", ".join(closed_set_name(c) for c in MACOS_CELLS)
    text = {"recommended": "\\texttt{%s}" % tex_escape(rec["set"] or ""), "none": "none",
            "not decided": "not decided (a macOS cell was not measured)"}[rec["status"]]
    vals["q4.recommendation"] = {"text": text, "value": rec, "source": macos_src + ":results/10|100/*/acc_ci"}
    win = docs.get(WINDOWS_CELL)
    if win is None:
        q = "the Windows cell was not measured"
        qv = None
    elif rec["status"] == "recommended":
        qv = near_chance(win, rec["set"])
        q = {True: "holds on Windows", False: "does not hold on Windows", None: "has no value on Windows"}[qv]
    else:
        qv = dict((f, near_chance(win, f)) for f in RULE_SETS)
        q = "; ".join("\\texttt{%s} near chance on Windows: %s" % (tex_escape(f), yes_no(qv[f])) for f in RULE_SETS)
    vals["q4.windows.qualification"] = {"text": q, "value": qv,
                                        "source": "windows/" + closed_set_name(WINDOWS_CELL) + ":results/10|100/*/acc_ci"}
    for cell in cells:
        doc = docs.get(cell.label)
        if doc is None:
            continue
        src = cell.prefix + closed_set_name(cell.label)
        al = doc.get("alignment") or {}
        vals["%s.q4.unscored" % cell.label] = {
            "text": "%s blocks, %s trials" % (fmt_int(al.get("n_blocks_unscored", 0)), fmt_int(al.get("n_trials_unscored", 0))),
            "value": [al.get("n_blocks_unscored"), al.get("n_trials_unscored")], "source": src + ":alignment"}
        for f in RULE_SETS:
            for K in RULE_KS:
                r = doc["results"][str(K)][f]
                vals["%s.q4.%s.k%d.acc" % (cell.label, f, K)] = {
                    "text": est_ci(r["acc"], r["acc_ci"][0], r["acc_ci"][1]), "value": [r["acc"]] + list(r["acc_ci"]),
                    "source": "%s:results/%d/%s/acc|acc_ci" % (src, K, f)}
            vals["%s.q4.%s.near" % (cell.label, f)] = {
                "text": yes_no(near_chance(doc, f)), "value": near_chance(doc, f),
                "source": "%s:results/10|100/%s/acc_ci" % (src, f)}
    return vals


def open_set_name(label):
    return "e2_open_set_%s.json" % label


def read_open_set(cell):
    """The open-set result of a cell, or None when its file is absent; both splits and both length levels must be
    present with K0 and K1."""
    p = os.path.join(cell.directory, open_set_name(cell.label))
    if not os.path.isfile(p):
        return None
    doc = load(p)
    for split, model, _ in OPEN_SET_ATTACKERS:
        for li, _ in OPEN_SET_LENGTHS:
            r = (doc.get("splits") or {}).get(split, {}).get(li)
            if r is None or model not in r or model not in (r.get("shuffled") or {}):
                raise ValueError("%s: no result for the split %s, length %s and model %s" % (
                    cell.prefix + open_set_name(cell.label), split, li, model))
    return doc


def open_set_values(cell, doc):
    """Values of the open set for the text: per attacker and length level, the attack's CER, the gain over the
    baseline and the gain over the shuffled control, each with its interval."""
    vals = {}
    if doc is None:
        return vals
    src = cell.prefix + open_set_name(cell.label)
    for split, model, label in OPEN_SET_ATTACKERS:
        key = label.split(" ")[0].replace("+", "plus") + ("" if split == "work" or model == "K1" else ".phrase")
        for li, _ in OPEN_SET_LENGTHS:
            r = doc["splits"][split][li]
            sh = r["shuffled"][model]
            base = "%s.q4.open.%s.%s" % (cell.label, key, li)
            vals[base + ".cer"] = {"text": est_ci(r[model]["cer"], r[model]["cer_ci"][0], r[model]["cer_ci"][1]),
                                   "value": [r[model]["cer"]] + list(r[model]["cer_ci"]),
                                   "source": "%s:splits/%s/%s/%s/cer" % (src, split, li, model)}
            vals[base + ".gain"] = {"text": est_ci(r["gain"][model]["gain"], r["gain"][model]["gain_ci"][0],
                                                   r["gain"][model]["gain_ci"][1], fmt_signed),
                                    "value": [r["gain"][model]["gain"]] + list(r["gain"][model]["gain_ci"]),
                                    "source": "%s:splits/%s/%s/gain/%s" % (src, split, li, model)}
            vals[base + ".gainvsshuffled"] = {
                "text": est_ci(sh["gain_vs_shuffled"], sh["gain_vs_shuffled_ci"][0], sh["gain_vs_shuffled_ci"][1],
                               fmt_signed),
                "value": [sh["gain_vs_shuffled"]] + list(sh["gain_vs_shuffled_ci"]),
                "source": "%s:splits/%s/%s/shuffled/%s/gain_vs_shuffled" % (src, split, li, model)}
    return vals


# ---------------------------------------------------------------- question 5: runtime cost


def _e3_number(s):
    return None if s == "n/a" else float(s)


def read_e3(path):
    """{condition: summary} from the output of kit/e3/summarize_e3.py (one block per condition)."""
    with open(path, "rb") as f:
        text = f.read().decode("utf-8")
    out, cur = {}, None
    for line in text.splitlines():
        if line.startswith("== "):
            name = line[3:].split(" (", 1)[0]
            if name in out:
                raise ValueError("%s: the condition %s appears twice" % (path, name))
            cur = out[name] = {"status": None, "cpu": None, "cpu_all_zero": None, "rss_final_mb": None,
                               "rss_slope_mb_per_h": None, "hours": None, "usable": None}
            continue
        if cur is None:
            continue
        if line.startswith("rows: "):
            cur["usable"] = int(line.split()[1])
        elif line.startswith("cpu % (one core = 100): "):
            p = line.split()
            cur["cpu"] = dict((p[i], _e3_number(p[i + 1])) for i in range(6, len(p) - 1, 2))
        elif line.startswith("cpu_all_zero: "):
            cur["cpu_all_zero"] = line.split()[1] == "true"
        elif line.startswith("resident memory: final "):
            p = line.split()
            cur["rss_final_mb"], cur["rss_slope_mb_per_h"], cur["hours"] = (
                _e3_number(p[3]), _e3_number(p[6]), _e3_number(p[9]))
        elif line.startswith("status: "):
            cur["status"] = line[len("status: "):].split(" -- ", 1)[0]
    for name, s in out.items():
        if name not in E3_CONDITIONS:
            raise ValueError("%s: unknown condition %s" % (path, name))
        if s["status"] not in ("measured", "insufficient", "not measured"):
            raise ValueError("%s: the condition %s has no status" % (path, name))
        if s["status"] != "not measured" and (s["cpu"] is None or set(s["cpu"]) != {"mean", "median", "p95", "max"}):
            raise ValueError("%s: the CPU line of the condition %s cannot be read" % (path, name))
    return out


def e3_quotable(system, condition, s):
    """Whether the figures of a condition may be quoted (section 6.10): measured, and on Windows not a working
    condition whose every CPU sample is zero (section 10.9 takes that as a counter that could not be read)."""
    if s is None or s["status"] != "measured":
        return False
    if system == "windows" and condition == "working" and s["cpu_all_zero"]:
        return False
    return True


def read_e3_all(results_dir):
    """{system: (source, {condition: summary})} for every system whose summary file exists."""
    out = {}
    for sub, system, name in E3_FILES:
        p = os.path.join(results_dir, sub, name) if sub else os.path.join(results_dir, name)
        if os.path.isfile(p):
            out[system] = ((sub + "/" if sub else "") + name, read_e3(p))
    return out


def fmt_cpu(x):
    return NO_VALUE if x is None else "%.2f" % x


def e3_values(e3):
    """Item (iv) of the rule for the abstract: the mean CPU of each condition per system, without an interval."""
    vals = {}
    for system in ("macos", "windows"):
        src, conds = e3.get(system, (None, {}))
        for c in E3_CONDITIONS:
            s = conds.get(c)
            ok = e3_quotable(system, c, s)
            vals["%s.e3.%s.cpu.mean" % (system, c)] = {
                "text": fmt_cpu(s["cpu"]["mean"]) if ok else NO_VALUE,
                "value": s["cpu"]["mean"] if ok else None,
                "source": ("%s:%s/cpu mean" % (src, c)) if src else "not measured"}
    return vals


# ---------------------------------------------------------------- question 3: per-text agreement


def fmt_signed(x, ms=False):
    """A difference: whole milliseconds for a duration, three decimals otherwise, with a typeset minus sign."""
    if x is None:
        return NO_VALUE
    if ms:
        return fmt_ms(x)
    s = "%.3f" % x
    return "$-$" + s[1:] if s.startswith("-") else s


def l2_mixtures(cell, scope):
    """The mixtures of speeds of a scope, checked against the weights of section 6.7."""
    mixes = cell.l2[scope]["mixture_bias"]["mixtures"]
    for name, _, w in L2_MIXTURES:
        got = mixes.get(name, {}).get("weights") or {}
        if any(abs(got.get(s, -1.0) - x) > 1e-9 for s, x in zip(SPEEDS, w)):
            raise ValueError("%s: the weights of the mixture %s are not those of section 6.7" % (
                cell.path("e1_l2.json", scope, "mixture_bias/mixtures"), name))
    return mixes


def l2_values(cell):
    """Per-speed bias and ICC of the four per-text measures in the primary scope, for the text."""
    vals = {}
    by = cell.l2[PRIMARY_SCOPE]["agreement_by_stratum"]
    for m, _, ms in L2_MEASURES:
        for s in SPEEDS:
            e = (by.get(s) or {}).get(m)
            if e is None:
                continue
            ba = e["bland_altman"]
            vals["%s.l2.%s.%s.bias" % (cell.label, m, s)] = {
                "text": est_ci(ba["bias"], e["bias_ci"][0], e["bias_ci"][1], lambda x: fmt_signed(x, ms)),
                "value": [ba["bias"]] + list(e["bias_ci"]),
                "source": cell.path("e1_l2.json", PRIMARY_SCOPE, "agreement_by_stratum", s, m, "bias_ci")}
            vals["%s.l2.%s.%s.icc" % (cell.label, m, s)] = {
                "text": est_ci(e["icc21"], e["icc21_ci"][0], e["icc21_ci"][1], lambda x: fmt_signed(x)),
                "value": [e["icc21"]] + list(e["icc21_ci"]),
                "source": cell.path("e1_l2.json", PRIMARY_SCOPE, "agreement_by_stratum", s, m, "icc21_ci")}
    return vals


# ---------------------------------------------------------------- deviation D10: the corrected merge rate


def read_d10(results_dir, cell):
    """The detection block of the corrected analysis (deviation D10) for the cell, or None when it was not run. The
    registered block must not carry the switch and the corrected one must carry it."""
    p = os.path.join(results_dir, D10_DIRS[cell.system], "e1_detection.json")
    for scope in SCOPES:
        if "merge_recount" in cell.det[scope]["config"]:
            raise ValueError("%s: the registered results carry the switch of deviation D10" % cell.src["e1_detection.json"])
    if not os.path.isfile(p):
        return None
    block = load(p)["cells"][cell.label][cell.definition][PRIMARY_COMPARISON]
    for scope in SCOPES:
        if block[scope]["config"].get("merge_recount") != "obs":
            raise ValueError("%s: the corrected results do not record merge_recount obs" % p)
    return block


def d10_strata(block, scope):
    out = {}
    for st in block[scope]["metrics"]["by_stratum"]:
        if st["stratum"] in (None, "all") or st["stratum"].get("scenario") is None:
            continue
        out[stratum_key(st["stratum"])] = st
    return out


def d10_values(cell, block):
    """The number of strata whose merge rate the corrected analysis changes, per scope."""
    vals = {}
    if block is None:
        return vals
    for scope in SCOPES:
        reg, cor = cell.detection_strata(scope), d10_strata(block, scope)
        if sorted(reg) != sorted(cor):
            raise ValueError("%s: the strata of the corrected results differ from the registered ones" % cell.label)
        n = sum(1 for k in reg if reg[k]["merge_rate"] != cor[k]["merge_rate"])
        tag = "primary" if scope == PRIMARY_SCOPE else "all"
        vals["%s.d10.%s.merge.differ" % (cell.label, tag)] = {
            "text": "%d of %d" % (n, len(reg)), "value": [n, len(reg)],
            "source": "%s and %s/e1_detection.json:%s/metrics/by_stratum/*/merge_rate" % (
                cell.src["e1_detection.json"], D10_DIRS[cell.system].replace(os.sep, "/"), scope)}
    return vals


# ---------------------------------------------------------------- tables


def tex_escape(s):
    return s.replace("_", "\\_").replace("%", "\\%").replace("&", "\\&")


def ci_text(e):
    return est_ci(e.get("value"), e.get("lo"), e.get("hi"))


def table_detection(cells):
    lines = [GENERATED_NOTE,
             "\\begin{table}[t]\n",
             "\\caption{Detection per cell and speed: the range from the lowest lower end to the highest upper end of the "
             "Wilson intervals of the scenarios that keep at least %d trials and have a value of the measure, with the "
             "number of such scenarios and of all scenarios in parentheses, in the primary scope and over all trials; "
             "%s: no scenario in the range}\n" % (MIN_TRIALS, NO_VALUE),
             "\\label{tab:detection}\n",
             "\\begin{tabular}{L{0.18}L{0.08}L{0.185}L{0.185}L{0.185}L{0.185}}\n",
             "\\toprule\n",
             "Cell & Speed & Recall & Precision & Recall, all trials & Precision, all trials \\\\\n",
             "\\midrule\n"]
    for cell in cells:
        per_scope = {}
        for scope in SCOPES:
            kept, _, _ = cell.kept_trials(scope)
            per_scope[scope] = (kept, cell.detection_strata(scope))
        for sp in SPEEDS:
            row = [tex_escape(cell.label) if sp == SPEEDS[0] else "", sp]
            for scope in SCOPES:
                kept, strata = per_scope[scope]
                keys = [k for k in kept if k[1] == sp]
                for m in ("recall", "precision"):
                    used = strata_in_range(kept, strata, keys, m)
                    if used:
                        lo, hi = interval_range([strata[k][m] for k in used])
                        row.append("%s--%s (%d/%d)" % (fmt_p(lo), fmt_p(hi), len(used), len(keys)))
                    else:
                        row.append("%s (0/%d)" % (NO_VALUE, len(keys)))
            lines.append(" & ".join(row) + " \\\\\n")
    lines += ["\\bottomrule\n", "\\end{tabular}\n", "\\end{table}\n"]
    return "".join(lines)


def table_session(cells):
    lines = [GENERATED_NOTE,
             "\\begin{sidewaystable}[p]\n",
             "\\caption{Per-session agreement per cell and speed, primary scope: the difference of \\texttt{dwell\\_ms} "
             "from the duration of the reference session (bias with its interval, limits of agreement, median absolute "
             "difference), the agreement of \\texttt{abandon} with the outcome of the session (raw agreement and kappa), "
             "and the exact agreement of \\texttt{nav} with the arrow presses sent; Pairs is the number of matched "
             "sessions; " + NO_VALUE + ": no value in the result file}\n",
             "\\label{tab:session}\n",
             "\\begin{tabular}{L{0.14}L{0.07}L{0.07}L{0.17}L{0.15}L{0.08}L{0.11}L{0.12}L{0.09}}\n",
             "\\toprule\n",
             "Cell & Speed & Pairs & Bias (ms) & Limits (ms) & Median absolute difference (ms) & "
             "\\texttt{abandon} agreement & "
             "\\texttt{abandon} kappa & \\texttt{nav} exact \\\\\n",
             "\\midrule\n"]
    for cell in cells:
        sp = cell.speed_sessions(PRIMARY_SCOPE)
        for i, s in enumerate(SPEEDS):
            if s not in sp:
                continue
            e = sp[s]
            dw, ba = e["dwell"], e["dwell"]["bland_altman"]
            ab, nav = e["abandon"], e["nav"]
            row = [tex_escape(cell.label) if i == 0 else "", s, fmt_int(dw["n"]),
                   est_ci(ba["bias"], dw["bias_ci"][0], dw["bias_ci"][1], fmt_ms),
                   "%s, %s" % (fmt_ms(ba["loa_lo"]), fmt_ms(ba["loa_hi"])),
                   fmt_ms(dw["mae"]),
                   est_ci(ab["agree"], ab["agree_ci"][0], ab["agree_ci"][1]),
                   est_ci(ab["kappa"], ab["kappa_ci"][0], ab["kappa_ci"][1]),
                   est_ci(nav["exact"], nav["exact_ci"][0], nav["exact_ci"][1])]
            lines.append(" & ".join(row) + " \\\\\n")
    lines += ["\\bottomrule\n", "\\end{tabular}\n", "\\end{sidewaystable}\n"]
    return "".join(lines)


def table_strata(cell, d10=None):
    """One landscape long table per scope (the supplement loads pdflscape and longtable). The last column is the merge
    rate of the corrected analysis of deviation D10, next to the registered one."""
    lines = [GENERATED_NOTE]
    for scope in SCOPES:
        name = "the primary scope (\\texttt{%s})" % tex_escape(scope) if scope == PRIMARY_SCOPE else \
            "all trials (\\texttt{%s})" % tex_escape(scope)
        lines += ["\\begin{landscape}\n", "{\\footnotesize\n",
                  "\\begin{longtable}{L{0.08}L{0.06}L{0.07}L{0.08}L{0.06}L{0.17}L{0.17}L{0.10}L{0.10}L{0.10}}\n",
                  "\\caption{Detection per stratum in %s, cell %s (definition \\texttt{%s}, comparison \\texttt{%s}), "
                  "with Wilson intervals. Trials: trials kept in the scope; Sessions and Rows: the reference sessions "
                  "and the session rows of the stratum that entered the matching; Merge rate: as registered; "
                  "Corrected: the merge rate of the corrected analysis of deviation D10%s; %s: no value (no "
                  "denominator, or a numerator above the denominator, deviation D10)}\\label{tab:strata-%s-%s}\\\\\n" % (
                      name, tex_escape(cell.label), tex_escape(cell.definition), tex_escape(PRIMARY_COMPARISON),
                      "" if d10 is not None else " (not computed for this cell)", NO_VALUE, cell.label, scope),
                  "\\toprule\n",
                  "Scenario & Speed & Trials & Sessions & Rows & Recall & Precision & Split rate & Merge rate & "
                  "Corrected \\\\\n",
                  "\\midrule\n\\endhead\n"]
        kept, _, _ = cell.kept_trials(scope)
        strata = cell.detection_strata(scope)
        corrected = d10_strata(d10, scope) if d10 is not None else {}
        for k in sorted(kept, key=lambda k: (scenario_order(k[0]), SPEEDS.index(k[1]))):
            if k not in strata:
                why = "no trial in the scope" if kept[k] == 0 else "no session in the scope"
                lines.append("%s & %s & %s & \\multicolumn{7}{l}{%s} \\\\\n" % (k[0], k[1], fmt_int(kept[k]), why))
                continue
            st = strata[k]
            cor = fmt_p(corrected[k]["merge_rate"]["value"]) if k in corrected else NO_VALUE
            lines.append(" & ".join([k[0], k[1], fmt_int(kept[k]), fmt_int(st["n_gt"]), fmt_int(st["n_obs"]),
                                     ci_text(st["recall"]), ci_text(st["precision"]),
                                     fmt_p(st["split_rate"]["value"]), fmt_p(st["merge_rate"]["value"]), cor])
                         + " \\\\\n")
        lines += ["\\bottomrule\n", "\\end{longtable}\n", "}\n", "\\end{landscape}\n"]
    return "".join(lines)


def table_closed_set(cells, docs):
    """Table 11: the judgement of section 6.8 on the two sets of the rule, per cell and K, and the recommendation."""
    rec = recommend(docs)
    lines = [GENERATED_NOTE,
             "\\begin{sidewaystable}[p]\n",
             "\\caption{Closed-set identification for the two feature sets that keep no time: the accuracy (the maximum "
             "over the set and the sets derivable from it) with its Wilson interval and, descriptively, the interval "
             "that resamples blocks; a set is near chance at K when the upper end of the Wilson interval is at most "
             "2/K, and near chance for the rule when it is so at both K = 10 and K = 100. The recommendation is "
             "decided from the two macOS cells; the Windows judgement is reported as its qualification; %s: no value}\n"
             % NO_VALUE,
             "\\label{tab:closed-set}\n",
             "\\begin{tabular}{L{0.20}L{0.12}L{0.06}L{0.07}L{0.22}L{0.15}L{0.07}L{0.10}}\n",
             "\\toprule\n",
             "Cell & Feature set & K & Trials & Accuracy & Block interval & 2/K & Near chance \\\\\n",
             "\\midrule\n"]
    for cell in cells:
        doc = docs.get(cell.label)
        if doc is None:
            lines.append("%s & \\multicolumn{7}{l}{not measured} \\\\\n" % tex_escape(cell.label))
            continue
        first = True
        for f in RULE_SETS:
            for K in RULE_KS:
                r = doc["results"][str(K)][f]
                blk = r.get("acc_ci_block") or [None, None]
                lines.append(" & ".join([
                    tex_escape(cell.label) if first else "", "\\texttt{%s}" % tex_escape(f), fmt_int(K), fmt_int(r["n"]),
                    est_ci(r["acc"], r["acc_ci"][0], r["acc_ci"][1]),
                    "%s, %s" % (fmt_p(blk[0]), fmt_p(blk[1])) if blk[0] is not None else NO_VALUE,
                    fmt_p(2.0 / K), yes_no(near_chance_at(r, K))]) + " \\\\\n")
                first = False
    lines += ["\\midrule\n",
              "\\multicolumn{8}{l}{Recommendation from the two macOS cells: %s} \\\\\n" % (
                  {"recommended": "\\texttt{%s}" % tex_escape(rec["set"] or ""), "none": "none",
                   "not decided": "not decided (a macOS cell was not measured)"}[rec["status"]]),
              "\\bottomrule\n", "\\end{tabular}\n", "\\end{sidewaystable}\n"]
    return "".join(lines)


def table_closed_set_all(cells, docs):
    """Supplement: every feature set at every K per cell, and the raw accuracy per speed and per scenario."""
    lines = [GENERATED_NOTE, "\\section*{Closed-set identification}\n\\label{sec:supp-closed-set}\n\n",
             "Every feature set at every K, per cell, from the closed-set result files (deviation D8: every trial of "
             "%s left out). Accuracy is the maximum over the set and the sets derivable from it, with its source and "
             "its Wilson interval; Raw is the accuracy of the set alone with its Wilson interval; the speed and "
             "scenario columns give the raw accuracy, descriptively and without an interval. The feature sets that "
             "keep time are estimates only (section 6.8 of the registration).\n\n" % CLOSED_SET_SKIPPED]
    for cell in cells:
        doc = docs.get(cell.label)
        if doc is None:
            lines.append("Cell %s: not measured.\n\n" % tex_escape(cell.label))
            continue
        lines += ["\\begin{landscape}\n", "{\\footnotesize\n",
                  "\\begin{longtable}{L{0.13}L{0.06}L{0.06}L{0.20}L{0.12}L{0.18}L{0.07}L{0.06}L{0.06}L{0.06}}\n",
                  "\\caption{Closed set, cell %s: accuracy per feature set and K}\\label{tab:closed-set-%s}\\\\\n" % (
                      tex_escape(cell.label), cell.label),
                  "\\toprule\n",
                  "Feature set & K & Trials & Accuracy & Source & Raw & Mean rank & Slow & Mid & Fast \\\\\n",
                  "\\midrule\n\\endhead\n"]
        for f in CLOSED_SET_SETS:
            for K in CLOSED_SET_KS:
                r = doc["results"][str(K)][f]
                sp = r.get("by_speed") or {}
                lines.append(" & ".join(
                    ["\\texttt{%s}" % tex_escape(f), fmt_int(K), fmt_int(r["n"]),
                     est_ci(r["acc"], r["acc_ci"][0], r["acc_ci"][1]), "\\texttt{%s}" % tex_escape(r["acc_source"]),
                     est_ci(r["acc_raw"], r["acc_ci_raw"][0], r["acc_ci_raw"][1]),
                     NO_VALUE if r.get("mean_rank") is None else "%.2f" % r["mean_rank"]]
                    + [fmt_p((sp.get(s) or {}).get("acc")) for s in SPEEDS]) + " \\\\\n")
        lines += ["\\bottomrule\n", "\\end{longtable}\n", "}\n", "\\end{landscape}\n"]
        scen = sorted(set(s for K in CLOSED_SET_KS for f in CLOSED_SET_SETS
                          for s in (doc["results"][str(K)][f].get("by_scenario") or {})), key=scenario_order)
        lines += ["\\begin{landscape}\n", "{\\footnotesize\n",
                  "\\begin{longtable}{L{0.08}L{0.06}" + "L{0.14}" * len(CLOSED_SET_SETS) + "}\n",
                  "\\caption{Closed set, cell %s: raw accuracy per scenario}\\label{tab:closed-set-scenario-%s}\\\\\n" % (
                      tex_escape(cell.label), cell.label),
                  "\\toprule\n",
                  "Scenario & K & " + " & ".join("\\texttt{%s}" % tex_escape(f) for f in CLOSED_SET_SETS) + " \\\\\n",
                  "\\midrule\n\\endhead\n"]
        for K in CLOSED_SET_KS:
            for s in scen:
                row = [s, fmt_int(K)]
                for f in CLOSED_SET_SETS:
                    e = (doc["results"][str(K)][f].get("by_scenario") or {}).get(s) or {}
                    row.append("%s (%s)" % (fmt_p(e.get("acc")), fmt_int(e.get("n", 0))))
                lines.append(" & ".join(row) + " \\\\\n")
        lines += ["\\bottomrule\n", "\\end{longtable}\n", "}\n", "\\end{landscape}\n\n"]
    return "".join(lines)


def table_open_set(cells, docs):
    """The open set (section 6.8) per cell, attacker and knowledge of the length."""
    lines = [GENERATED_NOTE,
             "\\begin{sidewaystable}[p]\n",
             "{\\footnotesize\n",
             "\\caption{Open-set reconstruction per cell and attacker: character error rate (CER) of the attack and of "
             "the prior-only baseline, the gain (baseline CER minus attack CER) and the gain over the shuffled control "
             "(the CER of another trial's decoding minus the attack's), each with a block-clustered 95\\%% percentile "
             "interval. K1 holds out whole works, K1+ splits the corpus by phrase; the baseline knows the number of "
             "segments or the true length. Undecodable: trials for which no string fits; %s: no value}\n" % NO_VALUE,
             "\\label{tab:open-set}\n",
             "\\begin{tabular}{L{0.14}L{0.11}L{0.10}L{0.06}L{0.13}L{0.13}L{0.12}L{0.11}L{0.10}}\n",
             "\\toprule\n",
             "Cell & Attacker & Length known & Trials & CER & Baseline CER & Gain & Gain over shuffled & "
             "Undecod\\-able \\\\\n",
             "\\midrule\n"]
    for cell in cells:
        doc = docs.get(cell.label)
        if doc is None:
            lines.append("%s & \\multicolumn{8}{l}{not measured} \\\\\n" % tex_escape(cell.label))
            continue
        first = True
        for split, model, label in OPEN_SET_ATTACKERS:
            for j, (li, li_label) in enumerate(OPEN_SET_LENGTHS):
                r = doc["splits"][split][li]
                a, b, g, sh = r[model], r["baseline"][model], r["gain"][model], r["shuffled"][model]
                lines.append(" & ".join([
                    tex_escape(cell.label) if first else "", label if j == 0 else "", li_label, fmt_int(r["n"]),
                    est_ci(a["cer"], a["cer_ci"][0], a["cer_ci"][1]), est_ci(b["cer"], b["cer_ci"][0], b["cer_ci"][1]),
                    est_ci(g["gain"], g["gain_ci"][0], g["gain_ci"][1], fmt_signed),
                    est_ci(sh["gain_vs_shuffled"], sh["gain_vs_shuffled_ci"][0], sh["gain_vs_shuffled_ci"][1],
                           fmt_signed),
                    fmt_int(a["n_undecodable"])]) + " \\\\\n")
                first = False
    lines += ["\\bottomrule\n", "\\end{tabular}\n", "}\n", "\\end{sidewaystable}\n"]
    return "".join(lines)


def table_cost(e3):
    """Table 12: runtime cost per system and condition, never reduced to one figure; the systems are not compared."""
    lines = [GENERATED_NOTE,
             "\\begin{sidewaystable}[p]\n",
             "\\caption{Runtime cost of the logger per system and condition: CPU of the logger (one core is 100) over "
             "the samples, its final resident memory (macOS) or working set (Windows) and the least-squares slope of "
             "it. The samplers of the two systems measure differently, so the values are read within each system and "
             "not compared between systems; %s: not measured, or not to be quoted (section 6.10)}\n" % NO_VALUE,
             "\\label{tab:cost}\n",
             "\\begin{tabular}{L{0.10}L{0.09}L{0.18}L{0.07}L{0.09}L{0.10}L{0.10}L{0.07}L{0.10}L{0.10}}\n",
             "\\toprule\n",
             "System & Condition & Status & Mean & Median & 95th percentile & Maximum & Hours & Memory (MB) & "
             "Slope (MB/h) \\\\\n",
             "\\midrule\n"]
    for system in ("macos", "windows"):
        src, conds = e3.get(system, (None, {}))
        for i, c in enumerate(E3_CONDITIONS):
            s = conds.get(c)
            head = [{"macos": "macOS", "windows": "Windows"}[system] if i == 0 else "", c]
            if s is None:
                lines.append(" & ".join(head + ["not measured"] + [NO_VALUE] * 7) + " \\\\\n")
                continue
            ok = e3_quotable(system, c, s)
            status = s["status"] if ok or s["status"] != "measured" else "insufficient (every CPU sample is zero)"
            if ok and s["cpu_all_zero"]:
                status += " (every CPU sample is zero)"
            cpu = s["cpu"] or {}
            row = head + [status] + [fmt_cpu(cpu.get(m)) if ok else NO_VALUE for m in ("mean", "median", "p95", "max")]
            row += ["%.2f" % s["hours"] if ok and s["hours"] is not None else NO_VALUE,
                    "%.1f" % s["rss_final_mb"] if ok and s["rss_final_mb"] is not None else NO_VALUE,
                    fmt_cpu(s["rss_slope_mb_per_h"]) if ok else NO_VALUE]
            lines.append(" & ".join(row) + " \\\\\n")
    lines += ["\\bottomrule\n", "\\end{tabular}\n", "\\end{sidewaystable}\n"]
    return "".join(lines)


def _agreement_row(e, ms):
    """Texts, bias, limits of agreement and ICC(A,1) of one per-text measure, each with its interval."""
    sg = lambda x: fmt_signed(x, ms)
    ba = e["bland_altman"]
    return [fmt_int(e["n"]), est_ci(ba["bias"], e["bias_ci"][0], e["bias_ci"][1], sg),
            est_ci(ba["loa_lo"], e["loa_lo_ci"][0], e["loa_lo_ci"][1], sg),
            est_ci(ba["loa_hi"], e["loa_hi_ci"][0], e["loa_hi_ci"][1], sg),
            est_ci(e["icc21"], e["icc21_ci"][0], e["icc21_ci"][1], fmt_signed)]


def _agreement_rows(cell, scope, first_col=None):
    """Rows of measure and speed; with first_col, a first column that names the cell on the first row."""
    lines = []
    by = cell.l2[scope]["agreement_by_stratum"]
    first = True
    for m, label, ms in L2_MEASURES:
        for i, s in enumerate(SPEEDS):
            e = (by.get(s) or {}).get(m)
            head = ([first_col if first else ""] if first_col is not None else []) + [label if i == 0 else "", s]
            first = False
            if e is None:
                lines.append(" & ".join(head) + " & \\multicolumn{5}{l}{no text in the scope} \\\\\n")
                continue
            lines.append(" & ".join(head + _agreement_row(e, ms)) + " \\\\\n")
    return lines


AGREEMENT_HEAD = ("Speed & Texts & Bias & Lower limit & Upper limit & ICC(A,1) \\\\\n")


def table_text_agreement(cells):
    """Table 10: per-text agreement of the four measures per cell and speed, primary scope."""
    lines = [GENERATED_NOTE,
             "\\begin{sidewaystable}[p]\n",
             "{\\footnotesize\n",
             "\\caption{Per-text agreement per cell, measure and speed, primary scope: bias and limits of agreement of the "
             "per-text difference (observation minus reference) and ICC(A,1), each with a 95\\%% interval that resamples "
             "blocks; Texts is the number of texts with a value on both sides. An estimate printed without an interval "
             "has its interval withheld (the reason is in the result file); %s: no value. The values hold for this "
             "design's numbers of trials per text and are not compared between speeds}\n" % NO_VALUE,
             "\\label{tab:text-agreement}\n",
             "\\begin{tabular}{L{0.15}L{0.15}L{0.06}L{0.06}L{0.15}L{0.15}L{0.15}L{0.13}}\n",
             "\\toprule\n",
             "Cell & Measure & " + AGREEMENT_HEAD,
             "\\midrule\n"]
    for cell in cells:
        lines += _agreement_rows(cell, PRIMARY_SCOPE, tex_escape(cell.label))
    lines += ["\\bottomrule\n", "\\end{tabular}\n", "}\n", "\\end{sidewaystable}\n"]
    return "".join(lines)


def text_agreement_supplement(cells):
    """Supplement: per-text agreement over all trials, the values pooled over speeds and the mixtures of speeds in
    both scopes, and the per-trial differences per scenario and speed in the primary scope."""
    lines = [GENERATED_NOTE, "\\section*{Per-text agreement and per-trial differences}\n\\label{sec:supp-text}\n\n",
             "Generated from the result files of question 3. The values pooled over speeds are given for comparison "
             "only, because a difference in level between speeds inflates a pooled ICC. The mixtures weight the speeds "
             "(slow, mid, fast) as stated. The per-trial differences (observation minus reference) are given per "
             "scenario and speed with the mean on each side, so that the scenarios can be weighted differently; the "
             "views that leave out the trials of the carry layers need the layers of the prediction and are not "
             "computed for the Windows cell.\n\n"]
    for cell in cells:
        name = tex_escape(cell.label)
        lines += ["\\begin{landscape}\n", "{\\footnotesize\n",
                  "\\begin{longtable}{L{0.14}L{0.11}L{0.06}L{0.12}L{0.14}L{0.14}L{0.14}L{0.14}}\n",
                  "\\caption{Per-text agreement pooled over speeds and the bias in three mixtures of speeds (weights "
                  "of slow, mid and fast), cell %s}\\label{tab:text-pooled-%s}\\\\\n" % (name, cell.label),
                  "\\toprule\n",
                  "Measure & Scope & Texts & ICC(A,1), pooled & Bias, pooled & "
                  + " & ".join("Bias, %s" % w for _, w, _ in L2_MIXTURES) + " \\\\\n",
                  "\\midrule\n\\endhead\n"]
        for m, label, ms in L2_MEASURES:
            sg = lambda x, ms=ms: fmt_signed(x, ms)
            for j, scope in enumerate(SCOPES):
                e = cell.l2[scope]["agreement"][m]
                mixes = l2_mixtures(cell, scope)
                mix = [est_ci(mixes[key]["bias"][m], mixes[key]["bias_ci"][m][0], mixes[key]["bias_ci"][m][1], sg)
                       for key, _, _ in L2_MIXTURES]
                lines.append(" & ".join([label if j == 0 else "", "\\texttt{%s}" % tex_escape(scope), fmt_int(e["n"]),
                                         est_ci(e["icc21"], e["icc21_ci"][0], e["icc21_ci"][1], fmt_signed),
                                         est_ci(e["bland_altman"]["bias"], e["bias_ci"][0], e["bias_ci"][1], sg)]
                                        + mix) + " \\\\\n")
        lines += ["\\bottomrule\n", "\\end{longtable}\n", "}\n", "\\end{landscape}\n\n"]
        lines += ["\\begin{landscape}\n", "{\\footnotesize\n",
                  "\\begin{longtable}{L{0.20}L{0.06}L{0.07}L{0.17}L{0.17}L{0.17}L{0.15}}\n",
                  "\\caption{Per-text agreement per measure and speed over all trials (\\texttt{all\\_trials}), cell "
                  "%s}\\label{tab:text-all-%s}\\\\\n" % (name, cell.label),
                  "\\toprule\n",
                  "Measure & " + AGREEMENT_HEAD,
                  "\\midrule\n\\endhead\n"]
        lines += _agreement_rows(cell, "all_trials")
        lines += ["\\bottomrule\n", "\\end{longtable}\n", "}\n", "\\end{landscape}\n\n"]
        for view, title in L2_VIEWS:
            v = cell.l2[PRIMARY_SCOPE][view]
            if v is None:
                lines.append("Cell %s, %s: not computed for this cell (no layers of the prediction).\n\n" % (name, title))
                continue
            lines += ["\\begin{landscape}\n", "{\\footnotesize\n",
                      "\\begin{longtable}{L{0.08}L{0.06}L{0.06}" + "L{0.26}" * len(L2_TRIAL_MEASURES) + "}\n",
                      "\\caption{Per-trial differences per scenario and speed, primary scope, %s, cell %s: mean "
                      "difference with a block-bootstrap interval (mean of the observation; mean of the reference)}"
                      "\\label{tab:text-%s-%s}\\\\\n" % (title, name, view.replace("_", "-"), cell.label),
                      "\\toprule\n",
                      "Scenario & Speed & Trials & " + " & ".join(t for _, t, _ in L2_TRIAL_MEASURES) + " \\\\\n",
                      "\\midrule\n\\endhead\n"]
            for st in sorted(v["by_stratum"], key=lambda st: (scenario_order(st["stratum"]["scenario"]),
                                                             SPEEDS.index(st["stratum"]["speed"]))):
                k = stratum_key(st["stratum"])
                if st["status"] != "ok":
                    lines.append("%s & %s & %s & \\multicolumn{%d}{l}{%s} \\\\\n" % (
                        k[0], k[1], fmt_int(st["n_trials"]), len(L2_TRIAL_MEASURES),
                        "no trial" if st["status"] == "no_trial" else tex_escape(st["status"])))
                    continue
                row = [k[0], k[1], fmt_int(st["n_trials"])]
                for m, _, ms in L2_TRIAL_MEASURES:
                    e = st[m]
                    row.append("%s (%s; %s)" % (
                        est_ci(e["diff_mean"], e["diff_ci"][0], e["diff_ci"][1], lambda x: fmt_signed(x, ms)),
                        fmt_signed(e["obs_mean"], ms), fmt_signed(e["gt_mean"], ms)))
                lines.append(" & ".join(row) + " \\\\\n")
            lines += ["\\bottomrule\n", "\\end{longtable}\n", "}\n", "\\end{landscape}\n\n"]
    return "".join(lines)


def values_tex(values):
    lines = [GENERATED_NOTE, "% Read with \\rv{<key>}; the source of each value is in values.json.\n"]
    for k in sorted(values):
        lines.append("\\expandafter\\def\\csname rv@%s\\endcsname{%s}\n" % (k, values[k]["text"]))
    return "".join(lines)


def build(results_dir):
    """{file name: bytes} of every generated file."""
    found = find_cells(results_dir)
    cells = [Cell(*f) for f in found]
    docs = dict((c.label, read_closed_set(c)) for c in cells)
    open_docs = dict((c.label, read_open_set(c)) for c in cells)
    e3 = read_e3_all(results_dir)
    d10 = dict((c.label, read_d10(results_dir, c)) for c in cells)
    values = {}
    for cell in cells:
        values.update(abstract_values(cell))
        values.update(d10_values(cell, d10[cell.label]))
        values.update(l2_values(cell))
        values.update(open_set_values(cell, open_docs[cell.label]))
    values.update(closed_set_values(cells, docs))
    values.update(e3_values(e3))
    files = {
        "values.json": (json.dumps({"min_trials": MIN_TRIALS, "cells": [c.label for c in cells], "values": values},
                                   ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf-8"),
        "values.tex": values_tex(values).encode("utf-8"),
        "table-detection.tex": table_detection(cells).encode("utf-8"),
        "table-session.tex": table_session(cells).encode("utf-8"),
        "table-closed-set.tex": table_closed_set(cells, docs).encode("utf-8"),
        "table-open-set.tex": table_open_set(cells, open_docs).encode("utf-8"),
        "table-cost.tex": table_cost(e3).encode("utf-8"),
        "closed-set-all.tex": table_closed_set_all(cells, docs).encode("utf-8"),
        "table-text-agreement.tex": table_text_agreement(cells).encode("utf-8"),
        "text-agreement.tex": text_agreement_supplement(cells).encode("utf-8"),
    }
    strata = [GENERATED_NOTE, "\\section*{Detection per stratum}\n\\label{sec:supp-strata}\n\n",
              "The tables below are generated from the result files of the analysis. The cells whose result files were "
              "not available when the tables were generated are: %s.\n\n" % (
                  ", ".join(tex_escape(c) for c in EXPECTED_CELLS if c not in [x.label for x in cells]) or "none")]
    for cell in cells:
        strata.append(table_strata(cell, d10[cell.label]).replace(GENERATED_NOTE, ""))
    files["detection-strata.tex"] = "".join(strata).encode("utf-8")
    return files


def write_or_check(files, out_dir, check):
    if check:
        differ = []
        for name, data in sorted(files.items()):
            p = os.path.join(out_dir, name)
            if not os.path.isfile(p):
                differ.append(name + " (missing)")
                continue
            with open(p, "rb") as f:
                if f.read() != data:
                    differ.append(name)
        if differ:
            print("results_tables.py: out of date with the result files: %s" % ", ".join(differ), file=sys.stderr)
            return 1
        print("results_tables.py: %d files up to date" % len(files))
        return 0
    os.makedirs(out_dir, exist_ok=True)
    for name, data in sorted(files.items()):
        with open(os.path.join(out_dir, name), "wb") as f:
            f.write(data)
    print("results_tables.py: wrote %d files to %s" % (len(files), out_dir))
    return 0


# ---------------------------------------------------------------- selftest


def _stratum(scenario, speed, n_gt, x, lo, hi):
    e = lambda: {"value": float(x) / n_gt if n_gt else None, "lo": lo, "hi": hi, "n": n_gt, "x": x}
    zero = {"value": 0.0, "lo": 0.0, "hi": 0.1, "n": n_gt, "x": 0}
    return {"stratum": {"cell": "c", "scenario": scenario, "speed": speed}, "n_gt": n_gt, "n_obs": n_gt,
            "recall": e(), "precision": e(), "split_rate": zero, "merge_rate": zero}


def _agreement(bias, ms):
    """A per-text agreement entry with distinct lower and upper limits (so that swapping them shows)."""
    lo, hi = (bias - 900.0, bias + 700.0) if ms else (bias - 0.25, bias + 0.125)
    return {"n": 40, "bland_altman": {"bias": bias, "loa_lo": lo, "loa_hi": hi, "n": 40, "sd": 1.0},
            "bias_ci": [bias - 1.0, bias + 1.0] if ms else [bias - 0.01, bias + 0.01], "bias_ci_status": "ok",
            "loa_lo_ci": [lo - 1.0, lo + 1.0] if ms else [lo - 0.01, lo + 0.01], "loa_lo_ci_status": "ok",
            "loa_hi_ci": [hi - 1.0, hi + 1.0] if ms else [hi - 0.01, hi + 0.01], "loa_hi_ci_status": "ok",
            "icc21": 0.75, "icc21_ci": [0.5, 0.875], "icc21_ci_status": "ok"}


def _fixture(tmp, label="windows-test", sub="windows"):
    """A synthetic Windows cell: S1 keeps 75, 30 and 29 trials (mid is at the minimum, slow under it), S2 keeps 0."""
    d = os.path.join(tmp, sub)
    os.makedirs(d)
    prim = {"comparison": PRIMARY_COMPARISON, "scope": PRIMARY_SCOPE}

    def det_scope(strata, carry):
        return {"metrics": {"by_stratum": strata + [{"stratum": {"cell": "c", "scenario": None, "speed": None},
                                                      "n_gt": 0, "n_obs": 3}]},
                "excluded": {"trials": {"by_type": {"carry_over": carry}, "n": carry}},
                "config": {"theta": 0.5}}

    det_u = [_stratum("S1", "fast", 75, 70, 0.85, 0.97), _stratum("S1", "mid", 30, 22, 0.60, 0.86),
             _stratum("S1", "slow", 29, 20, 0.10, 0.99)]
    det_a = [_stratum("S1", "fast", 75, 70, 0.84, 0.96), _stratum("S1", "mid", 75, 60, 0.70, 0.88),
             _stratum("S1", "slow", 75, 50, 0.55, 0.77), _stratum("S2", "fast", 75, 75, 0.95, 1.0),
             _stratum("S2", "mid", 75, 75, 0.95, 1.0), _stratum("S2", "slow", 75, 0, 0.0, 0.049)]
    # S2 slow over all trials: no session row, so precision and the merge rate have no value; recall is 0.
    none = {"value": None, "lo": None, "hi": None, "n": 0, "x": 0}
    det_a[-1]["precision"], det_a[-1]["merge_rate"], det_a[-1]["n_obs"] = dict(none), dict(none), 0

    def l2_scope(kept, oos, excl):
        bs = []
        diff = {"diff_mean": -0.5, "diff_ci": [-0.75, -0.25], "diff_ci_status": "ok", "diff_sd": 1.0, "gt_mean": 2.0,
                "obs_mean": 1.5}
        for (sc, sp), n in kept.items():
            st = {"stratum": {"scenario": sc, "speed": sp}, "n_trials": n, "status": "ok" if n else "no_trial",
                  "trials_not_used": {"excluded": excl.get((sc, sp), 0), "not_run": 0,
                                      "out_of_scope": oos.get((sc, sp), 0)}}
            if n:
                st.update({"n_conversions": dict(diff), "dwell_sum_ms": dict(diff, diff_mean=-1234.4,
                                                                             diff_ci=[-1500.0, -900.0]),
                           "n_cancelled": dict(diff)})
            bs.append(st)
        agr = dict((m, _agreement(-1234.4 if ms else -0.0125, ms)) for m, _, ms in L2_MEASURES)
        mixes = dict((name, {"weights": dict(zip(SPEEDS, w)), "bias": dict((m, -0.01) for m, _, _ in L2_MEASURES),
                             "bias_ci": dict((m, [-0.02, 0.0]) for m, _, _ in L2_MEASURES),
                             "bias_ci_status": dict((m, "ok") for m, _, _ in L2_MEASURES)})
                     for name, _, w in L2_MIXTURES)
        by_speed = dict((s, dict(agr)) for s in ("mid", "fast"))
        # slow: the interval of the ICC withheld, and no text for the abandonment rate
        slow = dict(agr)
        slow["conversions_per_trial"] = dict(agr["conversions_per_trial"], icc21_ci=[None, None],
                                             icc21_ci_status="undefined in a resample")
        del slow["abandon_rate"]
        by_speed["slow"] = slow
        return {"per_trial": {"by_stratum": bs, "n_trials": sum(kept.values()),
                              "trials_not_used": {"excluded": sum(excl.values()), "not_run": 0,
                                                  "out_of_scope": sum(oos.values())}},
                "per_trial_uncontaminated": None, "per_trial_layer_none": None,
                "agreement": agr, "agreement_by_stratum": by_speed,
                "mixture_bias": {"mixtures": mixes, "by_stratum": {}}}

    keys = [("S1", "fast"), ("S1", "mid"), ("S1", "slow"), ("S2", "fast"), ("S2", "mid"), ("S2", "slow")]
    excl = {("S1", "mid"): 1}
    kept_u = {("S1", "fast"): 75, ("S1", "mid"): 30, ("S1", "slow"): 29, ("S2", "fast"): 0, ("S2", "mid"): 0,
              ("S2", "slow"): 0}
    oos_u = {("S1", "mid"): 44, ("S1", "slow"): 46, ("S2", "fast"): 75, ("S2", "mid"): 75, ("S2", "slow"): 75}
    kept_a = dict((k, 75) for k in keys)
    kept_a[("S1", "mid")] = 74

    def l1_scope(biases):
        out = []
        for sp, (b, lo, hi) in biases.items():
            out.append({"stratum": {"cell": "c", "speed": sp},
                        "dwell": {"bias_ci": [lo, hi], "bland_altman": {"bias": b, "loa_lo": b - 900, "loa_hi": b + 900,
                                                                          "n": 50, "sd": 450},
                                  "mae": 300.0, "n": 50},
                        "abandon": {"agree": 0.9, "agree_ci": [0.8, 0.95], "kappa": None, "kappa_ci": [None, None]},
                        "nav": {"exact": 1.0, "exact_ci": [0.93, 1.0], "n": 50}})
        return {"metrics": {"by_speed": out}}

    cells_det = {"windows_def": {PRIMARY_COMPARISON: {"under_limit": det_scope(det_u, 1), "all_trials": det_scope(det_a, 1)}}}
    cells_l1 = {"windows_def": {PRIMARY_COMPARISON: {
        "under_limit": l1_scope({"slow": (-900.4, -1050.6, -800.2), "mid": (-500.0, -600.0, -400.0),
                                 "fast": (-100.0, -150.0, -49.5)}),
        "all_trials": l1_scope({"slow": (-2000.0, -2500.0, -1500.0), "mid": (-500.0, -600.0, -400.0),
                                "fast": (-100.0, -150.0, -50.0)})}}}
    cells_l2 = {"windows_def": {PRIMARY_COMPARISON: {"under_limit": l2_scope(kept_u, oos_u, excl),
                                                     "all_trials": l2_scope(kept_a, {}, excl)}}}
    # over all trials another value, so that reading the wrong scope shows
    cells_l2["windows_def"][PRIMARY_COMPARISON]["all_trials"]["agreement_by_stratum"]["slow"]["mean_dwell_ms"] = \
        _agreement(-4321.0, True)
    for name, cells in (("e1_detection.json", cells_det), ("e1_l1.json", cells_l1), ("e1_l2.json", cells_l2)):
        with open(os.path.join(d, name), "wb") as f:
            f.write(json.dumps({"primary": prim, "cells": {label: cells}}).encode("utf-8"))
    return tmp


def _cs_doc(his=None, raw_his=None, n=100, skipped=True):
    """A closed-set result: the upper end of the Wilson interval of acc is his[(K, set)] (0.9 when absent, far from
    chance); that of acc_raw is raw_his[(K, set)] (the same as acc when absent)."""
    his, raw_his = his or {}, raw_his or {}
    res = {}
    for K in CLOSED_SET_KS:
        res[str(K)] = {}
        for f in CLOSED_SET_SETS:
            hi = his.get((K, f), 0.9)
            rhi = raw_his.get((K, f), hi)
            lo = 0.0 if hi is None else max(0.0, hi - 0.01)
            res[str(K)][f] = {"acc": None if hi is None else lo, "acc_ci": [None if hi is None else lo, hi],
                              "acc_source": f, "acc_raw": None if rhi is None else max(0.0, rhi - 0.01),
                              "acc_ci_raw": [None if rhi is None else max(0.0, rhi - 0.01), rhi],
                              "acc_ci_block": [lo, hi], "acc_ci_raw_block": [lo, rhi], "ci_block_status": "ok",
                              "chance": 1.0 / K, "n": 0 if hi is None else n, "n_skipped": 0, "mean_rank": 1.5,
                              "n_blocks": 3, "by_scenario": {"S1": {"acc": 0.5, "n": n // 2}, "S2": {"acc": 0.5, "n": n // 2}},
                              "by_speed": dict((s, {"acc": 0.5, "n": n // 3}) for s in SPEEDS)}
    doc = {"results": res, "alignment": {"n_blocks": 3, "n_blocks_unscored": 0, "n_trials": n, "n_trials_unscored": 0},
           "n_trials": n}
    if skipped:
        doc["skipped_scenarios"] = {CLOSED_SET_SKIPPED: 225}
    return doc


def _os_doc(drop=None):
    """An open-set result whose values differ per split and model, so that a mix-up of attackers shows."""
    cer = {("work", "K0"): 0.9, ("work", "K1"): 0.8, ("phrase", "K1"): 0.6, ("phrase", "K0"): 0.95}
    splits = {}
    for split in ("work", "phrase"):
        splits[split] = {}
        for li, _ in OPEN_SET_LENGTHS:
            r = {"n": 50, "baseline": {}, "gain": {}, "shuffled": {}}
            for model in ("K0", "K1"):
                c = cer[(split, model)]
                g = 1.0 - c
                r[model] = {"cer": c, "cer_ci": [c - 0.05, c + 0.05], "n_undecodable": 2}
                r["baseline"][model] = {"cer": 1.0, "cer_ci": [0.95, 1.05]}
                r["gain"][model] = {"gain": g, "gain_ci": [g - 0.05, g + 0.05]}
                r["shuffled"][model] = {"cer": 1.0, "cer_ci": [0.95, 1.05], "gain": 0.0, "gain_ci": [-0.05, 0.05],
                                        "gain_vs_shuffled": g + 0.01, "gain_vs_shuffled_ci": [g - 0.04, g + 0.06]}
            splits[split][li] = r
    if drop:
        del splits[drop[0]][drop[1]]
    return {"splits": splits, "alignment": {"n_blocks_unscored": 0, "n_trials_unscored": 0}}


def _near(sets, k10=0.2, k100=0.02):
    """The upper ends that put the sets near chance at K = 10 and K = 100, exactly at the bound by default."""
    out = {}
    for f in sets:
        out[(10, f)], out[(100, f)] = k10, k100
    return out


E3_FIXTURE = """== idle (samples.tsv)
rows: 960 usable, 0 with the process absent, 0 unreadable
floors used: at least 480 usable rows and 480 rows with a CPU value; window of at least 4.0 h
sampling interval (measured): median 30.0 s  max 31 s
cpu % (one core = 100): mean 1.23  median 1.00  p95 2.50  max 9.75
cpu_all_zero: {idle_zero}
presence transitions (present, absent, present): 0
resident memory: final 41.2 MB  slope 0.05 MB/h  over 8.00 h
status: measured
== working (samples.tsv)
rows: 300 usable, 0 with the process absent, 0 unreadable
floors used: at least 480 usable rows and 480 rows with a CPU value; window of at least 4.0 h
sampling interval (measured): median 30.0 s  max 31 s
cpu % (one core = 100): mean 3.21  median 3.00  p95 6.50  max 12.00
cpu_all_zero: {working_zero}
presence transitions (present, absent, present): 0
resident memory: final 45.0 MB  slope n/a MB/h  over 2.50 h
status: {working_status}
"""


def _selftest_rules(check):
    """Question 4 and question 5 on constructed inputs (no files)."""
    on_off_near = _near(RULE_SETS)
    docs = {MACOS_CELLS[0]: _cs_doc(on_off_near), MACOS_CELLS[1]: _cs_doc(on_off_near), WINDOWS_CELL: _cs_doc()}
    check("q4: the bound 2/K itself is near chance (at most), and of two sets near chance the more detailed "
          "(no_time) is recommended",
          recommend(docs) == {"status": "recommended", "set": "no_time"}, str(recommend(docs)))
    off = _near(RULE_SETS)
    off[(100, "no_time")] = 0.0201
    docs2 = {MACOS_CELLS[0]: _cs_doc(on_off_near), MACOS_CELLS[1]: _cs_doc(off)}
    check("q4: a set that is not near chance at K = 100 in one macOS cell falls to the coarser set",
          recommend(docs2) == {"status": "recommended", "set": "counts_only"}, str(recommend(docs2)))
    docs3 = {MACOS_CELLS[0]: _cs_doc(), MACOS_CELLS[1]: _cs_doc(on_off_near)}
    check("q4: near chance in only one macOS cell recommends nothing",
          recommend(docs3) == {"status": "none", "set": None}, str(recommend(docs3)))
    k1000 = _near(RULE_SETS)
    k1000[(1000, "no_time")] = 0.9
    docs4 = {MACOS_CELLS[0]: _cs_doc(k1000), MACOS_CELLS[1]: _cs_doc(k1000)}
    check("q4: K = 1,000 is descriptive and does not enter the rule",
          recommend(docs4)["set"] == "no_time", str(recommend(docs4)))
    raw_low = dict(((K, f), 0.001) for K in RULE_KS for f in RULE_SETS)
    docs5 = {MACOS_CELLS[0]: _cs_doc(None, raw_low), MACOS_CELLS[1]: _cs_doc(None, raw_low)}
    check("q4: the rule reads the interval of the reported accuracy (the maximum over coarser sets), not of the "
          "set alone", recommend(docs5)["status"] == "none", str(recommend(docs5)))
    docs6 = dict(docs)
    docs6[WINDOWS_CELL] = _cs_doc(on_off_near)
    docs6[MACOS_CELLS[1]] = _cs_doc()
    check("q4: the Windows cell does not decide the recommendation", recommend(docs6)["status"] == "none")
    docs7 = {MACOS_CELLS[0]: _cs_doc(on_off_near), WINDOWS_CELL: _cs_doc(on_off_near)}
    try:
        rec7 = recommend(docs7)
    except Exception as e:  # a missing cell must give "not decided", not an error
        rec7 = repr(e)
    check("q4: without both macOS cells nothing is recommended (not decided)",
          rec7 == {"status": "not decided", "set": None}, str(rec7))
    nan = _near(RULE_SETS)
    nan[(10, "no_time")] = None
    docs8 = {MACOS_CELLS[0]: _cs_doc(nan), MACOS_CELLS[1]: _cs_doc(on_off_near)}
    check("q4: a set without a value (no scored trial) is not near chance",
          near_chance(docs8[MACOS_CELLS[0]], "no_time") is None and recommend(docs8)["set"] == "counts_only",
          str(recommend(docs8)))
    v = closed_set_values([], docs)
    check("q4: the Windows judgement is the qualification of the recommended set",
          v["q4.windows.qualification"]["text"] == "does not hold on Windows"
          and v["q4.recommendation"]["text"] == "\\texttt{no\\_time}", str(v["q4.windows.qualification"]))
    v6 = closed_set_values([], docs6)
    check("q4: with nothing recommended, the Windows judgement of each set is reported",
          v6["q4.windows.qualification"]["text"].count("near chance on Windows: yes") == 2,
          v6["q4.windows.qualification"]["text"])
    tmp = tempfile.mkdtemp(prefix="results_tables_e3_")
    try:
        p = os.path.join(tmp, "e3.txt")
        with open(p, "wb") as f:
            f.write(E3_FIXTURE.format(idle_zero="false", working_zero="false",
                                      working_status="insufficient -- fewer than 480 usable rows").encode("utf-8"))
        e3 = {"macos": ("e3_macos.txt", read_e3(p))}
        vals = e3_values(e3)
        check("q5: a measured condition gives its mean CPU, an insufficient one is not quoted",
              vals["macos.e3.idle.cpu.mean"]["text"] == "1.23" and vals["macos.e3.working.cpu.mean"]["text"] == NO_VALUE
              and vals["windows.e3.idle.cpu.mean"]["text"] == NO_VALUE, str(vals))
        cost = table_cost(e3)
        check("q5: the table shows an insufficient condition without figures and a missing system as not measured",
              "working & insufficient & --" in cost and "Windows & idle & not measured" in cost, cost[-600:])
        with open(p, "wb") as f:
            f.write(E3_FIXTURE.format(idle_zero="true", working_zero="true", working_status="measured").encode("utf-8"))
        e3w = {"windows": ("windows/e3_windows.txt", read_e3(p))}
        vw = e3_values(e3w)
        cost_w = table_cost(e3w)
        check("q5: on Windows a working condition whose every CPU sample is zero is insufficient (section 10.9); "
              "an idle one is reported with the flag",
              vw["windows.e3.working.cpu.mean"]["text"] == NO_VALUE and vw["windows.e3.idle.cpu.mean"]["text"] == "1.23"
              and "insufficient (every CPU sample is zero)" in cost_w
              and "measured (every CPU sample is zero)" in cost_w, cost_w[-700:])
        with open(p, "wb") as f:
            f.write(E3_FIXTURE.replace("== working", "== busy").format(
                idle_zero="false", working_zero="false", working_status="measured").encode("utf-8"))
        try:
            read_e3(p)
            check("q5: negative: an unknown condition stops the script", False)
        except ValueError:
            check("q5: negative: an unknown condition stops the script", True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def selftest():
    fails, ran = [], []

    def check(name, cond, detail=""):
        ran.append(name)
        if not cond:
            fails.append(name)
            print("FAIL: %s %s" % (name, detail))

    _selftest_rules(check)

    tmp = tempfile.mkdtemp(prefix="results_tables_selftest_")
    try:
        _fixture(tmp)
        files = build(tmp)
        vals = json.loads(files["values.json"].decode("utf-8"))["values"]
        check("the cell under windows/ is found and read with windows_def", "windows-test.trials.total" in vals,
              str(sorted(vals)[:3]))
        check("the total counts every trial of the design (kept, excluded, out of scope)",
              vals["windows-test.trials.total"]["value"] == 75 * 6, str(vals["windows-test.trials.total"]))
        check("a stratum at the minimum of trials (30) is in the range; one under it (29) and strata without trials "
              "are left out",
              vals["windows-test.primary.recall.strata.used"]["value"] == 2
              and vals["windows-test.primary.recall.strata.left"]["value"] == 4,
              str((vals["windows-test.primary.recall.strata.used"], vals["windows-test.primary.recall.strata.left"])))
        check("the primary range is the lowest lower end to the highest upper end of the strata used",
              vals["windows-test.primary.recall.range"]["value"] == [0.60, 0.97]
              and vals["windows-test.primary.recall.range"]["text"] == "0.600--0.970",
              str(vals["windows-test.primary.recall.range"]))
        check("the range over all trials uses the strata of all trials, per measure: a stratum without a value of "
              "precision (no session row) stays in the range of recall (its recall of 0) and is left out of precision",
              vals["windows-test.all.recall.range"]["value"] == [0.0, 1.0]
              and vals["windows-test.all.precision.range"]["value"] == [0.55, 1.0]
              and vals["windows-test.all.recall.strata.left"]["value"] == 0
              and vals["windows-test.all.precision.strata.left"]["value"] == 1,
              str((vals["windows-test.all.recall.range"], vals["windows-test.all.precision.range"])))
        check("a stratum whose rates have no value is printed with the mark of no value, not dropped",
              "S2 & slow & 75 & 75 & 0 & 0.000 [0.000, 0.049] & %s" % NO_VALUE in files["detection-strata.tex"].decode("utf-8"))
        check("the fractions set aside by the scope and by carry-over are counts over the total",
              vals["windows-test.scope.setaside"]["value"] == [315, 450]
              and vals["windows-test.scope.setaside"]["text"] == "315 of 450 trials (70.0\\%)"
              and vals["windows-test.carryover"]["value"] == [1, 450], str(vals["windows-test.scope.setaside"]))
        check("the dwell-bias range spans the per-speed intervals, in whole milliseconds with a minus sign",
              vals["windows-test.primary.dwellbias.range"]["value"] == [-1050.6, -49.5]
              and vals["windows-test.primary.dwellbias.range"]["text"] == "$-$1,051 to $-$50~ms",
              str(vals["windows-test.primary.dwellbias.range"]))
        check("every value of questions 1 to 3 names its source file, and every value has a source",
              all(v["source"].startswith("windows/e1_") for k, v in vals.items()
                  if k.startswith("windows-test.") and ".q4." not in k and ".d10." not in k)
              and all(v["source"] for v in vals.values()))
        strata_tex = files["detection-strata.tex"].decode("utf-8")
        check("the supplement names the expected cells that were not available",
              all(c in strata_tex for c in EXPECTED_CELLS), strata_tex[:300])
        check("the per-stratum table states a stratum without sessions instead of leaving it out",
              "no trial in the scope" in strata_tex and "S2 & fast" in strata_tex)
        check("the generated files say that they are generated", all(
            data.decode("utf-8").startswith("% Generated") for n, data in files.items() if n.endswith(".tex")))
        t10 = files["table-text-agreement.tex"].decode("utf-8")
        check("q3: a duration is in whole milliseconds with a minus sign, and the bias, the lower and the upper limit "
              "and the ICC each come with their own interval",
              "Mean conversion time (ms) & slow & 40 & $-$1,234 [$-$1,235, $-$1,233] & $-$2,134 [$-$2,135, $-$2,133] "
              "& $-$534 [$-$535, $-$533] & 0.750 [0.500, 0.875] \\\\" in t10, t10[-1500:])
        row = [l for l in t10.splitlines() if "Conversions per trial & slow" in l]
        check("q3: an estimate whose interval is withheld is printed alone, not dropped",
              len(row) == 1 and row[0].endswith("& 0.750 \\\\"), str(row))
        check("q3: a measure with no text in the scope is stated",
              "Abandonment rate & slow & \\multicolumn{5}{l}{no text in the scope}" in t10)
        check("q3: proportions keep three decimals with a minus sign",
              "Fraction of time converting & slow & 40 & $-$0.01" in t10)
        sup = files["text-agreement.tex"].decode("utf-8")
        check("q3: the views that need the layers are stated as not computed for a Windows cell",
              sup.count("not computed for this cell (no layers of the prediction)") == 2, sup[:400])
        check("q3: the per-trial differences give the mean difference with its interval and the mean on each side, "
              "and a stratum without trials is stated",
              "$-$0.500 [$-$0.750, $-$0.250] (1.500; 2.000)" in sup and "\\multicolumn{3}{l}{no trial}" in sup)
        check("q3: the pooled values and the three mixtures are given for both scopes",
              sup.count("\\texttt{under\\_limit}") >= 4 and sup.count("\\texttt{all\\_trials}") >= 4
              and "Bias, 0.6/0.3/0.1" in sup and "Bias, equal" in sup)
        check("q3: the values for the text name their source",
              vals["windows-test.l2.mean_dwell_ms.slow.bias"]["text"] == "$-$1,234 [$-$1,235, $-$1,233]"
              and "agreement_by_stratum/slow/mean_dwell_ms" in vals["windows-test.l2.mean_dwell_ms.slow.bias"]["source"],
              str(vals.get("windows-test.l2.mean_dwell_ms.slow.bias")))
        p2 = os.path.join(tmp, "windows", "e1_l2.json")
        good = load(p2)
        bad = json.loads(json.dumps(good))
        bad["cells"]["windows-test"]["windows_def"][PRIMARY_COMPARISON]["all_trials"]["mixture_bias"]["mixtures"][
            "uniform"]["weights"]["slow"] = 0.5
        with open(p2, "wb") as f:
            f.write(json.dumps(bad).encode("utf-8"))
        try:
            build(tmp)
            check("q3: negative: a mixture whose weights are not those of section 6.7 stops the script", False)
        except ValueError:
            check("q3: negative: a mixture whose weights are not those of section 6.7 stops the script", True)
        with open(p2, "wb") as f:
            f.write(json.dumps(good).encode("utf-8"))
        check("the same input gives byte-identical output", build(tmp) == files)
        out = os.path.join(tmp, "out")
        check("writing exits 0", write_or_check(files, out, False) == 0)
        check("--check passes on the files just written", write_or_check(files, out, True) == 0)
        with open(os.path.join(out, "table-detection.tex"), "ab") as f:
            f.write(b"% edited\n")
        check("negative: --check fails when a table was edited by hand", write_or_check(files, out, True) == 1)
        os.remove(os.path.join(out, "values.tex"))
        check("negative: --check fails when a file is missing", write_or_check(files, out, True) == 1)
        check("q4: a cell without a closed-set file is reported as not measured",
              "windows-test & \\multicolumn{7}{l}{not measured}" in files["table-closed-set.tex"].decode("utf-8"))
        check("d10: without the corrected analysis the column says so",
              "(not computed for this cell)" in files["detection-strata.tex"].decode("utf-8"))
        cs = os.path.join(tmp, "windows", closed_set_name("windows-test"))
        with open(cs, "wb") as f:
            f.write(json.dumps(_cs_doc(skipped=False)).encode("utf-8"))
        try:
            build(tmp)
            check("q4: negative: a closed-set file that keeps S12 (not deviation D8) stops the script", False)
        except ValueError:
            check("q4: negative: a closed-set file that keeps S12 (not deviation D8) stops the script", True)
        with open(cs, "wb") as f:
            f.write(json.dumps(_cs_doc(_near(RULE_SETS))).encode("utf-8"))
        files_cs = build(tmp)
        t11 = files_cs["table-closed-set.tex"].decode("utf-8")
        check("q4: the table gives the judgement per set and K, and the recommendation is not decided without the "
              "macOS cells", "\\texttt{no\\_time} & 10 & 100 & " in t11 and t11.count("& yes \\\\") == 4
              and "not decided (a macOS cell was not measured)" in t11, t11[-900:])
        check("open set: a cell without a file is reported as not measured",
              "windows-test & \\multicolumn{8}{l}{not measured}" in files["table-open-set.tex"].decode("utf-8"))
        osp = os.path.join(tmp, "windows", open_set_name("windows-test"))
        with open(osp, "wb") as f:
            f.write(json.dumps(_os_doc(drop=("phrase", "true"))).encode("utf-8"))
        try:
            build(tmp)
            check("open set: negative: a missing split or length level stops the script", False)
        except ValueError:
            check("open set: negative: a missing split or length level stops the script", True)
        with open(osp, "wb") as f:
            f.write(json.dumps(_os_doc()).encode("utf-8"))
        files_os = build(tmp)
        tos = files_os["table-open-set.tex"].decode("utf-8")
        vos = json.loads(files_os["values.json"].decode("utf-8"))["values"]
        check("open set: K1+ is K1 with the corpus split by phrase, and the gain and the gain over the shuffled "
              "control are not interchanged",
              "& K1+ & number of segments & 50 & 0.600 [0.550, 0.650] & 1.000 [0.950, 1.050] & 0.400 [0.350, 0.450] "
              "& 0.410 [0.360, 0.460] & 2 \\\\" in tos
              and vos["windows-test.q4.open.K1plus.count.cer"]["text"] == "0.600 [0.550, 0.650]"
              and vos["windows-test.q4.open.K1.true.gainvsshuffled"]["text"] == "0.210 [0.160, 0.260]"
              and vos["windows-test.q4.open.K0.phrase.count.cer"]["text"] == "0.950 [0.900, 1.000]", tos[-1200:])
        os.remove(osp)
        d10d = os.path.join(tmp, "d10", "windows")
        os.makedirs(d10d)
        reg = load(os.path.join(tmp, "windows", "e1_detection.json"))
        cor = json.loads(json.dumps(reg))
        blk = cor["cells"]["windows-test"]["windows_def"][PRIMARY_COMPARISON]
        for scope in SCOPES:
            blk[scope]["config"]["merge_recount"] = "obs"
        blk["under_limit"]["metrics"]["by_stratum"][0]["merge_rate"] = {"value": 0.25, "lo": 0.1, "hi": 0.5, "n": 4,
                                                                         "x": 1}
        with open(os.path.join(d10d, "e1_detection.json"), "wb") as f:
            f.write(json.dumps(cor).encode("utf-8"))
        files_d = build(tmp)
        vd = json.loads(files_d["values.json"].decode("utf-8"))["values"]
        check("d10: the strata whose merge rate the corrected analysis changes are counted per scope, and the "
              "supplement shows the corrected rate next to the registered one",
              vd["windows-test.d10.primary.merge.differ"]["value"] == [1, 3]
              and vd["windows-test.d10.all.merge.differ"]["value"] == [0, 6]
              and "& 0.000 & 0.250 \\\\" in files_d["detection-strata.tex"].decode("utf-8"),
              str((vd.get("windows-test.d10.primary.merge.differ"), vd.get("windows-test.d10.all.merge.differ"))))
        del blk["all_trials"]["config"]["merge_recount"]
        with open(os.path.join(d10d, "e1_detection.json"), "wb") as f:
            f.write(json.dumps(cor).encode("utf-8"))
        try:
            build(tmp)
            check("d10: negative: corrected results without the switch stop the script", False)
        except ValueError:
            check("d10: negative: corrected results without the switch stop the script", True)
        shutil.rmtree(d10d)
        reg_blk = reg["cells"]["windows-test"]["windows_def"][PRIMARY_COMPARISON]
        reg_blk["under_limit"]["config"]["merge_recount"] = "obs"
        with open(os.path.join(tmp, "windows", "e1_detection.json"), "wb") as f:
            f.write(json.dumps(reg).encode("utf-8"))
        try:
            build(tmp)
            check("d10: negative: registered results that carry the switch stop the script", False)
        except ValueError:
            check("d10: negative: registered results that carry the switch stop the script", True)
        del reg_blk["under_limit"]["config"]["merge_recount"]
        with open(os.path.join(tmp, "windows", "e1_detection.json"), "wb") as f:
            f.write(json.dumps(reg).encode("utf-8"))
        # a primary that is not the registered one stops the script
        p = os.path.join(tmp, "windows", "e1_l1.json")
        doc = load(p)
        doc["primary"]["scope"] = "all_trials"
        with open(p, "wb") as f:
            f.write(json.dumps(doc).encode("utf-8"))
        try:
            build(tmp)
            check("negative: a result file whose primary scope differs stops the script", False)
        except ValueError:
            check("negative: a result file whose primary scope differs stops the script", True)
        empty = tempfile.mkdtemp(prefix="results_tables_empty_")
        try:
            files_e = build(empty)
            check("no result files: no cell, and the tables are written without rows",
                  json.loads(files_e["values.json"].decode("utf-8"))["cells"] == [])
        finally:
            shutil.rmtree(empty, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    n = len(ran)
    if fails:
        print("selftest failed: %d of %d checks" % (len(fails), n))
        return 1
    print("selftest OK (%d checks)" % n)
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description="Tables and values of the manuscript from the result files")
    ap.add_argument("--results", help="the results directory (experiment/results)")
    ap.add_argument("--out", help="the output directory (manuscript/generated)")
    ap.add_argument("--check", action="store_true", help="compare instead of writing; exit 1 when any file differs")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not (a.results and a.out):
        ap.print_usage(sys.stderr)
        return 2
    try:
        files = build(a.results)
    except (ValueError, KeyError, OSError) as e:
        print("results_tables.py: %s" % e, file=sys.stderr)
        return 2
    return write_or_check(files, a.out, a.check)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
