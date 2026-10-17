"""Dummy records (no real record) and checks for c_screening.py, end to end (decision 33).

Usage: uv run --with openpyxl python check_screening.py [work_dir]   (default: a fresh temporary directory)
Builds 20 dummy records, a screening database, a git repository with a remote, and dummy AI outputs; runs every
command of c_screening.py in the order of a real batch, and checks results and refusals with assert.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import c_screening as cs  # noqa: E402
import c_synthesis as syn  # noqa: E402
import make_trace_db  # noqa: E402
from openpyxl import load_workbook  # noqa: E402

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.mkdtemp(prefix="gse_screening_"))
root.mkdir(parents=True, exist_ok=True)
repo, remote, data, ftdir, work, pub = (root / n for n in ("repo", "remote.git", "data", "fulltext", "work", "pub"))
for d in (data, ftdir, work):
    d.mkdir()
state = repo / "screening"
xlsx = root / "db.xlsx"

N = 20
IDS = [f"D{i:02d}" for i in range(1, N + 1)]
POPS = ["students_learners", "workers_other", "unknown"]
WORDS = " ".join(["fatigue"] * 120 + ["artificial", "intelligence"] * 60)  # 240 words

# --- inputs: order, records, meta, full texts ---------------------------------
order = root / "order.csv"
order.write_text("".join(f"{POPS[i % 3]},{rid}\n" for i, rid in enumerate(IDS)), encoding="utf-8")
json.dump([{"id": rid, "title": f"Title of {rid}", "doi": f"10.0/{rid}", "year": 2026, "journal": "J", "source": "s",
            "group": "", "population": POPS[i % 3], "order": i, "origin": "o"} for i, rid in enumerate(IDS)],
          open(data / "records264.json", "w", encoding="utf-8"))
json.dump({rid: {"abstract": "" if rid == "D03" else f"Abstract of {rid}.", "abstract_source": "" if rid == "D03" else
                 "OpenAlex", "authors": "A", "oa_status": "gold", "fulltext": None} for rid in IDS},
          open(data / "meta.json", "w", encoding="utf-8"))
json.dump({rid: {"status": "saved", "url": ""} if rid == "D06" else
           {"status": "ok", "url": f"https://example.org/{rid}", "how": "Chrome"} for rid in IDS},
          open(data / "chrome_status.json", "w", encoding="utf-8"))
# full texts: html for most, XML with and without its extracted .txt, a short page, and none for D05 and D14
for rid in IDS:
    if rid in ("D05", "D14"):
        continue
    if rid == "D02":
        (ftdir / "D02.xml").write_text("<article><body><p>ignored</p></body></article>", encoding="utf-8")
        (ftdir / "D02.txt").write_text("EXTRACTED " + WORDS, encoding="utf-8")
    elif rid == "D04":
        (ftdir / "D04.xml").write_text(f"<article><body><sec><title>Methods</title><p>{WORDS}</p></sec></body></article>",
                                       encoding="utf-8")
    else:
        (ftdir / f"{rid}.html").write_text(f"<html><head><script>var x=1;</script></head><body><p>{WORDS}</p>"
                                           f"<p>Body of {rid}</p></body></html>", encoding="utf-8")


def run(*argv):
    return cs.main([*argv, "--state", str(state), "--order", str(order), "--work", str(work), "--data", str(data),
                    "--fulltext", str(ftdir), "--xlsx", str(xlsx)])


def must_stop(label, *argv):
    rc = run(*argv)
    assert rc == 3, (label, rc)


def git(*args):
    r = subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                       capture_output=True, text=True)
    assert r.returncode == 0, (args, r.stderr)
    return r.stdout


subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
subprocess.run(["git", "init", "-q", str(repo)], check=True)
git("remote", "add", "origin", str(remote))
(repo / "README").write_text("x", encoding="utf-8")
git("add", "README")
git("commit", "-q", "-m", "init")
git("push", "-q", "-u", "origin", "HEAD")


def commit_push(*paths):
    git("add", *[str(p) for p in paths])
    git("commit", "-q", "-m", "c")
    git("push", "-q")


# --- the screening database -----------------------------------------------------
sys.argv = ["make_trace_db.py", "--data", str(data), "--fulltext", str(ftdir), "--out", str(xlsx)]
make_trace_db.main()
wb = load_workbook(xlsx)
assert wb.sheetnames == ["はじめに", "段1", "段2・3", "文献DB", "全文", "判定基準"], wb.sheetnames
h1 = [c.value for c in wb["段1"][1]]
assert "全文" not in h1 and "ファイル" not in h1, h1  # GSRR-33: no full-text column at stage 1
assert [r[2].value for r in wb["段1"].iter_rows(min_row=2)] == [i // 9 + 1 for i in range(N)]


def fill(sheet, rid, **cells):
    wb = load_workbook(xlsx)
    ws = wb[sheet]
    head = [c.value for c in ws[1]]
    for row in ws.iter_rows(min_row=2):
        if row[0].value == rid:
            for k, v in cells.items():
                row[head.index(k)].value = v
            break
    else:
        raise AssertionError(rid)
    wb.save(xlsx)


def ai_out(w, rid, stage, decision, code="", centre="", quote="supporting words", read=None, **over):
    o = {"id": rid, "stage": stage, "read": read or ("abstract" if stage == 1 else "full text"), "source": "s",
         "answers": {q: {"answer": "yes", "where": "abstract, sentence 1", "quote": quote} for q in cs.QUESTIONS},
         "decision": decision, "code": code, "centre": centre, "note": "one sentence."}
    if stage == 1:
        o["answers"]["Q7"] = {}
    o.update(over)
    (w / f"out{stage}").mkdir(parents=True, exist_ok=True)
    (w / f"out{stage}" / f"{rid}.json").write_text(json.dumps(o), encoding="utf-8")


# --- stage 1, batch b01 ------------------------------------------------------------
must_stop("stage 3 next", "next", "--stage", "3")
must_stop("short at stage 1", "next", "--stage", "1", "--short")
assert run("next", "--stage", "1") == 0
NS = type("NS", (), {"state": state})()
b01 = cs.batch_ids(NS, 1, "b01")
assert b01 == IDS[:9], b01
assert run("prepare", "--stage", "1", "--batch", "b01") == 0
w1 = work / "s1-b01"

assert sorted(p.name for p in (w1 / "in").iterdir()) == [f"{i}.stage1.txt" for i in b01]
assert not list((w1 / "ft").iterdir())  # stage 1: no full text in the working directory
assert "Abstract (not retrieved):" in (w1 / "in" / "D03.stage1.txt").read_text(encoding="utf-8")
assert (w1 / "instructions.md").read_bytes() == cs.DEFAULTS["instructions"].read_bytes()
prompt = (w1 / "prompt.txt").read_text(encoding="utf-8")
assert ", ".join(b01) in prompt and str(w1) in prompt and "<up to nine" not in prompt and "<working" not in prompt

# author 1 fills stage 1: D01-D06 include, D07-D09 exclude E4 (D09 E2)
for rid in b01:
    fill("段1", rid, 判定="含める" if rid <= "D06" else "除外", 除外理由="" if rid <= "D06" else
         ("E2" if rid == "D09" else "E4"), 読んだ範囲="抄録")
fill("段1", "D01", 判定="未判定")
must_stop("undecided", "export-author", "--stage", "1", "--batch", "b01")
fill("段1", "D01", 判定="含める", 除外理由="E4")
must_stop("include with code", "export-author", "--stage", "1", "--batch", "b01")
fill("段1", "D01", 除外理由="", 読んだ範囲="全文")
must_stop("full text read at stage 1", "export-author", "--stage", "1", "--batch", "b01")
fill("段1", "D01", 読んだ範囲="抄録")
fill("段1", "D07", 除外理由="")
must_stop("exclude without code", "export-author", "--stage", "1", "--batch", "b01")
fill("段1", "D07", 除外理由="E4")
assert run("export-author", "--stage", "1", "--batch", "b01") == 0
a1 = state / "s1" / "b01.author1.csv"
must_stop("gate before commit", "gate", "--stage", "1", "--batch", "b01")
git("add", str(a1))
git("commit", "-q", "-m", "a")
must_stop("gate before push", "gate", "--stage", "1", "--batch", "b01")
time.sleep(1.1)
ai_out(w1, "D01", 1, "include")
must_stop("check-ai before push", "check-ai", "--stage", "1", "--batch", "b01")  # gate skipped (review 2)
(w1 / "out1" / "D01.json").unlink()
git("push", "-q")
assert run("gate", "--stage", "1", "--batch", "b01") == 0
must_stop("check-ai without outputs", "check-ai", "--stage", "1", "--batch", "b01")
assert not list(w1.glob("attempt*"))  # a check-ai run before the AI screener does not use up the re-run

# AI outputs: D05 exclude E4 (author included), D08 include (author excluded), D09 exclude E4 (author E2)
time.sleep(1.1)
for rid in b01:
    if rid == "D05":
        ai_out(w1, rid, 1, "exclude", "E4")
    elif rid == "D08":
        ai_out(w1, rid, 1, "include")
    elif rid in ("D07", "D09"):
        ai_out(w1, rid, 1, "exclude", "E4")
    else:
        ai_out(w1, rid, 1, "include", read="title only" if rid == "D03" else None)
must_stop("gate after outputs", "gate", "--stage", "1", "--batch", "b01")
old = time.time() - 3600
os.utime(w1 / "out1" / "D02.json", (old, old))  # an output older than author 1's commit (GSRR-33)
must_stop("output before commit", "check-ai", "--stage", "1", "--batch", "b01")
os.utime(w1 / "out1" / "D02.json")
with open(w1 / "instructions.md", "a", encoding="utf-8") as f:
    f.write("x")
try:
    must_stop("instructions changed", "check-ai", "--stage", "1", "--batch", "b01")
finally:
    (w1 / "instructions.md").write_bytes(cs.DEFAULTS["instructions"].read_bytes())
assert run("check-ai", "--stage", "1", "--batch", "b01") == 0
must_stop("check-ai twice", "check-ai", "--stage", "1", "--batch", "b01")
must_stop("export-author after AI", "export-author", "--stage", "1", "--batch", "b01")
man = cs.read_csv(state / "s1" / "b01.ai.csv")
assert len(man) == 9 and all(r["valid"] == "yes" and len(r["sha256"]) == 64 for r in man)
assert {r["author1_commit"] for r in man} == {git("log", "-1", "--format=%H", "--", str(a1)).strip()}
commit_push(state / "s1" / "b01.ai.csv")
keep05 = (w1 / "out1" / "D05.json").read_bytes()
(w1 / "out1" / "D05.json").write_bytes(keep05.replace(b"one sentence.", b"another sentence."))
must_stop("output changed after check-ai", "differences", "--stage", "1", "--batch", "b01")  # review 2, M3
(w1 / "out1" / "D05.json").write_bytes(keep05)

assert run("differences", "--stage", "1", "--batch", "b01") == 0
dtext = (w1 / "differences-1.md").read_text(encoding="utf-8")
assert "## D05" in dtext and "## D08" in dtext and "## D09" in dtext and "## D01" not in dtext
must_stop("final missing", "export-final", "--stage", "1", "--batch", "b01")
fill("段1", "D05", 最終="含める")
fill("段1", "D08", 最終="除外", 最終の除外理由="E3")
must_stop("codes differ", "export-final", "--stage", "1", "--batch", "b01")  # D09: E2 against E4
fill("段1", "D09", 最終="除外", 最終の除外理由="E2")
fill("段1", "D01", 最終="除外", 最終の除外理由="E4")
must_stop("final against agreement", "export-final", "--stage", "1", "--batch", "b01")
fill("段1", "D01", 最終=None, 最終の除外理由=None)
assert run("export-final", "--stage", "1", "--batch", "b01") == 0
f1 = {r["record_id"]: r for r in cs.read_csv(state / "s1" / "b01.final.csv")}
assert [f1[i]["final"] for i in b01] == ["include"] * 6 + ["exclude"] * 3
assert f1["D05"]["decided_by"] == "author1" and f1["D01"]["decided_by"] == "agreed"
assert f1["D08"]["code"] == "E3" and f1["D07"]["code"] == "E4"
commit_push(state / "s1" / "b01.final.csv")

# --- stage 1, batch b02: two format failures -> author 1 alone ------------------------
assert run("next", "--stage", "1") == 0
b02 = IDS[9:18]
assert run("prepare", "--stage", "1", "--batch", "b02") == 0
for rid in b02:
    fill("段1", rid, 判定="含める" if rid != "D18" else "除外", 除外理由="E1" if rid == "D18" else "")
assert run("export-author", "--stage", "1", "--batch", "b02") == 0
commit_push(state / "s1" / "b02.author1.csv")
assert run("gate", "--stage", "1", "--batch", "b02") == 0
w2 = work / "s1-b02"
time.sleep(1.1)
for rid in b02:
    ai_out(w2, rid, 1, "include", quote=" ".join(["w"] * 26))  # quotes longer than 25 words
assert run("check-ai", "--stage", "1", "--batch", "b02") == 1
assert (w2 / "attempt1" / "out1").exists() and not list((w2 / "out1").iterdir())
for rid in b02[:-1]:
    ai_out(w2, rid, 1, "include")  # second output: one record missing
assert run("check-ai", "--stage", "1", "--batch", "b02") == 0
man2 = cs.read_csv(state / "s1" / "b02.ai.csv")
assert all(r["valid"] == "no" and r["attempt"] == "2" for r in man2)
commit_push(state / "s1" / "b02.ai.csv")
assert run("differences", "--stage", "1", "--batch", "b02") == 0
assert run("export-final", "--stage", "1", "--batch", "b02") == 0
f2 = cs.read_csv(state / "s1" / "b02.final.csv")
assert all(r["decided_by"] == "author1_alone" and r["ai"] == "" for r in f2)
commit_push(state / "s1" / "b02.final.csv")

# --- stage 2 waits for stage 1 in order -----------------------------------------------
assert run("next", "--stage", "1") == 0  # b03: D19, D20 (last batch, smaller)
assert cs.batch_ids(NS, 1, "b03") == ["D19", "D20"]
must_stop("no record left", "next", "--stage", "1")
# passed so far: D01-D06 (b01) + D10-D17 (b02) = 14 >= 9 -> a full batch can be cut
assert run("next", "--stage", "2") == 0
s2b01 = cs.batch_ids(NS, 2, "b01")
assert s2b01 == ["D01", "D02", "D03", "D04", "D05", "D06", "D10", "D11", "D12"], s2b01
must_stop("stage 2 waits for b03", "next", "--stage", "2")  # 5 ready, D19 not final
must_stop("screening.csv with a batch not final", "screening-csv")  # review 2, HIGH-2
assert cs.incomplete(NS) == ["s1 b03", "s2 b01 (stage 2)"], cs.incomplete(NS)
assert run("prepare", "--stage", "1", "--batch", "b03") == 0
for rid in ("D19", "D20"):
    fill("段1", rid, 判定="除外", 除外理由="E4")
assert run("export-author", "--stage", "1", "--batch", "b03") == 0
commit_push(state / "s1" / "b03.author1.csv")
w5 = work / "s1-b03"
time.sleep(1.1)
ai_out(w5, "D19", 1, "exclude", "E4")
must_stop("check-ai without gate", "check-ai", "--stage", "1", "--batch", "b03")  # review 2, M4
(w5 / "out1" / "D19.json").unlink()
assert run("gate", "--stage", "1", "--batch", "b03") == 0
time.sleep(1.1)
for rid in ("D19", "D20"):
    ai_out(w5, rid, 1, "exclude", "E4")
assert run("check-ai", "--stage", "1", "--batch", "b03") == 0
commit_push(state / "s1" / "b03.ai.csv")
assert run("differences", "--stage", "1", "--batch", "b03") == 0
assert run("export-final", "--stage", "1", "--batch", "b03") == 0
commit_push(state / "s1" / "b03.final.csv")

# --- stage 2 and 3, batch b01 ----------------------------------------------------------
assert run("prepare", "--stage", "2", "--batch", "b01") == 0
w3 = work / "s2-b01"
assert sorted(p.name for p in (w3 / "in").iterdir()) == ["D05.stage1.txt"]  # no full text
ft = {p.stem: p.read_text(encoding="utf-8") for p in (w3 / "ft").iterdir()}
assert set(ft) == set(s2b01) - {"D05"}
assert ft["D02"].startswith("https://example.org/D02 (Europe PMC") and "EXTRACTED" in ft["D02"]
assert ft["D06"].startswith("https://doi.org/10.0/D06 (saved by author 1 in a web browser; publisher")
assert "Methods" in ft["D04"] and ft["D01"].startswith("https://example.org/D01 (publisher") and "var x" not in ft["D01"]
p2 = (w3 / "prompt.txt").read_text(encoding="utf-8")
assert "2. Records with a full text: D01, D02, D03, D04, D06, D10, D11, D12" in p2
assert "3. Records with no free full text found: D05" in p2 and "<IDs>" not in p2

# author 1: D01 include A, D02 include B, D03 include boundary, D04 exclude E2, D05 pending E6, D06 include A,
#           D10 pending (no code), D11 include A, D12 exclude E5 (same sample as D11)
plan = {"D01": ("含める", "", "中心-A"), "D02": ("含める", "", "中心-B"), "D03": ("含める", "", "境界（保留）"),
        "D04": ("除外", "E2", None), "D05": ("保留", "E6", None), "D06": ("含める", "", "中心-A"),
        "D10": ("保留", "", None), "D11": ("含める", "", "中心-A"), "D12": ("除外", "E5", None)}
for rid, (d, c, ce) in plan.items():
    fill("段2・3", rid, 判定=d, 除外理由=c, 中心=ce, 読んだ範囲="全文")
fill("段2・3", "D04", 中心="中心-A")
must_stop("centre on an exclusion", "export-author", "--stage", "2", "--batch", "b01")
fill("段2・3", "D04", 中心=None)
fill("段2・3", "D01", 中心=None)
must_stop("include without centre", "export-author", "--stage", "2", "--batch", "b01")
fill("段2・3", "D01", 中心="中心-A")
assert run("export-author", "--stage", "2", "--batch", "b01") == 0
au2 = cs.read_csv(state / "s2" / "b01.author1.csv")
assert [(r["record_id"], r["stage"]) for r in au2 if r["stage"] == "3"] == [(i, "3") for i in
                                                                            ("D01", "D02", "D03", "D06", "D11")]
commit_push(state / "s2" / "b01.author1.csv")
assert run("gate", "--stage", "2", "--batch", "b01") == 0
time.sleep(1.1)
# AI: D01 include A, D02 include A (differs), D03 include B, D04 include B (differs: author excluded),
#     D05 pending E6, D06 exclude E2 (differs: author included), D10 include boundary, D11 include A, D12 exclude E5
ai2 = {"D01": ("include", "", "centre-A"), "D02": ("include", "", "centre-A"), "D03": ("include", "", "centre-B"),
       "D04": ("include", "", "centre-B"), "D05": ("pending", "E6", None), "D06": ("exclude", "E2", None),
       "D10": ("include", "", "boundary"), "D11": ("include", "", "centre-A"), "D12": ("exclude", "E5", None)}
for rid, (d, c, ce) in ai2.items():
    ai_out(w3, rid, 2, d, c, read="title only" if rid == "D05" else None)
    if ce:
        ai_out(w3, rid, 3, "include", centre=ce,
               quote="I feel exhausted when I use the chatbot" if rid == "D01" else "supporting words")
(w3 / "out3" / "D06.json").write_text("{}", encoding="utf-8")
assert run("check-ai", "--stage", "2", "--batch", "b01") == 1  # out3 for a record the AI excluded
for d in ("out2", "out3"):
    for p in (w3 / "attempt1" / d).iterdir():
        if p.name != "D06.json" or d == "out2":
            os.replace(p, w3 / d / p.name)
must_stop("re-run that is the first output", "check-ai", "--stage", "2", "--batch", "b01")  # review 9
time.sleep(1.1)
for d in ("out2", "out3"):
    for p in (w3 / d).iterdir():
        os.utime(p)  # the AI screener's second run writes new files
assert run("check-ai", "--stage", "2", "--batch", "b01") == 0
man3 = cs.read_csv(state / "s2" / "b01.ai.csv")
assert all(r["attempt"] == "2" for r in man3) and sum(r["stage"] == "3" for r in man3) == 6
commit_push(state / "s2" / "b01.ai.csv")

assert run("differences", "--stage", "2", "--batch", "b01") == 0
d2 = (w3 / "differences-2.md").read_text(encoding="utf-8")
assert "## D04" in d2 and "## D06" in d2 and "## D10" in d2 and "## D01" not in d2
assert "centre-" not in d2  # the stage-2 differences do not show the AI screener's centre (decision 33)
must_stop("stage 3 before stage 2 final", "differences", "--stage", "3", "--batch", "b01")
fill("段2・3", "D04", 最終="含める")  # included in the end: author 1 needs a centre
fill("段2・3", "D06", 最終="含める")
fill("段2・3", "D10", 最終="除外", 最終の除外理由="E3")
fill("段2・3", "D12", 最終="除外", 最終の除外理由="E5", **{"同じ標本の相手（E5）": "D11"})
must_stop("late centre missing", "export-final", "--stage", "2", "--batch", "b01")
fill("段2・3", "D04", 中心="中心-B")
fill("段2・3", "D12", **{"同じ標本の相手（E5）": None})
must_stop("E5 without partner", "export-final", "--stage", "2", "--batch", "b01")
fill("段2・3", "D12", **{"同じ標本の相手（E5）": "D11"})
assert run("export-final", "--stage", "2", "--batch", "b01") == 0
fin2 = {r["record_id"]: r for r in cs.read_csv(state / "s2" / "b01.final2.csv")}
assert fin2["D05"]["final"] == "pending" and fin2["D05"]["code"] == "E6" and fin2["D05"]["decided_by"] == "agreed"
assert fin2["D12"]["e5_with"] == "D11" and fin2["D12"]["decided_by"] == "agreed"
assert fin2["D10"]["final"] == "exclude" and fin2["D04"]["final"] == "include"
late = cs.read_csv(state / "s2" / "b01.author1-late.csv")
assert [(r["record_id"], r["centre"]) for r in late] == [("D04", "B")]
must_stop("late centre not committed", "differences", "--stage", "3", "--batch", "b01")  # review 4
commit_push(state / "s2" / "b01.final2.csv", state / "s2" / "b01.author1-late.csv")

# stage 3: records included in the end: D01, D02, D03, D04, D06, D11
assert run("differences", "--stage", "3", "--batch", "b01") == 0
d3 = (w3 / "differences-3.md").read_text(encoding="utf-8")
assert "## D02" in d3 and "## D03" in d3 and "## D04" not in d3 and "## D01" not in d3
must_stop("stage 3 finals missing", "export-final", "--stage", "3", "--batch", "b01")
fill("段2・3", "D02", 最終の中心="中心-B")
fill("段2・3", "D03", 最終の中心="中心-B")
fill("段2・3", "D01", 最終の中心="中心-B")
must_stop("final against agreed centre", "export-final", "--stage", "3", "--batch", "b01")
fill("段2・3", "D01", 最終の中心=None)
assert run("export-final", "--stage", "3", "--batch", "b01") == 0
fin3 = {r["record_id"]: r for r in cs.read_csv(state / "s2" / "b01.final3.csv")}
assert set(fin3) == {"D01", "D02", "D03", "D04", "D06", "D11"}
assert fin3["D06"]["ai"] == "" and fin3["D06"]["decided_by"] == "author1_alone" and fin3["D06"]["final"] == "A"
assert fin3["D04"]["ai"] == "B" and fin3["D04"]["author1"] == "B" and fin3["D04"]["decided_by"] == "agreed"
assert fin3["D03"]["author1"] == "boundary" and fin3["D03"]["final"] == "B"
commit_push(state / "s2" / "b01.final3.csv")

# --- a pending record screened again when its full text is found (GSRR-33, decision 33) ------
must_stop("revisit a record that is not pending", "next", "--stage", "2", "--revisit", "D01")
must_stop("revisit at stage 1", "next", "--stage", "1", "--revisit", "D05")
must_stop("revisit without a full text", "next", "--stage", "2", "--revisit", "D05")  # review 2, LOW-1
(ftdir / "D05.html").write_text(f"<html><body><p>{WORDS}</p></body></html>", encoding="utf-8")
assert run("next", "--stage", "2", "--revisit", "D05") == 0
must_stop("revisit twice", "next", "--stage", "2", "--revisit", "D05")
assert cs.batch_ids(NS, 2, "b02") == ["D05"]
assert run("prepare", "--stage", "2", "--batch", "b02") == 0
w4 = work / "s2-b02"
assert [p.name for p in (w4 / "ft").iterdir()] == ["D05.txt"]
fill("段2・3", "D05", 判定="含める", 除外理由=None, 中心="中心-A", 最終="保留")
must_stop("revisit with an old 最終", "export-author", "--stage", "2", "--batch", "b02")  # review 2, M2
fill("段2・3", "D05", 最終=None)
assert run("export-author", "--stage", "2", "--batch", "b02") == 0
commit_push(state / "s2" / "b02.author1.csv")
assert run("gate", "--stage", "2", "--batch", "b02") == 0
time.sleep(1.1)
ai_out(w4, "D05", 2, "include", quote="other words")  # the second round quotes differently (review 2, HIGH-1)
ai_out(w4, "D05", 3, "include", centre="centre-A", quote="other words")
assert run("check-ai", "--stage", "2", "--batch", "b02") == 0
commit_push(state / "s2" / "b02.ai.csv")
assert run("differences", "--stage", "2", "--batch", "b02") == 0
assert run("export-final", "--stage", "2", "--batch", "b02") == 0
commit_push(state / "s2" / "b02.final2.csv")
must_stop("release with stage 3 not final", "release", "--out", str(pub))  # review 2, HIGH-2
assert cs.incomplete(NS) == ["s2 b02 (stage 3)"], cs.incomplete(NS)
assert "D05" not in cs.stage3_records(NS, "b01") and cs.stage3_records(NS, "b02") == ["D05"]  # review 2, M1
assert run("differences", "--stage", "3", "--batch", "b02") == 0
assert run("export-final", "--stage", "3", "--batch", "b02") == 0
commit_push(state / "s2" / "b02.final3.csv")
assert cs.finals(NS, 2)["D05"]["final"] == "include"

# --- screening.csv and the agreement of c_synthesis.py ------------------------------------
assert run("screening-csv") == 0
h1, h2 = (cs.read_csv(state / f"screening-half{n}.csv") for n in (1, 2))
assert len(h1) + len(h2) == len(cs.read_csv(state / "screening.csv"))
assert all(int(r["record_id"][1:]) <= 10 for r in h1) and all(int(r["record_id"][1:]) > 10 for r in h2)
rows = syn.load_screening(state / "screening.csv")
st = {k: [r for r in rows if r["stage"] == k] for k in ("1", "2", "3")}
assert len(st["1"]) == 11 and len(st["2"]) == 9 and len(st["3"]) == 6, {k: len(v) for k, v in st.items()}
ag = {r["stage"]: r for r in syn.screening_agreement(rows)}
# D09 differs in its code only: the agreement compares decisions, so stage 1 has 2 differences (D05, D08)
assert ag[1]["differed"] == 2 and ag[1]["decided_as_author1"] == 2 and ag[1]["decided_as_ai"] == 0, ag[1]
assert ag[2]["differed"] == 3, ag[2]
assert ag[3]["boundary_either"] == 1 and ag[3]["differed"] == 2

# --- review-quotes, release, verify-removed -----------------------------------------------
must_stop("release before review", "release", "--out", str(pub))
assert run("review-quotes") == 0
rev = cs.read_csv(work / "quote-review.csv")
item = [r for r in rev if r["text"].startswith("I feel")]
assert item and all(r["flag"] == "check" for r in item)
must_stop("review twice", "review-quotes")
must_stop("release unconfirmed", "release", "--out", str(pub))
for r in rev:
    r["scale_item"] = "yes" if r["text"].startswith("I feel") else "no"
cs.write_csv(work / "quote-review.csv", cs.REVIEW_COLS, rev)
assert run("release", "--out", str(pub)) == 0
assert run("verify-removed", "--out", str(pub)) == 0
pub_text = (pub / "ai-screener-answers.csv").read_text(encoding="utf-8")
assert "I feel exhausted" not in pub_text and "[removed: scale item]" in pub_text
dec = cs.read_csv(pub / "screening-decisions.csv")
d10 = [r for r in dec if r["record_id"] == "D10" and r["stage"] == "3"]
assert [(r["ai"], r["final"], r["boundary_judged_by"]) for r in d10] == [("boundary", "", "ai")], d10  # review 11
assert [(r["batch"], r["final"]) for r in dec if r["record_id"] == "D05" and r["stage"] == "2"] == \
    [("b01", "pending"), ("b02", "include")]
d04 = [r for r in dec if r["record_id"] == "D04" and r["stage"] == "3"]
assert d04[0]["author1_commit_utc"] != [r for r in dec if r["record_id"] == "D01" and r["stage"] == "3"][0][
    "author1_commit_utc"]  # a late centre carries the time of its own commit
assert [r["boundary_judged_by"] for r in dec if r["record_id"] == "D03" and r["stage"] == "3"] == ["author1"]
assert all(r["author1_commit_utc"] for r in dec)
for p in pub.iterdir():
    t = p.read_text(encoding="utf-8")
    assert "Abstract of" not in t and "fatigue fatigue" not in t and "EXTRACTED" not in t  # no abstract or full text
# a check that would miss nothing: a removed quote left in the public file is caught
with open(pub / "ai-screener-answers.csv", "a", encoding="utf-8") as f:
    f.write('D01,3,Q1,yes,x,"I feel exhausted when I use the chatbot",,,,,\n')
must_stop("removed quote left", "verify-removed", "--out", str(pub))
f2p = state / "s2" / "b01.final2.csv"
keep = f2p.read_text(encoding="utf-8")
f2p.write_text(keep.replace("D12,2,exclude,exclude,exclude,E5,D11", "D12,2,exclude,exclude,exclude,E5,D10"), encoding="utf-8")
assert f2p.read_text(encoding="utf-8") != keep
must_stop("E5 partner not included", "release", "--out", str(pub))
f2p.write_text(keep, encoding="utf-8")
# changing author 1's late centres after the stage-3 decisions is caught at release
with open(state / "s2" / "b01.author1-late.csv", "a", encoding="utf-8") as f:
    f.write("D06,3,,,B,full text\n")
commit_push(state / "s2" / "b01.author1-late.csv")
must_stop("late centres changed", "release", "--out", str(pub))
git("reset", "-q", "--hard", "HEAD~1")
git("push", "-q", "-f")  # the temporary remote only
# changing author 1's file after the AI screener ran is caught at release
with open(state / "s1" / "b01.author1.csv", "a", encoding="utf-8") as f:
    f.write("D99,1,include,,,\n")
commit_push(state / "s1" / "b01.author1.csv")
must_stop("author file changed after AI", "release", "--out", str(pub))

# --- format errors, one by one --------------------------------------------------------------
good = json.loads((w1 / "out1" / "D01.json").read_text(encoding="utf-8"))
bad_dir = root / "bad"
bad_dir.mkdir()


def errs(obj, stage=1, rid="D01"):
    p = bad_dir / f"{rid}.json"
    p.write_text(obj if isinstance(obj, str) else json.dumps(obj), encoding="utf-8")
    return cs.output_errors(p, rid, stage)


assert errs(good) == []
assert errs("not json") == ["not valid JSON"]
assert errs(dict(good, extra=1))[0].startswith("fields differ")
assert errs(dict(good, id="D02")) == ["id does not match the file name"]
assert errs(dict(good, stage=2)) != []
assert errs(dict(good, read="full text")) == ["read"]
assert errs(dict(good, decision="pending")) == ["decision"]
assert errs(dict(good, code="E9")) == ["code"]
assert errs(dict(good, code="E4")) == ["code does not fit the decision"]
assert errs(dict(good, centre="centre-A")) == ["centre not empty before stage 3"]
assert errs(dict(good, answers=dict(good["answers"], Q1={"answer": "maybe", "where": "", "quote": ""}))) == \
    ["answers.Q1.answer"]
assert errs(dict(good, answers=dict(good["answers"], Q7={"answer": "no", "where": "", "quote": ""}))) == \
    ["answers.Q7 not empty at stage 1"]
long_q = " ".join(["word"] * 26)
e = errs(dict(good, answers=dict(good["answers"], Q2={"answer": "yes", "where": "", "quote": long_q})))
assert e == ["answers.Q2.quote longer than 25 words (26)"] and "word word" not in e[0]
signs = " ".join(["word"] * 24 + ["n", "=", "120", "-"])  # 26 words, 2 signs: 26 > 25
assert errs(dict(good, answers=dict(good["answers"], Q2={"answer": "yes", "where": "", "quote": signs}))) != []
signs = " ".join(["word"] * 23 + ["n", "=", "120", "-"])  # 25 words and 2 signs: accepted
assert errs(dict(good, answers=dict(good["answers"], Q2={"answer": "yes", "where": "", "quote": signs}))) == []
q7 = {"answer": "no", "where": "Methods", "quote": ""}
assert errs(dict(good, stage=3, read="full text", centre="middle", answers=dict(good["answers"], Q7=q7)), stage=3) \
    == ["centre"]
# review 3: values of the wrong type are format errors, not crashes
assert errs(dict(good, read=[])) == ["read not text"]
assert errs(dict(good, decision={}, code=[])) == ["decision not text", "code not text"]
assert errs(dict(good, stage=True)) == ["stage"]
assert errs(dict(good, answers=dict(good["answers"], Q1={"answer": ["yes"], "where": "", "quote": ""}))) == \
    ["answers.Q1.answer"]
# review 7: Japanese counts as one word per two characters (50 characters)
ja = dict(good["answers"], Q2={"answer": "yes", "where": "", "quote": "あ" * 51})
assert errs(dict(good, answers=ja)) == ["answers.Q2.quote longer than 25 words (26)"]
ja = dict(good["answers"], Q2={"answer": "yes", "where": "", "quote": "あ" * 50})
assert errs(dict(good, answers=ja)) == []
assert cs.word_count("AI疲労の尺度 n = 120") == 6  # AI 1 + five kanji/kana 3 + n 1 + 120 1; "=" is not a word
# no error message carries a value from the output
sentinel = "SENTINELVALUE"
for o in (dict(good, read=sentinel), dict(good, decision=sentinel), dict(good, code=sentinel), dict(good, id=sentinel)):
    assert all(sentinel not in m for m in errs(o)), errs(o)

# review 1: an agreed E5 needs its partner
try:
    cs.final_row("X", 2, ("exclude", "E5"), ("exclude", "E5"), {})
    raise AssertionError("E5 without partner accepted")
except cs.Stop as ex:
    assert "E5 needs" in str(ex)
# review 10: E5 and E6 are not stage-1 codes
try:
    cs.check_decision("X", 1, "exclude", "E6")
    raise AssertionError("E6 accepted at stage 1")
except cs.Stop:
    pass
assert errs(dict(good, decision="exclude", code="E6")) == ["code not used at stage 1"]

# a full text that gives almost no words stops prepare
(ftdir / "D19.html").write_text("<p>too short</p>", encoding="utf-8")
try:
    cs.fulltext_input("D19", ftdir, "u")
    raise AssertionError("short full text accepted")
except cs.Stop as ex:
    assert "fewer than 200 words" in str(ex)

print(f"screening tools checked in {root}; all checks passed")
