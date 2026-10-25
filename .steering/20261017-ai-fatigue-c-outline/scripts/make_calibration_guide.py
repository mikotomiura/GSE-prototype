"""較正の 1 回分の案内の冊を作る（判断 106）。

シートは はじめに・一覧（探索の集合の 11 研究と全文へのリンク）・ZEF（どの記録にも使われないので符号化の冊に
入らない ZEF の 15 項目を、C2b の型・境界・対象だけ符号化する表）。選び肢は c_coding_book.py の listed() と同じ。
ZEF の項目の文は核 1 の items.csv から、項目の文と前置きだけを写す（以前の判定の列は写さない）。

    uv run -q --with openpyxl python -I make_calibration_guide.py --pass 1 --coder coder1 \
        --links links.json --items <核 1 の items.csv> --titles-dir ~/TRACE-screening/check34-r3/in \
        --trace ~/TRACE --out ~/Documents/TRACE/calibration/pass1
"""

import argparse
import csv
import datetime
import json
import sys
from pathlib import Path

IDS = ["AF001", "AF002", "AF004", "AF005", "AF006", "AF007", "AF008", "AF010", "AF011", "AF012", "AF019"]
SCALE_NOTE = {"AF001": "Lau et al. の AI Fatigue Scale（探索の集合の 4 尺度の 1 つ）",
              "AF005": "Zhao & Liu の AI misinformation fatigue と AI privacy fatigue（探索の集合の 4 尺度の 2 つ）"}
ZEF_COLS = ["version_id", "item_no", "項目の文", "前置き", "type", "boundary", "secondary_type", "target",
            "target_from_stem", "item_source"]


def title(d, rid):
    for ln in (Path(d).expanduser() / f"{rid}.stage1.txt").read_text(encoding="utf-8").splitlines():
        if ln.startswith("Title: "):
            return ln[len("Title: "):]
    raise SystemExit(f"{rid}: no title")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="n", type=int, choices=[1, 2], required=True)
    ap.add_argument("--coder", choices=["coder1", "coder2"], required=True)
    ap.add_argument("--links", required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--titles-dir", required=True)
    ap.add_argument("--trace", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sys.path.insert(0, str(Path(a.trace).expanduser() / "scripts"))
    from openpyxl import Workbook
    from openpyxl.worksheet.datavalidation import DataValidation
    import c_coding_book as book
    import trace_style as st

    links = json.loads(Path(a.links).read_text(encoding="utf-8"))
    if sorted(links) != sorted(IDS):
        raise SystemExit("links.json は 11 研究の ID と一致しない")
    zef = [r for r in csv.DictReader(open(Path(a.items).expanduser(), encoding="utf-8")) if r["scale_id"] == "ZEF"]
    if [int(r["item_no"]) for r in zef] != list(range(1, 16)):
        raise SystemExit("ZEF の項目が 1〜15 でない")

    wb = Workbook()
    today = datetime.date.today().isoformat()
    st.intro(wb.active, f"TRACE｜較正・{a.n} 回目の案内", f"作成 {today}・11 研究と ZEF の 15 項目", [
        ("この冊の位置づけ", [
            "較正の符号化は、登録の GSRR-44 の 2 による。探索の集合の一次研究 11 件を、1 回目は 2026 年 11 月、2 回目は 12 月に、4 週間以上空けて符号化する。2 回目は 1 回目を見ずに行う。",
            "較正の符号はデータではない。2 回の一致を登録の単位ごとに出し、比べる数が 5 以上で 80% に届かない単位は、本番の前に定義を直して改訂を登録する。改訂の根拠は 2 回の食い違いだけとし、追加候補の選別で読んだものは使わない。",
        ]),
        ("記入する冊", [
            f"記録・尺度・項目・再計算は、同じフォルダの『TRACE_較正{a.n}回目_符号化_{a.coder}.xlsx』に書く。本番の符号化の冊と同じ形で、ファイル名の頭の『較正{a.n}回目』とフォルダで本番と分ける。",
            "records の set の欄は、11 件すべて exploration とする。",
            "instruments の instrument_id は、その記録の主の尺度を main とし、ほかの尺度を I1・I2 のように書く。集計の脚本は main の行だけを主の尺度として読む（登録と列の辞書には書かれていない決まりで、本番の前の改訂の候補にする）。",
            "ZEF はどの記録にも使われていないため、符号化の冊には入れられない（書き出しの検査で止まる）。ZEF の 15 項目は、この冊の『ZEF』のシートで、C2b の型・境界・対象だけを符号化する。ZEF の項目の一部はコードブックの例と重なるので、その一致が高く出やすいことを較正の結果に注記する。",
        ]),
        ("全文", [
            "『一覧』の全文の列にリンクがある。8 件は Drive の較正のフォルダに置いた PDF、AF004・AF011・AF019 の 3 件は出版社または PMC の無料公開のページである（自動の取得が出版社の確かめで止まるため）。",
        ]),
    ])

    ws = wb.create_sheet("一覧")
    ws.append(["ID", "題名", "全文", "探索の集合の尺度"])
    for rid in IDS:
        ws.append([rid, title(a.titles_dir, rid), links[rid], SCALE_NOTE.get(rid, "")])
        c = ws.cell(row=ws.max_row, column=3)
        c.hyperlink = links[rid]
        c.style = "Hyperlink"
    for col, w in zip("ABCD", (9, 70, 45, 50)):
        ws.column_dimensions[col].width = w

    z = wb.create_sheet("ZEF")
    z.append(ZEF_COLS)
    for r in zef:
        z.append(["V-ZEF", r["item_no"], r["item_text"], r["context"], "", "", "", "", "", "printed"])
    for i, col in enumerate(ZEF_COLS, start=1):
        values = book.listed(col)
        if values is None:
            continue
        dv = DataValidation(type="list", formula1='"' + ",".join(values) + '"', allow_blank=True)
        letter = z.cell(row=1, column=i).column_letter
        dv.add(f"{letter}2:{letter}16")
        z.add_data_validation(dv)
    for col, w in zip("ABCDEFGHIJ", (9, 8, 60, 28, 10, 10, 14, 12, 16, 12)):
        z.column_dimensions[col].width = w
    z.freeze_panes = "C2"

    out = Path(a.out).expanduser()
    p = out / f"TRACE_較正{a.n}回目_案内とZEF_{a.coder}.xlsx"
    if p.exists():
        raise SystemExit(f"{p} がすでにある")
    wb.save(p)
    print(f"wrote {p}")


if __name__ == "__main__":
    main()
