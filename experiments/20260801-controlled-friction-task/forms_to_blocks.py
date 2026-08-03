#!/usr/bin/env python3
"""★ 強制比較フォーム（G1-M）の CSV を `blocks/P0xx.json` の回答欄に変換する。

なぜ要るか:
  `preregistration.md §2.6` の操作チェックは **7 回の二択**であり、これを手で
  `manipulation_check_answers` に書き写すと **1 つずれた転記**が起こりうる。
  ★ しかも操作チェックは「**どの分母でも 1 問しか外せない**」（§5.3）ので、
  **転記ミス 1 件で合否が反転しうる**。手転記を経路から外す。

  ⚠️ **これは判定に一切関与しない。** 合否を計算するのは `analyze.py` であり、
  本スクリプトは**フォームの選択肢をブロック番号に直すだけ**である。

フォーム側との契約（★ `Form_G1/GSE_G1_Form_Builder.gs` と同じ版であること）:
  列        キーワード          値
  被験者ID  "被験者"            P015 など
  ブロック  "ブロック"          3〜9
  回答      "詰まった"          「1つ前のブロックのほう」 / 「直前のブロックのほう」
                                → harder = (ブロック番号 - 1) / (ブロック番号)

  ★ 選択肢を**相対表現**にしてあるのは、被験者にブロック番号を計算させないためである
    （番号を答えさせると、そこで 1 つずれる）。

使い方:
    python3 forms_to_blocks.py --csv 回答.csv --subject P015          # 内容を確認する
    python3 forms_to_blocks.py --csv 回答.csv --subject P015 --write  # blocks/P015.json に書く
    python3 forms_to_blocks.py --selftest

⚠️ **CSV のタイムスタンプ列は読み捨てる。** 成果物に実施日時を出さない（本 repo は一時 public
   化の運用がある）。CSV そのものを repo に置かないこと。
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import pathlib
import re
import sys

# ★ フォーム側の設問タイトルに含まれる語（`GSE_G1_Form_Builder.gs` の Q_* と対応）。
HEADER_KEYS = {"subject": "被験者", "block": "ブロック", "harder": "詰まった"}
# ★ 選択肢の語（同 CHOICE_PREV / CHOICE_CURRENT）。
CHOICE_PREV = "1つ前"
CHOICE_CURRENT = "直前"

MCHECK_BLOCKS = tuple(range(3, 10))  # §2.6: G1 ブロック 3〜9 の直後・計 7 回


def find_columns(header: list[str]) -> dict[str, int]:
    idx: dict[str, int] = {}
    for name, key in HEADER_KEYS.items():
        hits = [i for i, h in enumerate(header) if key in h]
        if not hits:
            # ⚠️ ★ ヘッダ全体をダンプしない。誤って G1-C（同意）の CSV を渡すと
            #    「お名前」「メールアドレス」という列名が出力に混ざる（`/cross-review` の指摘）。
            raise SystemExit(
                f"[NG] CSV に「{key}」を含む列が無い（列数 {len(header)}）。"
                f"★ G1-M（強制比較）の CSV か確認すること。"
                f"フォームの設問文を変えたなら、本スクリプトの HEADER_KEYS も"
                f"同じ版に直すこと (decisions.md E-6 / E-7 の教訓)")
        if len(hits) > 1:
            raise SystemExit(f"[NG] 「{key}」を含む列が {len(hits)} 個ある。設問文を一意にすること")
        idx[name] = hits[0]
    return idx


def parse_rows(rows: list[list[str]], subject: str) -> list[dict]:
    """★ 曖昧な行を黙って落とさない。落とすなら理由を上げて止める。"""
    if not rows:
        raise SystemExit("[NG] CSV が空")
    idx = find_columns(rows[0])

    answers: dict[int, int] = {}
    for lineno, row in enumerate(rows[1:], start=2):
        if not any(c.strip() for c in row):
            continue
        if len(row) <= max(idx.values()):
            raise SystemExit(f"[NG] {lineno} 行目: 列が足りない")
        sid = row[idx["subject"]].strip()
        if sid != subject:
            continue  # 別の被験者の回答（同じフォームを全員で使う）
        raw_block = row[idx["block"]].strip()
        try:
            block = int(raw_block)
        except ValueError:
            raise SystemExit(f"[NG] {lineno} 行目: ブロック番号が数値でない ({raw_block!r})")
        if block not in MCHECK_BLOCKS:
            raise SystemExit(
                f"[NG] {lineno} 行目: ブロック {block} には強制比較を取らない。"
                f"§2.6 は 3〜9 の直後のみと凍結している（copy と G1 の最初には比較対象が無い）")

        choice = row[idx["harder"]].strip()
        # ★ 部分一致で判定するので、**両方に合致する値**は先勝ちで黙って通ってしまう。
        #   単一選択フォームでは起きにくいが、「二択の外は推測で埋めない」という本スクリプトの
        #   方針からすると先勝ちは推測である（`/cross-review` の指摘）。明示的に止める。
        hit_prev, hit_cur = CHOICE_PREV in choice, CHOICE_CURRENT in choice
        if hit_prev and hit_cur:
            raise SystemExit(
                f"[NG] {lineno} 行目: 回答が二択の**両方**に合致する ({choice!r})。"
                f"★ どちらを選んだのかスクリプトには決められない。実験者が確認すること")
        if hit_prev:
            harder = block - 1
        elif hit_cur:
            harder = block
        else:
            raise SystemExit(
                f"[NG] {lineno} 行目: 回答が二択のどちらでもない ({choice!r})。"
                f"★ 「どちらでもない」を選ばせてはならない（§2.6）")

        if block in answers:
            # ★ 黙って上書きしない。1 分休憩で焦って二重送信した可能性があり、
            #   どちらが本物かはスクリプトには決められない（実験者が決めること）。
            raise SystemExit(
                f"[NG] ブロック {block} の回答が 2 件ある（{lineno} 行目）。"
                f"二重送信の疑い。★ 実験者が CSV 側でどちらを残すか決めてから再実行すること")
        answers[block] = harder

    missing = [b for b in MCHECK_BLOCKS if b not in answers]
    if missing:
        raise SystemExit(
            f"[NG] {subject}: ブロック {missing} の回答が無い（{len(answers)}/7 件）。"
            f"★ 足りないぶんを紙のバックアップから補うこと（推測で埋めない）")
    return [{"block": b, "harder": answers[b]} for b in MCHECK_BLOCKS]


def write_into_spec(spec_path: pathlib.Path, answers: list[dict]) -> None:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if spec.get("manipulation_check_answers"):
        raise SystemExit(
            f"[NG] {spec_path.name} には既に manipulation_check_answers がある。"
            f"上書きしない（先に中身を確認すること）")
    spec["manipulation_check_answers"] = answers
    spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


#: ★ GAS builder の定数名 → 本スクリプト側で「その文字列に含まれていなければならない」語。
#  `Q_SUBJECT_ID = "被験者ID"` のように、`.gs` 側は本スクリプトのキーを**含む**文字列を持つ。
GS_CONTRACT = {
    "Q_SUBJECT_ID": HEADER_KEYS["subject"],
    "Q_BLOCK_NO": HEADER_KEYS["block"],
    "Q_HARDER": HEADER_KEYS["harder"],
    "CHOICE_PREV": CHOICE_PREV,
    "CHOICE_CURRENT": CHOICE_CURRENT,
}
GS_BUILDER = pathlib.Path(__file__).resolve().parents[2] / "Form_G1" / "GSE_G1_Form_Builder.gs"


def check_gs_contract() -> list[str]:
    """★ フォーム側（GAS）と本スクリプトの契約が同じ版かを機械的に突き合わせる。

    ⚠️ **これが無いと、`.gs` の設問文だけ変えても `--selftest` は緑のまま残る。**
    このプロジェクトでは「文書だけ改訂して実装が追随しない」事故が 3 回起きており
    （E-6 / E-7 / B-1）、その教訓が GAS↔Python の境界に及んでいなかった
    （`/cross-review` 2026-08-03 の指摘）。

    ★ **`.gs` が見つからない場合は FAIL にする。** 「見つからないので飛ばす」は
    `silent-failure-in-guard-scripts` そのものであり、ゲートを素通りさせる。
    """
    if not GS_BUILDER.is_file():
        return [f"GAS builder が見つからない: {GS_BUILDER}（契約を検証できない）"]
    src = GS_BUILDER.read_text(encoding="utf-8")
    out: list[str] = []
    for var, needle in GS_CONTRACT.items():
        m = re.search(rf'^var\s+{re.escape(var)}\s*=\s*"([^"]*)"\s*;', src, re.MULTILINE)
        if m is None:
            out.append(f"{GS_BUILDER.name} に `var {var} = \"...\";` が無い")
        elif needle not in m.group(1):
            out.append(
                f"★ 契約が食い違っている: {GS_BUILDER.name} の {var}={m.group(1)!r} が "
                f"本スクリプトの {needle!r} を含まない。"
                f"どちらかを直して**同じ版**にすること")
    return out


def selftest() -> int:
    fails: list[str] = []

    # 0) ★ GAS 側との契約（設問文・選択肢）
    fails += check_gs_contract()

    header = ["タイムスタンプ", "被験者ID", "ブロック番号", "より詰まったのはどちらですか"]

    def rows_for(pairs, subject="P015"):
        out = [header]
        for b, c in pairs:
            out.append(["2026-01-01 00:00:00", subject, str(b), c])
        return out

    full = [(b, "直前のブロックのほう" if b % 2 else "1つ前のブロックのほう") for b in MCHECK_BLOCKS]
    got = parse_rows(rows_for(full), "P015")
    want = [{"block": b, "harder": b if b % 2 else b - 1} for b in MCHECK_BLOCKS]
    if got != want:
        fails.append(f"正常系の変換が違う: {got}")

    def expect_exit(name, rows, subject="P015"):
        try:
            parse_rows(rows, subject)
        except SystemExit:
            return
        fails.append(f"{name}: SystemExit を期待したが通った")

    expect_exit("回答が 6 件", rows_for(full[:-1]))
    expect_exit("ブロック 2 の回答", rows_for([(2, "直前のブロックのほう")] + full))
    expect_exit("二重送信", rows_for(full + [(3, "直前のブロックのほう")]))
    expect_exit("二択の外", rows_for(full[:-1] + [(9, "どちらでもない")]))
    # ★ 両方に合致する値を先勝ちで通さない（`/cross-review` の指摘）
    expect_exit("二択の両方に合致",
                rows_for(full[:-1] + [(9, "1つ前のブロックのほう / 直前のブロックのほう")]))
    expect_exit("列が無い", [["タイムスタンプ", "氏名"], ["x", "y"]])
    # ★ 他被験者の行は無視され、当該被験者の 7 件が揃っていれば通る
    mixed = rows_for(full) + [["t", "P016", "3", "直前のブロックのほう"]]
    if parse_rows(mixed, "P015") != want:
        fails.append("他被験者の行を混ぜると結果が変わる")

    if fails:
        print("[NG] forms_to_blocks.py --selftest 失敗:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("[OK] forms_to_blocks.py --selftest 緑")
    return 0


def main() -> int:
    here = pathlib.Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="G1-M フォームの回答 CSV")
    ap.add_argument("--subject", help="被験者 ID (例: P015)")
    ap.add_argument("--blocks-dir", default=str(here / "blocks"))
    ap.add_argument("--write", action="store_true",
                    help="blocks/<subject>.json の manipulation_check_answers に書き込む")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if not a.csv or not a.subject:
        ap.error("--csv と --subject が要る（または --selftest）")

    raw = pathlib.Path(a.csv).read_text(encoding="utf-8-sig", errors="replace")
    rows = list(csv.reader(io.StringIO(raw)))
    answers = parse_rows(rows, a.subject)

    print(f"[forms] {a.subject}: 強制比較 {len(answers)} 件")
    for x in answers:
        # ★ 条件（HI/LO）は出さない。フォームも本スクリプトも条件を知らない。
        print(f"  ブロック {x['block']}: より詰まった = ブロック {x['harder']}")

    if not a.write:
        print("\n  （--write を付けると blocks/ に書き込む）")
        print(json.dumps({"manipulation_check_answers": answers}, ensure_ascii=False, indent=2))
        return 0

    spec_path = pathlib.Path(a.blocks_dir) / f"{a.subject}.json"
    if not spec_path.is_file():
        raise SystemExit(f"[NG] {spec_path} が無い。先に `python3 assign.py --subject {a.subject} "
                         f"--json > {spec_path}` を実行すること")
    write_into_spec(spec_path, answers)
    print(f"\n[OK] {spec_path.name} に書き込んだ。"
          f"★ 続けて `python3 validate_blocks.py` で整合を確かめること。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
