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
# 偽シートを使う検査で追加で切り出すもの（Spreadsheet API を呼ぶが、偽物で受けられる）
SHEET_FUNCS = ["unmergeAll_", "styleSubmissionTab_"]
CONSTS = ["G1_BLOCK_COUNT", "G1_MCHECK_BLOCKS", "G1_SUBMIT_FOLDER_PROP"]


def extract(src: str, extra: list[str] | None = None) -> str:
    """`.gs` から定数と純関数だけを切り出す。★ 見つからなければ例外で止める（黙って空にしない）。"""
    out = []
    for name in CONSTS:
        m = re.search(rf"^var {re.escape(name)} = .*?;$", src, re.M)
        if not m:
            raise AssertionError(f"★ 定数 {name} が .gs に無い（切り出しが空回りする）")
        out.append(m.group(0))
    for name in FUNCS + (extra or []):
        m = re.search(rf"^function {re.escape(name)}\(.*?^\}}", src, re.M | re.S)
        if not m:
            raise AssertionError(f"★ 関数 {name} が .gs に無い（切り出しが空回りする）")
        out.append(m.group(0))
    return "\n".join(out)


def run_js(src: str, script: str, extra: list[str] | None = None) -> object:
    """切り出したコード + 検査スクリプトを node で走らせ、JSON を返す。"""
    prog = extract(src, extra) + "\n" + script
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

    def test_folder_unset_is_not_shown_as_not_started(self):
        """⚠️★ 「見ていない」を「未提出」に見せない。

        2026-08-08 の cross-review で Codex が指摘した誤読。凡例では
        「見ていません」と言いながら、表では全員が「未着手」に見えていた。
        """
        rows = run_js(
            self.src,
            'console.log(JSON.stringify(submissionRows_(["P001"], null, {})));',
        )
        row = rows[3]
        self.assertEqual(row[1:11], ["?"] * 10, "★ 未設定なのに空欄（= 未着）に見えている")
        self.assertIn("未設定", row[15])
        self.assertNotIn("未着手", row[15])

    def test_out_of_range_blocks_do_not_inflate_the_count(self):
        """⚠️ `block099` のような壊れた名前で「提出(/10)」が 10 を超えないこと。"""
        rows = run_js(
            self.src,
            'console.log(JSON.stringify(submissionRows_(["P001"],'
            ' {P001:{blocks:[1,2,3,99],firstYmd:"20260810"}}, {})));',
        )
        row = rows[3]
        self.assertEqual(row[11], 3, "★ 範囲外のブロックが件数に混ざっている")
        self.assertIn("範囲外", row[15])

    # --- ★ 実物の制約を入れた偽シート -----------------------------------------

    def test_redraw_breaks_merges_before_writing_values(self):
        """⚠️★★ 2 回目の再描画で落ちないこと（`clear()` は結合を解かない）。

        ★ 前回の教訓（`.steering/_handoff` §6-1）を実行する:
          **実物で落ちたら、まず偽物に制約を足してから直す。**
        ここでの偽シートは「結合が残っている範囲へ `setValues` したら落ちる」という
        Apps Script 側の制約を持っている。★ 制約の無い偽物は緑になってしまう。
        """
        harness = """
        var log = [];
        function FakeSheet() { this.merges = []; }
        FakeSheet.prototype.getMaxRows = function () { return 100; };
        FakeSheet.prototype.getMaxColumns = function () { return 26; };
        FakeSheet.prototype.setRowHeight = function () { return this; };
        FakeSheet.prototype.setColumnWidth = function () { return this; };
        FakeSheet.prototype.setFrozenRows = function () { return this; };
        FakeSheet.prototype.setFrozenColumns = function (n) {
          // ★ 実物の制約: 結合の一部だけを含む列は固定できない
          for (var i = 0; i < this.merges.length; i++) {
            var m = this.merges[i];
            if (m.c <= n && m.c + m.w - 1 > n) {
              throw new Error("結合されたセルの一部だけを含む列を固定することはできません");
            }
          }
          return this;
        };
        FakeSheet.prototype.clear = function () { log.push("clear"); return this; };
        var sheet = new FakeSheet();
        function FakeRange(r, c, h, w) { this.r=r; this.c=c; this.h=h; this.w=w; }
        FakeRange.prototype.merge = function () {
          sheet.merges.push({ r:this.r, c:this.c, h:this.h, w:this.w });
          log.push("merge");
          return this;
        };
        FakeRange.prototype.breakApart = function () {
          sheet.merges = [];
          log.push("breakApart");
          return this;
        };
        FakeRange.prototype.setValues = function () {
          // ★ 実物の制約: 結合が残っている範囲へは書けない
          if (sheet.merges.length) throw new Error("結合セルへ setValues した");
          log.push("setValues");
          return this;
        };
        ["setFontWeight","setFontColor","setBackground","setWrap","setVerticalAlignment",
         "setHorizontalAlignment","setFontSize","setValue"].forEach(function (m) {
          FakeRange.prototype[m] = function () { return this; };
        });
        FakeSheet.prototype.getRange = function (r, c, h, w) { return new FakeRange(r, c, h, w); };
        var Logger = { log: function () {} };

        // 1 回目と 2 回目を、同じシートに対して回す
        function redraw() {
          var rows = submissionRows_(["P001"], {P001:{blocks:[1],firstYmd:"20260810"}}, {});
          var width = rows[0].length;
          unmergeAll_(sheet);
          sheet.clear();
          sheet.getRange(1, 1, rows.length, width).setValues(rows);
          styleSubmissionTab_(sheet, rows.length, width);
        }
        redraw();
        redraw();
        console.log(JSON.stringify(log));
        """
        log = run_js(self.src, harness, extra=SHEET_FUNCS)
        self.assertEqual(log.count("setValues"), 2, "★ 2 回目の setValues に到達していない")
        # ★ setValues の直前に必ず breakApart が来ていること
        for i, ev in enumerate(log):
            if ev == "setValues":
                self.assertIn(
                    "breakApart",
                    log[:i],
                    "★ setValues より前に breakApart が無い",
                )

    def test_real_code_unmerges_before_clear(self):
        """★ 実コードの順序を静的に固定する: `unmergeAll_` → `clear` → `setValues`。

        ⚠️ `clear()` は結合を解かないので、この順序が崩れると 2 回目の再描画で落ちる。
        """
        body = re.search(
            r"^function refreshSubmissionTab_\(.*?^\}", self.src, re.M | re.S
        )
        self.assertIsNotNone(body, "★ refreshSubmissionTab_ が .gs に無い")
        text = body.group(0)
        i_unmerge = text.index("unmergeAll_(sh)")
        i_clear = text.index("sh.clear()")
        i_set = text.index(".setValues(rows)")
        self.assertLess(i_unmerge, i_clear, "★ unmergeAll_ が clear より後にある")
        self.assertLess(i_clear, i_set, "★ clear が setValues より後にある")

    def test_fake_sheet_constraint_is_not_vacuous(self):
        """⚠️ ★ 上の偽シートが**本当に制約を効かせている**こと。

        ★ 制約の無い偽物は何でも緑にする（`.steering/_handoff` §6-1 の教訓）。
        ここでは **わざと `unmergeAll_` を抜いた手順**を偽シートに流し、
        2 回目で落ちることを確かめる。落ちなければ、上の検査は空回りしている。
        ⚠️ `.gs` は変異させない（この harness は実コードの順序を使っていないため、
        変異させても意味が無い。★ 効いているように見せない）。
        """
        harness_no_unmerge = """
        var log = [];
        function FakeSheet() { this.merges = []; }
        FakeSheet.prototype.getMaxRows = function () { return 100; };
        FakeSheet.prototype.getMaxColumns = function () { return 26; };
        ["setRowHeight","setColumnWidth","setFrozenRows","setFrozenColumns"].forEach(function (m) {
          FakeSheet.prototype[m] = function () { return this; };
        });
        FakeSheet.prototype.clear = function () { return this; };
        var sheet = new FakeSheet();
        function FakeRange(r, c, h, w) { this.r=r; this.c=c; this.h=h; this.w=w; }
        FakeRange.prototype.merge = function () {
          sheet.merges.push({ r:this.r, c:this.c, h:this.h, w:this.w }); return this;
        };
        FakeRange.prototype.breakApart = function () { sheet.merges = []; return this; };
        FakeRange.prototype.setValues = function () {
          if (sheet.merges.length) throw new Error("結合セルへ setValues した");
          return this;
        };
        ["setFontWeight","setFontColor","setBackground","setWrap","setVerticalAlignment",
         "setHorizontalAlignment","setFontSize","setValue"].forEach(function (m) {
          FakeRange.prototype[m] = function () { return this; };
        });
        FakeSheet.prototype.getRange = function (r, c, h, w) { return new FakeRange(r, c, h, w); };
        var Logger = { log: function () {} };
        function redraw() {
          var rows = submissionRows_(["P001"], {P001:{blocks:[1],firstYmd:"20260810"}}, {});
          var width = rows[0].length;
          sheet.clear();                                   // ★ unmergeAll_ を呼ばない
          sheet.getRange(1, 1, rows.length, width).setValues(rows);
          styleSubmissionTab_(sheet, rows.length, width);
        }
        var err = "";
        try { redraw(); redraw(); } catch (e) { err = String(e.message); }
        console.log(JSON.stringify({ err: err }));
        """
        out = run_js(self.src, harness_no_unmerge, extra=["styleSubmissionTab_"])
        self.assertIn(
            "結合セルへ setValues した",
            out["err"],
            "★ 偽シートが制約を効かせていない（この検査は空回りしている）",
        )

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
