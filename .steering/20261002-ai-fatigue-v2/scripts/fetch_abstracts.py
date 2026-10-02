"""抄録を無料の学術 API から取る（design §4）。

- 対象: 追加候補の未判定 213 件（判定者用ファイルの DOI）と探索の読む一覧 46 件（`search-records.json` の key が DOI のもの）。
- 順: Semantic Scholar（batch）→ Europe PMC → OpenAlex → Crossref。最初に取れたもの（`MIN_CHARS` 字以上）を使う。
- ★ メールアドレス・キーを送らない（`mailto` を付けない・User-Agent にメールを入れない）。
- ★ 抄録の本文は git の外（`common.ABSTRACTS`）。repo には状態（出どころ・文字数・SHA-256）だけ（`common.ABSTRACT_STATUS`）。
- 既に取れた記録は取り直さない（`--force` で全部取り直す）。

使い方: uv run --with openpyxl python fetch_abstracts.py [--force] [--only ID,ID]
"""
import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import openpyxl

import common

UA = "ai-fatigue-review-abstracts/1.0 (scoping review; no contact)"  # ★ メールアドレスを入れない
MIN_CHARS = 100
TIMEOUT = 30


def _get(url, data=None, tries=4):
    for k in range(tries):
        req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, "Accept": "application/json",
                                                               **({"Content-Type": "application/json"} if data else {})})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503, 504) and k < tries - 1:
                time.sleep(3 * (k + 1) ** 2)
                continue
            return {"_error": f"HTTP {e.code}"}
        except Exception as e:  # 接続の失敗・途中で切れた読み込み（IncompleteRead）など
            if k < tries - 1:
                time.sleep(3 * (k + 1))
                continue
            return {"_error": type(e).__name__}
    return None


def _clean(t):
    if not t:
        return ""
    t = re.sub(r"<[^>]+>", " ", t)          # JATS・HTML のタグ
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"^(Abstract|ABSTRACT)[:.\s]+", "", t)
    return t


def from_s2_batch(dois):
    out = {}
    for i in range(0, len(dois), 100):
        chunk = dois[i:i + 100]
        url = "https://api.semanticscholar.org/graph/v1/paper/batch?fields=abstract,externalIds"
        res = _get(url, data=json.dumps({"ids": [f"DOI:{d}" for d in chunk]}).encode("utf-8"), tries=6)
        if isinstance(res, list):
            for d, p in zip(chunk, res):
                if p and p.get("abstract"):
                    out[d.lower()] = _clean(p["abstract"])
        time.sleep(3)
    return out


def from_epmc(doi):
    q = urllib.parse.quote(f'DOI:"{doi}"')
    res = _get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&resultType=core&format=json&pageSize=1")
    try:
        r = res["resultList"]["result"][0]
        if (r.get("doi") or "").lower() == doi.lower():
            return _clean(r.get("abstractText"))
    except Exception:
        pass
    return ""


def from_openalex(doi):
    res = _get("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="/") + "?select=abstract_inverted_index")
    inv = (res or {}).get("abstract_inverted_index") if isinstance(res, dict) else None
    if not inv:
        return ""
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return _clean(" ".join(w for _, w in pos))


def from_crossref(doi):
    res = _get("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"))
    try:
        return _clean(res["message"].get("abstract"))
    except Exception:
        return ""


def targets():
    """(ID, DOI か None) の一覧。追加候補の未判定 213 件 → 探索の読む一覧 46 件の順。"""
    wb = openpyxl.load_workbook(common.JUDGE_FILE, read_only=True, data_only=True)
    rows = list(wb[common.JUDGE_SHEET].iter_rows(values_only=True))
    data = [r for r in rows[common.JUDGE_HEADER_ROW:] if r and r[0]]
    judged = {json.loads(l)["item"] for l in open(common.PREV_LOG, encoding="utf-8")}
    out = [(r[0], (str(r[6]).strip() if r[6] else None)) for r in data if r[0] not in judged]
    recs = json.load(open(common.SEARCH_RECORDS, encoding="utf-8"))
    rl = sorted((r for r in recs if r["reading"] and re.fullmatch(r"R\d\d", r["reading"])), key=lambda r: r["reading"])
    out += [(r["reading"], (r["key"] if r["key"].startswith("10.") else None)) for r in rl]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    for p, s in ((common.JUDGE_FILE, common.JUDGE_FILE_SHA256),):
        if common.sha256(p) != s:
            sys.exit(f"元の資料の SHA-256 が違う: {p}")
    tg = targets()
    if a.only:
        keep = set(a.only.split(","))
        tg = [t for t in tg if t[0] in keep]
    os.makedirs(os.path.dirname(common.ABSTRACTS), exist_ok=True)
    store = json.load(open(common.ABSTRACTS, encoding="utf-8")) if os.path.exists(common.ABSTRACTS) else {}
    todo = [(i, d) for i, d in tg if d and (a.force or not (store.get(i) or {}).get("text"))]
    print(f"対象 {len(tg)} 件・DOI で取る {len(todo)} 件・DOI なし {sum(1 for _, d in tg if not d)} 件", flush=True)

    s2 = from_s2_batch([d for _, d in todo])
    print(f"Semantic Scholar: {len(s2)} 件", flush=True)
    for n, (i, d) in enumerate(todo, 1):
        text, src = s2.get(d.lower(), ""), "Semantic Scholar"
        for name, fn in (("Europe PMC", from_epmc), ("OpenAlex", from_openalex), ("Crossref", from_crossref)):
            if len(text) >= MIN_CHARS:
                break
            text, src = fn(d), name
            time.sleep(0.4)
        store[i] = {"doi": d, "source": src if len(text) >= MIN_CHARS else None, "text": text if len(text) >= MIN_CHARS else ""}
        if n % 20 == 0:
            print(f"  {n}/{len(todo)}", flush=True)
            json.dump(store, open(common.ABSTRACTS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for i, d in tg:
        if not d and i not in store:
            store[i] = {"doi": None, "source": None, "text": ""}
    json.dump(store, open(common.ABSTRACTS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    status = {}
    for i, _ in targets():
        s = store.get(i) or {}
        t = s.get("text") or ""
        status[i] = {"doi": s.get("doi"), "source": s.get("source"), "chars": len(t),
                     "sha256": hashlib.sha256(t.encode("utf-8")).hexdigest() if t else None}
    with open(common.ABSTRACT_STATUS, "w", encoding="utf-8", newline="\n") as f:
        json.dump(status, f, ensure_ascii=False, indent=1)
        f.write("\n")
    got = sum(1 for v in status.values() if v["chars"])
    by = {}
    for v in status.values():
        by[v["source"]] = by.get(v["source"], 0) + 1
    print(f"取れた {got} / {len(status)}・出どころ {by}")
    print("取れなかった:", ", ".join(i for i, v in status.items() if not v["chars"]))


if __name__ == "__main__":
    main()
