"""N-05 の検索式の開発（design.md §2・2026-09-30 固定）: 情報源ごとの件数と、種 25 件の再現を試す。

★ 検索式の開発であってスクリーニングではない。件数と、種の DOI が結果に含まれるかだけを見る（題名・抄録で記録を選ばない）。
★ 取得した記録の ID の一覧は scratchpad（repo の外）に置き、repo には件数・種の再現・一覧の SHA-256 だけを書く。
★ 連絡先（メールアドレス）を送らない。User-Agent は道具名だけ。

使い方（このディレクトリで）:
  python search_dev.py counts  --version v0 --out search_dev_counts_v0.json
  python search_dev.py seeds   --seeds seeds.json --out search_dev_seeds.json
  python search_dev.py fetch   --version v0 --source epmc --store <scratchpad の dir>
  python search_dev.py recall  --version v0 --seeds seeds.json --store <dir> --out search_dev_recall_v0.json
"""
import argparse
import datetime
import hashlib
import http.client
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(os.path.dirname(os.path.dirname(HERE)), "20260929-ai-fatigue-surveys", "evidence")
sys.path.insert(0, PREV)
from common import allowed_url, ensure_outside_repo, guarded_opener  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doi_guard import doi_path  # noqa: E402  ★ 判断 17: DOI の . と .. の区切りを拒む

UA = {"User-Agent": "protocol-search-dev/0.1"}  # ★ 判断 17: 内部の語を外した
ALLOWED = [
    "https://www.ebi.ac.uk/europepmc/webservices/rest/",
    "https://api.semanticscholar.org/graph/v1/",
    "https://api.ies.ed.gov/eric/",
    "https://export.arxiv.org/api/",
    "https://zenodo.org/api/records",
]
OPENER = guarded_opener(ALLOWED)

# ---- design.md §2.1 の概念のブロック（版ごと。v0 は固定の値そのまま） ----
A_V0 = ["artificial intelligence", "AI", "generative AI", "GenAI", "generative artificial intelligence", "ChatGPT",
        "large language model", "large language models", "LLM", "LLMs", "chatbot", "chatbots",
        "conversational agent", "conversational agents", "AI assistant", "AI assistants", "Copilot",
        "machine learning", "AI-assisted", "AI-based", "AI scribe", "ambient AI", "algorithmic management"]
F_V0 = ["fatigue", "fatigued", "exhaustion", "exhausted", "burnout", "burn-out", "burned out", "burnt out",
        "weariness", "tiredness", "depletion", "depleted", "drained"]
B1_V0 = ["AI scribe", "ambient scribe", "ambient listening", "digital scribe", "AI-drafted", "AI-generated draft",
         "draft replies", "coding assistant", "GitHub Copilot", "code generation"]
MATERIAL_V0 = ["fatigue life", "fatigue crack", "fatigue strength", "fatigue damage", "alloy", "weld", "concrete",
               "composite"]

VERSIONS = {
    "v0": dict(A=A_V0, F=F_V0, B1=B1_V0, MATERIAL=MATERIAL_V0),
}


def quote(term):
    """空白・ハイフンを含む語は引用符で囲む（句として検索する）。"""
    return f'"{term}"' if re.search(r"[\s-]", term) else term


def epmc_query(a, f):
    return f"TITLE_ABS:({' OR '.join(map(quote, a))}) AND TITLE_ABS:({' OR '.join(map(quote, f))})"


def s2_query(a, f, neg=None):
    q = f"({' | '.join(map(quote, a))}) + ({' | '.join(map(quote, f))})"
    if neg:
        q += f" + -({' | '.join(map(quote, neg))})"
    return q


def eric_query(a, f):
    def both(terms):
        g = " OR ".join(map(quote, terms))
        return f"(title:({g}) OR description:({g}))"
    return f"{both(a)} AND {both(f)}"


def arxiv_query(a, f):
    def both(terms):
        return "(" + " OR ".join(f"{fld}:{quote(t)}" for t in terms for fld in ("ti", "abs")) + ")"
    return f"{both(a)} AND {both(f)}"


def zenodo_query(a, f):
    return f"({' OR '.join(map(quote, a))}) AND ({' OR '.join(map(quote, f))})"


def zenodo_subqueries(a, f):
    """★ 2026-10-01（decisions.md 判断 11）: Zenodo は A AND F の 1 本の式に 500 を返した。
    F の語ごとの (A) AND (f) に分け、結果の和を取る（A AND (f1 OR … OR fn) と論理的に同じ）。語は変えない。"""
    return [f"({' OR '.join(map(quote, a))}) AND ({quote(t)})" for t in f]


ARXIV_ID_RE = re.compile(r"^(\d{4}\.\d{4,5}|[a-z][a-z.-]*/\d{7})(v\d+)?$", re.I)  # 新旧の arXiv の ID
SPLIT_BY_F = {"zenodo"}  # 取得で F の語ごとに分けて和を取る情報源（判断 11）
ZENODO_PAGE = 25  # 判断 11: Zenodo の匿名の問い合わせの 1 ページの上限


def eric_doi(url):
    """★ 判断 11: ERIC の API は DOI の欄を返さない。url の欄が doi.org のリンクのときだけ DOI とみなす。"""
    if url and re.match(r"^https?://(dx\.)?doi\.org/", url.strip(), re.I):
        return norm_doi(url)
    return None


def queries(version):
    """版の検索式を (source, name, query) の並びで返す。"""
    v = VERSIONS[version]
    A, F, B1, M = v["A"], v["F"], v["B1"], v["MATERIAL"]
    return [
        ("epmc", "main", epmc_query(A, F)),
        ("epmc", "b1", epmc_query(B1, F)),
        ("s2", "main", s2_query(A, F)),
        ("s2", "main_v2", s2_query(A, F, M)),
        ("s2", "b1", s2_query(B1, F)),
        ("eric", "main", eric_query(A, F)),
        ("arxiv", "main", arxiv_query(A, F)),
        ("zenodo", "main", zenodo_query(A, F)),
    ]


# ---- 取得 ----
def get(url, tries=6):
    if not allowed_url(url, ALLOWED):
        raise ValueError(f"許していない URL: {url}")
    wait = 2.0
    for i in range(tries):
        try:
            with OPENER.open(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < tries - 1:
                time.sleep(wait)
                wait *= 2
                continue
            raise
        except (urllib.error.URLError, TimeoutError, http.client.IncompleteRead):  # ★ 判断 11: 途中で切れた応答も再試行
            if i < tries - 1:
                time.sleep(wait)
                wait *= 2
                continue
            raise
    raise RuntimeError("到達しない")


def norm_doi(doi):
    if not doi:
        return None
    d = doi.strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    d = re.sub(r"^doi:\s*", "", d)
    return d or None


def count(source, query):
    """件数だけを 1 回の問い合わせで取る。"""
    if source == "epmc":
        u = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
            {"query": query, "format": "json", "resultType": "idlist", "pageSize": 1})
        return json.loads(get(u))["hitCount"]
    if source == "s2":
        u = "https://api.semanticscholar.org/graph/v1/paper/search/bulk?" + urllib.parse.urlencode(
            {"query": query, "fields": "externalIds"})
        return json.loads(get(u))["total"]
    if source == "eric":
        u = "https://api.ies.ed.gov/eric/?" + urllib.parse.urlencode(
            {"search": query, "format": "json", "rows": 1, "fields": "id"})
        return json.loads(get(u))["response"]["numFound"]
    if source == "arxiv":
        u = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({"search_query": query, "max_results": 1})
        m = re.search(r"<opensearch:totalResults[^>]*>(\d+)<", get(u))
        return int(m.group(1)) if m else None
    if source == "zenodo":
        u = "https://zenodo.org/api/records?" + urllib.parse.urlencode({"q": query, "size": 1})
        return json.loads(get(u))["hits"]["total"]
    raise ValueError(source)


STATS = {}  # ★ 判断 18: 直前の fetch_ids の総数（情報源が返した数）と、受け取った件数（重なりを除く前）


def _stat(total=None, raw=0):
    if total is not None and STATS.get("total") is None:
        STATS["total"] = int(total)
    STATS["raw"] = STATS.get("raw", 0) + raw


def fetch_ids(source, query):
    """結果の ID（DOI を優先。無ければ情報源の ID）を全部取る。戻り値は (ids の集合, 取れた件数)。"""
    ids = set()
    STATS.clear()
    if source == "epmc":
        cursor = "*"
        while True:
            u = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
                {"query": query, "format": "json", "resultType": "lite", "pageSize": 1000, "cursorMark": cursor})
            d = json.loads(get(u))
            res = d.get("resultList", {}).get("result", [])
            _stat(d.get("hitCount"), len(res))
            for x in res:
                ids.add(("doi", norm_doi(x.get("doi"))) if x.get("doi") else ("epmc", f"{x.get('source')}:{x.get('id')}"))
            nxt = d.get("nextCursorMark")
            if not res or not nxt or nxt == cursor:
                break
            cursor = nxt
            time.sleep(0.3)
        return ids
    if source == "s2":
        token = None
        while True:
            p = {"query": query, "fields": "externalIds"}
            if token:
                p["token"] = token
            d = json.loads(get("https://api.semanticscholar.org/graph/v1/paper/search/bulk?" + urllib.parse.urlencode(p)))
            _stat(d.get("total"), len(d.get("data", [])))
            for x in d.get("data", []):
                ext = x.get("externalIds") or {}
                ids.add(("doi", norm_doi(ext["DOI"])) if ext.get("DOI") else ("s2", x.get("paperId")))
                if ext.get("ArXiv"):
                    ids.add(("doi", f"10.48550/arxiv.{ext['ArXiv'].lower()}"))
            token = d.get("token")
            if not token:
                break
            time.sleep(1.2)
        return ids
    if source == "eric":
        start = 0
        while True:
            u = "https://api.ies.ed.gov/eric/?" + urllib.parse.urlencode(
                {"search": query, "format": "json", "rows": 2000, "start": start, "fields": "id,url"})
            d = json.loads(get(u))["response"]
            _stat(d["numFound"], len(d["docs"]))
            for x in d["docs"]:
                ids.add(("eric", x["id"]))
                doi = eric_doi(x.get("url"))  # ★ 判断 11: 種の再現を DOI で数えるため
                if doi:
                    ids.add(("doi", doi))
            start += 2000
            if start >= d["numFound"]:
                break
        return ids
    if source == "arxiv":
        start = 0
        while True:
            u = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
                {"search_query": query, "start": start, "max_results": 500})
            t = get(u)
            got = re.findall(r"<id>https?://arxiv\.org/abs/([^<]+?)(v\d+)?</id>", t)
            for aid, _v in got:
                ids.add(("doi", f"10.48550/arxiv.{aid.lower()}"))
            total = int(re.search(r"<opensearch:totalResults[^>]*>(\d+)<", t).group(1))
            _stat(total, len(got))
            start += 500
            if not got or start >= total:
                break
            time.sleep(3.1)
        return ids
    if source == "zenodo":
        page = 1
        while True:
            # ★ 判断 11: 匿名の問い合わせは 1 ページ 25 件まで（26 以上は 400「Page size cannot be greater than 25」）
            u = "https://zenodo.org/api/records?" + urllib.parse.urlencode(
                {"q": query, "size": ZENODO_PAGE, "page": page})
            d = json.loads(get(u))
            hits = d["hits"]["hits"]
            _stat(d["hits"]["total"], len(hits))
            for h in hits:
                doi = h.get("doi") or (h.get("metadata") or {}).get("doi")
                ids.add(("doi", norm_doi(doi)) if doi else ("zenodo", str(h.get("id"))))
            if not hits or page * ZENODO_PAGE >= d["hits"]["total"]:
                break
            page += 1
            time.sleep(1.0)
        return ids
    raise ValueError(source)


def seed_presence(source, doi):
    """種の DOI が情報源に記録されているか（検索式の外で 1 件ずつ）。True / False / None（確かめる口が無い）。"""
    d = norm_doi(doi)
    if source == "epmc":
        u = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
            {"query": f'DOI:"{d}"', "format": "json", "resultType": "idlist", "pageSize": 1})
        return json.loads(get(u))["hitCount"] > 0
    if source == "s2":
        # ★ 判断 11: Semantic Scholar は arXiv の記録を DataCite の DOI でなく arXiv の ID で持つ
        m = re.match(r"10\.48550/arxiv\.(.+)$", d)
        if m and not ARXIV_ID_RE.match(m.group(1)):  # ★ 判断 18: arXiv の ID の形を確かめてから路に入れる
            raise ValueError(f"arXiv の ID の形でない: {m.group(1)!r}")
        key = f"ARXIV:{urllib.parse.quote(m.group(1), safe='/')}" if m else "DOI:" + doi_path(d)
        u = "https://api.semanticscholar.org/graph/v1/paper/" + key + "?fields=title"
        try:
            get(u, tries=4)
            return True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
            raise
    if source == "arxiv":
        m = re.match(r"10\.48550/arxiv\.(.+)$", d)
        if not m:
            return False
        t = get("https://export.arxiv.org/api/query?" + urllib.parse.urlencode({"id_list": m.group(1)}))
        return "<entry>" in t and "<title>Error</title>" not in t
    if source == "zenodo":
        u = "https://zenodo.org/api/records?" + urllib.parse.urlencode({"q": f'doi:"{d}"', "size": 1})
        return json.loads(get(u))["hits"]["total"] > 0
    return None  # ERIC は DOI で引く口を確かめていない


def now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec="seconds")


def qsha(q):
    return hashlib.sha256(q.encode("utf-8")).hexdigest()


def by_ref(obj):
    """★ 2026-10-01（decisions.md 判断 13）: 記録の JSON では、検索式を SHA-256 で持つ（式の本文は search-dev.md と
    protocol-ja.md の付録 D。前タスクの検査器が JSON の 500 字を超える文字列を抄録の混入として止めるため）。
    `query`（文字列）を `query_sha256` に、`subqueries`（文字列の並び）を `subqueries_sha256` に置き換える。"""
    if isinstance(obj, list):
        return [by_ref(x) for x in obj]
    if not isinstance(obj, dict):
        return obj
    out = {}
    for k, v in obj.items():
        if k == "query" and isinstance(v, str):
            out["query_sha256"] = qsha(v)
        elif k == "subqueries" and isinstance(v, list):
            out["subqueries_sha256"] = [qsha(x) for x in v]
        else:
            out[k] = by_ref(v)
    return out


def write_json(path, obj):
    with open(path, "x", encoding="utf-8", newline="\n") as f:  # 既存の記録を上書きしない
        json.dump(by_ref(obj), f, ensure_ascii=False, indent=1)
        f.write("\n")


def check_store_record(d, version, src, name, q):
    """★ 判断 18（Codex 1 巡目）: 取得の記録の版・情報源・式が、いまのコードの式と同じかを確かめる（違えば止まる）。"""
    if (d.get("version"), d.get("source"), d.get("name")) != (version, src, name):
        raise SystemExit(f"取得の記録の版・情報源が違う: {d.get('version')} {d.get('source')} {d.get('name')}")
    if d.get("query") != q:
        raise SystemExit(f"取得の記録の式がコードの式と違う: {version} {src} {name}")
    if src in SPLIT_BY_F and name == "main":
        v = VERSIONS[version]
        if d.get("subqueries") != zenodo_subqueries(v["A"], v["F"]):
            raise SystemExit(f"取得の記録の分けた式がコードと違う: {version} {src} {name}")


def recall(ids, seeds):
    """種のうち、結果の ID の集合に DOI が含まれるもの。"""
    got = {i[1] for i in ids if i[0] == "doi"}
    return {k: (norm_doi(v["doi"]) in got) for k, v in seeds.items() if v.get("doi")}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["counts", "seeds", "fetch", "recall"])
    ap.add_argument("--version", default="v0")
    ap.add_argument("--source")
    ap.add_argument("--name")
    ap.add_argument("--seeds")
    ap.add_argument("--store")
    ap.add_argument("--out")
    a = ap.parse_args(argv)

    if a.cmd == "counts":
        rows = []
        for src, name, q in queries(a.version):
            try:
                n, err = count(src, q), None
            except Exception as e:  # 失敗は欠測として記録する（0 件に化けさせない）
                n, err = None, f"{type(e).__name__}: {e}"
            row = dict(source=src, name=name, query=q, count=n, error=err, executed=now())
            if src in SPLIT_BY_F and name == "main":  # ★ 判断 17: 分けた式ごとの件数も記録する（和の前の総数）
                v = VERSIONS[a.version]
                subs = zenodo_subqueries(v["A"], v["F"])
                sub_counts = []
                for sq in subs:
                    try:
                        sub_counts.append(count(src, sq))
                    except Exception as e:  # 失敗は欠測（0 件に化けさせない）
                        sub_counts.append(None)
                        print("sub", type(e).__name__, e)
                    time.sleep(1.0)
                row.update(subqueries=subs, sub_counts=sub_counts)
            rows.append(row)
            print(src, name, n, err or "", row.get("sub_counts", ""))
            time.sleep(1.5)
        write_json(a.out, dict(version=a.version, runs=rows))
        return 0

    seeds = json.load(open(a.seeds, encoding="utf-8")) if a.seeds else {}
    if a.cmd == "seeds":
        out = {}
        for src in ("epmc", "s2", "arxiv", "zenodo"):
            out[src] = {}
            for k, v in seeds.items():
                try:
                    out[src][k] = seed_presence(src, v["doi"])
                except Exception as e:
                    out[src][k] = f"ERR {type(e).__name__}: {e}"
                time.sleep(1.2 if src == "s2" else 0.4)
            print(src, sum(1 for x in out[src].values() if x is True), "/", len(seeds))
        write_json(a.out, dict(executed=now(), presence=out))
        return 0

    store = ensure_outside_repo(a.store)
    os.makedirs(store, exist_ok=True)
    if a.cmd == "fetch":
        for src, name, q in queries(a.version):
            if src != a.source or (a.name and name != a.name):
                continue
            t0 = now()
            subs = None
            stats = []  # ★ 判断 18: 総数に届いたか（途中の空ページで黙って止まるのを記録に残す）
            if src in SPLIT_BY_F and name == "main":  # ★ 判断 11: F の語ごとに分けて和を取る
                v = VERSIONS[a.version]
                subs = zenodo_subqueries(v["A"], v["F"])
                ids = set()
                for sq in subs:
                    ids |= fetch_ids(src, sq)
                    stats.append(dict(STATS))
            else:
                ids = fetch_ids(src, q)
                stats.append(dict(STATS))
            for s in stats:
                s["complete"] = s.get("total") is not None and s.get("raw", 0) >= s["total"]
            complete = all(s["complete"] for s in stats)
            path = os.path.join(store, f"ids_{a.version}_{src}_{name}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(dict(version=a.version, source=src, name=name, query=q, subqueries=subs, started=t0,
                               finished=now(), stats=stats, complete=complete, ids=sorted(map(list, ids))), f)
            print(src, name, len(ids), path, "" if complete else "★ 総数に届いていない")
        return 0

    if a.cmd == "recall":
        rows = []
        for src, name, q in queries(a.version):
            path = os.path.join(store, f"ids_{a.version}_{src}_{name}.json")
            if not os.path.exists(path):
                continue
            d = json.load(open(path, encoding="utf-8"))
            check_store_record(d, a.version, src, name, q)  # ★ 判断 18: 版と式がコードと同じ記録だけを数える
            ids = {tuple(x) for x in d["ids"]}
            r = recall(ids, seeds)
            blob = "\n".join(sorted("\t".join(x) for x in ids)).encode("utf-8")
            rows.append(dict(source=src, name=name, query=q, subqueries=d.get("subqueries"),
                             started=d["started"], finished=d["finished"],
                             n_ids=len(ids), n_doi=sum(1 for x in ids if x[0] == "doi"),
                             ids_sha256=hashlib.sha256(blob).hexdigest(),
                             seeds_found=sorted(k for k, v in r.items() if v),
                             seeds_missing=sorted(k for k, v in r.items() if not v)))
            print(src, name, len(ids), "種", sum(r.values()), "/", len(r))
        write_json(a.out, dict(version=a.version, runs=rows))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
