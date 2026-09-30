#!/usr/bin/env python3
# kit: selftest
"""End-to-end analysis of the first experiment: from run directories to the level-1 and level-2
agreement results and the detection results, in one command. Uses only the Python standard library.
Every stage is an existing module of this directory and is only called here, never reimplemented:
gt_sessions (ground-truth sessions), match (pairing and detection metrics), l1 (per-session
agreement) and l2 (aggregate agreement).

  pipeline.py --runs DIR [DIR ...] --config CFG.json --seed N --out RESULTS_DIR [--prereg PATH --seed-file SEED]
  pipeline.py --runs-from LIST.md --config CFG.json --seed N --out RESULTS_DIR [--prereg PATH --seed-file SEED]
  pipeline.py --freeze-hash --config CFG.json --seed-file SEED
  pipeline.py --check-prereg PATH --config CFG.json --seed-file SEED
  pipeline.py --synthetic DIR --seed N            write two synthetic run directories under DIR
  pipeline.py --check-deposit DIR [DIR ...]       refuse a run directory that is not safe to deposit
  pipeline.py --pack DIR --out ARCHIVE.zip        bundle the five deposit files into a checked archive
  pipeline.py --selftest [--full]                 default: a representative variant of every case
                                                  (one positive and the most important negatives of
                                                  each gate); --full: every variant, about a minute

A run directory (written by the run-cell tool) holds plan.jsonl, oracle.jsonl, gt.jsonl, obs.jsonl and
run.json (the manifest, format run/1). The manifest records the SHA-256 of every log; a log that no
longer matches its recorded hash stops the run. A run whose manifest says aborted is left out of the
matching and is counted (its cell is listed under "runs" in every result file).

Cell labels. The label of a cell is the "label" of the cell recorded in run.json (the cell file of the
run-cell tool carries it). A run without a label is refused; the operating system is never used in its
place. Among the runs that were not aborted, two runs must not share a label; an aborted run may share
the label of the run that replaced it and is counted.

Step 0 (checks that run before any statistic). The gt and obs logs must pass the content-free
validator (kit/formats/validate_logs.py), the plan must pass the plan validator, the oracle must pass
the oracle validator, and the header of the observation log must declare the "key" and "ime_shadow"
channels among its capabilities. When the header places "ime_shadow" among the gated channels
(threshold_gated or config_gated), the channel may legitimately produce no row; a run that has
ground-truth sessions but no "ime_shadow" row at all is then refused, because agreement cannot be
judged from an empty channel. Any violation is listed and the run stops with exit status 1.

Stages, per run directory (one cell): ground-truth sessions from gt, oracle and plan; then, for each of
two session definitions (the one that follows the operating system in the plan header, macos_def or
windows_def, and the common definition "all"), matching against the observation log, level 1 and level 2.
Every result file holds cells[label][definition].

Configuration CFG (JSON; keys starting with "_" are annotations and are not read):
  {"iou_min": 0.5, "obs_end_offset_ms": 0, "theta": 0.5, "drop_start_while_open": false,
   "text_size_trials": 8, "bootstrap_B": 2000, "limit_ms": 20000, "mixtures": {...},
   "gt_rules": "path/to/rules.json"}
Every key is optional except gt_rules, which is resolved relative to the configuration file. The
clock offsets between the two logs are not passed to the matcher (all offsets are zero).

Seed. The seed is a command-line argument or the content of the seed file (one non-negative integer
without spaces; the experiment keeps it in one file). It is passed unchanged to every bootstrap of
level 1 and level 2, and each stage derives its own streams from it. A synthetic run directory number i
(i = 0, 1) uses the seed 1000 * seed + i to generate the ground truth and that value xor 0x5eed to
inject observation errors, so the two random streams are independent.

Freeze marks. Real data is analysed only after the analysis is frozen. The pre-registration file holds,
outside HTML comments and code fences, exactly one line "frozen_at: YYYY-MM-DD..." and exactly one line
"sha256: <64 lowercase hex digits>"; placeholders and empty values are not marks. The sha256 is the
SHA-256 of the text made of, in this order, the SHA-256 (lowercase hex) of the configuration file, of
the seed file and of the ground-truth rule file named by gt_rules, each followed by a line feed; --freeze-hash
prints it. Every analysis of real data needs --prereg and --seed-file, recomputes the value and stops with
exit status 3 when a mark is missing, malformed, duplicated or different. Only runs that carry the mark
"synthetic": true in their manifest (written by --synthetic) are exempt; the mark is a convenience for
rehearsals, not a defence against a person who edits a manifest. A synthetic result also carries
"synthetic": true and is never written under experiment/results.

Outputs (RESULTS_DIR): e1_l1.json, e1_l2.json and e1_detection.json. Each one carries the seed, the
SHA-256 of the configuration, of the rule file, of every manifest and of every input log, and the
per-cell results. No path is written to any of them, and identical inputs always give identical bytes
(sorted keys, LF, UTF-8, no BOM). The files are written to a temporary directory and moved into place; when
the move fails, no result of an earlier run is left behind.

Runs list. --runs-from reads lines "- run_dir: PATH  manifest_sha256: <64 hex digits>" (a relative PATH is
relative to the list file), outside HTML comments and code fences. The SHA-256 of run.json must match;
a line without it, or with a different one, stops the analysis. The labels that were used are printed.

Deposit check. Only run.json and the four logs are meant to be deposited. --check-deposit exits 1 when a
run directory is not safe to deposit and reports the file and line (never the value). It refuses a file
that contains (a) any absolute path: a drive letter, a UNC path, /Users/, /home/, /Volumes/, /root/,
/mnt/, an MSYS drive path such as /c/, in the plain spelling and in the spelling of a JSON string (only
paths that start with ~ or <repo>, and relative paths, are allowed); (b) the home directory of the
current user or of --also-home PATH (any number), in every separator spelling and in the MSYS spelling;
(c) the absolute path of the repository; (d) the login name of the current user or a name given with
--also-user NAME (any number), as a whole word; (e) content in the ground-truth or observation log (the
content-free validator), for a run that was not aborted. It first checks every recorded hash, so a
changed log or a missing log whose hash is recorded exits 2; a log that an aborted run recorded with a
null hash need not exist. The repository path is found as the run-cell tool finds it. The standard-error
files are not deposited and are not read.
Known misses (this is a safeguard against slips, not proof of anonymity): a login name of at most two
characters is not searched for; a name is not found when it touches a letter, digit, underscore, dot or
hyphen; a bare short (8.3) name such as YAMADA~1 is found only inside a path; a path that does not begin
with one of the listed roots (for example /tmp/) is not recognised; host names, e-mail addresses and
other personal text are not searched; the current user is found only when the standard library can name
it. Pass the values of the measuring machine with --also-user and --also-home when the check runs on
another machine.

--pack reads the five files, runs the deposit check, writes them to a ZIP archive in a fixed order, with
fixed times (1980-01-01), fixed attributes and no compression (so the bytes do not depend on the
compression library), checks the contents of the archive again with the same check and prints its
SHA-256. An existing output file is never overwritten.

Self-test. The default --selftest runs, for every case, a positive variant and the most important negative
variants of each gate, calls functions directly where it can and starts a child process only for the shell
entry point; it is meant to finish in under 20 seconds. --selftest --full runs every variant (all freeze-mark
spellings, every shell-entry variant, every usage and configuration error, every spelling of a path, and the
rarer input errors) and takes about a minute. Files that have not changed are read from disk once during a
self-test.

Exit status: 0 on success; 1 when a check finds a violation; 2 when an input cannot be read, is
malformed or does not match its recorded hash, when usage is incorrect, or on an unexpected error (the
message then names the type of the error only); 3 when the analysis is not frozen.
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
import stat
import subprocess
import sys
import tempfile
import time
import zipfile

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
EXPERIMENT_RESULTS = os.path.join(os.path.dirname(KIT), "experiment", "results")
LOG_NAMES = ("plan", "oracle", "gt", "obs")
LOG_FILES = {"plan": "plan.jsonl", "oracle": "oracle.jsonl", "gt": "gt.jsonl", "obs": "obs.jsonl"}
MANIFEST = "run.json"
RUN_FORMAT = "run/1"
DEPOSIT_FILES = (MANIFEST,) + tuple(LOG_FILES[n] for n in LOG_NAMES)
DEFINITION_OF_OS = {"macos": "macos_def", "windows": "windows_def"}
REQUIRED_CHANNELS = ("key", "ime_shadow")
GATED_KEYS = ("threshold_gated", "config_gated")
CONFIG_KEYS = ("iou_min", "obs_end_offset_ms", "theta", "drop_start_while_open", "text_size_trials",
               "bootstrap_B", "limit_ms", "mixtures", "gt_rules")
MIN_NAME_LEN = 3
MAX_FILE_BYTES = 512 * 1024 * 1024
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
FROZEN_RE = re.compile(r"^frozen_at:[ \t]*[0-9]{4}-[0-9]{2}-[0-9]{2}")
SHA_LINE_RE = re.compile(r"^sha256:[ \t]*([0-9a-f]{64})[ \t]*$")
RUN_LINE_RE = re.compile(r"^- run_dir:[ \t]*(\S.*?)[ \t]+manifest_sha256:[ \t]*([0-9a-f]{64})[ \t]*$")
ZIP_TIME = (1980, 1, 1, 0, 0, 0)
RESULT_FILES = (("l1", "e1_l1.json"), ("l2", "e1_l2.json"), ("detection", "e1_detection.json"))


class CheckFailed(Exception):
    """One or more checks found a violation (exit status 1)."""

    def __init__(self, findings):
        Exception.__init__(self, "%d violation(s)" % len(findings))
        self.findings = findings


class NotFrozen(Exception):
    """The analysis is not frozen (exit status 3)."""


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


# The selftest sets a dict here: a file that has not changed is read from disk once. Only a file whose
# modification time is at least CACHE_SETTLE_NS old is cached, so a file that is rewritten within the
# resolution of the clock is never mistaken for the earlier one.
_READ_CACHE = None
CACHE_SETTLE_NS = 300000000


def _read_regular(path, what):
    """Read a regular file of at most MAX_FILE_BYTES; a link or a special file is refused."""
    try:
        st = os.lstat(path)
    except OSError as e:
        raise InputError("%s: cannot be opened (%s)" % (what, type(e).__name__))
    if not stat.S_ISREG(st.st_mode):
        raise InputError("%s: not a regular file (a link or a special file is refused)" % what)
    if st.st_size > MAX_FILE_BYTES:
        raise InputError("%s: larger than %d MiB" % (what, MAX_FILE_BYTES // (1024 * 1024)))
    key = (os.path.abspath(path), st.st_mtime_ns, st.st_size, st.st_ino)
    if _READ_CACHE is not None and key in _READ_CACHE:
        return _READ_CACHE[key]
    try:
        with open(path, "rb") as fh:
            data = fh.read(MAX_FILE_BYTES + 1)
    except OSError as e:
        raise InputError("%s: cannot be read (%s)" % (what, type(e).__name__))
    if _READ_CACHE is not None and time.time_ns() - st.st_mtime_ns > CACHE_SETTLE_NS:
        _READ_CACHE[key] = data
    if len(data) > MAX_FILE_BYTES:
        raise InputError("%s: larger than %d MiB" % (what, MAX_FILE_BYTES // (1024 * 1024)))
    return data


def _git_top():
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=_HERE, stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


def repo_root():
    """The root of the repository as the run-cell tool defines it: the top level reported by git, or,
    when git cannot tell, the directory three levels above kit/."""
    top = _git_top()
    if top is not None and top.strip():
        return os.path.normpath(top.strip())
    return os.path.dirname(os.path.dirname(os.path.dirname(KIT)))


def _is_under(path, base):
    a = os.path.normcase(os.path.realpath(path))
    b = os.path.normcase(os.path.realpath(base))
    return a == b or a.startswith(b.rstrip("\\/") + os.sep)


def _visible_lines(text):
    """The lines of a Markdown text that lie outside HTML comments (single or multiple lines) and code
    fences. Text that follows the end of a comment on the same line is kept but no longer starts the line."""
    out = []
    in_comment = in_fence = False
    for raw in text.split("\n"):
        line = raw.rstrip("\r")
        if in_comment:
            end = line.find("-->")
            if end < 0:
                continue
            in_comment = False
            line = " " + line[end + 3:]
        elif re.match(r"^ {0,3}(```|~~~)", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        while True:
            start = line.find("<!--")
            if start < 0:
                break
            end = line.find("-->", start + 4)
            if end < 0:
                in_comment = True
                line = line[:start]
                break
            line = line[:start] + " " + line[end + 3:]
        out.append(line)
    return out


# ---------------------------------------------------------------- configuration

def parse_config(data, base_dir):
    """Parse the configuration bytes into a dict; gt_rules is resolved against base_dir."""
    obj = match._json_loads(match._decode(data, "config"), "config", True)
    if not isinstance(obj, dict):
        raise InputError("config: the top level must be an object")
    cfg = {"iou_min": 0.5, "obs_end_offset_ms": 0, "theta": 0.5, "drop_start_while_open": False,
           "text_size_trials": 8, "bootstrap_B": 2000, "limit_ms": 20000, "mixtures": None, "gt_rules": None}
    for k, v in obj.items():
        if k.startswith("_"):
            continue
        if k not in CONFIG_KEYS:
            raise InputError("config: unknown key '%s'" % k)
        cfg[k] = v
    if not isinstance(cfg["gt_rules"], str) or not cfg["gt_rules"]:
        raise InputError("config: gt_rules (the path of the rule file) is required")
    cfg["gt_rules"] = os.path.normpath(os.path.join(base_dir, cfg["gt_rules"]))
    match.parse_config(_enc({"iou_min": cfg["iou_min"], "obs_end_offset_ms": cfg["obs_end_offset_ms"],
                             "theta": cfg["theta"], "drop_start_while_open": cfg["drop_start_while_open"]}))
    return cfg


def _enc(d):
    return json.dumps(d, sort_keys=True).encode("utf-8")


def _stage_configs(cfg, seed, label):
    """The configuration bytes handed to each stage (the stages validate their own keys)."""
    l2c = {"text_size_trials": cfg["text_size_trials"], "B": cfg["bootstrap_B"], "seed": seed}
    if cfg["mixtures"] is not None:
        l2c["mixtures"] = cfg["mixtures"]
    return {"match": _enc({"iou_min": cfg["iou_min"], "obs_end_offset_ms": cfg["obs_end_offset_ms"],
                           "theta": cfg["theta"], "drop_start_while_open": cfg["drop_start_while_open"],
                           "cell": label}),
            "l1": _enc({"B": cfg["bootstrap_B"], "seed": seed, "limit_ms": cfg["limit_ms"]}),
            "l2": _enc(l2c)}


def read_seed_file(path):
    """The seed in a seed file: one non-negative integer without spaces, optionally followed by a line end."""
    text = match._decode(_read_regular(path, "seed file"), "seed file")
    if not re.fullmatch(r"[0-9]{1,18}(\r?\n)?", text):
        raise InputError("seed file: it must hold one non-negative integer and nothing else")
    return int(text.strip())


# ---------------------------------------------------------------- freeze marks

def freeze_hash_of(config_bytes, seed_bytes, rules_bytes):
    """The value recorded as sha256 in the pre-registration."""
    text = "".join(_sha(b) + "\n" for b in (config_bytes, seed_bytes, rules_bytes))
    return _sha(text.encode("ascii"))


def freeze_hash(config_path, seed_path):
    cfg_bytes = _read_regular(config_path, "config")
    cfg = parse_config(cfg_bytes, os.path.dirname(os.path.abspath(config_path)))
    return freeze_hash_of(cfg_bytes, _read_regular(seed_path, "seed file"), _read_regular(cfg["gt_rules"], "rules"))


def check_prereg_text(text, want):
    """Raise NotFrozen unless the visible lines of the text hold exactly one well-formed frozen_at line
    and exactly one sha256 line, and that sha256 equals want."""
    lines = _visible_lines(text)
    frozen = [ln for ln in lines if FROZEN_RE.match(ln)]
    shas = [SHA_LINE_RE.match(ln).group(1) for ln in lines if SHA_LINE_RE.match(ln)]
    if len(frozen) != 1:
        raise NotFrozen("the pre-registration needs exactly one 'frozen_at: YYYY-MM-DD' line (found %d)" % len(frozen))
    if len(shas) != 1:
        raise NotFrozen("the pre-registration needs exactly one 'sha256: <64 hex digits>' line (found %d)" % len(shas))
    if shas[0] != want:
        raise NotFrozen("the recorded sha256 does not match the configuration, seed and rule files "
                        "(they changed after the freeze, or the mark is wrong)")


def check_prereg(prereg_path, config_path, seed_path):
    """Raise NotFrozen (exit 3) or InputError (exit 2)."""
    if not os.path.isfile(prereg_path):
        raise NotFrozen("the pre-registration file does not exist; the analysis is not frozen")
    text = match._decode(_read_regular(prereg_path, "pre-registration"), "pre-registration")
    check_prereg_text(text, freeze_hash(config_path, seed_path))


# ---------------------------------------------------------------- run directories

def read_run_files(run_dir, names=DEPOSIT_FILES):
    """{file name: bytes} for the named files of a run directory that exist. run.json must exist."""
    out = {}
    for fname in names:
        p = os.path.join(run_dir, fname)
        if fname != MANIFEST and not os.path.lexists(p):
            continue
        out[fname] = _read_regular(p, fname)
    return out


def _parse_manifest(mbytes):
    m = match._json_loads(match._decode(mbytes, "run.json"), "run.json", True)
    if not isinstance(m, dict) or m.get("format") != RUN_FORMAT:
        raise InputError("run.json: not a %s manifest" % RUN_FORMAT)
    if type(m.get("aborted")) is not bool:
        raise InputError("run.json: aborted must be a boolean")
    cell = m.get("cell")
    if not isinstance(cell, dict):
        raise InputError("run.json: cell must be an object")
    label = cell.get("label")
    if not isinstance(label, str) or not match.CELL_RE.fullmatch(label):
        raise InputError("run.json: the cell has no label of the form %s; add a \"label\" to the cell file "
                         "and record the run again" % match.CELL_RE.pattern)
    return m, label


def parse_run(files, run_dir, verify_all=False):
    """Parse a run from {file name: bytes}. Returns {"dir", "manifest", "manifest_sha", "label", "aborted",
    "synthetic", "files", "sha"}. The logs are checked against the recorded hashes when the run was not
    aborted, or always when verify_all is true. A log recorded with a null hash (an aborted run) need not
    exist; a log whose hash is recorded must."""
    mbytes = files.get(MANIFEST)
    if mbytes is None:
        raise InputError("run.json: cannot be opened")
    m, label = _parse_manifest(mbytes)
    run = {"dir": run_dir, "manifest": m, "manifest_sha": _sha(mbytes), "label": label, "aborted": m["aborted"],
           "synthetic": m.get("synthetic") is True, "files": {}, "sha": {}}
    outs = m.get("outputs")
    if not isinstance(outs, dict):
        raise InputError("run.json: outputs must be an object")
    for name in LOG_NAMES:
        rec = outs.get(name)
        if not isinstance(rec, dict):
            raise InputError("run.json: outputs.%s is missing" % name)
        sha = rec.get("sha256")
        if sha is not None and not (isinstance(sha, str) and SHA_RE.fullmatch(sha)):
            raise InputError("run.json: outputs.%s.sha256 must be null or 64 lowercase hex digits" % name)
        run["sha"][name] = sha
        if m["aborted"] and not verify_all:
            continue
        data = files.get(LOG_FILES[name])
        if data is None:
            if sha is None and m["aborted"]:
                continue
            raise InputError("%s: is missing although run.json records its hash" % LOG_FILES[name])
        if sha is None and m["aborted"] and not data:
            continue
        if sha != _sha(data):
            raise InputError("%s: SHA-256 does not match run.json (the log changed after the run)" % LOG_FILES[name])
        run["files"][name] = data
    return run


def load_run(run_dir):
    """Read a run directory for the analysis (the logs of an aborted run are not read)."""
    mbytes = _read_regular(os.path.join(run_dir, MANIFEST), "run.json")
    m, _label = _parse_manifest(mbytes)
    files = {MANIFEST: mbytes}
    if not m["aborted"]:
        for name in LOG_NAMES:
            files[LOG_FILES[name]] = _read_regular(os.path.join(run_dir, LOG_FILES[name]), LOG_FILES[name])
    return parse_run(files, run_dir)


def read_runs_list(path):
    """[(run directory, manifest SHA-256)] from the lines '- run_dir: PATH  manifest_sha256: HEX' (relative
    paths are relative to the list file); lines inside comments and code fences are not read."""
    text = match._decode(_read_regular(path, "runs list"), "runs list")
    base = os.path.dirname(os.path.abspath(path))
    out = []
    for line in _visible_lines(text):
        if not line.startswith("- run_dir:"):
            continue
        m = RUN_LINE_RE.match(line)
        if not m:
            raise InputError("runs list: a run_dir line has no valid manifest_sha256 (write "
                             "'- run_dir: PATH  manifest_sha256: <64 hex digits>')")
        out.append((os.path.normpath(os.path.join(base, m.group(1))), m.group(2)))
    return out


# ---------------------------------------------------------------- step 0

def _content_free(run, name):
    """Findings of the content-free validator for the gt and obs logs of a run."""
    vl = _tool("validate_logs", "formats", "validate_logs.py")
    out = []
    for kind in ("gt", "obs"):
        try:
            for ln, code, msg in vl.validate(kind, run["files"][kind]):
                out.append("%s/%s:%d: [%s] %s" % (name, LOG_FILES[kind], ln, code, msg))
        except RecursionError:
            out.append("%s/%s:1: [nesting] the log is nested too deeply to be checked" % (name, LOG_FILES[kind]))
    return out


def _oracle_findings(em, data):
    """Findings of the oracle validator for verified bytes (the validator reads a path, so the bytes that were
    checked against the recorded hash are written to a temporary file)."""
    fd, tmp = tempfile.mkstemp(prefix="oracle_", suffix=".jsonl")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        try:
            return em.validate_oracle(tmp)
        except RecursionError:
            return ["nested too deeply to be checked"]
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


def _capabilities(first_line):
    try:
        caps = json.loads(first_line.decode("utf-8")).get("capabilities")
    except (ValueError, AttributeError, RecursionError):
        caps = None
    return caps if isinstance(caps, dict) else {}


def _has_ime_rows(obs):
    for line in obs.split(b"\n"):
        if b"ime_shadow" not in line:
            continue
        try:
            row = json.loads(line.decode("utf-8"))
        except (ValueError, RecursionError):
            continue
        if isinstance(row, dict) and row.get("type") == "ime_shadow":
            return True
    return False


def check_run(run, rules_bytes):
    """Step 0 for one run. Returns a list of 'file:line: message' findings (empty when clean)."""
    gp = _tool("generate_plan", "gen", "generate_plan.py")
    em = _tool("emit", "emit", "emit.py")
    name = os.path.basename(os.path.normpath(run["dir"]))
    out = _content_free(run, name)
    try:
        for ln, code, msg in gp.validate_plan(run["files"]["plan"]):
            out.append("%s/%s:%d: [%s] %s" % (name, LOG_FILES["plan"], ln, code, msg))
    except RecursionError:
        out.append("%s/%s:1: [nesting] the plan is nested too deeply to be checked" % (name, LOG_FILES["plan"]))
    for msg in _oracle_findings(em, run["files"]["oracle"]):
        out.append("%s/%s: %s" % (name, LOG_FILES["oracle"], msg))
    caps = _capabilities(run["files"]["obs"].split(b"\n", 1)[0])
    declared, gated = set(), set()
    for k in ("unconditional",) + GATED_KEYS:
        if isinstance(caps.get(k), list):
            declared.update(x for x in caps[k] if isinstance(x, str))
    for k in GATED_KEYS:
        if isinstance(caps.get(k), list):
            gated.update(x for x in caps[k] if isinstance(x, str))
    for ch in REQUIRED_CHANNELS:
        if ch not in declared:
            out.append("%s/%s:1: the header does not declare the '%s' channel in meta.capabilities" % (name, LOG_FILES["obs"], ch))
    if "ime_shadow" in gated and not out and not _has_ime_rows(run["files"]["obs"]):
        sess = gt_sessions.assemble(run["files"]["gt"], run["files"]["oracle"], rules_bytes, run["files"]["plan"])
        if sess["definitions"]["all"]:
            out.append("%s/%s:1: cannot be judged: the channel is gated and produced no row although the ground truth "
                       "holds sessions" % (name, LOG_FILES["obs"]))
    return out


# ---------------------------------------------------------------- stages

def run_stages(run, cfg, rules_bytes, seed):
    """The stages for one run, for the definition of its operating system and for "all". Returns
    {definition: (l1 output, l2 output, match output)} (JSON-ready dicts)."""
    f = run["files"]
    plan = match.parse_plan_strata(f["plan"])
    if plan["os"] not in DEFINITION_OF_OS:
        raise InputError("plan: the operating system has no session definition")
    sc = _stage_configs(cfg, seed, run["label"])
    sessions = gt_sessions.assemble(f["gt"], f["oracle"], rules_bytes, f["plan"])
    sess_bytes = gt_sessions.render(sessions)
    out = {}
    for definition in (DEFINITION_OF_OS[plan["os"]], "all"):
        m_out = match.evaluate(sess_bytes, definition, f["obs"], f["plan"], f["oracle"], sc["match"])
        m_bytes = match.render(m_out)
        l1_out = l1.evaluate(m_bytes, sess_bytes, f["plan"], f["oracle"], sc["l1"])
        l2_out = l2.evaluate(m_bytes, sess_bytes, f["obs"], f["plan"], f["oracle"], sc["l2"])
        out[definition] = (l1_out, l2_out, m_out)
    return out


def _write(path, data):
    with open(path, "wb") as fh:
        fh.write(data)


def _write_results(out_dir, blobs):
    """Write the result files to a temporary directory and move them into out_dir. When anything fails, the
    result files of an earlier run are removed as well, so that no stale result is left next to a failure."""
    os.makedirs(out_dir, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix=".pipeline_tmp_", dir=out_dir)
    try:
        for fname, data in blobs:
            _write(os.path.join(tmp, fname), data)
        for fname, _data in blobs:
            os.replace(os.path.join(tmp, fname), os.path.join(out_dir, fname))
    except BaseException:
        for fname, _data in blobs:
            try:
                os.remove(os.path.join(out_dir, fname))
            except OSError:
                pass
        raise
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def analyse(run_dirs, config_path, seed, out_dir, prereg=None, seed_file=None, manifest_shas=None):
    """The whole pipeline. Writes the three result files; raises CheckFailed / NotFrozen / InputError."""
    if not _is_int(seed):
        raise InputError("seed must be an integer")
    cfg_bytes = _read_regular(config_path, "config")
    cfg = parse_config(cfg_bytes, os.path.dirname(os.path.abspath(config_path)))
    rules_bytes = _read_regular(cfg["gt_rules"], "rules")
    if not run_dirs:
        raise InputError("no run directory was given")
    runs = [load_run(d) for d in run_dirs]
    if manifest_shas is not None:
        for r, want in zip(runs, manifest_shas):
            if r["manifest_sha"] != want:
                raise InputError("run.json of a listed run does not match the manifest_sha256 in the runs list")
    n_syn = sum(1 for r in runs if r["synthetic"])
    if 0 < n_syn < len(runs):
        raise InputError("synthetic and real runs cannot be analysed together")
    synthetic = n_syn == len(runs)
    if synthetic:
        if _is_under(out_dir, EXPERIMENT_RESULTS):
            raise InputError("synthetic runs must not be written to the results directory of the experiment")
    else:
        if prereg is None or seed_file is None:
            raise NotFrozen("real data needs --prereg and --seed-file; the analysis is not frozen")
        if not os.path.isfile(prereg):
            raise NotFrozen("the pre-registration file does not exist; the analysis is not frozen")
        if read_seed_file(seed_file) != seed:
            raise InputError("--seed differs from the seed file")
        want = freeze_hash_of(cfg_bytes, _read_regular(seed_file, "seed file"), rules_bytes)
        check_prereg_text(match._decode(_read_regular(prereg, "pre-registration"), "pre-registration"), want)
    used = sorted((r for r in runs if not r["aborted"]), key=lambda r: r["label"])
    labels = [r["label"] for r in used]
    if len(set(labels)) != len(labels):
        raise InputError("two runs that were not aborted share a cell label (give each cell a distinct label)")
    findings = []
    for r in used:
        findings += check_run(r, rules_bytes)
    if findings:
        raise CheckFailed(findings)
    listing = [{"cell": r["label"], "aborted": r["aborted"], "logs_sha256": r["sha"], "manifest_sha256": r["manifest_sha"]}
               for r in sorted(runs, key=lambda r: (r["label"], r["aborted"], r["manifest_sha"]))]
    head = {"seed": seed, "synthetic": synthetic, "config_sha256": _sha(cfg_bytes), "rules_sha256": _sha(rules_bytes),
            "runs": {"n": len(runs), "n_aborted": sum(1 for r in runs if r["aborted"]),
                     "n_used": len(used), "list": listing}}
    res = {"l1": dict(head, cells={}), "l2": dict(head, cells={}), "detection": dict(head, cells={})}
    for r in used:
        per_def = run_stages(r, cfg, rules_bytes, seed)
        for key in res:
            res[key]["cells"][r["label"]] = {}
        for definition, (l1_out, l2_out, m_out) in per_def.items():
            res["l1"]["cells"][r["label"]][definition] = l1_out
            res["l2"]["cells"][r["label"]][definition] = l2_out
            res["detection"]["cells"][r["label"]][definition] = dict((k, m_out[k]) for k in (
                "definition", "config", "inputs_sha256", "input", "excluded", "used", "diagnostics", "metrics"))
    _write_results(out_dir, [(fname, match.render(res[key])) for key, fname in RESULT_FILES])
    return res


# ---------------------------------------------------------------- deposit check

_NAME_EDGE = r"[\w~>.\-/\\]"
ABSOLUTE_PATH_RES = (
    r"(?<![A-Za-z0-9_])[A-Za-z]:[\\/]",                               # a drive letter
    r"(?<!%s)\\{2,4}[\w$.-]" % _NAME_EDGE,                            # a UNC path (plain or as a JSON string)
    r"(?<![\w~>.:\-/\\])//[\w$.-]+/",                                 # a UNC path with slashes
    r"(?<!%s)/(?:Users|home|Volumes|root|mnt)/" % _NAME_EDGE,         # a home-like root
    r"(?<!%s)/[A-Za-z](?=/)" % _NAME_EDGE,                            # an MSYS drive path such as /c/
)
_ESC_RE = re.compile(r"\\(u[0-9a-fA-F]{4}|.)", re.DOTALL)
_SIMPLE_ESC = {"b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}


def _unescape(line):
    """The line with the escapes of a JSON string decoded (so that C:\\\\Users and \\u005c are seen as they are)."""
    def rep(m):
        g = m.group(1)
        if g[0] == "u" and len(g) == 5:
            return chr(int(g[1:], 16))
        return _SIMPLE_ESC.get(g, g)
    return _ESC_RE.sub(rep, line)


def _forms(path):
    """The spellings of a directory path to look for: as given, with '/', with the backslash, with the
    backslash doubled (how a JSON string spells it), and the MSYS spelling of a drive path (/c/Users/name)."""
    p = path.rstrip("/\\")
    back = p.replace("/", "\\")
    forms = set([p, p.replace("\\", "/"), back, back.replace("\\", "\\\\")])
    if re.match(r"^[A-Za-z]:[\\/]", p):
        forms.add("/" + p[0].lower() + p[2:].replace("\\", "/"))
    return sorted(forms, key=len, reverse=True)


def build_patterns(home=None, user=None, repo=None, also_users=(), also_homes=()):
    """[(kind, compiled pattern)] for the deposit check."""
    home = os.path.expanduser("~") if home is None else home
    if user is None:
        try:
            user = getpass.getuser()
        except Exception:
            user = None
    repo = repo_root() if repo is None else repo
    flags = re.IGNORECASE if os.name == "nt" else 0
    pats = [("absolute path", re.compile(rx, re.IGNORECASE)) for rx in ABSOLUTE_PATH_RES]
    paths = [("repository path", repo), ("home directory", home)] + [("home directory", h) for h in also_homes]
    for kind, path in paths:
        if path and len(path.rstrip("/\\")) >= 2 and path not in ("~", "/", "\\"):
            pats.append((kind, re.compile("|".join(re.escape(f) for f in _forms(path)), flags)))
    for name in also_users:
        if len(name) < MIN_NAME_LEN:
            raise InputError("--also-user: a name of fewer than %d characters cannot be searched for reliably" % MIN_NAME_LEN)
    names = ([user] if user and len(user) >= MIN_NAME_LEN else []) + list(also_users)
    for name in names:
        pats.append(("login name", re.compile(r"(?<![\w.-])%s(?![\w.-])" % re.escape(name), flags)))
    return pats


def scan_text(fname, text, pats):
    """[(file, line number, kind)] for the text of one file."""
    out = []
    for n, line in enumerate(text.split("\n"), 1):
        dec = _unescape(line) if "\\" in line else line
        seen = set()
        for kind, pat in pats:
            if kind not in seen and (pat.search(line) or (dec is not line and pat.search(dec))):
                seen.add(kind)
                out.append((fname, n, kind))
    return out


def scan_files(files, pats):
    out = []
    for fname in DEPOSIT_FILES:
        if fname in files:
            out += scan_text(fname, match._decode(files[fname], fname), pats)
    return out


def deposit_check_files(files, name, pats):
    """Findings ('file:line: message') for the five files of a run given as {file name: bytes}. Raises InputError
    when a hash does not match or a log whose hash is recorded is missing."""
    run = parse_run(files, name, verify_all=True)
    out = ["%s/%s:%d: contains %s" % (name, f, n, kind) for f, n, kind in scan_files(files, pats)]
    if not run["aborted"]:
        out += _content_free(run, name)
    return out


def check_deposit(run_dirs, pats):
    """Exit status of --check-deposit (prints the findings to standard error)."""
    bad = 0
    for d in run_dirs:
        name = os.path.basename(os.path.normpath(d))
        for line in deposit_check_files(read_run_files(d), name, pats):
            print(line, file=sys.stderr)
            bad += 1
    if bad:
        print("pipeline: %d finding(s); do not deposit these run directories" % bad, file=sys.stderr)
        return 1
    print("pipeline: deposit check passed for %d run director%s" % (len(run_dirs), "y" if len(run_dirs) == 1 else "ies"))
    return 0


def build_archive(files):
    """The bytes of a ZIP archive that holds the deposit files in a fixed order, with fixed times and attributes and
    no compression."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as zf:
        for fname in DEPOSIT_FILES:
            if fname in files:
                zi = zipfile.ZipInfo(fname, date_time=ZIP_TIME)
                zi.compress_type = zipfile.ZIP_STORED
                zi.create_system = 3
                zi.external_attr = 0o100644 << 16
                zf.writestr(zi, files[fname])
    return buf.getvalue()


def pack(run_dir, out_path, pats):
    """Exit status of --pack."""
    if os.path.lexists(out_path):
        raise InputError("the output file already exists and is not overwritten")
    name = os.path.basename(os.path.normpath(run_dir))
    files = read_run_files(run_dir)
    findings = deposit_check_files(files, name, pats)
    if not findings:
        data = build_archive(files)
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            back = dict((n, zf.read(n)) for n in zf.namelist())
        if back != files:
            raise InputError("the archive does not hold the files that were read")
        findings = deposit_check_files(back, name + ".zip", pats)
    if findings:
        for line in findings:
            print(line, file=sys.stderr)
        print("pipeline: %d finding(s); no archive was written" % len(findings), file=sys.stderr)
        return 1
    try:
        with open(out_path, "xb") as fh:
            fh.write(data)
    except FileExistsError:
        raise InputError("the output file already exists and is not overwritten")
    print("pipeline: archive sha256 %s (%d files, %d bytes)" % (_sha(data), len(files), len(data)))
    return 0


# ---------------------------------------------------------------- synthetic runs

WALL0 = 1700000000000
MONO0 = 50000000
SYN_TRIALS_PER_BLOCK = 32
SYN_SPECS = (("synthetic-a", ("slow", "mid")), ("synthetic-b", ("mid", "fast")))
INJECT_XOR = 0x5eed


def make_synthetic_run(run_dir, seed, label, speeds):
    """A complete synthetic run directory in the form the run-cell tool writes: two blocks of
    SYN_TRIALS_PER_BLOCK trials, one composition per trial (a quarter of them cancelled), a few arrow
    presses, and an observation log made by inject.py from the assembled ground truth. The ground truth is
    generated from the seed and the observation errors from the seed xor INJECT_XOR."""
    rng = random.Random(seed)
    os.mkdir(run_dir)
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

    rules = _read_regular(os.path.join(_HERE, "gt_rules.example.json"), "rules")
    sess = gt_sessions.assemble(gt_bytes, oracle_bytes, rules, plan_bytes)["definitions"]["macos_def"]
    obs_ime, _truth = inject.inject(sess, {"miss": 0.05, "split": 0.04, "merge": 0.04, "false_pos": 0.05},
                                    {"bias_ms": 20, "sd_ms": 10, "end_lag_ms_max": 30}, seed ^ INJECT_XOR)
    obs_rows = [{"type": "meta", "format": "obs/1", "os": "macos", "logger_version": "0.1.0",
                 "manifest_sha256": "0" * 64,
                 "capabilities": {"unconditional": ["key"], "threshold_gated": [], "config_gated": ["ime_shadow"]}}]
    keys = [{"type": "key", "t": WALL0 + t[2], "category": "alphabetic", "press": True} for t in trials]
    obs_rows += sorted(keys + obs_ime, key=lambda r: (r["t"], r["type"]))
    obs_bytes = _jl(obs_rows)

    logs = {"plan": plan_bytes, "oracle": oracle_bytes, "gt": gt_bytes, "obs": obs_bytes}
    outputs = {}
    for name in LOG_NAMES:
        _write_new(os.path.join(run_dir, LOG_FILES[name]), logs[name])
        outputs[name] = {"file": LOG_FILES[name], "sha256": _sha(logs[name]), "lines": logs[name].count(b"\n")}
    cell = {"os": "macos", "label": label, "ime": "synthetic", "ime_settings": {}, "refinput_cmd": ["synthetic-input", "{out}"],
            "logger_cmd": ["synthetic-logger", "{out}"], "reset_cmd": [], "focus_cmd": [], "ready_wait_ms": 0,
            "backend": "dryrun", "clock_sync_disabled": False, "auto_update_disabled": False}
    manifest = {"format": RUN_FORMAT, "runner_version": "synthetic", "emitter_version": "synthetic", "synthetic": True,
                "cell": cell, "plan_sha256": _sha(plan_bytes),
                "git_commit": None, "git_dirty": None, "host": {}, "started": None, "ended": None,
                "outputs": outputs, "children": {}, "resets": [], "focus": [], "aborted": False, "abort_reason": None}
    _write_new(os.path.join(run_dir, MANIFEST), _json_bytes(manifest))


def _write_new(path, data):
    with open(path, "xb") as fh:
        fh.write(data)


def make_synthetic(out_dir, seed):
    """Two synthetic run directories (run-a, run-b) under out_dir; returns their paths. An existing directory
    of the same name is never overwritten, and nothing is written under the results directory of the experiment."""
    if _is_under(out_dir, EXPERIMENT_RESULTS):
        raise InputError("synthetic runs must not be written under the results directory of the experiment")
    paths = [os.path.join(out_dir, "run-" + label[-1]) for label, _s in SYN_SPECS]
    for p in paths:
        if os.path.lexists(p):
            raise InputError("a run directory of that name already exists and is not overwritten")
    os.makedirs(out_dir, exist_ok=True)
    for i, ((label, speeds), p) in enumerate(zip(SYN_SPECS, paths)):
        make_synthetic_run(p, seed * 1000 + i, label, speeds)
    return paths


# ---------------------------------------------------------------- CLI

def _resolve_seed(args, ap):
    seed = args.seed
    if args.seed_file:
        from_file = read_seed_file(args.seed_file)
        if seed is not None and seed != from_file:
            ap.error("--seed differs from the seed file")
        seed = from_file
    return seed


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
    ap.add_argument("--seed-file")
    ap.add_argument("--out")
    ap.add_argument("--prereg", help="the pre-registration file (required for real data)")
    ap.add_argument("--freeze-hash", action="store_true", dest="freeze_hash",
                    help="print the value that the pre-registration records as sha256")
    ap.add_argument("--check-prereg", dest="check_prereg", metavar="PATH", help="check the freeze marks of a pre-registration")
    ap.add_argument("--synthetic")
    ap.add_argument("--check-deposit", nargs="+", dest="deposit")
    ap.add_argument("--pack", metavar="RUN_DIR")
    ap.add_argument("--also-user", action="append", default=[], dest="also_users", metavar="NAME")
    ap.add_argument("--also-home", action="append", default=[], dest="also_homes", metavar="PATH")
    ap.add_argument("--selftest", action="store_true",
                    help="fast default: a representative variant of every case (about 20 seconds)")
    ap.add_argument("--full", action="store_true",
                    help="with --selftest: run every variant of every case (about a minute)")
    args = ap.parse_args(argv)
    if args.full and not args.selftest:
        ap.error("--full is used together with --selftest")
    if args.selftest:
        global FULL
        FULL = args.full
        return selftest()
    res = None
    try:
        if args.freeze_hash or args.check_prereg:
            if not (args.config and args.seed_file):
                ap.error("--freeze-hash and --check-prereg need --config and --seed-file")
            if args.freeze_hash:
                print(freeze_hash(args.config, args.seed_file))
            else:
                check_prereg(args.check_prereg, args.config, args.seed_file)
                print("pipeline: the freeze marks are well formed and match the configuration, seed and rule files")
            return 0
        if args.deposit:
            return check_deposit(args.deposit, build_patterns(also_users=args.also_users, also_homes=args.also_homes))
        if args.pack:
            if not args.out:
                ap.error("--pack needs --out")
            return pack(args.pack, args.out, build_patterns(also_users=args.also_users, also_homes=args.also_homes))
        if args.synthetic:
            seed = _resolve_seed(args, ap)
            if seed is None:
                ap.error("--synthetic needs --seed")
            for p in make_synthetic(args.synthetic, seed):
                print("pipeline: wrote a synthetic run directory (%s)" % os.path.basename(p))
            return 0
        seed = _resolve_seed(args, ap)
        if not (args.config and args.out and seed is not None and bool(args.runs) != bool(args.runs_from)):
            ap.error("--config, --seed (or --seed-file), --out and exactly one of --runs / --runs-from are required")
        shas = None
        if args.runs:
            dirs = args.runs
        else:
            listed = read_runs_list(args.runs_from)
            dirs, shas = [d for d, _s in listed], [s for _d, s in listed]
        res = analyse(dirs, args.config, seed, args.out, args.prereg, args.seed_file, shas)
    except CheckFailed as e:
        for line in e.findings[:50]:
            print("pipeline: " + line, file=sys.stderr)
        if len(e.findings) > 50:
            print("pipeline: ...and %d more" % (len(e.findings) - 50), file=sys.stderr)
        print("pipeline: step 0 found %d violation(s); nothing was analysed" % len(e.findings), file=sys.stderr)
        return 1
    except NotFrozen as e:
        print("pipeline: not frozen: %s" % e, file=sys.stderr)
        return 3
    except (InputError, ValueError) as e:
        print("pipeline: %s" % e, file=sys.stderr)
        return 2
    except RecursionError:
        print("pipeline: an input is nested too deeply", file=sys.stderr)
        return 2
    except (KeyError, TypeError, AttributeError, IndexError) as e:
        print("pipeline: an input has an unexpected shape (%s)" % type(e).__name__, file=sys.stderr)
        return 2
    except OSError as e:
        print("pipeline: could not read or write a file (%s)" % type(e).__name__, file=sys.stderr)
        return 2
    except Exception as e:
        print("pipeline: unexpected internal error (%s); this is not a problem with the input's form" % type(e).__name__,
              file=sys.stderr)
        return 2
    r = res["l1"]["runs"]
    print("pipeline: %d run(s), %d aborted, %d analysed; results written" % (r["n"], r["n_aborted"], r["n_used"]))
    print("pipeline: cells used: %s" % ", ".join(sorted(res["l1"]["cells"])))
    return 0


# ---------------------------------------------------------------- selftest

FULL = False   # --selftest --full runs every variant of every case; the default runs a representative subset

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


def _seed_file(d, text="7\n"):
    path = os.path.join(d, "SEED")
    _write(path, text.encode("utf-8"))
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
    for k in [k for k, v in kw.items() if v is _DROP]:
        del m[k]
    _write(mp, _json_bytes(m))


_DROP = object()


def _real_runs(d, name, seed=2):
    """Synthetic runs without the synthetic mark (they stand in for real runs)."""
    runs = make_synthetic(os.path.join(d, name), seed)
    for r in runs:
        _set_manifest(r, synthetic=_DROP)
    return runs


def _case_synthetic_form(d):
    f = []
    runs = make_synthetic(os.path.join(d, "form"), 5)
    cell_tool = _tool("run_cell", "run", "run_cell.py")
    for p in runs:
        if sorted(os.listdir(p)) != sorted(DEPOSIT_FILES):
            f.append("a synthetic run directory does not hold exactly run.json and the four logs: %r" % sorted(os.listdir(p)))
        r = load_run(p)
        if r["aborted"] or not r["synthetic"] or r["label"] not in ("synthetic-a", "synthetic-b"):
            f.append("the manifest of a synthetic run is wrong: %r" % (r["label"],))
        try:
            cell_tool.check_cell(r["manifest"]["cell"])
        except Exception as e:
            f.append("the cell of a synthetic manifest is refused by the run-cell tool: %s" % type(e).__name__)
        bad = check_run(r, match._read(os.path.join(_HERE, "gt_rules.example.json"), "rules"))
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
    before = open(os.path.join(runs[0], MANIFEST), "rb").read()
    rc, _o, _e = _quiet(["--synthetic", os.path.join(d, "form"), "--seed", "9"])
    if rc != 2 or open(os.path.join(runs[0], MANIFEST), "rb").read() != before:
        f.append("an existing synthetic run directory was overwritten or not refused (rc %s)" % (rc,))
    target = os.path.join(EXPERIMENT_RESULTS, "selftest-refused")
    if _quiet(["--synthetic", target, "--seed", "1"])[0] != 2 or os.path.exists(target):
        f.append("a synthetic output under the results directory of the experiment was not refused")
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
        if o.get("synthetic") is not True:
            f.append("%s of synthetic runs is not marked synthetic" % name)
        if any(sorted(c) != ["all", "macos_def"] for c in o["cells"].values()):
            f.append("%s does not hold both the operating-system definition and the common definition per cell" % name)
        if any(not re.fullmatch(r"[0-9a-f]{64}", x.get("manifest_sha256", "")) for x in o["runs"]["list"]):
            f.append("%s lists a run without its manifest hash" % name)
    pooled = l1o["cells"]["synthetic-a"]["macos_def"]["metrics"]["pooled"]
    if not pooled["dwell"]["n"] > 30 or pooled["dwell"]["mae"] is None:
        f.append("level 1 has too few pairs in a synthetic cell: %r" % (pooled["dwell"]["n"],))
    if not l2o["cells"]["synthetic-a"]["macos_def"]["texts"]["n"] == 8:
        f.append("level 2 should hold 8 texts per synthetic cell: %r" % (l2o["cells"]["synthetic-a"]["macos_def"]["texts"]["n"],))
    det = deto["cells"]["synthetic-a"]["macos_def"]["metrics"]["pooled"]
    if det is None or not det["recall"]["value"] > 0.7 or not det["precision"]["value"] > 0.7:
        f.append("detection on a synthetic cell is implausibly low: %r" % (det and det["recall"]["value"],))
    # the seed matters, and the injected errors are visible (a run with no misses would not show them)
    if det is not None and det["n_miss"] + det["n_false_pos"] + det["n_split_gt"] + det["n_merge_obs"] == 0:
        f.append("no injected error reached the detection counts")
    if not FULL:
        return f
    o3 = os.path.join(d, "out3")
    if _quiet(["--runs"] + runs + ["--config", cfg, "--seed", "8", "--out", o3])[0] != 0 or _read_results(o3) == outs[0]:
        f.append("a different seed gives the same results")
    # the two matcher settings that used to be fixed reach the matcher
    o4 = os.path.join(d, "out4")
    cfg4 = _config_file(d, {"theta": 0.9, "drop_start_while_open": True})
    if _quiet(["--runs"] + runs + ["--config", cfg4, "--seed", "7", "--out", o4])[0] != 0:
        f.append("a configuration with theta and drop_start_while_open was refused")
    elif json.loads(_read_results(o4)["e1_detection.json"].decode("utf-8"))["cells"]["synthetic-a"]["macos_def"]["config"].get("theta") != 0.9:
        f.append("theta from the configuration did not reach the matcher")
    return f


def _case_labels_and_hashes(d):
    f = []
    cfg = _config_file(d)
    runs = make_synthetic(os.path.join(d, "abt"), 4)
    _set_manifest(runs[1], aborted=True, abort_reason="synthetic")
    o = os.path.join(d, "outa")
    rc, _o, err = _quiet(["--runs"] + runs + ["--config", cfg, "--seed", "1", "--out", o])
    res = json.loads(open(os.path.join(o, "e1_l1.json"), "rb").read().decode("utf-8")) if rc == 0 else None
    if rc != 0 or sorted(res["cells"]) != ["synthetic-a"] or res["runs"]["n_aborted"] != 1 or res["runs"]["n_used"] != 1:
        f.append("an aborted run is not left out and counted (rc %d): %s" % (rc, err[-200:]))
    if res and [x["aborted"] for x in res["runs"]["list"]] != [False, True]:
        f.append("the run list does not say which run was aborted")
    if FULL:
        # an aborted run may share the label of the run that replaced it, and is counted
        runs1 = make_synthetic(os.path.join(d, "abt1"), 4)
        m0 = json.loads(open(os.path.join(runs1[0], MANIFEST), "rb").read().decode("utf-8"))
        _set_manifest(runs1[1], cell=dict(m0["cell"]), aborted=True, abort_reason="synthetic")
        rc, _o, err = _quiet(["--runs"] + runs1 + ["--config", cfg, "--seed", "1", "--out", os.path.join(d, "outa1")])
        if rc != 0:
            f.append("an aborted run with the label of a finished run was refused (rc %d): %s" % (rc, err[-200:]))
    # a log that no longer matches its recorded hash stops the run (exit 2)
    runs2 = make_synthetic(os.path.join(d, "abt2"), 4)
    with open(os.path.join(runs2[0], "obs.jsonl"), "ab") as fh:
        fh.write(b"\n")
    rc = _quiet(["--runs"] + runs2 + ["--config", cfg, "--seed", "1", "--out", os.path.join(d, "outb")])[0]
    if rc != 2:
        f.append("a log that changed after the run was accepted (rc %d)" % rc)
    if os.path.exists(os.path.join(d, "outb", "e1_l1.json")):
        f.append("a result was written although the run stopped")
    # two runs that were not aborted with one label are refused
    runs3 = make_synthetic(os.path.join(d, "abt3"), 4)
    m = json.loads(open(os.path.join(runs3[1], MANIFEST), "rb").read().decode("utf-8"))
    _set_manifest(runs3[1], cell=dict(m["cell"], label="synthetic-a"))
    if _quiet(["--runs"] + runs3 + ["--config", cfg, "--seed", "1", "--out", os.path.join(d, "outc")])[0] != 2:
        f.append("two runs with the same cell label were accepted")
    # a cell without a label is refused, and the operating system is not used in its place
    runs4 = make_synthetic(os.path.join(d, "abt4"), 4)
    m = json.loads(open(os.path.join(runs4[0], MANIFEST), "rb").read().decode("utf-8"))
    nolabel = dict((k, v) for k, v in m["cell"].items() if k != "label")
    _set_manifest(runs4[0], cell=nolabel)
    rc, _o, err = _quiet(["--runs"] + runs4 + ["--config", cfg, "--seed", "1", "--out", os.path.join(d, "outd")])
    if rc != 2 or "label" not in err:
        f.append("a cell without a label was accepted or not explained (rc %d)" % rc)
    if FULL:
        # a recorded hash that is not 64 lowercase hex digits is refused, also for an aborted run
        runs5 = make_synthetic(os.path.join(d, "abt5"), 4)
        m = json.loads(open(os.path.join(runs5[1], MANIFEST), "rb").read().decode("utf-8"))
        m["outputs"]["obs"]["sha256"] = "ABC"
        _set_manifest(runs5[1], outputs=m["outputs"], aborted=True)
        if _quiet(["--runs"] + runs5 + ["--config", cfg, "--seed", "1", "--out", os.path.join(d, "oute")])[0] != 2:
            f.append("a malformed recorded hash of an aborted run was accepted")
    return f


def _case_step_zero(d):
    f = []
    cfg = _config_file(d)

    def rc_of(run_dirs, out):
        return _quiet(["--runs"] + run_dirs + ["--config", cfg, "--seed", "1", "--out", os.path.join(d, out)])

    base = make_synthetic(os.path.join(d, "s0"), 2)[:1]
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
    if FULL:
        # a header that does not declare ime_shadow is refused
        base2 = make_synthetic(os.path.join(d, "s0b"), 2)
        lines = open(os.path.join(base2[0], "obs.jsonl"), "rb").read().split(b"\n", 1)
        hdr = json.loads(lines[0].decode("utf-8"))
        hdr["capabilities"]["config_gated"] = []
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
    # a gated channel that produced no row, although the ground truth holds sessions, cannot be judged
    base4 = make_synthetic(os.path.join(d, "s0d"), 2)
    rows = [ln for ln in open(os.path.join(base4[0], "obs.jsonl"), "rb").read().split(b"\n") if ln and b'"type":"ime_shadow"' not in ln]
    _rewrite_log(base4[0], "obs", b"\n".join(rows) + b"\n")
    rc, _o, err = rc_of(base4, "o4")
    if rc != 1 or "gated and produced no row" not in err:
        f.append("a gated channel with no row was accepted or not explained (rc %d)" % rc)
    if FULL:
        # a header that names the channel as unconditional is not held to that rule
        hdr2 = json.loads(rows[0].decode("utf-8"))
        hdr2["capabilities"] = {"unconditional": ["key", "ime_shadow"], "threshold_gated": [], "config_gated": []}
        rows[0] = json.dumps(hdr2, separators=(",", ":")).encode("utf-8")
        _rewrite_log(base4[0], "obs", b"\n".join(rows) + b"\n")
        if rc_of(base4, "o5")[0] != 0:
            f.append("an unconditional channel with no row was refused")
        # a first line nested too deeply is reported, not a crash
        base5 = make_synthetic(os.path.join(d, "s0e"), 2)
        lines = open(os.path.join(base5[0], "obs.jsonl"), "rb").read().split(b"\n", 1)
        _rewrite_log(base5[0], "obs", b"[" * 100000 + b"]" * 100000 + b"\n" + lines[1])
        rc, _o, err = rc_of(base5, "o6")
        if rc not in (1, 2) or "Traceback" in err:
            f.append("a deeply nested first line was not reported cleanly (rc %s)" % (rc,))
    return f


def _prereg_text(sha, extra=""):
    return "# Pre-registration\n\nfrozen_at: 2026-01-01\nsha256: %s\n%s" % (sha, extra)


def _case_freeze_gate(d):
    f = []
    cfg = _config_file(d)
    seedf = _seed_file(d)
    good = freeze_hash(cfg, seedf)
    if not re.fullmatch(r"[0-9a-f]{64}", good):
        return ["the freeze hash is not 64 hex digits"]
    rc, out, _e = _quiet(["--freeze-hash", "--config", cfg, "--seed-file", seedf])
    if rc != 0 or out.strip() != good:
        f.append("--freeze-hash does not print the value")
    rules = open(os.path.join(_HERE, "gt_rules.example.json"), "rb").read()
    want = _sha(("%s\n%s\n%s\n" % (_sha(open(cfg, "rb").read()), _sha(open(seedf, "rb").read()), _sha(rules))).encode("ascii"))
    if want != good:
        f.append("the freeze hash is not defined as the hash of the three file hashes, each followed by a line feed")
    runs = _real_runs(d, "gate")[:1]
    pr = os.path.join(d, "preregistration.md")

    def analyse_rc(name, with_prereg=True):
        argv = ["--runs"] + runs + ["--config", cfg, "--seed-file", seedf, "--out", os.path.join(d, name)]
        if with_prereg:
            argv += ["--prereg", pr]
        return _quiet(argv)[0]

    def check_rc(cli=FULL):
        if cli:
            return _quiet(["--check-prereg", pr, "--config", cfg, "--seed-file", seedf])[0]
        try:   # the default runs the check in-process; the command line is exercised by the other calls
            check_prereg_text(open(pr, "rb").read().decode("utf-8"), good)
            return 0
        except NotFrozen:
            return 3

    if analyse_rc("g0", False) != 3:
        f.append("real data was analysed without --prereg")
    if FULL and (analyse_rc("g1") != 3 or check_rc() != 3):
        f.append("real data was analysed although the pre-registration file does not exist")
    zero = "0" * 64
    negatives = (
        ("no marks", "# Pre-registration\n"),
        ("placeholders", "frozen_at: (to be filled in)\nsha256: (to be filled in)\n"),
        ("empty values", "frozen_at:\nsha256:\n"),
        ("marks inside a multi-line comment", "<!--\nfrozen_at: 2026-01-01\nsha256: %s\n-->\n" % good),
        ("marks inside a code fence", "```\nfrozen_at: 2026-01-01\nsha256: %s\n```\n" % good),
        ("marks inside a tilde fence", "~~~\nfrozen_at: 2026-01-01\nsha256: %s\n~~~\n" % good),
        ("a second frozen_at line", _prereg_text(good, "frozen_at: 2026-02-02\n")),
        ("a second sha256 line", _prereg_text(good, "sha256: %s\n" % good)),
        ("a sha256 that does not match", _prereg_text(zero)),
        ("an upper-case sha256", _prereg_text(good.upper())),
        ("a frozen_at without a date", "frozen_at: soon\nsha256: %s\n" % good),
        ("an unclosed comment", "<!-- start\nfrozen_at: 2026-01-01\nsha256: %s\n" % good),
    )
    representative = ("placeholders", "marks inside a multi-line comment", "marks inside a code fence",
                      "a second frozen_at line", "a sha256 that does not match")
    for i, (name, text) in enumerate(negatives):
        if not FULL and name not in representative:
            continue
        _write(pr, text.encode("utf-8"))
        if check_rc() != 3 or ((i % 3 == 0 if FULL else name == "a sha256 that does not match") and analyse_rc("g2") != 3):
            f.append("the freeze gate accepted: %s" % name)
        if os.path.exists(os.path.join(d, "g2", "e1_l1.json")):
            f.append("a result was written when the gate refused: %s" % name)
    positives = (("well-formed marks", _prereg_text(good)),
                 ("marks with a comment and a fence elsewhere", "<!-- note -->\n```\nx\n```\n" + _prereg_text(good)),
                 ("marks with CRLF line ends", _prereg_text(good).replace("\n", "\r\n")))
    for i, (name, text) in enumerate(positives):
        _write(pr, text.encode("utf-8"))
        if i > 0 and not FULL:
            break
        rc = analyse_rc("g3") if i == 0 else 0
        if rc != 0 or (FULL and check_rc() != 0):
            f.append("the freeze gate refused: %s (rc %s)" % (name, rc))
    # the analysis settings changed by one byte after the freeze
    _write(pr, _prereg_text(good).encode("utf-8"))
    with open(cfg, "ab") as fh:
        fh.write(b" ")
    if check_rc(True) != 3 or (FULL and analyse_rc("g4") != 3):
        f.append("a configuration that changed by one byte after the freeze was accepted")
    if FULL:
        _write(cfg, open(cfg, "rb").read()[:-1])
        _write(seedf, b"8\n")
        if analyse_rc("g5") not in (2, 3):
            f.append("a seed that changed after the freeze was accepted")
    return f


def _case_run_sh(d):
    f = []
    bash = shutil.which("bash")
    if bash is None or not os.path.isfile(os.path.join(os.path.dirname(KIT), "experiment", "run.sh")):
        return f
    root = os.path.join(d, "tree")
    shutil.copytree(KIT, os.path.join(root, "kit"), ignore=shutil.ignore_patterns("target", ".build", "__pycache__", "logger", "e2", "refinput-macos", "refinput-windows", "pilot", "corpus"))
    exp = os.path.join(root, "experiment")
    os.makedirs(exp)
    shutil.copyfile(os.path.join(os.path.dirname(KIT), "experiment", "run.sh"), os.path.join(exp, "run.sh"))
    _write(os.path.join(exp, "config.json"), json.dumps({"bootstrap_B": 100, "gt_rules": "../kit/analysis/gt_rules.example.json"}).encode("utf-8"))
    _write(os.path.join(exp, "SEED"), b"7\n")
    runs = _real_runs(root, "runs")[:1]
    lines = "".join("- run_dir: ../runs/%s  manifest_sha256: %s\n" % (os.path.basename(r), _sha(open(os.path.join(r, MANIFEST), "rb").read()))
                    for r in runs)
    _write(os.path.join(exp, "data.md"), ("# Data\n\n" + lines).encode("utf-8"))
    env = dict(os.environ, IME_RESULTS_DIR=os.path.join(root, "res"), PYTHONUTF8="1")

    def sh(*args):
        try:
            return subprocess.run([bash, "experiment/run.sh"] + list(args), cwd=root, env=env, stdin=subprocess.DEVNULL,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=170).returncode
        except (OSError, subprocess.SubprocessError):
            return None

    pr = os.path.join(exp, "preregistration.md")
    if sh() != 3:
        f.append("run.sh ran without a pre-registration file")
    good = freeze_hash(os.path.join(exp, "config.json"), os.path.join(exp, "SEED"))
    variants = (("no marks", "# Pre-registration\n"), ("placeholders", "frozen_at: (to be filled in)\nsha256: (to be filled in)\n"),
                       ("empty values", "frozen_at:\nsha256:\n"), ("marks in a comment", "<!--\nfrozen_at: 2026-01-01\nsha256: %s\n-->\n" % good),
                       ("marks in a fence", "```\nfrozen_at: 2026-01-01\nsha256: %s\n```\n" % good),
                       ("two frozen_at lines", _prereg_text(good, "frozen_at: 2026-02-02\n")),
                       ("a sha256 that does not match", _prereg_text("0" * 64)))
    for name, text in variants:
        if not FULL and name != "a sha256 that does not match":
            continue
        _write(pr, text.encode("utf-8"))
        if sh() != 3:
            f.append("run.sh accepted: %s" % name)
    _write(pr, _prereg_text(good).encode("utf-8"))
    rc = sh()
    if rc != 0 or not os.path.isfile(os.path.join(root, "res", "e1_l1.json")):
        f.append("run.sh refused well-formed marks (rc %s)" % (rc,))
    if not FULL:
        return f
    with open(os.path.join(exp, "config.json"), "ab") as fh:
        fh.write(b" ")
    if sh() != 3:
        f.append("run.sh accepted a configuration that changed after the freeze")
    _write(os.path.join(exp, "SEED"), b"1 2\n")
    if sh("--synthetic") != 2:
        f.append("run.sh accepted a seed file with two integers")
    return f


def _case_deposit_paths(d):
    f = []
    runs = make_synthetic(os.path.join(d, "dep"), 2)
    home, repo, user = "C:\\Users\\alice", "/work/ime-repo", "alice"
    pats = build_patterns(home, user, repo)
    files = read_run_files(runs[0])
    if scan_files(files, pats):
        f.append("a clean synthetic run directory has findings")
    m = json.loads(files[MANIFEST].decode("utf-8"))

    def kinds_of(text, patterns=pats):
        mm = dict(files)
        mm[MANIFEST] = _json_bytes(dict(m, note=text))
        return sorted(set(k for _f, _n, k in scan_files(mm, patterns)))

    ap_, hd, rp, ln = "absolute path", "home directory", "repository path", "login name"
    cases = (("the home directory (backslashes, as a JSON string spells them)", "started at C:\\Users\\alice\\work", [ap_, hd, ln]),
             ("the home directory (slashes)", "started at C:/Users/alice/work", [ap_, hd, ln]),
             ("the home directory (MSYS spelling)", "started at /c/Users/alice/work", [ap_, hd, ln]),
             ("the repository path", "cwd /work/ime-repo/papers", [rp]),
             ("the login name", "written by alice on this machine", [ln]),
             ("a drive path of another user", "C:\\Users\\bob\\x", [ap_]),
             ("a short (8.3) name in a drive path", "C:\\Users\\YAMADA~1\\x", [ap_]),
             ("a short (8.3) name in an MSYS path", "/c/Users/YAMADA~1/x", [ap_]),
             ("a drive path with slashes", "D:/data/x", [ap_]),
             ("a UNC path", "\\\\server\\share\\x", [ap_]),
             ("a UNC path with slashes", "//server/share/x", [ap_]),
             ("a macOS home", "/Users/carol/x", [ap_]),
             ("a Linux home", "/home/dave/x", [ap_]),
             ("a mounted volume", "/Volumes/DISK/x", [ap_]),
             ("an MSYS drive", "/d/work/x", [ap_]),
             ("a path after a colon", "PATH=/usr/bin:/home/erin/bin", [ap_]))
    for name, text, want in cases:
        got = kinds_of(text)
        if got != sorted(want):
            f.append("%s is reported as %r, expected %r" % (name, got, sorted(want)))
    # an escape that a JSON string uses for a separator is decoded before the search
    mm = dict(files)
    for name, spelling in (("unicode escapes", b"\\u002fhome\\u002falice"), ("escaped slashes", b"\\/home\\/alice"),
                           ("a drive with a unicode escape", b"C:\\u005cx")):
        mm[MANIFEST] = files[MANIFEST].replace(b'"format"', b'"note":"' + spelling + b'","format"', 1)
        if [k for _f, _n, k in scan_files(mm, pats)] != [ap_]:
            f.append("a path spelled with %s was not found" % name)
    for name, text in (("replaced paths", "started at ~/work in <repo>/papers"), ("replaced paths with backslashes", "~\\\\work <repo>\\\\kit"),
                       ("a name inside a longer word", "alicesprings"), ("a relative path", "kit/analysis/x kit\\\\analysis"),
                       ("an address", "see http://example.org/a/b"), ("a fraction", "and/or a/b 1/2/3"),
                       ("a relative path that contains a root name", "kit/home/x ./Users/y ../mnt/z")):
        if kinds_of(text):
            f.append("%s was reported: %r" % (name, kinds_of(text)))
    if kinds_of("alice", build_patterns(home, "al", repo)):
        f.append("a login name shorter than %d characters was searched for" % MIN_NAME_LEN)
    # names and homes of the measuring machine
    extra = build_patterns(home, user, repo, ["frank"], ["E:\\Users\\gina"])
    if kinds_of("by frank", extra) != [ln] or kinds_of("E:\\Users\\gina\\x", extra) != [ap_, hd]:
        f.append("--also-user / --also-home were not searched for")
    try:
        build_patterns(home, user, repo, ["zz"])
        f.append("a two-character --also-user name was accepted")
    except InputError:
        pass
    # a finding in a log is reported with its line, and the standard-error files are not read
    _write(os.path.join(runs[0], "reset.stderr.txt"), b"/work/ime-repo alice\n")
    if scan_files(read_run_files(runs[0]), pats):
        f.append("a standard-error file was read")
    with open(os.path.join(runs[0], "gt.jsonl"), "ab") as fh:
        fh.write(b'{"note":"/work/ime-repo/x"}\n')
    n_lines = open(os.path.join(runs[0], "gt.jsonl"), "rb").read().count(b"\n")
    if scan_files(read_run_files(runs[0]), pats) != [("gt.jsonl", n_lines, "repository path")]:
        f.append("a finding in a log is not reported with its file and line")
    return f


def _case_deposit_runs(d):
    f = []
    runs = make_synthetic(os.path.join(d, "dr"), 2)
    m = json.loads(open(os.path.join(runs[1], MANIFEST), "rb").read().decode("utf-8"))
    # the command line: exit 1 with the real home directory, 0 once it is replaced
    real = os.path.expanduser("~")
    if len(real.rstrip("/\\")) >= 2 and real != "~":
        _write(os.path.join(runs[1], MANIFEST), _json_bytes(dict(m, note="in " + real + "/x")))
        rc, _o, err = _quiet(["--check-deposit", runs[1]])
        if rc != 1 or real in err:
            f.append("the real home directory was not refused, or was echoed (rc %d)" % rc)
    # a path directly under the default repository root is refused, and the value is not echoed
    root = repo_root()
    _write(os.path.join(runs[1], MANIFEST), _json_bytes(dict(m, note="cwd " + os.path.join(root, "papers"))))
    rc, _o, err = _quiet(["--check-deposit", runs[1]])
    if rc != 1 or root in err:
        f.append("an absolute path under the default repository root was not refused (rc %d)" % rc)
    if "repository path" not in [k for _f, _n, k in scan_files(read_run_files(runs[1]), build_patterns(home="~", user=""))]:
        f.append("the default repository root is not searched for")
    _write(os.path.join(runs[1], MANIFEST), _json_bytes(dict(m, note="in ~/x and <repo>/y")))
    if _quiet(["--check-deposit", runs[1]])[0] != 0:
        f.append("a manifest with the paths replaced by ~ and <repo> was refused")
    _write(os.path.join(runs[1], MANIFEST), _json_bytes(m))
    if FULL:
        if _quiet(["--check-deposit", runs[1], "--also-user", "synthetic"])[0] != 1:
            f.append("--also-user was not applied on the command line")
        if _quiet(["--check-deposit", os.path.join(d, "no-such-dir")])[0] != 2:
            f.append("a missing run directory should exit 2")
    # a log that changed after the run exits 2; a missing log whose hash is recorded exits 2
    with open(os.path.join(runs[1], "gt.jsonl"), "ab") as fh:
        fh.write(b"\n")
    if _quiet(["--check-deposit", runs[1]])[0] != 2:
        f.append("a log that changed after the run was not refused by the deposit check")
    os.remove(os.path.join(runs[1], "gt.jsonl"))
    if _quiet(["--check-deposit", runs[1]])[0] != 2:
        f.append("a missing log with a recorded hash was accepted")
    # the archive (the second run directory is used up by now, so the first one is packed)
    good = runs[0]
    m0 = json.loads(open(os.path.join(good, MANIFEST), "rb").read().decode("utf-8"))
    arch1, arch2 = os.path.join(d, "a1.zip"), os.path.join(d, "a2.zip")
    rc1, out1, _e = _quiet(["--pack", good, "--out", arch1])
    rc2, out2, _e = _quiet(["--pack", good, "--out", arch2])
    if rc1 != 0 or rc2 != 0 or open(arch1, "rb").read() != open(arch2, "rb").read():
        f.append("packing the same run twice does not give the same bytes (rc %s, %s)" % (rc1, rc2))
    else:
        data = open(arch1, "rb").read()
        if _sha(data) not in out1:
            f.append("--pack does not print the SHA-256 of the archive")
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            infos = zf.infolist()
            if [i.filename for i in infos] != list(DEPOSIT_FILES) or any(i.date_time != ZIP_TIME for i in infos):
                f.append("the archive does not hold the five files in the fixed order with fixed times")
            if any(zf.read(i.filename) != open(os.path.join(good, i.filename), "rb").read() for i in infos):
                f.append("the archive holds different bytes from the run directory")
    before = open(arch1, "rb").read()
    if _quiet(["--pack", good, "--out", arch1])[0] != 2 or open(arch1, "rb").read() != before:
        f.append("an existing archive was overwritten or not refused")
    _write(os.path.join(good, MANIFEST), _json_bytes(dict(m0, note="/home/harry/x")))
    arch3 = os.path.join(d, "a3.zip")
    if _quiet(["--pack", good, "--out", arch3])[0] != 1 or os.path.exists(arch3):
        f.append("a run with an absolute path was packed")
    _write(os.path.join(good, "reset.stderr.txt"), b"x\n")
    _write(os.path.join(good, MANIFEST), _json_bytes(m0))
    if _quiet(["--pack", good, "--out", arch3])[0] != 0:
        f.append("a clean run was not packed")
    elif "reset.stderr.txt" in zipfile.ZipFile(arch3).namelist():
        f.append("a standard-error file was packed")
    # content in a log of a run that was not aborted is refused (with the hash updated, so only content is at fault)
    obs = open(os.path.join(good, "obs.jsonl"), "rb").read()
    _rewrite_log(good, "obs", obs + b'{"type":"key","t":1700000000001,"category":"alphabetic","press":true,"char":"a"}\n')
    rc, _o, err = _quiet(["--check-deposit", good])
    if rc != 1 or "obs.jsonl" not in err:
        f.append("content in an observation log passed the deposit check (rc %d)" % rc)
    # an aborted run whose manifest recorded no hash for a log need not have it
    ma = json.loads(open(os.path.join(good, MANIFEST), "rb").read().decode("utf-8"))
    for name in ("gt", "obs"):
        ma["outputs"][name]["sha256"] = None
        os.remove(os.path.join(good, LOG_FILES[name]))
    _set_manifest(good, outputs=ma["outputs"], aborted=True)
    if _quiet(["--check-deposit", good])[0] != 0:
        f.append("an aborted run without the logs that it recorded as absent was refused")
    if FULL:
        os.remove(os.path.join(good, MANIFEST))
        if _quiet(["--check-deposit", good])[0] != 2:
            f.append("a run directory without run.json was accepted")
    return f


def _case_lists_seeds_files(d):
    f = []
    if _quiet([])[0] != 2:
        f.append("no arguments should exit 2")
    runs = make_synthetic(os.path.join(d, "use"), 2)
    for name, body in (("an unknown key", {"nope": 1}), ("a bad bootstrap size", {"bootstrap_B": 0}),
                       ("a bad overlap threshold", {"iou_min": 2}), ("a bad theta", {"theta": "x"}),
                       ("a bad drop flag", {"drop_start_while_open": 1})):
        cfg = _config_file(d, body)
        rc = _quiet(["--runs"] + runs + ["--config", cfg, "--seed", "1", "--out", os.path.join(d, "outu")])[0]
        if rc != 2:
            f.append("a configuration with %s was accepted (rc %d)" % (name, rc))
    no_rules = os.path.join(d, "no-rules.json")
    _write(no_rules, b'{"bootstrap_B": 10}')
    if _quiet(["--runs"] + runs + ["--config", no_rules, "--seed", "1", "--out", os.path.join(d, "outu")])[0] != 2:
        f.append("a configuration without gt_rules was accepted")
    shas = [_sha(open(os.path.join(r, MANIFEST), "rb").read()) for r in runs]
    listing = os.path.join(d, "list.md")
    text = ("notes\n<!--\n- run_dir: %s\n-->\n```\n- run_dir: %s\n```\n- run_dir: %s  manifest_sha256: %s\n"
            "<!-- - run_dir: %s -->\n- run_dir: %s  manifest_sha256: %s\n" % (runs[0], runs[1], runs[0], shas[0], runs[1], runs[1], shas[1]))
    _write(listing, text.encode("utf-8"))
    cfg = _config_file(d)
    o = os.path.join(d, "outl")
    rc, out, err = _quiet(["--runs-from", listing, "--config", cfg, "--seed", "7", "--out", o])
    if rc != 0:
        f.append("--runs-from did not run (rc %s): %s" % (rc, err[-200:]))
    elif "synthetic-a, synthetic-b" not in out:
        f.append("--runs-from did not print the labels that were used")
    if FULL:
        o2 = os.path.join(d, "outl2")
        _quiet(["--runs"] + runs + ["--config", cfg, "--seed", "7", "--out", o2])
        if _read_results(o) != _read_results(o2):
            f.append("--runs-from and --runs give different results")
        if _quiet(["--runs-from", listing, "--runs"] + runs + ["--config", cfg, "--seed", "7", "--out", o])[0] != 2:
            f.append("--runs together with --runs-from was accepted")
    for name, body in (("a line without the manifest hash", "- run_dir: %s\n" % runs[0]),
                       ("a different manifest hash", "- run_dir: %s  manifest_sha256: %s\n" % (runs[0], "0" * 64)),
                       ("a malformed manifest hash", "- run_dir: %s  manifest_sha256: xyz\n" % runs[0])):
        _write(listing, body.encode("utf-8"))
        if _quiet(["--runs-from", listing, "--config", cfg, "--seed", "7", "--out", os.path.join(d, "outl3")])[0] != 2:
            f.append("--runs-from accepted %s" % name)
    if FULL:
        # the seed file: exactly one integer, no spaces
        for name, body, ok in (("one integer", "5\n", True), ("no line end", "5", True), ("two integers", "1 2\n", False),
                               ("spaces around", " 5\n", False), ("two lines", "5\n6\n", False), ("empty", "", False),
                               ("a sign", "-5\n", False), ("a word", "five\n", False)):
            p = _seed_file(d, body)
            try:
                read_seed_file(p)
                got = True
            except InputError:
                got = False
            if got != ok:
                f.append("the seed file check is wrong for %s" % name)
        if _quiet(["--runs"] + runs + ["--config", cfg, "--seed", "5", "--seed-file", _seed_file(d, "6\n"), "--out", os.path.join(d, "outs")])[0] != 2:
            f.append("--seed that differs from --seed-file was accepted")
    # a failure to write a result leaves no result of an earlier run
    of = o
    if not os.path.isfile(os.path.join(of, "e1_l1.json")):
        f.append("the first analysis failed")
    else:
        os.remove(os.path.join(of, "e1_detection.json"))
        os.mkdir(os.path.join(of, "e1_detection.json"))
        rc = _quiet(["--runs"] + runs + ["--config", cfg, "--seed", "7", "--out", of])[0]
        if rc != 2 or os.path.exists(os.path.join(of, "e1_l1.json")) or os.path.exists(os.path.join(of, "e1_l2.json")):
            f.append("a stale result was left after a failed write (rc %s)" % (rc,))
        if [n for n in os.listdir(of) if n.startswith(".pipeline_tmp_")]:
            f.append("a temporary directory was left in the results directory")
    if FULL:
        # synthetic results are not written under the results directory of the experiment
        if _quiet(["--runs"] + runs + ["--config", cfg, "--seed", "7", "--out", os.path.join(EXPERIMENT_RESULTS, "selftest-refused")])[0] != 2 \
                or os.path.exists(os.path.join(EXPERIMENT_RESULTS, "selftest-refused")):
            f.append("synthetic results were written under the results directory of the experiment")
    # input files: a link is refused, and there is an upper limit on the size
    target = os.path.join(d, "target.jsonl")
    _write(target, b"x\n")
    if FULL:
        link = os.path.join(d, "link.jsonl")
        try:
            os.symlink(target, link)
        except (OSError, NotImplementedError, AttributeError):
            link = None
        if link is not None:
            try:
                _read_regular(link, "link")
                f.append("a symbolic link was read")
            except InputError:
                pass
    global MAX_FILE_BYTES
    saved, MAX_FILE_BYTES = MAX_FILE_BYTES, 1
    try:
        _read_regular(target, "big")
        f.append("a file above the size limit was read")
    except InputError:
        pass
    finally:
        MAX_FILE_BYTES = saved
    try:
        _read_regular(d, "directory")
        f.append("a directory was read as a file")
    except InputError:
        pass
    return f


CASES = [
    ("synthetic run directories (form, cell accepted by the run-cell tool, determinism, seed, no overwrite)", _case_synthetic_form),
    ("one command reproduces the results (byte-identical, no paths, both definitions, seed matters)", _case_reproduces),
    ("labels come from the cell; aborted runs are counted; a changed log or a shared label stops the run", _case_labels_and_hashes),
    ("step 0 refuses content, a missing channel, an invalid plan and a gated channel with no row", _case_step_zero),
    ("the freeze gate of the analysis (well-formed marks, comments, fences, duplicates, changed settings)", _case_freeze_gate),
    ("the freeze gate of the shell entry point", _case_run_sh),
    ("deposit check: absolute paths, home directories, login names, escapes, lines, stderr files", _case_deposit_paths),
    ("deposit check and archive: hashes, aborted runs, content, deterministic archive, no overwrite", _case_deposit_runs),
    ("usage, configuration, runs list, seed file, failed writes and input files", _case_lists_seeds_files),
]


def selftest():
    global _READ_CACHE
    _READ_CACHE = {}
    try:
        return _selftest()
    finally:
        _READ_CACHE = None


def _selftest():
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
