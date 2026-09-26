# 実測記録（Mac・arm64・2026-09-26）

> 一次資料。引き継ぎメモ §1 の値（Windows 機・同日）との差を取る。測り方は各行に書く。

## 0. 全ゲートの実測（§3-0）

| 検査 | Windows（メモ §1） | Mac 初回 | Mac 修正後 | 備考 |
|---|---|---|---|---|
| `check-g1-collection-readiness.sh` | 通過 14 / 未達 6 | **13 / 7** | **14 / 6** | 差 1 件 = 下記 D-1（環境） |
| 〃 `--selftest` | 33 件（メモ） | **32 / 失敗 1** | **33 / 失敗 0** | 差 1 件 = 下記 D-2（Mac 固有の欠陥） |
| `check-o1-release-readiness.sh` | 通過 21 / 未達 2 | 21 / 2 | — | 一致。未達は ①同意文書の状態表に「⚠️ 未了」 ②リリースタグ v0.1.35 が古い（71 コミット） |
| 〃 `--selftest` | — | 59 / 失敗 0 | — | |
| `check-shell-portability.sh` | — | 12 / 未達 0 | — | |
| `make-common-app-zip.sh --selftest` | — | 19 / 失敗 0 | — | ⚠️ dmg / 署名 / zip は 1 つも実行していない（スクリプト自身の警告） |

## 差の原因

### D-1. gse-dataset の schema parity ❌（環境・コードの欠陥ではない）
- 原因: `~/gse-dataset` のローカル clone が origin/main より **2 コミット遅れ**（`576b873` → `32f3e86`）。`activity_label`（ADR-031）を含む schema が未反映で、`check_schema_parity.py` が rc=1（食い違い）を返した。
- 対処: `git fetch` → `git merge --ff-only origin/main`（ローカル clone のみ・リモートへの書き込みなし）。再測で parity rc=0、G1 ゲートは 14 / 6。
- 教訓: ゲートの [4] は `GSE_DATASET`（既定 `$HOME/gse-dataset`）の**鮮度に依存する**。ゲートを回す前に clone を fetch すること。⚠️ 「食い違っている」の文言だけでは「repo 側が古い」のか「clone が古い」のか区別できない。

### D-2. G1 selftest の変異が BSD sed で空振り（macOS 固有の欠陥）
- 症状: `❌ 壊しても緑のまま: ★ 表から消して散文だけ残す (検査 6)`。
- 原因: `scripts/check-g1-collection-readiness.sh:801` の変異 `sed_i '/^ *#\? *|/ s/文字数/字数欄なし/g'`。BSD sed の BRE は `\?` を解釈せず、**何にもマッチしないため変異が無音で no-op になる**（GNU sed では動く）。
- 実測（対照）: 3 行の試験ファイルに対し、`\?` 版は 3 行とも不変、`sed -E '/^ *#? *\|/ …'` 版は表の行 2 本だけが変わり散文の行は不変。
- 対処: `sed_i -E '/^ *#? *\|/ s/文字数/字数欄なし/g'` に変更（`sed_i` は引数を素通しする）。再測で 33 / 0。
- 影響: 本番ゲート（[6]）の判定ロジックは無傷。壊れていたのは「検査 6 が壊れたら赤になること」を確かめる selftest 側のみ。
- 範囲確認: `scripts/` と `experiments/20260801-controlled-friction-task/` の `*.sh` で同型（sed の BRE に `\?` `\+` を使う箇所）を grep → 他に該当なし。
- 型: メモリ「変異が素通りする型 ⚠️変異が当たらない」・PR #128 と同じ系統（Windows 緑 / Mac 赤）。

## 3. G1 課題ページの機械照合（§3-3 の前段・2026-09-26）

- 手順: `python3 build_task_pages.py --subject P010 --out <scratch>` で 10 枚を再生成（repo 外・`pages/` は gitignore 済みなので repo は汚さない）。
- 結果: 10 枚すべてで **生の `**` = 0**、`<strong>` の開閉が一致、`<title>` は「G1 ブロック N」まで（条件・題材名なし）。
- 強調の照合: 各ブロックの `<strong>` 数は 11（UI の定数）＋原典 md の `**…**` 数（HI=5 → 16、LO=3 → 14、copy=0 → 11）に一致し、**原典の強調が html に欠落しているものは 0**。
- ⚠️ 機械で言えるのはここまで。**文面の妥当性・強調の反転（HI/LO の取り違え）・Drive 上の実物は目視と記録票 C（研究者）**。P010 はブロック定義の一例であり、確証標本（P017 / P018 ほか）の実割付は使っていない。

## 4. 台帳項目の再確認（9/20 → 9/26・一次で確認）

| 項目 | 一次 | 結果 |
|---|---|---|
| G1-9 `status` | `config.json` | `CONFIRMATORY_IN_PROGRESS_1_OF_3` のまま（メモの記述と同じ） |
| G1-10 roster | 同上 | `sample_roster.confirmatory` は 2 名・`n_subjects=3`（3 人目未登録） |
| G1-11 週セレクタ | `src/App.tsx:240-249` | 週セレクタが在り既定は `week1_blind`（コードで強制していない） |
| ADR-031 / 032 | 各 ADR の「ステータス」 | Proposed（同意文書の改訂が研究者の承認待ち）。ADR-034 は Accepted |
| O1-3 O1 事前登録 | `experiments/` を ls | `*left-observation*` は存在しない（未作成のまま） |
| 承認マーカ | repo 全体を grep | `<!-- o1-esm-consent: approved -->` は steering の記述にしか無く、文書には未挿入 |
| 配布スクリプトの既定タグ | `grep` | `make-common-app-zip.sh` = `v0.1.24`（`make-distribution.sh` は既定 `v0.1.23`）。⚠️ 古いまま |
| C-3 残骸 worktree | `git worktree list` | この Mac には無い（Windows 機側の話） |
