"""S-15・S-14・S-13 の検索（design.md「サーヴェイ」S0〜S3・2026-09-30 03:54 に固定）。

書誌だけを repo の JSON に書き、抄録は repo の外（第 3 引数のディレクトリ）にだけ書く（common.write_pair で対にする）。
連絡先（メールアドレス）は送らない。無料の情報源だけ（Europe PMC・Semantic Scholar）。

使い方（uv で openpyxl を入れて、本ファイルのディレクトリで実行する）:
  python search_round.py S-15 <書誌の出力 JSON（repo の中）> <抄録の置き場（repo の外のディレクトリ）>
  python search_round.py S-15 --batches <書誌 JSON> <抄録 JSON> <出力ディレクトリ（repo の外）>   # 抽出に渡す束を作る
"""
import glob
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
STEER = os.path.dirname(TASK)
PREV = os.path.join(STEER, "20260929-ai-fatigue-surveys")
sys.path.insert(0, os.path.join(PREV, "evidence"))
import common  # noqa: E402  前タスクの共通の関数（空の抄録で上書きしない・repo の外・対の書き出し・URL の柵）

DB_XLSX = os.path.join(STEER, "20260928-ai-fatigue-db-appraisal", "archive", "input",
                       "AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx")
ALLOWED = ["https://www.ebi.ac.uk/europepmc/webservices/rest/", "https://api.semanticscholar.org/graph/v1/"]
OPENER = common.guarded_opener(ALLOWED)
UA = {"User-Agent": "Mozilla/5.0 (literature-search script)"}
CAP = 5000  # 1 本の検索で取る記録の上限（超えたら打ち切り、記録に truncated と書く）
MAX_TITLE_0B = 250  # 0 段目の通過がこれを超えたら 0b 段を当てる（design.md S0）
AI_RE = r"(?i)artificial intelligence|\bAI\b|machine learning|algorithm|decision support|automat|large language model|\bLLM|ChatGPT|generative"

SURVEYS = {
    "S-15": {
        "epmc": [
            'TITLE_ABS:("automation bias" OR overreliance OR "over-reliance" OR overtrust OR "over-trust" OR "AI reliance" OR '
            '"reliance on AI" OR "AI dependence" OR "AI dependency" OR "algorithmic advice" OR "advice taking" OR complacency) AND '
            'TITLE_ABS:(fatigue OR "decision fatigue" OR "mental fatigue" OR "ego depletion" OR exhaustion OR "sleep deprivation" OR '
            'sleepiness OR burnout) AND TITLE_ABS:("artificial intelligence" OR "machine learning" OR "decision support" OR algorithm OR '
            '"large language model" OR ChatGPT OR "generative AI" OR automation OR automated)',
            'TITLE_ABS:("decision fatigue" OR "mental fatigue" OR "cognitive fatigue") AND TITLE_ABS:("artificial intelligence" OR '
            '"decision support" OR "machine learning" OR "large language model" OR "generative AI" OR ChatGPT OR algorithm)',
        ],
        "s2": [
            '("automation bias" | overreliance | "over-reliance" | "AI reliance" | "reliance on AI" | "AI dependence" | complacency) + '
            '(fatigue | "decision fatigue" | "mental fatigue" | exhaustion | depletion)',
            '("decision fatigue" | "mental fatigue" | "cognitive fatigue") + ("AI advice" | "AI recommendations" | "decision support" | '
            '"algorithmic advice" | "AI-assisted")',
            '("generative AI" | ChatGPT | "large language model") + (dependence | dependency | overreliance) + (fatigue | exhaustion | burnout)',
        ],
        "seeds": ["10.1016/j.actpsy.2025.105725", "10.3389/fpsyg.2026.1879080"],
        "groups": {
            "依存": r"(?i)automation bias|over-?reliance|over-?trust|reliance|reliant|rely|dependen|complacen|advice[- ]taking|"
                    r"algorithm(ic)? advice|acceptance of (AI|algorithm)",
            "疲労": r"(?i)fatigue|depletion|exhaust|burn-?out|sleep|tired|drowsi",
            "AI": AI_RE,
        },
        "title_group": "疲労",
    },
    "S-14": {
        "epmc": [
            'TITLE_ABS:(technostress OR "techno-stress" OR technostressor OR technostressors OR "AI anxiety" OR "AI awareness" OR STARA OR '
            '"AI-induced stress" OR "AI stressors" OR "AI-related stress") AND TITLE_ABS:(burnout OR "burn-out" OR exhaustion OR '
            '"emotional exhaustion" OR strain) AND TITLE_ABS:("artificial intelligence" OR "generative AI" OR ChatGPT OR "machine learning" OR '
            '"large language model" OR robot OR algorithm)',
            'TITLE_ABS:("artificial intelligence" OR "generative AI" OR ChatGPT OR "large language model") AND TITLE_ABS:("Maslach Burnout '
            'Inventory" OR "Copenhagen Burnout Inventory" OR "Oldenburg Burnout Inventory" OR "Burnout Assessment Tool" OR "Shirom-Melamed")',
        ],
        "s2": [
            '(technostress | technostressor | "AI anxiety" | "AI awareness" | STARA | "AI stressor") + (burnout | exhaustion | strain) + '
            '("artificial intelligence" | "generative AI" | ChatGPT)',
            '("AI-induced technostress" | "AI technostress" | "AI-stressors" | "AI stressors") + (burnout | exhaustion | well-being)',
        ],
        "seeds": ["10.1016/j.ijinfomgt.2025.102887", "10.1057/s41599-024-04018-w", "10.1038/s41598-026-45402-7"],
        "groups": {
            "ストレッサー": r"(?i)technostress|techno-stress|stressor|AI anxiety|AI awareness|STARA|job insecurity|stress",
            "燃え尽き": r"(?i)burn-?out|exhaust|strain|fatigue",
            "AI": r"(?i)artificial intelligence|\bAI\b|machine learning|algorithm|automat|robot|large language model|\bLLM|ChatGPT|generative",
        },
        "title_group": "燃え尽き",
    },
    # ★ S-14 の補い（decisions.md 判断 8・design.md S2 からの逸脱）。0 段目の 3 群と種文献は S-14 と同じ。
    "S-14s": {
        "epmc": [
            'TITLE_ABS:(technostress OR "job stress" OR "work stress" OR "occupational stress" OR "AI anxiety" OR "AI awareness" OR STARA) AND '
            'TITLE_ABS:(burnout OR "burn-out" OR exhaustion OR "emotional exhaustion") AND TITLE_ABS:(AI OR "artificial intelligence" OR '
            '"AI adoption" OR "AI dependency" OR "generative AI" OR ChatGPT)',
        ],
        "s2": [
            '("AI adoption" | "AI dependency" | "AI use" | "AI usage" | "AI implementation") + ("job stress" | technostress | "work stress") + '
            '(burnout | exhaustion)',
        ],
        "seeds": ["10.1016/j.ijinfomgt.2025.102887", "10.1057/s41599-024-04018-w", "10.1038/s41598-026-45402-7"],
        "groups": None,  # 下で S-14 のものを入れる
        "title_group": "燃え尽き",
    },
    "S-13": {
        "epmc": [
            'TITLE_ABS:("artificial intelligence" OR "generative AI" OR ChatGPT OR "AI adoption" OR "AI implementation") AND '
            'TITLE_ABS:(organizational OR organisational OR leadership OR "organizational support" OR "change management" OR '
            '"human resource" OR "AI policy" OR managerial OR supervisor) AND TITLE_ABS:(fatigue OR burnout OR exhaustion OR "change fatigue")',
            'TITLE_ABS:("change fatigue" OR "initiative fatigue" OR "transformation fatigue" OR "innovation fatigue" OR "AI fatigue") AND '
            'TITLE_ABS:(organization OR organisation OR organizational OR organisational OR workplace OR employee OR employees)',
        ],
        "s2": [
            '("change fatigue" | "transformation fatigue" | "innovation fatigue" | "AI fatigue") + (organization | organisation | workplace | employees)',
            '("AI adoption" | "AI implementation" | "generative AI") + (leadership | "organizational support" | "change management" | "AI policy") + '
            '(burnout | exhaustion | fatigue)',
        ],
        "seeds": ["10.3389/fpubh.2024.1343932", "10.1016/j.ijinfomgt.2025.102887"],
        "groups": {
            "組織": r"(?i)organi[sz]ation|leader|manager|supervisor|human resource|\bHR\b|change management|polic|team|climate|culture|workplace",
            "疲労": r"(?i)fatigue|burn-?out|exhaust|strain",
            "AI": r"(?i)artificial intelligence|\bAI\b|machine learning|algorithm|automat|large language model|\bLLM|ChatGPT|generative|"
                  r"digital transformation",
        },
        "title_group": "組織",
    },
}

SURVEYS["S-14s"]["groups"] = SURVEYS["S-14"]["groups"]

# ★ タグの名前を限って除く（`re.sub(r"<[^>]+>", …)` は「p < .001」の < から次の > までを消す・前タスク判断 11）
TAGS = re.compile(r"</?(?:h[1-6]|p|b|i|u|em|strong|sub|sup|br|span|div|sec|title|italic|bold|list|list-item|abstract|"
                  r"jats:[a-z-]+|mml:[a-z]+)(?:\s[^<>]*)?/?>", re.I)
DOI_RE = re.compile(r"10\.\d{4,9}/[^\s|）)。,、;\]]+", re.I)


def clean(text):
    return re.sub(r"\s+", " ", TAGS.sub(" ", text or "")).strip()


def get(url, tries=4):
    if not common.allowed_url(url, ALLOWED):
        raise ValueError(f"許していない URL: {url}")
    err = None
    for k in range(tries):
        try:
            with OPENER.open(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            err = e
            if e.code in (400, 404):
                break
            time.sleep(int(e.headers.get("Retry-After") or 8 * (k + 1)))
        except (urllib.error.URLError, TimeoutError, ValueError) as e:
            err = e
            time.sleep(8 * (k + 1))
    raise err


def epmc(q):
    recs, abstracts, cursor, total, truncated = [], {}, "*", None, False
    while True:
        d = get("https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
            {"query": q, "format": "json", "pageSize": 1000, "resultType": "core", "cursorMark": cursor}, quote_via=urllib.parse.quote))
        total = d.get("hitCount")
        rs = d.get("resultList", {}).get("result", [])
        for r in rs:
            key = (r.get("doi") or f'{r.get("source")}:{r.get("id")}').lower()
            recs.append({"key": key, "title": clean(r.get("title", "")), "year": r.get("pubYear"), "doi": r.get("doi", ""),
                         "journal": ((r.get("journalInfo") or {}).get("journal") or {}).get("title", "")[:200],
                         "authors": (r.get("authorString") or "")[:200]})
            common.merge_abstract(abstracts, key, clean(r.get("abstractText", "")))
        nxt = d.get("nextCursorMark")
        if len(recs) >= CAP:
            truncated = True
            break
        if not rs or not nxt or nxt == cursor:
            break
        cursor = nxt
        time.sleep(1)
    return total, recs, abstracts, truncated


def s2_bulk(q):
    recs, abstracts, token, total, truncated = [], {}, None, None, False
    while True:
        p = {"query": q, "fields": "title,year,venue,externalIds,authors,abstract"}
        if token:
            p["token"] = token
        d = get("https://api.semanticscholar.org/graph/v1/paper/search/bulk?" + urllib.parse.urlencode(p))
        total = d.get("total")
        for r in d.get("data", []):
            ext = r.get("externalIds") or {}
            key = (ext.get("DOI") or f'S2:{r.get("paperId")}').lower()
            recs.append({"key": key, "title": clean(r.get("title", "")), "year": r.get("year"), "doi": ext.get("DOI", ""),
                         "journal": (r.get("venue") or "")[:200],
                         "authors": ", ".join(a.get("name", "") for a in (r.get("authors") or [])[:6])[:200]})
            common.merge_abstract(abstracts, key, clean(r.get("abstract") or ""))
        token = d.get("token")
        if len(recs) >= CAP:
            truncated = True
            break
        if not token:
            break
        time.sleep(2)
    return total, recs, abstracts, truncated


def seed_record(doi):
    d = get("https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
        {"query": f'DOI:"{doi}"', "format": "json", "resultType": "core"}, quote_via=urllib.parse.quote))
    rs = d.get("resultList", {}).get("result", [])
    if not rs:
        return None, ""
    return clean(rs[0].get("title", "")), clean(rs[0].get("abstractText", ""))


def known_dois():
    """既出（design.md S0）: DB の 34 件・前タスクの事実のファイル・本タスクの事実のファイルに書かれた DOI。"""
    out = set()
    for p in glob.glob(os.path.join(PREV, "survey-S-??.md")) + glob.glob(os.path.join(TASK, "survey-S-??.md")):
        out |= {m.group(0).rstrip(".").lower() for m in DOI_RE.finditer(open(p, encoding="utf-8").read())}
    import openpyxl
    ws = openpyxl.load_workbook(DB_XLSX, read_only=True)["文献DB"]
    for row in ws.iter_rows(min_row=5, max_row=38, values_only=True):
        if row[7] and str(row[7]).startswith("10."):
            out.add(str(row[7]).lower())
    return out


def passes(spec, title, abstract):
    txt = f"{title} {abstract}"
    return all(re.search(p, txt) for p in spec["groups"].values())


def main(sid, out, abs_dir):
    spec = SURVEYS[sid]
    common.ensure_outside_repo(abs_dir)
    if not os.path.isdir(abs_dir):
        sys.exit(f"抄録の置き場が無い（作らない）: {abs_dir}")
    abs_path = os.path.join(abs_dir, f"{sid.lower()}_abstracts.json")
    if os.path.exists(out) or os.path.exists(abs_path):
        sys.exit("出力先が既にある（上書きしない）")
    known = known_dois()
    runs, all_abs = [], {}
    plan = [("Europe PMC", f"E{i + 1}", q, epmc) for i, q in enumerate(spec["epmc"])]
    plan += [("Semantic Scholar", f"S{i + 1}", q, s2_bulk) for i, q in enumerate(spec["s2"])]
    for source, label, q, fn in plan:
        try:
            total, recs, abstracts, truncated = fn(q)
            status = "ok"
        except Exception as e:  # noqa: BLE001  取得の失敗は記録に残し、件数を推測で埋めない
            total, recs, abstracts, truncated, status = None, [], {}, False, f"ERR {type(e).__name__}: {e}"
        for key, text in abstracts.items():
            common.merge_abstract(all_abs, key, text)
        runs.append({"source": source, "label": label, "query": q, "status": status, "total": total, "truncated": truncated,
                     "records": recs})
        print(source, label, status, total, len(recs), flush=True)
        time.sleep(2)
    # 0 段目・0b 段・既出（記録の和で判定する: 情報源をまたいで集めた抄録で見る）
    uniq = {}
    for run in runs:
        for r in run["records"]:
            uniq.setdefault(r["key"], r)
    for key, r in uniq.items():
        a = all_abs.get(key, "")
        r["stage0"] = passes(spec, r["title"], a)
        r["stage0b"] = bool(r["stage0"] and re.search(spec["groups"][spec["title_group"]], r["title"] or ""))
        r["known"] = bool(r["doi"]) and r["doi"].lower() in known
        r["has_abstract"] = bool(a.strip())
        r["year_ok"] = not (isinstance(r["year"], int) and r["year"] > 2026)
    for run in runs:
        for r in run["records"]:
            r.update({k: uniq[r["key"]][k] for k in ("stage0", "stage0b", "known", "has_abstract", "year_ok")})
    seeds = []
    for doi in spec["seeds"]:
        try:
            t, a = seed_record(doi)
        except Exception as e:  # noqa: BLE001
            t, a = None, f"ERR {type(e).__name__}"
        seeds.append({"doi": doi, "found_in_runs": doi.lower() in uniq, "title": t, "stage0": bool(t) and passes(spec, t, a),
                      "has_abstract": bool(a and not a.startswith("ERR"))})
        time.sleep(1)
    n0 = sum(r["stage0"] and r["year_ok"] for r in uniq.values())
    meta = {"executed": time.strftime("%Y-%m-%d %H:%M:%S %z"), "survey": sid, "design": "design.md サーヴェイ S0・" + sid,
            "unique": len(uniq), "stage0": n0, "stage0b": sum(r["stage0b"] and r["year_ok"] for r in uniq.values()),
            "use_0b": n0 > MAX_TITLE_0B, "known": sum(r["known"] for r in uniq.values()), "seeds": seeds}
    common.write_pair(out, abs_path, {"meta": meta, "runs": runs}, all_abs)
    print(json.dumps(meta, ensure_ascii=False))


def batches(sid, bib_path, abs_path, out_dir, size=80, exclude_bib=None):
    """抽出に渡す束（題名・年・掲載誌・抄録）を repo の外に書く。0 段目（通過が多ければ 0b 段）・既出でない・年が範囲内の記録。
    exclude_bib: 先に束にした検索の書誌 JSON（その記録の鍵は束にしない。補いの検索で重複を除くため・判断 8）。"""
    common.ensure_outside_repo(out_dir)
    bib, ab = json.load(open(bib_path, encoding="utf-8")), json.load(open(abs_path, encoding="utf-8"))
    if not common.same_run(bib, ab):
        sys.exit("書誌と抄録が同じ実行の対ではない")
    stage = "stage0b" if bib["meta"]["use_0b"] else "stage0"
    seen, rows = set(), []
    if exclude_bib:
        prev = json.load(open(exclude_bib, encoding="utf-8"))
        seen |= {r["key"] for run in prev["runs"] for r in run["records"]}
    for run in bib["runs"]:
        for r in run["records"]:
            if r["key"] in seen or not r[stage] or r["known"] or not r["year_ok"]:
                continue
            seen.add(r["key"])
            rows.append({"id": f"{sid}-{len(rows) + 1:03d}", "key": r["key"], "doi": r["doi"], "title": r["title"], "year": r["year"],
                         "journal": r["journal"], "abstract": ab["abstracts"].get(r["key"], "")})
    for i in range(0, len(rows), size):
        p = os.path.join(out_dir, f"{sid.lower()}_batch{i // size + 1}.json")
        with common.open_exclusive(p) as fh:
            json.dump(rows[i:i + size], fh, ensure_ascii=False, indent=1)
    print(stage, len(rows), "件 →", (len(rows) + size - 1) // size, "束")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] in SURVEYS and "--batches" in sys.argv:
        a = [x for x in sys.argv[1:] if x != "--batches"]
        batches(a[0], a[1], a[2], a[3], exclude_bib=a[4] if len(a) > 4 else None)
    elif len(sys.argv) == 4 and sys.argv[1] in SURVEYS:
        main(*sys.argv[1:4])
    else:
        sys.exit(__doc__)
