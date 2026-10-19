"""Make the workbook in which author 1 checks the key of the fictional cases (TRACE attachment 7, decision 58).

The key (key.csv, key-items.csv) was drafted with an AI assistant; author 1 checks every expected code before
registration. The workbook lists, case by case, each coded input of the key with its value and the finding it relates
to, and each C2b item code, with a column for author 1's check. The derived codes (exp_*) are not checked here: the
synthesis script derives them (check_validation_cases.py), so a corrected input changes them there.

The workbook carries the key, so it must not reach author 2 (who answers the cases without the key): it is written
outside the shared Drive folders.

Run: uv run --with openpyxl python make_key_check.py ~/TRACE ~/Documents/TRACE/key-check
"""

import csv
import datetime
import re
import sys
from pathlib import Path

from openpyxl import Workbook

TRACE = Path(sys.argv[1]).expanduser()
OUT = Path(sys.argv[2]).expanduser()
sys.path.insert(0, str(TRACE / "scripts"))
import trace_style as st  # noqa: E402

VC = TRACE / "registration-attachments" / "validation-cases"
CHECK = "未確認,合っている,違う,迷う"
WHAT = {   # what the coded input is (short Japanese gloss of the registration's GSRR-43)
    "main_instrument_identified": "主な尺度が特定できるか", "conclusion_identified": "主な結論の文が特定できるか",
    "title_ai_fatigue_term": "題に AI 疲労の語があるか（C6c）", "conclusion_ai_fatigue_term": "結論に AI 疲労の語があるか（C7 (ii)）",
    "conclusion_family": "結論の構成概念の語の系統（C7 (iii)）", "main_instrument_family": "主な尺度の名前の系統（C6a・C7 (iii)）",
    "C6a": "題の構成概念の語と主な尺度の名前（C6a）", "C6b": "因果の語とデザイン（C6b）", "design": "デザインの区分（C6b）",
    "ai_manipulated": "AI の側の変数を操作したか（C6b）",
}
for lv in ["L1a", "L1b", "L2", "L3", "L4", "L5", "L6"]:
    WHAT[f"C1_{lv}"] = f"C1 の水準 {lv} が当たるか"


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def case_texts():
    """The text of each case section of cases.md, keyed by its heading (V01 ...); variants (V05b) sit in their case."""
    text, out, cur = (VC / "cases.md").read_text(encoding="utf-8"), {}, None
    for line in text.splitlines():
        m = re.match(r"## (V\d+\w*)\s*$", line)
        if m:
            cur = m.group(1)
            out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def section(case_id, texts):
    return texts.get(case_id) or texts.get(re.sub(r"[a-z]+$", "", case_id), "")


def main():
    key, items, texts = read(VC / "key.csv"), read(VC / "key-items.csv"), case_texts()
    inputs = [c for c in key[0] if c not in ("case_id", "finding") and not c.startswith("exp_")]
    missing = [c for c in inputs if c not in WHAT]
    if missing:
        raise SystemExit(f"no gloss for the key columns {missing}")
    OUT.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    st.intro(wb.active, "TRACE｜反例集のキーの確かめ（第一著者）", f"作成 {datetime.date.today().isoformat()}・key.csv の {len(key)} 件・key-items.csv の {len(items)} 項目", [
        ("何をするか", [
            "AI と下書きした反例集のキーを、登録の前に第一著者がすべて確かめる（判断 58・findings.md の「not yet done」）。",
            "『入力のコード』と『項目のコード』の青い欄に、合っている・違う・迷う を選ぶ。違うときは正しい値とその理由を書く。",
            "事例の文は『事例』にある（cases.md と同じ）。定義は登録の下書き GSRR-43 と、決めた所見は findings.md（F1〜F7）。",
        ]),
        ("確かめなくてよいもの", ["導かれる値（C1 の代表値・C6c・C7 の 3 条件とまとめ）は集計の脚本が入力から導き、check_validation_cases.py がキーと照らす。入力を直せば、そちらで直る。"]),
        ("このファイルを渡さないこと", ["キーが入っているので、共著者（答えを見ずに解く）には渡さない。共有フォルダに置かない。"]),
        ("終わったら", ["違う・迷うの行をメインに渡す。メインが key.csv・key-items.csv と findings.md を直し、check_validation_cases.py を走らせる。"]),
    ])
    rows = []
    for r in key:
        for i, c in enumerate(inputs):
            rows.append([r["case_id"], c, WHAT[c], r[c], r["finding"] if i == 0 else "", "未確認", "", ""])
    ws = wb.create_sheet("入力のコード")
    cols = ["事例", "欄", "何を符号化するか", "キーの値", "関係する所見", "確認", "正しい値", "理由・メモ"]
    st.table(ws, cols, [8, 26, 36, 22, 10, 12, 18, 40], rows, inputs={"確認", "正しい値", "理由・メモ"},
             wrap={"何を符号化するか", "理由・メモ"}, tab="2563EB")
    st.choices(ws, cols, [("確認", CHECK)])
    ws2 = wb.create_sheet("項目のコード")
    cols2 = ["事例", "項目", "type", "boundary", "secondary_type", "target", "キーの注", "確認", "正しい値", "理由・メモ"]
    st.table(ws2, cols2, [8, 50, 8, 9, 13, 11, 30, 12, 18, 40],
             [[r["case_id"], r["item"], r["type"], r["boundary"], r["secondary_type"], r["target"], r["note"], "未確認", "", ""]
              for r in items], inputs={"確認", "正しい値", "理由・メモ"}, wrap={"項目", "キーの注", "理由・メモ"}, tab="2563EB")
    st.choices(ws2, cols2, [("確認", CHECK)])
    ws3 = wb.create_sheet("事例")
    st.table(ws3, ["事例", "文（cases.md）"], [8, 120], [[r["case_id"], section(r["case_id"], texts)] for r in key],
             wrap={"文（cases.md）"}, tab="64748B", height=lambda v: st.text_height((v[1], 120)))
    exp = [c for c in key[0] if c.startswith("exp_")]
    ws4 = wb.create_sheet("導かれる値（参考）")
    st.table(ws4, ["事例"] + exp, [8] + [16] * len(exp), [[r["case_id"]] + [r[c] for c in exp] for r in key], tab="64748B")
    path = OUT / "TRACE_反例集キーの確かめ.xlsx"
    if path.exists():
        raise SystemExit(f"{path} exists; author 1 may have filled it")
    wb.save(path)
    print(f"wrote {path}: {len(rows)} input codes, {len(items)} item codes")


if __name__ == "__main__":
    main()
