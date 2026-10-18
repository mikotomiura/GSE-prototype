"""抄録と CSL を取りに行く（build.py --fetch のときだけ呼ばれる・判断 7）。

キャッシュにあるものは取り直さない。連絡先のメールアドレスは送らない（User-Agent だけ）。
抄録は著作物なので repo に入れず、キャッシュ（~/.cache/gse-refdb/）だけに置く。
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = {"User-Agent": "gse-refdb/0.1"}


def doi_of(key: str) -> str | None:
    t, _, v = key.partition(":")
    if t == "doi":
        return v
    if t == "arXiv":
        return "10.48550/arXiv." + v
    return None


def _get(url: str, headers: dict | None = None, timeout: int = 20):
    req = urllib.request.Request(url, headers=headers or UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def _permanent(e: Exception) -> bool:
    """404・410 は「無い」と覚えてよい。タイムアウトや 429・5xx は一過性なのでキャッシュに残さない（次の --fetch で取り直す）。"""
    return isinstance(e, urllib.error.HTTPError) and e.code in (404, 410)


def _retry(rec: dict) -> bool:
    """前の回にキャッシュした抄録の無い記録のうち、失敗が一過性だけのもの（429・名前解決の失敗など）は取り直す。
    2026-10-18 の回は一過性の失敗も保存していた（429 が 26 件・名前解決が 7 件）。"""
    errs = [v for k, v in rec.items() if k.startswith("err")]
    return not rec.get("abs") and any("404" not in e and "410" not in e for e in errs)


def _retry_csl(rec: dict) -> bool:
    """CSL の記録のうち、取れなかった理由が一過性（404・410 以外）のものは取り直す。"""
    e = rec.get("_err")
    return e is not None and "404" not in e and "410" not in e


def _inverted(ii: dict) -> str:
    pos = [(p, w) for w, ps in ii.items() for p in ps]
    return " ".join(w for _, w in sorted(pos))


def _save(out: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


def fetch_abstracts(keys: list[str], path: Path) -> int:
    """OpenAlex → Semantic Scholar → Crossref の順。DOI と arXiv のものだけ。"""
    out = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    todo = [k for k in keys if (k not in out or _retry(out[k])) and doi_of(k)]
    transient = 0
    for n, k in enumerate(todo, 1):
        doi = urllib.parse.quote(doi_of(k), safe="/")
        rec: dict = {"src": None, "abs": ""}
        flaky = False
        try:
            j = _get("https://api.openalex.org/works/doi:" + doi)
            if j.get("abstract_inverted_index"):
                rec = {"src": "openalex", "abs": _inverted(j["abstract_inverted_index"])}
            rec["type"], rec["title"] = j.get("type"), j.get("title")
        except Exception as e:  # noqa: BLE001  取れなければ次の取り先へ
            rec["err_oa"] = str(e)[:80]
            flaky |= not _permanent(e)
        if not rec["abs"]:
            try:
                j = _get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=abstract")
                if j.get("abstract"):
                    rec.update(src="s2", abs=j["abstract"])
            except Exception as e:  # noqa: BLE001
                rec["err_s2"] = str(e)[:80]
                flaky |= not _permanent(e)
            time.sleep(1.1)
        if not rec["abs"]:
            try:
                j = _get("https://api.crossref.org/works/" + doi)["message"]
                if j.get("abstract"):
                    rec.update(src="crossref", abs=j["abstract"])
            except Exception as e:  # noqa: BLE001
                rec["err_cr"] = str(e)[:80]
                flaky |= not _permanent(e)
        if rec["abs"] or not flaky:
            out[k] = rec
        else:
            transient += 1
        if n % 25 == 0:
            _save(out, path)
        time.sleep(0.15)
    _save(out, path)
    print(f"抄録: {len(todo)} 件を問い合わせた（キャッシュ {len(out)} 件・一過性の失敗で残さなかった {transient} 件）")
    return len(todo)


def fetch_csl(keys: list[str], path: Path) -> int:
    """https://doi.org/<doi> に CSL-JSON を求める。"""
    out = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    # 前の回に一過性の失敗（429・タイムアウト）を _err として残したものは取り直す（404・410 は「無い」のまま）
    todo = [k for k in keys if (k not in out or _retry_csl(out[k])) and doi_of(k)]
    hdr = {**UA, "Accept": "application/vnd.citationstyles.csl+json"}
    transient = 0
    for n, k in enumerate(todo, 1):
        try:
            out[k] = _get("https://doi.org/" + urllib.parse.quote(doi_of(k), safe="/"), hdr, 25)
        except Exception as e:  # noqa: BLE001
            if _permanent(e):
                out[k] = {"_err": str(e)[:80]}
            else:
                transient += 1
        if n % 50 == 0:
            _save(out, path)
        time.sleep(0.2)
    _save(out, path)
    failed = sum("_err" in out[k] for k in todo if k in out)
    print(f"CSL: {len(todo)} 件を問い合わせた（無い {failed}・一過性の失敗で残さなかった {transient}）")
    return len(todo)
