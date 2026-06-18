# タスクリスト

## 準備
- [x] Phase 0 results / カメラ提案 / intervention.rs calculate_opportunity を確認
- [x] ブランチ + steering 作成

## Step 1: 診断 (production 不変)
- [x] `MinMedMax` / `GtGroup` / `NudgeDiagnosticGroup` / `NudgeDiagnostic` 型
- [x] `compute_nudge_diagnostic` (ACT を reason×GT で層別 → 特徴量 min/median/max)
- [x] `format_nudge_diagnostic_pretty`
- [x] `gse-replay --nudge-diag` モード (複数 session / 相互排他 / pretty+JSON / usage、`collect_sweep_inputs` 共通化)
- [x] 単体テスト (分離 / ACT0 / 空入力 / ALL 網羅性ガード)
- [x] `cargo test --workspace` 緑 / snapshot byte-equal / schema drift なし / clippy・fmt 通過

## Step 1 実データ
- [x] P000 13 session で `--nudge-diag` → correction_after_pause の FP vs TP 特徴量分布
- [x] 分離可能性を結論 → results.md (Step1): クリーンな分離無し、f4/f6 低裾のみ TP ゼロコスト候補

## レビュー
- [x] code-reviewer + security-checker 並列 (HIGH/CRITICAL/MEDIUM なし)
- [x] LOW 対応 (group_idx 共通化 / GT coverage 0 warning / ALL 網羅性テスト)

## チェックポイント (ユーザー承認)
- [x] Step 1 の結論提示 → ユーザーが Step 2 (f4/f6 floor 試算) を選択

## Step 2 (実施済み)
- [x] tweak 候補を injectable 化 (InterventionThresholds.correction_f4/f6_floor, 既定 None)
- [x] `--corr-floor` で counterfactual HIR/recall 試算 → **f4≥2.38 が Pareto 最適** (FP 22→13, TP/recall 不変)
- [x] 候補 ≤3 を results.md に提示 + 過学習留保
- [ ] production 採用判断 (要 policy version / golden 再生成) → **ユーザー承認待ち**

## 完了処理
- [x] design/results 最終化 / Step 1 commit (1ce1d6f)
- [ ] Step 2 commit / push / PR (方針確定後)
