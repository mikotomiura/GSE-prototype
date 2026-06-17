# 設計 — calibration-smoke-runbook

## 実装アプローチ

実データ収集の核 (GUI 実機) は人手に委ね、その**周辺の非GUI部分**を整備する:
(1) ビルド検証、(2) `--calibration`→`gse-cohort` を束ねる helper、(3) 収集ランブック、(4) fixtures ドライラン。
製品コードは触らない。既存 `sync-session.*` の I/O 契約 (位置引数 / `--no-commit` 風フラグ / exit code) を尊重。

## 変更対象

### 新規作成
- `scripts/run-calibration-cohort.sh` — git-bash 用 helper。
  - 入力: dataset root (既定 `$GSE_DATASET` → なければ `C:/gse-dataset`)。
  - 手順: (a) `cargo build --release --bin gse-replay --bin gse-cohort` を 1 回、
    (b) `<root>/raw/P*/` 各被験者の NDJSON を時刻順に `gse-replay --calibration ... --json` →
    `<root>/metrics/Pxxx/<os>/Pxxx.calib.json` を生成 (os = uname 判定 windows/macos)、
    (c) `gse-cohort <root>` を実行しコホート判定 JSON を stdout + `<root>/cohort/cohort_<date>.json` に出力。
  - フラグ: `--no-cohort` (calib.json のみ) / `--dry-run` (生成せずコマンド表示) / `--os <macos|windows>` /
    `--root <path>`。NDJSON は読むだけ・移動やコミットはしない。
- `docs/calibration-smoke-runbook.md` — 収集ランブック (下記構成)。

### 修正
- `docs/functional-design.md` — §2.x 較正解析の近くに runbook へのポインタを 1 行追記 (任意・最小)。

### 触らない
- `src-tauri/src/`, `src/` (製品コード)。logger の P000 固定も改修しない (運用で吸収)。
- 既存 `sync-session.*` / `sync-all.*` (v0.2 metrics 経路はそのまま)。

## ランブック構成 (`docs/calibration-smoke-runbook.md`)
1. **前提/env**: `GSE_DATASET=C:\gse-dataset` 設定。git-bash 必須。プライバシー (NDJSON ローカル保持・共有は集計 JSON のみ §10)。
2. **ビルド**: `cargo build --release` / `npm run build` (or `npm run tauri dev` で起動)。
3. **Phase A 自己ドッグフード (1名・end-to-end 検証)**: アプリ起動 (blind dashboard 既定) → 較正セッションを1本
   → `raw/P000/gse_*.ndjson` 生成を tracing log の `resolved_log_dir` で確認 → helper で P000 を解析 →
   `metrics/P000/<os>/P000.calib.json` が出ることを確認。input OS フックは実機確認。
4. **Phase B 3-5名スモーク**: 各参加者でセッション収集。**logger は P000 固定**なので、各参加者ぶんの
   `raw/P000/*.ndjson` を収集後に `raw/P001`, `raw/P002`, ... へ手動整理 (手順明記)。
   PreReg-5 最低要件: 評価セッション ≥6/人 (= main セッション ≥8 本。先頭2本は β 較正 holdout)・
   ランダムプローブ ≥16件/人。`interventionEnabled=false`・`calibrationMode=ON` で収集。
5. **判定**: `scripts/run-calibration-cohort.sh` → cohort JSON。`overall` の読み方:
   `go`/`kill`(measurement or model)/`inconclusive`/`data_insufficient`。
   **未達なら「データ拡充」と正直報告** (無理に go と言わない・§11)。MNAR/二軸性は併走報告。
6. **共有**: `metrics/` と `cohort/` の集計 JSON のみ gse-dataset へ (NDJSON は置かない)。

## テスト戦略
- **ビルド検証**: `cargo build`(workspace) + `npm run build` 緑。可能なら `cargo tauri build` (重いので任意)。
- **ドライラン (非GUI)**: 一時 fixture ツリーを作り (`tests/fixtures/calib_subject_*.ndjson` を raw/P001 等に配置)、
  `scripts/run-calibration-cohort.sh --root <tmp>` を実行 → calib.json 生成 + `gse-cohort` 判定 JSON が出ることを確認。
  helper のコマンド連鎖・OS パス・cohort 入力整合を実証する。
- `cargo test --workspace` 緑維持 (製品コード無変更なので回帰なし、確認のみ)。
- helper は shellcheck 観点で安全に (set -euo pipefail・パスのクォート・ファイル数/サイズは gse-replay/cohort 側の上限に委譲)。

## ロールバック計画
- 追加は scripts 1 本 + docs のみ。製品コード不変 → revert で完結、副作用なし。
