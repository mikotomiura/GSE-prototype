"""summary.md の主表を、6 回の一次の JSON と照らす（design の「check_summary.py」）。

使い方（この dir で）:
    python check_summary.py          # 照合。bad 0 なら終了コード 0
    python check_summary.py --emit   # 一次から期待の行を出す（表を書くときの写し元）

主表は summary.md の `<!-- main-table:begin -->` と `<!-- main-table:end -->` の間。
各行の最初の列は行の鍵で、SOURCES が鍵ごとに一次の場所を持つ。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXP = ROOT / "experiments"

R1 = "20261012-rhythm-stage-desk-check"
R2 = "20261013-rhythm-stage-round2"
GW = "20261014-rhythm-stage-graded-world"
CW = "20261014-rhythm-stage-speed-confound-world"
SW = "20261015-rhythm-stage-speed-shape-world"

LABELS = ("L300", "L60", "L1800")
N_CAND = 24

# 鍵 → (種類, 入れ物, 段)
#   main:     本番を回した段（summary.json の判定と _detector の AUC）
#   ceiling:  天井で止めた段（ceiling.json の steps の status と L300 の AUC）
#   unusable: 第 1 回の 1 回目の下見 0 で使えなかった world（choice.per_world）
SOURCES = {
    "r1-v2": ("unusable", R1, "v2"),
    "r1-v3": ("unusable", R1, "v3"),
    "r1-v4": ("main", R1, None),
    "r2-v4": ("main", R2, None),
    "g-t025": ("ceiling", GW, "t025"),
    "g-t050": ("ceiling", GW, "t050"),
    "g-t075": ("ceiling", GW, "t075"),
    "h-c050": ("ceiling", CW, "c050"),
    "h-c100": ("main", CW, "c100"),
    "h-c200": ("main", CW, "c200"),
    "f-f100": ("ceiling", SW, "f100"),
    "f-f200": ("main", SW, "f200"),
    "d-d100": ("main", SW, "d100"),
    "d-d200": ("main", SW, "d200"),
}

JP = {
    "green": "緑",
    "red_detected": "赤・検出",
    "red_unconfirmed": "赤・未確認",
    "undecidable": "判定不能",
}
ORDER = ("緑", "赤・検出", "赤・未確認", "判定不能")
NOT_RUN = {"ceiling": "走っていない（天井）", "unusable": "走っていない（使えない）"}
STATE = {"main": "先へ進む", "ceiling": "天井", "unusable": "使えない"}


def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def counts_text(verdicts: list[str], bad: list[str], key: str, label: str) -> str:
    c = {k: 0 for k in ORDER}
    for v in verdicts:
        if v == "red_detected_stop_path":
            bad.append(f"{key} {label}: red_detected_stop_path が出ている（まとめは 0 本を前提にしている）")
            v = "red_detected"
        if v not in JP:
            bad.append(f"{key} {label}: 知らない判定 {v!r}")
            continue
        c[JP[v]] += 1
    if sum(c.values()) != N_CAND:
        bad.append(f"{key} {label}: 判定の合計が {sum(c.values())}（{N_CAND} でない）")
    return "・".join(f"{k} {c[k]}" for k in ORDER if c[k])


def main_dir(box: str, step: str | None) -> Path:
    if step is None:
        return EXP / box / "results" / "main"
    return EXP / box / "results" / step / "main"


def has_ceiling_dir(box: str) -> bool:
    return (EXP / box / "results" / "ceiling").exists()


def main_state(key: str, box: str, step: str | None, bad: list[str]) -> str:
    """本番を回した段の「下見 0」の列を一次から決める。"""
    if box in (R1, R2):
        # 第 1 回・第 2 回の本番の world は provenance.json の worlds で確かめる
        worlds = load(main_dir(box, step) / "provenance.json").get("worlds")
        if worlds != ["v4"]:
            bad.append(f"{key}: 本番の provenance の worlds が {worlds!r}（v4 でない）")
    if box == R2:
        # 第 2 回は下見 0 を回していない（第 1 回の固定で選んだ v4 を使う）
        if has_ceiling_dir(box):
            bad.append(f"{key}: 第 2 回に results/ceiling がある（下見 0 を回していない前提）")
        return "—（第 1 回の v4）"
    c = load(EXP / box / "results" / "ceiling" / "ceiling.json")
    if box == R1:
        ok = c["choice"]["chosen"] == "v4" and c["choice"]["per_world"]["v4"]["usable"]
    else:
        ok = c["steps"][step]["status"] == "go"
    if not ok:
        bad.append(f"{key}: 下見 0 で先へ進む段になっていない")
    return STATE["main"]


def expected(key: str, bad: list[str]) -> list[str]:
    kind, box, step = SOURCES[key]
    state = STATE[kind]
    kinds_text = "—"
    if kind == "main":
        s = load(main_dir(box, step) / "summary.json")
        cands = sorted(k for k in s if k.startswith("S-"))
        if len(cands) != N_CAND:
            bad.append(f"{key}: summary.json の候補が {len(cands)} 本")
        det = s["_detector"]["L300"]
        auc = det["auc_A_speed"]
        aucs = (auc["hgb"], auc["lr"])
        kinds_text = "・".join(sorted(det["ceiling_kinds"])) or "なし"
        state = main_state(key, box, step, bad)
        source = "本番"
        cols = [counts_text([s[c][lab] for c in cands], bad, key, lab) for lab in LABELS]
    elif kind == "ceiling":
        c = load(EXP / box / "results" / "ceiling" / "ceiling.json")
        st = c["steps"][step]
        if st["status"] != "ceiling":
            bad.append(f"{key}: ceiling.json の status が {st['status']!r}")
        aucs = tuple(st["L300_auc_A_speed"])
        source = "下見 0"
        cols = [NOT_RUN["ceiling"]] * 3
    else:
        c = load(EXP / box / "results" / "ceiling-1" / "ceiling.json")
        pw = c["choice"]["per_world"][step]
        if pw["usable"]:
            bad.append(f"{key}: ceiling-1 で usable が真")
        r = c["results"][step]["L300"]
        aucs = (r["hgb"]["auc_A_speed"], r["lr"]["auc_A_speed"])
        source = "下見 0（P 40）"
        cols = [NOT_RUN["unusable"]] * 3
    auc_text = f"{aucs[0]:.3f} / {aucs[1]:.3f}"
    return [key, state, source, auc_text, kinds_text, *cols]


def table_rows(text: str, bad: list[str]) -> dict[str, list[str]]:
    m = re.search(r"<!-- main-table:begin -->(.*?)<!-- main-table:end -->", text, re.S)
    if not m:
        bad.append("summary.md に主表の印が無い")
        return {}
    rows: dict[str, list[str]] = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|") or set(line) <= set("|-: "):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        cells[0] = cells[0].strip("`")
        key = cells[0]
        if key == "鍵":
            continue
        if key in rows:
            bad.append(f"主表の鍵 {key} が重複")
        rows[key] = cells
    return rows


# 主表の列: 鍵 | 回 | world と段 | 下見 0 | AUC の出どころ | L300 の AUC(A_speed) hgb / lr |
#           L300 で外した分類器 | L300 | L60 | L1800
# 照らすのは 鍵・下見 0・出どころ・AUC・外した分類器・3 ラベル（回と world の説明の列は照らさない。
# ただし探索的と併記する段は world の列に「探索的」を含むことを確かめる）
N_COLS = 10
CHECK_COLS = (0, 3, 4, 5, 6, 7, 8, 9)
# 探索的と併記する段は一次の JSON に印が無い（揺れの world の notes「接続」の規則 (f) による）ので、
# 鍵を定数で持つ。表の world の列と、本文の §4・§7 の併記の文（EXPLORATORY_TEXT が 2 回以上）を確かめる。
EXPLORATORY = {"h-c200"}
EXPLORATORY_TEXT = "`h(2)` は探索的と併記"

# 読みの表（split-table）: 段 → compare.json の (c, world)。列は lr|none・lr|R2・lrbin|R2・hgb|none・hgb|R2
SPLIT_ROWS = {"h(1)": ("1", "confound"), "d(1)": ("1", "drift"), "h(2)": ("2", "confound"),
              "f(2)": ("2", "factor"), "d(2)": ("2", "drift")}
SPLIT_COLS = ("lr|none", "lr|R2", "lrbin|R2", "hgb|none", "hgb|R2")


def split_cell(c: dict) -> str:
    n = (c["remains"], c["vanishes"], c["undetermined"], c["unreadable"])
    if n[3] == N_CAND:
        return f"読めない {N_CAND}"
    if sum(n) != N_CAND:
        return f"合計が {sum(n)}"
    return " / ".join(str(x) for x in n)


def check_split(text: str, bad: list[str]) -> int:
    m = re.search(r"<!-- split-table:begin -->(.*?)<!-- split-table:end -->", text, re.S)
    if not m:
        bad.append("summary.md に読みの表の印が無い")
        return 0
    comp = load(EXP / SW / "results" / "compare" / "compare.json")
    seen = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line.startswith("| `"):
            continue
        cells = [c.strip().replace(r"\|", "|") for c in line.strip("|").split(" | ")]
        key = cells[0].strip("`")
        if key in seen:
            bad.append(f"読みの表の段 {key} が重複")
        seen[key] = cells
    for key, (c, world) in SPLIT_ROWS.items():
        if key not in seen:
            bad.append(f"読みの表に段 {key} が無い")
            continue
        counts = comp["by_c"][c]["worlds"][world]["split"]["counts"]
        exp = [split_cell(counts[v]) for v in SPLIT_COLS]
        got = seen[key][1:]
        if got != exp:
            bad.append(f"読みの表 {key}: 表 {got} ／ 一次 {exp}")
    for key in seen:
        if key not in SPLIT_ROWS:
            bad.append(f"読みの表に知らない段 {key}")
    return len(seen)


def main(argv: list[str]) -> int:
    bad: list[str] = []
    if "--emit" in argv:
        for key in SOURCES:
            e = expected(key, bad)
            print("| `" + e[0] + "` | | | " + " | ".join(e[1:]) + " |")  # 回と world の列は手で書く
        for b in bad:
            print("bad:", b)
        return 1 if bad else 0
    text = (HERE / "summary.md").read_text(encoding="utf-8")
    rows = table_rows(text, bad)
    for key in SOURCES:
        if key not in rows:
            bad.append(f"主表に鍵 {key} が無い")
            continue
        cells = rows[key]
        if len(cells) != N_COLS:
            bad.append(f"{key}: 列の数が {len(cells)}（{N_COLS} でない）")
            continue
        got = [cells[i] for i in CHECK_COLS]
        e = expected(key, bad)
        if got != e:
            bad.append(f"{key}: 主表 {got} ／ 一次 {e}")
        if key in EXPLORATORY and "探索的" not in cells[2]:
            bad.append(f"{key}: 探索的と併記する段なのに world の列に「探索的」が無い")
    if text.count(EXPLORATORY_TEXT) < 2:
        bad.append(f"本文に「{EXPLORATORY_TEXT}」が 2 回以上無い（§4・§7）")
    n_split = check_split(text, bad)
    for key in rows:
        if key not in SOURCES:
            bad.append(f"主表に知らない鍵 {key}")
    for b in bad:
        print("bad:", b)
    print(f"rows {len(rows)} / sources {len(SOURCES)} / split rows {n_split} / bad {len(bad)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
