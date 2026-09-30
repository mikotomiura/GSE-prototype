"""検索式の開発の雑音の見積もり（design.md §2.4 の 3）: 結果から無作為の 50 件を取り、題名を書誌で引く。

★ 開発の記録であってスクリーニングではない。題名で数えるのは「材料・構造の疲労」「AI が人の疲労を検出・予測するだけ」の
   2 つの種類の件数だけで、どの記録かは repo に書かない（題名の一覧は scratchpad に置く）。
★ 題名は Crossref（無ければ DataCite）の 1 件の取得で引く。連絡先を送らない。

使い方（このディレクトリで）:
  python search_noise.py sample --store <scratchpad の dir> --source epmc --name main --out <scratchpad>/noise_epmc_main.json
  （出力の JSON の "titles" を読み、種類を数えて search-dev.md に件数だけを書く）
"""
import argparse
import hashlib
import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(os.path.dirname(os.path.dirname(HERE)), "20260929-ai-fatigue-surveys", "evidence")
sys.path.insert(0, PREV)
from common import allowed_url, ensure_outside_repo, guarded_opener  # noqa: E402

UA = {"User-Agent": "protocol-search-noise/0.1"}
ALLOWED = ["https://api.crossref.org/works/", "https://api.datacite.org/dois/"]
OPENER = guarded_opener(ALLOWED)
SEED = 20261001
N = 50


def get_json(url):
    if not allowed_url(url, ALLOWED):
        raise ValueError(f"許していない URL: {url}")
    with OPENER.open(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def title_of(doi):
    q = urllib.parse.quote(doi, safe="/")
    try:
        t = get_json("https://api.crossref.org/works/" + q)["message"].get("title") or []
        return ("crossref", t[0] if t else "")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    try:
        t = get_json("https://api.datacite.org/dois/" + q)["data"]["attributes"].get("titles") or []
        return ("datacite", t[0].get("title", "") if t else "")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    return ("none", "")


def sample(ids, n=N, seed=SEED):
    """DOI を持つ ID だけから、並べ替えた順で無作為に n 件（seed 固定）。"""
    dois = sorted(x[1] for x in ids if x[0] == "doi")
    return random.Random(seed).sample(dois, min(n, len(dois)))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sample"])
    ap.add_argument("--store", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--name", default="main")
    ap.add_argument("--version", default="v0")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    store = ensure_outside_repo(a.store)
    out = ensure_outside_repo(a.out)
    d = json.load(open(os.path.join(store, f"ids_{a.version}_{a.source}_{a.name}.json"), encoding="utf-8"))
    ids = {tuple(x) for x in d["ids"]}
    picked = sample(ids)
    rows = []
    for doi in picked:
        src, t = title_of(doi)
        rows.append(dict(doi=doi, via=src, title=t))
        time.sleep(0.3)
    blob = "\n".join(picked).encode("utf-8")
    with open(out, "x", encoding="utf-8") as f:
        json.dump(dict(version=a.version, source=a.source, name=a.name, seed=SEED, n=len(picked),
                       n_doi_population=sum(1 for x in ids if x[0] == "doi"),
                       sample_sha256=hashlib.sha256(blob).hexdigest(), titles=rows), f, ensure_ascii=False, indent=1)
    print(a.source, a.name, len(picked), out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
