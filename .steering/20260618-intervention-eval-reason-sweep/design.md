# 設計

## 実装アプローチ

production 挙動を**完全に不変**に保ったまま、評価専用の計測能力を 2 軸で増やす:
(1) reason 別の HIR/Precision 分解、(2) `nudge_need` 閾値の sweep。

核となる設計判断は「閾値を const から注入可能 config へ」と「opportunity reason を機械可読 enum 化」。
いずれも既定値・既定文字列を現行と完全一致させることで production を不変に保つ。

### D1: `OpportunityReason` enum を単一真実源に（`intervention.rs`）
- 現行 `calculate_opportunity()` が返す 8 種の reason 文字列
  (`low_opportunity` / `short_pause` / `medium_pause` / `long_pause` / `active_typing` /
   `post_burst_pause` / `correction_after_pause` / `active_correction_loop`) を enum 化。
- `as_str()` が**現行文字列を byte 一致で再生**する → `reason_for` の Nudge ケースは
  `opportunity_reason.as_str().to_string()` に置換でき、3 つの文字列 assert テストは不変で通る。
- `calculate_opportunity()` の戻り値型を `(f64, OpportunityReason)` に変更（module 非公開、呼び出し元は decide() のみ）。
- `InterventionDecision` に `opportunity_reason: OpportunityReason` を **`#[serde(skip)]` 付き**で追加。
  影響分析で確認済み: schema_dto.rs は独立 DTO・logger は固定 format・IPC は serde skip で不可視
  → schema drift 0 / NDJSON byte 不変 / frontend 型不変。
  → eval は全 decision（nudge に限らず none/defer も）の opportunity reason を機械可読で取得できる。

### D2: `InterventionThresholds` config 構造体（`intervention.rs`）
- 5 つの float 閾値（`nudge_need`=0.60 / `wall_need`=0.70 / `wall_slack`=0.50 /
  `nudge_opportunity`=0.35 / `wall_opportunity`=0.45）を保持。`Default` が現行 const と同値。
- `InterventionPolicyState` に `thresholds: InterventionThresholds` フィールド追加。
  - `new(now)` は `Default` を使う → **production 呼び出し (lib.rs) は不変**。
  - `new_with_thresholds(now, thresholds)` を eval 用に追加。
- `decide()` / `update_wall_accumulation()` / `should_log()` / `reason_for()` の const 参照を
  `self.thresholds.*` に置換（duration/cap 系 const は sweep 対象外なので据え置き）。
- sweep 対象は `nudge_need` のみ。⚠️ DC 不変条件（need>=0.50 で defer-run 回復起点が run 後に限られる）を
  守るため sweep 範囲を **0.50–0.90（0.05 刻み, 9 点）** に限定。他閾値は既定固定。

### D3: eval の decision 保持を拡張（`intervention_eval.rs`）
- `decisions: Vec<(u64, InterventionAction)>` → `Vec<EvalDecision>`。
  `EvalDecision { ts, action, opportunity_reason, need_score, opportunity_score, suppressed_by }`。
- `evaluate_defer_runs` を `&[EvalDecision]` 対応に（`.action` / `.ts` を読む）。不変条件 doc は維持。

### D4: reason 別層別化 + recall（`intervention_eval.rs`）
- `ReasonStratum { reason, confusion: BinaryConfusion, act_labeled, hir, precision, act_count }`。
- `InterventionMetrics` に `reason_breakdown: Vec<ReasonStratum>`（enum 固定順で決定的）と
  `recall: Option<f64>`（= TP/(TP+FN)）を追加。`--intervention --json` がそのまま豊かになる
  （golden snapshot ではない stdout 出力なのでフィールド追加は安全）。
- `compute_intervention_metrics(...)` に `thresholds: &InterventionThresholds` 引数追加。
  既存 CLI/テストは `&InterventionThresholds::default()` を渡す＝出力不変。

### D5: sweep モード + CLI（`intervention_eval.rs` + `bin/replay.rs`）
- `SweepInput { feats, labels, key_press_ts }`（1 セッション分）。
- `compute_intervention_sweep(sessions: &[SweepInput], sweep_points: &[f64], recovery_window_ms)
   -> InterventionSweepReport`。各閾値で各セッションを独立評価し confusion/counts を**プール**。
  pooled HIR/precision/recall/DC/burden + reason 別 pooled breakdown を `SweepPoint` に格納。
- CLI に `--sweep` モード追加。`--calibration` と同じく**複数 positional**（1 被験者の複数セッション）を受け、
  プールして sweep 表を出す。pretty + `--json`。既存モードとの相互排他リストに追加。

## 変更対象

### 修正するファイル
- `src-tauri/src/analysis/intervention.rs` — OpportunityReason enum / InterventionThresholds /
  PolicyState に thresholds / decide 系の const→self.thresholds 置換 / InterventionDecision に skip field。
- `src-tauri/src/analysis/intervention_eval.rs` — EvalDecision / reason 層別化 / recall /
  thresholds 引数 / sweep 関数群 / pretty・JSON 整形。
- `src-tauri/src/bin/replay.rs` — `--sweep` モード追加（parse_args 相互排他 + 実行経路 + usage）。

### 新規作成するファイル
- なし（既存モジュールに追加）。出力 results は `.steering/.../results.md`。

## 影響範囲
- production: `InterventionPolicyState::new(now)` と `decide()` の挙動・戻り値（serde 出力）不変。
  lib.rs / frontend は変更不要。
- schema: `schema_dto.rs` / `schema/current.json` を触らない。`emit_schema` drift なし。
- snapshot: FeatSnapshot 列のみの golden。intervention 系は含まれず byte-equal 不変。

## 既存パターンとの整合性
- `--calibration` の複数 positional + プール集約パターンを `--sweep` に流用。
- `InterventionMetrics::empty()` の「ゼロ値 1 箇所集約」パターンを新フィールドにも適用。
- 純粋関数・`Result<_, String>`（bin 層）・`Vec` 決定順（HashMap 非依存）を踏襲。

## テスト戦略
- 単体（intervention_eval.rs）:
  - reason 分類: post_burst/short/correction/active_typing の opportunity_reason が期待 enum。
  - reason 層別 confusion の和 = 全体 confusion（保存則）。
  - sweep 単調性/境界: `nudge_need` を上げると ACT 数は単調非増加。境界 0.50 と 0.90 で panic しない。
  - recall = TP/(TP+FN) の算出。
- 単体（intervention.rs）: `InterventionThresholds::default()` が現行 const と一致する assert。
  既存 5 テスト（reason 文字列含む）が不変で通る。
- 回帰: `gse-replay --snapshot tests/snapshots/minimal.json` が byte-equal。
- schema: `emit_schema` 出力が `schema/current.json` と byte-equal。
- 実データ: P000 13 セッションに `--sweep` を流し reason 別 HIR / 閾値 sweep 表を results.md へ。

## ロールバック計画
- 追加は評価経路に限定。問題時は intervention.rs の thresholds/enum 変更を revert（const へ戻す）し、
  eval/CLI の追加分を削除すれば production は元から不変なので影響なし。
