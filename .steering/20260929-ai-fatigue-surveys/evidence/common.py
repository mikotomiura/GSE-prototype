"""サーヴェイの検索スクリプトを流用するときの共通の関数（decisions.md 判断 16）。

2026-09-29 に実行した版（`S-*/*.py`）は記録として残し、再実行しない。流用するときは、下の関数を使って書き直す。
テストは `test_common.py`（`python -m unittest test_common` を、このディレクトリで実行）。
"""
import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request
import uuid


def merge_abstract(store, key, text):
    """情報源をまたいで抄録を集める。★ 空の抄録で、取れている抄録を上書きしない。長い方を残す。

    2026-09-29 の S-05 では `dict.update` で後の情報源の空の抄録が前の抄録を消し、6 件が抄録なしで抽出に渡った。
    """
    text = text or ""
    old = store.get(key) or ""
    if len(text.strip()) > len(old.strip()):
        store[key] = text
    elif key not in store:
        store[key] = old
    return store


def repo_root(start=None):
    """git の作業ツリーの根（worktree を含む）。git が無ければ `.git` を上へ探す。"""
    start = os.path.abspath(start or os.path.dirname(__file__))
    try:
        out = subprocess.run(["git", "-C", start, "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                             check=True).stdout.strip()
        if out:
            return os.path.realpath(out)
    except (OSError, subprocess.CalledProcessError):
        pass
    d = start
    while True:
        if os.path.exists(os.path.join(d, ".git")):
            return os.path.realpath(d)
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def is_inside(path, root):
    """path が root の中か（リンクを解決し、大文字小文字の違いを無視して比べる）。"""
    p = os.path.normcase(os.path.realpath(path))
    r = os.path.normcase(os.path.realpath(root))
    try:
        return os.path.commonpath([p, r]) == r
    except ValueError:  # 別のドライブ
        return False


def ensure_outside_repo(path, root=None):
    """抄録・本文の置き場が repo の外であることを確かめる。中なら例外。"""
    root = root or repo_root()
    if root is None:
        raise RuntimeError("repo の根が分からないので、置き場を確かめられない")
    if is_inside(path, root):
        raise RuntimeError(f"抄録の置き場が repo の中にある（repo の外を指定する）: {path}")
    return path


def open_exclusive(path):
    """既にあるファイルを上書きしない（書誌の JSON・抄録のファイルとも）。"""
    return open(path, "x", encoding="utf-8")


def write_pair(bib_path, abs_path, bib_obj, abs_obj):
    """書誌（repo の中）と抄録（repo の外）を、同じ実行の対として書く。

    ★ 両方を排他的に開けてから書く（片方が既にあれば、どちらも書かない）。両方の `run_id` に同じ値を入れるので、
    後から対応を `same_run` で確かめられる（`open_exclusive` だけでは、別の実行の抄録と組み合わさるのを防げない）。
    """
    rid = uuid.uuid4().hex
    bib_obj = {**bib_obj, "run_id": rid}
    abs_obj = {"run_id": rid, "abstracts": abs_obj}
    fb = open_exclusive(bib_path)
    try:
        fa = open_exclusive(abs_path)
    except BaseException:
        fb.close()
        os.remove(bib_path)
        raise
    with fb, fa:
        json.dump(abs_obj, fa, ensure_ascii=False, indent=1)
        json.dump(bib_obj, fb, ensure_ascii=False, indent=1)
    return rid


def same_run(bib_obj, abs_obj):
    """書誌と抄録が同じ実行の対か（`write_pair` の `run_id` で比べる）。"""
    rid = bib_obj.get("run_id")
    return bool(rid) and rid == abs_obj.get("run_id")


def _parts(url):
    u = urllib.parse.urlsplit(url or "")
    try:
        port = u.port
    except ValueError:
        return None
    if u.username is not None or u.password is not None or not u.hostname:
        return None
    return u.scheme.lower(), u.hostname.lower(), port or (443 if u.scheme.lower() == "https" else None), u.path or "/"


def allowed_url(url, prefixes):
    """https で、許した接頭辞の URL の下だけを開く。

    ★ 文字列の前方一致ではなく、スキーム・ホスト・ポートを分けて完全一致で比べ、パスは区切りの単位で前方一致を見る
    （`https://host.evil/`・`https://host@evil/` を通さない）。利用者情報（`user@`）の付いた URL は通さない。
    ⚠️ 開いた後のリダイレクトは、この関数では見ない。開くときは `guarded_opener` を使う。
    """
    got = _parts(url)
    if got is None or got[0] != "https":
        return False
    for p in prefixes:
        want = _parts(p)
        if want is None or want[:3] != got[:3]:
            continue
        base = want[3]
        if base.endswith("/") and got[3].startswith(base):
            return True
        if got[3] == base or got[3].startswith(base + "/"):
            return True
    return False


def guarded_opener(prefixes):
    """リダイレクトの先も `allowed_url` で確かめる opener（許していない先へは要求を送らずに例外）。"""

    class _Guard(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            if not allowed_url(newurl, prefixes):
                raise urllib.error.URLError(f"許していない先へのリダイレクト: {newurl}")
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    return urllib.request.build_opener(_Guard)


def slice_between(page, start_marker, end_markers):
    """start_marker から、最初に現れる end_markers のどれかの手前までを返す。★ 終わりの目印が無ければ空を返す
    （固定の文字数で切ると、前後の本文が混ざるか、長い抄録が途中で切れる）。"""
    i = page.find(start_marker)
    if i < 0:
        return ""
    ends = [j for j in (page.find(m, i + len(start_marker)) for m in end_markers) if j > 0]
    if not ends:
        return ""
    return page[i:min(ends)]
