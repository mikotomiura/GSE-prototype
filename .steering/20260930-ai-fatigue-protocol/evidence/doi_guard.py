"""DOI を URL のパスに入れる前の検査（★ 2026-10-01 の security-checker L-2・decisions.md 判断 17）。

`quote(doi, safe="/")` は `/` を残すので、`10.x/../../members` のような `..` の区切りが残る。
前タスクの `common.allowed_url` はパスを正規化せずに前方一致で比べるので、同じホストの別のパスへの要求が通りうる。
→ DOI の形（`10.<4〜9 桁>/<空白の無い文字列>`）を確かめ、`.`・`..` の区切りを拒んでから quote する。
"""
import re
import urllib.parse

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")


def doi_path(doi, safe="/"):
    """パスに入れてよい形の DOI を quote して返す。形が違えば ValueError。"""
    d = (doi or "").strip()
    if not DOI_RE.match(d):
        raise ValueError(f"DOI の形でない: {d!r}")
    if any(seg in (".", "..") for seg in d.split("/")):
        raise ValueError(f"DOI に . か .. の区切りがある: {d!r}")
    return urllib.parse.quote(d, safe=safe)
