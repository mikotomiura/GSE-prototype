#!/usr/bin/env python3
# kit: selftest
"""単体ロガーの manifest を、写した元の GSE ソースツリーと突き合わせる内部の道具（公開しない）。

  check_manifest_upstream.internal.py --against-upstream [--repo DIR]
      copies match the reference source tree's current files (detects drift)
  check_manifest_upstream.internal.py --update --manifest FILE --entries SPEC.json [--repo DIR]
      rewrites exactly one manifest, merging by id (an entry whose id already exists is replaced;
      every other existing entry is kept; no other manifest*.json is touched)
  check_manifest_upstream.internal.py --selftest
      negative-control suite (fast by default, a few seconds)

対象は `check_manifest.py` と同じ manifest*.json（`--logger-dir` で上書き可）。公開用の `check_manifest.py`
から自己照合（`--self`）まわりの共通処理を import し、ここでは写した元との照合だけを持つ。
出どころの記録は `PROVENANCE.internal.md` を参照。

Entry kinds:
  file    the whole file is identical to the reference file at upstream_path (verbatim copy).
  excerpt a range is identical to a range of the reference file at upstream_path. The reference range
          is the lines from the start anchor (inclusive) to the end anchor (exclusive); matching is by
          whole line, ignoring trailing whitespace, and each anchor must occur exactly once in the
          file. The copy-side range is the lines strictly between `// @excerpt-begin <id>` and
          `// @excerpt-end <id>`.
  new     a file written independently of the reference implementation (a reason is required). Two
          independent checks run, each only when its fields are present (upstream_path alone triggers
          neither):
          - check_decls: true verifies that the type and value of every `pub const|static NAME: T = V;`
            declaration on the copy side matches the reference declaration (used to pin a shim's
            constants and statics to their source of truth).
          - start_anchor / end_anchor / upstream_range_sha256, when present, verify that the SHA-256 of
            the reference range (sliced the same way as an excerpt) still equals
            upstream_range_sha256, detecting a change in the reference implementation's own logic even
            though the copy need not be verbatim.
`upstream_path` is relative to the root of the reference source tree (a leading `/` or `\\`, NUL, or a
path that escapes the base directory is rejected). Exit code: 0 = match / 1 = mismatch / 2 = usage
error, unreadable input, zero manifests, zero entries, a path-safety violation or malformed JSON.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_manifest as base  # noqa: E402  公開用の自己照合の共通処理を再利用する

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

HERE = base.HERE
Bad = base.Bad
Unsafe = base.Unsafe
FIELDS = (
    "kind", "id", "path", "upstream_path", "upstream_last_commit", "start_anchor", "end_anchor",
    "symbol", "sha256", "upstream_range_sha256", "check_decls", "reason",
)
DECL = re.compile(r"^\s*pub\s+(const|static)\s+(\w+)\s*:\s*([^=]+?)\s*=\s*(.+?)\s*;")


def decls(lines):
    out = {}
    for l in lines:
        m = DECL.match(l)
        if m:
            out[m.group(2)] = (m.group(1), " ".join(m.group(3).split()), m.group(4))
    return out


def read_upstream_lines(repo, ent):
    return base.to_lines(base.read_bytes(base.safe_join(repo, ent.get("upstream_path"), "upstream_path")))


def upstream_range(lines, ent):
    if not ent.get("start_anchor") or not ent.get("end_anchor"):
        raise Bad("excerpt has no anchors (%s)" % ent.get("id"))
    s = base.once(lines, ent["start_anchor"], "start anchor")
    e = base.once(lines, ent["end_anchor"], "end anchor")
    if e <= s:
        raise Bad("the end anchor precedes the start anchor")
    return lines[s:e]


def check_new_entry(repo, ldir, ent):
    """Checks a `kind: "new"` entry. Two independent checks run, each only when its fields are present
    (upstream_path alone triggers neither)."""
    did_check = False
    if ent.get("check_decls"):
        if not ent.get("upstream_path"):
            raise Bad("check_decls is true but upstream_path is missing")
        mine = decls(base.read_copy_lines(ldir, ent))
        theirs = decls(read_upstream_lines(repo, ent))
        for name, d in sorted(mine.items()):
            if theirs.get(name) != d:
                raise Bad("shim declaration %s differs from the reference (type, value, or the reference declaration is absent)" % name)
        did_check = True
    if ent.get("start_anchor") or ent.get("end_anchor"):
        if not ent.get("upstream_path"):
            raise Bad("start_anchor/end_anchor are present but upstream_path is missing")
        want = ent.get("upstream_range_sha256")
        if not want:
            raise Bad("a new entry has anchors but no upstream_range_sha256")
        body = upstream_range(read_upstream_lines(repo, ent), ent)
        if base.sha(base.join(body)) != want:
            raise Bad("the reference implementation's logic in this range has changed (upstream_range_sha256 mismatch, %s)" % ent.get("upstream_path"))
        sym = ent.get("symbol")
        if sym and not re.search(r"\b(?:fn|enum|struct)\s+" + re.escape(sym) + r"\b", "\n".join(body)):
            raise Bad("symbol %s does not occur in the range" % sym)
        did_check = True
    if not did_check:
        return  # Neither check_decls nor an anchor pair: --against-upstream checks nothing (--self only).


def check_upstream_entry(repo, ldir, ent):
    kind = ent.get("kind")
    if kind == "new":
        check_new_entry(repo, ldir, ent)
        return
    lines = read_upstream_lines(repo, ent)
    body = upstream_range(lines, ent) if kind == "excerpt" else lines
    if base.sha(base.join(body)) != ent.get("sha256"):
        raise Bad("SHA-256 mismatch against the reference implementation's current file (%s)" % ent.get("upstream_path"))
    sym = ent.get("symbol")
    if kind == "excerpt" and sym and not re.search(r"\b(?:fn|enum|struct)\s+" + re.escape(sym) + r"\b", "\n".join(body)):
        raise Bad("symbol %s does not occur in the range" % sym)


def check_against_upstream(ldir, repo):
    return base.each_entry(ldir, lambda ent: check_upstream_entry(repo, ldir, ent))


def git(repo, *args):
    try:
        r = subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def default_repo(ldir):
    return git(ldir, "rev-parse", "--show-toplevel") or os.path.abspath(os.path.join(ldir, "..", "..", "..", ".."))


def update(ldir, repo, manifest, spec_path):
    base_name = os.path.basename(manifest)
    here = os.path.normcase(os.path.dirname(os.path.abspath(manifest)))
    if not (base_name.startswith("manifest") and base_name.endswith(".json")) or here != os.path.normcase(os.path.abspath(ldir)):
        raise Bad("--manifest must be a manifest*.json in the logger directory: " + manifest)
    if os.path.islink(manifest):
        raise Unsafe("--manifest is a symbolic link: " + manifest)
    try:
        spec = json.loads(base.read_bytes(spec_path).decode("utf-8"))
    except ValueError:
        raise Bad("cannot parse --entries as JSON: " + spec_path)
    if not isinstance(spec, list):
        raise Bad("--entries must be an array: " + spec_path)

    # Merges into the existing manifest by id: an entry whose id already exists is replaced, every
    # other existing entry is kept. No other manifest*.json is opened here.
    existing = []
    if os.path.exists(manifest):
        try:
            prev = json.loads(base.read_bytes(manifest).decode("utf-8"))
        except ValueError:
            raise Bad("cannot parse the existing manifest as JSON: " + manifest)
        if isinstance(prev, dict) and isinstance(prev.get("entries"), list):
            existing = prev["entries"]
    order = [e.get("id") for e in existing if isinstance(e, dict)]
    by_id = {e.get("id"): e for e in existing if isinstance(e, dict)}

    for s in spec:
        if not isinstance(s, dict) or not s.get("id"):
            raise Bad("an --entries element has no id: %r" % (s,))
        ent = {k: s.get(k) for k in FIELDS}
        ent["sha256"] = base.sha(base.copy_bytes(ldir, ent))
        if ent.get("kind") == "new" and ent.get("upstream_path") and ent.get("start_anchor") and ent.get("end_anchor"):
            ent["upstream_range_sha256"] = base.sha(base.join(upstream_range(read_upstream_lines(repo, ent), ent)))
        else:
            ent["upstream_range_sha256"] = None
        ent["upstream_last_commit"] = (git(repo, "log", "-1", "--format=%H", "--", ent["upstream_path"]) or None) if ent["upstream_path"] else None
        if ent["upstream_path"] and not ent["upstream_last_commit"]:
            print("WARN: cannot determine upstream_last_commit (uncommitted?): " + ent["upstream_path"], file=sys.stderr)
        check_upstream_entry(repo, ldir, ent)  # Refuses to write unless the copy matches the reference.
        if ent["id"] not in by_id:
            order.append(ent["id"])
        by_id[ent["id"]] = ent

    entries = [by_id[i] for i in order]
    head = git(repo, "rev-parse", "HEAD")
    if not head:
        print("WARN: cannot determine upstream_repo_commit", file=sys.stderr)
    text = json.dumps({"upstream_repo_commit": head, "entries": entries}, ensure_ascii=False, indent=2) + "\n"
    with open(manifest, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ---------------------------------------------------------------------------
# selftest（判断 33 の範囲のずれ・check_decls・symbol・別 manifest 不変・別ディレクトリ拒否 を含む）
# ---------------------------------------------------------------------------
SPEC = [
    {"kind": "file", "id": "a", "path": "src/a_copy.rs", "upstream_path": "reference/src/a.rs"},
    {"kind": "excerpt", "id": "ex1", "path": "src/ex.rs", "upstream_path": "reference/src/a.rs", "start_anchor": "/// START", "end_anchor": "/// END", "symbol": "beta"},
    {"kind": "new", "id": "shim", "path": "src/shim.rs", "upstream_path": "reference/src/a.rs", "check_decls": True, "reason": "shim"},
]
SPEC_B = [{"kind": "new", "id": "other", "path": "src/other.rs", "reason": "belongs to a different manifest"}]
# An entry that lets a `new` kind still detect upstream drift (anchors plus upstream_range_sha256).
SPEC_JUDGMENT = [
    {
        "kind": "new", "id": "judgment", "path": "src/judgment.rs", "upstream_path": "reference/src/a.rs",
        "start_anchor": "/// START", "end_anchor": "/// END", "symbol": "beta",
        "reason": "a transcription of the same logic as beta, written independently",
    }
]


def selftest():
    fails = []
    tmp = tempfile.mkdtemp(prefix="check_manifest_upstream_selftest_")
    repo, ldir = os.path.join(tmp, "repo"), os.path.join(tmp, "logger")
    script = os.path.abspath(__file__)

    def put(base_dir, rel, text):
        p = os.path.join(base_dir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(text.encode("utf-8"))
        return p

    def run(*args):
        r = subprocess.run([sys.executable, script, "--logger-dir", ldir, "--repo", repo] + list(args), capture_output=True,
                           text=True, encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONUTF8="1"), timeout=60)
        return r.returncode, r.stdout + r.stderr

    def expect(name, args, rc_want, needle=None):
        rc, out = run(*args)
        if rc != rc_want or "Traceback" in out or (needle and needle not in out):
            fails.append("%s: exit %d (expected %d) %s" % (name, rc, rc_want, out.strip()[-160:]))

    def mutated(path, old, new, name, args, needle):
        with open(path, "rb") as f:
            orig = f.read()
        assert old.encode() in orig, name
        with open(path, "wb") as f:
            f.write(orig.replace(old.encode(), new.encode(), 1))
        try:
            expect(name, args, 1, needle)
        finally:
            with open(path, "wb") as f:
                f.write(orig)

    upstream = put(repo, "reference/src/a.rs", base.FILE_TEXT)
    put(ldir, "src/a_copy.rs", base.FILE_TEXT)
    ex = put(ldir, "src/ex.rs", base.EXCERPT_TEXT)
    put(ldir, "src/shim.rs", "pub const K: u32 = 0x19;\n")
    put(ldir, "src/other.rs", "// other\n")
    put(ldir, "src/judgment.rs", "// A transcription of the same logic as beta, written independently.\n")
    spec = put(tmp, "spec.json", json.dumps(SPEC, ensure_ascii=False))
    spec_b = put(tmp, "spec_b.json", json.dumps(SPEC_B, ensure_ascii=False))
    spec_judgment = put(tmp, "spec_judgment.json", json.dumps(SPEC_JUDGMENT, ensure_ascii=False))
    mf, mf_b = os.path.join(ldir, "manifest.json"), os.path.join(ldir, "manifest.other.json")

    expect("--update (B)", ["--update", "--manifest", mf_b, "--entries", spec_b], 0)
    expect("--update (A)", ["--update", "--manifest", mf, "--entries", spec], 0)
    expect("positive control --against-upstream", ["--against-upstream"], 0)
    if base.check_self(ldir):
        fails.append("positive control: check_self reports a mismatch right after --update")

    mutated(upstream, "alpha", "alphb", "negative 2: a one-byte change upstream makes --against-upstream fail", ["--against-upstream"], "reference")
    mutated(upstream, "/// START\n", "/// STARt\n", "negative 3: a missing anchor fails", ["--against-upstream"], "anchor")
    mutated(upstream, "/// END\n", "/// END\n/// START\n", "negative 4: an anchor occurring twice fails", ["--against-upstream"], "anchor")
    mutated(upstream, "pub const K: u32 = 0x19;", "pub const K: u32 = 0x1A;", "negative 7: a check_decls value diverging from upstream fails", ["--against-upstream"], "shim")
    mutated(mf, '"symbol": "beta"', '"symbol": "gamma"', "negative 5: a symbol absent from the range fails", ["--against-upstream"], "symbol")

    # check_decls is skipped unless explicitly set (upstream_path alone does not trigger it).
    # Uses an independent logger-dir/repo pair so that this mutation does not also trip the "shim"
    # entry registered above, which does have check_decls set.
    nd = os.path.join(tmp, "nodecls")
    nd_ldir, nd_repo = os.path.join(nd, "logger"), os.path.join(nd, "repo")
    nd_upstream = put(nd_repo, "reference/src/a.rs", base.FILE_TEXT)
    put(nd_ldir, "src/shim.rs", "pub const K: u32 = 0x19;\n")
    nd_spec = put(nd, "spec.json", json.dumps(
        [{"kind": "new", "id": "shim2", "path": "src/shim.rs", "upstream_path": "reference/src/a.rs", "reason": "shim without check_decls"}],
        ensure_ascii=False,
    ))

    def nd_run(*args):
        return subprocess.run(
            [sys.executable, script, "--logger-dir", nd_ldir, "--repo", nd_repo] + list(args),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=dict(os.environ, PYTHONUTF8="1"), timeout=60,
        )

    def nd_expect(name, args, rc_want):
        r = nd_run(*args)
        out = r.stdout + r.stderr
        if r.returncode != rc_want or "Traceback" in out:
            fails.append("%s: exit %d (expected %d) %s" % (name, r.returncode, rc_want, out.strip()[-160:]))

    nd_expect("registers a new entry without check_decls", ["--update", "--manifest", os.path.join(nd_ldir, "manifest.json"), "--entries", nd_spec], 0)
    with open(nd_upstream, "rb") as f:
        nd_orig = f.read()
    try:
        with open(nd_upstream, "wb") as f:
            f.write(nd_orig.replace(b"pub const K: u32 = 0x19;", b"pub const K: u32 = 0x1A;", 1))
        nd_expect("negative control: without check_decls, a value drift leaves --against-upstream passing", ["--against-upstream"], 0)
    finally:
        with open(nd_upstream, "wb") as f:
            f.write(nd_orig)

    before = base.read_bytes(mf_b)
    expect("negative 6: --update --manifest A does not modify B (run)", ["--update", "--manifest", mf, "--entries", spec], 0)
    if base.read_bytes(mf_b) != before:
        fails.append("negative 6: --update --manifest A modified manifest.other.json")
    expect("negative 6b: --manifest outside the logger directory is refused", ["--update", "--manifest", os.path.join(tmp, "manifest.json"), "--entries", spec], 2)

    # --update merges by id: adding judgment later to the same manifest keeps the existing a / ex1 / shim
    # entries.
    expect("adds judgment afterward", ["--update", "--manifest", mf, "--entries", spec_judgment], 0)
    try:
        ids = sorted(e.get("id") for e in json.loads(base.read_bytes(mf).decode("utf-8"))["entries"])
    except (ValueError, KeyError):
        ids = None
    if ids != ["a", "ex1", "judgment", "shim"]:
        fails.append("the id set after the merge is not what was expected: %r" % (ids,))
    expect("still passes --against-upstream after the merge", ["--against-upstream"], 0)

    # A change to the upstream range of an anchored `new` entry makes --against-upstream fail (the copy
    # itself need not be verbatim; this detects a change in the reference implementation's own logic).
    mutated(upstream, "2\n}\n", "9\n}\n", "negative 8: an upstream change inside an anchored new entry's range fails",
            ["--against-upstream"], "judgment")

    # Anchors present but upstream_range_sha256 missing fails.
    m = re.search(r'"id": "judgment".*?"upstream_range_sha256": "([0-9a-f]{64})"', base.read_bytes(mf).decode("utf-8"), re.S)
    if m is None:
        fails.append("the manifest has no upstream_range_sha256 for judgment")
    else:
        mutated(mf, '"upstream_range_sha256": "%s"' % m.group(1), '"upstream_range_sha256": null',
                "negative 9: anchors present but upstream_range_sha256 missing fails", ["--against-upstream"], "upstream_range_sha256")

    # --entries not JSON and a symlinked --manifest (path safety / malformed input, exit 2 not a traceback)
    sec = os.path.join(tmp, "sec")
    sec_ldir, sec_repo = os.path.join(sec, "logger"), os.path.join(sec, "repo")
    os.makedirs(sec_repo, exist_ok=True)

    def sec_run(*args):
        return subprocess.run(
            [sys.executable, script, "--logger-dir", sec_ldir, "--repo", sec_repo] + list(args),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=dict(os.environ, PYTHONUTF8="1"), timeout=60,
        )

    def sec_expect(name, args, rc_want):
        r = sec_run(*args)
        out = r.stdout + r.stderr
        if r.returncode != rc_want or "Traceback" in out:
            fails.append("%s: exit %d (expected %d) %s" % (name, r.returncode, rc_want, out.strip()[-160:]))

    sec_spec_not_json = put(sec, "spec_not_json.txt", "not json {{{")
    put(sec_ldir, "manifest.json", json.dumps({"entries": [{"kind": "new", "id": "z", "path": "z.rs", "reason": "z"}]}, ensure_ascii=False))
    put(sec_ldir, "z.rs", "// z\n")
    sec_expect(
        "negative 13: --entries not JSON is exit 2 (not a traceback)",
        ["--update", "--manifest", os.path.join(sec_ldir, "manifest.json"), "--entries", sec_spec_not_json],
        2,
    )

    try:
        link_target = put(sec, "manifest_target.json", json.dumps({"entries": [{"kind": "new", "id": "z", "path": "z.rs", "reason": "z"}]}))
        link_path = os.path.join(sec_ldir, "manifest.link.json")
        if os.path.exists(link_path) or os.path.islink(link_path):
            os.remove(link_path)
        os.symlink(link_target, link_path)
        sec_spec_empty = put(sec, "spec_empty.json", "[]")
        sec_expect("negative 14: --update refuses a symlinked manifest", ["--update", "--manifest", link_path, "--entries", sec_spec_empty], 2)
    except OSError:
        pass  # Creating a symbolic link requires a privilege some environments lack; skip this control there.

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    for f in fails:
        print("NG:", f)
    if not fails:
        print("check_manifest_upstream selftest ok")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for flag in ("--against-upstream", "--update", "--selftest"):
        ap.add_argument(flag, action="store_true")
    ap.add_argument("--manifest")
    ap.add_argument("--entries")
    ap.add_argument("--logger-dir", default=HERE)
    ap.add_argument("--repo")
    a = ap.parse_args()
    modes = [f for f in ("against_upstream", "update", "selftest") if getattr(a, f)]
    if len(modes) != 1:
        print("exactly one of --against-upstream / --update / --selftest is required", file=sys.stderr)
        return 2
    if a.selftest:
        return selftest()
    ldir = os.path.abspath(a.logger_dir)
    repo = os.path.abspath(a.repo) if a.repo else default_repo(ldir)
    try:
        if a.update:
            if not (a.manifest and a.entries):
                print("--update requires --manifest and --entries", file=sys.stderr)
                return 2
            update(ldir, repo, a.manifest, a.entries)
            return 0
        errs = check_against_upstream(ldir, repo)
    except (Bad, ValueError) as e:
        print("NG:", e)
        return 2
    for e in errs:
        print("NG:", e)
    print("--against-upstream: %s" % ("%d mismatches" % len(errs) if errs else "match"))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
