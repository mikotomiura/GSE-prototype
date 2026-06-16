# 設計 v1 (退避) — Task D「オフライン解析 gse-replay 拡張」

> /reimagine Step 1 で退避した初回案。比較用。最新の採用案は design.md を参照。

## アプローチ

記録済み NDJSON を読む**純解析パイプライン**を `gse-replay` に追加する。中核は新規
`src-tauri/src/analysis/calibration_eval.rs`(OS 非依存・純関数)で、replay.rs は CLI 配線のみ。
既存 `metrics.rs`(v0.2 流 confusion/precision/recall)は **流用しない**(D-14)。新パスとして
方向付き C-index・2段ゲート・MNAR 上下限・ビネット採点を実装する。

責務分割:
- **抽出層** (replay.rs): NDJSON 1 セッションを `SessionData`(session_meta + probe_assignment +
  realtime_label + vignette_response + feat 列)に組み立てる。新 4 variant を `ReplayEvent` に追加。
- **解析層** (calibration_eval.rs): `SessionData` → 窓集約 → C-index/ゲート/MNAR/ビネット/二軸性。
  単一セッションで計算可能な指標は CLI `--calibration` が metrics.json に出力。
  **被験者内 holdout・被験者横断ゲート**は純関数として実装し、合成データで golden test。
  実データの multi-session/multi-subject オーケストレーションは **Task E**(handoff 明記)。

なぜ CLI は単一セッションか: NDJSON 1 ファイル = 1 セッションで、subject_id/session 番号は
gse-dataset のディレクトリ構造(P000/, ファイル時刻順)が持つ。被験者横断の集約は Task E。
Task D は「最初の2セッションで凍結」の holdout 分割ロジックと全ゲート関数を実装し golden test で
数値を決定論的に固める(handoff: 「ロジックまで実装、実データ評価は E」)。

## 変更対象

### 新規作成
- `src-tauri/src/analysis/calibration_eval.rs` — 較正解析の純関数群 (compute_* / format_*_pretty)。
- `src-tauri/tests/fixtures/calibration_minimal.ndjson` — CLI 抽出経路用の合成 NDJSON。

### 修正
- `src-tauri/src/analysis/mod.rs` — `pub mod calibration_eval;` 追記。
- `src-tauri/src/bin/replay.rs`: ReplayEvent に 4 variant 追加・網羅 match 2 箇所更新・
  `--calibration` フラグ追加・`collect_session_data()` で抽出。
- docs (architecture/repository-structure/functional-design/glossary) 追記。

### 不変
- `schema_dto.rs` / `schema/current.json`(A 凍結)・`metrics.rs`(流用禁止 D-14)。

## 中核アルゴリズム (要点)
- 窓集約: 【判断 A】raw_x/raw_y 中央値・MIN_WINDOW_FEATS=3 推奨。
- C-index: Harrell C 流 concordance。X↔Q1 と Y↔Q2 併報。【判断 B】ゲートは X↔Q1 主・Y↔Q2 secondary。
- 前向き holdout: 先頭2=calibration 除外・残り=eval。X は再計算せず分割のみ。
- 2段ゲート: 測定法(回答率/latency/有効件数/ビネット)→ モデル(Go/Kill/INCONCLUSIVE)。
- MNAR: 未回答 q を 5/1 代入で C-index 上下限。除外しない。
- ビネット採点: frontend と同一 infer_quadrant。Recall 点推定なし。track=exploratory 隔離。

## 出力
`compute_session_calibration -> SessionCalibration`(Serialize)を `--calibration --json` で metrics.json 出力。
被験者横断ゲートは Task E が集約。

## テスト戦略
- 単体: concordance/2段ゲート/MNAR/ビネット/holdout/track 隔離を合成 in-code データで決定論検証。
- 統合: 合成 calibration_minimal.ndjson で --calibration を end-to-end。
- 回帰: --snapshot minimal 緑・cargo test/clippy 緑・emit_schema 差分なし。

## 比較点
- A. 窓集約方法。B. C-index ペアリング。
