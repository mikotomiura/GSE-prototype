"""サーヴェイの検索スクリプトを流用するときの共通の関数（decisions.md 判断 16）。

2026-09-29 に実行した版（`S-*/*.py`）は記録として残し、再実行しない。流用するときは、下の関数を使って書き直す。
テストは `test_common.py`（`python -m unittest test_common` を、このディレクトリで実行）。
"""
import os
import subprocess
import urllib.parse


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


def allowed_url(url, prefixes):
    """https で、許した接頭辞で始まる URL だけを開く。"""
    u = urllib.parse.urlparse(url or "")
    return u.scheme == "https" and any((url or "").startswith(p) for p in prefixes)


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
