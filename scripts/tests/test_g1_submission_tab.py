#!/usr/bin/env python3
"""★ セッション提出トラッキングの組み立てを **node で実際に動かして** 検算する。

⚠️ ★ grep で「関数がある」ことを確かめても、**中身が正しいことにはならない**。
   `submissionRows_` / `submissionRowFor_` / `submissionStatus_` / `submissionOrphans_` は
   Spreadsheet を触らない純関数なので、`.gs` から切り出して node で走らせられる。

⚠️ ★ 各ケースは「緑になること」だけでなく、**壊すと赤になること**まで見る
   （このプロジェクトで繰り返し踏んだのは「検査は緑だが何も見ていなかった」である）。

    python3 -m unittest scripts.tests.test_g1_submission_tab -v
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
GAS = REPO / "Form_G1" / "GSE_G1_Form_Builder.gs"

# `.gs` から取り出す純関数（★ ここに無いものは参照できない = 依存が漏れたら node が落ちる）
FUNCS = [
    "submissionRows_",
    "submissionRowFor_",
    "submissionYmdLabel_",
    "submissionStatus_",
    "submissionOrphans_",
]
CONSTS = ["G1_BLOCK_COUNT", "G1_MCHECK_BLOCKS", "G1_SUBMIT_FOLDER_PROP"]


def extract(src: str) -> str:
    """`.gs` から定数と純関数だけを切り出す。★ 見つからなければ例外で止める（黙って空にしない）。"""
    out = []
    for name in CONSTS:
        m = re.search(rf"^var {re.escape(name)} = .*?;$", src, re.M)
        if not m:
            raise AssertionError(f"★ 定数 {name} が .gs に無い（切り出しが空回りする）")
        out.append(m.group(0))
    for name in FUNCS:
        m = re.search(rf"^function {re.escape(name)}\(.*?^\}}", src, re.M | re.S)
        if not m:
            raise AssertionError(f"★ 関数 {name} が .gs に無い（切り出しが空回りする）")
        out.append(m.group(0))
    return "\n".join(out)


def run_js(src: str, script: str) -> object:
    """切り出したコード + 検査スクリプトを node で走らせ、JSON を返す。"""
    prog = extract(src) + "\n" + script
    p = subprocess.run(
        ["node", "-e", prog], capture_output=True, text=True, timeout=60
    )
    if p.returncode != 0:
        raise AssertionError(f"node が落ちた:\n{p.stderr}")
    return json.loads(p.stdout)


# 3 人ぶんの筋書き:
#   P001 … 10 本そろい、G1-M も 3〜9 全部 → 完了
#   P002 … 7 本 (4 と 8 と 10 が欠け)、G1-M は 5 だけ → 実施中 + G1-M 不足
#   P003 … 1 本も無い → 未着手
#   P999 … シートに居ないのに .age がある → 打ち間違いとして別枠に出る
SCENARIO = """
var pids = ["P001", "P002", "P003"];
var submitted = {
  P001: { blocks: [1,2,3,4,5,6,7,8,9,10], firstYmd: "20260810" },
  P002: { blocks: [1,2,3,5,6,7,9], firstYmd: "20260811" },
  P999: { blocks: [1,2], firstYmd: "20260812" }
};
var mcheck = {
  P001: ["3","4","5","6","7","8","9"],
  P002: ["5"]
};
var rows = submissionRows_(pids, submitted, mcheck);
console.log(JSON.stringify(rows));
"""


class TestSubmissionTab(unittest.TestCase):
    def setUp(self):
        self.src = GAS.read_text(encoding="utf-8")
        self.rows = run_js(self.src, SCENARIO)
        # 行 1 = バナー / 行 2 = 凡例 / 行 3 = ヘッダ / 行 4 以降 = データ
        self.header = self.rows[2]
        self.by_pid = {r[0]: r for r in self.rows[3:] if r and r[0]}

    def test_header_has_all_ten_blocks(self):
        self.assertEqual(self.header[0], "P-ID")
        self.assertEqual(self.header[1:11], [f"{n:02d}" for n in range(1, 11)])
        self.assertIn("欠けているブロック", self.header)
        self.assertIn("G1-M 未(3〜9)", self.header)

    def test_complete_participant(self):
        row = self.by_pid["P001"]
        self.assertEqual(row[1:11], ["✅"] * 10, "10 本そろっているのに ✅ でない")
        self.assertEqual(row[11], 10)
        self.assertEqual(row[12], "", "欠けが無いのに欠け一覧が空でない")
        self.assertEqual(row[13], "", "G1-M 全部あるのに未回答が出ている")
        self.assertEqual(row[14], "2026-08-10")
        self.assertEqual(row[15], "完了")

    def test_partial_participant_shows_which_blocks_are_missing(self):
        """★ ここがこのタブの存在理由: 「7/10」の**どの 3 つ**かを出す。"""
        row = self.by_pid["P002"]
        self.assertEqual(row[12], "4,8,10")
        # 3,6,7,9 は .age は来たが G1-M 未回答 → ▲。5 は回答済 → ✅
        self.assertEqual(row[3], "▲", "block03 は G1-M 未なので ▲ のはず")
        self.assertEqual(row[5], "✅", "block05 は G1-M 済なので ✅ のはず")
        self.assertEqual(row[13], "3,6,7,9")
        # 1・2 は G1-M の対象外なので、届いていれば ✅（▲ にしない）
        self.assertEqual(row[1], "✅", "block01 は G1-M 対象外なので ✅ のはず")
        self.assertEqual(row[2], "✅", "block02 は G1-M 対象外なので ✅ のはず")
        self.assertEqual(row[15], "実施中 (7/10)")

    def test_participant_with_nothing(self):
        row = self.by_pid["P003"]
        self.assertEqual(row[11], 0)
        self.assertEqual(row[12], "1,2,3,4,5,6,7,8,9,10")
        self.assertEqual(row[15], "未着手")

    def test_orphan_age_is_surfaced(self):
        """⚠️ ★ シートに居ない P-ID の .age を黙って捨てない（打ち間違いの検出）。"""
        flat = "\n".join(str(r) for r in self.rows)
        self.assertIn("P999", flat, "★ シートに無い P-ID の提出が消えている")
        self.assertIn("シートに無い P-ID", flat)

    def test_folder_unset_says_so(self):
        """フォルダ未設定なら、空表ではなく**理由**を出す。"""
        rows = run_js(
            self.src,
            'console.log(JSON.stringify(submissionRows_(["P001"], null, {})));',
        )
        self.assertIn("未設定", rows[1][1])

    def test_banner_text_is_in_column_b(self):
        """⚠️★ バナー本文は **B1**（A1 ではない）。

        A1 に置くと (a) 幅 80px の P-ID 列の中で折り返されて読めなくなり、
        (b) A1 から結合すると `setFrozenColumns(1)` が
        「結合されたセルの一部だけを含む列を固定することはできません」で落ちる
        （2026-08-08 に実施トラッキングで実測した罠）。
        """
        self.assertEqual(self.rows[0][0], "⚠", "★ A1 は目印 1 文字だけにする")
        self.assertIn("手動編集禁止", self.rows[0][1])
        self.assertEqual(self.rows[1][0], "", "★ A2 も空にする（結合の境界を跨がせない）")

    # --- ★ ここから「壊すと赤になるか」 -------------------------------------

    def test_mutation_missing_blocks_not_reported(self):
        """欠けたブロックを出さないように壊すと、赤になること。"""
        broken = self.src.replace(
            'row.push(missing.length ? missing.join(",") : "");',
            'row.push("");',
        )
        self.assertNotEqual(broken, self.src, "★ 変異点が .gs に無い")
        rows = run_js(broken, SCENARIO)
        row = next(r for r in rows[3:] if r and r[0] == "P002")
        self.assertEqual(row[12], "", "変異が効いていない（前提が崩れた）")
        self.assertNotEqual(row[12], "4,8,10")

    def test_mutation_mcheck_ignored(self):
        """G1-M の未回答を見ないように壊すと、▲ が消えて赤になること。"""
        broken = self.src.replace(
            "if (needsM && answered.indexOf(b) < 0) {",
            "if (false) {",
        )
        self.assertNotEqual(broken, self.src, "★ 変異点が .gs に無い")
        rows = run_js(broken, SCENARIO)
        row = next(r for r in rows[3:] if r and r[0] == "P002")
        self.assertEqual(row[3], "✅", "変異が効いていない（前提が崩れた）")
        self.assertNotEqual(row[3], "▲")

    def test_mutation_orphans_dropped(self):
        """シート外の .age を捨てるように壊すと、P999 が消えて赤になること。"""
        broken = self.src.replace(
            "    if (pids.indexOf(pid) >= 0) continue;",
            "    if (pid) continue;",
        )
        self.assertNotEqual(broken, self.src, "★ 変異点が .gs に無い")
        rows = run_js(broken, SCENARIO)
        self.assertNotIn("P999", "\n".join(str(r) for r in rows))


if __name__ == "__main__":
    unittest.main()
