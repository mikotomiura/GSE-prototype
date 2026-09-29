"""S-05: 自動化を見張る疲労（受動的疲労・覚醒の低下・自動化への慢心）を探す（design.md §5.2・§5.3）。

書誌だけを出力 JSON に書く。抄録は第 2 引数のディレクトリ（repo の外）にだけ書く。連絡先は送らない。
使い方: python search_s05.py <出力 JSON> <抄録の保存先（repo の外）>
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (literature-search script)"}
SEEDS = ["10.1201/b12791-3.1", "10.1037/a0034386", "10.1016/j.promfg.2015.07.499", "10.1177/0018720811423261",
         "10.1016/j.aap.2018.04.004", "10.1177/0018720810376055"]
EPMC = [
    'TITLE_ABS:"passive fatigue"',
    'TITLE_ABS:("automation complacency" OR "automation-induced complacency")',
    'TITLE_ABS:("vigilance decrement" OR "vigilance decline" OR underload) AND TITLE_ABS:(automation OR automated OR autonomous '
    'OR "artificial intelligence") AND TITLE_ABS:(fatigue OR sleepiness OR drowsiness OR arousal)',
    'TITLE_ABS:("human oversight" OR "human-in-the-loop" OR "human monitoring" OR supervisory OR supervision) AND '
    'TITLE_ABS:("artificial intelligence" OR "machine learning" OR "AI system" OR "AI-assisted") AND TITLE_ABS:(fatigue OR vigilance OR complacency)',
]
S2 = [
    '"passive fatigue"',
    '("passive fatigue" | "task-induced fatigue" | "vigilance decrement" | underload) + (automation | automated | autonomous | "artificial intelligence")',
    '("human oversight" | "human-in-the-loop" | "AI-assisted" | "decision support") + (vigilance | "passive fatigue" | complacency) + ("artificial intelligence" | "machine learning")',
]
F0 = re.compile(r"(?i)passive fatigue|vigilance|complacen|underload|sleepiness|drowsiness|task-induced fatigue|fatigue")
A0 = re.compile(r"(?i)automat|autonomous|artificial intelligence|machine learning|AI-assisted|decision support|supervis|monitoring|oversight")


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
                         "pmcid": r.get("pmcid", ""), "journal": (r.get("journalInfo") or {}).get("journal", {}).get("title", ""),
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
        p = {"query": q, "fields": "title,year,venue,externalIds,authors,abstract"}
        if token:
            p["token"] = token
        d = get("https://api.semanticscholar.org/graph/v1/paper/search/bulk?" + urllib.parse.urlencode(p))
        total = d.get("total")
        for r in d.get("data", []):
            ext = r.get("externalIds") or {}
            key = (ext.get("DOI") or f'S2:{r.get("paperId")}').lower()
            recs.append({"key": key, "title": r.get("title", ""), "year": r.get("year"), "doi": ext.get("DOI", ""),
                         "journal": r.get("venue", ""), "authors": ", ".join(a.get("name", "") for a in (r.get("authors") or [])[:6])})
            abstracts[key] = r.get("abstract") or ""
        token = d.get("token")
        if not token:
            break
        time.sleep(2)
    return total, recs, abstracts


def seeds():
    recs, abstracts = [], {}
    for doi in SEEDS:
        m = get("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/")).get("message", {})
        key = doi.lower()
        recs.append({"key": key, "title": (m.get("title") or [""])[0], "year": (m.get("issued") or {}).get("date-parts", [[None]])[0][0],
                     "doi": doi, "journal": (m.get("container-title") or [""])[0], "type": m.get("type"),
                     "authors": ", ".join(f'{a.get("family", "")} {a.get("given", "")}'.strip() for a in m.get("author", [])[:6])})
        abstracts[key] = re.sub(r"<[^>]+>", " ", m.get("abstract", "") or "")
        time.sleep(1)
    return len(recs), recs, abstracts


def main(out, abs_dir):
    if os.path.exists(out):
        sys.exit(f"出力先が既にある（上書きしない）: {out}")
    os.makedirs(abs_dir, exist_ok=True)
    spec = [("Crossref", "種文献 6 件", " ".join(SEEDS), lambda q: seeds())]
    spec += [("Europe PMC", f"E{i+1}", q, epmc) for i, q in enumerate(EPMC)]
    spec += [("Semantic Scholar", f"S{i+1}", q, s2_bulk) for i, q in enumerate(S2)]
    runs, all_abs = [], {}
    for source, label, q, fn in spec:
        try:
            total, recs, abstracts = fn(q)
            status = "ok"
        except Exception as e:  # noqa: BLE001
            total, recs, abstracts, status = None, [], {}, f"ERR {e}"
        for r in recs:
            txt = (r["title"] or "") + " " + (abstracts.get(r["key"]) or "")
            r["stage0"] = bool(F0.search(txt) and A0.search(txt))
        all_abs.update(abstracts)
        runs.append({"source": source, "label": label, "query": q, "status": status, "total": total, "records": recs})
        print(source, label, status, total, len(recs), "stage0:", sum(r["stage0"] for r in recs), flush=True)
        time.sleep(2)
    with open(os.path.join(abs_dir, "s05_abstracts.json"), "w", encoding="utf-8") as fh:
        json.dump(all_abs, fh, ensure_ascii=False, indent=1)
    with open(out, "x", encoding="utf-8") as fh:
        json.dump({"meta": {"executed": time.strftime("%Y-%m-%d %H:%M:%S %z"), "design": "design.md §5"}, "runs": runs},
                  fh, ensure_ascii=False, indent=1)


RERUN_BLOCKED = ("この版は 2026-09-29 に実行した版の記録で、そのまま再実行しない（evidence/README.md・decisions.md 判断 16）。"
                 "流用するときは evidence/common.py の関数（抄録を空で上書きしない・repo の外の確認・排他的な作成・URL の許可）で直した新しいスクリプトを作る。")


if __name__ == "__main__":
    sys.exit(RERUN_BLOCKED)  # 実行した時の呼び出し: main(*sys.argv[1:3])
