#!/usr/bin/env python3
# kit: selftest
"""Scenario emitter: plays a ``plan/1`` file through a key-sending backend and writes an ``oracle/1`` log.

  emit.py --plan PLAN --out ORACLE --backend dryrun|macos|windows [--backend-opt k=v ...]
  emit.py --validate ORACLE
  emit.py --selftest

The emitter waits only for the intervals the plan gives (``gap_before_ms``, ``marker_gap_ms``, and the
per-step ``at_ms``); it never chooses an interval itself. Every key it sends is recorded with the wall-clock
and monotonic time taken immediately before dispatch, so the oracle states what was intended and when it was
actually sent. The oracle is used only to verify the observed ground truth, never as an input to an observer.

Sending is opt-in. A backend that posts real key events is refused with exit status 2 unless the flag named
by ``SEND_FLAG`` is given, and no output file is created in that case. Synthetic keys go to the application
that is in front, so run a real backend only against a prepared target window.

Library use (an orchestrator that also resets the input method between blocks)::

    with Emitter(backend, out_path, plan_sha256, os_name, backend_name) as em:
        em.write_reset(block_id, exit_code)
        em.run_block(block, trials)

The context manager opens the backend on entry and always closes it on exit, including after an exception.

Backend contract (``backend_<name>.py``): ``SUPPORTED_KEYS`` (a frozenset of key names, pseudo-keys
included) and a ``Backend`` class with ``__init__(opts)`` (unknown options raise), ``open()``, ``send(key, down)``,
and ``close()``. A plan that uses a key outside ``SUPPORTED_KEYS`` is refused before anything is sent.

Exit status: 0 success / 1 validation failed or a run failed / 2 the run was refused or could not start.
"""
import argparse
import hashlib
import contextlib
import importlib.util
import io
import json
import os
import re
import sys
import tempfile
import time

EMITTER_VERSION = "1"
SEND_FLAG = "--i-understand-this-sends-keys"
HERE = os.path.dirname(os.path.abspath(__file__))
BACKENDS = ("dryrun", "macos", "windows")
OS_NAMES = ("macos", "windows")
SPIN_SECONDS = 0.002
VERSION_RE = re.compile(r"^[0-9A-Za-z.+-]{1,32}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
KEYS_OF_KIND = {
    "block_begin": ("block_id",),
    "block_end": ("block_id",),
    "trial_begin": ("trial_id",),
    "trial_end": ("trial_id",),
    "sent": ("trial_id", "step", "key", "down"),
    "marker": ("block_id", "seq"),
    "reset": ("block_id", "exit_code"),
}
TIME_KEYS = ("t_wall_ms", "t_mono_ns")


class PlanError(Exception):
    pass


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _dumps(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


# ------------------------------------------------------------------ plan

def read_plan(path):
    """Return (sha256 of the file bytes, header, [(block, [trial, ...]), ...]); raise PlanError."""
    with open(path, "rb") as f:
        raw = f.read()
    sha = hashlib.sha256(raw).hexdigest()
    header, blocks = None, []
    for n, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError:
            raise PlanError("line %d: not JSON" % n)
        if not isinstance(row, dict):
            raise PlanError("line %d: not an object" % n)
        kind = row.get("kind")
        if header is None:
            if kind != "header" or row.get("format") != "plan/1" or row.get("os") not in OS_NAMES:
                raise PlanError("line %d: the first row must be a plan/1 header with a known os" % n)
            header = row
        elif kind == "block":
            if not _is_int(row.get("block_id")) or not isinstance(row.get("marker", []), list):
                raise PlanError("line %d: malformed block row" % n)
            if not all(isinstance(k, str) for k in row.get("marker", [])):
                raise PlanError("line %d: marker must list key names" % n)
            if not all(_is_int(row.get(k, 0)) and row.get(k, 0) >= 0 for k in ("marker_gap_ms",)):
                raise PlanError("line %d: marker_gap_ms must be a non-negative integer" % n)
            blocks.append((row, []))
        elif kind == "trial":
            if not blocks:
                raise PlanError("line %d: a trial precedes every block" % n)
            if row.get("block_id") != blocks[-1][0]["block_id"]:
                raise PlanError("line %d: block_id differs from the preceding block row" % n)
            if not isinstance(row.get("trial_id"), str):
                raise PlanError("line %d: trial_id must be a string" % n)
            if not (_is_int(row.get("gap_before_ms", 0)) and row.get("gap_before_ms", 0) >= 0):
                raise PlanError("line %d: gap_before_ms must be a non-negative integer" % n)
            prev = 0
            steps = row.get("steps")
            if not isinstance(steps, list):
                raise PlanError("line %d: steps must be an array" % n)
            for s in steps:
                if (not isinstance(s, dict) or not isinstance(s.get("key"), str)
                        or not _is_int(s.get("at_ms")) or s["at_ms"] < prev
                        or not isinstance(s.get("down"), bool)):
                    raise PlanError("line %d: malformed or out-of-order step" % n)
                prev = s["at_ms"]
            blocks[-1][1].append(row)
        else:
            raise PlanError("line %d: unknown row kind" % n)
    if header is None:
        raise PlanError("empty plan")
    return sha, header, blocks


def plan_keys(blocks):
    keys = set()
    for block, trials in blocks:
        keys.update(block.get("marker", []))
        for t in trials:
            keys.update(s["key"] for s in t["steps"])
    return keys


# ------------------------------------------------------------------ emitter

def _wait_until(target):
    """Sleep until time.perf_counter() reaches target; the last SPIN_SECONDS are a busy-wait."""
    while True:
        remaining = target - time.perf_counter()
        if remaining <= 0:
            return
        if remaining > SPIN_SECONDS:
            time.sleep(remaining - SPIN_SECONDS)


def _wait_ms(ms):
    _wait_until(time.perf_counter() + ms / 1000.0)


def _stamp():
    return {"t_wall_ms": time.time_ns() // 1000000, "t_mono_ns": time.monotonic_ns()}


class Emitter(object):
    def __init__(self, backend, out, plan_sha256, os_name, backend_name):
        self.backend = backend
        self.out = out
        self._header = {"kind": "header", "format": "oracle/1", "plan_sha256": plan_sha256,
                        "os": os_name, "emitter_version": EMITTER_VERSION, "backend": backend_name}
        self._f = None

    def __enter__(self):
        self._f = open(self.out, "x", encoding="utf-8", newline="\n")
        try:
            self._row(self._header)
            self.backend.open()
        except BaseException:
            self._finish()
            raise
        return self

    def __exit__(self, exc_type, exc, tb):
        self._finish()
        return False

    def _finish(self):
        try:
            self.backend.close()
        finally:
            if self._f is not None:
                self._f.close()
                self._f = None

    def _row(self, obj):
        self._f.write(_dumps(obj) + "\n")
        self._f.flush()

    def _emit(self, kind, **fields):
        row = {"kind": kind}
        row.update(fields)
        row.update(_stamp())
        self._row(row)

    def write_reset(self, block_id, exit_code):
        self._emit("reset", block_id=block_id, exit_code=exit_code)

    def run_block(self, block, trials):
        block_id = block["block_id"]
        self._emit("block_begin", block_id=block_id)
        gap = block.get("marker_gap_ms", 0)
        for seq, key in enumerate(block.get("marker", [])):
            if seq > 0:
                _wait_ms(gap)
            st = _stamp()
            self.backend.send(key, True)
            row = {"kind": "marker", "block_id": block_id, "seq": seq}
            row.update(st)
            self._row(row)
            self.backend.send(key, False)
        for trial in trials:
            self.run_trial(trial)
        self._emit("block_end", block_id=block_id)

    def run_trial(self, trial):
        trial_id = trial["trial_id"]
        _wait_ms(trial.get("gap_before_ms", 0))
        start = time.perf_counter()
        self._emit("trial_begin", trial_id=trial_id)
        for i, step in enumerate(trial["steps"]):
            _wait_until(start + step["at_ms"] / 1000.0)
            st = _stamp()
            self.backend.send(step["key"], step["down"])
            row = {"kind": "sent", "trial_id": trial_id, "step": i, "key": step["key"], "down": step["down"]}
            row.update(st)
            self._row(row)
        self._emit("trial_end", trial_id=trial_id)


# ------------------------------------------------------------------ oracle validation

def validate_oracle(path):
    """Return a list of violation descriptions (never containing a value from the file)."""
    errors = []

    def bad(n, msg):
        errors.append("line %d: %s" % (n, msg))

    try:
        with open(path, "rb") as f:
            text = f.read().decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return ["cannot read the file as UTF-8"]
    if text.startswith("﻿"):
        return ["the file starts with a byte order mark"]
    lines = [(n, l.rstrip("\r")) for n, l in enumerate(text.split("\n"), 1)]
    while lines and not lines[-1][1]:
        lines.pop()
    if not lines:
        return ["empty file"]
    state = "top"            # top -> block -> trial
    block_id, marker_seq, trial_started = None, 0, False
    trial_id, step, down = None, 0, set()
    seen_trials, last_mono = set(), None
    for idx, (n, line) in enumerate(lines):
        if re.search(r"\s", line) or "\\" in line:
            bad(n, "whitespace or a backslash outside the compact form")
            continue
        try:
            row = json.loads(line)
        except ValueError:
            bad(n, "not JSON")
            continue
        if not isinstance(row, dict):
            bad(n, "not an object")
            continue
        kind = row.get("kind")
        if idx == 0:
            want = {"kind", "format", "plan_sha256", "os", "emitter_version", "backend"}
            if (set(row) != want or row.get("kind") != "header" or row.get("format") != "oracle/1"
                    or not isinstance(row.get("plan_sha256"), str) or not HEX64_RE.match(row["plan_sha256"])
                    or row.get("os") not in OS_NAMES or row.get("backend") not in BACKENDS
                    or not isinstance(row.get("emitter_version"), str)
                    or not VERSION_RE.match(row["emitter_version"])):
                bad(n, "malformed header")
            continue
        if kind not in KEYS_OF_KIND:
            bad(n, "unknown or misplaced row kind")
            continue
        if set(row) != set(("kind",) + KEYS_OF_KIND[kind] + TIME_KEYS):
            bad(n, "%s row has the wrong set of keys" % kind)
            continue
        if not all(_is_int(row[k]) and row[k] >= 0 for k in TIME_KEYS):
            bad(n, "timestamps must be non-negative integers")
            continue
        if last_mono is not None and row["t_mono_ns"] < last_mono:
            bad(n, "monotonic time goes backwards")
        last_mono = row["t_mono_ns"]
        if kind in ("block_begin", "block_end", "marker", "reset") and not _is_int(row["block_id"]):
            bad(n, "block_id must be an integer")
            continue
        if kind == "reset":
            if state != "top" or not _is_int(row["exit_code"]):
                bad(n, "reset must sit between blocks and carry an integer exit_code")
        elif kind == "block_begin":
            if state != "top":
                bad(n, "block_begin inside a block")
            state, block_id, marker_seq, trial_started = "block", row["block_id"], 0, False
        elif kind == "marker":
            if state != "block" or trial_started or row["block_id"] != block_id or row["seq"] != marker_seq:
                bad(n, "marker out of place or out of sequence")
            marker_seq += 1
        elif kind == "trial_begin":
            if state != "block" or not isinstance(row["trial_id"], str) or row["trial_id"] in seen_trials:
                bad(n, "trial_begin outside a block, or a repeated trial_id")
            state, trial_id, step, down, trial_started = "trial", row["trial_id"], 0, set(), True
            seen_trials.add(row["trial_id"])
        elif kind == "sent":
            if state != "trial" or row["trial_id"] != trial_id or row["step"] != step:
                bad(n, "sent outside its trial or out of step order")
            elif not isinstance(row["key"], str) or not isinstance(row["down"], bool):
                bad(n, "sent needs a string key and a boolean down")
            elif row["down"]:
                if row["key"] in down:
                    bad(n, "key pressed twice without a release")
                down.add(row["key"])
            elif row["key"] not in down:
                bad(n, "release without a press")
            else:
                down.discard(row["key"])
            step += 1
        elif kind == "trial_end":
            if state != "trial" or row["trial_id"] != trial_id:
                bad(n, "trial_end without its trial_begin")
            elif down:
                bad(n, "trial ends with a key still pressed")
            state = "block"
        elif kind == "block_end":
            if state != "block" or row["block_id"] != block_id:
                bad(n, "block_end without its block_begin")
            state = "top"
    if state != "top":
        errors.append("the file ends inside an open %s" % state)
    return errors


# ------------------------------------------------------------------ command line

def load_backend(name):
    path = os.path.join(HERE, "backend_%s.py" % name)
    if not os.path.isfile(path):
        raise PlanError("backend %s is not implemented" % name)
    spec = importlib.util.spec_from_file_location("backend_%s" % name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "SUPPORTED_KEYS") or not hasattr(module, "Backend"):
        raise PlanError("backend %s does not follow the backend contract" % name)
    return module


def parse_opts(items):
    opts = {}
    for item in items:
        if "=" not in item:
            raise PlanError("--backend-opt expects k=v")
        k, v = item.split("=", 1)
        if not k or k in opts:
            raise PlanError("--backend-opt: empty or repeated key")
        opts[k] = v
    return opts


def run(args):
    try:
        opts = parse_opts(args.backend_opt)
        sha, header, blocks = read_plan(args.plan)
    except (PlanError, OSError, UnicodeDecodeError) as e:
        print("emit: %s" % e, file=sys.stderr)
        return 2
    if args.backend != "dryrun" and not args.send_flag:
        print("emit: backend %s sends real key events; it is not started without %s" % (args.backend, SEND_FLAG),
              file=sys.stderr)
        return 2
    try:
        module = load_backend(args.backend)
    except PlanError as e:
        print("emit: %s" % e, file=sys.stderr)
        return 2
    if args.backend != "dryrun" and header["os"] != args.backend:
        print("emit: the plan is for %s but the backend is %s" % (header["os"], args.backend), file=sys.stderr)
        return 2
    unsupported = sorted(plan_keys(blocks) - set(module.SUPPORTED_KEYS))
    if unsupported:
        print("emit: keys not supported by backend %s: %s" % (args.backend, ", ".join(unsupported)),
              file=sys.stderr)
        return 2
    if os.path.exists(args.out):
        print("emit: refusing to overwrite an existing output file", file=sys.stderr)
        return 2
    try:
        backend = module.Backend(opts)
    except (ValueError, TypeError) as e:
        print("emit: %s" % e, file=sys.stderr)
        return 2
    try:
        with Emitter(backend, args.out, sha, header["os"], args.backend) as em:
            for block, trials in blocks:
                em.run_block(block, trials)
    except (RuntimeError, OSError) as e:
        print("emit: run failed: %s" % e, file=sys.stderr)
        return 1
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Play a plan/1 file through a key-sending backend and write an oracle/1 log.")
    ap.add_argument("--plan")
    ap.add_argument("--out")
    ap.add_argument("--backend", choices=BACKENDS)
    ap.add_argument("--backend-opt", action="append", default=[], metavar="K=V")
    ap.add_argument(SEND_FLAG, dest="send_flag", action="store_true",
                    help="required for any backend that sends real key events")
    ap.add_argument("--validate", metavar="ORACLE")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.validate:
        errors = validate_oracle(args.validate)
        for e in errors[:20]:
            print("oracle: %s" % e)
        print("oracle: %s" % ("valid" if not errors else "%d violation(s)" % len(errors)))
        return 1 if errors else 0
    if not (args.plan and args.out and args.backend):
        ap.print_usage(sys.stderr)
        return 2
    return run(args)


# ------------------------------------------------------------------ self-test (dryrun only)

def _make_plan(path, with_unsupported=False):
    sha = "0" * 64
    rows = [{"kind": "header", "format": "plan/1", "os": "macos", "seed": 1, "generator_version": "0",
             "config_sha256": sha}]
    n = 0
    for b in range(2):
        rows.append({"kind": "block", "block_id": b, "speed": "mid", "reset_ime": b == 1,
                     "marker": ["f13", "f14"], "marker_gap_ms": 5})
        for _ in range(3):
            n += 1
            steps = []
            for i in range(20):
                steps.append({"key": "a", "at_ms": i * 8, "down": True})
                steps.append({"key": "a", "at_ms": i * 8 + 4, "down": False})
            if with_unsupported:
                steps.append({"key": "mouse_click", "at_ms": 200, "down": True})
            rows.append({"kind": "trial", "trial_id": "t%05d" % n, "block_id": b, "scenario": "S3",
                         "speed": "mid", "gap_before_ms": 50, "think_ms": 0, "phrase_id": "w1-1-1",
                         "reading_len": 1, "steps": steps, "intent": {}})
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(_dumps(r) + "\n")


def _load_rows(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def _quiet_main(argv):
    """Run main() with its messages captured; the self-test reports results itself."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return main(argv)


def selftest():
    failures = []

    def check(name, cond):
        print("%s %s" % ("ok  " if cond else "FAIL", name))
        if not cond:
            failures.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        plan = os.path.join(tmp, "plan.jsonl")
        out = os.path.join(tmp, "oracle.jsonl")
        _make_plan(plan)
        rc = _quiet_main(["--plan", plan, "--out", out, "--backend", "dryrun"])
        check("a dryrun of a two-block plan exits 0", rc == 0)
        check("the produced oracle passes validation", _quiet_main(["--validate", out]) == 0)
        rows = _load_rows(out)
        kinds = [r["kind"] for r in rows]
        check("row order is header, block_begin, markers, trials, block_end",
              kinds[:4] == ["header", "block_begin", "marker", "marker"] and kinds[-1] == "block_end"
              and kinds.count("trial_begin") == 6 and kinds.count("trial_end") == 6)
        check("one sent row per planned step", kinds.count("sent") == 6 * 40)
        check("marker rows carry a 0-based seq", [r["seq"] for r in rows if r["kind"] == "marker"][:2] == [0, 1])

        # timing: actual send time against the planned time, and the plan's own waits
        prev_end, gaps = None, []
        for r in rows:
            if r["kind"] == "trial_begin" and prev_end is not None:
                gaps.append((r["t_mono_ns"] - prev_end) / 1e6)
            elif r["kind"] == "trial_end":
                prev_end = r["t_mono_ns"]
        _, _, blocks = read_plan(plan)
        planned = {}
        for _b, trials in blocks:
            for t in trials:
                planned[t["trial_id"]] = t["steps"]
        starts, late = {}, []
        for r in rows:
            if r["kind"] == "trial_begin":
                starts[r["trial_id"]] = r["t_mono_ns"]
            elif r["kind"] == "sent":
                due = starts[r["trial_id"]] + planned[r["trial_id"]][r["step"]]["at_ms"] * 1000000
                late.append((r["t_mono_ns"] - due) / 1e6)
        late.sort()
        p95 = late[int(0.95 * (len(late) - 1))]
        check("95th percentile of send lateness is under 20 ms (%.2f ms)" % p95, p95 < 20.0 and late[0] >= -1.0)
        check("the inter-trial wait of the plan is honoured", all(g >= 49.0 for g in gaps) and len(gaps) >= 4)

        # negative controls for the validator
        text = open(out, encoding="utf-8").read()
        bad_cases = {
            "a missing trial_end": "".join(l + "\n" for l in text.splitlines() if '"kind":"trial_end"' not in l),
            "a missing header": "".join(l + "\n" for l in text.splitlines()[1:]),
            "a release without a press": text.replace('"down":true', '"down":false', 1),
            "a missing block_end": "".join(l + "\n" for l in text.splitlines() if '"kind":"block_end"' not in l),
            "whitespace in a row": text.replace('"kind":"sent",', '"kind": "sent",', 1),
            "a non-integer timestamp": text.replace('"t_wall_ms":', '"t_wall_ms":1.5,"x":', 1),
        }
        for name, body in bad_cases.items():
            p = os.path.join(tmp, "bad.jsonl")
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(body)
            check("validation rejects %s" % name, _quiet_main(["--validate", p]) == 1)

        # sending is opt-in
        for real in ("macos", "windows"):
            o = os.path.join(tmp, "real_%s.jsonl" % real)
            check("backend %s without the send flag exits 2 and writes nothing" % real,
                  _quiet_main(["--plan", plan, "--out", o, "--backend", real]) == 2 and not os.path.exists(o))

        # a key outside SUPPORTED_KEYS stops the run before anything is sent
        plan_bad = os.path.join(tmp, "plan_bad.jsonl")
        _make_plan(plan_bad, with_unsupported=True)
        o = os.path.join(tmp, "unsupported.jsonl")
        check("an unsupported key stops the run before any send",
              _quiet_main(["--plan", plan_bad, "--out", o, "--backend", "dryrun"]) == 2 and not os.path.exists(o))

        # the backend is always closed, including after a failure mid-run
        module = load_backend("dryrun")
        _, _, blocks = read_plan(plan)
        backend = module.Backend({"fail_after": "10"})
        try:
            with Emitter(backend, os.path.join(tmp, "failed.jsonl"), "0" * 64, "macos", "dryrun") as em:
                for block, trials in blocks:
                    em.run_block(block, trials)
            raised = False
        except RuntimeError:
            raised = True
        check("an injected failure propagates", raised)
        check("close ran exactly once after the failure", backend.closed == 1 and backend.opened == 1)
        check("an unknown backend option is refused",
              _quiet_main(["--plan", plan, "--out", os.path.join(tmp, "x.jsonl"), "--backend", "dryrun",
                    "--backend-opt", "bogus=1"]) == 2)
        check("an existing output file is not overwritten",
              _quiet_main(["--plan", plan, "--out", out, "--backend", "dryrun"]) == 2)

        # reset rows come before block_begin when the orchestrator writes them
        o2 = os.path.join(tmp, "reset.jsonl")
        with Emitter(module.Backend({}), o2, "0" * 64, "macos", "dryrun") as em:
            em.write_reset(0, 0)
            em.run_block(blocks[0][0], blocks[0][1][:1])
        check("a reset row before block_begin validates", _quiet_main(["--validate", o2]) == 0
              and [r["kind"] for r in _load_rows(o2)][1:3] == ["reset", "block_begin"])
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
