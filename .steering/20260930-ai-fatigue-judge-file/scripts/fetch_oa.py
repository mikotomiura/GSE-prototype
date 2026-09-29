"""判定者用ファイルの DOI（DB 34 件＋追加候補）について、OpenAlex の open_access を 1 件ずつ取る（design.md「判定者用ファイル」3）。

★ 無料の情報源（OpenAlex の `/works/doi:` の 1 件の取得）だけ。連絡先（メールアドレス）は送らない（`mailto` を付けない）。
★ 書き出すのは DOI・取得の状態・is_oa・oa_status・oa_url だけ（抄録の鍵を持たない）。既存の出力は上書きしない。
使い方: python fetch_oa.py <出力 JSON>
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import judge_xlsx as J  # noqa: E402
import candidates as CAND  # noqa: E402

sys.path.insert(0, J.EVID_PREV)
import common  # noqa: E402

ALLOWED = ["https://api.openalex.org/works/"]
OPENER = common.guarded_opener(ALLOWED)
UA = {"User-Agent": "Mozilla/5.0 (literature-search script)"}


def all_dois():
    import openpyxl
    ws = openpyxl.load_workbook(J.DB_XLSX, read_only=True)["文献DB"]
    out = [str(r[7]) for r in ws.iter_rows(min_row=5, max_row=38, values_only=True) if r[7] and str(r[7]).startswith("10.")]
    out += [J.extract(c)["doi"] for c in CAND.CANDIDATES]
    return list(dict.fromkeys(d for d in out if d))


def fetch(doi):
    url = "https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="/:;()._-")
    if not common.allowed_url(url, ALLOWED):
        return {"status": "ERR 許していない URL"}
    for k in range(3):
        try:
            with OPENER.open(urllib.request.Request(url, headers=UA), timeout=60) as r:
                d = json.loads(r.read())
            oa = d.get("open_access") or {}
            return {"status": "ok", "is_oa": bool(oa.get("is_oa")), "oa_status": oa.get("oa_status"),
                    "oa_url": (oa.get("oa_url") or "")[:400]}
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {"status": "not found"}
            time.sleep(5 * (k + 1))
        except (urllib.error.URLError, TimeoutError, ValueError):
            time.sleep(5 * (k + 1))
    return {"status": "ERR 取得できず"}


def main(out):
    if os.path.exists(out):
        sys.exit(f"出力先が既にある（上書きしない）: {out}")
    recs = {}
    for doi in all_dois():
        recs[doi] = fetch(doi)
        time.sleep(0.5)
    with common.open_exclusive(out) as fh:
        json.dump({"meta": {"executed": time.strftime("%Y-%m-%d %H:%M:%S %z"), "source": "OpenAlex /works/doi:（open_access）"},
                   "records": recs}, fh, ensure_ascii=False, indent=1)
    print(len(recs), "件", {s: sum(1 for r in recs.values() if r["status"] == s) for s in {r["status"] for r in recs.values()}})


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
