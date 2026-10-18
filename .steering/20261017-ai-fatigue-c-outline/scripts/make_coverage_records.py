"""Turn the coverage sample (decision 38, 40) into screening material, and set the screening order of all records.

    records   from <search>/new_records.json (c_search.py merge, outside the repository) write
              <data>/records-coverage.json (the 300 drawn records, in the form of records264.json, population
              "確かめの標本", order unset) and add their abstracts to <data>/meta.json. A record without an abstract
              from the search is looked up once in Crossref by DOI (abstract_source "Crossref"); the rest stay
              without one (the AI screener then judges from the title, GSRR-33). meta.json is copied to
              <data>/../backup/ first; records already in meta.json are not changed.
    long      an "abstract" (from any source) longer than LONG words is the body of the report, not an abstract (2026-10-18: 26
              of the 300, up to 4,174 words; the 264 additional candidates have at most 663). It is not given at the
              title and abstract stage: the abstract is looked up in Crossref, then Semantic Scholar, by DOI, and the
              record is otherwise left without one (title only), with abstract_note saying why.
    retry     ask Crossref and Semantic Scholar again for records still without an abstract, waiting on rate limits;
              a failed lookup is recorded as failed (abstract_lookup), never as "no abstract"
    order     from the screening order list (attachment 4: population,record_id per line) write the position of each
              record into "order" of records264.json and records-coverage.json (both copied to backup first). Stops
              if a record of either file is not in the list, or the list names a record of neither.

Run:
    python3 make_coverage_records.py records --search ~/Documents/TRACE/search/2026-10-18 --data ~/Documents/TRACE/data
    python3 make_coverage_records.py order --data ~/Documents/TRACE/data --order ../registration-attachments/screening-order.csv
"""

import argparse
import csv
import datetime
import html
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

POPULATION = "確かめの標本"
ORIGIN = "確かめの標本 300（確かめの検索・2026-10-18）"


def backup(path):
    bak = path.parent.parent / "backup"
    bak.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(path, bak / f"{path.stem}.before-coverage.{stamp}{path.suffix}")


class LookupError_(Exception):
    """A lookup that failed (network, rate limit): not the same as "no abstract", so the record can be tried again."""


def fetch_json(url, tries=4):
    """JSON from url; None when the service says the record is not there (404); LookupError_ after tries on 429,
    5xx or network errors (waits 5, 10, 20 s)."""
    for t in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            err = f"HTTP {e.code}"
        except Exception as e:
            err = type(e).__name__
        if t < tries - 1:
            time.sleep(5 * 2 ** t)
    raise LookupError_(err)


TAG_ATTR = r"(?:\s[^<>]*)?/?>"   # a tag's attributes never contain < or >, so no text is swallowed


def crossref_abstract(doi):
    d = fetch_json("https://api.crossref.org/works/" + urllib.parse.quote(doi))
    ab = ((d or {}).get("message") or {}).get("abstract") or ""
    ab = re.sub(r"</?jats:[A-Za-z-]+" + TAG_ATTR, " ", ab)   # JATS tags only
    ab = html.unescape(ab)
    # some abstracts hold escaped HTML (&lt;p&gt;), which unescaping turns into tags (2026-10-18: 2 records); only
    # these known tags are removed, never a bare less-than sign
    ab = re.sub(r"</?(?:p|div|br|span|i|b|em|strong|sub|sup|h\d|ul|ol|li)" + TAG_ATTR, " ", ab, flags=re.I)
    return re.sub(r"\s+", " ", ab).strip()


def cmd_records(a):
    rows = [r for r in json.loads((a.search / "new_records.json").read_text(encoding="utf-8")) if r["coverage_sample"]]
    if len(rows) != 300:
        sys.exit(f"{len(rows)} drawn records in new_records.json, expected 300")
    recs = [{"id": r["id"], "title": r["title"], "source": "確かめの検索: " + "・".join(r["sources"]),
             "doi": r["doi"], "year": str(r["year"] or ""), "journal": r["venue"] or "", "group": "",
             "population": POPULATION, "origin": ORIGIN, "order": None} for r in rows]
    out = a.data / "records-coverage.json"
    if out.exists():
        sys.exit(f"{out} exists; nothing written")
    meta_p = a.data / "meta.json"
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    clash = sorted(set(meta) & {r["id"] for r in rows})
    if clash:
        sys.exit(f"meta.json already has coverage records ({clash[:5]}); nothing written")
    added, from_crossref = {}, 0
    for r in rows:
        ab, src = r["abstract"], {"europepmc": "Europe PMC", "openalex": "OpenAlex"}.get(r["abstract_source"], "")
        look = {}
        if not ab and r["doi"]:
            try:
                ab = crossref_abstract(r["doi"])
                look["Crossref"] = "found" if ab else "none"
            except LookupError_ as e:
                look["Crossref"] = f"failed ({e})"
            src = "Crossref" if ab else ""
            from_crossref += bool(ab)
            time.sleep(1)
        added[r["id"]] = {"id": r["id"], "doi": r["doi"], "abstract": ab, "abstract_source": src,
                          "abstract_lookup": look, "authors": "", "oa": [], "errors": [], "done": True}
    backup(meta_p)
    out.write_text(json.dumps(recs, ensure_ascii=False, indent=1), encoding="utf-8")
    meta.update(added)
    meta_p.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")   # as before: one line
    n_ab = sum(bool(v["abstract"]) for v in added.values())
    print(f"wrote {out}: {len(recs)} records; abstracts {n_ab} (Crossref {from_crossref}), without {len(recs) - n_ab}")


LONG = 1000


def s2_abstract(doi):
    d = fetch_json("https://api.semanticscholar.org/graph/v1/paper/DOI:" + urllib.parse.quote(doi) + "?fields=abstract")
    return ((d or {}).get("abstract") or "").strip()


def cmd_long(a):
    meta_p = a.data / "meta.json"
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    long_ = sorted(k for k, v in meta.items() if k.startswith("CS") and len(v.get("abstract", "").split()) > LONG)
    backup(meta_p)
    fixed = {"Crossref": 0, "Semantic Scholar": 0, "none": 0}
    for k in long_:
        m, doi = meta[k], meta[k].get("doi") or ""
        ab, src, look = "", "", {}
        for name, get in (("Crossref", crossref_abstract), ("Semantic Scholar", s2_abstract)):
            if doi:
                try:
                    got = get(doi)
                    look[name] = "found" if got and len(got.split()) <= LONG else ("too long" if got else "none")
                except LookupError_ as e:
                    got, look[name] = "", f"failed ({e})"
                time.sleep(1.5)
                if got and len(got.split()) <= LONG:
                    ab, src = got, name
                    break
        m["abstract"], m["abstract_source"], m["abstract_lookup"] = ab, src, look
        m["abstract_note"] = (f"OpenAlex の抄録の欄は本文だった（{LONG} 語超）ので使わず、{src} の抄録にした。" if ab else
                              f"OpenAlex の抄録の欄は本文だった（{LONG} 語超）ので使わない。ほかに抄録が見つからず、題名だけ。")
        fixed[src or "none"] += 1
    meta_p.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    print(f"long OpenAlex abstracts: {len(long_)}; replaced {fixed}")


def cmd_retry(a):
    """Records of the coverage sample still without an abstract, with a DOI: ask Crossref, then Semantic Scholar,
    again, waiting on rate limits (fetch_json). A lookup that fails again is recorded as failed, not as none."""
    meta_p = a.data / "meta.json"
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    todo = sorted(k for k, v in meta.items() if k.startswith("CS") and not v.get("abstract") and v.get("doi"))
    backup(meta_p)
    got_n, failed = 0, []
    for k in todo:
        m = meta[k]
        look = dict(m.get("abstract_lookup") or {})
        for name, get in (("Crossref", crossref_abstract), ("Semantic Scholar", s2_abstract)):
            try:
                got = get(m["doi"])
                look[name] = "found" if got and len(got.split()) <= LONG else ("too long" if got else "none")
            except LookupError_ as e:
                got, look[name] = "", f"failed ({e})"
            time.sleep(3)
            if got and len(got.split()) <= LONG:
                m["abstract"], m["abstract_source"] = got, name
                m["abstract_note"] = (m.get("abstract_note", "") + f" {name} の抄録（2026-10-18 に取り直した）。").strip()
                got_n += 1
                break
        m["abstract_lookup"] = look
        if any(str(v).startswith("failed") for v in look.values()) and not m.get("abstract"):
            failed.append(k)
    meta_p.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    print(f"retried {len(todo)}: abstracts found {got_n}; still failed (try again later) {len(failed)} {failed[:10]}")


def cmd_order(a):
    order = [row[1] for row in csv.reader(open(a.order, encoding="utf-8")) if row]
    if len(set(order)) != len(order):
        sys.exit("the order list names a record twice")
    pos = {rid: i for i, rid in enumerate(order)}
    files = [a.data / "records264.json", a.data / "records-coverage.json"]
    data = {p: json.loads(p.read_text(encoding="utf-8")) for p in files}
    ids = [r["id"] for d in data.values() for r in d]
    missing = sorted(set(ids) - set(pos))
    extra = sorted(set(pos) - set(ids))
    if missing or extra:
        sys.exit(f"order list and records differ: not in the list {missing[:5]}, not in the records {extra[:5]}")
    for p, d in data.items():
        backup(p)
        for r in d:
            r["order"] = pos[r["id"]]
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1),
                     encoding="utf-8")
    print(f"order set for {len(ids)} records from {a.order}")


def selftest():
    """Offline checks of the lookups: 404 is "none", 429 and network errors become a failed lookup after the tries,
    and the Crossref clean-up keeps a less-than sign."""
    import io
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok &= bool(cond)

    real_open, real_sleep = urllib.request.urlopen, time.sleep
    time.sleep = lambda s: None
    try:
        def opener(code, body=b"{}"):
            def f(url, timeout=None):
                if code == 200:
                    return io.BytesIO(body)
                raise urllib.error.HTTPError(url, code, "x", {}, None)
            return f
        urllib.request.urlopen = opener(404)
        check("404 is no record", fetch_json("u") is None)
        urllib.request.urlopen = opener(429)
        try:
            fetch_json("u")
            check("429 is a failed lookup", False)
        except LookupError_:
            check("429 is a failed lookup", True)
        body = json.dumps({"message": {"abstract": "<jats:p>&lt;p&gt;In (n&lt;p) settings, k&gt;2 &lt;/p&gt;</jats:p>"}})
        urllib.request.urlopen = opener(200, body.encode())
        check("Crossref clean-up keeps a less-than sign", crossref_abstract("10.1/x") == "In (n<p) settings, k>2")
        raw = json.dumps({"message": {"abstract": "<jats:p>a < b and c > d</jats:p>"}})   # malformed: a bare <
        urllib.request.urlopen = opener(200, raw.encode())
        check("a bare less-than sign in JATS survives", crossref_abstract("10.1/y") == "a < b and c > d")
    finally:
        urllib.request.urlopen, time.sleep = real_open, real_sleep
    print("selftest:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


def main():
    if sys.argv[1:] == ["selftest"]:
        selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["records", "long", "retry", "order"])
    ap.add_argument("--search", type=Path)
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--order", type=Path)
    a = ap.parse_args()
    a.data = a.data.expanduser()
    if a.cmd == "records":
        if not a.search:
            ap.error("records needs --search")
        a.search = a.search.expanduser()
        cmd_records(a)
    elif a.cmd == "long":
        cmd_long(a)
    elif a.cmd == "retry":
        cmd_retry(a)
    else:
        if not a.order:
            ap.error("order needs --order")
        cmd_order(a)


if __name__ == "__main__":
    main()
