"""Shared helpers: paths, SHA-256 checks of the inputs, loading the earlier experiment's code, seeds.

The earlier experiment's modules (build_segments.py, romaji_table.py) are imported only after their bytes match
the SHA-256 in config.json "code".
"""
import hashlib
import importlib.util
import json
import os
import sys
import tempfile

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
        # RuntimeError, not SystemExit: this also runs in pool workers, where SystemExit would hang the pool
        raise RuntimeError("prior_module: %s does not match config.json" % rel)
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


def inside_git_tree(path):
    """True when `path` (resolved) or one of its parents holds a .git entry (any checkout or worktree)."""
    p = os.path.realpath(path)
    while True:
        if os.path.exists(os.path.join(p, ".git")):
            return True
        parent = os.path.dirname(p)
        if parent == p:
            return False
        p = parent


def assert_private_dir(path):
    """Stops unless `path` is outside every git checkout (record-derived files go only there; data.md)."""
    if inside_git_tree(path) or inside_git_tree(os.path.dirname(os.path.abspath(path))):
        raise SystemExit("the work directory must be outside every git checkout: %s" % path)


def write_private_json(path, obj):
    """write_json for record-derived files: the directory must be outside every git checkout and the file
    must not be a symbolic link. The data go to a new temporary file in that directory, which then replaces
    the name, so a hard link to an existing file (possibly inside a checkout) is never written through."""
    d = os.path.dirname(os.path.abspath(path))
    assert_private_dir(d)
    if os.path.islink(path):
        raise SystemExit("refusing to write through a link: %s" % path)
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", suffix=".json", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def corpus_build_key(cfg):
    """SHA-256 of what the corpus and the copy segments are built from: the text rule, the inputs, the earlier
    experiment's code and this experiment's build code. Stored in corpus_g1_stats.json and checked on reuse."""
    parts = {"text_rule": cfg["text_rule"], "inputs": cfg["inputs"], "code": cfg["code"],
             "own": {n: sha256_file(os.path.join(HERE, n)) for n in ("g1rule.py", "build_corpus.py", "common.py")}}
    return sha256_bytes(json.dumps(parts, sort_keys=True, ensure_ascii=False).encode("utf-8"))


def stats_body_sha256(stats):
    """SHA-256 of corpus_g1_stats.json without its own body_sha256 field (detects an edited value)."""
    body = {k: v for k, v in stats.items() if k != "body_sha256"}
    return sha256_bytes(json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8"))


def check_corpus_current(cfg, stats_path, corpus_path, copy_path):
    """Stops unless corpus_g1_stats.json records the current build key and the SHA-256 of both outputs."""
    st = read_json(stats_path)
    bad = []
    if st.get("body_sha256") != stats_body_sha256(st):
        bad.append("corpus_g1_stats.json was edited")
    if st.get("build_key") != corpus_build_key(cfg):
        bad.append("build key (rule, inputs or code changed; rebuild with build_corpus.py)")
    if sha256_file(corpus_path) != st.get("corpus_sha256"):
        bad.append(corpus_path)
    if sha256_file(copy_path) != st.get("copy_segments_sha256"):
        bad.append(copy_path)
    if bad:
        raise SystemExit("the corpus is not current: %s" % "; ".join(bad))
    return st


def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
