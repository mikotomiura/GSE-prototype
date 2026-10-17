"""Throwaway check: the verdict-count, split-count and PCr tables in notes.md against compare.json."""
import json
import re
import sys
from pathlib import Path

exp = Path(sys.argv[1])
c = json.loads((exp / "results/compare/compare.json").read_text(encoding="utf-8"))
full = (exp / "notes.md").read_text(encoding="utf-8")


def section(head):
    s = full.index(head)
    e = full.find("\n#", s + len(head))
    return full[s:e if e > 0 else None]


SEC = {"v": section("### 項目 1 の判定の数"), "s": section("### (j) 切り分けの読み"), "p": section("### PCr の読み")}
notes = ""
STEP = {"c100": ("1", "confound"), "d100": ("1", "drift"), "c200": ("2", "confound"),
        "f200": ("2", "factor"), "d200": ("2", "drift")}
AB = {"rd": "red_detected", "ru": "red_unconfirmed", "g": "green", "u": "undecidable"}
bad = 0


def row(prefix, sec):
    for line in SEC[sec].splitlines():
        if line.startswith(prefix):
            return [x.strip() for x in line.strip("|").split("|")]
    raise SystemExit(f"no row {prefix}")


def fail(msg):
    global bad
    bad += 1
    print("FAIL", msg)


# verdict counts
for step, (cc, w) in STEP.items():
    v = c["by_c"][cc]["worlds"][w]
    label = {"c100": "| c100（`h(1)`）", "c200": "| c200（`h(2)`）"}.get(step, f"| {step} |")
    cells = row(label, "v")
    for i, L in enumerate(("L300", "L60", "L1800")):
        got = {AB[k]: int(n) for k, n in re.findall(r"(rd|ru|g|u) (\d+)", cells[1 + i])}
        want = {k: n for k, n in v["verdict_counts"][L].items() if n}
        if got != want:
            fail(f"verdicts {step} {L}: notes {got} json {want}")
        if sum(got.values()) != 24:
            fail(f"verdicts {step} {L} sum {sum(got.values())}")
# split counts
cols = ["lr|none", "lr|R2", "lr|A2", "lrbin|R2", "hgb|none", "hgb|R2"]
for step, (cc, w) in STEP.items():
    sp = c["by_c"][cc]["worlds"][w]["split"]["counts"]
    cells = row(f"| {step} | ", "s")
    for i, col in enumerate(cols):
        x = sp[col]
        cell = cells[1 + i]
        if cell.startswith("読めない"):
            ok = x["unreadable"] == 24 and cell == "読めない 24"
        else:
            ok = cell == f'{x["remains"]} / {x["vanishes"]} / {x["undetermined"]} / {x["unreadable"]}'
        if not ok:
            fail(f"split {step} {col}: notes {cell} json {x}")
# PCr works and used
for step in ("d100", "d200", "f200"):
    cc, w = STEP[step]
    sp = c["by_c"][cc]["worlds"][w]["split"]
    for m in ("lr", "lrbin", "hgb"):
        cells = row(f"| {step} | {m} |", "p")
        for i, (var, fam) in enumerate((("none", "level"), ("R2", "level"), ("none", "var"), ("R2", "var"))):
            n = sp["pcr_counts"][f"{m}|{var}"][fam]["works"]
            if not re.match(rf"^{n}(\D|$)", cells[2 + i]):
                fail(f"pcr {step} {m} {var} {fam}: notes {cells[2 + i]} json {n}")
        used = [sum(z["used"] for z in sp["pcr_R2"][f"{m}|R2"][fam].values()) for fam in ("level", "var")]
        if not cells[6].startswith(f"{used[0]} / {used[1]}"):
            fail(f"used {step} {m}: notes {cells[6]} json {used}")
print("bad", bad)
sys.exit(1 if bad else 0)
