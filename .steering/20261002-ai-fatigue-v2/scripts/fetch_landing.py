"""無料の API で抄録が取れなかった記録を、出版社のページのメタデータと題名の完全一致で補う（decisions 判断 2）。

- DOI がある記録: https://doi.org/<DOI> を開き、HTML の meta（citation_abstract・dc.description・DC.Description・
  og:description・description・twitter:description）のうち最も長いもの（`MIN_CHARS` 字以上）を使う。
- DOI が無い記録: 題名の **完全一致**（小文字・英数字だけに寄せて比べる）のときだけ、arXiv・Europe PMC・OpenAlex の記録を使う。
  一致しなければ使わない（別の論文の抄録を載せない）。
- ★ メールアドレス・キーを送らない。有料の壁・ログインの先に進まない（ページの meta だけを読む）。
- ★ 抄録の本文は git の外（`common.ABSTRACTS`）。状態は `common.ABSTRACT_STATUS`。
使い方: uv run --with openpyxl python fetch_landing.py ID,ID,...
"""
import hashlib
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import common
from fetch_abstracts import UA, MIN_CHARS, _clean, _get, targets

TIMEOUT = 30
# ★ 「抄録」の meta だけ（og:description・description は切れた文やサイトの説明文を返した・decisions 判断 2）
META_NAMES = ("citation_abstract", "abstract", "dc.description", "dcterms.abstract")


def usable(t, title=""):
    """切れた文（… で終わる）・題名だけ・サイトの定型文を捨てる。"""
    if len(t) < MIN_CHARS or re.search(r"(…|\.\.\.|&hellip;)\s*$", t):
        return False
    # ★ 英字の題名だけに当てる（和文は英数字に寄せるとほぼ空になり、抄録を題名と取り違えた・判断 2）
    if len(norm(title)) >= 20 and norm(t).startswith(norm(title)) and len(norm(t)) < len(norm(title)) + 80:
        return False
    return not re.search(r"Content is hosted by|Read and download full-text here|J-STAGE is an online platform", t)


def norm(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


def landing(doi, title=""):
    req = urllib.request.Request("https://doi.org/" + doi, headers={"User-Agent": UA, "Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read(3_000_000).decode("utf-8", "replace")
            url = r.geturl()
    except Exception as e:
        return "", None, type(e).__name__
    best = ""
    for m in re.finditer(r"<meta\s+[^>]*>", body, re.I):
        tag = m.group(0)
        nm = re.search(r'(?:name|property)\s*=\s*["\']([^"\']+)["\']', tag, re.I)
        ct = re.search(r'content\s*=\s*"([^"]*)"', tag, re.I) or re.search(r"content\s*=\s*'([^']*)'", tag, re.I)
        if nm and ct and nm.group(1).lower() in META_NAMES:
            t = _clean(html.unescape(ct.group(1)))
            if usable(t, title) and len(t) > len(best):
                best = t
    host = urllib.parse.urlparse(url).netloc
    return (best if len(best) >= MIN_CHARS else ""), host, None


def by_title_arxiv(title):
    q = urllib.parse.quote(f'ti:"{title}"')
    req = urllib.request.Request(f"https://export.arxiv.org/api/query?search_query={q}&max_results=5", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            root = ET.fromstring(r.read())
    except Exception:
        return ""
    ns = {"a": "http://www.w3.org/2005/Atom"}
    for e in root.findall("a:entry", ns):
        if norm(e.findtext("a:title", "", ns)) == norm(title):
            return _clean(e.findtext("a:summary", "", ns))
    return ""


def by_title_epmc(title):
    q = urllib.parse.quote(f'TITLE:"{title}"')
    res = _get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&resultType=core&format=json&pageSize=5")
    for r in ((res or {}).get("resultList") or {}).get("result", []) if isinstance(res, dict) else []:
        if norm(r.get("title")) == norm(title):
            return _clean(r.get("abstractText"))
    return ""


def by_title_openalex(title):
    q = urllib.parse.quote(title.replace(",", " "))
    res = _get(f"https://api.openalex.org/works?filter=title.search:{q}&per-page=5&select=title,abstract_inverted_index")
    for w in (res or {}).get("results", []) if isinstance(res, dict) else []:
        if norm(w.get("title")) == norm(title) and w.get("abstract_inverted_index"):
            inv = w["abstract_inverted_index"]
            pos = sorted((p, x) for x, ps in inv.items() for p in ps)
            return _clean(" ".join(x for _, x in pos))
    return ""


def titles():
    import openpyxl
    wb = openpyxl.load_workbook(common.JUDGE_FILE, read_only=True, data_only=True)
    rows = list(wb[common.JUDGE_SHEET].iter_rows(values_only=True))
    out = {r[0]: r[3] for r in rows[common.JUDGE_HEADER_ROW:] if r and r[0]}
    for r in json.load(open(common.SEARCH_RECORDS, encoding="utf-8")):
        if r["reading"] and re.fullmatch(r"R\d\d", r["reading"]):
            out[r["reading"]] = r["title"]
    return out


def main():
    ids = sys.argv[1].split(",")
    store = json.load(open(common.ABSTRACTS, encoding="utf-8"))
    status = json.load(open(common.ABSTRACT_STATUS, encoding="utf-8"))
    doi_of = dict(targets())
    tt = titles()
    if ids == ["--short"]:
        # ★ 600 字未満の抄録は、ほかの API の使える文のうち最も長いものに替える（S2 が JAMA の 1 文の要約を返した・判断 2）
        from fetch_abstracts import from_epmc, from_openalex, from_crossref
        ids = [k for k, v in status.items() if 0 < v["chars"] < 600 and v.get("doi")]
        for i in ids:
            best = (store[i]["text"], store[i]["source"])
            for name, fn in (("Europe PMC", from_epmc), ("OpenAlex", from_openalex), ("Crossref", from_crossref)):
                t = fn(doi_of[i])
                if usable(t, tt.get(i, "")) and len(t) > len(best[0]):
                    best = (t, name)
                time.sleep(0.5)
            print(i, len(store[i]["text"]), "→", best[1], len(best[0]), flush=True)
            store[i] = {"doi": doi_of[i], "source": best[1], "text": best[0]}
            status[i] = {"doi": doi_of[i], "source": best[1], "chars": len(best[0]),
                         "sha256": hashlib.sha256(best[0].encode("utf-8")).hexdigest()}
        ids = []
    for i in ids:
        doi = doi_of.get(i)
        text, src = "", None
        store[i] = {"doi": doi, "source": None, "text": ""}            # ★ 前の結果を残さない
        status[i] = {"doi": doi, "source": None, "chars": 0, "sha256": None}
        if doi:
            text, host, err = landing(doi, tt.get(i, ""))
            src = f"出版社のページ（{host}）" if text else None
            print(i, doi, "→", host, err or "", len(text), flush=True)
        else:
            for name, fn in (("arXiv（題名の完全一致）", by_title_arxiv), ("Europe PMC（題名の完全一致）", by_title_epmc),
                             ("OpenAlex（題名の完全一致）", by_title_openalex)):
                text = fn(tt[i])
                if len(text) >= MIN_CHARS:
                    src = name
                    break
                time.sleep(1)
            print(i, "題名", "→", src, len(text or ""), flush=True)
        if text and len(text) >= MIN_CHARS:
            store[i] = {"doi": doi, "source": src, "text": text}
            status[i] = {"doi": doi, "source": src, "chars": len(text),
                         "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}
        time.sleep(1)
    json.dump(store, open(common.ABSTRACTS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(common.ABSTRACT_STATUS, "w", encoding="utf-8", newline="\n") as f:
        json.dump(status, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("まだ無い:", ", ".join(k for k, v in status.items() if not v["chars"]))


if __name__ == "__main__":
    main()
