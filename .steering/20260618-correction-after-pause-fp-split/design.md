# 設計 (Step 1: 診断)

## アプローチ

Phase 0 で作った評価器 (`intervention_eval`) に、**ACT decision を (reason × GT) で層別した
特徴量サマリ**を出す診断関数を追加する。production は完全不変 (既定 thresholds で decide を
再実行し、特徴量を読むだけ)。

correction_after_pause の FP 群 (GT=PROTECT) と TP 群 (GT=STALL) で、決定時の
p_stuck / f3 / f4 / f6 / idle_ms の分布が違えば、分離カット (Step 2 の tweak) を設計できる。

## 変更対象

### 修正
- `src-tauri/src/analysis/intervention_eval.rs`:
  - `FeatureStat { count, p_stuck, f3, f4, f6, idle_ms }`（各特徴は `MinMedMax{min,median,max}`）。
  - `NudgeDiagnosticGroup { reason, gt: GtGroup(Protect/Stall/Unlabeled), stat }`。
  - `NudgeDiagnostic { groups: Vec<..>, total_act, warnings }`（reason×gt 固定順で決定的）。
  - `compute_nudge_diagnostic(sessions: &[SweepInput], thresholds) -> NudgeDiagnostic`:
    各 session で decide 再実行 → ACT decision のみ (reason, gt, features) を収集 → pooled で
    群ごとに min/median/max を算出。既存 helper (derive_ranges_from_points / range_class_at /
    binarize_action / idle_ms_at) を再利用。
  - `format_nudge_diagnostic_pretty`。
- `src-tauri/src/bin/replay.rs`:
  - `--nudge-diag` モード（複数 session、`--sweep` と同じ収集経路、既存モードと相互排他、pretty+JSON）。

### 新規ファイル
- なし。

## 既存パターン整合
- `SweepInput` を入力に再利用。pooled・enum 固定順・純粋関数・Result<_,String>(bin層) を踏襲。
- ACT decision の features は decide ループ内の `f`(FeatSnapshot) + `idle_ms_at` から取得。

## テスト戦略
- 単体: FP/TP 群で median が期待通りに分かれる合成データ / ACT 0 件 / 空入力 no-panic。
- 回帰: snapshot byte-equal・schema drift なし・`cargo test --workspace` 緑。

## ロールバック
- 診断は読み取り専用追加。問題時は当該関数 + CLI 分岐を削除すれば production は元から不変。

## Step 2 (結果次第)
- 分離特徴が見つかれば、correction_after_pause の発火条件に追加ゲート (例: p_stuck 下限 /
  idle 帯 / f4 条件) を入れる候補を ≤3 設計し、injectable にして counterfactual で HIR/recall 試算。
  production 変更の採否はユーザー承認後。
