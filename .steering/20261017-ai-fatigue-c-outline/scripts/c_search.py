"""The coverage search of this review and the draw of the coverage sample (GSRR-21, GSRR-32, GSRR-39; decision 38).

One search, run once before registration, in three free sources, with the same query (Q6) in title and abstract,
no date limit and no document-type limit:
    openalex   OpenAlex API, filter title_and_abstract.search
    europepmc  Europe PMC REST API, field TITLE_ABS (= TITLE OR ABSTRACT)
    acm        ACM Digital Library web interface (ACM Guide to Computing Literature), fields Title OR Abstract;
               the result list is read in the browser by acm_export.js and posted to `acm-receive`
The exports (raw API pages, with abstracts) are kept outside the repository; only counts, query strings, file names
and SHA-256 go into attachment 3.

Then `merge`:
1. normalises every record (DOI: lower case, without the https://doi.org/ prefix; title: NFKC, lower case, letters
   and digits only);
2. merges records that share a DOI or a normalised title (any source, transitively);
3. removes every merged record that shares a DOI or a normalised title with a record of the source database
   (the 34 exploratory records and the 264 additional candidates);
4. gives the remaining "new records" IDs CS00001... in the order of (normalised title, DOI, source IDs);
5. draws the coverage sample: min(SAMPLE_SIZE, n) IDs with Python random.sample from the sorted IDs, using a
   generator freshly seeded with SAMPLE_SEED; the drawn IDs are returned sorted.

Usage (paths outside the repository):
    python3 c_search.py openalex  <out_dir>
    python3 c_search.py europepmc <out_dir>
    python3 c_search.py acm-receive <out_dir> [--port N]      # then run acm_export.js in an ACM DL tab
    python3 c_search.py merge <out_dir> --records264 <records264.json> --source-db <AI_fatigue_database...xlsx>
    python3 c_search.py selftest
`merge` writes <out_dir>/new_records.json (with abstracts; never committed), <out_dir>/new-records.csv (ID, DOI,
title, year, sources and whether drawn: bibliographic data only; attachment 3) and <out_dir>/search-log.json (counts,
dates and SHA-256, no abstracts; attachment 3), and prints the counts and
the SHA-256 of every file it read or wrote. It stops on a missing export, an export whose record count differs from
the count the source reported, or a source-database file it cannot read.
"""

import argparse
import csv
import datetime
import hashlib
import http.server
import json
import random
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import zipfile
from collections import Counter
import xml.etree.ElementTree as ET
from pathlib import Path

SAMPLE_SIZE = 300
SAMPLE_SEED = 20261022

# --- the query (Q6 of the proposal; decision 38) ------------------------------------------------------------------
FATIGUE = ["fatigue", "exhaustion", "exhausted", "burnout", '"burn-out"', "depletion", "depleted", "tiredness",
           "weariness"]
AI = ['"artificial intelligence"', '"generative AI"', "GenAI", "ChatGPT", '"large language model"',
      '"large language models"', "LLM", "chatbot", '"AI tool"', '"AI tools"', '"AI assistant"', '"AI-assisted"',
      '"AI use"']
TECHNICAL = ['"fatigue life"', '"fatigue crack"', '"fatigue strength"', '"fatigue damage"', '"driver fatigue"',
             '"driver drowsiness"', '"fatigue detection"', '"muscle fatigue"', "battery", "alloy", "welded"]


def group(terms):
    return "(" + " OR ".join(terms) + ")"


def query_openalex():
    return f"{group(FATIGUE)} AND {group(AI)} NOT {group(TECHNICAL)}"


def query_europepmc():
    f = lambda terms: "(" + " OR ".join(f"TITLE_ABS:{t}" for t in terms) + ")"
    return f"{f(FATIGUE)} AND {f(AI)} NOT {f(TECHNICAL)}"


def query_acm():
    f = lambda terms: f"(Title:{group(terms)} OR Abstract:{group(terms)})"
    return f"{f(FATIGUE)} AND {f(AI)} NOT {f(TECHNICAL)}"


QUERIES = {"openalex": query_openalex, "europepmc": query_europepmc, "acm": query_acm}


# --- helpers ------------------------------------------------------------------------------------------------------

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec="seconds")


OPENALEX_KEY_FILE = Path.home() / ".config" / "openalex" / "api_key"


def openalex_headers():
    """The researcher's free OpenAlex API key, read from OPENALEX_KEY_FILE (written by the researcher, never by this
    script), sent as an Authorization header so that it appears in no URL, file or log. Without the file, no key."""
    if OPENALEX_KEY_FILE.exists():
        key = OPENALEX_KEY_FILE.read_text(encoding="utf-8").strip()
        if key:
            return {"Authorization": "Bearer " + key}
    return {}


def get_json(url, tries=4, headers=None):
    for i in range(tries):
        req = urllib.request.Request(url)
        for k, v in (headers or {}).items():
            req.add_unredirected_header(k, v)   # never forwarded to a redirect target
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except Exception as e:  # network errors are retried, then reported
            err = e
            time.sleep(10 * (i + 1))
    raise SystemExit(f"request failed after {tries} tries: {url[:120]} ({str(err)[:200]})")


def write_log(out, source, entry):
    path = out / f"{source}-log.json"
    path.write_text(json.dumps(entry, ensure_ascii=False, indent=1), encoding="utf-8")
    return path


# --- exports ------------------------------------------------------------------------------------------------------

def openalex_pages(out, q, headers, year, tag):
    """One cursor run over one publication year; returns (page files, record IDs)."""
    base = "https://api.openalex.org/works?"
    pages, ids, cursor = [], [], "*"
    while cursor:
        url = base + urllib.parse.urlencode({"filter": f"title_and_abstract.search:{q},publication_year:{year}",
                                             "per-page": 200, "cursor": cursor})
        d = get_json(url, headers=headers)
        p = out / f"openalex-{year}-{tag}-{len(pages) + 1:03d}.json"
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        pages.append(p)
        ids += [w["id"] for w in d["results"]]
        cursor = d["meta"].get("next_cursor") if d["results"] else None
        time.sleep(0.5)
    return pages, ids


def export_openalex(out, tries=3):
    """OpenAlex's cursor paging over the whole result repeated and skipped records (2026-10-18: 10,838 read for
    10,827 reported, 10,813 unique). So the result is cut by publication year (group_by), each year is paged on its
    own (records without a year as one more slice, publication_year:null), and a year is kept only when its unique
    records equal its count and no record repeats; otherwise its pages are removed and the year is paged again (up to
    `tries` times, then the export stops). The year counts must add up to the total."""
    q = query_openalex()
    headers = openalex_headers()
    for old in out.glob("openalex-[0-9]*.json"):
        old.unlink()
    started = now()
    g = get_json("https://api.openalex.org/works?" + urllib.parse.urlencode(
        {"filter": "title_and_abstract.search:" + q, "group_by": "publication_year", "per-page": 200}), headers=headers)
    total, groups = g["meta"]["count"], {x["key"]: x["count"] for x in g["group_by"]}
    if not all(re.fullmatch(r"\d{4}", k) for k in groups):
        raise SystemExit(f"OpenAlex: a year group is not a year: {sorted(groups)}")
    # records without a publication year are in no group (2026-10-18: 34); they are paged as one more slice
    no_year = get_json("https://api.openalex.org/works?" + urllib.parse.urlencode(
        {"filter": f"title_and_abstract.search:{q},publication_year:null", "per-page": 1}), headers=headers)
    groups["null"] = no_year["meta"]["count"]
    if sum(groups.values()) != total:
        raise SystemExit(f"OpenAlex: year groups and records without a year ({groups['null']}) do not add up to "
                         f"{total}: {sum(groups.values())}")
    files, n, retries, repeated = [], 0, {}, {}
    for year in sorted(groups):
        for t in range(1, tries + 1):
            pages, ids = openalex_pages(out, q, headers, year, f"t{t}")
            if len(set(ids)) == groups[year]:   # every record of the year, each at least once
                rep_ = sorted(k for k, c in Counter(ids).items() if c > 1)
                if rep_:
                    repeated[year] = rep_   # the same record returned twice in one run (2026-10-18: 2023, 1)
                break
            retries[year] = t
            for p in pages:
                p.unlink()
        else:
            raise SystemExit(f"OpenAlex {year}: {len(ids)} read ({len(set(ids))} unique) for {groups[year]}, "
                             f"after {tries} tries")
        files += pages
        n += len(ids)
    if n - sum(len(v) for v in repeated.values()) != total:
        raise SystemExit(f"OpenAlex: {n} records read, {total} reported, repeats {repeated}")
    oql = (json.loads(files[0].read_text(encoding="utf-8"))["meta"].get("x_query") or {}).get("oql", "")
    entry = {"source": "OpenAlex API", "api_key_sent": bool(headers), "query": q, "interpreted_as": oql,
             "filter": "title_and_abstract.search, then publication_year one year at a time", "date_limit": None,
             "type_limit": None, "started": started, "finished": now(), "reported_count": total,
             "year_counts": groups, "years_paged_again": retries, "retrieved": n,
             "repeated_ids": repeated, "unique_retrieved": n - sum(len(v) for v in repeated.values()),
             "files": {p.name: sha256(p) for p in files}}
    print(json.dumps({k: v for k, v in entry.items() if k not in ("files", "year_counts")}, ensure_ascii=False))
    write_log(out, "openalex", entry)


def export_europepmc(out):
    q = query_europepmc()
    base = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?"
    started, pages, cursor, n, reported = now(), [], "*", 0, None
    while True:
        url = base + urllib.parse.urlencode({"query": q, "format": "json", "resultType": "core", "pageSize": 1000,
                                             "cursorMark": cursor})
        d = get_json(url)
        reported = d["hitCount"] if reported is None else reported
        res = d.get("resultList", {}).get("result", [])
        if not res:
            break
        p = out / f"europepmc-{len(pages) + 1:03d}.json"
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        pages.append(p)
        n += len(res)
        nxt = d.get("nextCursorMark")
        if not nxt or nxt == cursor:
            break
        cursor = nxt
        time.sleep(1)
    entry = {"source": "Europe PMC REST API", "query": q, "field": "TITLE_ABS", "date_limit": None,
             "type_limit": None, "started": started, "finished": now(), "reported_count": reported,
             "retrieved": n, "files": {p.name: sha256(p) for p in pages}}
    print(json.dumps({k: v for k, v in entry.items() if k != "files"}, ensure_ascii=False))
    write_log(out, "europepmc", entry)


MAX_POST = 20 * 1024 * 1024


def acm_receive(out, port):
    """Receive the ACM result list posted by acm_export.js, save it, then stop. Only a POST to the one-time path
    printed at start, from the ACM Digital Library origin, under MAX_POST bytes, whose query is the registered ACM
    query and whose records match its reported count, is saved; anything else gets 403/400 and the server waits on."""
    token = hashlib.sha256(str(time.time_ns()).encode() + bytes(16)).hexdigest()[:24]

    class H(http.server.BaseHTTPRequestHandler):
        timeout = 30   # a connection that sends nothing (Chrome opens some ahead of time) is dropped after 30 s

        def _cors(self):
            self.send_header("Access-Control-Allow-Origin", "https://dl.acm.org")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Private-Network", "true")

        def do_OPTIONS(self):
            self.send_response(204)
            self._cors()
            self.end_headers()

        def _refuse(self, code, why):
            self.send_response(code)
            self._cors()
            self.end_headers()
            self.wfile.write(why.encode())
            print(f"refused ({code}): {why}", flush=True)

        def do_POST(self):
            if self.path != "/" + token:
                return self._refuse(403, "wrong path")
            if self.headers.get("Origin") != "https://dl.acm.org":
                return self._refuse(403, "wrong origin")
            n = int(self.headers.get("Content-Length") or 0)
            if not 0 < n <= MAX_POST:
                return self._refuse(400, "bad size")
            body = self.rfile.read(n)
            try:
                d = json.loads(body)
                recs = d["records"]
                ok = (d.get("query") == query_acm() and isinstance(recs, list)
                      and len(recs) == d.get("reported_count")
                      and all(isinstance(r, dict) and r.get("href") for r in recs)
                      and len({r["href"] for r in recs}) == len(recs))
            except (ValueError, KeyError, TypeError):
                ok = False
            if not ok:
                return self._refuse(400, "not the registered query, or records do not match the reported count")
            p = out / "acm-results.json"
            p.write_bytes(body)
            entry = {"source": "ACM Digital Library web interface (ACM Guide to Computing Literature)",
                     "query": query_acm(), "query_sent": d.get("query"), "date_limit": None, "type_limit": None,
                     "started": d.get("started"), "finished": d.get("finished"),
                     "reported_count": d.get("reported_count"), "retrieved": len(d.get("records", [])),
                     "passes": d.get("passes"),
                     "files": {p.name: sha256(p)}}
            write_log(out, "acm", entry)
            self.send_response(200)
            self._cors()
            self.end_headers()
            self.wfile.write(b"saved")
            print(json.dumps({k: v for k, v in entry.items() if k != "files"}, ensure_ascii=False), flush=True)
            self.server.done = True

        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), H)   # one silent connection blocks no other
    srv.timeout = 1
    srv.done = False
    print(f"listening on http://127.0.0.1:{port}/{token}\nrun in the ACM tab: await acmExport(QUERY, {port}, '{token}')\n"
          f"QUERY:\n{query_acm()}", flush=True)
    while not srv.done:
        srv.handle_request()


# --- normalising --------------------------------------------------------------------------------------------------

def norm_doi(d):
    d = (d or "").strip().lower()
    d = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", d)
    return d if d.startswith("10.") else ""


def norm_title(t):
    t = unicodedata.normalize("NFKC", t or "").lower()
    return "".join(ch for ch in t if ch.isalnum())


def oa_abstract(inv):
    if not inv:
        return ""
    pos = sorted((i, w) for w, idx in inv.items() for i in idx)
    return " ".join(w for _, w in pos)


def logged_files(out, source, pattern):
    """The export files listed in the source's log, in order; every file on disk that matches the pattern must be
    listed (a stale page from an earlier run stops the merge)."""
    names = list(json.loads((out / f"{source}-log.json").read_text(encoding="utf-8"))["files"])
    extra = sorted(p.name for p in out.glob(pattern) if p.name not in names)
    if extra:
        raise SystemExit(f"{source}: files not in {source}-log.json: {extra}")
    return [out / n for n in names]


def records_openalex(out):
    """Each record once. A record that OpenAlex returned twice is read once only if the log lists it as repeated;
    any other repeat is kept, so that the merge stops on it."""
    log = json.loads((out / "openalex-log.json").read_text(encoding="utf-8"))
    allowed = {i for v in log.get("repeated_ids", {}).values() for i in v}
    seen = set()
    for p in logged_files(out, "openalex", "openalex-[0-9]*.json"):
        for w in json.loads(p.read_text(encoding="utf-8"))["results"]:
            if w.get("id") in allowed and w["id"] in seen:
                continue
            seen.add(w.get("id"))
            yield {"source": "openalex", "source_id": w.get("id", ""), "doi": norm_doi(w.get("doi")),
                   "title": w.get("display_name") or w.get("title") or "", "year": w.get("publication_year"),
                   "type": w.get("type", ""), "venue": ((w.get("primary_location") or {}).get("source") or {})
                   .get("display_name", ""), "abstract": oa_abstract(w.get("abstract_inverted_index"))}


def records_europepmc(out):
    for p in logged_files(out, "europepmc", "europepmc-[0-9]*.json"):
        for r in json.loads(p.read_text(encoding="utf-8"))["resultList"]["result"]:
            yield {"source": "europepmc", "source_id": f"{r.get('source', '')}:{r.get('id', '')}",
                   "doi": norm_doi(r.get("doi")), "title": r.get("title", ""), "year": r.get("pubYear"),
                   "type": "; ".join((r.get("pubTypeList") or {}).get("pubType", [])),
                   "venue": ((r.get("journalInfo") or {}).get("journal") or {}).get("title", "")
                   or r.get("bookOrReportDetails", {}).get("publisher", ""),
                   "abstract": re.sub(r"<[^>]+>", "", r.get("abstractText", "") or "")}


def records_acm(out):
    p = out / "acm-results.json"
    for r in json.loads(p.read_text(encoding="utf-8"))["records"]:
        doi = acm_doi(r.get("href"))
        yield {"source": "acm", "source_id": r.get("href", ""), "doi": doi, "title": r.get("title", ""),
               "year": r.get("date", ""), "type": r.get("type", ""), "venue": r.get("venue", ""), "abstract": ""}


def acm_doi(href):
    """The DOI in an ACM result link, whatever its form (/doi/..., /doi/abs/..., /doi/book/...)."""
    m = re.search(r"10\.\d{4,}/[^\s?#]+", href or "")
    return norm_doi(m.group(0) if m else "")


READERS = {"openalex": records_openalex, "europepmc": records_europepmc, "acm": records_acm}


# --- the source database (34 + 264) -------------------------------------------------------------------------------

M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def xlsx_rows(path, name):
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        shared = ["".join(si.itertext()) for si in ET.fromstring(z.read("xl/sharedStrings.xml"))]
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    for s in wb.find(M + "sheets"):
        if s.get("name") == name:
            target = rels[s.get(REL)].lstrip("/")
            target = target if target.startswith("xl/") else "xl/" + target
            for r in ET.fromstring(z.read(target)).iter(M + "row"):
                cells = {}
                for c in r.findall(M + "c"):
                    col = re.match(r"[A-Z]+", c.get("r")).group()
                    v = c.find(M + "v")
                    if c.get("t") == "s" and v is not None:
                        cells[col] = shared[int(v.text)]
                    elif c.get("t") == "inlineStr":
                        cells[col] = "".join(c.itertext())
                    else:
                        cells[col] = v.text if v is not None else ""
                yield cells
            return
    raise SystemExit(f"sheet {name!r} not found in {path}")


def source_db(records264, xlsx):
    recs = json.loads(Path(records264).read_text(encoding="utf-8"))
    if len(recs) != 264:
        raise SystemExit(f"{records264}: {len(recs)} records, expected 264")
    out = [{"id": r["id"], "doi": norm_doi(r.get("doi")), "t": norm_title(r.get("title"))} for r in recs]
    n34 = 0
    for c in xlsx_rows(xlsx, "文献DB"):  # A = ID, E = title, H = DOI
        if re.fullmatch(r"AF\d{3}", c.get("A", "").strip()):
            out.append({"id": c["A"].strip(), "doi": norm_doi(c.get("H")), "t": norm_title(c.get("E"))})
            n34 += 1
    if n34 != 34:
        raise SystemExit(f"{xlsx}: {n34} exploratory records in '文献DB', expected 34")
    return out


# --- merge, remove, draw ------------------------------------------------------------------------------------------

TITLE_MIN = 15        # a normalised title shorter than this ("Index", "Editorial", "Preface") never merges
TITLE_MAX_DOIS = 3    # nor does a title carried by more distinct DOIs than this (chapters of one book, columns)


def title_keys(recs):
    """The normalised titles that may merge records: at least TITLE_MIN characters, and carried by at most
    TITLE_MAX_DOIS distinct DOIs (2026-10-18: "Index" had 19 DOIs, a book title 43). Versions of one report (a
    preprint and its article) share a title with one to three DOIs."""
    dois = {}
    for r in recs:
        t = norm_title(r["title"])
        if t:
            dois.setdefault(t, set())
            if r["doi"]:
                dois[t].add(r["doi"])
    return {t for t, d in dois.items() if len(t) >= TITLE_MIN and len(d) <= TITLE_MAX_DOIS}


def merge_records(recs):
    """Union records that share a DOI, or a normalised title that may merge (title_keys), transitively.
    Returns a list of groups (lists of records)."""
    parent = list(range(len(recs)))
    ok_titles = title_keys(recs)

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    seen = {}
    for i, r in enumerate(recs):
        t = norm_title(r["title"])
        for key in (("d", r["doi"]), ("t", t if t in ok_titles else "")):
            if not key[1]:
                continue
            if key in seen:
                parent[find(i)] = find(seen[key])
            else:
                seen[key] = i
    groups = {}
    for i, r in enumerate(recs):
        groups.setdefault(find(i), []).append(r)
    return list(groups.values())


ABSTRACT_PREFERENCE = ["europepmc", "openalex", "acm"]  # OpenAlex abstracts can lose text around < and >


def summarise(g):
    def first(field):
        for src in ABSTRACT_PREFERENCE:
            for r in g:
                if r["source"] == src and r[field]:
                    return r[field]
        return ""
    return {"doi": sorted({r["doi"] for r in g if r["doi"]})[0] if any(r["doi"] for r in g) else "",
            "dois": sorted({r["doi"] for r in g if r["doi"]}), "title": first("title"), "year": first("year"),
            "type": first("type"), "venue": first("venue"), "abstract": first("abstract"),
            "abstract_source": next((s for s in ABSTRACT_PREFERENCE for r in g if r["source"] == s and r["abstract"]),
                                    ""),
            "sources": sorted({r["source"] for r in g}), "source_ids": sorted({r["source_id"] for r in g})}


def remove_known(groups, known):
    kd = {k["doi"]: k["id"] for k in known if k["doi"]}
    kt = {k["t"]: k["id"] for k in known if len(k["t"]) >= TITLE_MIN}
    new, matched = [], []
    for g in groups:
        hit = sorted({kd[r["doi"]] for r in g if r["doi"] in kd} | {kt[norm_title(r["title"])] for r in g
                                                                     if norm_title(r["title"]) in kt})
        (matched if hit else new).append((g, hit))
    return [g for g, _ in new], [(g, h) for g, h in matched]


def assign_ids(groups):
    rows = sorted((summarise(g) for g in groups), key=lambda s: (norm_title(s["title"]), s["doi"], s["source_ids"]))
    if len(rows) > 99999:
        raise SystemExit(f"{len(rows)} new records: more than the ID width allows")
    for i, s in enumerate(rows, 1):
        s["id"] = f"CS{i:05d}"
    return rows


def draw_sample(ids):
    ids = sorted(ids)
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate IDs")
    return sorted(random.Random(SAMPLE_SEED).sample(ids, min(SAMPLE_SIZE, len(ids))))


def merge(out, records264, xlsx):
    recs, read = [], {}
    for src, reader in READERS.items():
        log = out / f"{src}-log.json"
        if not log.exists():
            raise SystemExit(f"missing export of {src}: {log}")
        entry = json.loads(log.read_text(encoding="utf-8"))
        for name, h in entry["files"].items():
            if sha256(out / name) != h:
                raise SystemExit(f"{name}: SHA-256 differs from {log.name}")
            read[name] = h
        got = list(reader(out))
        dup = [k for k, c in Counter(r["source_id"] for r in got).items() if c > 1]
        if dup:
            raise SystemExit(f"{src}: {len(dup)} records listed twice (for example {dup[0]}); pages overlap")
        if len(got) != entry["reported_count"]:
            raise SystemExit(f"{src}: {len(got)} records read, the source reported {entry['reported_count']}")
        recs += got
    known = source_db(records264, xlsx)
    groups = merge_records(recs)
    new, matched = remove_known(groups, known)
    rows = assign_ids(new)
    sample = set(draw_sample([r["id"] for r in rows]))
    for r in rows:
        r["coverage_sample"] = r["id"] in sample
    (out / "new_records.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(out / "new-records.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["record_id", "doi", "title", "year", "sources", "coverage_sample"])
        for r in rows:
            w.writerow([r["id"], r["doi"], r["title"], r["year"], "|".join(r["sources"]),
                        "1" if r["coverage_sample"] else "0"])
    by_src = {s: sum(1 for r in recs if r["source"] == s) for s in READERS}
    log = {"merged": now(), "python": sys.version.split()[0], "records_by_source": by_src,
           "records_total": len(recs), "after_merging": len(groups), "matching_source_database": len(matched),
           "matched_source_ids": sorted({i for _, h in matched for i in h}), "new_records": len(rows),
           "sample_size": len(sample), "sample_seed": SAMPLE_SEED,
           "groups_of_3_or_more": sum(1 for g in groups if len(g) >= 3),
           "merged_groups_with_short_title": sum(1 for g in groups if len(g) > 1
                                                 and min(len(norm_title(r["title"])) for r in g) < 15),
           "new_with_abstract": sum(1 for r in rows if r["abstract"]),
           "sample_with_abstract": sum(1 for r in rows if r["coverage_sample"] and r["abstract"]),
           "inputs": {**read, Path(records264).name: sha256(records264), Path(xlsx).name: sha256(xlsx)},
           "outputs": {n: sha256(out / n) for n in ("new_records.json", "new-records.csv")}}
    (out / "search-log.json").write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(log, ensure_ascii=False, indent=1))


# --- self test ----------------------------------------------------------------------------------------------------

def selftest():
    ok = True

    def check(name, cond):
        nonlocal ok
        print(("PASS " if cond else "FAIL ") + name)
        ok &= bool(cond)

    check("doi prefix removed", norm_doi("https://doi.org/10.1/AbC") == "10.1/abc")
    check("doi without 10. is empty", norm_doi("arXiv:1234") == "")
    check("title normalised", norm_title("AI Fatigue: a Scale!") == norm_title("ai fatigue — a scale"))
    check("abstract rebuilt", oa_abstract({"b": [1], "a": [0]}) == "a b")
    check("ACM DOI from any link form", acm_doi("/doi/abs/10.1145/3544548.3581234") == "10.1145/3544548.3581234"
          and acm_doi("/doi/10.1016/j.x.2026.1") == "10.1016/j.x.2026.1" and acm_doi("/action/x") == "")
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        (t / "openalex-001.json").write_text("{}")
        (t / "openalex-002.json").write_text("{}")
        (t / "openalex-log.json").write_text(json.dumps({"files": {"openalex-001.json": ""}}))
        try:
            logged_files(t, "openalex", "openalex-[0-9]*.json")
            check("a stale page not in the log stops", False)
        except SystemExit:
            check("a stale page not in the log stops", True)
        (t / "openalex-002.json").unlink()
        check("logged pages are read", [p.name for p in logged_files(t, "openalex", "openalex-[0-9]*.json")]
              == ["openalex-001.json"])
    R = lambda s, d, t: {"source": s, "source_id": s + t, "doi": d, "title": t, "year": 2025, "type": "",
                         "venue": "", "abstract": ""}
    TA, TB, TC = "Fatigue and generative AI use", "A different title of the same report", "Another study entirely"
    g = merge_records([R("openalex", "10.1/x", TA), R("europepmc", "", TA.lower()), R("acm", "10.1/x", TB),
                       R("acm", "10.1/y", TC)])
    check("merge by DOI and title, transitively", sorted(len(x) for x in g) == [1, 3])
    T = "A generic but long enough title"
    gen = merge_records([R("openalex", f"10.9/{i}", T) for i in range(4)])
    check("a title carried by more than 3 DOIs does not merge", sorted(len(x) for x in gen) == [1, 1, 1, 1])
    ver = merge_records([R("openalex", "10.9/pre", T), R("openalex", "10.9/art", T), R("europepmc", "", T)])
    check("versions (2 DOIs, one title) merge", [len(x) for x in ver] == [3])
    short = merge_records([R("openalex", "10.9/a", "Index"), R("acm", "10.9/b", "Index")])
    check("a short title does not merge", sorted(len(x) for x in short) == [1, 1])
    known = [{"id": "AF001", "doi": "10.1/y", "t": ""}]
    new, matched = remove_known(g, known)
    check("known DOI removed", len(new) == 1 and matched[0][1] == ["AF001"])
    known_t = [{"id": "S01", "doi": "", "t": norm_title(TA)}]
    new2, _ = remove_known(g, known_t)
    check("known title removed (whole group)", len(new2) == 1 and new2[0][0]["title"] == TC)
    _, m3 = remove_known(merge_records([R("acm", "10.9/z", "Index")]), [{"id": "S02", "doi": "", "t": "index"}])
    check("a short known title does not remove", m3 == [])
    ids = [f"CS{i:04d}" for i in range(1, 1001)]
    s1, s2 = draw_sample(ids), draw_sample(list(reversed(ids)))
    check("sample size", len(s1) == SAMPLE_SIZE)
    check("sample does not depend on input order", s1 == s2)
    check("sample is the seeded draw", s1 == sorted(random.Random(20261022).sample(sorted(ids), 300)))
    check("all when fewer than the sample size", draw_sample(ids[:10]) == ids[:10])
    try:
        draw_sample(["a", "a"])
        check("duplicate IDs stop", False)
    except ValueError:
        check("duplicate IDs stop", True)
    s = summarise([dict(R("openalex", "10.1/x", "T"), abstract="oa text"),
                   dict(R("europepmc", "", "T"), abstract="epmc text")])
    check("abstract taken from Europe PMC first", s["abstract"] == "epmc text" and s["abstract_source"] == "europepmc")
    check("queries keep the three term groups", all(q().count("OR") > 25 and "NOT" in q() for q in QUERIES.values()))
    print("selftest:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["openalex", "europepmc", "acm-receive", "merge", "selftest", "queries"])
    ap.add_argument("out", nargs="?", type=Path)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--records264", type=Path)
    ap.add_argument("--source-db", type=Path)
    a = ap.parse_args()
    if a.cmd == "selftest":
        selftest()
    if a.cmd == "queries":
        for k, q in QUERIES.items():
            print(f"{k}:\n{q()}\n")
        return
    if a.out is None:
        ap.error("out_dir is required")
    a.out.mkdir(parents=True, exist_ok=True)
    if a.cmd == "openalex":
        export_openalex(a.out)
    elif a.cmd == "europepmc":
        export_europepmc(a.out)
    elif a.cmd == "acm-receive":
        acm_receive(a.out, a.port)
    elif a.cmd == "merge":
        if not (a.records264 and a.source_db):
            ap.error("merge needs --records264 and --source-db")
        merge(a.out, a.records264, a.source_db)


if __name__ == "__main__":
    main()
