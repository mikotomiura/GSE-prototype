"""Throwaway check: the tables in notes.md against results/<step>/main/*.json (prints bad 0 when they agree).

Outside the instrument's fingerprint (not under scripts/). Run: python check_notes.py .
"""
import json
import re
import sys
from pathlib import Path

exp = Path(sys.argv[1])
notes = (exp / "notes.md").read_text(encoding="utf-8")
CANDS = ["D-run-hold-sec", "D-all-hold-sec", "S-raw-hold-sec", "S-raw-hold-sub", "S-rank-hold-sec", "S-rank-hold-sub"]
AB = {"rd": "red_detected", "u": "undecidable"}
KINDS = ["full/hgb", "full/lr", "small/hgb", "small/lr"]
bad = 0


def fail(msg):
    global bad
    bad += 1
    print("FAIL", msg)


def load(step, name):
    return json.loads((exp / "results" / step / "main" / name).read_text(encoding="utf-8"))


def rows(prefix):
    out = [[x.strip() for x in ln.strip().strip("|").split("|")] for ln in notes.splitlines() if ln.startswith(prefix)]
    if not out:
        fail(f"no row {prefix}")
    return out


def nums(cell):
    return [float(x) for x in re.findall(r"-?\d+\.\d+", cell)]


def close(got, want, tag, tol=0.0015):
    if len(got) != len(want) or any(abs(g - w) > tol for g, w in zip(got, want)):
        fail(f"{tag}: notes {got} json {[round(w, 3) for w in want]}")


for step in ("g050", "f200"):
    s, e, d = load(step, "summary.json"), load(step, "e13.json"), load(step, "describe.json")
    # verdicts
    for base, key in (("A（主）", "A"), ("A_speed（副）", "A_speed")):
        cells = rows(f"| {step} | {base} |")[0][2:]
        for c, cell in zip(CANDS, cells):
            ab = cell.split("（")[0].strip()
            if AB.get(ab) != s["verdicts"][key][c]:
                fail(f"verdict {step} {key} {c}: notes {ab} json {s['verdicts'][key][c]}")
    # AUC and speed_minus_A
    cells = [r for r in rows(f"| {step} | 0.") if len(r) == 4][0]
    close(nums(cells[1]), [s["auc"]["A"]["hgb"], s["auc"]["A"]["lr"]], f"aucA {step}")
    close(nums(cells[2]), [s["auc"]["A_speed"]["hgb"], s["auc"]["A_speed"]["lr"]], f"aucS {step}")
    sm = s["speed_minus_A"]
    close(nums(cells[3]), [sm["hgb"]["diff"], *sm["hgb"]["ci95"], sm["lr"]["diff"], *sm["lr"]["ci95"]], f"sma {step}")
    # max gains over A
    cells = [r for r in rows(f"| {step} | 0.") if len(r) == 7][0][1:]
    for c, cell in zip(CANDS, cells):
        x = e["A"]["configs"][c]
        close(nums(cell), [x["gain_max"], x["lower_max"], x["upper_max"]], f"gain {step} {c}")
    # dropped
    for c, short in (("D-run-hold-sec", "D-run"), ("D-all-hold-sec", "D-all")):
        cells = rows(f"| {step} | {short} |")[0][2:]
        att = e["A"]["configs"][c]["attackers"]
        close(nums(cells[0]), [att[k]["gain"] for k in KINDS], f"none {step} {c}")
        for cell, w in zip(cells[1:], ("without_a", "without_r", "without_smooth")):
            close(nums(cell), [e["A"]["dropped"][c][w][k]["gain"] for k in KINDS], f"{w} {step} {c}")
    # d2
    names = CANDS + ["PC-corr"]
    for lab, key in (("窓の打鍵の数（全量）", "item3_presses_r2"), ("窓の打鍵の数（滑らかさだけ）", "d2_presses_r2_smooth"),
                     ("セッションの倍率 `u`（全量）", "d2_u_r2"), ("セッションの倍率 `u`（滑らかさだけ）", "d2_u_r2_smooth")):
        if key.startswith("d2_u") and step == "g050":
            continue
        cells = rows(f"| {step} | {lab} |")[0][2:]
        close([float(x) for x in cells], [d[n][key] for n in names], f"d2 {step} {key}")

print("bad", bad)
