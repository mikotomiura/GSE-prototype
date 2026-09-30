"""S-02: 11 件（＋ N-06 のデータセット 2 件）の書誌と抄録を取る（design.md §2.2 の 1・2）。

書誌（と訂正の関係・オープンアクセスの有無）だけを出力 JSON に書く。抄録は第 2 引数のディレクトリ（repo の外）にだけ書く。
連絡先は送らない（mailto を付けない）。
使い方: python fetch_meta.py <出力 JSON> <抄録の保存先（repo の外）>
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (literature-search script)"}
DOIS = ["10.1108/jeim-10-2025-1027", "10.1038/s41598-026-45402-7", "10.1016/j.actpsy.2026.107396",
        "10.1007/s00146-025-02764-2", "10.1016/j.techsoc.2026.103553", "10.1007/s10639-024-13198-6",
        "10.31152/jb.2025.12.10.6.297", "10.5281/zenodo.22838191", "10.1057/s41599-024-04018-w",
        "10.1108/JSM-03-2023-0115", "10.3389/fpubh.2024.1343932"]
DATASETS = ["10.21227/rz27-ze05", "10.21227/94rd-ny74"]


def get_json(url):
    for k in range(4):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(5 * (k + 1))
        except Exception:  # noqa: BLE001
            time.sleep(5 * (k + 1))
    return None


def clean(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t or "")).strip()


def crossref(doi):
    d = get_json("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"))
    if not d:
        return {}, ""
    m = d["message"]
    rel = {k: [x.get("id") for x in v] for k, v in (m.get("relation") or {}).items()}
    upd = [{"type": u.get("type"), "doi": u.get("DOI")} for u in (m.get("update-to") or [])]
    meta = {
        "title": (m.get("title") or [""])[0], "container": (m.get("container-title") or [""])[0],
        "issued": (m.get("issued") or {}).get("date-parts", [[None]])[0],
        "authors": [f'{a.get("family", "")} {a.get("given", "")}'.strip() for a in m.get("author", [])],
        "affiliations_first3": [[x.get("name") for x in a.get("affiliation", [])] for a in m.get("author", [])[:3]],
        "type": m.get("type"), "license": [x.get("URL") for x in m.get("license", [])],
        "relation": rel, "update_to": upd, "links": [x.get("URL") for x in m.get("link", [])][:3],
    }
    return meta, clean(m.get("abstract", ""))


def epmc(doi):
    q = urllib.parse.quote(f'DOI:"{doi}"')
    d = get_json(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&format=json&resultType=core")
    rs = (d or {}).get("resultList", {}).get("result", [])
    if not rs:
        return {}, ""
    r = rs[0]
    return {"pmcid": r.get("pmcid"), "isOpenAccess": r.get("isOpenAccess"), "epmc_affiliation": (r.get("affiliation") or "")[:300]}, clean(r.get("abstractText", ""))


def s2(doi):
    d = get_json(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{urllib.parse.quote(doi, safe='/')}?fields=title,abstract,openAccessPdf,venue,year")
    if not d:
        return {}, ""
    return {"s2_openAccessPdf": (d.get("openAccessPdf") or {}).get("url")}, clean(d.get("abstract", ""))


def datacite(doi):
    d = get_json("https://api.datacite.org/dois/" + urllib.parse.quote(doi, safe="/"))
    if not d:
        return {}, ""
    a = d["data"]["attributes"]
    desc = " ".join(clean(x.get("description", "")) for x in a.get("descriptions", []))
    meta = {"title": (a.get("titles") or [{}])[0].get("title"), "publisher": a.get("publisher"),
            "year": a.get("publicationYear"), "creators": [c.get("name") for c in a.get("creators", [])],
            "resourceType": (a.get("types") or {}).get("resourceTypeGeneral"), "url": a.get("url"),
            "relatedIdentifiers": [(r.get("relationType"), r.get("relatedIdentifier")) for r in a.get("relatedIdentifiers", [])][:10]}
    return meta, desc


def main(out, abs_dir):
    if os.path.exists(out):
        sys.exit(f"出力先が既にある（上書きしない）: {out}")
    os.makedirs(abs_dir, exist_ok=True)
    recs, abstracts = [], {}
    for doi in DOIS:
        meta, ab = crossref(doi)
        src = "crossref" if ab else ""
        if not meta:
            meta, ab = datacite(doi)
            src = "datacite" if ab else ""
        m2, ab2 = epmc(doi)
        meta.update(m2)
        if not ab and ab2:
            ab, src = ab2, "europepmc"
        m3, ab3 = s2(doi)
        meta.update(m3)
        if not ab and ab3:
            ab, src = ab3, "semanticscholar"
        abstracts[doi] = ab
        recs.append({"doi": doi, **meta, "abstract_source": src or "none", "abstract_chars": len(ab)})
        print(doi, "|", meta.get("title", "")[:70], "|", src or "NO ABSTRACT", len(ab), "| upd:", meta.get("update_to"), "| rel:", meta.get("relation"), flush=True)
        time.sleep(1.5)
    for doi in DATASETS:
        meta, desc = datacite(doi)
        abstracts[doi] = desc
        recs.append({"doi": doi, **meta, "abstract_source": "datacite-description", "abstract_chars": len(desc)})
        print(doi, "|", meta.get("title"), "|", len(desc), flush=True)
        time.sleep(1)
    with open(os.path.join(abs_dir, "s02_abstracts.json"), "w", encoding="utf-8") as fh:
        json.dump(abstracts, fh, ensure_ascii=False, indent=1)
    with open(out, "x", encoding="utf-8") as fh:
        json.dump({"meta": {"executed": time.strftime("%Y-%m-%d %H:%M:%S %z"), "design": "design.md §2"},
                   "records": recs}, fh, ensure_ascii=False, indent=1)


RERUN_BLOCKED = ("この版は 2026-09-29 に実行した版の記録で、そのまま再実行しない（evidence/README.md・decisions.md 判断 16）。"
                 "流用するときは evidence/common.py の関数（抄録を空で上書きしない・repo の外の確認・排他的な作成・URL の許可）で直した新しいスクリプトを作る。")


if __name__ == "__main__":
    sys.exit(RERUN_BLOCKED)  # 実行した時の呼び出し: main(*sys.argv[1:3])
