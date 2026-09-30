"""259 件の間引きの候補の組を出す（design.md §7・2026-09-30 固定）。

★ 候補の組を出すだけで、分けるのはメイン（§7.3）。範囲の判断（E1〜E3）はしない。
★ 抄録は前タスクが scratchpad に置いたものを読むだけで、repo に写さない（repo には書誌・組・抄録から取った数と国名だけ）。
★ 連絡先（メールアドレス）を送らない。

使い方（このディレクトリで。openpyxl が要る）:
  uv run --with openpyxl python dedup.py meta  --out dedup/meta_2026-09-30.json --cache <scratchpad の dir>
  uv run --with openpyxl python dedup.py pairs --meta dedup/meta_2026-09-30.json --abs <抄録の JSON> \
      --out dedup/pairs_2026-09-30.json --bundle <scratchpad の md>
"""
import argparse
import datetime
import difflib
import hashlib
import itertools
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
STEER = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(STEER, "20260929-ai-fatigue-surveys", "evidence"))
from common import allowed_url, ensure_outside_repo, guarded_opener  # noqa: E402

JUDGE_XLSX = os.path.join(STEER, "20260930-ai-fatigue-judge-file", "archive", "judge",
                          "AI_fatigue_judge-sheet_2026-09-30_judge1.xlsx")
JUDGE_SHA = "6984472edeef3794a9ed075076568aaca8373c4fb675afba608cdba280e6c883"
# ★ 2026-10-01 に判定者用ファイルを作り直した（判断 8）ので、入力の版（上の SHA-256）は作業ツリーに無い。git の記録から読む
JUDGE_COMMIT = "d9354547"
ABS_RUN_ID = "1980b7a2a275414d973174c6c3d918e3"

UA = {"User-Agent": "gse-protocol-dedup/0.1"}
ALLOWED = ["https://api.crossref.org/works/", "https://api.datacite.org/dois/"]
OPENER = guarded_opener(ALLOWED)

# ---- §7.2 の規則（固定の値） ----
REL_CROSSREF = {"is-preprint-of", "has-preprint", "is-version-of", "has-version", "is-identical-to", "is-same-as",
                "is-manifestation-of", "has-manifestation", "is-translation-of", "has-translation"}
REL_DATACITE = {"isversionof", "hasversion", "ispreviousversionof", "isnewversionof", "isidenticalto",
                "isvariantformof", "isoriginalformof", "istranslationof"}
PREPRINT_PREFIXES = ("10.21203/", "10.2139/", "10.31234/", "10.31219/", "10.31235/", "10.35542/", "10.20944/",
                     "10.22541/", "10.1101/", "10.48550/", "10.5281/", "10.36227/", "10.32388/")
TITLE_HIGH, TITLE_LOW = 0.85, 0.60
SAMPLE_NOUNS = (r"participants?|students?|respondents?|employees?|workers?|teachers?|nurses?|physicians?|users?|"
                r"adults?|individuals?|learners?|undergraduates?|professionals?|clinicians?|people|subjects?|"
                r"managers?|doctors?|residents?|staff|educators?|faculty|consumers?|customers?|academics?|"
                r"学生|参加者|回答者|従業員|看護師|医師|教員")
COUNTRIES = ["china", "chinese", "korea", "korean", "japan", "japanese", "india", "indian", "pakistan", "pakistani",
             "philippines", "filipino", "indonesia", "indonesian", "malaysia", "malaysian", "vietnam", "vietnamese",
             "thailand", "thai", "saudi", "arabia", "uae", "emirates", "egypt", "egyptian", "turkey", "turkish",
             "iran", "iranian", "israel", "israeli", "nigeria", "nigerian", "ghana", "kenya", "south africa",
             "united states", "usa", "u.s.", "american", "canada", "canadian", "mexico", "brazil", "brazilian",
             "chile", "colombia", "peru", "spain", "spanish", "portugal", "italy", "italian", "germany", "german",
             "france", "french", "netherlands", "dutch", "belgium", "switzerland", "swiss", "austria", "poland",
             "polish", "uk", "united kingdom", "british", "england", "ireland", "sweden", "swedish", "norway",
             "finland", "denmark", "australia", "australian", "new zealand", "singapore", "taiwan", "taiwanese",
             "hong kong", "bangladesh", "sri lanka", "nepal", "jordan", "lebanon", "qatar", "kuwait", "oman",
             "morocco", "tunisia", "algeria", "ethiopia", "romania", "greece", "czech", "hungary", "ukraine",
             "russia", "kazakhstan", "uzbekistan", "cyprus", "croatia", "serbia", "slovenia", "slovakia", "estonia",
             "latvia", "lithuania", "中国", "韓国", "日本"]


def now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec="seconds")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def norm_title(t):
    t = unicodedata.normalize("NFKC", t or "").lower()
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def title_ratio(a, b):
    a, b = norm_title(a), norm_title(b)
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def norm_name(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z぀-ヿ一-鿿]", "", s.lower())


def label_families(label):
    """事実のファイルでの表記（例: 'Honggang W, Khoso AK, Althubyani AR 2026'）から姓らしい語を取る（書誌が無いときだけ使う）。"""
    out = []
    for part in re.split(r"[,;、]| and | & |ほか|et al\.?", label or ""):
        toks = [t for t in re.split(r"\s+", part.strip()) if t]
        toks = [t for t in toks if not re.fullmatch(r"[A-Z]{1,3}\.?|\d{4}|[A-Z]\.([A-Z]\.)*", t)]
        if toks:
            out.append(norm_name(toks[0]))
    return [x for x in out if len(x) >= 2]


def is_preprint_doi(doi):
    return bool(doi) and doi.lower().startswith(PREPRINT_PREFIXES)


def sample_numbers(text):
    """抄録から標本の数らしい整数（30 以上）を取る。"""
    t = text or ""
    nums = set()
    for m in re.finditer(r"\b[Nn]\s*=\s*([\d,]{2,7})", t):
        nums.add(m.group(1))
    pat = rf"(\d[\d,]{{1,6}})\s+(?:\S+\s+){{0,3}}?(?:{SAMPLE_NOUNS})"
    for m in re.finditer(pat, t, flags=re.I):
        nums.add(m.group(1))
    out = set()
    for n in nums:
        try:
            v = int(n.replace(",", ""))
        except ValueError:
            continue
        if 30 <= v <= 1_000_000 and not (1900 <= v <= 2100):
            out.add(v)
    return out


def countries(text):
    t = " " + (text or "").lower() + " "
    got = set()
    for c in COUNTRIES:
        if re.search(r"(?<![a-z])" + re.escape(c) + r"(?![a-z])", t):
            got.add(c)
    return got


# ---- 入力 ----
def judge_input():
    """間引きの入力（判定者用ファイルの SHA-256 が JUDGE_SHA の版）を開く。
    作業ツリーの版が違えば（2026-10-01 に作り直した後）、JUDGE_COMMIT の記録から読み、同じ SHA-256 かを確かめる。"""
    import io
    import subprocess
    import openpyxl
    data = open(JUDGE_XLSX, "rb").read()
    if hashlib.sha256(data).hexdigest() != JUDGE_SHA:
        repo = os.path.dirname(STEER)
        rel = os.path.relpath(JUDGE_XLSX, repo).replace(os.sep, "/")
        data = subprocess.run(["git", "-C", repo, "show", f"{JUDGE_COMMIT}:{rel}"], capture_output=True, check=True).stdout
        if hashlib.sha256(data).hexdigest() != JUDGE_SHA:
            sys.exit("判定者用ファイルの入力の版（作業ツリー・git の記録とも）の SHA-256 が固定値と違う")
    return openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)


def load_259():
    wb = judge_input()
    recs = []
    for r in wb["判定シート"].iter_rows(min_row=5, values_only=True):
        if r[0]:
            recs.append(dict(key=r[0], sheet="DB", title=r[1] or "", label=r[2] or "", year=r[3], journal=r[4] or "",
                             pubtype=r[5] or "", doi=(r[6] or "").strip().lower() if r[6] and str(r[6]).startswith("10.") else None))
    for r in wb["追加候補"].iter_rows(min_row=5, values_only=True):
        if r[0]:
            recs.append(dict(key=r[0], sheet="候補", title=r[3] or "", label=r[2] or "", year=r[4], journal=r[5] or "",
                             pubtype="", doi=(r[6] or "").strip().lower() or None))
    if len(recs) != 259:
        sys.exit(f"259 件ではない: {len(recs)}")
    return recs


def get_json(url, tries=5):
    if not allowed_url(url, ALLOWED):
        raise ValueError(f"許していない URL: {url}")
    wait = 2.0
    for i in range(tries):
        try:
            with OPENER.open(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503, 504) and i < tries - 1:
                time.sleep(wait)
                wait *= 2
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if i < tries - 1:
                time.sleep(wait)
                wait *= 2
                continue
            raise
    return None


def meta_for(doi):
    """Crossref → DataCite の順に書誌を取る（抄録は取らない）。"""
    m = get_json("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"))
    if m and m.get("message"):
        x = m["message"]
        rel = []
        for typ, items in (x.get("relation") or {}).items():
            for it in items if isinstance(items, list) else [items]:
                if it.get("id-type") == "doi":
                    rel.append([typ.lower(), (it.get("id") or "").lower()])
        return dict(source="crossref", type=x.get("type"), title=(x.get("title") or [""])[0],
                    container=(x.get("container-title") or [""])[0],
                    issued=(x.get("issued") or {}).get("date-parts"),
                    authors=[[a.get("family") or a.get("name") or "", a.get("given") or ""] for a in x.get("author", [])],
                    relations=rel)
    d = get_json("https://api.datacite.org/dois/" + urllib.parse.quote(doi, safe="/"))
    if d and d.get("data"):
        at = d["data"]["attributes"]
        rel = [[(r.get("relationType") or "").lower(), (r.get("relatedIdentifier") or "").lower()]
               for r in at.get("relatedIdentifiers") or [] if (r.get("relatedIdentifierType") or "").upper() == "DOI"]
        return dict(source="datacite", type=(at.get("types") or {}).get("resourceTypeGeneral"),
                    title=(at.get("titles") or [{}])[0].get("title", ""), container=at.get("publisher") or "",
                    issued=at.get("publicationYear"),
                    authors=[[c.get("familyName") or c.get("name") or "", c.get("givenName") or ""]
                             for c in at.get("creators", [])],
                    relations=rel)
    return None


def families(rec, meta):
    m = meta.get(rec["key"]) or {}
    fam = [norm_name(a[0].split(",")[0] if "," in a[0] else a[0]) for a in m.get("authors", []) if a and a[0]]
    fam = [f for f in fam if len(f) >= 2]
    return fam or label_families(rec["label"])


# ---- 検出（§7.2） ----
def detect(recs, meta, abstracts):
    by_doi = {r["doi"]: r["key"] for r in recs if r["doi"]}
    fam = {r["key"]: families(r, meta) for r in recs}
    nums = {r["key"]: sample_numbers(abstracts.get(r["key"], "")) for r in recs}
    ctry = {r["key"]: countries(abstracts.get(r["key"], "")) for r in recs}
    year = {}
    for r in recs:
        try:
            year[r["key"]] = int(str(r["year"])[:4])
        except (TypeError, ValueError):
            year[r["key"]] = None
    rel_pairs = set()
    for r in recs:
        m = meta.get(r["key"]) or {}
        for typ, target in m.get("relations", []):
            ok = typ in REL_CROSSREF if m.get("source") == "crossref" else typ in REL_DATACITE
            if ok and target in by_doi and by_doi[target] != r["key"]:
                rel_pairs.add(tuple(sorted((r["key"], by_doi[target]))) + (typ,))
    pairs = {}

    def add(a, b, tag, **info):
        k = tuple(sorted((a, b)))
        p = pairs.setdefault(k, dict(a=k[0], b=k[1], perspectives=[], info={}))
        if tag not in p["perspectives"]:
            p["perspectives"].append(tag)
        p["info"].update(info)

    for a, b, typ in rel_pairs:
        add(a, b, "P1", relation=typ)
    keyed = {r["key"]: r for r in recs}
    for ra, rb in itertools.combinations(recs, 2):
        a, b = ra["key"], rb["key"]
        ratio = title_ratio(ra["title"], rb["title"])
        shared = sorted(set(fam[a]) & set(fam[b]))
        first_same = bool(fam[a] and fam[b] and fam[a][0] == fam[b][0])
        ydiff_ok = year[a] is not None and year[b] is not None and abs(year[a] - year[b]) <= 1
        if ratio >= TITLE_HIGH or (ratio >= TITLE_LOW and shared):
            add(a, b, "P2", title_ratio=round(ratio, 3))
        if len(shared) >= 2 or (first_same and ydiff_ok):
            add(a, b, "P3", shared_authors=shared, first_author_same=first_same)
        if (is_preprint_doi(ra["doi"]) or is_preprint_doi(rb["doi"])) and ratio >= TITLE_LOW:
            add(a, b, "P4", title_ratio=round(ratio, 3))
        same_n = sorted(nums[a] & nums[b])
        if same_n and ((ctry[a] & ctry[b]) or shared):
            add(a, b, "P5", same_n=same_n, shared_countries=sorted(ctry[a] & ctry[b]), shared_authors=shared)
    for p in pairs.values():
        p["info"].setdefault("title_ratio", round(title_ratio(keyed[p["a"]]["title"], keyed[p["b"]]["title"]), 3))
        p["info"].setdefault("shared_authors", sorted(set(fam[p["a"]]) & set(fam[p["b"]])))
        p["info"]["n_a"], p["info"]["n_b"] = sorted(nums[p["a"]]), sorted(nums[p["b"]])
        p["info"]["countries_a"], p["info"]["countries_b"] = sorted(ctry[p["a"]]), sorted(ctry[p["b"]])
        p["perspectives"].sort()
    return sorted(pairs.values(), key=lambda p: (p["a"], p["b"]))


def author_ids(meta_rec):
    """（姓, 名の頭文字）の集合。判断 4: 観点 P3 だけで当たった組は、この単位で 2 名以上が重なるときだけ読む。"""
    out = set()
    for fam, giv in (meta_rec or {}).get("authors", []):
        f = norm_name(fam)
        if len(f) >= 2:
            out.add((f, norm_name(giv)[:1]))
    return out


def refine(pairs, meta):
    """判断 4（2026-09-30・実行後の逸脱）: P3 だけの組のうち、姓＋名の頭文字で 2 名以上が重ならない組を外す（keep, drop）。"""
    keep, drop = [], []
    for p in pairs:
        if p["perspectives"] == ["P3"] and len(author_ids(meta.get(p["a"])) & author_ids(meta.get(p["b"]))) < 2:
            drop.append([p["a"], p["b"]])
        else:
            keep.append([p["a"], p["b"]])
    return keep, drop


def load_abstracts(path):
    d = json.load(open(path, encoding="utf-8"))
    if d.get("run_id") != ABS_RUN_ID:
        sys.exit("抄録のファイルの run_id が前タスクの記録と違う")
    return d["abstracts"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["meta", "pairs", "refine"])
    ap.add_argument("--pairs")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cache")
    ap.add_argument("--meta")
    ap.add_argument("--abs")
    ap.add_argument("--bundle")
    a = ap.parse_args(argv)
    if a.cmd == "refine":
        meta = json.load(open(a.meta, encoding="utf-8"))["meta"]
        keep, drop = refine(json.load(open(a.pairs, encoding="utf-8"))["pairs"], meta)
        with open(a.out, "x", encoding="utf-8", newline="\n") as f:
            json.dump(dict(executed=now(), rule="判断 4: P3 だけの組は姓＋名の頭文字で 2 名以上", keep=keep, drop=drop),
                      f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("keep", len(keep), "drop", len(drop))
        return 0
    recs = load_259()
    if a.cmd == "meta":
        out, errors = {}, []
        for r in recs:
            if not r["doi"]:
                continue
            try:
                out[r["key"]] = meta_for(r["doi"])
            except Exception as e:  # 失敗は欠測として残す
                errors.append([r["key"], f"{type(e).__name__}: {e}"])
            time.sleep(0.25)
        with open(a.out, "x", encoding="utf-8", newline="\n") as f:
            json.dump(dict(executed=now(), input_sha256=JUDGE_SHA, n=len(recs),
                           n_with_doi=sum(1 for r in recs if r["doi"]), errors=errors, meta=out),
                      f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("meta", len(out), "errors", len(errors))
        return 0
    meta = json.load(open(a.meta, encoding="utf-8"))["meta"]
    abstracts = load_abstracts(a.abs)
    pairs = detect(recs, meta, abstracts)
    with open(a.out, "x", encoding="utf-8", newline="\n") as f:
        json.dump(dict(executed=now(), input_sha256=JUDGE_SHA, abs_run_id=ABS_RUN_ID, n_pairs=len(pairs), pairs=pairs),
                  f, ensure_ascii=False, indent=1)
        f.write("\n")
    if a.bundle:
        ensure_outside_repo(a.bundle)
        keyed = {r["key"]: r for r in recs}
        with open(a.bundle, "x", encoding="utf-8") as f:
            for i, p in enumerate(pairs, 1):
                f.write(f"## 組 {i}: {p['a']} ― {p['b']}（観点 {'・'.join(p['perspectives'])}）\n\n")
                for k in (p["a"], p["b"]):
                    r, m = keyed[k], meta.get(k) or {}
                    au = "; ".join(" ".join(x for x in au if x) for au in m.get("authors", [])[:8]) or r["label"]
                    f.write(f"### {k}（{r['sheet']}）\n- 題名: {r['title']}\n- 著者: {au}\n- 年・誌: {r['year']}・{r['journal']}\n"
                            f"- DOI: {r['doi']}\n- 型: {m.get('type')}・関係: {m.get('relations')}\n\n"
                            f"抄録: {abstracts.get(k) or '（抄録なし）'}\n\n")
    print("pairs", len(pairs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
