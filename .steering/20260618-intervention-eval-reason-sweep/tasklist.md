# タスクリスト

## 準備
- [x] ハンドオフ / improvement-plan / intervention.rs / intervention_eval.rs / replay.rs / schema_dto.rs を読む
- [x] 影響範囲を impact-analyzer で調査（InterventionDecision は schema 非依存と確認）
- [x] 必須 Skill 参照（rust-standards / architecture-rules / intervention-design / hmm-analysis / ml-workflow）

## 実装（intervention.rs — production 不変）
- [x] `OpportunityReason` enum + `as_str()`（現行 8 文字列を byte 一致再生）
- [x] `calculate_opportunity` を `(f64, OpportunityReason)` 返しに
- [x] `InterventionThresholds` config（Default = 現行 const）
- [x] `InterventionPolicyState` に thresholds / `new_with_thresholds`
- [x] decide/update_wall_accumulation/should_log/reason_for を self.thresholds へ
- [x] `InterventionDecision` に `#[serde(skip)] opportunity_reason`
- [x] default == const の assert テスト / 既存 5 テスト不変確認

## 実装（intervention_eval.rs）
- [x] `EvalDecision` 構造体へ拡張 / evaluate_defer_runs 対応
- [x] `reason_breakdown: Vec<ReasonStratum>` + `recall` を InterventionMetrics に
- [x] `compute_intervention_metrics` に thresholds 引数
- [x] sweep: `SweepInput` / `compute_intervention_sweep` / `InterventionSweepReport`
- [x] pretty + JSON 整形（reason 別表 / 閾値別表）

## 実装（bin/replay.rs）
- [x] `--sweep` モード（複数 positional / 相互排他 / 実行経路 / usage）

## テスト
- [x] reason 分類・保存則・sweep 単調性/境界・recall の新規 unit (+ DC 不変条件の定数ガード)
- [x] `cargo test --workspace` 通過 (164 lib + 12 bin)
- [x] `gse-replay --snapshot` byte-equal（production 不変の証明、15/15）
- [x] `emit_schema` vs schema/current.json byte-equal（drift なし）
- [x] clippy 新規警告なし / `cargo fmt --check` 通過

## レビュー
- [x] code-reviewer + security-checker 並列（HIGH/CRITICAL なし）
- [x] code-reviewer MEDIUM×2（magic 0.60 / power warning 欠落）対応済み
- [x] LOW（reason_index assert / BinaryConfusion::merge dedup / 不変条件定数テスト）対応済み
- [~] /cross-review の Codex 系統: jq 不在で blocked → Claude 単独へ縮退（理由は完了報告に明記）

## 実データ / アウトプット
- [x] P000 13 セッションに `--sweep` 実行 → results.md + p000_sweep.json
      （犯人=correction_after_pause / sweep 表 / 閾値候補 3 案: 0.70/0.80/0.85）

## 完了処理
- [x] design.md / decisions.md / results.md 最終化
- [ ] git commit（ユーザー確認待ち: ブランチ選択）
