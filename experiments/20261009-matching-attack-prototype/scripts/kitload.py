"""Load the IME paper's evaluation kit and the previous task's scripts after checking their SHA-256, and check
the input files (design.md sections 1 and 2).

The kit files are imported, not copied, and never written. A file whose SHA-256 differs from config.json stops
the run before anything is read from it. Standard library only.
"""
import hashlib
import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(EXP))
CONFIG = os.path.join(EXP, "config.json")


class CheckError(Exception):
    """An input or a code file is not the one recorded in config.json."""


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def repo_path(rel):
    """A path of config.json, relative to the repository with '/' separators and staying inside it. A
    backslash, a drive or a colon is refused (on Windows they would escape the '..' check), and the resolved
    path must lie under the repository."""
    if (not rel or os.path.isabs(rel) or "\\" in rel or ":" in rel or rel.startswith("/")
            or ".." in rel.split("/")):
        raise CheckError("a path in config.json must be relative to the repository and stay inside it: %s" % rel)
    path = os.path.join(REPO, *rel.split("/"))
    root = os.path.realpath(REPO)
    try:
        inside = os.path.commonpath([os.path.realpath(path), root]) == root
    except ValueError:   # another drive (a junction inside the repository pointing elsewhere)
        inside = False
    if not inside:
        raise CheckError("a path in config.json resolves outside the repository: %s" % rel)
    return path


def load_config(path=CONFIG):
    with open(path, "rb") as f:
        return json.loads(f.read().decode("utf-8"))


def read_seed(path=os.path.join(EXP, "SEED")):
    with open(path, "rb") as f:
        return int(f.read().decode("ascii").strip())


def seed_int(*parts):
    """A 64-bit seed from the SHA-256 of the parts joined with ':' (the previous task's convention)."""
    return int.from_bytes(hashlib.sha256(":".join(str(p) for p in parts).encode("utf-8")).digest()[:8], "big")


def below(rng, n):
    """A uniform integer in [0, n) from rng.random() only (stable across Python versions)."""
    return min(int(rng.random() * n), n - 1)


def percentile(sorted_vals, q):
    """Linear interpolation between the closest ranks (the previous task's percentile)."""
    if not sorted_vals:
        return None
    pos = q * (len(sorted_vals) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


def check_file(rel, want):
    path = repo_path(rel)
    if not os.path.isfile(path):
        raise CheckError("missing file: %s (data.md says where to get it)" % rel)
    got = sha256_file(path)
    if got != want:
        raise CheckError("SHA-256 of %s is %s, not the recorded %s" % (rel, got, want))
    return path


def input_path(cfg, name, check=True):
    """The path of an input named in config.json, after its SHA-256 is checked (when one is recorded)."""
    ent = cfg["inputs"][name]
    if check and "sha256" in ent:
        return check_file(ent["path"], ent["sha256"])
    path = repo_path(ent["path"])
    if not os.path.isfile(path):
        raise CheckError("missing file: %s" % ent["path"])
    return path


def check_run_manifest(cfg):
    """run.json names the SHA-256 of the observation and the plan it produced; both must agree with config.json."""
    path = input_path(cfg, "run_manifest")
    with open(path, "rb") as f:
        run = json.loads(f.read().decode("utf-8"))
    outs = run.get("outputs", {})
    for name in ("obs", "plan"):
        if outs.get(name, {}).get("sha256") != cfg["inputs"][name]["sha256"]:
            raise CheckError("run.json does not name the recorded %s SHA-256" % name)


class Kit(object):
    """The imported modules: closed_set, simulate_obs, generate_plan, romaji, stats, and (prior=True) romaji_table
    and build_segments of the previous task."""


# Module name -> file, in dependency order: each module is executed from the bytes whose SHA-256 was checked and
# registered in sys.modules before the modules that import it, so their `import` statements find the checked
# module instead of searching the path (and no .pyc is read or written).
KIT_MODULES = [
    ("romaji", "papers/ime-observation/kit/gen/romaji.py"),
    ("generate_plan", "papers/ime-observation/kit/gen/generate_plan.py"),
    ("simulate_obs", "papers/ime-observation/kit/e2/simulate_obs.py"),
    ("stats", "papers/ime-observation/kit/analysis/stats.py"),
    ("closed_set", "papers/ime-observation/kit/e2/closed_set.py"),
]
PRIOR_MODULES = [
    ("romaji_table", "experiments/20261009-length-sequence-uniqueness/scripts/romaji_table.py"),
    ("prior_build_segments", "experiments/20261009-length-sequence-uniqueness/scripts/build_segments.py"),
]


def load_checked_module(name, rel, want):
    """Read the file once, check the SHA-256 of those bytes, and execute the same bytes as module `name`."""
    path = repo_path(rel)
    if not os.path.isfile(path):
        raise CheckError("missing file: %s" % rel)
    with open(path, "rb") as f:
        data = f.read()
    got = sha256_bytes(data)
    if got != want:
        raise CheckError("SHA-256 of %s is %s, not the recorded %s" % (rel, got, want))
    mod = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader=None, origin=path))
    mod.__file__ = path
    sys.modules[name] = mod
    try:
        exec(compile(data, path, "exec"), mod.__dict__)
    except BaseException:
        del sys.modules[name]
        raise
    return mod


def import_kit(cfg, prior=False):
    sys.dont_write_bytecode = True
    wanted = list(KIT_MODULES) + (list(PRIOR_MODULES) if prior else [])
    for _, rel in wanted:
        if rel not in cfg["code"]:
            raise CheckError("config.json records no SHA-256 for %s" % rel)
    kit = Kit()
    saved = list(sys.path)
    try:
        for name, rel in wanted:
            if name in sys.modules and getattr(sys.modules[name], "__file__", None) is not None and \
                    os.path.normcase(sys.modules[name].__file__) == os.path.normcase(repo_path(rel)) and \
                    getattr(sys.modules[name], "_kitload_sha256", None) == cfg["code"][rel]:
                mod = sys.modules[name]
            else:
                mod = load_checked_module(name, rel, cfg["code"][rel])
                mod._kitload_sha256 = cfg["code"][rel]
            setattr(kit, {"prior_build_segments": "build_segments"}.get(name, name), mod)
    finally:
        # The kit and the previous task's modules insert their directories into sys.path when they run; the
        # previous task's directory holds scripts with the same names as ours (matching, selftest, summarize), so
        # the path is restored.
        sys.path[:] = saved
    # every module the kit imports by name must be the checked one
    for name, rel in KIT_MODULES + (PRIOR_MODULES if prior else []):
        mod = sys.modules.get(name)
        if mod is None or getattr(mod, "_kitload_sha256", None) != cfg["code"][rel]:
            raise CheckError("module %s is not the checked file" % name)
    if kit.closed_set.generate_plan is not kit.generate_plan or kit.closed_set.stats is not kit.stats or \
            kit.closed_set.simulate_obs is not kit.simulate_obs or kit.simulate_obs.generate_plan is not \
            kit.generate_plan or kit.generate_plan.romaji is not kit.romaji:
        raise CheckError("a kit module imported another copy of a checked module")
    if prior and kit.build_segments.count_keys is not kit.romaji_table.count_keys:
        raise CheckError("build_segments imported another copy of romaji_table")
    return kit


# ---------------------------------------------------------------- worker initialisation of a multiprocessing Pool
# An exception raised inside a Pool initializer kills the worker, and the Pool starts a new one forever: the run
# hangs instead of stopping (seen with Python 3.11). The initializer is therefore wrapped: an error is kept and
# raised by the first task, which the parent receives through imap.
_INIT_ERROR = []


def guarded_init(fn, *args):
    try:
        fn(*args)
    except BaseException:  # noqa: B036 - kept and re-raised by the task
        import traceback
        _INIT_ERROR.append(traceback.format_exc())


def check_init():
    """Raise in the task what the worker's initialisation raised (a failed check of an input or a code file, or
    any other error; the traceback of the worker is kept in the message)."""
    if _INIT_ERROR:
        raise CheckError("the worker's initialisation failed (a changed input or code file, or another error); "
                         "its traceback:\n%s" % _INIT_ERROR[0])


def load_inputs(cfg, kit):
    """Read the corpus, the recipes and the plan configuration (after checking every SHA-256)."""
    check_run_manifest(cfg)
    corpus = kit.generate_plan.load_corpus(input_path(cfg, "corpus"))
    recipes = kit.generate_plan.load_recipes(input_path(cfg, "recipes"))
    with open(input_path(cfg, "plan_config"), "rb") as f:
        pcfg = json.loads(f.read().decode("utf-8"))
    kit.generate_plan.normalize_config(pcfg)
    return corpus, recipes, pcfg


def write_json(path, obj):
    data = (json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf-8")
    tmp = path + ".part"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)
    return sha256_bytes(data)


def read_json(path, want_sha=None):
    with open(path, "rb") as f:
        data = f.read()
    if want_sha is not None and sha256_bytes(data) != want_sha:
        raise CheckError("SHA-256 of %s differs from the one recorded" % path)
    return json.loads(data.decode("utf-8")), sha256_bytes(data)
