"""Shared helpers: paths, SHA-256 checks of the inputs, loading the earlier experiment's code, seeds.

The earlier experiment's modules (build_segments.py, romaji_table.py) are imported only after their bytes match
the SHA-256 in config.json "code".
"""
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(EXP))
PRIOR_SCRIPTS = os.path.join(REPO, "experiments", "20261009-length-sequence-uniqueness", "scripts")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def repo_path(rel):
    return os.path.join(REPO, *rel.split("/"))


def load_config(path=None):
    path = path or os.path.join(EXP, "config.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def read_seed(path=None):
    path = path or os.path.join(EXP, "SEED")
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def check_inputs(cfg):
    """Stops when an input or the earlier experiment's code does not match config.json."""
    bad = []
    for name, e in cfg["inputs"].items():
        if sha256_file(repo_path(e["path"])) != e["sha256"]:
            bad.append(e["path"])
    for rel, want in cfg["code"].items():
        if sha256_file(repo_path(rel)) != want:
            bad.append(rel)
    if bad:
        raise SystemExit("check_inputs: SHA-256 differs from config.json: %s" % ", ".join(bad))


_MODULES = {}


def prior_module(name, cfg):
    """Import experiments/20261009-length-sequence-uniqueness/scripts/<name>.py after checking its SHA-256.
    The module is executed from the bytes that were hashed."""
    if name in _MODULES:
        return _MODULES[name]
    rel = "experiments/20261009-length-sequence-uniqueness/scripts/%s.py" % name
    want = cfg["code"].get(rel)
    path = repo_path(rel)
    with open(path, "rb") as f:
        data = f.read()
    if want is None or sha256_bytes(data) != want:
        raise SystemExit("prior_module: %s does not match config.json" % rel)
    if name == "build_segments":
        prior_module("romaji_table", cfg)  # build_segments imports romaji_table by name
    spec = importlib.util.spec_from_loader(name, loader=None, origin=path)
    mod = importlib.util.module_from_spec(spec)
    mod.__file__ = path
    sys.modules[name] = mod
    exec(compile(data, path, "exec"), mod.__dict__)
    _MODULES[name] = mod
    return mod


def seed_int(*parts):
    """64-bit integer from the SHA-256 of the parts joined with ':'."""
    return int.from_bytes(hashlib.sha256(":".join(str(p) for p in parts).encode("utf-8")).digest()[:8], "big")


def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
