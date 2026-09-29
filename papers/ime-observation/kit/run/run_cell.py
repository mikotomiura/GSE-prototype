#!/usr/bin/env python3
# kit: selftest
"""Cell runner: measures one cell (operating system x input method x settings) with one command.

  run_cell.py --cell CELL.json --plan PLAN --run-dir DIR [--i-understand-this-sends-keys]
  run_cell.py --selftest

The runner starts the standalone observer (``logger_cmd``) and the reference input field (``refinput_cmd``) as
child processes, waits ``ready_wait_ms``, and then plays the plan block by block through the scenario emitter
(``kit/emit/emit.py``, used as a library). Before each block whose plan row asks for it (``reset_ime``), it runs
``reset_cmd`` and records the exit status in the oracle; before every block it runs ``focus_cmd``. After the last
block both children are asked to stop (SIGTERM; on Windows ``terminate``), and one that does not exit within
``stop_wait_ms`` is killed; the manifest says which happened. Everything is written to the run directory:

  plan.jsonl     a byte-for-byte copy of the plan that was played
  oracle.jsonl   what the emitter sent and when (``oracle/1``)
  gt.jsonl       the reference input field's log (``gt/1``)
  obs.jsonl      the observer's log (``obs/1``)
  run.json       the manifest (``run/1``): the cell, the commit, both clocks at start and end, the SHA-256 and
                 line count of each log, the children's exit statuses and how each was stopped, the reset
                 statuses, and ``aborted`` with its reason
  <child>.stderr.txt  what each child wrote to standard error

The commands are not chosen here. How an input method is reset and how the reference input field is brought to
the front differ by system and input method; the cell file gives them and this runner executes them and
records the exit status. A cell file has these keys (all required except the last four):

  os, ime, ime_settings, refinput_cmd, logger_cmd, reset_cmd, focus_cmd, ready_wait_ms, backend,
  clock_sync_disabled, auto_update_disabled, backend_opts, stop_wait_ms, settle_ms, command_timeout_ms

``refinput_cmd`` and ``logger_cmd`` are argument arrays in which the text ``{out}`` is replaced by the path of
the log that child writes; ``reset_cmd`` and ``focus_cmd`` are argument arrays (an empty array does nothing).
``clock_sync_disabled`` and ``auto_update_disabled`` are statements by the person who prepared the machine; the
runner records them and cannot check them.

Sending is opt-in, as in the emitter: a backend other than ``dryrun`` needs the flag named by ``SEND_FLAG``
(exit status 2 without it). The flag check, the plan check, and the check that the run directory does not exist
all happen before any child process is started, and an existing run directory is never touched.

A child that exits while the run is in progress stops the run at the next key: the run is marked ``aborted``
with the reason (a material for the exclusion rule "the host crashed"). A reset or focus command that cannot be
run or times out is recorded with exit status -1 (a reset) or aborts the run (a focus command, since the keys
would go to the wrong window).

Exit status: 0 the run completed / 1 the run was aborted or its manifest could not be written / 2 refused or
could not start.
"""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time

RUN_FORMAT = "run/1"
RUNNER_VERSION = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
LOG_NAMES = ("plan", "oracle", "gt", "obs")
LOG_FILES = {"plan": "plan.jsonl", "oracle": "oracle.jsonl", "gt": "gt.jsonl", "obs": "obs.jsonl"}
MANIFEST_FILE = "run.json"
OUT_MARK = "{out}"
POLL_SECONDS = 0.05
MAX_WAIT_MS = 3600000
DEFAULT_STOP_WAIT_MS = 5000
DEFAULT_SETTLE_MS = 0
DEFAULT_COMMAND_TIMEOUT_MS = 60000
FAILED_TO_RUN = -1     # exit status recorded for a reset command that could not start or timed out
SIGTERM_STATUS = 143


def _load_module(name, *parts):
    path = os.path.join(KIT, *parts)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EM = _load_module("kit_emit", "emit", "emit.py")
SEND_FLAG = EM.SEND_FLAG
BACKENDS = EM.BACKENDS
OS_NAMES = EM.OS_NAMES


class CellError(Exception):
    pass


class Aborted(Exception):
    """Raised inside a run when it has to stop and be marked aborted."""


class ChildDied(RuntimeError):
    pass


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


# ------------------------------------------------------------------ cell file

REQUIRED_KEYS = ("os", "ime", "ime_settings", "refinput_cmd", "logger_cmd", "reset_cmd", "focus_cmd",
                 "ready_wait_ms", "backend", "clock_sync_disabled", "auto_update_disabled")
OPTIONAL_KEYS = ("backend_opts", "stop_wait_ms", "settle_ms", "command_timeout_ms")


def _cmd(cell, key, allow_empty, needs_out):
    v = cell[key]
    if (not isinstance(v, list) or not all(isinstance(a, str) and a for a in v)
            or (not allow_empty and not v)):
        raise CellError("%s must be an array of non-empty strings%s" % (key, "" if allow_empty else " (not empty)"))
    if needs_out and not any(OUT_MARK in a for a in v):
        raise CellError("%s must contain %s in an argument, where the path of its log goes" % (key, OUT_MARK))
    return v


def check_cell(cell):
    """Return the cell with its optional keys filled in; raise CellError."""
    if not isinstance(cell, dict):
        raise CellError("the cell file must hold one JSON object")
    missing = [k for k in REQUIRED_KEYS if k not in cell]
    if missing:
        raise CellError("missing key(s): %s" % ", ".join(missing))
    unknown = sorted(set(cell) - set(REQUIRED_KEYS) - set(OPTIONAL_KEYS))
    if unknown:
        raise CellError("unknown key(s): %s" % ", ".join(unknown))
    if cell["os"] not in OS_NAMES:
        raise CellError("os must be one of %s" % ", ".join(OS_NAMES))
    if not isinstance(cell["ime"], str) or not cell["ime"]:
        raise CellError("ime must be a non-empty string (name and version)")
    if not isinstance(cell["ime_settings"], dict):
        raise CellError("ime_settings must be an object")
    _cmd(cell, "refinput_cmd", False, True)
    _cmd(cell, "logger_cmd", False, True)
    _cmd(cell, "reset_cmd", True, False)
    _cmd(cell, "focus_cmd", True, False)
    if cell["backend"] not in BACKENDS:
        raise CellError("backend must be one of %s" % ", ".join(BACKENDS))
    for key in ("clock_sync_disabled", "auto_update_disabled"):
        if not isinstance(cell[key], bool):
            raise CellError("%s must be true or false" % key)
    full = dict(cell)
    full.setdefault("backend_opts", {})
    full.setdefault("stop_wait_ms", DEFAULT_STOP_WAIT_MS)
    full.setdefault("settle_ms", DEFAULT_SETTLE_MS)
    full.setdefault("command_timeout_ms", DEFAULT_COMMAND_TIMEOUT_MS)
    opts = full["backend_opts"]
    if not isinstance(opts, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in opts.items()):
        raise CellError("backend_opts must be an object of strings")
    for key, low in (("ready_wait_ms", 0), ("stop_wait_ms", 0), ("settle_ms", 0), ("command_timeout_ms", 1)):
        if not _is_int(full[key]) or not low <= full[key] <= MAX_WAIT_MS:
            raise CellError("%s must be an integer from %d to %d" % (key, low, MAX_WAIT_MS))
    return full


def load_cell(path):
    with open(path, "rb") as f:
        raw = f.read()
    try:
        cell = json.loads(raw.decode("utf-8"), object_pairs_hook=EM._no_duplicate_keys)
    except (ValueError, UnicodeDecodeError, RecursionError):
        raise CellError("the cell file is not JSON (or a key is repeated)")
    return check_cell(cell)


# ------------------------------------------------------------------ children

def _substitute(cmd, out):
    return [a.replace(OUT_MARK, out) for a in cmd]


class Child(object):
    """One child process whose standard error goes to ``<name>.stderr.txt`` in the run directory."""

    def __init__(self, name, cmd, run_dir):
        self.name = name
        self.stderr_file = name + ".stderr.txt"
        self.how_stopped = None
        self.exit_code = None
        self._err = open(os.path.join(run_dir, self.stderr_file), "wb")
        try:
            self.proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                         stderr=self._err)
        except BaseException:
            self._err.close()
            raise

    def stop(self, wait_s):
        """Ask the child to end, wait, and kill it if it does not; remember which of the three happened."""
        try:
            if self.proc.poll() is not None:
                self.how_stopped = "exited_before_stop"
            else:
                self.proc.terminate()
                try:
                    self.proc.wait(timeout=wait_s)
                    self.how_stopped = "terminated"
                except subprocess.TimeoutExpired:
                    self.proc.kill()
                    self.proc.wait()
                    self.how_stopped = "killed"
            self.exit_code = self.proc.returncode
        finally:
            self._err.close()


def check_children(children):
    for c in children:
        code = c.proc.poll()
        if code is not None:
            raise ChildDied("%s exited with status %s before the run was over" % (c.name, code))


class Watcher(threading.Thread):
    """Notices a child that exits, so that the next key press is refused."""

    def __init__(self, children):
        threading.Thread.__init__(self)
        self.daemon = True
        self.children = children
        self.dead = None
        self._done = threading.Event()

    def run(self):
        while not self._done.wait(POLL_SECONDS):
            try:
                check_children(self.children)
            except ChildDied as e:
                self.dead = str(e)
                return

    def finish(self):
        self._done.set()
        self.join()


class GuardedBackend(object):
    """Wraps a backend: once a child has died no key is pressed (releases still go through, so no key is left
    held)."""

    def __init__(self, inner, watcher):
        self._inner = inner
        self._watcher = watcher

    def open(self):
        self._inner.open()

    def send(self, key, down):
        if down and self._watcher.dead is not None:
            raise ChildDied(self._watcher.dead)
        self._inner.send(key, down)

    def close(self):
        self._inner.close()


def run_command(cmd, timeout_ms):
    """Run a command to completion and return its exit status (FAILED_TO_RUN if it could not start or timed out)."""
    try:
        return subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              timeout=timeout_ms / 1000.0).returncode
    except (OSError, subprocess.SubprocessError):
        return FAILED_TO_RUN


def wait_ready(children, ms):
    deadline = time.perf_counter() + ms / 1000.0
    while True:
        check_children(children)
        remaining = deadline - time.perf_counter()
        if remaining <= 0:
            return
        time.sleep(min(remaining, POLL_SECONDS))


# ------------------------------------------------------------------ manifest

def sha256_and_lines(path):
    """(sha256, number of lines) of a file, or (None, None) if it is absent or empty."""
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None, None
    if not data:
        return None, None
    lines = data.count(b"\n") + (0 if data.endswith(b"\n") else 1)
    return hashlib.sha256(data).hexdigest(), lines


def git_commit():
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE, stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    text = r.stdout.decode("ascii", "replace").strip()
    return text if r.returncode == 0 and len(text) == 40 and all(c in "0123456789abcdef" for c in text) else None


def _clocks():
    return {"wall_ms": EM._wall_ns() // 1000000, "mono_ns": EM._mono_ns()}


def build_manifest(cell, plan_sha, run_dir, started, ended, children, resets, focus, aborted, reason):
    outputs = {}
    for name in LOG_NAMES:
        sha, lines = sha256_and_lines(os.path.join(run_dir, LOG_FILES[name]))
        outputs[name] = {"file": LOG_FILES[name], "sha256": sha, "lines": lines}
    return {
        "format": RUN_FORMAT,
        "runner_version": RUNNER_VERSION,
        "emitter_version": EM.EMITTER_VERSION,
        "cell": cell,
        "plan_sha256": plan_sha,
        "git_commit": git_commit(),
        "started": started,
        "ended": ended,
        "outputs": outputs,
        "children": dict((c.name, {"exit_code": c.exit_code, "stopped": c.how_stopped,
                                   "stderr_file": c.stderr_file}) for c in children),
        "resets": resets,
        "focus_exit_codes": focus,
        "aborted": aborted,
        "abort_reason": reason,
    }


def write_manifest(run_dir, manifest):
    text = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with open(os.path.join(run_dir, MANIFEST_FILE), "x", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ------------------------------------------------------------------ the run

def _sigterm(signum, frame):
    sys.exit(SIGTERM_STATUS)


def play(cell, header, blocks, plan_sha, backend, module, allow_send, run_dir, children, resets, focus):
    """Start the children, play every block, and return; raise Aborted / ChildDied / emitter errors."""
    logger_out = os.path.join(run_dir, LOG_FILES["obs"])
    refinput_out = os.path.join(run_dir, LOG_FILES["gt"])
    children.append(Child("logger", _substitute(cell["logger_cmd"], logger_out), run_dir))
    children.append(Child("refinput", _substitute(cell["refinput_cmd"], refinput_out), run_dir))
    watcher = Watcher(children)
    watcher.start()
    try:
        wait_ready(children, cell["ready_wait_ms"])
        guarded = GuardedBackend(backend, watcher)
        with EM.Emitter(guarded, os.path.join(run_dir, LOG_FILES["oracle"]), plan_sha, header["os"],
                        cell["backend"], allow_send=allow_send, supported_keys=module.SUPPORTED_KEYS) as em:
            for block, trials in blocks:
                block_id = block["block_id"]
                check_children(children)
                if block.get("reset_ime") is True and cell["reset_cmd"]:
                    code = run_command(cell["reset_cmd"], cell["command_timeout_ms"])
                    em.write_reset(block_id, code)
                    resets.append({"block_id": block_id, "exit_code": code})
                if cell["focus_cmd"]:
                    code = run_command(cell["focus_cmd"], cell["command_timeout_ms"])
                    focus.append({"block_id": block_id, "exit_code": code})
                    if code != 0:
                        raise Aborted("the focus command exited with status %d before block %d; "
                                      "nothing was sent to that block" % (code, block_id))
                check_children(children)
                em.run_block(block, trials)
        time.sleep(cell["settle_ms"] / 1000.0)
        check_children(children)
    finally:
        watcher.finish()


def execute(cell, header, blocks, plan_sha, plan_bytes, backend, module, allow_send, run_dir):
    """Create the run directory and run the cell in it. Return the exit status."""
    parent = os.path.dirname(os.path.abspath(run_dir))
    os.makedirs(parent, exist_ok=True)
    try:
        os.mkdir(run_dir)
    except FileExistsError:
        print("run_cell: the run directory already exists; it is never reused", file=sys.stderr)
        return 2
    with open(os.path.join(run_dir, LOG_FILES["plan"]), "xb") as f:
        f.write(plan_bytes)
    children, resets, focus = [], [], []
    aborted, reason, pending = False, None, None
    started = _clocks()
    previous = signal.signal(signal.SIGTERM, _sigterm)
    try:
        play(cell, header, blocks, plan_sha, backend, module, allow_send, run_dir, children, resets, focus)
    except (Aborted, ChildDied) as e:
        aborted, reason = True, str(e)
    except (EM.SendRefused, EM.ClockTooCoarse, EM.PlanError) as e:
        aborted, reason = True, "the emitter refused to run: %s" % e
    except (RuntimeError, OSError, subprocess.SubprocessError) as e:
        aborted, reason = True, "%s: %s" % (type(e).__name__, e)
    except BaseException as e:
        aborted, reason = True, "interrupted (%s)" % type(e).__name__
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            pending = e
    finally:
        signal.signal(signal.SIGTERM, previous)
        for c in children:
            try:
                c.stop(cell["stop_wait_ms"] / 1000.0)
            except OSError as e:
                c.how_stopped = "stop failed: %s" % type(e).__name__
    ended = _clocks()
    if not aborted:
        for c, name in (("logger", "obs"), ("refinput", "gt")):
            if sha256_and_lines(os.path.join(run_dir, LOG_FILES[name]))[0] is None:
                aborted, reason = True, "%s wrote no output" % c
                break
    manifest = build_manifest(cell, plan_sha, run_dir, started, ended, children, resets, focus, aborted, reason)
    try:
        write_manifest(run_dir, manifest)
    except OSError as e:
        print("run_cell: could not write the manifest: %s" % type(e).__name__, file=sys.stderr)
        if pending is not None:
            raise pending
        return 1
    if pending is not None:
        raise pending
    if aborted:
        print("run_cell: the run was aborted: %s" % reason, file=sys.stderr)
        return 1
    print("run_cell: wrote %s" % os.path.join(run_dir, MANIFEST_FILE))
    return 0


def run(args):
    try:
        cell = load_cell(args.cell)
        plan_sha, header, blocks = EM.read_plan(args.plan)
        with open(args.plan, "rb") as f:
            plan_bytes = f.read()
    except (CellError, EM.PlanError, OSError, UnicodeDecodeError) as e:
        print("run_cell: %s" % e, file=sys.stderr)
        return 2
    if cell["backend"] != "dryrun" and not args.send_flag:
        print("run_cell: backend %s sends real key events; it is not started without %s"
              % (cell["backend"], SEND_FLAG), file=sys.stderr)
        return 2
    if cell["os"] != header["os"]:
        print("run_cell: the cell is for %s but the plan is for %s" % (cell["os"], header["os"]), file=sys.stderr)
        return 2
    try:
        module = EM.load_backend(cell["backend"])
    except (EM.PlanError, ValueError, OSError, SyntaxError, ImportError) as e:
        print("run_cell: backend %s could not be loaded: %s" % (cell["backend"], e), file=sys.stderr)
        return 2
    if cell["backend"] != "dryrun" and header["os"] != cell["backend"]:
        print("run_cell: the plan is for %s but the backend is %s" % (header["os"], cell["backend"]),
              file=sys.stderr)
        return 2
    keys = EM.plan_keys(blocks)
    unsupported = sorted(keys - set(module.SUPPORTED_KEYS))
    if unsupported:
        print("run_cell: keys not supported by backend %s: %s" % (cell["backend"], ", ".join(unsupported)),
              file=sys.stderr)
        return 2
    missing = EM.check_key_options(module, keys, cell["backend_opts"])
    if missing:
        print("run_cell: keys that need a backend option the cell does not give: %s" % ", ".join(missing),
              file=sys.stderr)
        return 2
    if os.path.exists(args.run_dir):
        print("run_cell: the run directory already exists; it is never reused", file=sys.stderr)
        return 2
    try:
        backend = module.Backend(cell["backend_opts"])
    except (ValueError, TypeError) as e:
        print("run_cell: %s" % e, file=sys.stderr)
        return 2
    if cell["backend"] != "dryrun" and not (cell["clock_sync_disabled"] and cell["auto_update_disabled"]):
        print("run_cell: note: the cell does not state that time synchronisation and automatic updates are off",
              file=sys.stderr)
    return execute(cell, header, blocks, plan_sha, plan_bytes, backend, module, args.send_flag, args.run_dir)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Measure one cell: start the observers, play a plan, stop, and "
                                             "write the run directory.")
    ap.add_argument("--cell", help="cell file (JSON)")
    ap.add_argument("--plan", help="plan/1 file to play")
    ap.add_argument("--run-dir", help="run directory to create (must not exist)")
    ap.add_argument(SEND_FLAG, dest="send_flag", action="store_true",
                    help="required for any backend that sends real key events")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not (args.cell and args.plan and args.run_dir):
        ap.print_usage(sys.stderr)
        return 2
    return run(args)


# ------------------------------------------------------------------ self-test (dryrun and stub children only)

ZERO = "0" * 64
GT_HEADER = '{"kind":"header","format":"gt/1","src":"mac_nstic","app_version":"0.1.0","os":"macos"}'
OBS_HEADER = ('{"type":"meta","format":"obs/1","os":"macos","logger_version":"0.1.0","manifest_sha256":"%s",'
              '"capabilities":{"unconditional":["key"],"threshold_gated":[],"config_gated":["ime_shadow"]}}' % ZERO)
STUB_SOURCE = '''import signal, sys, time
out, header, mode, seconds = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
if mode == "ignore-term":
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
if mode != "silent":
    with open(out, "w", encoding="utf-8", newline="\\n") as f:
        f.write(header + "\\n")
time.sleep(seconds)
'''


def _write_plan(path, first_gap_ms=0):
    rows = [{"kind": "header", "format": "plan/1", "os": "macos", "seed": 1, "generator_version": "0",
             "config_sha256": ZERO, "recipes_sha256": ZERO, "corpus_sha256": ZERO}]
    n = 0
    for b in range(2):
        rows.append({"kind": "block", "block_id": b, "speed": "mid", "reset_ime": b == 1,
                     "marker": ["f13", "f14"], "marker_gap_ms": 5})
        for _ in range(2):
            n += 1
            rows.append({"kind": "trial", "trial_id": "t%05d" % n, "block_id": b, "scenario": "S3", "speed": "mid",
                         "gap_before_ms": first_gap_ms if n == 1 else 20, "think_ms": 0, "phrase_id": "w1-1-1",
                         "reading_len": 1,
                         "steps": [{"key": "a", "at_ms": 0, "down": True}, {"key": "a", "at_ms": 30, "down": False}],
                         "intent": {"commit": "enter", "cand_index": 0, "nav_count": 0, "abandon": False,
                                    "predictive": False, "ime_toggle_mid": False, "focus_switch_mid": False,
                                    "expect_session": True}})
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(EM._dumps(r) + "\n")


def _cell(stub, over=None, logger_mode="normal", logger_seconds="60", refinput_mode="normal"):
    cell = {"os": "macos", "ime": "stub-ime 1.0", "ime_settings": {"layout": "stub"},
            "refinput_cmd": [sys.executable, stub, OUT_MARK, GT_HEADER, refinput_mode, "60"],
            "logger_cmd": [sys.executable, stub, OUT_MARK, OBS_HEADER, logger_mode, logger_seconds],
            "reset_cmd": [], "focus_cmd": [], "ready_wait_ms": 200, "backend": "dryrun",
            "clock_sync_disabled": True, "auto_update_disabled": True, "stop_wait_ms": 3000}
    cell.update(over or {})
    return cell


def _write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f)


def _quiet_main(argv):
    """Run main() with its messages captured; the self-test reports results itself."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return main(argv)


def _tool(*parts):
    return os.path.join(KIT, *parts)


def _tool_ok(args):
    return subprocess.run([sys.executable] + args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode == 0


def selftest():
    failures = []

    def check(name, cond):
        print("%s %s" % ("ok  " if cond else "FAIL", name))
        if not cond:
            failures.append(name)

    def exit_with(n):
        return [sys.executable, "-c", "import sys; sys.exit(%d)" % n]

    with tempfile.TemporaryDirectory() as tmp:
        stub = os.path.join(tmp, "stub.py")
        with open(stub, "w", encoding="utf-8", newline="\n") as f:
            f.write(STUB_SOURCE)
        plan = os.path.join(tmp, "plan.jsonl")
        _write_plan(plan)
        cell_path = os.path.join(tmp, "cell.json")

        def go(name, cell, plan_path=None, flag=False, expect=None):
            """Run one cell in the directory tmp/<name>; return (exit status, run directory)."""
            _write_json(cell_path, cell)
            run_dir = os.path.join(tmp, name)
            argv = ["--cell", cell_path, "--plan", plan_path or plan, "--run-dir", run_dir]
            if flag:
                argv.append(SEND_FLAG)
            return _quiet_main(argv), run_dir

        def manifest_of(run_dir):
            with open(os.path.join(run_dir, MANIFEST_FILE), encoding="utf-8") as f:
                return json.load(f)

        def oracle_rows(run_dir):
            with open(os.path.join(run_dir, LOG_FILES["oracle"]), encoding="utf-8") as f:
                return [json.loads(line) for line in f if line.strip()]

        # a complete run of one cell
        rc, d = go("ok", _cell(stub))
        check("a dryrun cell with stub children exits 0", rc == 0)
        files = sorted(os.listdir(d)) if os.path.isdir(d) else []
        check("the run directory holds the four logs and the manifest",
              all(name in files for name in list(LOG_FILES.values()) + [MANIFEST_FILE]))
        m = manifest_of(d)
        check("the manifest is complete and not aborted",
              m["format"] == RUN_FORMAT and m["aborted"] is False and m["abort_reason"] is None
              and m["cell"]["ime"] == "stub-ime 1.0" and m["plan_sha256"] == EM.read_plan(plan)[0])
        sums_ok = True
        for name in LOG_NAMES:
            with open(os.path.join(d, LOG_FILES[name]), "rb") as f:
                data = f.read()
            entry = m["outputs"][name]
            sums_ok = sums_ok and entry["sha256"] == hashlib.sha256(data).hexdigest() \
                and entry["lines"] == data.count(b"\n") and entry["file"] == LOG_FILES[name]
        check("the SHA-256 and the line count of every log match the files", sums_ok)
        with open(os.path.join(d, "plan.jsonl"), "rb") as f1, open(plan, "rb") as f2:
            check("plan.jsonl is a byte-for-byte copy of the plan", f1.read() == f2.read())
        check("the manifest holds both clocks at the start and at the end",
              all(isinstance(m[k][c], int) for k in ("started", "ended") for c in ("wall_ms", "mono_ns"))
              and m["ended"]["mono_ns"] >= m["started"]["mono_ns"])
        check("the manifest records the commit or null",
              m["git_commit"] is None or (isinstance(m["git_commit"], str) and len(m["git_commit"]) == 40))
        check("both children were stopped by a termination request",
              all(m["children"][n]["stopped"] == "terminated" for n in ("logger", "refinput")))
        check("the gt log passes its validator", _tool_ok([_tool("formats", "validate_logs.py"), "--kind", "gt",
                                                          os.path.join(d, "gt.jsonl")]))
        check("the obs log passes its validator", _tool_ok([_tool("formats", "validate_logs.py"), "--kind", "obs",
                                                           os.path.join(d, "obs.jsonl")]))
        check("the oracle passes the emitter's validation",
              _tool_ok([_tool("emit", "emit.py"), "--validate", os.path.join(d, "oracle.jsonl")]))
        check("the plan passes the generator's validation",
              _tool_ok([_tool("gen", "generate_plan.py"), "--validate", os.path.join(d, "plan.jsonl")]))
        check("without a reset command no reset row is written",
              [r for r in oracle_rows(d) if r["kind"] == "reset"] == [] and m["resets"] == [])

        # the reset command's exit status goes into the oracle
        rc, d = go("reset", _cell(stub, {"reset_cmd": exit_with(3)}))
        rows = [r for r in oracle_rows(d) if r["kind"] == "reset"] if rc == 0 else []
        check("the exit status of the reset command is written to the oracle",
              len(rows) == 1 and rows[0]["exit_code"] == 3 and rows[0]["block_id"] == 1
              and manifest_of(d)["resets"] == [{"block_id": 1, "exit_code": 3}])
        check("an oracle with a reset row passes the emitter's validation",
              _tool_ok([_tool("emit", "emit.py"), "--validate", os.path.join(d, "oracle.jsonl")]))
        rc, d = go("reset_ok", _cell(stub, {"reset_cmd": exit_with(0)}))
        check("a reset that succeeds is recorded with status 0",
              rc == 0 and [r["exit_code"] for r in oracle_rows(d) if r["kind"] == "reset"] == [0])
        rc, d = go("reset_missing", _cell(stub, {"reset_cmd": [os.path.join(tmp, "no-such-command")]}))
        check("a reset command that cannot start is recorded as failed, not fatal",
              rc == 0 and [r["exit_code"] for r in oracle_rows(d) if r["kind"] == "reset"] == [FAILED_TO_RUN])

        # a failing focus command stops the run before anything is sent
        rc, d = go("focus", _cell(stub, {"focus_cmd": exit_with(4)}))
        m = manifest_of(d) if os.path.isfile(os.path.join(d, MANIFEST_FILE)) else {}
        check("a focus command that fails aborts the run before any key",
              rc == 1 and m.get("aborted") is True and "focus" in (m.get("abort_reason") or "")
              and not [r for r in oracle_rows(d) if r["kind"] in ("sent", "marker")])

        # a child that dies is an aborted run
        slow = os.path.join(tmp, "slow.jsonl")
        _write_plan(slow, first_gap_ms=1500)
        rc, d = go("dead", _cell(stub, logger_seconds="0.3", over={"ready_wait_ms": 100}), plan_path=slow)
        m = manifest_of(d) if os.path.isfile(os.path.join(d, MANIFEST_FILE)) else {}
        check("a dead child process marks the run aborted",
              rc == 1 and m.get("aborted") is True and "logger" in (m.get("abort_reason") or ""))
        check("the other child is still stopped after an abort",
              m.get("children", {}).get("refinput", {}).get("stopped") == "terminated")
        check("no key is pressed after the child died",
              not [r for r in oracle_rows(d) if r["kind"] == "sent" and r["down"]])
        rc, d = go("silent", _cell(stub, logger_mode="silent"))
        m = manifest_of(d) if os.path.isfile(os.path.join(d, MANIFEST_FILE)) else {}
        check("a child that never writes its log marks the run aborted",
              rc == 1 and m.get("aborted") is True and "no output" in (m.get("abort_reason") or ""))
        if os.name == "posix":
            rc, d = go("stubborn", _cell(stub, logger_mode="ignore-term", over={"ready_wait_ms": 500,
                                                                               "stop_wait_ms": 300}))
            check("a child that ignores the termination request is killed and the manifest says so",
                  rc == 0 and manifest_of(d)["children"]["logger"]["stopped"] == "killed"
                  and manifest_of(d)["children"]["refinput"]["stopped"] == "terminated")
        else:
            print("info the kill path is checked on POSIX only (terminate cannot be ignored on Windows)")

        # refusals happen before any child is started
        keep = os.path.join(tmp, "existing")
        os.mkdir(keep)
        with open(os.path.join(keep, "keep.txt"), "w") as f:
            f.write("keep")
        _write_json(cell_path, _cell(stub))
        rc = _quiet_main(["--cell", cell_path, "--plan", plan, "--run-dir", keep])
        with open(os.path.join(keep, "keep.txt")) as f:
            kept = f.read()
        check("an existing run directory is not overwritten", rc == 2 and kept == "keep"
              and os.listdir(keep) == ["keep.txt"])
        loaded = []

        def sentinel_loader(name):
            loaded.append(name)
            raise AssertionError("load_backend must not be reached without the send flag")

        original_loader = EM.load_backend
        EM.load_backend = sentinel_loader
        try:
            rc, d = go("real", _cell(stub, {"backend": "macos"}))
        finally:
            EM.load_backend = original_loader
        check("a real backend without the send flag exits 2 and starts nothing",
              rc == 2 and loaded == [] and not os.path.exists(d))
        bad_plan = os.path.join(tmp, "bad_plan.jsonl")
        with open(bad_plan, "w") as f:
            f.write("not a plan\n")
        rc, d = go("badplan", _cell(stub), plan_path=bad_plan)
        check("an invalid plan exits 2 and starts nothing", rc == 2 and not os.path.exists(d))
        cell = _cell(stub)
        del cell["reset_cmd"]
        rc, d = go("missing_key", cell)
        check("a cell with a missing key exits 2 and starts nothing", rc == 2 and not os.path.exists(d))
        rc, d = go("unknown_key", _cell(stub, {"rest_cmd": []}))
        check("a cell with an unknown key exits 2 and starts nothing", rc == 2 and not os.path.exists(d))
        rc, d = go("no_out", _cell(stub, {"logger_cmd": [sys.executable, stub]}))
        check("a child command that never receives its log path exits 2", rc == 2 and not os.path.exists(d))
        rc, d = go("os_mismatch", _cell(stub, {"os": "windows"}))
        check("a cell whose os differs from the plan's exits 2", rc == 2 and not os.path.exists(d))
        check("no argument at all exits 2", _quiet_main([]) == 2)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
