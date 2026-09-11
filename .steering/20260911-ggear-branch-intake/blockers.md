# 詰まりと解決 — G-GEAR ブランチ取り込み

## B-1: `md2pptx.py --selftest` が macOS で必ず落ちる (branch 側の実バグ・修正済み)

- **症状**: `[NG] repo 外の画像は埋め込まない: /private/var/folders/.../fig.png`
  と出て `--selftest` が exit 1。⚠️ ★ **repo 内 (tempdir 内) の画像なのに repo 外と言われる。**
- **真因**: `resolve_image()` が **画像側だけ `.resolve()`** してから、未解決の `root` に
  対して `relative_to()` していた。★ macOS の `tempfile` は `/var/folders/...`
  (= `/private/var/...` への symlink) を返すので、**片側だけ正規化された比較**になる。
  ★ 実測: `Path(d).resolve() != d` が macOS では True。
- **回り道**: ⚠️ 最初 `build()` 側で `root` を resolve したが**直らなかった**。
  ★ traceback を取って初めて、落ちているのが `render_slide()` の直接呼び出し
  (`build()` を経由しない経路) だと判った。→ ★ **正規化は呼び出し側ではなく
  関門 (`resolve_image`) に置く**のが正しい。
- **解決**: `resolve_image()` の冒頭で `root = pathlib.Path(root).resolve()`。
- **陽性対照 3 本** (★ 修正がガードを殺していないことの確認):
  1. repo 外の実在 PNG → ✅ 拒む
  2. repo 内の実在 PNG (`docs/mitou_submission/figures/gse-layer-map.png`) → ✅ 通す
  3. symlink な root 配下の PNG → ✅ 通す (★ これが今回の修正点)
- **影響** (⚠️★★★ **2026-09-11 に自分の主張を訂正した**):
  ★ 当初「CI の `check` job が macOS レッグを持つので確実に赤になる」と書いたが、
  ⚠️ **誤りだった。** ★ 実測: md2pptx の step が属するのは `check` ではなく
  **`frontend-check` (`runs-on: ubuntu-latest`)** であり、`check` job の step に
  `md2pptx` は **0 件**。★ Linux の `/tmp` は symlink ではないので、
  **この欠陥は CI を赤にしない**。
- **★ では何が壊れていたか**: ⚠️ **開発機 (macOS) では `--selftest` が必ず落ちる**。
  ★ つまり「手元で確かめてから CI に出す」という順序が**この検査だけ踏めない**状態で、
  ⚠️ 実際に**手元で落ちたからこそ気づいた**。→ ★ 修正の価値は変わらないが、
  **深刻度は「CI が赤」ではなく「手元で検査が使えない」**である。
- ⚠️★★★ **教訓**: ★ 「CI が緑」と「何を検証したか」は別
  (memory: `github-pr-ci-mechanics`)。⚠️ **どの job が走らせるかを確かめずに
  影響範囲を書いた**。★ job の step 一覧を API で引けば 1 コマンドで判る。

## B-2: `check-o1-release-readiness.sh` が 20/0 → 19/1 に転じた (branch 側の実バグ・修正済み)

- **症状**: main では 20 件 / 0 件だったのに、PR-B を展開すると
  `❌ ★ bash 3.2 で壊れる書き方が残っている` で 19 件 / 1 件。
- **真因**: `experiments/20260906-interruption-resumption-arm1/run.sh:129` に
  `$HMM_V。` があった。★ bash 3.2 は `$VAR` の直後の多バイト文字を**変数名に食う**
  (memory: `macos-default-tools-break-gates`)。⚠️ 引き継ぎメモ §5 が**事前に警告していた**罠。
- **解決**: `${HMM_V}。` と括る。→ 20 件 / 0 件へ復帰。
- **★ 学び**: ゲートが**branch を展開した瞬間に赤へ転じた**ので捕まった。
  ⚠️ 逆に言えば、**取り込み前に main でゲートを 1 回走らせておかないと、
  赤が「元からか / 自分が持ち込んだか」を切り分けられない**。★ 今回は §0 で走らせてあった。

## B-3: `test_build_analysis_db` が duckdb 無しだと 18/19 skip する (既知・回避)

- ⚠️ 素の `python3` では `ModuleNotFoundError: duckdb` で **18/19 が skip され、
  それでも `OK` と出る**。★ 「ほぼ何も検査しない緑」。
- ★ macOS の Homebrew python は PEP 668 で `pip install` を拒む
  (`externally-managed-environment`)。→ ★ venv (`/tmp/gsevenv`) を作って導入し、
  **skip=0 で 19/19** を確認した。
- ⚠️ CI 側は main の ci.yml が `pip install duckdb` を明示済みなので問題ない。

## B-4: `scripts/svg2png.py` の `--selftest` は実装されていない (未対処・情報)

- ★ ファイル内に `--selftest` の文字列はあるが、実行すると `[NG] 未知のオプション`。
- ⚠️ ただし **CI にも `check-tests-are-wired.sh` の対象にも入っていない**ので、
  「あるはずの検査が空振りしている」状態ではない。★ 本 PR のスコープ外として残す。
