# 設計 — Task E 通し検証 (cohort orchestration) — v2 (再生成)

## 実装アプローチ

cohort 判定の計算実体は極めて小さい: 被験者ごとに「C-index 代表値」と「回答率」を集め、
既存の純関数 `model_gate(&[f64])` と `measurement_gate(overall, &[f64])` に渡すだけ。
したがって設計の要点は **「per-被験者の数値をどこから・どれだけ薄く取り出すか」** に尽きる。

### 原則: D には一切触れない (read-model DTO で疎結合)
cohort が必要とする per-被験者の値は CalibrationReport のごく一部 (C-index 中央値・回答率・
評価セッション数・有効プローブ数・無回答率・per_subject_pass 等の数スカラ) だけ。
serde は既定で未知フィールドを無視するため、**必要フィールドだけを宣言した軽量 read-model
構造体**を用意すれば、D が出力する calibration JSON 全体をそのままパースできる。
→ **D の `calibration_eval.rs` (構造体・関数) は一切変更しない** (Deserialize 派生も足さない)。
D を文字通り凍結したまま、新しい関心 (cohort) を独立モジュールに隔離する。

### 層構成 (D と対称・関心分離)
- **純ロジック (新規 `analysis/cohort.rs`)**: per-被験者サマリ集合を受け取り、`calibration_eval` の
  `model_gate`/`measurement_gate` を import して cohort 判定を組み立てる `cohort_verdict(...) -> CohortReport`。
  OS 非依存・golden test 可能。read-model DTO (`SubjectCalibrationView`) もここに置く。
- **I/O (新規バイナリ `gse-cohort`)**: `<dataset>/metrics/P*/<os>/*.calib.json` を走査・読込・
  軽量デシリアライズし、`cohort_verdict` を駆動して cohort レポート JSON を出力する。

### なぜ独立バイナリ (`gse-cohort`) か / replay --cohort サブモードにしない理由
- 入力モデルが根本的に異なる: replay は「1 NDJSON セッション」、cohort は「JSON ファイル群のツリー」。
  replay の mutually-exclusive モード行列に手を入れると、凍結している `--snapshot` 回帰経路に
  変更面が生じる。独立バイナリなら **replay は 1 文字も変えず回帰リスクゼロ**。
- 「1 ツール 1 責務」: replay = NDJSON→metrics、cohort = metrics→横断判定。合成可能なパイプライン
  (`gse-replay --calibration ... --json > P00X.calib.json` → `gse-cohort <dataset>`)。
- Python 集約案は不採用: 凍結ゲート閾値を Python 側で再実装することになり drift / forking paths を招く。
  Rust の純関数を再利用できる Rust 経路に統一する。

### 設計判断: cohort ゲートに入れる代表値 = session-median (凍結契約に従う)
PreReg-4 は凍結済みで「各人の C-index **中央値**」と明記。契約を曲げないため
**ゲート駆動 = `cindex.x_q1_session_median`**。`x_q1_pooled` は頑健性参考値として cohort レポートに
併記するがゲートには使わない (forking paths 排除)。session_median が `None` (セッション不足) の
被験者は判定母数から除外し notes に記録 (値を捏造しない・§11)。

## 変更対象

### 新規作成するファイル
- `src-tauri/src/analysis/cohort.rs` — read-model DTO `SubjectCalibrationView` + 純関数
  `cohort_verdict` + 出力型 `CohortReport` (model_gate/measurement_gate 再利用)。
- `src-tauri/src/bin/cohort.rs` — `gse-cohort` バイナリ (dataset ツリー走査・JSON 読込・出力)。
- `src-tauri/tests/fixtures/cohort/*.calib.json` — 合成多被験者 calibration レポート (golden 入力)。

### 修正するファイル
- `src-tauri/src/analysis/mod.rs` — `pub mod cohort;` 追加。
- `src-tauri/Cargo.toml` — `[[bin]] name = "gse-cohort"` 追記。

### 触らないファイル (重要)
- `src-tauri/src/analysis/calibration_eval.rs` — **無変更** (D 凍結)。
- `src-tauri/src/bin/replay.rs` — **無変更** (--snapshot 回帰経路を保護)。
- `src-tauri/src/schema_dto.rs` — **無変更** (A 凍結)。

## 既存パターンとの整合性
- D の「純関数 (analysis) + I/O (bin)」分離を踏襲。cohort も同型。
- `model_gate`/`measurement_gate` (D が golden 済) を再利用。E は実データ駆動 + 集約のみ。
- 出力は集計値のみ (C-index 中央値・回答率・判定 enum・件数)。ID/本文は read-model に存在しない (§10/DD-9)。
- 走査上限・パスバリデーション (security): 被験者数/ファイル数上限を設け、シンボリックリンク・
  予期せぬ深さを弾く (D の MAX_CALIBRATION_FILES と同精神)。

## テスト戦略
- 単体/golden (`analysis/cohort.rs`): 合成 read-model 集合で `cohort_verdict` の Go/Kill/INCONCLUSIVE
  分岐を境界検証 (model_gate: median≥0.65 & all≥0.55 / Kill: median≤0.55 or 2人≤0.50,
  measurement_gate: overall<0.80 or 2人<0.70)。session_median=None 除外 + notes 検証。
- 統合 (バイナリ): fixture ツリーを `gse-cohort` に通し JSON 出力を検証 (DTO の subset パースが
  D の実 JSON 形と一致することを、D の出力 fixture で確認)。
- 回帰: `gse-replay --snapshot tests/snapshots/minimal.json` が byte-equal 維持 (replay 無変更で自明)。
- `cargo test --workspace` 緑・clippy 緑・main ビルド可。
- E2E (自己ドッグフード): A+B+C+D 統合ビルド → 実セッション 1 本 → `gse-replay --calibration` で
  metrics.json 生成確認 (input/ OS フックは実機手動・cargo test 対象外)。
- 3-5 名スモーク: 実データを `gse-cohort` にかけ PreReg-1..8 判定。PreReg-5 (eval≥6/人・probe≥16/人)
  未達なら「データ拡充」と正直報告 (Go と言わない)。

## ロールバック計画
- 全て新規ファイル + 2 行の登録 (mod.rs / Cargo.toml) のみ。既存挙動完全不変 → revert は新規分の
  削除で完結。cohort 判定が誤っても D の per-被験者 metrics.json と PreReg 契約は独立に保たれる。

## 設計判断の履歴
- 実行回数: 1 回目
- 採用: **v2 (再生成案)**
- 根拠: handoff 最重要制約「D を再実装しない／凍結」を最も忠実に満たす。D (calibration_eval.rs)・
  replay.rs・schema_dto.rs を 1 文字も変えず、serde の未知フィールド無視を使った軽量 read-model DTO で
  cohort 集約を疎結合に隔離。重い CalibrationReport 全体の Deserialize 化が不要で、回帰リスク最小。
  詳細は design-comparison.md。
