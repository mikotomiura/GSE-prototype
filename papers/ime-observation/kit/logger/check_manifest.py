#!/usr/bin/env python3
# kit: selftest
"""単体ロガーの manifest 照合器（Python 標準ライブラリだけ）。

  check_manifest.py --self                           コピーが manifest と一致（GSE を読まない・公開 repo でも回る）
  check_manifest.py --against-gse [--repo DIR]       GSE の現在のファイルと一致（ずれの検出）
  check_manifest.py --update --manifest FILE --entries SPEC.json [--repo DIR]
                                                     指定した 1 つの manifest だけを書き直す（他の manifest*.json は書かない）
  check_manifest.py --selftest                       陰性対照（速い既定・数秒）

対象は kit/logger/（このファイルのあるディレクトリ・--logger-dir で変えられる）の manifest*.json を**すべて**。
exit 0 = 一致 / 1 = 不一致（または manifest が 0 本・エントリが 0 件の空振り） / 2 = 使い方の誤り・読めない。

エントリの kind:
  file    ファイル全体が GSE の gse_path と同じ（逐語コピー）
  excerpt 範囲が GSE の gse_path の範囲と同じ。GSE 側 = 開始アンカーの行を含み終了アンカーの行を含まない範囲
          （行全体の一致・行末の空白を除く・アンカーはファイル中にちょうど 1 回）。
          コピー側 = `// @excerpt-begin <id>` と `// @excerpt-end <id>` の**間**。
  new     新規に書いたファイル（reason が要る）。gse_path があれば、そのファイルの `pub const|static NAME: T = V;` と
          型・値が同じことを --against-gse が確かめる（シムの値の照合）。
SHA-256 は CRLF を LF に揃えてから取る。path は logger ディレクトリからの相対・gse_path は repo のルートからの相対。
"""
import argparse
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

for _s in (sys.stdout, sys.stderr):  # cp932 の端末でも日本語の出力で落ちない
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS = ("file", "excerpt", "new")
FIELDS = ("kind", "id", "path", "gse_path", "gse_last_commit", "start_anchor", "end_anchor", "symbol", "sha256", "reason")
DECL = re.compile(r"^\s*pub\s+(const|static)\s+(\w+)\s*:\s*([^=]+?)\s*=\s*(.+?)\s*;")


class Bad(Exception):
    pass


def norm(b):
    return b.replace(b"\r\n", b"\n")


def sha(b):
    return hashlib.sha256(norm(b)).hexdigest()


def read_bytes(path):
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError as e:
        raise Bad("読めない: %s (%s)" % (path, e.strerror))


def to_lines(b):
    lines = norm(b).decode("utf-8").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def join(lines):
    return "".join(l + "\n" for l in lines).encode("utf-8")


def once(lines, want, what):
    hits = [i for i, l in enumerate(lines) if l.rstrip() == want.rstrip()]
    if len(hits) != 1:
        raise Bad("%s がちょうど 1 回でない（%d 回）" % (what, len(hits)))
    return hits[0]


def copy_range(lines, eid):
    b, e = once(lines, "// @excerpt-begin " + eid, "コピー側の @excerpt-begin " + eid), once(lines, "// @excerpt-end " + eid, "コピー側の @excerpt-end " + eid)
    if e < b:
        raise Bad("@excerpt-end が @excerpt-begin より前（%s）" % eid)
    return lines[b + 1:e]


def gse_range(lines, ent):
    if not ent.get("start_anchor") or not ent.get("end_anchor"):
        raise Bad("excerpt にアンカーが無い（%s）" % ent.get("id"))
    s = once(lines, ent["start_anchor"], "開始アンカー")
    e = once(lines, ent["end_anchor"], "終了アンカー")
    if e <= s:
        raise Bad("終了アンカーが開始アンカーより前")
    return lines[s:e]


def decls(lines):
    out = {}
    for l in lines:
        m = DECL.match(l)
        if m:
            out[m.group(2)] = (m.group(1), " ".join(m.group(3).split()), m.group(4))
    return out


def manifests(ldir):
    paths = sorted(glob.glob(os.path.join(ldir, "manifest*.json")))
    if not paths:
        raise Bad("manifest*.json が 1 本も無い（空振りの緑を出さない）: " + ldir)
    out = []
    for p in paths:
        try:
            m = json.loads(read_bytes(p).decode("utf-8"))
        except ValueError:
            raise Bad("JSON として読めない: " + os.path.basename(p))
        if not isinstance(m, dict) or not m.get("entries"):
            raise Bad("エントリが 0 件（空振りの緑を出さない）: " + os.path.basename(p))
        out.append((os.path.basename(p), m))
    return out


def safe_rel(p, what):
    if not isinstance(p, str) or not p or os.path.isabs(p) or ".." in p.replace("\\", "/").split("/") or ":" in p:
        raise Bad("%s が相対パスでない: %r" % (what, p))
    return p


def copy_bytes(ldir, ent):
    """コピー側の照合対象のバイト列。"""
    if ent.get("kind") not in KINDS:
        raise Bad("kind が不正: %r" % ent.get("kind"))
    lines = to_lines(read_bytes(os.path.join(ldir, safe_rel(ent.get("path"), "path"))))
    if ent["kind"] == "excerpt":
        return join(copy_range(lines, ent.get("id")))
    if ent["kind"] == "new" and not ent.get("reason"):
        raise Bad("new に reason が無い")
    return join(lines)


def each_entry(ldir, check):
    errs = []
    for name, m in manifests(ldir):
        for ent in m["entries"]:
            try:
                check(ent)
            except (Bad, UnicodeDecodeError) as e:
                errs.append("%s: %s: %s" % (name, ent.get("id"), e))
    return errs


def check_self(ldir):
    def one(ent):
        if sha(copy_bytes(ldir, ent)) != ent.get("sha256"):
            raise Bad("SHA-256 が一致しない（%s）" % ent.get("path"))
    return each_entry(ldir, one)


def check_gse_entry(repo, ldir, ent):
    kind = ent.get("kind")
    if kind == "new" and not ent.get("gse_path"):
        return
    lines = to_lines(read_bytes(os.path.join(repo, safe_rel(ent.get("gse_path"), "gse_path"))))
    if kind == "new":  # シム: pub const / static の型と値が GSE と同じ
        mine = decls(to_lines(read_bytes(os.path.join(ldir, safe_rel(ent.get("path"), "path")))))
        theirs = decls(lines)
        for name, d in sorted(mine.items()):
            if theirs.get(name) != d:
                raise Bad("シムの %s が GSE と違う（型か値・GSE 側に無い場合も含む）" % name)
        return
    body = gse_range(lines, ent) if kind == "excerpt" else lines
    if sha(join(body)) != ent.get("sha256"):
        raise Bad("GSE の現在のファイルと SHA-256 が一致しない（%s）" % ent.get("gse_path"))
    sym = ent.get("symbol")
    if kind == "excerpt" and sym and not re.search(r"\b(?:fn|enum|struct)\s+" + re.escape(sym) + r"\b", "\n".join(body)):
        raise Bad("symbol %s が範囲の中に無い" % sym)


def check_against_gse(ldir, repo):
    return each_entry(ldir, lambda ent: check_gse_entry(repo, ldir, ent))


def git(repo, *args):
    try:
        r = subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def default_repo(ldir):
    return git(ldir, "rev-parse", "--show-toplevel") or os.path.abspath(os.path.join(ldir, "..", "..", "..", ".."))


def update(ldir, repo, manifest, spec_path):
    base = os.path.basename(manifest)
    here = os.path.normcase(os.path.dirname(os.path.abspath(manifest)))
    if not (base.startswith("manifest") and base.endswith(".json")) or here != os.path.normcase(os.path.abspath(ldir)):
        raise Bad("--manifest は logger ディレクトリの manifest*.json であること: " + manifest)
    spec = json.loads(read_bytes(spec_path).decode("utf-8"))
    entries = []
    for s in spec:
        ent = {k: s.get(k) for k in FIELDS}
        ent["sha256"] = sha(copy_bytes(ldir, ent))
        ent["gse_last_commit"] = (git(repo, "log", "-1", "--format=%H", "--", ent["gse_path"]) or None) if ent["gse_path"] else None
        if ent["gse_path"] and not ent["gse_last_commit"]:
            print("WARN: gse_last_commit を取れない（未コミット？）: " + ent["gse_path"], file=sys.stderr)
        entries.append(ent)
    for ent in entries:  # ★ コピーが GSE と逐語でない manifest は書かない
        check_gse_entry(repo, ldir, ent)
    head = git(repo, "rev-parse", "HEAD")
    if not head:
        print("WARN: gse_repo_commit を取れない", file=sys.stderr)
    text = json.dumps({"gse_repo_commit": head, "entries": entries}, ensure_ascii=False, indent=2) + "\n"
    with open(manifest, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ---------------------------------------------------------------------------
# selftest
# ---------------------------------------------------------------------------
GSE_A = "// header\npub const K: u32 = 0x19; // c\npub fn alpha() -> u32 {\n    1\n}\n/// START\npub fn beta() -> u32 {\n    2\n}\n/// END\npub fn gamma() {}\n"
EXCERPT = "use std::io;\n// @excerpt-begin ex1\n/// START\npub fn beta() -> u32 {\n    2\n}\n// @excerpt-end ex1\n"
SPEC = [
    {"kind": "file", "id": "a", "path": "src/a_copy.rs", "gse_path": "src-tauri/src/a.rs"},
    {"kind": "excerpt", "id": "ex1", "path": "src/ex.rs", "gse_path": "src-tauri/src/a.rs", "start_anchor": "/// START", "end_anchor": "/// END", "symbol": "beta"},
    {"kind": "new", "id": "shim", "path": "src/shim.rs", "gse_path": "src-tauri/src/a.rs", "reason": "シム"},
]
SPEC_B = [{"kind": "new", "id": "other", "path": "src/other.rs", "reason": "別の manifest の持ち物"}]


def selftest():
    fails = []
    tmp = tempfile.mkdtemp(prefix="check_manifest_selftest_")
    repo, ldir = os.path.join(tmp, "repo"), os.path.join(tmp, "logger")
    script = os.path.abspath(__file__)

    def put(base, rel, text):
        p = os.path.join(base, rel)
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
            fails.append("%s: exit %d（期待 %d）%s" % (name, rc, rc_want, out.strip()[-160:]))

    def mutated(path, old, new, name, args, needle):  # 1 か所を変えて赤を確かめ、元に戻す
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

    gse = put(repo, "src-tauri/src/a.rs", GSE_A)
    cpy = put(ldir, "src/a_copy.rs", GSE_A)
    ex = put(ldir, "src/ex.rs", EXCERPT)
    shim = put(ldir, "src/shim.rs", "pub const K: u32 = 0x19;\n")
    other = put(ldir, "src/other.rs", "// 別\n")
    spec = put(tmp, "spec.json", json.dumps(SPEC, ensure_ascii=False))
    spec_b = put(tmp, "spec_b.json", json.dumps(SPEC_B, ensure_ascii=False))
    mf, mf_b = os.path.join(ldir, "manifest.json"), os.path.join(ldir, "manifest.other.json")

    expect("manifest が 0 本なら赤", ["--self"], 1, "manifest")
    expect("--update (B)", ["--update", "--manifest", mf_b, "--entries", spec_b], 0)
    expect("--update (A)", ["--update", "--manifest", mf, "--entries", spec], 0)
    expect("陽性対照 --self", ["--self"], 0)
    expect("陽性対照 --against-gse", ["--against-gse"], 0)

    mutated(cpy, "alpha", "alphb", "陰性 1: コピーを 1 バイト変えると --self が赤", ["--self"], "一致しない")
    mutated(ex, "2\n", "3\n", "陰性 1b: 抜粋のコピーを 1 バイト変えると --self が赤", ["--self"], "一致しない")
    mutated(ex, "// @excerpt-end ex1", "// @excerpt-end ex2", "陰性 1c: コピー側の目印が無いと --self が赤", ["--self"], "@excerpt-end")
    mutated(other, "別", "他", "陰性 1d: 別の manifest のコピーも --self が読む", ["--self"], "manifest.other.json")
    mutated(gse, "alpha", "alphb", "陰性 2: GSE 側を 1 バイト変えると --against-gse が赤", ["--against-gse"], "GSE")
    mutated(gse, "/// START\n", "/// STARt\n", "陰性 3: アンカーが見つからないと赤", ["--against-gse"], "アンカー")
    mutated(gse, "/// END\n", "/// END\n/// START\n", "陰性 4: アンカーが 2 回現れると赤", ["--against-gse"], "アンカー")
    mutated(gse, "pub const K: u32 = 0x19;", "pub const K: u32 = 0x1A;", "陰性 7: シムの値が GSE と違うと赤", ["--against-gse"], "シム")
    mutated(mf, '"symbol": "beta"', '"symbol": "gamma"', "陰性 5: symbol が範囲に無いと赤", ["--against-gse"], "symbol")

    before = read_bytes(mf_b)
    expect("陰性 6: --update --manifest A が B を書き換えない（実行）", ["--update", "--manifest", mf, "--entries", spec], 0)
    if read_bytes(mf_b) != before:
        fails.append("陰性 6: --update --manifest A が manifest.other.json を書き換えた")
    expect("陰性 6b: --manifest が別のディレクトリなら拒否", ["--update", "--manifest", os.path.join(tmp, "manifest.json"), "--entries", spec], 2)
    expect("更新後も陽性", ["--self"], 0)

    shutil.rmtree(tmp, ignore_errors=True)
    for f in fails:
        print("NG:", f)
    if not fails:
        print("check_manifest selftest ok")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for flag in ("--self", "--against-gse", "--update", "--selftest"):
        ap.add_argument(flag, action="store_true")
    ap.add_argument("--manifest")
    ap.add_argument("--entries")
    ap.add_argument("--logger-dir", default=HERE)
    ap.add_argument("--repo")
    a = ap.parse_args()
    modes = [f for f in ("self", "against_gse", "update", "selftest") if getattr(a, f)]
    if len(modes) != 1:
        print("--self / --against-gse / --update / --selftest のどれか 1 つ", file=sys.stderr)
        return 2
    if a.selftest:
        return selftest()
    ldir = os.path.abspath(a.logger_dir)
    repo = os.path.abspath(a.repo) if a.repo else default_repo(ldir)
    try:
        if a.update:
            if not (a.manifest and a.entries):
                print("--update には --manifest と --entries が要る", file=sys.stderr)
                return 2
            update(ldir, repo, a.manifest, a.entries)
            return 0
        errs = check_self(ldir) if a.self else check_against_gse(ldir, repo)
    except Bad as e:
        print("NG:", e)
        return 2 if a.update else 1
    for e in errs:
        print("NG:", e)
    print("%s: %s" % ("--self" if a.self else "--against-gse", "不一致 %d 件" % len(errs) if errs else "一致"))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
