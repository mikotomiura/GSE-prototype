"""S-12: 英語の情報源で、日本の対象者の研究を探す（design.md §1.2・§1.3）。

書誌だけを出力 JSON に書く。抄録は第 3 引数のディレクトリ（repo の外）にだけ書く（判定の材料）。
学術 API には連絡先を送らない（mailto を付けない）。
使い方: python search_en.py <出力 JSON> <抄録の保存先（repo の外）>
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (literature-search script)"}
A_EN = ['"generative AI"', "ChatGPT", '"large language model"', '"artificial intelligence"', "chatbot"]
F_EN = ["fatigue", "burnout", "exhaustion", "technostress"]
JP = ["Japan", "Japanese"]


def get(url, tries=5):
    err = None
    for k in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read()
        except urllib.error.HTTPError as e:
            err = e
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After") or 10 * (k + 1)))
            else:
                time.sleep(5 * (k + 1))
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(5 * (k + 1))
    raise err


def epmc(q):
    recs, abstracts, cursor, total = [], {}, "*", None
    while True:
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
            {"query": q, "format": "json", "pageSize": 1000, "resultType": "core", "cursorMark": cursor},
            quote_via=urllib.parse.quote)
        d = json.loads(get(url))
        total = d.get("hitCount")
        rs = d.get("resultList", {}).get("result", [])
        for r in rs:
            key = r.get("doi") or f'{r.get("source")}:{r.get("id")}'
            recs.append({"key": key, "title": r.get("title", ""), "year": r.get("pubYear"),
                         "journal": (r.get("journalInfo") or {}).get("journal", {}).get("title", "") or r.get("bookOrReportDetails", {}).get("publisher", ""),
                         "doi": r.get("doi", ""), "pmid": r.get("pmid", ""), "pubType": r.get("pubType", ""),
                         "authors": r.get("authorString", "")[:200]})
            abstracts[key] = r.get("abstractText", "")
        nxt = d.get("nextCursorMark")
        if not rs or not nxt or nxt == cursor:
            break
        cursor = nxt
        time.sleep(1)
    return total, recs, abstracts


def s2(q):
    recs, abstracts, token, total = [], {}, None, None
    while True:
        params = {"query": q, "fields": "title,year,venue,externalIds,authors,abstract,publicationTypes"}
        if token:
            params["token"] = token
        url = "https://api.semanticscholar.org/graph/v1/paper/search/bulk?" + urllib.parse.urlencode(params)
        d = json.loads(get(url))
        total = d.get("total")
        for r in d.get("data", []):
            ext = r.get("externalIds") or {}
            key = ext.get("DOI") or f'S2:{r.get("paperId")}'
            recs.append({"key": key, "title": r.get("title", ""), "year": r.get("year"), "journal": r.get("venue", ""),
                         "doi": ext.get("DOI", ""), "authors": ", ".join(a.get("name", "") for a in (r.get("authors") or [])[:6])})
            abstracts[key] = r.get("abstract") or ""
        token = d.get("token")
        if not token:
            break
        time.sleep(2)
    return total, recs, abstracts


def openalex(q):
    recs, abstracts, cursor, total = [], {}, "*", None
    while cursor:
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(
            {"search": q, "per-page": 200, "cursor": cursor,
             "select": "id,doi,title,publication_year,primary_location,authorships,abstract_inverted_index,type"})
        d = json.loads(get(url))
        total = d.get("meta", {}).get("count")
        for r in d.get("results", []):
            key = (r.get("doi") or "").replace("https://doi.org/", "") or r.get("id")
            src = ((r.get("primary_location") or {}).get("source") or {}).get("display_name", "")
            recs.append({"key": key, "title": r.get("title") or "", "year": r.get("publication_year"), "journal": src,
                         "doi": (r.get("doi") or "").replace("https://doi.org/", ""), "type": r.get("type"),
                         "authors": ", ".join(a.get("author", {}).get("display_name", "") for a in (r.get("authorships") or [])[:6])})
            inv = r.get("abstract_inverted_index") or {}
            words = sorted(((p, w) for w, ps in inv.items() for p in ps))
            abstracts[key] = " ".join(w for _, w in words)
        cursor = d.get("meta", {}).get("next_cursor")
        time.sleep(1)
    return total, recs, abstracts


def main(out, abs_dir):
    if os.path.exists(out):
        sys.exit(f"出力先が既にある（上書きしない）: {out}")
    os.makedirs(abs_dir, exist_ok=True)
    a, f, j = " OR ".join(A_EN), " OR ".join(F_EN), " OR ".join(JP)
    queries = [
        ("Europe PMC", "TITLE_ABS＋AFF", f"TITLE_ABS:({a}) AND TITLE_ABS:({f}) AND (TITLE_ABS:({j}) OR AFF:Japan)", epmc),
        ("Europe PMC", "TITLE_ABS", f"TITLE_ABS:({a}) AND TITLE_ABS:({f}) AND TITLE_ABS:({j})", epmc),
        ("Semantic Scholar", "bulk（題名・抄録）",
         f"({' | '.join(A_EN)}) + ({' | '.join(F_EN)}) + ({' | '.join(JP)})", s2),
        ("OpenAlex", "search（題名・抄録・本文）", f"({a}) AND ({f}) AND ({j})", openalex),
    ]
    runs, all_abs = [], {}
    for source, field, q, fn in queries:
        try:
            total, recs, abstracts = fn(q)
            status = "ok"
        except Exception as e:  # noqa: BLE001
            total, recs, abstracts, status = None, [], {}, f"ERR {e}"
        all_abs.update(abstracts)
        runs.append({"source": source, "field": field, "query": q, "status": status, "total": total, "records": recs})
        print(source, field, status, total, len(recs), flush=True)
        time.sleep(2)
    with open(os.path.join(abs_dir, "s12_en_abstracts.json"), "w", encoding="utf-8") as fh:
        json.dump(all_abs, fh, ensure_ascii=False, indent=1)
    meta = {"executed": time.strftime("%Y-%m-%d %H:%M:%S %z"), "design": "design.md §1",
            "note": "書誌だけ。抄録は repo の外。件数は目安で PRISMA の件数ではない。"}
    with open(out, "x", encoding="utf-8") as fh:
        json.dump({"meta": meta, "runs": runs}, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:3])
