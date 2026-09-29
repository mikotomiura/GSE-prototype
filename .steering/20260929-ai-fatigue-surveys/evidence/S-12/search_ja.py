"""S-12: 日本語の情報源（J-STAGE・CiNii Research・KAKEN・国立国会図書館サーチ）を検索する。

手順は design.md §1（検索の実行前に固定）。書誌だけを JSON に書く（抄録は保存しない）。
使い方: python search_ja.py <出力 JSON>   （★ 既存のファイルは上書きしない）
"""
import itertools
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

UA = {"User-Agent": "Mozilla/5.0 (literature-search script)"}
A_JA = ["AI", "人工知能", "ChatGPT", "大規模言語モデル", "LLM", "チャットボット"]
F_JA = ["疲労", "疲れ", "疲弊", "燃え尽き", "バーンアウト", "消耗", "テクノストレス"]
A_NARROW = ["生成AI", "ChatGPT", "大規模言語モデル", "LLM"]
B_JA = ["負担", "負荷"]
A_EN = ["generative AI", "ChatGPT", "large language model", "artificial intelligence", "chatbot"]
F_EN = ["fatigue", "burnout", "exhaustion", "technostress"]

AI_RE = re.compile(
    r"生成\s*AI|人工知能|ChatGPT|チャット\s*GPT|大規模言語モデル|LLM|チャットボット|対話型\s*AI|Copilot"
    r"|(?<![A-Za-z0-9])AI(?![A-Za-z])")
AI_EN_RE = re.compile(r"artificial intelligence|generative|large language model|chatbot", re.I)
FT_RE = re.compile(r"疲労|疲れ|疲弊|燃え尽き|バーンアウト|消耗|テクノストレス"
                   r"|fatigue|burn-?out|exhaust|technostress|weariness|tired", re.I)


def title_pass(t):
    t = t or ""
    return bool((AI_RE.search(t) or AI_EN_RE.search(t)) and FT_RE.search(t))


def get(url, tries=4):
    for k in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read()
        except Exception as e:  # noqa: BLE001 - 記録して再試行
            err = e
            time.sleep(5 * (k + 1))
    raise err


NS = {"a": "http://www.w3.org/2005/Atom", "o": "http://a9.com/-/spec/opensearch/1.1/",
      "prism": "http://prismstandard.org/namespaces/basic/2.0/"}


def txt(e, path):
    x = e.find(path, NS)
    return (x.text or "").strip() if x is not None and x.text else ""


def jstage(field, terms):
    q = " ".join(terms)
    url = "https://api.jstage.jst.go.jp/searchapi/do?" + urllib.parse.urlencode(
        {"service": 3, field: q, "count": 1000})
    root = ET.fromstring(get(url))
    status = txt(root, "a:result/a:status")
    tot = txt(root, "o:totalResults") or "0"
    recs = []
    for e in root.findall("a:entry", NS):
        recs.append({
            "title_ja": txt(e, "a:article_title/a:ja"), "title_en": txt(e, "a:article_title/a:en"),
            "url": txt(e, "a:article_link/a:ja") or txt(e, "a:article_link/a:en"),
            "journal": txt(e, "a:material_title/a:ja") or txt(e, "a:material_title/a:en"),
            "year": txt(e, "a:pubyear"), "doi": txt(e, "prism:doi"),
            "authors": [a.text for a in e.findall("a:author/a:ja/a:name", NS) if a.text][:6]
            or [a.text for a in e.findall("a:author/a:en/a:name", NS) if a.text][:6],
        })
    return {"status": status, "total": int(tot), "records": recs}


def cinii(endpoint, title_q):
    recs, total, start = [], None, 1
    while True:
        url = f"https://cir.nii.ac.jp/opensearch/{endpoint}?" + urllib.parse.urlencode(
            {"title": title_q, "format": "json", "count": 200, "start": start},
            quote_via=urllib.parse.quote)
        d = json.loads(get(url))
        total = int(d.get("opensearch:totalResults") or 0)
        items = d.get("items", [])
        for it in items:
            recs.append({
                "title": it.get("title", ""), "url": it.get("@id", ""),
                "year": (it.get("prism:publicationDate") or "")[:4],
                "journal": it.get("prism:publicationName", ""),
                "type": it.get("dc:type", ""),
                "doi": next((i.get("@value") for i in (it.get("dc:identifier") or [])
                             if isinstance(i, dict) and i.get("@type") == "cir:DOI"), ""),
                "authors": [c if isinstance(c, str) else c.get("@value", "")
                            for c in (it.get("dc:creator") or [])][:6],
            })
        start += 200
        if not items or start > min(total, 1000):
            break
        time.sleep(1)
    return {"total": total, "records": recs}


def ndl(title_q):
    url = "https://ndlsearch.ndl.go.jp/api/opensearch?" + urllib.parse.urlencode(
        {"title": title_q, "cnt": 500}, quote_via=urllib.parse.quote)
    x = get(url).decode("utf-8")
    root = ET.fromstring(x)
    tot = root.find(".//{http://a9.com/-/spec/opensearchrss/1.0/}totalResults")
    if tot is None:
        tot = root.find(".//{http://a9.com/-/spec/opensearch/1.1/}totalResults")
    recs = []
    for it in root.iter("item"):
        g = lambda tag: (it.findtext(tag) or "").strip()  # noqa: E731
        recs.append({
            "title": g("title"), "url": g("link"),
            "year": (g("{http://purl.org/dc/terms/}issued") or g("pubDate"))[:4],
            "journal": g("{http://ndl.go.jp/dcndl/terms/}publicationName") or g("{http://purl.org/dc/elements/1.1/}publisher"),
            "type": g("category"),
            "authors": [(c.text or "") for c in it.findall("{http://purl.org/dc/elements/1.1/}creator")][:6],
        })
    return {"total": int(tot.text) if tot is not None and tot.text else None, "records": recs}


def orq(xs):
    return "(" + " OR ".join(xs) + ")"


def main(out):
    if os.path.exists(out):
        sys.exit(f"出力先が既にある（上書きしない）: {out}")
    runs = []
    # J-STAGE: 組ごと × 題名・抄録
    pairs = ([("A-ja×F-ja", a, f) for a, f in itertools.product(A_JA, F_JA)]
             + [("narrow×B-ja", a, b) for a, b in itertools.product(A_NARROW, B_JA)]
             + [("A-en×F-en", a, f) for a, f in itertools.product(A_EN, F_EN)])
    for block, a, f in pairs:
        for field in ("article", "abst"):
            try:
                r = jstage(field, [a, f])
            except Exception as e:  # noqa: BLE001
                r = {"status": f"ERR {e}", "total": None, "records": []}
            runs.append({"source": "J-STAGE", "field": field, "block": block, "query": f"{a} {f}", **r})
            print(f"J-STAGE {field:7} {a} {f}: total={r['total']} status={r['status']}", flush=True)
            time.sleep(1)
    # J-STAGE 全文（比較のため件数だけ）
    for a, f in [("生成AI", "疲労"), ("AI", "疲労")]:
        r = jstage("text", [a, f])
        runs.append({"source": "J-STAGE", "field": "text（件数のみ）", "block": "比較", "query": f"{a} {f}",
                     "status": r["status"], "total": r["total"], "records": []})
        time.sleep(1)
    # CiNii Research all / projects: 3 本
    a_en_quoted = ['"' + a + '"' if " " in a else a for a in A_EN]
    cq = [("A-ja×F-ja", f"{orq(A_JA)} {orq(F_JA)}"),
          ("narrow×B-ja", f"{orq(A_NARROW)} {orq(B_JA)}"),
          ("A-en×F-en", f"{orq(a_en_quoted)} {orq(F_EN)}")]
    for ep in ("all", "projects"):
        for block, q in cq:
            try:
                r = cinii(ep, q)
            except Exception as e:  # noqa: BLE001
                r = {"total": None, "records": [], "error": str(e)}
            runs.append({"source": f"CiNii Research ({ep})", "field": "title", "block": block, "query": q, **r})
            print(f"CiNii {ep} {block}: total={r['total']} got={len(r['records'])}", flush=True)
            time.sleep(1)
    # 国立国会図書館サーチ: 組ごと
    for a, f in itertools.product(A_JA, F_JA):
        try:
            r = ndl(f"{a} {f}")
        except Exception as e:  # noqa: BLE001
            r = {"total": None, "records": [], "error": str(e)}
        runs.append({"source": "NDL Search", "field": "title", "block": "A-ja×F-ja", "query": f"{a} {f}", **r})
        print(f"NDL {a} {f}: total={r['total']} got={len(r['records'])}", flush=True)
        time.sleep(1)
    for run in runs:
        for rec in run["records"]:
            t = rec.get("title") or rec.get("title_ja") or rec.get("title_en")
            rec["title_filter"] = title_pass(t) or title_pass(rec.get("title_en", ""))
    meta = {"executed": time.strftime("%Y-%m-%d %H:%M:%S %z"), "design": "design.md §1",
            "note": "書誌だけ。抄録は保存しない。件数は目安で PRISMA の件数ではない。"}
    with open(out, "x", encoding="utf-8") as fh:
        json.dump({"meta": meta, "runs": runs}, fh, ensure_ascii=False, indent=1)


RERUN_BLOCKED = ("この版は 2026-09-29 に実行した版の記録で、そのまま再実行しない（evidence/README.md・decisions.md 判断 16）。"
                 "流用するときは evidence/common.py の関数（抄録を空で上書きしない・repo の外の確認・排他的な作成・URL の許可）で直した新しいスクリプトを作る。")


if __name__ == "__main__":
    sys.exit(RERUN_BLOCKED)  # 実行した時の呼び出し: main(sys.argv[1])
