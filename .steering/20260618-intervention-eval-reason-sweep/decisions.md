# 重要な設計判断

## D1: OpportunityReason enum を reason 文字列の単一真実源にする

- **判断**: `calculate_opportunity` の戻り値を `(f64, String)` → `(f64, OpportunityReason)` に変更。
  `OpportunityReason::as_str()` が現行の 8 reason 文字列を **byte 一致で再生**し、`reason_for` の
  Nudge ケースは `opportunity_reason.as_str().to_string()` に置換。
- **根拠**: 評価層が reason 別層別化するには「全 decision（nudge に限らず none/defer も）の
  opportunity reason」が機械可読で要る。production の `reason: String` は nudge 以外では
  opportunity reason を表さない（`below_need_threshold` 等）。enum を `InterventionDecision` に
  `#[serde(skip)]` で載せれば全 decision で取得でき、文字列は不変。
- **production 不変の保証**: as_str が現行文字列を再生 → 既存 3 つの reason 文字列 assert テスト・
  NDJSON ログ・IPC JSON が不変。テスト `opportunity_reason_as_str_matches_legacy_strings` で固定。
- **影響分析（impact-analyzer）**: `InterventionDecision` は schema_dto.rs の独立 DTO 経由でしか
  schema 化されず、logger は固定 format 文字列、IPC は serde skip で不可視 → schema drift 0 /
  NDJSON byte 不変 / frontend 型不変。ユーザー承認済み（ハンドオフ §2 で sanction）。

## D2: 閾値を const から `InterventionThresholds` config へ（Default = 現行 const）

- **判断**: 5 float 閾値を `InterventionThresholds` に集約。`InterventionPolicyState` が 1 個保持し、
  `new(now)` は `Default`（= 現行 const）、`new_with_thresholds(now, t)` が評価用。decide /
  update_wall_accumulation / should_log / reason_for の const 参照を `self.thresholds.*` に置換。
- **根拠**: sweep は production を変えずに閾値だけ差し替える必要がある。Default を const に束ねれば
  production 呼び出し（lib.rs の `new(now)`）は完全不変。
- **却下案**: `decide(input, &thresholds)` 引数渡し → lib.rs 等全呼び出し変更が要り侵襲大。
- **保証**: テスト `default_thresholds_equal_production_consts` が Default==const を機械的に固定。
- **sweep 対象**: `nudge_need` のみ。duration/cap/pause band const は据え置き（本タスク対象外）。

## D3: sweep 範囲を nudge_need 0.50–0.90 に限定（DC 不変条件の保護）

- **判断**: `DEFAULT_SWEEP_NUDGE_NEED = [0.50..0.90 step 0.05]`、`MIN_SWEEP_NUDGE_NEED = 0.50`。
  `compute_intervention_sweep` は 0.50 未満の点を評価せず warning に記録。
- **根拠**: `evaluate_defer_runs` の回復起点は run 先頭。defer は `need>=nudge_need` のときのみ生じ、
  `nudge_need>=0.50` なら run 内 feat は `p_flow<=1-nudge_need<=0.50`、回復閾値は strict `>0.5`
  （`compute_recovered_at`）なので run 内 feat は回復に数えられず、回復は構造上 run の後に限られる。
  0.50 未満へ下げると本不変条件が破れる（起点を run 終端の次 feat へ要変更）。
- **保証**: テスト `sweep_skips_below_min_threshold` で 0.40 が skip + warning されることを固定。

## D4: reason 別 confusion は全 labeled decision を 1 reason bucket に層別化（保存則）

- **判断**: `ReasonStratum` で reason 別 BinaryConfusion を持ち、全体 confusion と同じ分類で
  両方を 1 パス加算。各 labeled decision はちょうど 1 reason に入るので
  Σ(reason confusion) == 全体 confusion。空 reason は出力から省く（和は不変）。
- **根拠**: HIR=0.647 の犯人 reason を特定する主目的に直結。保存則で集計バグを検出可能。
- **保証**: テスト `reason_breakdown_sums_to_global_confusion`。出力は `OpportunityReason::ALL`
  固定順で決定的（HashMap 非依存）。

## D5: EvalDecision は opportunity_reason のみ保持（need/opp/suppressed_by は持たない）

- **判断**: ハンドオフ §2-1 は need_score/opportunity_score/suppressed_by の保持も挙げるが、
  現行成果物（reason 別 HIR + nudge_need sweep）はいずれも消費しない。保持すると dead-field で
  clippy を汚すため `EvalDecision` は `ts / action / opportunity_reason` のみ。
- **根拠**: sweep は閾値ごとに `decide()` を再実行するため格納スコアは不要。将来の suppressor 別
  defer correctness（plan Phase 2）が要れば `decide()` 戻り値から自明に再取得できる。
- 注: コメントに同旨を明記（`EvalDecision` doc）。

## D6: --sweep は複数セッションをプール（results POOLED 行が主成果）

- **判断**: `--sweep` は `--calibration` と同じく複数 positional を受け、各セッションを独立
  `InterventionPolicyState` で評価（cooldown/cap は session/day 単位）し confusion/counts を生整数で
  プール。`SweepInput` は所有データ。
- **根拠**: 既存 results.md の見出しが POOLED（ACT=34）であり、閾値候補の根拠は pooled 指標。
  ファイル数上限は MAX_CALIBRATION_FILES を流用、各ファイルは MAX_SESSION_BYTES でガード。
