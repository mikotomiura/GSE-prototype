# タスクリスト — Task D「オフライン解析 gse-replay 拡張」

## 準備
- [x] docs / 設計書 §4.2/§6.4/§7/§8/§9/§10/§15・PreReg 凍結・decisions(D-8..D-14/TA-3/DC-*) を読む
- [x] replay.rs / logger.rs / metrics.rs / loop_step.rs / VignetteTest.tsx を読む
- [x] file-finder + impact-analyzer で fixture/snapshot/影響範囲を調査
- [x] /reimagine で 2 案比較・採用案確定(v2 ハイブリッド・ewma 中央値)

## 実装 (calibration_eval.rs — 純ロジック先行)
- [x] enum 型(TrackKind/ProbeSourceKind/SkipReasonKind/QuadrantKind)・AggSpec/AggSource/AggStat 定義
- [x] `infer_quadrant(q1,q2)` 実装(frontend と同一規則・端のみ採用)
- [x] `concordance_index(pairs)` 実装(比較可能ペアのみ・タイ 0.5・None 条件)
- [x] `aggregate_window(feats, start, end, spec)` 実装(0 件除外・median/mean/tail)
- [x] `prospective_holdout(sessions)` 実装(先頭2=較正除外・残り=評価)
- [x] `measurement_gate` / `model_gate`(Go/Kill/INCONCLUSIVE)実装
- [x] `compute_mnar_bounds`(q=5/1 代入 → C-index 上下限・無回答率閾値・母数=窓X有り)実装
- [x] `score_vignettes`(6/8)・`compute_bidimensionality`(非対角<10%)実装
- [x] `compute_calibration_metrics(sessions) -> CalibrationReport`(track 隔離・Recall withheld)+ Serialize
- [x] `format_calibration_pretty` 実装
- [x] calibration_eval の単体テスト 24 件(各関数の境界値・合成多被験者ゲート・偶然水準 0.5 厳密)

## 実装 (replay.rs 配線)
- [x] ReplayEvent に 4 variant 追加(NDJSON フィールド名一致)
- [x] 網羅 match 2 箇所更新(timestamp()=None / run_replay match — 読み飛ばし)
- [x] load_calibration_session(1 パス抽出 + collect_logged_feats 再利用・q 範囲再検証)
- [x] Args に calibration + 可変長 positional・parse_args 排他/`--json` 条件更新・ファイル数上限
- [x] main に --calibration 分岐(複数 file collect → compute → pretty/JSON)
- [x] analysis/mod.rs に `pub mod calibration_eval;`

## fixture / 統合テスト
- [x] 合成 `calib_subject_s1/s2/s3_eval.ndjson`(既知 X 系列 × realtime_label/vignette/probe_assignment/session_meta)
- [x] replay.rs 統合テスト 3 件: `--calibration` 経路 end-to-end(抽出→C-index→holdout→MNAR→ビネット→JSON)

## テスト・検証 (Step F)
- [x] `cargo test --workspace` パス(152 件・test-runner で実行)
- [x] `gse-replay --snapshot tests/snapshots/minimal.json` 緑(15 snapshot 一致・回帰維持)
- [x] `cargo clippy` 緑(新規コード警告 0)・`emit_schema` byte-equal(schema 不変確認)

## レビュー (Step G)
- [x] code-reviewer + security-checker を並列起動・HIGH 全対応(MNAR 母数/二軸性doc)・MEDIUM 全対応(security 含む)

## ドキュメント (Step H)
- [x] docs/architecture.md(フロー4b) / repository-structure.md(モジュール tree/list/依存矢印)に calibration_eval 追記
- [x] docs/functional-design.md に較正解析機能(§2.x)・docs/glossary.md に 時間隔離窓/MNAR 範囲報告 追記

## 完了処理 (/finish-task)
- [x] design.md 最終化(/reimagine 採用案)・decisions.md 作成(DD-1..DD-9)
- [ ] /finish-task で /cross-review(Claude code-reviewer ∥ Codex codex-review)必須・両者一致 CRITICAL/HIGH 最優先
- [ ] git commit(git-workflow・Refs: 付与)
