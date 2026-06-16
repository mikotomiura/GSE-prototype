# 設計 — Task E 通し検証 (cohort orchestration)

## 実装アプローチ (v1 草案 — /reimagine で v2 と比較する)

D の per-被験者解析 (`compute_calibration_metrics` → `CalibrationReport`) はそのまま再利用し、
**被験者横断 (cohort) 集約層**だけを追加する。データフロー上、gse-dataset には
`metrics/P*/<os>/*.metrics.json` (集計値) しか置かれず NDJSON は各収集機に留まる (§10/data-privacy)。
したがって cohort 集約の入力は **被験者別 calibration レポート JSON** とする (NDJSON ツリー走査ではない)。

層構成 (D と対称: 純関数は analysis、I/O は bin):
- **純関数 (analysis/calibration_eval.rs に追加)**: 被験者別サマリの集合 → `model_gate`/`measurement_gate`
  を再利用して cohort 判定を組み立てる `cohort_verdict(...) -> CohortReport`。OS 非依存・golden test 可能。
- **I/O (bin)**: `metrics/P*/<os>/*.calib.json` を走査・読込・デシリアライズし、上記純関数を駆動して
  cohort レポート JSON を出力する。実装形態 (gse-replay `--cohort` サブモード vs 独立バイナリ `gse-cohort`)
  は **/reimagine の設計判断 A** で確定する。

`CalibrationReport` は現状 `Serialize` のみ。読み戻しのため **`Deserialize` を追加 (派生のみ・additive)**。
これは再実装ではなく、D の出力構造に派生属性を 1 つ足すだけ (挙動不変)。

### 設計判断 B (cohort ゲートに入れる代表値) — 確定方針
PreReg-4 は凍結済みで文言は「各人の C-index **中央値**」。凍結契約を曲げないため、
**ゲート駆動 = `cindex.x_q1_session_median`** とする。`x_q1_pooled` は頑健性情報として
cohort レポートに併記するがゲート判定には使わない (forking paths 排除)。
session_median が `None` (セッション数不足) の被験者は「データ不足」として判定母数から除外し notes に記録
(無理に値を捏造しない・§11 主張限界)。

## 変更対象

### 修正するファイル
- `src-tauri/src/analysis/calibration_eval.rs` — `CalibrationReport` 及び全 sub-struct/enum に
  `Deserialize` 派生を追加。cohort 純関数 `cohort_verdict` + `CohortReport` 型を追加 (`model_gate`/
  `measurement_gate` を再利用)。
- `src-tauri/src/bin/replay.rs` **または** 新規 `src-tauri/src/bin/cohort.rs` — I/O 層 (/reimagine A で確定)。
- (新規バイナリなら) `src-tauri/Cargo.toml` に `[[bin]]` 追記。

### 新規作成するファイル
- (案による) `src-tauri/src/bin/cohort.rs` — cohort オーケストレーション CLI。
- `src-tauri/tests/fixtures/cohort_*.calib.json` — 合成多被験者 calibration レポート (golden 入力)。

### 削除するファイル
- なし。

## 影響範囲
- A schema 不変 (`schema_dto.rs` touch しない)。D の純関数シグネチャ不変 (派生追加のみ)。
- `gse-replay --snapshot` 回帰に影響なし (新モード追加のみ・既存モード不変)。
- mutually-exclusive モードフラグに `--cohort` を足す場合は mode_count 配列に 1 項追加 (案 A 採用時)。

## 既存パターンとの整合性
- D の「純関数 (calibration_eval) + I/O (replay)」分離をそのまま踏襲。
- `model_gate`/`measurement_gate` は D が golden test 済の純関数 → E は実データ駆動と集約のみ追加。
- 出力は集計値のみ (C-index 中央値・回答率・判定 enum・件数)。ID/本文は到達しない (§10/DD-9)。

## テスト戦略
- 単体/golden: 合成多被験者 `*.calib.json` を入力に `cohort_verdict` の Go/Kill/INCONCLUSIVE 分岐を
  決定論検証 (model_gate の median≥0.65&all≥0.55 / measurement_gate の overall<0.80 等の境界)。
  session_median=None 被験者の除外 + notes 記録を検証。
- 回帰: `gse-replay --snapshot tests/snapshots/minimal.json` が byte-equal 維持。
- `cargo test --workspace` 緑・clippy 緑・main ビルド可。
- E2E (自己ドッグフード): A+B+C+D 統合ビルド → 実セッション 1 本記録 → `gse-replay --calibration` で
  metrics.json 生成確認 (input/ OS フックは実機手動)。input は OS 依存のため cargo test 対象外。
- 3-5 名スモーク: 実データを cohort にかけ PreReg-1..8 判定。PreReg-5 (eval≥6/人・probe≥16/人) 未達なら
  「データ拡充」と正直報告 (Go と言わない)。

## ロールバック計画
- 新モード/新バイナリ + 派生追加のみで既存挙動不変 → revert は当該コミットの戻しで完結。
- cohort 判定が誤っても D の per-被験者 metrics.json と PreReg 契約は独立に保たれる。
