"""抄録を DOI で取り直す（design.md §0.2・§0.3・§2.2・§2.4・2026-09-30 18:05 に固定）。

書誌だけを repo の JSON に書き、抄録は repo の外（第 3 引数のディレクトリ）にだけ書く（common.write_pair で対にする）。
連絡先（メールアドレス）は送らない。無料の情報源だけ（Europe PMC・Semantic Scholar・OpenAlex・Crossref）。

使い方（openpyxl の入った Python で、本ファイルのディレクトリで実行する）:
  python fetch_abstracts.py records <書誌の出力 JSON（repo の中）> <抄録の置き場（repo の外のディレクトリ）>   # 259 件
  python fetch_abstracts.py theory  <書誌の出力 JSON（repo の中）> <抄録の置き場（repo の外のディレクトリ）>   # S-09 の原典・原著
  python fetch_abstracts.py theory2 <書誌の出力 JSON（repo の中）> <抄録の置き場（repo の外のディレクトリ）>   # 逸脱で足した 2 件（判断 3）
"""
import datetime
import email.utils
import hashlib
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
STEER = os.path.dirname(TASK)
sys.path.insert(0, os.path.join(STEER, "20260929-ai-fatigue-surveys", "evidence"))
sys.path.insert(0, os.path.join(STEER, "20260930-ai-fatigue-judge-file", "evidence"))
import common  # noqa: E402  空の抄録で上書きしない・repo の外・対の書き出し・URL の柵
from search_round import clean  # noqa: E402  タグの名前を限って除く（p < .001 の < を消さない）

JUDGE_XLSX = os.path.join(STEER, "20260930-ai-fatigue-judge-file", "archive", "judge",
                          "AI_fatigue_judge-sheet_2026-09-30_judge1.xlsx")
JUDGE_SHA = "6984472edeef3794a9ed075076568aaca8373c4fb675afba608cdba280e6c883"

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/"
S2 = "https://api.semanticscholar.org/graph/v1/"
OA = "https://api.openalex.org/"
CR = "https://api.crossref.org/"
ALLOWED = [EPMC, S2, OA, CR]
UA = {"User-Agent": "Mozilla/5.0 (literature-search script)"}

# design.md §2.2・§2.4 の固定の一覧（鍵, DOI, 題名の目印）。書籍で DOI の無いものは載せない（書誌だけを事実のファイルに書く）
THEORY = [
    ("Kurzban2013", "10.1017/S0140525X12003196", "opportunity cost model of subjective effort"),
    ("Agrawal2022", "10.1037/rev0000309", "temporal dynamics of opportunity costs"),
    ("Hockey1997", "10.1016/S0301-0511(96)05223-4", "Compensatory control"),
    ("DesmondHancock2000", "10.1201/b12791-3.1", "Active and Passive Fatigue"),
    ("Saxby2013", "10.1037/a0034386", "Active and passive fatigue in simulated driving"),
    ("Matthews2019", "10.1016/j.aap.2018.04.004", "passive fatigue"),
    ("Baumeister1998", "10.1037/0022-3514.74.5.1252", "Ego depletion"),
    ("Hagger2016", "10.1177/1745691616652873", "Multilab Preregistered Replication"),
    ("Carter2015", "10.1037/xge0000083", "meta-analytic tests of the depletion effect"),
    ("Friese2019", "10.1177/1088868318762183", "Is Ego Depletion Real"),
    ("Vohs2021", "10.1177/0956797621989733", "Multisite Preregistered Paradigmatic Test"),
    ("Dang2021", "10.1177/1948550619887702", "Multilab Replication of the Ego Depletion"),
    ("Vadillo2016", "10.1177/0956797616654911", "Sugar and Willpower"),
    ("Finley2019", "10.1027/1864-9335/a000376", "Sweet Nothings"),
    ("Hopstaken2015", "10.1111/psyp.12339", "mental fatigue and task disengagement"),
    ("Lin2020", "10.1177/0956797620904990", "Strong Effort Manipulations"),
    ("Demerouti2001", "10.1037/0021-9010.86.3.499", "job demands-resources model of burnout"),
    ("BakkerDemerouti2007", "10.1108/02683940710733115", "Job Demands-Resources model: state of the art"),
    ("Hobfoll1989", "10.1037/0003-066X.44.3.513", "Conservation of resources"),
    ("Tarafdar2007", "10.2753/MIS0742-1222240109", "Impact of Technostress"),
    ("RaguNathan2008", "10.1287/isre.1070.0165", "Consequences of Technostress"),
    ("Sweller1988", "10.1207/s15516709cog1202_4", "Cognitive load during problem solving"),
    ("Koeske1993", "10.1300/J079v17n03_06", "Stress-Strain-Outcome"),
    ("Cavanaugh2000", "10.1037/0021-9010.85.1.65", "self-reported work stress"),
    ("RyanDeci2000", "10.1037/0003-066X.55.1.68", "Self-determination theory"),
    ("Siegrist1996", "10.1037/1076-8998.1.1.27", "effort/low-reward"),
]

# ★ design.md §2.4 からの逸脱（decisions.md 判断 3）: 5 件以上の枠組みのうち、原著の抄録が無料の情報源に無いもの（F-COR）と、
#   原著を A 群の事実のファイルの要約でなく一次で読むもの（F-AUT）を足す
THEORY2 = [
    ("Hobfoll2018", "10.1146/annurev-orgpsych-032117-104640", "Conservation of Resources in the Organizational Context"),
    ("ParasuramanManzey2010", "10.1177/0018720810376055", "Complacency and Bias in Human Use of Automation"),
]


_OPENERS = {}


class FenceError(ValueError):
    """許していない URL・リダイレクト・空の許可の一覧（決定的な失敗なので再試行しない）。"""


def _opener_for(allowed):
    """許す一覧から、リダイレクトの先も同じ一覧で確かめる opener を作る（一覧ごとに 1 つ）。"""
    key = tuple(allowed)
    if key not in _OPENERS:
        _OPENERS[key] = common.guarded_opener(list(key))
    return _OPENERS[key]


def retry_after_seconds(value, k):
    """Retry-After（秒数または HTTP の日付）を待つ秒に直す。読めなければ 8×(k+1) 秒。上限 60 秒。"""
    if value:
        try:
            return min(60, max(0, int(value)))
        except ValueError:
            try:
                dt = email.utils.parsedate_to_datetime(value)
                return min(60, max(0, int((dt - datetime.datetime.now(dt.tzinfo)).total_seconds())))
            except (TypeError, ValueError):
                pass
    return min(60, 8 * (k + 1))


def get(url, tries=4, allowed=None):
    """許した接頭辞の URL だけを開く。allowed を省くと 4 つの API。opener は allowed から中で作る（一覧と柵が崩れない）。

    ★ 空の一覧は何も許さない（既定に広がらない）。400・404・410 は None（その情報源に記録なし・errors に残らない）。
    ★ 2026-09-30 の取得を回した後に、この形に直した（decisions.md 判断 9・12）。既定の引数での振る舞いは回した版と同じ。
    """
    allowed = ALLOWED if allowed is None else list(allowed)
    if not allowed:
        raise FenceError("許す URL の一覧が空")
    if not common.allowed_url(url, allowed):
        raise FenceError(f"許していない URL: {url}")
    opener = _opener_for(allowed)
    err = None
    for k in range(tries):
        try:
            with opener.open(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            err = e
            if e.code in (400, 404, 410):
                return None
            wait = retry_after_seconds(e.headers.get("Retry-After"), k)
        except urllib.error.URLError as e:
            if str(e.reason).startswith("許していない先へのリダイレクト"):
                raise FenceError(str(e.reason)) from e
            err = e
            wait = 8 * (k + 1)
        except (TimeoutError, ValueError) as e:
            err = e
            wait = 8 * (k + 1)
        if k < tries - 1:
            time.sleep(wait)
    raise err


def norm(t):
    return re.sub(r"[^a-z0-9ぁ-んァ-ン一-龥]", "", (t or "").lower())


def title_match(a, b):
    """題名の一致（正規化して、短い方の先頭 60 字が、長い方のどこかに含まれるか）。

    正規化で空になる題名（ハングル・キリル文字など）は None を返し、呼び出し側は不一致として扱わない（README の流用の注意）。
    """
    x, y = norm(a), norm(b)
    if not x or not y:
        return None
    s, l = sorted([x, y], key=len)
    return s[:60] in l


def q(doi):
    return urllib.parse.quote(doi, safe="/")


def from_epmc(doi=None, query=None):
    qq = query or f'DOI:"{doi}"'
    d = get(EPMC + "search?" + urllib.parse.urlencode({"query": qq, "format": "json", "resultType": "core", "pageSize": 5},
                                                       quote_via=urllib.parse.quote))
    rs = (d or {}).get("resultList", {}).get("result", [])
    if not rs:
        return None
    r = rs[0]
    return {"title": clean(r.get("title", "")), "text": clean(r.get("abstractText", "")), "n": d.get("hitCount")}


def from_s2(doi):
    d = get(S2 + f"paper/DOI:{q(doi)}?fields=title,abstract")
    if not d:
        return None
    return {"title": clean(d.get("title") or ""), "text": clean(d.get("abstract") or "")}


def from_openalex(doi):
    d = get(OA + f"works/doi:{q(doi)}")
    if not d:
        return None
    inv = d.get("abstract_inverted_index") or {}
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    oa = d.get("open_access") or {}
    return {"title": clean(d.get("title") or d.get("display_name") or ""), "text": " ".join(w for _, w in pos),
            "oa_url": oa.get("oa_url") or "", "oa_status": oa.get("oa_status") or ""}


def from_crossref(doi):
    d = get(CR + f"works/{q(doi)}")
    if not d:
        return None
    m = d.get("message") or {}
    return {"title": clean(" ".join(m.get("title") or [])), "text": clean(m.get("abstract") or "")}


SOURCES = {"epmc": from_epmc, "s2": from_s2, "openalex": from_openalex, "crossref": from_crossref}


def load_records():
    import openpyxl
    got = hashlib.sha256(open(JUDGE_XLSX, "rb").read()).hexdigest()
    if got != JUDGE_SHA:
        raise SystemExit(f"入力の xlsx の SHA-256 が違う（{got}）。止まる")
    wb = openpyxl.load_workbook(JUDGE_XLSX, data_only=True, read_only=True)
    out = []
    for sheet, kcol, tcol in (("判定シート", "ID", "論文タイトル"), ("追加候補", "候補番号", "題名（書誌の記録）")):
        rows = list(wb[sheet].iter_rows(values_only=True))
        hi = next(i for i, r in enumerate(rows) if r and r[0] == kcol)
        head = list(rows[hi])
        ki, ti, di = head.index(kcol), head.index(tcol), head.index("DOI")
        for r in rows[hi + 1:]:
            if not r or not r[ki]:
                continue
            m = re.search(r"10\.\d{4,9}/\S+", str(r[di] or ""))
            out.append((str(r[ki]), m.group(0).rstrip(".,;)") if m else None, str(r[ti] or "")))
    return out


# DOI の無い 4 件（design.md §0.2）: 題名で Europe PMC を 1 回ずつ（S12-24 は Europe PMC の前刷りの識別子）
NO_DOI_QUERY = {"S12-24": "EXT_ID:PPR268625 AND SRC:PPR"}


def fetch(items, abs_dir):
    """items: [(鍵, DOI or None, 題名)]。情報源ごとに 1 本のスレッドで、1 秒に 1 回。"""
    res = {k: {} for k, _, _ in items}
    lock = threading.Lock()
    errors = []

    def worker(src, fn):
        for key, doi, title in items:
            try:
                if doi:
                    got = fn(doi)
                elif src == "epmc":
                    qq = NO_DOI_QUERY.get(key) or 'TITLE:"%s"' % re.sub(r'["\\]', " ", title)[:200]
                    got = from_epmc(query=qq)
                else:
                    got = None
            except Exception as e:  # noqa: BLE001  情報源の失敗は記録して続ける（件数を推測で埋めない）
                with lock:
                    errors.append({"key": key, "source": src, "error": type(e).__name__ + ": " + str(e)[:120]})
                got = None
            with lock:
                res[key][src] = got
            time.sleep(1.1)

    ths = [threading.Thread(target=worker, args=(s, f)) for s, f in SOURCES.items()]
    for t in ths:
        t.start()
    for t in ths:
        t.join()

    bib, abstracts = [], {}
    for key, doi, title in items:
        per = res[key]
        store = {}
        rec = {"key": key, "doi": doi, "title": title[:300], "sources_with_text": [], "title_mismatch": [], "len": {}}
        for src in SOURCES:
            g = per.get(src)
            if not g:
                continue
            tm = title_match(title, g.get("title"))
            if tm is False:
                rec["title_mismatch"].append(src)
                if not doi:
                    continue  # 題名で引いたものは、題名が一致したときだけ使う
            if g.get("text"):
                rec["sources_with_text"].append(src)
                rec["len"][src] = len(g["text"])
                common.merge_abstract(store, key, g["text"])
            if src == "openalex":
                rec["oa_url"] = g.get("oa_url", "")
                rec["oa_status"] = g.get("oa_status", "")
        text = store.get(key) or ""
        rec["chars"] = len(text)
        bib.append(rec)
        abstracts[key] = text
    return bib, abstracts, errors


def main():
    mode, bib_path, abs_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    common.ensure_outside_repo(abs_dir)
    if common.is_inside(bib_path, abs_dir) or not common.is_inside(bib_path, common.repo_root()):
        raise SystemExit("書誌の JSON は repo の中に置く")
    if mode == "records":
        items = load_records()
    elif mode == "theory":
        items = [(k, d, t) for k, d, t in THEORY]
    elif mode == "theory2":
        items = [(k, d, t) for k, d, t in THEORY2]
    else:
        raise SystemExit("mode は records・theory・theory2 のどれか")
    executed = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    bib, abstracts, errors = fetch(items, abs_dir)
    os.makedirs(abs_dir, exist_ok=True)
    abs_path = os.path.join(abs_dir, os.path.basename(bib_path).replace(".json", "_abs.json"))
    common.write_pair(bib_path, abs_path,
                      {"executed": executed, "mode": mode, "input_sha256": JUDGE_SHA if mode == "records" else None,
                       "n": len(bib), "errors": errors, "records": bib},
                      abstracts)
    n_text = sum(1 for b in bib if b["chars"])
    print(f"{mode}: {len(bib)} 件・抄録あり {n_text} 件・エラー {len(errors)} 件 → {bib_path}（抄録は {abs_path}）")


if __name__ == "__main__":
    main()
