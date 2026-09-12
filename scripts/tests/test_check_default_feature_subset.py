"""Regression tests for scripts/check_default_feature_subset.py (F-4 の代替ゲート).

⚠️★★★ **本体より対照のほうが重要である。**
★ この種のゲートは「**違反を見逃す**」「**そもそも 1 行も読んでいない**」という形で壊れ、
⚠️ どちらも**実在の欠陥と見分けがつかない緑**を出す (本 repo は同型を複数回踏んでいる)。

→ ★ 検査するのは 4 つ:
  1. **陽性対照**: 違反を仕込んだら **赤くなる** (⚠️ 空白の揺れ・入れ子も含めて)
  2. **陰性対照**: 違反でないものを **赤にしない** (⚠️ 何にでも赤くなる検査器は使えない)
  3. ⚠️★★★ **空振り対照**: 対象が 1 つも無いときは **緑にしない** (★ exit 2)
  4. **実 repo**: 現状の不変条件が実際に保たれている

⚠️ 本 module は Rust も cargo も呼ばない (★ どの環境でも走る)。

実行方法:
    cd GSE-prototype
    PYTHONUTF8=1 python -m unittest scripts.tests.test_check_default_feature_subset -v
"""

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "check_default_feature_subset.py"
REPO_ROOT = SCRIPT.parent.parent

# ⚠️ 対照に使う違反文字列も**実行時に連結する** —— ★ このテストファイル自体が
#   将来 grep 対象に入っても自己参照で誤爆しないようにするため
#   (`gate-green-but-artifact-broken` ④ の型)。
_P = 'pack' + 'age'
_N = 'not('
VIOLATIONS = [
    ('標準形', '#[cfg(' + _N + 'feature = "' + _P + '"))]'),
    ('空白なし', '#[cfg(' + _N + 'feature="' + _P + '"))]'),
    ('空白過多', '#[cfg( ' + 'not ( ' + 'feature  =  "' + _P + '" ))]'),
    ('all の入れ子', '#[cfg(all(unix, ' + _N + 'feature = "' + _P + '")))]'),
    ('any の入れ子', '#[cfg(any(test, ' + _N + 'feature = "' + _P + '")))]'),
    ('not(all(..)) 形', '#[cfg(' + _N + 'all(feature = "' + _P + '", unix)))]'),
]
CLEAN = [
    '#[cfg(feature = "' + _P + '")]',      # ★ 肯定形は違反ではない
    '#[cfg(' + _N + 'feature = "other"))]',  # ★ 別 feature は対象外
    '#[cfg(target_os = "macos")]',
    '// ' + _N + 'feature は doc では触れてよい',
]


def _run(root):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(root)],
        capture_output=True,
        text=True,
    )


def _make_repo(tmp, lines):
    src = Path(tmp) / "src-tauri" / "src"
    src.mkdir(parents=True)
    (src / "x.rs").write_text("\n".join(["// control fixture", *lines, "fn f() {}"]), encoding="utf-8")
    return Path(tmp)


class PositiveControl(unittest.TestCase):
    """★ 違反を仕込んだら赤くなること (⚠️ 見逃す検査器は無いのと同じ)。"""

    def test_each_violation_form_is_detected(self):
        for label, line in VIOLATIONS:
            with self.subTest(form=label):
                with tempfile.TemporaryDirectory() as d:
                    r = _run(_make_repo(d, [line]))
                    self.assertEqual(
                        r.returncode, 1,
                        f"⚠️ 違反を検出できていない ({label}): {line!r}\n"
                        f"  stdout={r.stdout.strip()!r}",
                    )
                    self.assertIn(
                        "x.rs", r.stderr,
                        f"⚠️ 赤くはなったが該当箇所を報告していない ({label})",
                    )


class NegativeControl(unittest.TestCase):
    """⚠️ 何にでも赤くなる検査器は運用で無効化される。"""

    def test_clean_sources_stay_green(self):
        with tempfile.TemporaryDirectory() as d:
            r = _run(_make_repo(d, CLEAN))
            self.assertEqual(
                r.returncode, 0,
                f"⚠️ 違反でないのに赤: {r.stderr.strip()[:400]!r}",
            )


class EmptyScanControl(unittest.TestCase):
    """⚠️★★★ **最も危険な壊れ方**: 1 行も読まずに「違反 0 件」で緑になること。

    ★ `silent-failure-in-guard-scripts` の `find <無いdir> | wc -l` 型。
    """

    def test_missing_targets_do_not_pass(self):
        with tempfile.TemporaryDirectory() as d:
            r = _run(Path(d))  # ★ src-tauri が存在しない
            self.assertNotEqual(
                r.returncode, 0,
                "⚠️ 対象が 1 つも無いのに緑になった (★ 検査が動いていないのと同じ)",
            )
            self.assertEqual(r.returncode, 2, f"exit 2 を期待: stderr={r.stderr.strip()[:200]!r}")


class RealRepo(unittest.TestCase):
    """★ 現状の不変条件 (default ⊂ package) が実際に保たれていること。"""

    def test_repo_is_green_and_actually_scanned_files(self):
        r = _run(REPO_ROOT)
        self.assertEqual(r.returncode, 0, f"⚠️ 実 repo が赤: {r.stderr.strip()[:600]!r}")
        # ⚠️ 「0 ファイル走査で緑」を実 repo でも弾く (★ 出力に走査数が出る)。
        #   ⚠️ `split("(")` のような雑な取り出しはしない —— ★ 出力には
        #   「既知の限界 (★ ...)」の括弧もあり、**別の括弧を拾って落ちた**実績がある。
        m = re.search(r"\((\d+) ファイルを走査\)", r.stdout)
        self.assertIsNotNone(m, f"⚠️ 走査ファイル数が報告されていない: {r.stdout!r}")
        scanned = int(m.group(1))
        self.assertGreater(scanned, 10, f"⚠️ 走査ファイル数が少なすぎる ({scanned}) = 対象の取り違え")


if __name__ == "__main__":
    unittest.main()
