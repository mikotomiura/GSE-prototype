#!/usr/bin/env python3
# kit: selftest
"""End-to-end analysis of the first experiment: from run directories to the level-1 and level-2
agreement results and the detection results, in one command. Uses only the Python standard library.
Every stage is an existing module of this directory and is only called here, never reimplemented:
gt_sessions (ground-truth sessions), match (pairing and detection metrics), l1 (per-session
agreement) and l2 (aggregate agreement).

  pipeline.py --runs DIR [DIR ...] --config CFG.json --seed N --out RESULTS_DIR
  pipeline.py --runs-from LIST.md --config CFG.json --seed N --out RESULTS_DIR
  pipeline.py --synthetic DIR [--seed N]         write two synthetic run directories under DIR
  pipeline.py --check-deposit DIR [DIR ...]      refuse a run directory that is not safe to deposit
  pipeline.py --selftest                         fast default (a few seconds)

A run directory (written by the run-cell tool) holds plan.jsonl, oracle.jsonl, gt.jsonl, obs.jsonl and
run.json (the manifest, format run/1). The manifest records the SHA-256 of every log; a log that no
longer matches its recorded hash stops the run. A run whose manifest says aborted is left out of the
matching and is counted (its cell is listed under "runs" in every result file).

Step 0 (checks that run before any statistic). The gt and obs logs must pass the content-free
validator (kit/formats/validate_logs.py), the plan must pass the plan validator, the oracle must pass
the oracle validator, and the header of the observation log must declare the "key" and "ime_shadow"
channels among its capabilities. Any violation is listed and the run stops with exit status 1.

Stages, per run directory (one cell): ground-truth sessions from gt, oracle and plan; matching against
the observation log; level 1; level 2. The session definition follows the operating system in the plan
header (macos: macos_def, windows: windows_def). The label of a cell is the "label" of the cell in the
manifest, or its "os" when there is no label; two runs must not share a label.

Configuration CFG (JSON; keys starting with "_" are annotations and are not read):
  {"iou_min": 0.5, "obs_end_offset_ms": 0, "text_size_trials": 8, "bootstrap_B": 2000,
   "limit_ms": 20000, "mixtures": {...}, "gt_rules": "path/to/rules.json"}
Every key is optional except gt_rules, which is resolved relative to the configuration file. The seed is
a command-line argument (the experiment keeps it in one file) and is passed to every bootstrap.

Outputs (RESULTS_DIR): e1_l1.json, e1_l2.json and e1_detection.json. Each one carries the seed, the
SHA-256 of the configuration and of every input log, and the per-cell results. No path is written to
any of them, and identical inputs always give identical bytes (sorted keys, LF, UTF-8, no BOM).

Deposit check. Only run.json and the four logs are meant to be deposited. --check-deposit exits 1 when
any of the five files contains the absolute path of the home directory (either separator), the login
name of the current user (as a whole word, when it has at least three characters) or the absolute path
of this repository, and reports the file and line (never the value). The standard-error files are not
deposited and are not read.

Exit status: 0 on success; 1 when a check finds a violation; 2 when an input cannot be read, is
malformed or does not match its recorded hash, or when usage is incorrect.
"""
import argparse
import contextlib
import getpass
import hashlib
import importlib.util
import io
import json
import os
import random
import re
import shutil
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import gt_sessions  # noqa: E402  ground-truth sessions
import inject  # noqa: E402  synthetic observation rows with known errors
import l1  # noqa: E402  level 1
import l2  # noqa: E402  level 2
import match  # noqa: E402  pairing, detection metrics, file helpers

InputError = gt_sessions.InputError
KIT = os.path.dirname(_HERE)
LOG_NAMES = ("plan", "oracle", "gt", "obs")
LOG_FILES = {"plan": "plan.jsonl", "oracle": "oracle.jsonl", "gt": "gt.jsonl", "obs": "obs.jsonl"}
MANIFEST = "run.json"
RUN_FORMAT = "run/1"
DEPOSIT_FILES = (MANIFEST,) + tuple(LOG_FILES[n] for n in LOG_NAMES)
DEFINITION_OF_OS = {"macos": "macos_def", "windows": "windows_def"}
REQUIRED_CHANNELS = ("key", "ime_shadow")
CONFIG_KEYS = ("iou_min", "obs_end_offset_ms", "text_size_trials", "bootstrap_B", "limit_ms", "mixtures", "gt_rules")
MIN_NAME_LEN = 3


class CheckFailed(Exception):
    """One or more checks found a violation (exit status 1)."""

    def __init__(self, findings):
        Exception.__init__(self, "%d violation(s)" % len(findings))
        self.findings = findings


# ---------------------------------------------------------------- helpers

_TOOLS = {}


def _tool(name, *parts):
    """Load a module of the kit by file path (cached)."""
    if name not in _TOOLS:
        spec = importlib.util.spec_from_file_location("kit_" + name, os.path.join(KIT, *parts))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _TOOLS[name] = mod
    return _TOOLS[name]


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _jl(rows):
    return ("\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in rows) + "\n").encode("utf-8")


def _json_bytes(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _is_int(v):
    return type(v) is int


def repo_root():
    """The root of the repository that contains this kit (three levels above kit/)."""
    return os.path.dirname(os.path.dirname(KIT))


# ---------------------------------------------------------------- configuration

def parse_config(data, base_dir):
    """Parse the configuration bytes into a dict; gt_rules is resolved against base_dir."""
    obj = match._json_loads(match._decode(data, "config"), "config", True)
    if not isinstance(obj, dict):
        raise InputError("config: the top level must be an object")
    cfg = {"iou_min": 0.5, "obs_end_offset_ms": 0, "text_size_trials": 8, "bootstrap_B": 2000,
           "limit_ms": 20000, "mixtures": None, "gt_rules": None}
    for k, v in obj.items():
        if k.startswith("_"):
            continue
        if k not in CONFIG_KEYS:
            raise InputError("config: unknown key '%s'" % k)
        cfg[k] = v
    if not isinstance(cfg["gt_rules"], str) or not cfg["gt_rules"]:
        raise InputError("config: gt_rules (the path of the rule file) is required")
    cfg["gt_rules"] = os.path.normpath(os.path.join(base_dir, cfg["gt_rules"]))
    return cfg


def _stage_configs(cfg, seed, label):
    """The configuration bytes handed to each stage (the stages validate their own keys)."""
    def enc(d):
        return json.dumps(d, sort_keys=True).encode("utf-8")
    l2c = {"text_size_trials": cfg["text_size_trials"], "B": cfg["bootstrap_B"], "seed": seed}
    if cfg["mixtures"] is not None:
        l2c["mixtures"] = cfg["mixtures"]
    return {"match": enc({"iou_min": cfg["iou_min"], "obs_end_offset_ms": cfg["obs_end_offset_ms"], "cell": label}),
            "l1": enc({"B": cfg["bootstrap_B"], "seed": seed, "limit_ms": cfg["limit_ms"]}),
            "l2": enc(l2c)}


# ---------------------------------------------------------------- run directories

def load_run(run_dir):
    """Read a run directory. Returns {"dir", "manifest", "label", "aborted", "files"}; the logs are
    read (and checked against the recorded hashes) only when the run was not aborted."""
    mbytes = match._read(os.path.join(run_dir, MANIFEST), "run.json")
    m = match._json_loads(match._decode(mbytes, "run.json"), "run.json", True)
    if not isinstance(m, dict) or m.get("format") != RUN_FORMAT:
        raise InputError("run.json: not a %s manifest" % RUN_FORMAT)
    if type(m.get("aborted")) is not bool:
        raise InputError("run.json: aborted must be a boolean")
    cell = m.get("cell")
    if not isinstance(cell, dict):
        raise InputError("run.json: cell must be an object")
    label = cell.get("label") if isinstance(cell.get("label"), str) else cell.get("os")
    if not isinstance(label, str) or not match.CELL_RE.fullmatch(label):
        raise InputError("run.json: the cell needs a label (or an os) of the form %s" % match.CELL_RE.pattern)
    run = {"dir": run_dir, "manifest": m, "label": label, "aborted": m["aborted"], "files": {}, "sha": {}}
    outs = m.get("outputs")
    if not isinstance(outs, dict):
        raise InputError("run.json: outputs must be an object")
    for name in LOG_NAMES:
        rec = outs.get(name)
        if not isinstance(rec, dict):
            raise InputError("run.json: outputs.%s is missing" % name)
        run["sha"][name] = rec.get("sha256")
        if m["aborted"]:
            continue
        data = match._read(os.path.join(run_dir, LOG_FILES[name]), name)
        if rec.get("sha256") != _sha(data):
            raise InputError("%s: SHA-256 does not match run.json (the log changed after the run)" % LOG_FILES[name])
        run["files"][name] = data
    return run


def read_runs_list(path):
    """The run directories named in a list file: lines of the form '- run_dir: PATH' (relative paths are
    relative to the list file)."""
    text = match._decode(match._read(path, "runs list"), "runs list")
    base = os.path.dirname(os.path.abspath(path))
    out = []
    for line in text.split("\n"):
        m = re.match(r"^- run_dir:[ \t]*(\S.*?)[ \t\r]*$", line)
        if m:
            out.append(os.path.normpath(os.path.join(base, m.group(1))))
    return out


# ---------------------------------------------------------------- step 0

def check_run(run):
    """Step 0 for one run. Returns a list of 'file:line: message' findings (empty when clean)."""
    vl = _tool("validate_logs", "formats", "validate_logs.py")
    gp = _tool("generate_plan", "gen", "generate_plan.py")
    em = _tool("emit", "emit", "emit.py")
    name = os.path.basename(os.path.normpath(run["dir"]))
    out = []
    for kind in ("gt", "obs"):
        for ln, code, msg in vl.validate(kind, run["files"][kind]):
            out.append("%s/%s:%d: [%s] %s" % (name, LOG_FILES[kind], ln, code, msg))
    for ln, code, msg in gp.validate_plan(run["files"]["plan"]):
        out.append("%s/%s:%d: [%s] %s" % (name, LOG_FILES["plan"], ln, code, msg))
    for msg in em.validate_oracle(os.path.join(run["dir"], LOG_FILES["oracle"])):
        out.append("%s/%s: %s" % (name, LOG_FILES["oracle"], msg))
    first = run["files"]["obs"].split(b"\n", 1)[0]
    try:
        caps = json.loads(first.decode("utf-8")).get("capabilities")
    except (ValueError, AttributeError):
        caps = None
    declared = set()
    if isinstance(caps, dict):
        for k in ("unconditional", "threshold_gated", "config_gated"):
            if isinstance(caps.get(k), list):
                declared.update(x for x in caps[k] if isinstance(x, str))
    for ch in REQUIRED_CHANNELS:
        if ch not in declared:
            out.append("%s/%s:1: the header does not declare the '%s' channel in meta.capabilities" % (name, LOG_FILES["obs"], ch))
    return out


# ---------------------------------------------------------------- stages

def run_stages(run, cfg, rules_bytes, seed):
    """The four stages for one run. Returns the l1 / l2 / match output dicts (JSON-ready)."""
    f = run["files"]
    plan = match.parse_plan_strata(f["plan"])
    definition = DEFINITION_OF_OS[plan["os"]]
    sc = _stage_configs(cfg, seed, run["label"])
    sessions = gt_sessions.assemble(f["gt"], f["oracle"], rules_bytes, f["plan"])
    sess_bytes = gt_sessions.render(sessions)
    m_out = match.evaluate(sess_bytes, definition, f["obs"], f["plan"], f["oracle"], sc["match"])
    m_bytes = match.render(m_out)
    l1_out = l1.evaluate(m_bytes, sess_bytes, f["plan"], f["oracle"], sc["l1"])
    l2_out = l2.evaluate(m_bytes, sess_bytes, f["obs"], f["plan"], f["oracle"], sc["l2"])
    return l1_out, l2_out, m_out


def analyse(run_dirs, config_path, seed, out_dir):
    """The whole pipeline. Writes the three result files; raises CheckFailed / InputError."""
    if not _is_int(seed):
        raise InputError("seed must be an integer")
    cfg_bytes = match._read(config_path, "config")
    cfg = parse_config(cfg_bytes, os.path.dirname(os.path.abspath(config_path)))
    rules_bytes = match._read(cfg["gt_rules"], "rules")
    if not run_dirs:
        raise InputError("no run directory was given")
    runs = [load_run(d) for d in run_dirs]
    labels = [r["label"] for r in runs]
    if len(set(labels)) != len(labels):
        raise InputError("two runs share a cell label (give each cell a distinct label in run.json)")
    findings = []
    for r in runs:
        if not r["aborted"]:
            findings += check_run(r)
    if findings:
        raise CheckFailed(findings)
    used = sorted((r for r in runs if not r["aborted"]), key=lambda r: r["label"])
    listing = [{"cell": r["label"], "aborted": r["aborted"], "logs_sha256": r["sha"]}
               for r in sorted(runs, key=lambda r: r["label"])]
    head = {"seed": seed, "config_sha256": _sha(cfg_bytes), "rules_sha256": _sha(rules_bytes),
            "runs": {"n": len(runs), "n_aborted": sum(1 for r in runs if r["aborted"]),
                     "n_used": len(used), "list": listing}}
    res = {"l1": dict(head, cells={}), "l2": dict(head, cells={}), "detection": dict(head, cells={})}
    for r in used:
        l1_out, l2_out, m_out = run_stages(r, cfg, rules_bytes, seed)
        res["l1"]["cells"][r["label"]] = l1_out
        res["l2"]["cells"][r["label"]] = l2_out
        res["detection"]["cells"][r["label"]] = dict((k, m_out[k]) for k in (
            "definition", "config", "inputs_sha256", "input", "excluded", "used", "diagnostics", "metrics"))
    os.makedirs(out_dir, exist_ok=True)
    for key, fname in (("l1", "e1_l1.json"), ("l2", "e1_l2.json"), ("detection", "e1_detection.json")):
        match._write_atomic(os.path.join(out_dir, fname), match.render(res[key]))
    return res


# ---------------------------------------------------------------- deposit check

def _forms(path):
    """The spellings of a directory path to look for: as given, with '/', with the backslash, and with the
    backslash doubled (how a JSON string spells it)."""
    p = path.rstrip("/\\")
    back = p.replace("/", "\\")
    return sorted(set([p, p.replace("\\", "/"), back, back.replace("\\", "\\\\")]), key=len, reverse=True)


def deposit_findings(run_dir, home, user, repo):
    """Findings for one run directory: [(file, line number, kind)]. A missing file is an InputError."""
    ignore_case = os.name == "nt"
    flags = re.IGNORECASE if ignore_case else 0
    pats = []
    for kind, path in (("repository path", repo), ("home directory", home)):
        if path and len(path.rstrip("/\\")) >= 2 and path not in ("~", "/", "\\"):
            pats.append((kind, re.compile("|".join(re.escape(f) for f in _forms(path)), flags)))
    if user and len(user) >= MIN_NAME_LEN:
        pats.append(("login name", re.compile(r"(?<![\w.-])%s(?![\w.-])" % re.escape(user), flags)))
    out = []
    for fname in DEPOSIT_FILES:
        text = match._decode(match._read(os.path.join(run_dir, fname), fname), fname)
        for n, line in enumerate(text.split("\n"), 1):
            for kind, pat in pats:
                if pat.search(line):
                    out.append((fname, n, kind))
    return out


def check_deposit(run_dirs, home=None, user=None, repo=None):
    """Exit status of --check-deposit (prints the findings to standard error)."""
    home = os.path.expanduser("~") if home is None else home
    user = getpass.getuser() if user is None else user
    repo = repo_root() if repo is None else repo
    bad = 0
    for d in run_dirs:
        name = os.path.basename(os.path.normpath(d))
        for fname, n, kind in deposit_findings(d, home, user, repo):
            print("%s/%s:%d: contains a %s" % (name, fname, n, kind), file=sys.stderr)
            bad += 1
    if bad:
        print("pipeline: %d finding(s); do not deposit these run directories" % bad, file=sys.stderr)
        return 1
    print("pipeline: deposit check passed for %d run director%s" % (len(run_dirs), "y" if len(run_dirs) == 1 else "ies"))
    return 0


# ---------------------------------------------------------------- synthetic runs

WALL0 = 1700000000000
MONO0 = 50000000
SYN_TRIALS_PER_BLOCK = 32
SYN_SPECS = (("synthetic-a", ("slow", "mid")), ("synthetic-b", ("mid", "fast")))


def _write(path, data):
    with open(path, "wb") as fh:
        fh.write(data)


def make_synthetic_run(run_dir, seed, label, speeds):
    """A complete synthetic run directory in the form the run-cell tool writes: two blocks of
    SYN_TRIALS_PER_BLOCK trials, one composition per trial (a quarter of them cancelled), a few arrow
    presses, and an observation log made by inject.py from the assembled ground truth."""
    rng = random.Random(seed)
    os.makedirs(run_dir, exist_ok=True)
    plan_rows = [{"kind": "header", "format": "plan/1", "os": "macos", "seed": seed, "generator_version": "0.1",
                  "config_sha256": "0" * 64, "recipes_sha256": "0" * 64, "corpus_sha256": "0" * 64}]
    steps = [{"key": "a", "at_ms": 0, "down": True}, {"key": "a", "at_ms": 50, "down": False}]
    trials = []                                   # (trial_id, block, begin_rel, end_rel, lo_rel, length, cancel, arrow)
    idx = 0
    for b, speed in enumerate(speeds):
        plan_rows.append({"kind": "block", "block_id": b, "speed": speed, "reset_ime": False, "marker": [],
                          "marker_gap_ms": 0})
        for k in range(SYN_TRIALS_PER_BLOCK):
            idx += 1
            tid = "t%05d" % idx
            begin = (idx - 1) * 10000 + b * 5000
            length = 800 + int(rng.random() * 1500)
            cancel = rng.random() < 0.25
            arrow = (idx % 5 == 0)
            trials.append((tid, b, begin, begin + 6000, begin + 500, length, cancel, arrow))
            plan_rows.append({"kind": "trial", "trial_id": tid, "block_id": b, "scenario": "S%d" % (k % 3 + 1),
                              "speed": speed, "gap_before_ms": 1000, "think_ms": 500, "phrase_id": "kana-%d" % idx,
                              "reading_len": 4, "steps": steps,
                              "intent": {"commit": "enter", "cand_index": None, "nav_count": 1 if arrow else 0,
                                         "abandon": cancel, "predictive": False, "ime_toggle_mid": False,
                                         "focus_switch_mid": False, "expect_session": True}})
    plan_bytes = _jl(plan_rows)

    def orow(kind, t, **kw):
        return dict(kw, kind=kind, t_wall_ms=WALL0 + t, t_mono_ns=(MONO0 + t) * 1000000)

    orows = [{"kind": "header", "format": "oracle/1", "plan_sha256": _sha(plan_bytes), "os": "macos",
              "emitter_version": "0.1", "backend": "dryrun"}]
    grows = [{"kind": "header", "format": "gt/1", "src": "mac_nstic", "app_version": "0.1.0", "os": "macos"}]
    step = 0
    for b in range(len(speeds)):
        mine = [t for t in trials if t[1] == b]
        orows.append(orow("block_begin", mine[0][2] - 100, block_id=b))
        for tid, _b, begin, end, lo, length, cancel, arrow in mine:
            orows.append(orow("trial_begin", begin, trial_id=tid))
            if arrow:
                step = 0
                for down, dt in ((True, 300), (False, 340)):
                    orows.append(orow("sent", lo + dt, trial_id=tid, step=step, key="left", down=down))
                    step += 1
            orows.append(orow("trial_end", end, trial_id=tid))
            grows.append(orow("ev", lo, ev="set_marked", len=3, sel_loc=3, sel_len=0))
            if cancel:
                grows.append(orow("ev", lo + length, ev="set_marked", len=0, sel_loc=0, sel_len=0))
            else:
                grows.append(orow("ev", lo + length, ev="insert_text", len=3))
        orows.append(orow("block_end", mine[-1][3] + 100, block_id=b))
    oracle_bytes, gt_bytes = _jl(orows), _jl(grows)

    rules = match._read(os.path.join(_HERE, "gt_rules.example.json"), "rules")
    sess = gt_sessions.assemble(gt_bytes, oracle_bytes, rules, plan_bytes)["definitions"]["macos_def"]
    obs_ime, _truth = inject.inject(sess, {"miss": 0.05, "split": 0.04, "merge": 0.04, "false_pos": 0.05},
                                    {"bias_ms": 20, "sd_ms": 10, "end_lag_ms_max": 30}, seed)
    obs_rows = [{"type": "meta", "format": "obs/1", "os": "macos", "logger_version": "0.1.0",
                 "manifest_sha256": "0" * 64,
                 "capabilities": {"unconditional": ["key", "ime_shadow"], "threshold_gated": [], "config_gated": []}}]
    keys = [{"type": "key", "t": WALL0 + t[2], "category": "alphabetic", "press": True} for t in trials]
    obs_rows += sorted(keys + obs_ime, key=lambda r: (r["t"], r["type"]))
    obs_bytes = _jl(obs_rows)

    logs = {"plan": plan_bytes, "oracle": oracle_bytes, "gt": gt_bytes, "obs": obs_bytes}
    outputs = {}
    for name in LOG_NAMES:
        _write(os.path.join(run_dir, LOG_FILES[name]), logs[name])
        outputs[name] = {"file": LOG_FILES[name], "sha256": _sha(logs[name]), "lines": logs[name].count(b"\n")}
    manifest = {"format": RUN_FORMAT, "runner_version": "synthetic", "emitter_version": "synthetic",
                "cell": {"os": "macos", "label": label, "ime": "synthetic"}, "plan_sha256": _sha(plan_bytes),
                "git_commit": None, "git_dirty": None, "host": {}, "started": None, "ended": None,
                "outputs": outputs, "children": {}, "resets": [], "focus": [], "aborted": False, "abort_reason": None}
    _write(os.path.join(run_dir, MANIFEST), _json_bytes(manifest))


def make_synthetic(out_dir, seed):
    """Two synthetic run directories (run-a, run-b) under out_dir; returns their paths."""
    paths = []
    for i, (label, speeds) in enumerate(SYN_SPECS):
        p = os.path.join(out_dir, "run-" + label[-1])
        make_synthetic_run(p, seed * 1000 + i, label, speeds)
        paths.append(p)
    return paths


# ---------------------------------------------------------------- CLI

def main(argv):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="From run directories to the level-1, level-2 and detection results")
    ap.add_argument("--runs", nargs="+")
    ap.add_argument("--runs-from")
    ap.add_argument("--config")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--out")
    ap.add_argument("--synthetic")
    ap.add_argument("--check-deposit", nargs="+", dest="deposit")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    try:
        if args.deposit:
            return check_deposit(args.deposit)
        if args.synthetic:
            if args.seed is None:
                ap.error("--synthetic needs --seed")
            for p in make_synthetic(args.synthetic, args.seed):
                print("pipeline: wrote a synthetic run directory (%s)" % os.path.basename(p))
            return 0
        if not (args.config and args.out and args.seed is not None and bool(args.runs) != bool(args.runs_from)):
            ap.error("--config, --seed, --out and exactly one of --runs / --runs-from are required")
        dirs = args.runs if args.runs else read_runs_list(args.runs_from)
        res = analyse(dirs, args.config, args.seed, args.out)
    except CheckFailed as e:
        for line in e.findings[:50]:
            print("pipeline: " + line, file=sys.stderr)
        if len(e.findings) > 50:
            print("pipeline: ...and %d more" % (len(e.findings) - 50), file=sys.stderr)
        print("pipeline: step 0 found %d violation(s); nothing was analysed" % len(e.findings), file=sys.stderr)
        return 1
    except (InputError, ValueError) as e:
        print("pipeline: %s" % e, file=sys.stderr)
        return 2
    except (KeyError, TypeError, AttributeError, IndexError) as e:
        print("pipeline: an input has an unexpected shape (%s: %s)" % (type(e).__name__, e), file=sys.stderr)
        return 2
    except OSError as e:
        print("pipeline: could not read or write a file (%s)" % type(e).__name__, file=sys.stderr)
        return 2
    r = res["l1"]["runs"]
    print("pipeline: %d run(s), %d aborted, %d analysed; results written" % (r["n"], r["n_aborted"], r["n_used"]))
    return 0


# ---------------------------------------------------------------- selftest

def _quiet(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = main(argv)
        except SystemExit as e:  # argparse reports a usage error this way
            rc = e.code
    return rc, out.getvalue(), err.getvalue()


def _config_file(d, extra=None):
    cfg = {"bootstrap_B": 100, "gt_rules": os.path.join(_HERE, "gt_rules.example.json")}
    cfg.update(extra or {})
    path = os.path.join(d, "config.json")
    _write(path, json.dumps(cfg).encode("utf-8"))
    return path


def _read_results(d):
    return dict((n, open(os.path.join(d, n), "rb").read()) for n in ("e1_l1.json", "e1_l2.json", "e1_detection.json"))


def _rewrite_log(run_dir, name, data):
    """Replace a log and record its new hash in the manifest (so only step 0 can object)."""
    _write(os.path.join(run_dir, LOG_FILES[name]), data)
    mp = os.path.join(run_dir, MANIFEST)
    m = json.loads(open(mp, "rb").read().decode("utf-8"))
    m["outputs"][name]["sha256"] = _sha(data)
    _write(mp, _json_bytes(m))


def _set_manifest(run_dir, **kw):
    mp = os.path.join(run_dir, MANIFEST)
    m = json.loads(open(mp, "rb").read().decode("utf-8"))
    m.update(kw)
    _write(mp, _json_bytes(m))


def _case_synthetic_form(d):
    f = []
    runs = make_synthetic(os.path.join(d, "form"), 5)
    for p in runs:
        if sorted(os.listdir(p)) != sorted(DEPOSIT_FILES):
            f.append("a synthetic run directory does not hold exactly run.json and the four logs: %r" % sorted(os.listdir(p)))
        r = load_run(p)
        if r["aborted"] or r["label"] not in ("synthetic-a", "synthetic-b"):
            f.append("the manifest of a synthetic run is wrong: %r" % (r["label"],))
        bad = check_run(r)
        if bad:
            f.append("a synthetic run fails step 0: %r" % (bad[:2],))
        if match.parse_plan_strata(r["files"]["plan"])["trials"].__len__() != 2 * SYN_TRIALS_PER_BLOCK:
            f.append("a synthetic run does not have two blocks of %d trials" % SYN_TRIALS_PER_BLOCK)
    again = make_synthetic(os.path.join(d, "form2"), 5)
    if any(open(os.path.join(a, n), "rb").read() != open(os.path.join(b, n), "rb").read()
           for a, b in zip(runs, again) for n in DEPOSIT_FILES):
        f.append("the same seed gives different synthetic runs")
    other = make_synthetic(os.path.join(d, "form3"), 6)
    if open(os.path.join(other[0], "obs.jsonl"), "rb").read() == open(os.path.join(runs[0], "obs.jsonl"), "rb").read():
        f.append("the seed has no effect on the synthetic runs")
    return f


def _case_reproduces(d):
    f = []
    runs = make_synthetic(os.path.join(d, "rep"), 3)
    cfg = _config_file(d)
    outs = []
    for i in (1, 2):
        o = os.path.join(d, "out%d" % i)
        rc, _o, err = _quiet(["--runs"] + runs + ["--config", cfg, "--seed", "7", "--out", o])
        if rc != 0:
            return ["the pipeline did not exit 0 (%d): %s" % (rc, err[-300:])]
        outs.append(_read_results(o))
    if outs[0] != outs[1]:
        f.append("two runs on the same input give different bytes")
    for name, b in outs[0].items():
        if d.encode("utf-8") in b or b"\r" in b or b.startswith(b"\xef\xbb\xbf") or not b.endswith(b"\n"):
            f.append("%s is not LF / no BOM / free of paths" % name)
    l1o, l2o, deto = (json.loads(outs[0][n].decode("utf-8")) for n in ("e1_l1.json", "e1_l2.json", "e1_detection.json"))
    for name, o in (("e1_l1", l1o), ("e1_l2", l2o), ("e1_detection", deto)):
        if sorted(o["cells"]) != ["synthetic-a", "synthetic-b"] or o["seed"] != 7 or o["runs"]["n_used"] != 2:
            f.append("%s does not hold both cells, the seed and the run count" % name)
    pooled = l1o["cells"]["synthetic-a"]["metrics"]["pooled"]
    if not pooled["dwell"]["n"] > 30 or pooled["dwell"]["mae"] is None:
        f.append("level 1 has too few pairs in a synthetic cell: %r" % (pooled["dwell"]["n"],))
    if not l2o["cells"]["synthetic-a"]["texts"]["n"] == 8:
        f.append("level 2 should hold 8 texts per synthetic cell: %r" % (l2o["cells"]["synthetic-a"]["texts"]["n"],))
    det = deto["cells"]["synthetic-a"]["metrics"]["pooled"]
    if det is None or not det["recall"]["value"] > 0.7 or not det["precision"]["value"] > 0.7:
        f.append("detection on a synthetic cell is implausibly low: %r" % (det and det["recall"]["value"],))
    # the seed matters, and the injected errors are visible (a run with no misses would not show them)
    o3 = os.path.join(d, "out3")
    if _quiet(["--runs"] + runs + ["--config", cfg, "--seed", "8", "--out", o3])[0] != 0 or _read_results(o3) == outs[0]:
        f.append("a different seed gives the same results")
    if det is not None and det["n_miss"] + det["n_false_pos"] + det["n_split_gt"] + det["n_merge_obs"] == 0:
        f.append("no injected error reached the detection counts")
    return f


def _case_aborted_and_tampered(d):
    f = []
    runs = make_synthetic(os.path.join(d, "abt"), 4)
    cfg = _config_file(d)
    _set_manifest(runs[1], aborted=True, abort_reason="synthetic")
    o = os.path.join(d, "outa")
    rc, _o, err = _quiet(["--runs"] + runs + ["--config", cfg, "--seed", "1", "--out", o])
    res = json.loads(open(os.path.join(o, "e1_l1.json"), "rb").read().decode("utf-8")) if rc == 0 else None
    if rc != 0 or sorted(res["cells"]) != ["synthetic-a"] or res["runs"]["n_aborted"] != 1 or res["runs"]["n_used"] != 1:
        f.append("an aborted run is not left out and counted (rc %d): %s" % (rc, err[-200:]))
    if res and [x["aborted"] for x in res["runs"]["list"]] != [False, True]:
        f.append("the run list does not say which run was aborted")
    # a log that no longer matches its recorded hash stops the run (exit 2)
    runs2 = make_synthetic(os.path.join(d, "abt2"), 4)
    with open(os.path.join(runs2[0], "obs.jsonl"), "ab") as fh:
        fh.write(b"\n")
    rc = _quiet(["--runs"] + runs2 + ["--config", cfg, "--seed", "1", "--out", os.path.join(d, "outb")])[0]
    if rc != 2:
        f.append("a log that changed after the run was accepted (rc %d)" % rc)
    if os.path.exists(os.path.join(d, "outb", "e1_l1.json")):
        f.append("a result was written although the run stopped")
    # two runs with one label are refused
    runs3 = make_synthetic(os.path.join(d, "abt3"), 4)
    m = json.loads(open(os.path.join(runs3[1], MANIFEST), "rb").read().decode("utf-8"))
    _set_manifest(runs3[1], cell=dict(m["cell"], label="synthetic-a"))
    if _quiet(["--runs"] + runs3 + ["--config", cfg, "--seed", "1", "--out", os.path.join(d, "outc")])[0] != 2:
        f.append("two runs with the same cell label were accepted")
    return f


def _case_step_zero(d):
    f = []
    cfg = _config_file(d)

    def rc_of(run_dirs, out):
        return _quiet(["--runs"] + run_dirs + ["--config", cfg, "--seed", "1", "--out", os.path.join(d, out)])

    base = make_synthetic(os.path.join(d, "s0"), 2)
    if rc_of(base, "o0")[0] != 0:
        return ["the unmodified synthetic runs do not pass"]
    # content in the observation log (a typed character) is refused
    obs = open(os.path.join(base[0], "obs.jsonl"), "rb").read()
    _rewrite_log(base[0], "obs", obs + b'{"type":"key","t":1700000000001,"category":"alphabetic","press":true,"char":"a"}\n')
    rc, _o, err = rc_of(base, "o1")
    if rc != 1 or "obs.jsonl" not in err:
        f.append("an observation row with content was accepted (rc %d)" % rc)
    if os.path.exists(os.path.join(d, "o1", "e1_l1.json")):
        f.append("a result was written although step 0 found a violation")
    # a header that does not declare ime_shadow is refused
    base2 = make_synthetic(os.path.join(d, "s0b"), 2)
    lines = open(os.path.join(base2[0], "obs.jsonl"), "rb").read().split(b"\n", 1)
    hdr = json.loads(lines[0].decode("utf-8"))
    hdr["capabilities"]["unconditional"] = ["key"]
    _rewrite_log(base2[0], "obs", json.dumps(hdr, separators=(",", ":")).encode("utf-8") + b"\n" + lines[1])
    rc, _o, err = rc_of(base2, "o2")
    if rc != 1 or "ime_shadow" not in err:
        f.append("a header without the ime_shadow channel was accepted (rc %d)" % rc)
    # a plan that breaks the plan format is refused
    base3 = make_synthetic(os.path.join(d, "s0c"), 2)
    plan = open(os.path.join(base3[0], "plan.jsonl"), "rb").read().replace(b'"speed":"slow"', b'"speed":"sluggish"', 1)
    _rewrite_log(base3[0], "plan", plan)
    rc = rc_of(base3, "o3")[0]
    if rc != 1:
        f.append("an invalid plan was accepted (rc %d)" % rc)
    return f


def _case_deposit(d):
    f = []
    runs = make_synthetic(os.path.join(d, "dep"), 2)
    home, repo, user = "C:\\Users\\alice", "/work/ime-repo", "alice"
    if deposit_findings(runs[0], home, user, repo):
        f.append("a clean synthetic run directory has findings")
    m = json.loads(open(os.path.join(runs[0], MANIFEST), "rb").read().decode("utf-8"))
    # the home directory contains the login name, so a leaked home path is reported for both
    cases = (("the home directory (backslashes, as JSON spells them)", "started at C:\\Users\\alice\\work", ["home directory", "login name"]),
             ("the home directory (slashes)", "started at C:/Users/alice/work", ["home directory", "login name"]),
             ("the repository path", "cwd /work/ime-repo/papers", ["repository path"]),
             ("the login name", "written by alice on this machine", ["login name"]))
    for name, text, kinds in cases:
        _write(os.path.join(runs[0], MANIFEST), _json_bytes(dict(m, note=text)))
        got = sorted(k for _f, _n, k in deposit_findings(runs[0], home, user, repo))
        if got != sorted(kinds):
            f.append("%s is not reported as %r: %r" % (name, kinds, got))
    for name, text in (("replaced paths", "started at ~/work in <repo>/papers"), ("a name inside a longer word", "alicesprings"),
                       ("a home path of another user", "C:\\Users\\bob\\x")):
        _write(os.path.join(runs[0], MANIFEST), _json_bytes(dict(m, note=text)))
        if deposit_findings(runs[0], home, user, repo):
            f.append("%s was reported" % name)
    if deposit_findings(runs[0], home, "al", repo):
        f.append("a login name shorter than %d characters was searched for" % MIN_NAME_LEN)
    # a finding in a log is reported with its line, and the standard-error files are not read
    _write(os.path.join(runs[0], MANIFEST), _json_bytes(m))
    _write(os.path.join(runs[0], "reset.stderr.txt"), b"/work/ime-repo alice\n")
    if deposit_findings(runs[0], home, user, repo):
        f.append("a standard-error file was read")
    with open(os.path.join(runs[0], "gt.jsonl"), "ab") as fh:
        fh.write(b'{"note":"/work/ime-repo/x"}\n')
    n_lines = open(os.path.join(runs[0], "gt.jsonl"), "rb").read().count(b"\n")
    if deposit_findings(runs[0], home, user, repo) != [("gt.jsonl", n_lines, "repository path")]:
        f.append("a finding in a log is not reported with its file and line")
    # the command line: exit 1 with the real home directory, 0 once it is replaced
    real = os.path.expanduser("~")
    if len(real.rstrip("/\\")) >= 2 and real != "~":
        _write(os.path.join(runs[1], MANIFEST), _json_bytes(dict(m, note="in " + real + "/x")))
        rc, _o, err = _quiet(["--check-deposit", runs[1]])
        if rc != 1 or real in err:
            f.append("the real home directory was not refused, or was echoed (rc %d)" % rc)
        _write(os.path.join(runs[1], MANIFEST), _json_bytes(dict(m, note="in ~/x")))
        if _quiet(["--check-deposit", runs[1]])[0] != 0:
            f.append("a manifest with the home directory replaced by ~ was refused")
    if _quiet(["--check-deposit", os.path.join(d, "no-such-dir")])[0] != 2:
        f.append("a missing run directory should exit 2")
    return f


def _case_usage_and_config(d):
    f = []
    if _quiet([])[0] != 2:
        f.append("no arguments should exit 2")
    runs = make_synthetic(os.path.join(d, "use"), 2)
    for name, body in (("an unknown key", {"nope": 1}), ("a bad bootstrap size", {"bootstrap_B": 0}),
                       ("a bad overlap threshold", {"iou_min": 2})):
        cfg = _config_file(d, body)
        rc = _quiet(["--runs"] + runs + ["--config", cfg, "--seed", "1", "--out", os.path.join(d, "outu")])[0]
        if rc != 2:
            f.append("a configuration with %s was accepted (rc %d)" % (name, rc))
    no_rules = os.path.join(d, "no-rules.json")
    _write(no_rules, b'{"bootstrap_B": 10}')
    if _quiet(["--runs"] + runs + ["--config", no_rules, "--seed", "1", "--out", os.path.join(d, "outu")])[0] != 2:
        f.append("a configuration without gt_rules was accepted")
    listing = os.path.join(d, "list.md")
    _write(listing, ("notes\n- run_dir: %s\n- run_dir: %s\n" % (runs[0], runs[1])).encode("utf-8"))
    cfg = _config_file(d)
    o = os.path.join(d, "outl")
    if _quiet(["--runs-from", listing, "--config", cfg, "--seed", "7", "--out", o])[0] != 0:
        f.append("--runs-from did not run")
    o2 = os.path.join(d, "outl2")
    _quiet(["--runs"] + runs + ["--config", cfg, "--seed", "7", "--out", o2])
    if _read_results(o) != _read_results(o2):
        f.append("--runs-from and --runs give different results")
    if _quiet(["--runs-from", listing, "--runs"] + runs + ["--config", cfg, "--seed", "7", "--out", o])[0] != 2:
        f.append("--runs together with --runs-from was accepted")
    return f


CASES = [
    ("synthetic run directories (form, step 0, determinism, seed)", _case_synthetic_form),
    ("one command reproduces the results (byte-identical, no paths, seed matters)", _case_reproduces),
    ("aborted runs are left out and counted; a changed log or a shared label stops the run", _case_aborted_and_tampered),
    ("step 0 refuses content, a missing channel and an invalid plan", _case_step_zero),
    ("deposit check (paths, login name, replaced paths, lines, stderr files)", _case_deposit),
    ("usage errors, configuration errors and --runs-from", _case_usage_and_config),
]


def selftest():
    bad = 0
    for name, fn in CASES:
        d = tempfile.mkdtemp(prefix="pipeline_selftest_")
        try:
            fails = fn(d)
        except Exception as e:  # an unexpected exception counts as a failure
            fails = ["exception %s: %s" % (type(e).__name__, e)]
        finally:
            shutil.rmtree(d, ignore_errors=True)
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
