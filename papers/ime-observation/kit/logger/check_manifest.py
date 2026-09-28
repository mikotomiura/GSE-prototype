#!/usr/bin/env python3
# kit: selftest
"""単体ロガーの manifest 照合器（Python 標準ライブラリだけ）。

  check_manifest.py --self                           コピーが manifest と一致（GSE を読まない・公開 repo でも回る）
  check_manifest.py --against-gse [--repo DIR]       GSE の現在のファイルと一致（ずれの検出）
  check_manifest.py --update --manifest FILE --entries SPEC.json [--repo DIR]
                                                     指定した 1 つの manifest だけを **id 単位でマージ**して書く
                                                     （同じ id は置き換え・他の id は残す。他の manifest*.json は書かない）
  check_manifest.py --selftest                       陰性対照（速い既定・数秒）

対象は kit/logger/（このファイルのあるディレクトリ・--logger-dir で変えられる）の manifest*.json を**すべて**。
exit 0 = 一致 / 1 = 不一致 / 2 = 使い方の誤り・読めない・manifest が 0 本・エントリが 0 件の空振り・
パスの安全性違反（NUL・絶対パス・base の外）・壊れた JSON。

エントリの kind:
  file    ファイル全体が GSE の gse_path と同じ（逐語コピー）
  excerpt 範囲が GSE の gse_path の範囲と同じ。GSE 側 = 開始アンカーの行を含み終了アンカーの行を含まない範囲
          （行全体の一致・行末の空白を除く・アンカーはファイル中にちょうど 1 回）。
          コピー側 = `// @excerpt-begin <id>` と `// @excerpt-end <id>` の**間**。
  new     新規に書いたファイル（reason が要る）。2 つの独立した照合を、明示の欄があるときだけ行う
          （★ 判断 33・issue 011 merge ゲートレビュー item 5 / 6。`gse_path` があるだけでは何も照合しない）:
          - `check_decls: true` なら、コピー側ファイルの `pub const|static NAME: T = V;` の型・値が
            GSE の `gse_path` と同じことを --against-gse が確かめる（シムの値の照合）。
          - `start_anchor` / `end_anchor` / `gse_range_sha256` があれば、GSE の `gse_path` の
            その範囲（excerpt と同じ切り出し方）の SHA-256 が `gse_range_sha256` と一致することを
            --against-gse が確かめる（GSE 側の判断が変わっていないかの照合。コピー自体は逐語ではなくてよい）。
SHA-256 は CRLF を LF に揃えてから取る。path は logger ディレクトリからの相対・gse_path は repo のルートからの相対
（先頭の `/` `\\`・NUL・base の外を指すパスは拒否する）。
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
FIELDS = (
    "kind", "id", "path", "gse_path", "gse_last_commit", "start_anchor", "end_anchor", "symbol",
    "sha256", "gse_range_sha256", "check_decls", "reason",
)
DECL = re.compile(r"^\s*pub\s+(const|static)\s+(\w+)\s*:\s*([^=]+?)\s*=\s*(.+?)\s*;")


class Bad(Exception):
    pass


class Unsafe(Bad):
    """パスの安全性違反（NUL・絶対パス・base の外・シンボリックリンク等）。

    ⚠️ 通常の Bad（SHA-256 不一致等の「内容の不一致」）とは区別する: `each_entry` はこれを
    エントリ単位のエラー文字列に丸めず、呼び出し元まで伝播させて exit 2（使い方の誤り）にする
    （issue 011 merge ゲートレビュー item 8）。
    """


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
        if not isinstance(m, dict) or not isinstance(m.get("entries"), list) or not m.get("entries"):
            raise Bad("entries が配列でない、または 0 件（空振りの緑を出さない）: " + os.path.basename(p))
        out.append((os.path.basename(p), m))
    return out


def safe_rel(p, what):
    """相対パスとしての形を確かめる（`os.path.isabs` は Windows で `/foo` を絶対パスと**認めない**
    抜け道があるので、先頭の `/` `\\` は別途拒否する。issue 011 merge ゲートレビュー item 8）。"""
    if not isinstance(p, str) or not p:
        raise Unsafe("%s が無い" % what)
    if "\x00" in p:
        raise Unsafe("%s に NUL を含む: %r" % (what, p))
    if p.startswith("/") or p.startswith("\\"):
        raise Unsafe("%s が / または \\ で始まる: %r" % (what, p))
    if os.path.isabs(p) or ":" in p or ".." in p.replace("\\", "/").split("/"):
        raise Unsafe("%s が相対パスでない: %r" % (what, p))
    return p


def safe_join(base, rel, what):
    """`base` の中に必ず収まる絶対パスを返す（realpath を取って commonpath で確かめる。
    シンボリックリンクで base の外へ抜けるのも拒否する。issue 011 merge ゲートレビュー item 8）。"""
    rel = safe_rel(rel, what)
    base_real = os.path.realpath(base)
    p = os.path.realpath(os.path.join(base, rel))
    try:
        common = os.path.commonpath([base_real, p])
    except ValueError:  # Windows で別ドライブだと commonpath が ValueError を投げる
        raise Unsafe("%s が base の外を指す（別ドライブ）: %r" % (what, rel))
    if common != base_real:
        raise Unsafe("%s が base の外を指す: %r" % (what, rel))
    return p


def read_copy_lines(ldir, ent):
    return to_lines(read_bytes(safe_join(ldir, ent.get("path"), "path")))


def read_gse_lines(repo, ent):
    return to_lines(read_bytes(safe_join(repo, ent.get("gse_path"), "gse_path")))


def copy_bytes(ldir, ent):
    """コピー側の照合対象のバイト列。"""
    if ent.get("kind") not in KINDS:
        raise Bad("kind が不正: %r" % ent.get("kind"))
    lines = read_copy_lines(ldir, ent)
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
            except Unsafe:
                raise  # ★ パスの安全性違反は個別の不一致に丸めず、呼び出し元まで伝播させる
            except (Bad, UnicodeDecodeError) as e:
                errs.append("%s: %s: %s" % (name, ent.get("id"), e))
    return errs


def check_self(ldir):
    def one(ent):
        if sha(copy_bytes(ldir, ent)) != ent.get("sha256"):
            raise Bad("SHA-256 が一致しない（%s）" % ent.get("path"))
    return each_entry(ldir, one)


def check_new_entry(repo, ldir, ent):
    """`kind: "new"` の照合。2 つの独立した照合を、明示の欄があるときだけ行う
    （判断 33・issue 011 merge ゲートレビュー item 5 / 6。`gse_path` があるだけでは何もしない）。"""
    did_check = False
    if ent.get("check_decls"):
        if not ent.get("gse_path"):
            raise Bad("check_decls: true だが gse_path が無い")
        mine = decls(read_copy_lines(ldir, ent))
        theirs = decls(read_gse_lines(repo, ent))
        for name, d in sorted(mine.items()):
            if theirs.get(name) != d:
                raise Bad("シムの %s が GSE と違う（型か値・GSE 側に無い場合も含む）" % name)
        did_check = True
    if ent.get("start_anchor") or ent.get("end_anchor"):
        if not ent.get("gse_path"):
            raise Bad("start_anchor/end_anchor があるが gse_path が無い")
        want = ent.get("gse_range_sha256")
        if not want:
            raise Bad("new にアンカーがあるのに gse_range_sha256 が無い")
        body = gse_range(read_gse_lines(repo, ent), ent)
        if sha(join(body)) != want:
            raise Bad("GSE の判断の範囲が変わった（gse_range_sha256 が一致しない・%s）" % ent.get("gse_path"))
        sym = ent.get("symbol")
        if sym and not re.search(r"\b(?:fn|enum|struct)\s+" + re.escape(sym) + r"\b", "\n".join(body)):
            raise Bad("symbol %s が範囲の中に無い" % sym)
        did_check = True
    if not did_check:
        return  # check_decls も anchor も無ければ --against-gse では何も照合しない（--self だけの対象）


def check_gse_entry(repo, ldir, ent):
    kind = ent.get("kind")
    if kind == "new":
        check_new_entry(repo, ldir, ent)
        return
    lines = read_gse_lines(repo, ent)
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
    if os.path.islink(manifest):
        raise Unsafe("--manifest がシンボリックリンク: " + manifest)
    try:
        spec = json.loads(read_bytes(spec_path).decode("utf-8"))
    except ValueError:
        raise Bad("--entries を JSON として読めない: " + spec_path)
    if not isinstance(spec, list):
        raise Bad("--entries は配列であること: " + spec_path)

    # ★ 既存の manifest を id 単位でマージする（同じ id は置き換え、他は残す。
    #   issue 011 merge ゲートレビュー item 5b）。他の manifest*.json はここでは一切開かない。
    existing = []
    if os.path.exists(manifest):
        try:
            prev = json.loads(read_bytes(manifest).decode("utf-8"))
        except ValueError:
            raise Bad("既存の manifest を JSON として読めない: " + manifest)
        if isinstance(prev, dict) and isinstance(prev.get("entries"), list):
            existing = prev["entries"]
    order = [e.get("id") for e in existing if isinstance(e, dict)]
    by_id = {e.get("id"): e for e in existing if isinstance(e, dict)}

    for s in spec:
        if not isinstance(s, dict) or not s.get("id"):
            raise Bad("--entries の要素に id が無い: %r" % (s,))
        ent = {k: s.get(k) for k in FIELDS}
        ent["sha256"] = sha(copy_bytes(ldir, ent))
        if ent.get("kind") == "new" and ent.get("gse_path") and ent.get("start_anchor") and ent.get("end_anchor"):
            ent["gse_range_sha256"] = sha(join(gse_range(read_gse_lines(repo, ent), ent)))
        else:
            ent["gse_range_sha256"] = None
        ent["gse_last_commit"] = (git(repo, "log", "-1", "--format=%H", "--", ent["gse_path"]) or None) if ent["gse_path"] else None
        if ent["gse_path"] and not ent["gse_last_commit"]:
            print("WARN: gse_last_commit を取れない（未コミット？）: " + ent["gse_path"], file=sys.stderr)
        check_gse_entry(repo, ldir, ent)  # ★ コピーが GSE と逐語（または判断の範囲が一致）でなければ書かない
        if ent["id"] not in by_id:
            order.append(ent["id"])
        by_id[ent["id"]] = ent

    entries = [by_id[i] for i in order]
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
    {"kind": "new", "id": "shim", "path": "src/shim.rs", "gse_path": "src-tauri/src/a.rs", "check_decls": True, "reason": "シム"},
]
SPEC_B = [{"kind": "new", "id": "other", "path": "src/other.rs", "reason": "別の manifest の持ち物"}]
# ★ 判断 33: new でも GSE 側のずれを検出できるエントリ（アンカー + gse_range_sha256）。
SPEC_JUDGMENT = [
    {
        "kind": "new", "id": "judgment", "path": "src/judgment.rs", "gse_path": "src-tauri/src/a.rs",
        "start_anchor": "/// START", "end_anchor": "/// END", "symbol": "beta",
        "reason": "GSE の beta と同じ判断の写し（コードは別）",
    }
]


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
    put(ldir, "src/judgment.rs", "// GSE の beta と同じ判断の写し（コードは別）。\n")
    spec = put(tmp, "spec.json", json.dumps(SPEC, ensure_ascii=False))
    spec_b = put(tmp, "spec_b.json", json.dumps(SPEC_B, ensure_ascii=False))
    spec_judgment = put(tmp, "spec_judgment.json", json.dumps(SPEC_JUDGMENT, ensure_ascii=False))
    mf, mf_b = os.path.join(ldir, "manifest.json"), os.path.join(ldir, "manifest.other.json")

    expect("manifest が 0 本なら使い方の誤り（exit 2）", ["--self"], 2, "manifest")
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
    mutated(gse, "pub const K: u32 = 0x19;", "pub const K: u32 = 0x1A;", "陰性 7: check_decls の値が GSE と違うと赤", ["--against-gse"], "シム")
    mutated(mf, '"symbol": "beta"', '"symbol": "gamma"', "陰性 5: symbol が範囲に無いと赤", ["--against-gse"], "symbol")

    # ★ item 5a: check_decls が無ければシムの値照合をしない（gse_path があるだけでは照合しない）。
    #   ⚠️ 既存の manifest（"shim" は check_decls: true 付きで登録済み）と混ざると、同じ GSE の
    #   ミューテーションでそちら側が正しく赤くなってしまい判定できないので、独立した
    #   logger-dir / repo で確かめる。
    nd = os.path.join(tmp, "nodecls")
    nd_ldir, nd_repo = os.path.join(nd, "logger"), os.path.join(nd, "repo")
    nd_gse = put(nd_repo, "src-tauri/src/a.rs", GSE_A)
    put(nd_ldir, "src/shim.rs", "pub const K: u32 = 0x19;\n")
    nd_spec = put(nd, "spec.json", json.dumps(
        [{"kind": "new", "id": "shim2", "path": "src/shim.rs", "gse_path": "src-tauri/src/a.rs", "reason": "シム（check_decls 無し）"}],
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
            fails.append("%s: exit %d（期待 %d）%s" % (name, r.returncode, rc_want, out.strip()[-160:]))

    nd_expect("item 5a 準備: check_decls 無しの new を登録", ["--update", "--manifest", os.path.join(nd_ldir, "manifest.json"), "--entries", nd_spec], 0)
    with open(nd_gse, "rb") as f:
        nd_orig = f.read()
    try:
        with open(nd_gse, "wb") as f:
            f.write(nd_orig.replace(b"pub const K: u32 = 0x19;", b"pub const K: u32 = 0x1A;", 1))
        nd_expect("item 5a 陰性対照: check_decls 無しなら値がずれても against-gse は緑のまま", ["--against-gse"], 0)
    finally:
        with open(nd_gse, "wb") as f:
            f.write(nd_orig)

    before = read_bytes(mf_b)
    expect("陰性 6: --update --manifest A が B を書き換えない（実行）", ["--update", "--manifest", mf, "--entries", spec], 0)
    if read_bytes(mf_b) != before:
        fails.append("陰性 6: --update --manifest A が manifest.other.json を書き換えた")
    expect("陰性 6b: --manifest が別のディレクトリなら拒否", ["--update", "--manifest", os.path.join(tmp, "manifest.json"), "--entries", spec], 2)
    expect("更新後も陽性", ["--self"], 0)

    # ★ item 5b: --update は id 単位でマージする（同じ manifest に judgment を後から足しても
    #   既存の a / ex1 / shim は残る）。
    expect("item 5b: judgment を後から追加", ["--update", "--manifest", mf, "--entries", spec_judgment], 0)
    try:
        ids = sorted(e.get("id") for e in json.loads(read_bytes(mf).decode("utf-8"))["entries"])
    except (ValueError, KeyError):
        ids = None
    if ids != ["a", "ex1", "judgment", "shim"]:
        fails.append("item 5b: マージ後の id 集合が期待と違う: %r" % (ids,))
    expect("item 5b 後も陽性 --self", ["--self"], 0)
    expect("item 5b 後も陽性 --against-gse", ["--against-gse"], 0)

    # ★ item 6: new (アンカー付き) の GSE 側範囲が変わると against-gse が赤になる
    #   （コピー自体は逐語でなくてよい・GSE の「判断」が変わったことを検出する）。
    mutated(gse, "2\n}\n", "9\n}\n", "陰性 8: new (アンカー付き) の GSE 側範囲が変わると against-gse が赤",
            ["--against-gse"], "judgment")

    # ★ item 6: アンカーがあるのに gse_range_sha256 が無いと赤。
    m = re.search(r'"id": "judgment".*?"gse_range_sha256": "([0-9a-f]{64})"', read_bytes(mf).decode("utf-8"), re.S)
    if m is None:
        fails.append("item 6: manifest に judgment の gse_range_sha256 が無い")
    else:
        mutated(mf, '"gse_range_sha256": "%s"' % m.group(1), '"gse_range_sha256": null',
                "陰性 9: new にアンカーがあるのに gse_range_sha256 が無いと赤", ["--against-gse"], "gse_range_sha256")

    # --- item 8: パスの安全性・壊れた入力（Traceback ではなく exit 2） ---------------------
    sec = os.path.join(tmp, "sec")
    sec_ldir, sec_repo = os.path.join(sec, "logger"), os.path.join(sec, "repo")
    os.makedirs(sec_repo, exist_ok=True)

    def sec_run(*args):
        return subprocess.run(
            [sys.executable, script, "--logger-dir", sec_ldir, "--repo", sec_repo] + list(args),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=dict(os.environ, PYTHONUTF8="1"), timeout=60,
        )

    def sec_expect(name, args, rc_want, needle=None):
        r = sec_run(*args)
        out = r.stdout + r.stderr
        if r.returncode != rc_want or "Traceback" in out or (needle and needle not in out):
            fails.append("%s: exit %d（期待 %d）%s" % (name, r.returncode, rc_want, out.strip()[-160:]))

    put(sec_ldir, "manifest.json", json.dumps({"gse_repo_commit": "x", "entries": "abc"}, ensure_ascii=False))
    sec_expect("陰性 10: entries が配列でないと exit 2（Traceback ではない）", ["--self"], 2)

    put(sec_ldir, "manifest.json", json.dumps(
        {"gse_repo_commit": "x", "entries": [{"kind": "file", "id": "n", "path": "a\x00b", "gse_path": "x", "sha256": "0" * 64}]},
        ensure_ascii=False,
    ))
    sec_expect("陰性 11: path に NUL があると exit 2（Traceback ではない）", ["--self"], 2)

    put(sec_ldir, "manifest.json", json.dumps(
        {"gse_repo_commit": "x", "entries": [{"kind": "file", "id": "n", "path": "/etc/passwd", "gse_path": "x", "sha256": "0" * 64}]},
        ensure_ascii=False,
    ))
    sec_expect("陰性 12: path が / で始まると exit 2", ["--self"], 2)

    sec_spec_not_json = put(sec, "spec_not_json.txt", "not json {{{")
    put(sec_ldir, "manifest.json", json.dumps({"gse_repo_commit": "x", "entries": [{"kind": "new", "id": "z", "path": "z.rs", "reason": "z"}]}, ensure_ascii=False))
    put(sec_ldir, "z.rs", "// z\n")
    sec_expect(
        "陰性 13: --entries が JSON でないと exit 2（Traceback ではない）",
        ["--update", "--manifest", os.path.join(sec_ldir, "manifest.json"), "--entries", sec_spec_not_json],
        2,
    )

    try:
        link_target = put(sec, "manifest_target.json", json.dumps({"gse_repo_commit": "x", "entries": [{"kind": "new", "id": "z", "path": "z.rs", "reason": "z"}]}))
        link_path = os.path.join(sec_ldir, "manifest.link.json")
        if os.path.exists(link_path) or os.path.islink(link_path):
            os.remove(link_path)
        os.symlink(link_target, link_path)
        sec_spec_empty = put(sec, "spec_empty.json", "[]")
        sec_expect("陰性 14: --update はシンボリックリンクの manifest を拒否する", ["--update", "--manifest", link_path, "--entries", sec_spec_empty], 2)
    except OSError:
        pass  # ⚠️ シンボリックリンク作成に権限が要る環境がある（Windows）。作れなければこの陰性対照は飛ばす。

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
    except (Bad, ValueError) as e:
        # ⚠️ ここに来るのは常に構造的な誤り（JSON が壊れている・manifest が 0 本・
        #   パスの安全性違反等）であり、個別の不一致（`errs`）とは別枠。exit 2
        #   （issue 011 merge ゲートレビュー item 8: Traceback ではなく制御された終了）。
        print("NG:", e)
        return 2
    for e in errs:
        print("NG:", e)
    print("%s: %s" % ("--self" if a.self else "--against-gse", "不一致 %d 件" % len(errs) if errs else "一致"))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
