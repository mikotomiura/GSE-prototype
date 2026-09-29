"""S-08: AI 疲労の尺度の開発・検証を探す（design.md §3.3）。

書誌だけを出力 JSON に書く。抄録は第 2 引数のディレクトリ（repo の外）にだけ書く。連絡先は送らない。
使い方: python search_scales.py <出力 JSON> <抄録の保存先（repo の外）>
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (literature-search script)"}
TERMS = ['"AI fatigue"', '"artificial intelligence fatigue"', '"generative AI fatigue"', '"ChatGPT fatigue"',
         '"AI-induced fatigue"', '"AI-related fatigue"', '"chatbot fatigue"', '"GenAI fatigue"', '"AI exhaustion"',
         '"AI burnout"']
MEAS = ["scale", "questionnaire", "inventory", "instrument", "psychometric", "validation", '"factor analysis"']
AF001 = "10.1016/j.chbr.2026.101186"


def get(url, tries=4):
    err = None
    for k in range(tries):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read())
        except urllib.error.HTTPError as e:
            err = e
            if e.code in (400, 404):
                break
            time.sleep(int(e.headers.get("Retry-After") or 8 * (k + 1)))
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(8 * (k + 1))
    raise err


def epmc(q):
    recs, abstracts, cursor, total = [], {}, "*", None
    while True:
        d = get("https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
            {"query": q, "format": "json", "pageSize": 1000, "resultType": "core", "cursorMark": cursor},
            quote_via=urllib.parse.quote))
        total = d.get("hitCount")
        rs = d.get("resultList", {}).get("result", [])
        for r in rs:
            key = r.get("doi") or f'{r.get("source")}:{r.get("id")}'
            recs.append({"key": key, "title": r.get("title", ""), "year": r.get("pubYear"), "doi": r.get("doi", ""),
                         "journal": (r.get("journalInfo") or {}).get("journal", {}).get("title", ""),
                         "pubType": r.get("pubType", ""), "authors": (r.get("authorString") or "")[:200]})
            abstracts[key] = r.get("abstractText", "")
        nxt = d.get("nextCursorMark")
        if not rs or not nxt or nxt == cursor:
            break
        cursor = nxt
    return total, recs, abstracts


def s2_bulk(q):
    recs, abstracts, token, total = [], {}, None, None
    while True:
        p = {"query": q, "fields": "title,year,venue,externalIds,authors,abstract"}
        if token:
            p["token"] = token
        d = get("https://api.semanticscholar.org/graph/v1/paper/search/bulk?" + urllib.parse.urlencode(p))
        total = d.get("total")
        for r in d.get("data", []):
            ext = r.get("externalIds") or {}
            key = ext.get("DOI") or f'S2:{r.get("paperId")}'
            recs.append({"key": key, "title": r.get("title", ""), "year": r.get("year"), "doi": ext.get("DOI", ""),
                         "journal": r.get("venue", ""), "authors": ", ".join(a.get("name", "") for a in (r.get("authors") or [])[:6])})
            abstracts[key] = r.get("abstract") or ""
        token = d.get("token")
        if not token:
            break
        time.sleep(2)
    return total, recs, abstracts


def crossref_title(q):
    d = get("https://api.crossref.org/works?" + urllib.parse.urlencode({"query.title": q, "rows": 50}))
    recs = [{"key": i.get("DOI"), "title": (i.get("title") or [""])[0], "year": (i.get("issued") or {}).get("date-parts", [[None]])[0][0],
             "doi": i.get("DOI"), "journal": (i.get("container-title") or [""])[0], "type": i.get("type")}
            for i in d["message"]["items"]]
    return None, recs, {}


def openalex(q):
    d = get("https://api.openalex.org/works?" + urllib.parse.urlencode({"search": q, "per-page": 200,
                                                                       "select": "doi,title,publication_year,primary_location,type"}))
    recs = [{"key": (r.get("doi") or "").replace("https://doi.org/", ""), "title": r.get("title") or "",
             "year": r.get("publication_year"), "doi": (r.get("doi") or "").replace("https://doi.org/", ""),
             "journal": ((r.get("primary_location") or {}).get("source") or {}).get("display_name", ""), "type": r.get("type")}
            for r in d.get("results", [])]
    return d.get("meta", {}).get("count"), recs, {}


def s2_citations(doi):
    recs, off = [], 0
    while True:
        d = get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}/citations?" + urllib.parse.urlencode(
            {"fields": "title,year,venue,externalIds", "limit": 100, "offset": off}))
        for c in d.get("data", []):
            p = c.get("citingPaper") or {}
            ext = p.get("externalIds") or {}
            recs.append({"key": ext.get("DOI") or p.get("paperId"), "title": p.get("title", ""), "year": p.get("year"),
                         "doi": ext.get("DOI", ""), "journal": p.get("venue", "")})
        if d.get("next") is None:
            break
        off = d["next"]
    return len(recs), recs, {}


def main(out, abs_dir):
    if os.path.exists(out):
        sys.exit(f"出力先が既にある（上書きしない）: {out}")
    os.makedirs(abs_dir, exist_ok=True)
    t_or, m_or = " OR ".join(TERMS), " OR ".join(MEAS)
    runs_spec = [
        ("Europe PMC", "TITLE_ABS", f"TITLE_ABS:({t_or}) AND TITLE_ABS:({m_or})", epmc),
        ("Semantic Scholar", "bulk", f"({' | '.join(TERMS)}) + ({' | '.join(MEAS)})", s2_bulk),
        ("Crossref", "query.title（上位 50・件数なし）", "AI fatigue scale", crossref_title),
        ("Crossref", "query.title（上位 50・件数なし）", "AI fatigue questionnaire", crossref_title),
        ("Crossref", "query.title（上位 50・件数なし）", "generative AI fatigue scale", crossref_title),
        ("OpenAlex", "search", f"({t_or}) AND ({m_or})", openalex),
        ("Semantic Scholar", "citations of AF001", AF001, s2_citations),
    ]
    runs, all_abs = [], {}
    for source, field, q, fn in runs_spec:
        try:
            total, recs, abstracts = fn(q)
            status = "ok"
        except Exception as e:  # noqa: BLE001
            total, recs, abstracts, status = None, [], {}, f"ERR {e}"
        all_abs.update(abstracts)
        runs.append({"source": source, "field": field, "query": q, "status": status, "total": total, "records": recs})
        print(source, field, q[:60], status, total, len(recs), flush=True)
        time.sleep(2)
    with open(os.path.join(abs_dir, "s08_abstracts.json"), "w", encoding="utf-8") as fh:
        json.dump(all_abs, fh, ensure_ascii=False, indent=1)
    with open(out, "x", encoding="utf-8") as fh:
        json.dump({"meta": {"executed": time.strftime("%Y-%m-%d %H:%M:%S %z"), "design": "design.md §3"}, "runs": runs},
                  fh, ensure_ascii=False, indent=1)


RERUN_BLOCKED = ("この版は 2026-09-29 に実行した版の記録で、そのまま再実行しない（evidence/README.md・decisions.md 判断 16）。"
                 "流用するときは evidence/common.py の関数（抄録を空で上書きしない・repo の外の確認・排他的な作成・URL の許可）で直した新しいスクリプトを作る。")


if __name__ == "__main__":
    sys.exit(RERUN_BLOCKED)  # 実行した時の呼び出し: main(*sys.argv[1:3])
