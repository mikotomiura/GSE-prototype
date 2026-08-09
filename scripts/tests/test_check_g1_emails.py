#!/usr/bin/env python3
"""★ `scripts/check_g1_emails.py` が**空回りしていない**ことを実測する。

⚠️ ★ このプロジェクトで繰り返し踏んだ失敗は「検査は緑だが、実は何も見ていなかった」である
   （2026-08-08 だけで 3 件見つけた）。★ **ガードは壊して赤を見るまで信じない。**

各ケースは `.gs` の**コピー**を壊し、`G1_GAS_PATH` で検査対象を差し替えて実行し、
  (a) 赤くなること
  (b) ★ **狙った理由で**赤いこと（別の理由で落ちていれば、その検査は空回りしている）
の両方を確かめる。

    python3 -m unittest scripts.tests.test_check_g1_emails -v
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
GAS = REPO / "Form_G1" / "GSE_G1_Form_Builder.gs"
CHECKER = REPO / "scripts" / "check_g1_emails.py"

# (名前, 置換前, 置換後, 出力に必ず出る理由)
MUTATIONS = [
    (
        "受付メールから導線ブロックを外す",
        "    .concat(g1FormRoutingBlock_(pid))\n",
        "",
        "G1-M のリンクが無い",
    ),
    (
        "g1FormLink_ が空を返す",
        'function g1FormLink_(key, formId) {\n  var published = "";',
        'function g1FormLink_(key, formId) {\n  if (key) return "";\n  var published = "";',
        "G1-S のリンクが無い",
    ),
    (
        "短縮(1 段目)を見ない",
        "    if (s) return s;",
        "    if (s && false) return s;",
        "G1-M の**短縮**が本文に出ていない",
    ),
    (
        "publishedUrl(2 段目)を落とす",
        "  if (published) return published;",
        "  if (published && false) return published;",
        "publishedUrl** に落ちていない",
    ),
    (
        "G1-M と G1-S を取り違える",
        'var survey = g1FormLink_("G1_SURVEY", FORM_ID_SURVEY);',
        'var survey = g1FormLink_("G1_MCHECK", FORM_ID_MCHECK);',
        "G1-S のリンクが無い",
    ),
    (
        "「別のタブで開く」の案内を消す(protocol.md §3.1b)",
        '        ★ **ブラウザの別のタブ**で開いてください（protocol.md §3.1b）。",',
        '        ★ 開いてください。",',
        '"別のタブ" が無い',
    ),
    (
        "「計 7 回」を消す(§2.6 の回数)",
        "★ **3 回目〜9 回目の作業のあと、毎回（計 7 回）**",
        "★ **作業のあと、毎回**",
        '"計 7 回" が無い',
    ),
    (
        "★ 散文に条件名 HI を書く(URL 除去で HI/LO 検査が空回りしていないか)",
        '    "■ ご回答いただくフォームは 3 つです（★ 役割が違うので使い分けてください）",',
        '    "■ ご回答いただくフォームは 3 つです（HI のときだけ）",',
        '"HI" が受付メール',
    ),
    # --- 管理シートの列（★ ヘッダ名で引く箇所は、綴りがずれても例外が出ない）---------
    (
        "列を改名したのに WIDTHS が旧名のまま",
        '"G1モード確認": 110',
        '"GSE_DISABLE_PROBES=1": 110',
        "が RUN_HEADER に無い",
    ),
    (
        "列を足したのに幅を足し忘れる",
        '"配布URL(短縮)": 130,',
        "",
        '"配布URL(短縮)" の幅が WIDTHS に無い',
    ),
    (
        "移行の改名先を綴り間違える",
        '["課題文リンク送信日", "課題ページ送付日"]',
        '["課題文リンク送信日", "課題ページ送信日"]',
        "移行の改名先",
    ),
    (
        "削除した列を runCol_ が参照したまま",
        'var colShort = runCol_("配布URL(短縮)");',
        'var colShort = runCol_("配置(A/B)");',
        "削除した列",
    ),
    (
        "★ 紙署名の文言を書き戻す(D-1(a) の撤回)",
        '    "■ 参加は任意です",',
        '    "■ 当日は署名をお願いします",',
        "紙署名は廃止した",
    ),
]


def run_checker(gas_path: pathlib.Path) -> tuple[int, str]:
    env = dict(os.environ, G1_GAS_PATH=str(gas_path))
    r = subprocess.run(
        [sys.executable, str(CHECKER)], cwd=REPO, env=env, capture_output=True, text=True
    )
    return r.returncode, r.stdout + r.stderr


class TestCheckG1Emails(unittest.TestCase):
    def test_repo_gas_is_green(self):
        """★ まず本物が緑であること（赤いまま変異を試しても何も分からない）。"""
        rc, out = run_checker(GAS)
        self.assertEqual(rc, 0, out)

    def test_mutations_turn_it_red(self):
        src = GAS.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as td:
            copy = pathlib.Path(td) / "GSE_G1_Form_Builder.gs"
            for name, old, new, reason in MUTATIONS:
                with self.subTest(mutation=name):
                    # ⚠️ ★ 変異点が見つからない = この表が実装から取り残されている。
                    #    黙って飛ばすと「0 件試して緑」になる（silent-failure-in-guard-scripts）。
                    self.assertIn(old, src, f"変異点が .gs に無い: {name}")
                    copy.write_text(src.replace(old, new, 1), encoding="utf-8")
                    rc, out = run_checker(copy)
                    self.assertNotEqual(rc, 0, f"壊したのに緑のまま: {name}\n{out}")
                    self.assertIn(reason, out, f"赤いが理由が違う: {name}\n{out}")

    def test_repo_gas_untouched(self):
        """★ 変異はコピーにだけ当たっていること（本物を壊して終わらない）。"""
        rc, out = run_checker(GAS)
        self.assertEqual(rc, 0, out)


if __name__ == "__main__":
    unittest.main()
