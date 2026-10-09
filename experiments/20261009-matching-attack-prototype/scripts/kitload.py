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
    if os.path.isabs(rel) or ".." in rel.split("/"):
        raise CheckError("a path in config.json must be relative to the repository and stay inside it: %s" % rel)
    return os.path.join(REPO, *rel.split("/"))


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
    """The imported modules: closed_set, simulate_obs, generate_plan, romaji, and (prior=True) romaji_table and
    build_segments of the previous task."""


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def import_kit(cfg, prior=False):
    for rel, want in cfg["code"].items():
        if rel.startswith("experiments/") and not prior:
            continue
        check_file(rel, want)
    kit = Kit()
    saved = list(sys.path)
    try:
        e2 = repo_path("papers/ime-observation/kit/e2")
        for sub in ("e2", "gen", "analysis"):
            p = repo_path("papers/ime-observation/kit/" + sub)
            if p not in sys.path:
                sys.path.insert(0, p)
        kit.closed_set = _load_module("closed_set", os.path.join(e2, "closed_set.py"))
        kit.simulate_obs = sys.modules["simulate_obs"]
        kit.generate_plan = sys.modules["generate_plan"]
        kit.romaji = sys.modules["romaji"]
        if prior:
            pdir = repo_path("experiments/20261009-length-sequence-uniqueness/scripts")
            sys.path.insert(0, pdir)
            kit.romaji_table = _load_module("romaji_table", os.path.join(pdir, "romaji_table.py"))
            kit.build_segments = _load_module("prior_build_segments", os.path.join(pdir, "build_segments.py"))
    finally:
        # The previous task's directory holds scripts with the same names as ours (matching, selftest,
        # summarize); it must not stay on the path.
        sys.path[:] = saved
    for mod_name, mod in (("closed_set", kit.closed_set), ("simulate_obs", kit.simulate_obs),
                          ("generate_plan", kit.generate_plan), ("romaji", kit.romaji)):
        rel = {"closed_set": "papers/ime-observation/kit/e2/closed_set.py",
               "simulate_obs": "papers/ime-observation/kit/e2/simulate_obs.py",
               "generate_plan": "papers/ime-observation/kit/gen/generate_plan.py",
               "romaji": "papers/ime-observation/kit/gen/romaji.py"}[mod_name]
        if os.path.normcase(os.path.abspath(mod.__file__)) != os.path.normcase(repo_path(rel)):
            raise CheckError("module %s was imported from %s, not from the checked file" % (mod_name, mod.__file__))
    return kit


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
