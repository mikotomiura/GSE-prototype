# 設計

## 実装アプローチ

`concordance_index()` が内部で数えている比較可能ペア数 (`comparable`) を、既存シグネチャを
壊さずに外へ出す。具体的には `concordance_index_detailed(pairs) -> Option<(f64, u64)>` を新設し、
既存 `concordance_index()` はその第 1 要素だけを返す薄いラッパに書き換える (ロジックの二重化を避ける)。

得られたペア数を `SubjectCindex` (per-被験者) → `CohortSubjectSummary` (cohort read-model) の
2 段に、既存の「部分ビュー」パターン (`AxisDispersionView` が `AxisDispersion` の一部だけを
宣言する先例、`cohort.rs:124-129`) に倣って配線する。

到達可能性 bool (`x_q1_gate_attainable`) は `CINDEX_GO_MEDIAN` / `CINDEX_GO_ALL_MIN` 定数を
参照する純関数として `calibration_eval.rs` 側に置き、新しい閾値は導入しない。
C-index が `0.5/k` 刻みでしか値を取れない (`k` = 比較可能ペア数) ことから、
「そのペア数で理論上ゲート値に到達できるか」を機械的に判定する。

## 変更対象

### 修正するファイル
- `src-tauri/src/analysis/calibration_eval.rs`
  - `concordance_index_detailed()` を新設 (`concordance_index()` の実装を移し、薄いラッパ化)
  - `SubjectCindex` に以下を追加:
    - `x_q1_session_comparable_pairs: Vec<u64>` / `y_q2_session_comparable_pairs: Vec<u64>`
      (中央値計算と同じ `filter_map` の中で同時に集める。順序・件数を一致させる)
    - `x_q1_session_min_comparable_pairs: Option<u64>` / `x_q1_session_median_comparable_pairs: Option<u64>`
      (Vec から導出。`y_q2` 側は §2-4 の指定に無いため x_q1 のみでよい)
    - `x_q1_gate_attainable: Option<bool>` (母数が空なら `None`)
  - `compute_calibration_metrics()` の per-session ループ (旧 949-970 行相当) を
    `concordance_index_detailed` を使うよう書き換え、値とペア数を同じ `filter_map` で収集
  - 到達可能性を計算する純関数 (例: `cindex_gate_attainable(comparable_pairs: &[u64]) -> Option<bool>`)
    を新設。`CINDEX_GO_MEDIAN` / `CINDEX_GO_ALL_MIN` を参照
- `src-tauri/src/analysis/cohort.rs`
  - `CindexView` に上記フィールドを部分ビューとして追加 (`#[serde(default)]`)
  - `CohortSubjectSummary` に同フィールドを追加し、`cohort_verdict()` 内の構築箇所
    (`cohort.rs:471-487` 相当) で配線する
  - 母数除外規則は追加しない (`gate_eligible` の判定条件は変更しない)

### 新規作成するファイル
- なし

### 削除するファイル
- なし

## 影響範囲

- `CalibrationReport` の JSON 出力にフィールドが増える (`schema_dto.rs` の対象外・drift check 無関係)。
- `cohort.rs` の JSON 出力 (`CohortSubjectSummary`) にもフィールドが増える。
- 既存 `x_q1_session_median` 等の値は変更しない (回帰テストで確認)。
- `gse-replay --snapshot` の `FeatSnapshot` 列は本タスクの対象外 (`analysis::calibration_eval` /
  `cohort` は HMM の `FeatSnapshot` 生成経路とは別モジュール) だが、byte-equal を実測確認する
  (§4 の指示通り)。

## 既存パターンとの整合性

- `AxisDispersion` (生 Q1/Q2 分布向け) と `ResponseDispersion` の「算術的事実のみを出し、
  閾値は出さない」という設計思想をそのまま踏襲する (`calibration_eval.rs:639-670` の doc コメント)。
- `cohort.rs` の read-model が「必要フィールドだけを部分宣言する」パターン
  (`AxisDispersionView` / `DispersionView` の先例、`cohort.rs:124-143`) に倣う。
- `concordance_index()` を壊さず薄いラッパにする設計は、既存呼び出し元の互換性を壊さない
  最小差分の原則に沿う。

## テスト戦略

- 単体テスト (`calibration_eval.rs` 内):
  1. 比較可能ペア 1 件のセッションで C-index が算出され、ペア数が `1` と報告される
  2. 比較可能ペア 0 件 (straight-lining) のセッションが `None` になり、中央値の母数からも
     ペア数 `Vec` からも同じ集合として除外される (順序・件数の一致を assert)
  3. 既存の `x_q1_session_median` / `y_q2_session_median` の値が変更前と 1 ビットも変わらない
     (既存の期待値ベースのテストケースを流用して比較)
  4. `concordance_index()` と `concordance_index_detailed()` の第 1 要素が任意の入力で常に一致
  5. `cindex_gate_attainable()` が `CINDEX_GO_MEDIAN` / `CINDEX_GO_ALL_MIN` を跨ぐ境界ケース
     (例: 1 ペアしかない → 到達可能でも `0.0` か `1.0` にしかなれない) で妥当な bool を返す
- 単体テスト (`cohort.rs` 内): `SubjectCalibrationView` のデシリアライズで新フィールドが
  部分ビューとして正しく読めること、および欠落時 (旧 JSON) に `#[serde(default)]` でパースが
  壊れないこと
- 統合: `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json`
  の byte-equal 実行 (回帰・本タスクは非該当のはずだが実測で確認)
- E2E: 不要 (`analysis/` は OS 非依存の純粋関数レイヤ)

## ロールバック計画

追加のみの変更 (既存フィールド・関数シグネチャは変更しない、`concordance_index()` は
ラッパ化のみで戻り値の意味は不変) のため、問題が出た場合は該当コミットを revert すれば
`SubjectCindex` / `CohortSubjectSummary` は追加前の形に戻る。閾値・判定ロジック
(`model_gate` / `measurement_gate`) 自体には触れていないため、ゲート判定への影響はない。
