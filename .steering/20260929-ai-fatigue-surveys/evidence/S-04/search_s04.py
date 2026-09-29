"""S-04: AI の導入と使う人の疲労・燃え尽き（減る側の証拠を含む）を探す（design.md §4.3）。

書誌だけを出力 JSON に書く。抄録は第 2 引数のディレクトリ（repo の外）にだけ書く。連絡先は送らない。
使い方: python search_s04.py <出力 JSON> <抄録の保存先（repo の外）>
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (literature-search script)"}

Q1 = ('TITLE_ABS:("ambient AI" OR "AI scribe" OR "ambient scribe" OR "ambient listening" OR "ambient artificial intelligence" '
      'OR "ambient documentation" OR "digital scribe") AND TITLE_ABS:(burnout OR fatigue OR exhaustion OR "cognitive load" '
      'OR "task load" OR workload OR "documentation burden")')
Q2 = ('TITLE_ABS:("large language model" OR "generative AI" OR "AI-generated" OR "artificial intelligence") AND '
      'TITLE_ABS:("draft replies" OR "draft responses" OR "in-basket" OR inbox OR "patient messages") AND '
      'TITLE_ABS:(burnout OR fatigue OR "cognitive burden" OR "task load" OR workload)')
Q3 = ('TITLE_ABS:("generative AI" OR "large language model" OR ChatGPT OR Copilot OR "AI assistant" OR "AI tool" OR '
      '"artificial intelligence") AND TITLE_ABS:(burnout OR fatigue OR exhaustion) AND TITLE_ABS:(randomized OR randomised OR '
      '"controlled trial" OR crossover OR "pre-post" OR "before and after" OR "quasi-experimental" OR "difference-in-differences" '
      'OR "field experiment")')
S2Q = ('("generative AI" | ChatGPT | Copilot | "large language model" | "AI assistant") + (burnout | fatigue | exhaustion | '
       '"cognitive load" | workload) + (randomized | experiment | "field experiment" | intervention | "quasi-experimental" | '
       '"difference-in-differences")')
OAQ = ('("generative AI" OR "large language model" OR ChatGPT OR Copilot OR "AI assistant" OR "AI tool" OR "artificial intelligence") '
       'AND (burnout OR fatigue OR exhaustion) AND (randomized OR randomised OR "controlled trial" OR crossover OR "pre-post" OR '
       '"before and after" OR "quasi-experimental" OR "difference-in-differences" OR "field experiment")')


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
            key = (r.get("doi") or f'{r.get("source")}:{r.get("id")}').lower()
            recs.append({"key": key, "title": r.get("title", ""), "year": r.get("pubYear"), "doi": r.get("doi", ""),
                         "pmid": r.get("pmid", ""), "pmcid": r.get("pmcid", ""),
                         "journal": (r.get("journalInfo") or {}).get("journal", {}).get("title", ""),
                         "pubTypes": (r.get("pubTypeList") or {}).get("pubType", []),
                         "authors": (r.get("authorString") or "")[:200]})
            abstracts[key] = r.get("abstractText", "")
        nxt = d.get("nextCursorMark")
        if not rs or not nxt or nxt == cursor:
            break
        cursor = nxt
        time.sleep(1)
    return total, recs, abstracts


def s2_bulk(q):
    recs, abstracts, token, total = [], {}, None, None
    while True:
        p = {"query": q, "fields": "title,year,venue,externalIds,authors,abstract,publicationTypes"}
        if token:
            p["token"] = token
        d = get("https://api.semanticscholar.org/graph/v1/paper/search/bulk?" + urllib.parse.urlencode(p))
        total = d.get("total")
        for r in d.get("data", []):
            ext = r.get("externalIds") or {}
            key = (ext.get("DOI") or f'S2:{r.get("paperId")}').lower()
            recs.append({"key": key, "title": r.get("title", ""), "year": r.get("year"), "doi": ext.get("DOI", ""),
                         "journal": r.get("venue", ""), "pubTypes": r.get("publicationTypes") or [],
                         "authors": ", ".join(a.get("name", "") for a in (r.get("authors") or [])[:6])})
            abstracts[key] = r.get("abstract") or ""
        token = d.get("token")
        if not token:
            break
        time.sleep(2)
    return total, recs, abstracts


def openalex(q):
    recs, abstracts, cursor, total = [], {}, "*", None
    while cursor:
        d = get("https://api.openalex.org/works?" + urllib.parse.urlencode(
            {"search": q, "per-page": 200, "cursor": cursor,
             "select": "doi,title,publication_year,primary_location,type,abstract_inverted_index"}))
        total = d.get("meta", {}).get("count")
        for r in d.get("results", []):
            doi = (r.get("doi") or "").replace("https://doi.org/", "")
            key = doi.lower() or r.get("title", "")
            recs.append({"key": key, "title": r.get("title") or "", "year": r.get("publication_year"), "doi": doi,
                         "journal": ((r.get("primary_location") or {}).get("source") or {}).get("display_name", ""),
                         "type": r.get("type")})
            inv = r.get("abstract_inverted_index") or {}
            abstracts[key] = " ".join(w for _, w in sorted((p, w) for w, ps in inv.items() for p in ps))
        cursor = d.get("meta", {}).get("next_cursor")
        if len(recs) >= 1000:
            break
        time.sleep(1)
    return total, recs, abstracts


def main(out, abs_dir):
    if os.path.exists(out):
        sys.exit(f"出力先が既にある（上書きしない）: {out}")
    os.makedirs(abs_dir, exist_ok=True)
    spec = [("Europe PMC", "Q1 AI の記録支援", Q1, epmc), ("Europe PMC", "Q2 AI の下書き返信", Q2, epmc),
            ("Europe PMC", "Q3 一般", Q3, epmc), ("Semantic Scholar", "bulk（医療以外）", S2Q, s2_bulk),
            ("OpenAlex", "search（Q3 と同じ語・最大 1,000 件）", OAQ, openalex)]
    runs, all_abs = [], {}
    for source, label, q, fn in spec:
        try:
            total, recs, abstracts = fn(q)
            status = "ok"
        except Exception as e:  # noqa: BLE001
            total, recs, abstracts, status = None, [], {}, f"ERR {e}"
        all_abs.update(abstracts)
        runs.append({"source": source, "label": label, "query": q, "status": status, "total": total, "records": recs})
        print(source, label, status, total, len(recs), flush=True)
        time.sleep(2)
    with open(os.path.join(abs_dir, "s04_abstracts.json"), "w", encoding="utf-8") as fh:
        json.dump(all_abs, fh, ensure_ascii=False, indent=1)
    with open(out, "x", encoding="utf-8") as fh:
        json.dump({"meta": {"executed": time.strftime("%Y-%m-%d %H:%M:%S %z"), "design": "design.md §4"}, "runs": runs},
                  fh, ensure_ascii=False, indent=1)


RERUN_BLOCKED = ("この版は 2026-09-29 に実行した版の記録で、そのまま再実行しない（evidence/README.md・decisions.md 判断 16）。"
                 "流用するときは evidence/common.py の関数（抄録を空で上書きしない・repo の外の確認・排他的な作成・URL の許可）で直した新しいスクリプトを作る。")


if __name__ == "__main__":
    sys.exit(RERUN_BLOCKED)  # 実行した時の呼び出し: main(*sys.argv[1:3])
