"""Tools for screening the additional candidates after registration (GSRR-33, GSRR-36 to GSRR-38, GSRR-41; decision 33).

One batch at a time, in this order:

    next          cut the next batch from the fixed screening order (stage 1), or from the records that passed
                  stage 1, in the same order (stage 2; the AI screener judges stage 3 in the same call)
    prepare       write the AI screener's working directory for the batch, outside the repository: the
                  instructions (attachment 6), the inputs (in/<ID>.stage1.txt, ft/<ID>.txt) and the call wording
    export-author write author 1's judgements of the batch from the screening database (xlsx) to the repository
    (author 1's file is committed and pushed here, by hand: git add <that file> && git commit && git push)
    gate          check that author 1's file is committed and pushed, before the AI screener is run
    (the AI screener is run here, with prompt.txt of the working directory, as attachment 6 says)
    check-ai      check the format of the AI screener's output without displaying its content, and write its
                  manifest (decision, code, centre, SHA-256 and time of each output) to the repository
    differences   write, outside the repository, the AI screener's answers on the records where the two differ
    export-final  write the final decisions of the batch at one stage (agreements, and author 1's decisions on
                  the differences from the xlsx) to the repository

After the screening:

    screening-csv write screening.csv for c_synthesis.py --screening and report the counts of GSRR-37
    review-quotes write, outside the repository, every quotation and note of the AI screener with a pre-filled
                  flag for scale items; author 1 confirms each row
    release       write the public list of decisions and the AI screener's answers, with the quotations that
                  author 1 marked as scale items removed (GSRR-41)

Repository files (state directory, default ../screening): batches.csv; s1/<batch>.author1.csv, .ai.csv,
.final.csv; s2/<batch>.author1.csv, .author1-late.csv, .ai.csv, .final2.csv, .final3.csv. They hold IDs, codes,
hashes and times only. Abstracts, full texts and the AI screener's JSON (with its quotations) stay in the working
directory outside the repository.

Run with openpyxl via uv, from this directory:
    uv run --with openpyxl python c_screening.py <command> [options]
Every command stops (exit 3) with a message on input it does not accept.
"""

import argparse
import csv
import datetime
import hashlib
import html.parser
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

TASK = Path(__file__).resolve().parent.parent
ATT = TASK / "registration-attachments"
DRIVE_TRACE = "マイドライブ/Doe_Systems/Reserch_production/GSE/AI-fatigue/TRACE"


def drive_trace():
    """The Google Drive folder AI-fatigue/TRACE as synced by Drive for desktop, where author 1's workbook lives
    (decision 36). TRACE_DRIVE overrides it. If no synced folder is found, a path that does not exist is returned,
    so that a command reading the workbook fails instead of reading another copy."""
    if os.environ.get("TRACE_DRIVE"):
        return Path(os.environ["TRACE_DRIVE"])
    hits = sorted(Path("~/Library/CloudStorage").expanduser().glob("GoogleDrive-*/" + DRIVE_TRACE))
    return hits[0] if hits else Path("~/Library/CloudStorage/(Google Drive not found)") / DRIVE_TRACE


DEFAULTS = {
    "state": TASK / "screening",
    "order": ATT / "screening-order.csv",
    "instructions": ATT / "ai-screening" / "instructions.md",
    "call": ATT / "ai-screening" / "call.md",
    "work": Path("~/TRACE-screening"),
    "data": Path("~/Documents/TRACE/data"),
    "fulltext": Path("~/Documents/TRACE/fulltext"),
    "xlsx": drive_trace() / "TRACE_database.xlsx",
}
BATCH = 9
CODES = {f"E{i}" for i in range(1, 8)}
STAGE1_CODES = {"E1", "E2", "E3", "E4", "E7"}  # instructions section 4, stage 1
ANSWERS = {"yes", "no", "unclear"}
QUESTIONS = [f"Q{i}" for i in range(1, 8)]
OUT_KEYS = {"id", "stage", "read", "source", "answers", "decision", "code", "centre", "note"}
READS = {"title only", "abstract", "part of full text", "full text"}
QUOTE_WORDS = 25


CJK = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff\uff66-\uff9f]")


def word_count(text):
    """Words of a quotation (decision 33): whitespace-separated tokens with at least one letter or digit, so that a
    sign such as '=' in 'n = 120' is not a word; Japanese characters (kana and kanji) count as one word per two
    characters, so that 25 words are 50 Japanese characters."""
    n = 0
    for t in text.split():
        cjk = len(CJK.findall(t))
        rest = CJK.sub("", t)
        n += (cjk + 1) // 2 + (1 if re.search(r"\w", rest) else 0)
    return n

CENTRE_AI = {"centre-A": "A", "centre-B": "B", "boundary": "boundary"}

# xlsx values -> codes
JA_DECISION = {"含める": "include", "除外": "exclude", "保留": "pending", "未判定": "", None: "", "": ""}
JA_CENTRE = {"中心-A": "A", "中心-B": "B", "境界（保留）": "boundary", "未判定": "", None: "", "": ""}
JA_READ = {"題名のみ": "title only", "抄録": "abstract", "全文の一部": "part of full text", "全文": "full text",
           None: "", "": ""}
SHEET = {1: "段1", 2: "段2・3"}

AUTHOR_COLS = ["record_id", "stage", "decision", "code", "centre", "read"]
AI_COLS = ["record_id", "stage", "decision", "code", "centre", "read", "attempt", "valid", "sha256", "time_utc",
           "author1_commit", "gate_utc"]
FINAL_COLS = ["record_id", "stage", "author1", "ai", "final", "code", "e5_with", "decided_by", "date",
              "author1_late_commit"]


class Stop(Exception):
    pass


# --- small helpers -----------------------------------------------------------

def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, cols, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")


def batch_name(n):
    return f"b{n:02d}"


def stage_dir(a, stage):
    return a.state / f"s{stage}"


def work_dir(a, stage, batch):
    return a.work / f"s{stage}-{batch}"


def order_ids(a):
    """(record_id, population) in the fixed screening order (attachment 4: population,record_id per line)."""
    if not a.order.exists():
        raise Stop(f"missing screening order {a.order}")
    out = []
    with open(a.order, encoding="utf-8", newline="") as f:
        for row in csv.reader(f):
            if len(row) != 2 or not row[1]:
                raise Stop(f"{a.order.name}: line not in the form population,record_id: {row}")
            out.append((row[1], row[0]))
    ids = [i for i, _ in out]
    if len(set(ids)) != len(ids):
        raise Stop(f"{a.order.name}: a record is listed twice")
    return out


def batches(a):
    p = a.state / "batches.csv"
    return read_csv(p) if p.exists() else []


def batch_ids(a, stage, batch):
    ids = [r["record_id"] for r in batches(a) if r["stage"] == str(stage) and r["batch"] == batch]
    if not ids:
        raise Stop(f"no batch {batch} at stage {stage} in batches.csv")
    return ids


def finals(a, stage):
    """record_id -> final row, over every batch of the stage (stage 1, 2 or 3)."""
    d = stage_dir(a, 1 if stage == 1 else 2)
    suffix = ".final.csv" if stage == 1 else f".final{stage}.csv"
    out = {}
    for p in sorted(d.glob(f"*{suffix}")) if d.exists() else []:
        for r in read_csv(p):
            out[r["record_id"]] = r
    return out


# --- next --------------------------------------------------------------------

def cmd_next(a):
    order = [i for i, _ in order_ids(a)]
    rows = batches(a)
    done = {r["record_id"] for r in rows if r["stage"] == str(a.stage)}
    n = len({r["batch"] for r in rows if r["stage"] == str(a.stage)}) + 1
    if a.revisit:
        if a.stage != 2:
            raise Stop("--revisit applies to stage 2")
        f2 = finals(a, 2)
        want = {x.strip() for x in a.revisit.split(",") if x.strip()}
        bad = sorted(i for i in want if i not in f2 or f2[i]["final"] != "pending")
        if bad:
            raise Stop(f"--revisit takes records whose latest stage-2 decision is pending: {bad}")
        open_b = {r["record_id"] for r in rows if r["stage"] == "2" and
                  not (stage_dir(a, 2) / f"{r['batch']}.final2.csv").exists()}
        if want & open_b:
            raise Stop(f"already in a stage-2 batch that is not final: {sorted(want & open_b)}")
        import make_trace_db as db
        no_ft = sorted(i for i in want if not db.fulltext_file(i, str(a.fulltext)))
        if no_ft:
            raise Stop(f"no free full text in the full-text folder yet: {no_ft} (GSRR-33)")
        todo = [i for i in order if i in want]
        if len(todo) > BATCH:
            raise Stop(f"at most {BATCH} records in a batch")
    elif a.stage == 1:
        if a.short:
            raise Stop("--short applies to stage 2 only (stage-1 batches are cut from the fixed order at once)")
        todo = [i for i in order if i not in done][:BATCH]
    else:
        f1 = finals(a, 1)
        ready, blocked = [], None
        for i in order:
            if i not in f1:
                blocked = i
                break
            if f1[i]["final"] == "include" and i not in done:
                ready.append(i)
        if len(ready) >= BATCH:
            todo = ready[:BATCH]
        elif blocked is None or a.short:
            todo = ready
        else:
            raise Stop(f"{len(ready)} records ready for stage 2; a batch of {BATCH} waits for stage 1 of {blocked} "
                       "(use --short only for the last batch before 2026-12-31)")
    if not todo:
        raise Stop(f"no record left for stage {a.stage}")
    name = batch_name(n)
    now = utc(datetime.datetime.now().timestamp())
    rows += [{"stage": str(a.stage), "batch": name, "record_id": i, "cut_utc": now} for i in todo]
    write_csv(a.state / "batches.csv", ["stage", "batch", "record_id", "cut_utc"], rows)
    print(f"stage {a.stage} batch {name}: {' '.join(todo)}")


# --- prepare -----------------------------------------------------------------

class _Text(html.parser.HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "head"}
    BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "section", "table", "caption"}

    def __init__(self):
        super().__init__()
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def html_text(path):
    p = _Text()
    p.feed(Path(path).read_text(encoding="utf-8", errors="replace"))
    return re.sub(r"\n\s*\n+", "\n\n", "".join(p.parts)).strip()


def jats_text(path):
    root = ET.parse(path).getroot()
    out = []
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag in ("title", "p", "label", "td", "th", "caption"):
            t = " ".join("".join(el.itertext()).split())
            if t:
                out.append(t)
    return "\n\n".join(out)


def pdf_text(path):
    if not shutil.which("pdftotext"):
        raise Stop("pdftotext not found (brew install poppler)")
    r = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True)
    if r.returncode != 0:
        raise Stop(f"pdftotext failed on {Path(path).name}")
    return r.stdout


FT_KIND = {".pdf": "PDF, text extracted by machine", ".xml": "Europe PMC full-text XML, text extracted by machine",
           ".html": "publisher's article page, text extracted by machine"}


def source_line(url, doi, saved_by_hand):
    """The first line of ft/<ID>.txt (call.md). A file author 1 saved in a web browser has no recorded URL: the
    record's DOI link is given, with how the file was obtained; no URL is made up."""
    if url:
        return url, ""
    link = "https://doi.org/" + doi if doi.startswith("10.") else "(source URL not recorded)"
    return link, "saved by author 1 in a web browser; " if saved_by_hand else "source URL not recorded; "


def fulltext_input(rid, ftdir, source_url, doi="", saved_by_hand=False):
    """The text of the free full text, with its source on the first line; no retyping (GSRR-33)."""
    import make_trace_db as db  # only here: needs openpyxl
    name = db.fulltext_file(rid, str(ftdir))
    if not name:
        return None
    path = ftdir / name
    ext = path.suffix
    if ext == ".pdf":
        text = pdf_text(path)
    elif ext == ".xml":
        txt = ftdir / f"{rid}.txt"  # the machine-extracted text saved with the XML, when there is one
        text = txt.read_text(encoding="utf-8") if txt.exists() else jats_text(path)
    else:
        text = html_text(path)
    if word_count(text) < 200:
        raise Stop(f"{rid}: the full text {name} gives fewer than 200 words (a scan or a wrong page?)")
    link, how = source_line(source_url, doi, saved_by_hand)
    return f"{link} ({how}{FT_KIND[ext]})\n\n{text}\n"


def stage1_input(rid, rec, meta):
    m = meta.get(rid, {})
    doi = str(rec.get("doi") or "")
    doi = doi if doi.startswith("10.") else ""  # records found by title carry "title:..." in place of a DOI
    url = "https://doi.org/" + doi if doi else ""
    ab, src = (m.get("abstract") or "").strip(), m.get("abstract_source") or ""
    head = f"Abstract ({src}):" if ab else "Abstract (not retrieved):"
    return f"ID: {rid}\nTitle: {rec['title']}\nDOI: {doi}\nURL: {url}\n\n{head}\n{ab}\n"


def registered_sha(a):
    """SHA-256 of the instructions as listed in sha256.txt (made on the registration day), or of the attachment."""
    listed = ATT / "sha256.txt"
    if a.instructions == DEFAULTS["instructions"] and listed.exists():
        for ln in listed.read_text(encoding="utf-8").splitlines():
            if ln.endswith("(AI screener: instructions)"):
                return ln.split()[0]
    return sha256(a.instructions)


def call_wording(call_md, stage):
    """The fenced block of call.md for stage 1 or for stages 2 and 3."""
    text = Path(call_md).read_text(encoding="utf-8")
    heading = "## Wording for stage 1" if stage == 1 else "## Wording for stages 2 and 3"
    m = re.search(re.escape(heading) + r".*?\n```\n(.*?)\n```", text, re.S)
    if not m:
        raise Stop(f"{Path(call_md).name}: no wording under {heading!r}")
    return m.group(1)


def fill_wording(wording, stage, base, with_ft, without_ft):
    w = wording.replace("<working directory>", str(base))
    if stage == 1:
        return w.replace("<up to nine record IDs, in the screening order>", ", ".join(with_ft + without_ft))
    lines = []
    for ln in w.split("\n"):
        if ln.startswith("2. Records with a full text: "):
            if not with_ft:
                continue  # items 2 and 3 are left out when the batch has no record of that kind (call.md)
            ln = ln.replace("<IDs>", ", ".join(with_ft))
        elif ln.startswith("3. Records with no free full text found: "):
            if not without_ft:
                continue
            ln = ln.replace("<IDs>", ", ".join(without_ft))
        lines.append(ln)
    return "\n".join(lines)


def cmd_prepare(a):
    ids = batch_ids(a, a.stage, a.batch)
    w = work_dir(a, a.stage, a.batch)
    if w.exists() and any((w / d).exists() and any((w / d).iterdir()) for d in ("out1", "out2", "out3")):
        raise Stop(f"{w} already has outputs; it is not prepared again")
    recs = {r["id"]: r for r in json.loads((a.data / "records264.json").read_text(encoding="utf-8"))}
    meta = json.loads((a.data / "meta.json").read_text(encoding="utf-8"))
    chrome_p = a.data / "chrome_status.json"
    chrome = json.loads(chrome_p.read_text(encoding="utf-8")) if chrome_p.exists() else {}
    missing = [i for i in ids if i not in recs]
    if missing:
        raise Stop(f"records not in records264.json: {missing}")
    import make_trace_db as db
    for d in ("in", "ft", "out1", "out2", "out3"):
        (w / d).mkdir(parents=True, exist_ok=True)
    shutil.copyfile(a.instructions, w / "instructions.md")
    if sha256(w / "instructions.md") != registered_sha(a):
        raise Stop("the instructions differ from the registered attachment 6 (sha256.txt)")
    with_ft, without_ft = [], []
    for i in ids:
        if a.stage == 1:
            (w / "in" / f"{i}.stage1.txt").write_text(stage1_input(i, recs[i], meta), encoding="utf-8")
            with_ft.append(i)
            continue
        url = db.fulltext_status(i, meta, chrome, str(a.fulltext))[1]
        saved = chrome.get(i, {}).get("status") == "saved"
        text = fulltext_input(i, a.fulltext, url, str(recs[i].get("doi") or ""), saved)
        if text is None:
            (w / "in" / f"{i}.stage1.txt").write_text(stage1_input(i, recs[i], meta), encoding="utf-8")
            without_ft.append(i)
        else:
            (w / "ft" / f"{i}.txt").write_text(text, encoding="utf-8")
            with_ft.append(i)
    prompt = fill_wording(call_wording(a.call, a.stage), a.stage, w, with_ft, without_ft)
    (w / "prompt.txt").write_text(prompt + "\n", encoding="utf-8")
    print(f"prepared {w}: {len(ids)} records"
          + (f" (full text {len(with_ft)}, none {len(without_ft)})" if a.stage == 2 else "")
          + f"; instructions sha256 {sha256(w / 'instructions.md')}")


# --- export-author -----------------------------------------------------------

def sheet_rows(xlsx, stage):
    from openpyxl import load_workbook
    wb = load_workbook(os.path.expanduser(xlsx), data_only=True, read_only=True)
    name = SHEET[stage]
    if name not in wb.sheetnames:
        raise Stop(f"sheet {name!r} not in {Path(xlsx).name}")
    rows = list(wb[name].iter_rows(values_only=True))
    head = [str(c) if c is not None else "" for c in rows[0]]
    out = {}
    for r in rows[1:]:
        d = dict(zip(head, r))
        if d.get("ID"):
            out[str(d["ID"]).strip()] = {k: ("" if v is None else str(v).strip()) for k, v in d.items()}
    return out


def code_of(v, rid, col):
    if v and v not in CODES:
        raise Stop(f"{rid}: {col} {v!r} is not E1 to E7")
    return v


def check_decision(rid, stage, dec, code, centre=""):
    """GSRR-36: author 1 uses the decision rules of attachment 6 section 4."""
    allowed = {"include", "exclude"} if stage == 1 else {"include", "exclude", "pending"}
    if dec not in allowed:
        raise Stop(f"{rid}: stage {stage} decision {dec or '(empty)'!r} not in {sorted(allowed)}")
    if dec == "exclude" and not code:
        raise Stop(f"{rid}: an exclusion needs a code")
    if stage == 1 and code and code not in STAGE1_CODES:
        raise Stop(f"{rid}: {code} is not used at stage 1")
    if dec == "include" and code:
        raise Stop(f"{rid}: an inclusion has no code")
    if dec == "pending" and code not in ("", "E6"):
        raise Stop(f"{rid}: pending takes E6 or no code")
    if stage == 2 and dec == "include" and not centre:
        raise Stop(f"{rid}: included at stage 2 without a centre (stage 3 is judged with stage 2)")
    if stage == 2 and dec != "include" and centre:
        raise Stop(f"{rid}: a centre is given to a record not included at stage 2")


def cmd_export_author(a):
    ids = batch_ids(a, a.stage, a.batch)
    d = stage_dir(a, a.stage)
    out = d / f"{a.batch}.author1.csv"
    if (d / f"{a.batch}.ai.csv").exists():
        raise Stop(f"the AI screener's manifest of {a.batch} exists; author 1's judgements are not exported again")
    rows = sheet_rows(a.xlsx, a.stage)
    earlier = {r["record_id"] for r in batches(a) if r["stage"] == "2" and r["batch"] < a.batch} if a.stage == 2 else set()
    res = []
    for i in ids:
        if i not in rows:
            raise Stop(f"{i} not in sheet {SHEET[a.stage]}")
        r = rows[i]
        if i in earlier and any(r.get(c) for c in ("最終", "最終の除外理由", "最終の中心", "同じ標本の相手（E5）")):
            raise Stop(f"{i} is screened again: clear its '最終…' and '同じ標本の相手（E5）' cells first")
        dec, code = JA_DECISION.get(r.get("判定"), "?"), code_of(r.get("除外理由", ""), i, "除外理由")
        centre = JA_CENTRE.get(r.get("中心", ""), "?") if a.stage == 2 else ""
        read = JA_READ.get(r.get("読んだ範囲", ""), "?")
        if "?" in (dec, centre, read):
            raise Stop(f"{i}: a value outside the drop-down list")
        if a.stage == 1 and read not in ("", "title only", "abstract"):
            raise Stop(f"{i}: at stage 1 読んだ範囲 is 題名のみ or 抄録")
        check_decision(i, a.stage, dec, code, centre)
        res.append({"record_id": i, "stage": str(a.stage), "decision": dec, "code": code, "read": read})
        if a.stage == 2 and dec == "include":
            res.append({"record_id": i, "stage": "3", "centre": centre, "read": read})
    write_csv(out, AUTHOR_COLS, res)
    print(f"wrote {out.relative_to(a.state.parent) if out.is_relative_to(a.state.parent) else out}: {len(ids)} records."
          f" Next: git add {out} && git commit && git push; then gate")


# --- gate --------------------------------------------------------------------

def git(a, *args):
    r = subprocess.run(["git", "-C", str(a.state), *args], capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def commit_time(a, path):
    """(commit, ISO time) of the latest commit of the file, or None; Stop if it has uncommitted changes."""
    rc, log = git(a, "log", "-1", "--format=%H %cI", "--", str(path))
    if rc != 0 or not log:
        return None
    h, t = log.split()
    rc, st = git(a, "status", "--porcelain", "--", str(path))
    if st:
        raise Stop(f"{path.name} has uncommitted changes")
    return h, t


def pushed(a, ct, name):
    rc, remotes = git(a, "branch", "-r", "--contains", ct[0])
    if rc != 0 or not remotes:
        raise Stop(f"the commit of {name} ({ct[0][:8]}) is not on any remote branch: push it first")
    return remotes.splitlines()[0].strip()


def cmd_gate(a):
    p = stage_dir(a, a.stage) / f"{a.batch}.author1.csv"
    if not p.exists():
        raise Stop(f"missing {p.name}: run export-author first")
    ct = commit_time(a, p)
    if ct is None:
        raise Stop(f"{p.name} is not committed")
    remote = pushed(a, ct, p.name)
    w = work_dir(a, a.stage, a.batch)
    if not (w / "prompt.txt").exists():
        raise Stop(f"{w} is not prepared")
    outs = [x for d in ("out1", "out2", "out3") for x in (w / d).glob("*")]
    if outs:
        raise Stop(f"{w} already has {len(outs)} output files")
    (w / "gate.txt").write_text(f"{ct[0]} {utc(datetime.datetime.now().timestamp())}\n", encoding="utf-8")
    print(f"ready: author 1 committed {ct[1]} ({ct[0][:8]}), on {remote}. "
          f"Run the AI screener with {w / 'prompt.txt'}")


# --- check-ai ----------------------------------------------------------------

def output_errors(path, rid, stage):
    """Format errors of one output file, naming fields only, never values."""
    try:
        o = json.loads(Path(path).read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError):
        return ["not valid JSON"]
    if not isinstance(o, dict):
        return ["not a JSON object"]
    errs = []
    if set(o) != OUT_KEYS:
        errs.append("fields differ from section 5 (missing: %s; extra: %d)" % (sorted(OUT_KEYS - set(o)),
                                                                           len(set(o) - OUT_KEYS)))
        return errs
    errs = [f"{k} not text" for k in ("read", "source", "decision", "code", "centre", "note") if not isinstance(o[k], str)]
    if errs:
        return errs
    if o["id"] != rid:
        errs.append("id does not match the file name")
    if type(o["stage"]) is not int or o["stage"] != stage:
        errs.append("stage")
    if o["read"] not in READS or (stage == 1 and o["read"] not in ("title only", "abstract")):
        errs.append("read")
    if not isinstance(o["source"], str):
        errs.append("source")
    ans = o["answers"]
    if not isinstance(ans, dict) or set(ans) != set(QUESTIONS):
        errs.append("answers: not Q1 to Q7")
    else:
        for q in QUESTIONS:
            v = ans[q]
            if q == "Q7" and stage == 1:
                if v not in ({}, None, ""):
                    errs.append("answers.Q7 not empty at stage 1")
                continue
            if not isinstance(v, dict) or set(v) != {"answer", "where", "quote"}:
                errs.append(f"answers.{q}: fields")
                continue
            if not isinstance(v["answer"], str) or v["answer"] not in ANSWERS:
                errs.append(f"answers.{q}.answer")
            if not isinstance(v["where"], str) or not isinstance(v["quote"], str):
                errs.append(f"answers.{q}: where/quote not text")
            elif word_count(v["quote"]) > QUOTE_WORDS:
                errs.append(f"answers.{q}.quote longer than {QUOTE_WORDS} words ({word_count(v['quote'])})")
    dec, code, centre = o["decision"], o["code"], o["centre"]
    allowed = {1: {"include", "exclude"}, 2: {"include", "exclude", "pending"}, 3: {"include"}}[stage]
    if dec not in allowed:
        errs.append("decision")
    if code not in CODES | {""}:
        errs.append("code")
    elif dec == "exclude" and not code or dec == "include" and code or dec == "pending" and code not in ("", "E6"):
        errs.append("code does not fit the decision")
    elif stage == 1 and code and code not in STAGE1_CODES:
        errs.append("code not used at stage 1")
    if stage == 3:
        if centre not in CENTRE_AI:
            errs.append("centre")
    elif centre != "":
        errs.append("centre not empty before stage 3")
    return errs


def batch_errors(w, ids, stage):
    """Errors over the whole output of a batch call. Returns (errors, {(id, stage): (path, obj)})."""
    errs, outs = [], {}
    stages = [1] if stage == 1 else [2, 3]
    for st in stages:
        d = w / f"out{st}"
        names = {p.name for p in d.glob("*")} if d.exists() else set()
        extra = names - {f"{i}.json" for i in ids}
        if extra:
            errs.append(f"out{st}: {len(extra)} files that are not records of the batch")
    for i in ids:
        p = w / f"out{stage}" / f"{i}.json"
        if not p.exists():
            errs.append(f"{i} out{stage}: missing")
            continue
        e = output_errors(p, i, stage)
        errs += [f"{i} out{stage}: {x}" for x in e]
        if e:
            continue
        o = json.loads(p.read_text(encoding="utf-8"))
        outs[(i, stage)] = (p, o)
        if stage == 2:
            p3 = w / "out3" / f"{i}.json"
            if o["decision"] == "include" and not p3.exists():
                errs.append(f"{i} out3: missing for a record included at stage 2")
            elif o["decision"] != "include" and p3.exists():
                errs.append(f"{i} out3: present for a record not included at stage 2")
            elif p3.exists():
                e3 = output_errors(p3, i, 3)
                errs += [f"{i} out3: {x}" for x in e3]
                if not e3:
                    outs[(i, 3)] = (p3, json.loads(p3.read_text(encoding="utf-8")))
    return errs, outs


def cmd_check_ai(a):
    ids = batch_ids(a, a.stage, a.batch)
    d = stage_dir(a, a.stage)
    man = d / f"{a.batch}.ai.csv"
    if man.exists():
        raise Stop(f"{man.name} exists already")
    author = d / f"{a.batch}.author1.csv"
    ct = commit_time(a, author) if author.exists() else None
    if ct is None:
        raise Stop(f"{author.name} is not committed; the AI screener's output cannot be accepted (GSRR-33)")
    pushed(a, ct, author.name)
    w = work_dir(a, a.stage, a.batch)
    gate_p = w / "gate.txt"
    gate = gate_p.read_text(encoding="utf-8").split() if gate_p.exists() else []
    if len(gate) != 2 or gate[0] != ct[0]:
        raise Stop("gate has not passed for author 1's latest commit of this batch: run gate before the AI screener")
    if not (w / "instructions.md").exists() or sha256(w / "instructions.md") != registered_sha(a):
        raise Stop("the instructions in the working directory are not the registered attachment 6 (GSRR-36)")
    prev = sorted(w.glob("attempt*"))
    attempt = len(prev) + 1
    files = [x for sub in ("out1", "out2", "out3") for x in (w / sub).glob("*")]
    if not files:
        raise Stop("no output in the working directory: run the AI screener first")
    # outputs must be newer than author 1's commit (GSRR-33) and, on a re-run, than the first output's set-aside
    gate_ts = datetime.datetime.strptime(gate[1], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc).timestamp()
    since = max([gate_ts] + [x.stat().st_mtime for x in prev])
    early = [x.name for x in files if x.stat().st_mtime < since]
    if early:
        raise Stop(f"{len(early)} outputs are older than the gate ({gate[1]}, after author 1's commit was pushed)"
                   + (" or than the set-aside of the earlier output" if prev else "") + "; see GSRR-33")
    errs, outs = batch_errors(w, ids, a.stage)
    if errs:
        keep = w / f"attempt{attempt}"
        keep.mkdir()
        for sub in ("out1", "out2", "out3"):
            if (w / sub).exists():
                shutil.move(str(w / sub), str(keep / sub))
                (w / sub).mkdir()
        print(f"FORMAT NOT ACCEPTED (attempt {attempt}): {len(errs)} problems; the output is kept in {keep.name}/")
        for e in errs:
            print("  " + e)
        if attempt == 1:
            print("Re-run the AI screener once on this batch with the same prompt.txt, then run check-ai again.")
            return 1
        rows = [{"record_id": i, "stage": str(a.stage), "attempt": str(attempt), "valid": "no",
                 "author1_commit": ct[0], "gate_utc": gate[1]} for i in ids]
        write_csv(man, AI_COLS, rows)
        print(f"second output also not in the format: the batch is decided by author 1 alone (GSRR-33). "
              f"Wrote {man.name}; commit it.")
        return 0
    rows = []
    for (i, st), (p, o) in sorted(outs.items(), key=lambda x: (ids.index(x[0][0]), x[0][1])):
        rows.append({"record_id": i, "stage": str(st), "decision": o["decision"] if st != 3 else "",
                     "code": o["code"], "centre": CENTRE_AI[o["centre"]] if st == 3 else "", "read": o["read"],
                     "attempt": str(attempt), "valid": "yes", "sha256": sha256(p), "time_utc": utc(p.stat().st_mtime),
                     "author1_commit": ct[0], "gate_utc": gate[1]})
    write_csv(man, AI_COLS, rows)
    print(f"format accepted (attempt {attempt}): {len(rows)} outputs. Wrote {man.name}; commit it, then differences.")
    return 0


# --- differences / export-final ---------------------------------------------

def load_batch(a, stage, batch):
    """author 1's and the AI screener's values of the batch at one stage: {id: (author1, ai)}."""
    d = stage_dir(a, 1 if stage == 1 else 2)
    au = read_csv(d / f"{batch}.author1.csv")
    late = d / f"{batch}.author1-late.csv"
    if stage == 3 and late.exists():
        au += read_csv(late)
    mp = d / f"{batch}.ai.csv"
    if not mp.exists():
        raise Stop(f"missing {mp.name}: run check-ai first")
    ai = read_csv(mp)
    key = "centre" if stage == 3 else "decision"
    A = {r["record_id"]: (r[key], r["code"]) for r in au if r["stage"] == str(stage)}
    B = {r["record_id"]: (r[key], r["code"]) for r in ai if r["stage"] == str(stage) and r["valid"] == "yes"}
    return A, B, any(r["valid"] == "no" for r in ai)


def stage3_records(a, batch):
    """Records the batch itself included at stage 2 (a record screened again belongs to its own batch)."""
    p = stage_dir(a, 2) / f"{batch}.final2.csv"
    if not p.exists():
        raise Stop(f"stage 2 of {batch} is not final yet")
    return [r["record_id"] for r in read_csv(p) if r["final"] == "include"]


def cmd_differences(a):
    bstage = 1 if a.stage == 1 else 2
    A, B, alone = load_batch(a, a.stage, a.batch)
    w = work_dir(a, bstage, a.batch)
    ids = batch_ids(a, bstage, a.batch) if a.stage != 3 else stage3_records(a, a.batch)
    if a.stage == 3:
        need = [i for i in ids if i not in A]
        if need:
            raise Stop(f"author 1 has no centre for {need}: fill '中心' in 段2・3 and run export-final --stage 2 again")
        late = stage_dir(a, 2) / f"{a.batch}.author1-late.csv"
        if late.exists():  # author 1's late centres are fixed before the AI screener's centres are shown
            ct = commit_time(a, late)
            if ct is None:
                raise Stop(f"{late.name} is not committed")
            pushed(a, ct, late.name)
    diff = [i for i in ids if i in B and A.get(i) != B[i]]
    need = [i for i in ids if i in A and settled(a.stage, A[i], B.get(i)) is None]
    man = {(r["record_id"], r["stage"]): r["sha256"] for r in read_csv(stage_dir(a, bstage) / f"{a.batch}.ai.csv")
           if r["valid"] == "yes"}
    lines = [f"# Differences, stage {a.stage}, batch {a.batch}", ""]
    for i in [x for x in ids if x in B and (x in diff or x in need)]:  # every record author 1 decides (GSRR-38)
        f = w / f"out{a.stage}" / f"{i}.json"
        if sha256(f) != man[(i, str(a.stage))]:
            raise Stop(f"{f.name} differs from the SHA-256 recorded by check-ai")
        o = json.loads(f.read_text(encoding="utf-8"))
        lines += [f"## {i}", f"- author 1: {A.get(i)}", f"- AI: {o['decision']} {o['code']} {o['centre']}".rstrip(),
                  f"- AI read: {o['read']}" + (f"; note: {o['note']}" if a.stage != 2 else "")]
        # stage 2: the note is left out, since it may give the AI screener's view of the centre (decision 33)
        for q in QUESTIONS:
            v = o["answers"].get(q) or {}
            if v:
                lines.append(f"  - {q} {v['answer']} | {v['where']} | {v['quote']}")
        lines.append("")
    out = w / f"differences-{a.stage}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    no_ai = [i for i in ids if i not in B]
    col = "最終の中心" if a.stage == 3 else "最終"
    print(f"stage {a.stage} {a.batch}: {len(ids)} records, {len(diff)} differ"
          + (f", {len(no_ai)} without an AI judgement (author 1 alone)" if no_ai else "")
          + (" [batch decided by author 1 alone]" if alone else "")
          + f". Read {out}. Fill '{col}' in {SHEET[bstage]} for: {' '.join(need) or '(none)'}")


def settled(stage, a1, ai):
    """The value both screeners settle without author 1's decision, or None (GSRR-33). With no AI judgement
    (a batch decided by author 1 alone, or no AI centre), author 1's own value settles, except boundary and a
    stage-2 pending without E6."""
    a_val, a_code = a1
    if ai is None:
        if stage == 3:
            return a1 if a_val != "boundary" else None
        return a1 if a_val != "pending" or a_code == "E6" else None
    b_val, b_code = ai
    if a_val != b_val:
        return None
    if stage == 3:
        return a1 if a_val != "boundary" else None
    if a_val == "include" or a_val == "exclude" and a_code == b_code or a_val == "pending" and a_code == b_code == "E6":
        return a1
    return None


def final_row(rid, stage, a1, ai, sheet_row):
    """The final value of one record at one stage (GSRR-33, GSRR-38). sheet_row: author 1's '最終…' cells."""
    s = settled(stage, a1, ai)
    by = "agreed" if ai else "author1_alone"
    if stage == 3:
        f = JA_CENTRE.get(sheet_row.get("最終の中心", ""), "?")
        if f == "?" or f == "boundary":
            raise Stop(f"{rid}: 最終の中心 must be 中心-A or 中心-B")
        if s:
            if f and f != s[0]:
                raise Stop(f"{rid}: the centre is settled as {s[0]} but 最終の中心 differs")
            return {"final": s[0], "code": "", "decided_by": by}
        if not f:
            raise Stop(f"{rid}: 最終の中心 is needed (the screeners differ, or a screener said boundary)")
        return {"final": f, "code": "", "decided_by": "author1" if ai else "author1_alone"}
    f = JA_DECISION.get(sheet_row.get("最終", ""), "?")
    fcode = code_of(sheet_row.get("最終の除外理由", ""), rid, "最終の除外理由")
    if f == "?":
        raise Stop(f"{rid}: 最終 outside the list")
    e5 = sheet_row.get("同じ標本の相手（E5）", "") if stage == 2 else ""
    if s and f and (f, fcode) != s:
        raise Stop(f"{rid}: the decision is settled as {s} but 最終 differs (a revisited record: clear its '最終' cells)")
    if not f and not s:
        raise Stop(f"{rid}: 最終 is needed (the screeners differ, the codes differ, or a record is pending)")
    f, fcode = (f, fcode) if f else s
    check_decision(rid, stage, f, fcode, "x" if stage == 2 and f == "include" else "")
    if fcode == "E5" and not e5:
        raise Stop(f"{rid}: E5 needs 同じ標本の相手（E5）")
    if e5 and fcode != "E5":
        raise Stop(f"{rid}: 同じ標本の相手（E5） is filled but the code is not E5")
    return {"final": f, "code": fcode, "e5_with": e5, "decided_by": by if s else "author1" if ai else "author1_alone"}


def cmd_export_final(a):
    bstage = 1 if a.stage == 1 else 2
    d = stage_dir(a, bstage)
    out = d / (f"{a.batch}.final.csv" if a.stage == 1 else f"{a.batch}.final{a.stage}.csv")
    if out.exists():
        raise Stop(f"{out.name} exists already")
    sheet = sheet_rows(a.xlsx, bstage)
    if a.stage == 3:
        ids = stage3_records(a, a.batch)
    else:
        ids = batch_ids(a, bstage, a.batch)
    A, B, _ = load_batch(a, a.stage, a.batch)
    late_commit = ""
    late_p = d / f"{a.batch}.author1-late.csv"
    if a.stage == 3 and late_p.exists():
        ct = commit_time(a, late_p)
        if ct is None:
            raise Stop(f"{late_p.name} is not committed")
        pushed(a, ct, late_p.name)
        late_commit = ct[0]
    rows, late = [], []
    for i in ids:
        if a.stage == 3 and i not in A:
            raise Stop(f"{i}: author 1 has no centre; run export-final --stage 2 after filling '中心'")
        r = final_row(i, a.stage, A[i], B.get(i), sheet[i])
        rows.append({"record_id": i, "stage": str(a.stage), "author1": A[i][0], "ai": B[i][0] if i in B else "",
                     "date": today(), "author1_late_commit": late_commit, **r})
    if a.stage == 2:
        # records included in the end that author 1 had not included: author 1 gives the centre now (stage 3),
        # after reading the AI screener's stage-2 answers but not its centre (decision 33)
        for r in rows:
            if r["final"] == "include" and A[r["record_id"]][0] != "include":
                c = JA_CENTRE.get(sheet[r["record_id"]].get("中心", ""), "?")
                if c in ("", "?"):
                    raise Stop(f"{r['record_id']}: included in the end: author 1's '中心' is needed")
                late.append({"record_id": r["record_id"], "stage": "3", "centre": c, "read": "full text"})
        if late:
            write_csv(d / f"{a.batch}.author1-late.csv", AUTHOR_COLS, late)
    write_csv(out, FINAL_COLS, rows)
    print(f"wrote {out.name}" + (f" and {a.batch}.author1-late.csv ({len(late)} centres)" if late else "")
          + "; commit them" + ("; then differences --stage 3" if a.stage == 2 else ""))


# --- screening-csv -----------------------------------------------------------

def incomplete(a):
    """Batches whose stages are not all final: a release or a table built from them would be wrong."""
    out = []
    for r in {(r["stage"], r["batch"]) for r in batches(a)}:
        st, b = r
        d = stage_dir(a, int(st))
        if st == "1" and not (d / f"{b}.final.csv").exists():
            out.append(f"s1 {b}")
        elif st == "2":
            if not (d / f"{b}.final2.csv").exists():
                out.append(f"s2 {b} (stage 2)")
            elif stage3_records(a, b) and not (d / f"{b}.final3.csv").exists():
                out.append(f"s2 {b} (stage 3)")
    return sorted(out)


def cmd_screening_csv(a):
    if incomplete(a):
        raise Stop(f"batches not final: {incomplete(a)}")
    pop = dict(order_ids(a))
    rows, alone, no_ai_centre, reruns = [], 0, 0, 0
    for st in (1, 2, 3):
        for rid, r in finals(a, st).items():
            if not r["ai"]:
                if st == 3:
                    no_ai_centre += 1
                else:
                    alone += 1
                continue
            rows.append({"record_id": rid, "population": pop[rid], "stage": str(st), "author1": r["author1"],
                         "ai": r["ai"], "final": r["final"]})
    for p in sorted(a.state.glob("s*/*.ai.csv")):
        m = read_csv(p)
        reruns += any(r["attempt"] == "2" for r in m)
    cols = ["record_id", "population", "stage", "author1", "ai", "final"]
    write_csv(a.state / "screening.csv", cols, rows)
    # GSRR-37: agreement also for the first and second halves of the screening order
    pos = {rid: n for n, (rid, _) in enumerate(order_ids(a))}
    half = len(pos) / 2
    write_csv(a.state / "screening-half1.csv", cols, [r for r in rows if pos[r["record_id"]] < half])
    write_csv(a.state / "screening-half2.csv", cols, [r for r in rows if pos[r["record_id"]] >= half])
    f2 = finals(a, 2)
    for rid, r in f2.items():
        if r["e5_with"] and (r["e5_with"] not in f2 or f2[r["e5_with"]]["final"] != "include"):
            print(f"WARNING: {rid} is linked (E5) to {r['e5_with']}, which is not included at stage 2 (GSRR-33)")
    print(f"wrote screening.csv (and screening-half1.csv, screening-half2.csv: the first and second halves of the "
          f"screening order, GSRR-37): {len(rows)} rows. Re-run batches {reruns}; records decided by author 1 alone "
          f"(no valid AI output) {alone}; records without an AI centre {no_ai_centre}. "
          "Next: python3 c_synthesis.py --screening <state>/screening.csv")


# --- review-quotes / release -------------------------------------------------

ITEM_WHERE = re.compile(r"item|scale|questionnaire|survey|instrument|appendix|supplement|table|measure", re.I)
ITEM_TEXT = re.compile(r"\bI\b|\bmy\b|\bme\b|\bI'm\b|\bI am\b|strongly|agree|\(\d\s*=|\d\s*=\s*\w|\"|“", re.I)


def item_flag(where, text):
    """The pre-filled flag (GSRR-41): 'check' when the place or the wording looks like a scale item."""
    return "check" if text and (ITEM_WHERE.search(where or "") or ITEM_TEXT.search(text)) else ""


def ai_outputs(a):
    """Every accepted AI output: (record_id, stage, path, sha256) from the manifests, in the screening order."""
    out = []
    for p in sorted(a.state.glob("s*/*.ai.csv")):
        bstage = int(p.parent.name[1])
        batch = p.name.split(".")[0]
        w = work_dir(a, bstage, batch)
        for r in read_csv(p):
            if r["valid"] != "yes":
                continue
            f = w / f"out{r['stage']}" / f"{r['record_id']}.json"
            if not f.exists() or sha256(f) != r["sha256"]:
                raise Stop(f"{f} is missing or differs from the SHA-256 in {p.name}")
            out.append((r["record_id"], int(r["stage"]), f, r["sha256"], r["time_utc"], w.name))
    return out


def long_where(where):
    """A place description long enough to carry wording (more than 8 words, or quotation marks) is reviewed too."""
    return word_count(where) > 8 or bool(re.search(r"[\"“”]", where))


REVIEW_COLS = ["batch", "record_id", "stage", "field", "where", "text", "flag", "scale_item"]


def cmd_review_quotes(a):
    rows = []
    for rid, st, f, h, _, wb in ai_outputs(a):
        o = json.loads(f.read_text(encoding="utf-8"))
        for q in QUESTIONS:
            v = o["answers"].get(q) or {}
            if v and v["quote"].strip():
                rows.append({"batch": wb, "record_id": rid, "stage": st, "field": q, "where": v["where"], "text": v["quote"],
                             "flag": item_flag(v["where"], v["quote"])})
            if v and long_where(v["where"]):
                rows.append({"batch": wb, "record_id": rid, "stage": st, "field": f"{q}.where", "where": "", "text": v["where"],
                             "flag": item_flag("", v["where"])})
        if o["note"].strip():
            rows.append({"batch": wb, "record_id": rid, "stage": st, "field": "note", "where": "", "text": o["note"],
                         "flag": item_flag("", o["note"])})
    out = a.work / "quote-review.csv"
    if out.exists():
        raise Stop(f"{out} exists; author 1 may have filled it. Move it away to make a new one")
    write_csv(out, REVIEW_COLS, rows)
    print(f"wrote {out}: {len(rows)} rows, {sum(r['flag'] == 'check' for r in rows)} flagged. Author 1 fills "
          "scale_item with yes or no on every row (yes = it reproduces, in whole or in part, the wording of an item "
          "of a questionnaire or scale), then runs release")


def cmd_release(a):
    if incomplete(a):
        raise Stop(f"batches not final: {incomplete(a)}")
    rev_p = a.work / "quote-review.csv"
    if not rev_p.exists():
        raise Stop("run review-quotes first, and fill scale_item on every row")
    rev = {(r["batch"], r["record_id"], r["stage"], r["field"]): r for r in read_csv(rev_p)}
    bad = [k for k, r in rev.items() if r["scale_item"] not in ("yes", "no")]
    if bad:
        raise Stop(f"scale_item is not yes or no on {len(bad)} rows (first: {bad[0]})")
    answers, seen = [], set()
    for rid, st, f, h, t, wb in ai_outputs(a):
        o = json.loads(f.read_text(encoding="utf-8"))
        for q in QUESTIONS + ["note"]:
            v = (o["answers"].get(q) or {}) if q != "note" else {"answer": "", "where": "", "quote": o["note"]}
            if not v:
                continue
            text, where = v["quote"], v["where"]
            kw = (wb, rid, str(st), f"{q}.where")
            if q != "note" and long_where(where):
                if kw not in rev or rev[kw]["text"] != where:
                    raise Stop(f"quote-review.csv does not match the output of {rid} stage {st} {q}: run review-quotes again")
                seen.add(kw)
                if rev[kw]["scale_item"] == "yes":
                    where = "[removed: scale item]"
            k = (wb, rid, str(st), q)
            if text.strip():
                if k not in rev or rev[k]["text"] != text:
                    raise Stop(f"quote-review.csv does not match the output of {rid} stage {st} {q}: run review-quotes again")
                seen.add(k)
                if rev[k]["scale_item"] == "yes":
                    text = "[removed: scale item]"
            answers.append({"batch": wb, "record_id": rid, "stage": st, "question": q, "answer": v["answer"], "where": where,
                            "quote": text, "output_sha256": h, "output_time_utc": t,
                            "decision": o["decision"] if q == "note" else "", "code": o["code"] if q == "note" else "",
                            "centre": o["centre"] if q == "note" else ""})
    stale = set(rev) - seen
    if stale:
        raise Stop(f"quote-review.csv has {len(stale)} rows for outputs not released: run review-quotes again")
    pop = dict(order_ids(a))
    commit = {}
    for p in sorted(a.state.glob("s*/*.author1.csv")):
        ct = commit_time(a, p)
        if ct is None:
            raise Stop(f"{p.name} is not committed")
        man = p.with_name(p.name.replace(".author1.csv", ".ai.csv"))
        if not man.exists() or {r["author1_commit"] for r in read_csv(man)} != {ct[0]}:
            raise Stop(f"{p.name}: its latest commit is not the one the AI screener's manifest recorded")
        commit[(p.parent.name, p.name.split(".")[0])] = ct[1]
    f2 = finals(a, 2)
    bad_e5 = [rid for rid, r in f2.items() if r["e5_with"] and (r["e5_with"] not in f2 or
                                                                 f2[r["e5_with"]]["final"] != "include")]
    if bad_e5:
        raise Stop(f"E5 links to a record not included at stage 2 (GSRR-33): {bad_e5}")
    # every round of every batch (a revisited record appears once per round), in the order the batches were cut
    dec = []
    files = [p for pat in ("s1/*.final.csv", "s2/*.final2.csv", "s2/*.final3.csv") for p in sorted(a.state.glob(pat))]
    for p in files:
        batch, bs = p.name.split(".")[0], p.parent.name
        late_p = p.parent / f"{batch}.author1-late.csv"
        late_ids, late_time = set(), ""
        if late_p.exists() and p.name.endswith(".final3.csv"):
            ct = commit_time(a, late_p)
            if ct is None or {r["author1_late_commit"] for r in read_csv(p)} != {ct[0]}:
                raise Stop(f"{late_p.name}: its latest commit is not the one {p.name} recorded")
            late_ids, late_time = {r["record_id"] for r in read_csv(late_p)}, ct[1]
        rows = read_csv(p)
        for r in rows:
            dec.append({"record_id": r["record_id"], "population": pop[r["record_id"]], "stage": int(r["stage"]),
                        "batch": batch, "author1": r["author1"], "ai": r["ai"], "final": r["final"],
                        "exclusion_code": r["code"], "same_sample_as": r["e5_with"], "decided_by": r["decided_by"],
                        "decision_date": r["date"],
                        "author1_commit_utc": late_time if r["record_id"] in late_ids else commit[(bs, batch)]})
        if p.name.endswith(".final2.csv"):
            # centres given by a screener to a record not included in the end are released too (GSRR-41)
            A3, B3, _ = load_batch(a, 3, batch)
            final3 = p.parent / f"{batch}.final3.csv"
            in3 = {r["record_id"] for r in read_csv(final3)} if final3.exists() else set()
            for r in rows:
                i = r["record_id"]
                if i not in in3 and (i in A3 or i in B3):
                    dec.append({"record_id": i, "population": pop[i], "stage": 3, "batch": batch,
                                "author1": A3.get(i, ("", ""))[0], "ai": B3.get(i, ("", ""))[0], "final": "",
                                "exclusion_code": "", "same_sample_as": "", "decided_by": "not_included_at_full_text",
                                "decision_date": "", "author1_commit_utc": commit[(bs, batch)]})
    for r in dec:
        r["boundary_judged_by"] = ",".join(n for n in ("author1", "ai") if r[n] == "boundary") if r["stage"] == 3 else ""
    a.out.mkdir(parents=True, exist_ok=True)
    write_csv(a.out / "screening-decisions.csv",
              ["record_id", "population", "stage", "batch", "author1", "ai", "final", "exclusion_code",
               "same_sample_as", "boundary_judged_by", "decided_by", "decision_date", "author1_commit_utc"], dec)
    write_csv(a.out / "ai-screener-answers.csv",
              ["batch", "record_id", "stage", "question", "answer", "where", "quote", "decision", "code", "centre",
               "output_sha256", "output_time_utc"], answers)
    removed = sum(r["scale_item"] == "yes" for r in rev.values())
    print(f"wrote screening-decisions.csv ({len(dec)} rows) and ai-screener-answers.csv ({len(answers)} rows, "
          f"{removed} quotations removed as scale items) in {a.out}. Then run verify-removed")


def cmd_verify_removed(a):
    """The human check that the removal worked: none of the texts marked yes is left in the public file."""
    rev = [r for r in read_csv(a.work / "quote-review.csv") if r["scale_item"] == "yes"]  # quotations, notes, places
    cells = [v for r in read_csv(a.out / "ai-screener-answers.csv") for k, v in r.items() if k in ("quote", "where")]
    left = [f"{r['batch']} {r['record_id']} stage {r['stage']} {r['field']}" for r in rev if any(r["text"] in c for c in cells)]
    if left:
        raise Stop(f"{len(left)} scale-item quotations are still in the public file: {left}")
    print(f"none of the {len(rev)} quotations marked as scale items is in the public file")


# --- main --------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=["next", "prepare", "export-author", "gate", "check-ai", "differences",
                                        "export-final", "screening-csv", "review-quotes", "release",
                                        "verify-removed"])
    ap.add_argument("--stage", type=int, choices=[1, 2, 3])
    ap.add_argument("--batch")
    ap.add_argument("--short", action="store_true", help="next --stage 2: cut a smaller batch (2026-12-31)")
    ap.add_argument("--revisit", help="next --stage 2: comma-separated pending records to screen again (GSRR-33)")
    ap.add_argument("--out", type=Path, help="release: directory of the public files")
    for k, v in DEFAULTS.items():
        ap.add_argument(f"--{k}", type=Path, default=v)
    a = ap.parse_args(argv)
    for k in DEFAULTS:
        setattr(a, k, Path(os.path.expanduser(getattr(a, k))))
    needs_stage = {"next", "prepare", "export-author", "gate", "check-ai", "differences", "export-final"}
    try:
        if a.command in needs_stage and a.stage is None:
            raise Stop("--stage is needed")
        if a.command in needs_stage - {"next"} and not a.batch:
            raise Stop("--batch is needed")
        if a.command in {"next", "prepare", "export-author", "gate", "check-ai"} and a.stage == 3:
            raise Stop("stage 3 is judged with stage 2: use --stage 2")
        if a.command in {"release", "verify-removed"} and not a.out:
            raise Stop("--out is needed")
        fn = globals()["cmd_" + a.command.replace("-", "_")]
        return fn(a) or 0
    except Stop as e:
        print(f"STOPPED: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
