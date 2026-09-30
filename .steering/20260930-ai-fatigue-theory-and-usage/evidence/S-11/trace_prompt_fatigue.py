"""プロンプト疲れの概念分析（検索漏れ候補 No.128・129）の本体の論文を辿る（design.md §1.4・2026-09-30 18:05 に固定）。

Zenodo の記録の API で関連の識別子を見て、題名の語で Crossref・Semantic Scholar を 1 回ずつ引く。
書誌だけを repo の JSON に書き、記録の説明文（抄録に当たる）は repo の外にだけ書く（common.write_pair）。

使い方: python trace_prompt_fatigue.py <書誌の出力 JSON（repo の中）> <抄録の置き場（repo の外のディレクトリ）>
"""
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
EVID = os.path.dirname(HERE)
sys.path.insert(0, EVID)
import fetch_abstracts as F  # noqa: E402  common・clean・get の柵を共有する
common = F.common

ZEN = "https://zenodo.org/api/"
ALLOWED = F.ALLOWED + [ZEN]  # 4 つの API の根に Zenodo の API の根だけを足す（opener は F.get が一覧から作る）

RECORDS = ["21384564", "21384565"]
TITLE_Q = "Concept Analysis of Prompt Fatigue"


def get(url):
    return F.get(url, allowed=ALLOWED)


def main():
    bib_path, abs_dir = sys.argv[1], sys.argv[2]
    common.ensure_outside_repo(abs_dir)
    executed = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    out, texts = {"executed": executed, "zenodo": [], "crossref": [], "s2": []}, {}
    for rid in RECORDS:
        d = get(ZEN + f"records/{rid}") or {}
        m = d.get("metadata") or {}
        out["zenodo"].append({"record": rid, "doi": d.get("doi") or m.get("doi"), "title": F.clean(m.get("title") or "")[:300],
                              "resource_type": (m.get("resource_type") or {}).get("type"),
                              "publication_date": m.get("publication_date"),
                              "related_identifiers": [{"identifier": r.get("identifier"), "relation": r.get("relation"),
                                                       "scheme": r.get("scheme")} for r in (m.get("related_identifiers") or [])],
                              "conceptdoi": d.get("conceptdoi")})
        texts[f"zenodo:{rid}"] = F.clean(m.get("description") or "")
        time.sleep(1.1)
    d = get(F.CR + "works?" + urllib.parse.urlencode({"query.title": TITLE_Q, "rows": 5})) or {}
    for it in (d.get("message") or {}).get("items", []):
        out["crossref"].append({"doi": it.get("DOI"), "title": F.clean(" ".join(it.get("title") or []))[:300],
                                "type": it.get("type"), "year": ((it.get("issued") or {}).get("date-parts") or [[None]])[0][0],
                                "container": " ".join(it.get("container-title") or [])[:200]})
    time.sleep(1.1)
    try:
        d = get(F.S2 + "paper/search?" + urllib.parse.urlencode({"query": TITLE_Q, "fields": "title,year,venue,externalIds", "limit": 5})) or {}
    except urllib.error.HTTPError as e:  # 429 などは「使えなかった」と記録する（件数を推測で埋めない）
        out["s2_error"] = f"HTTP {e.code}"
        d = {}
    for it in d.get("data", []):
        out["s2"].append({"title": F.clean(it.get("title") or "")[:300], "year": it.get("year"), "venue": (it.get("venue") or "")[:200],
                          "doi": (it.get("externalIds") or {}).get("DOI")})
    abs_path = os.path.join(abs_dir, os.path.basename(bib_path).replace(".json", "_abs.json"))
    common.write_pair(bib_path, abs_path, out, texts)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
