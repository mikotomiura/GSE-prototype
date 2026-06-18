# 重要な設計判断

## D1: 診断 (--nudge-diag) は ACT を reason×GT で層別し特徴量 min/median/max を出す

- **判断**: FP/TP 分離可能性を見るため、ACT decision の決定時特徴量 (p_stuck/f3/f4/f6/idle_ms) を
  (reason × {Protect/Stall/Unlabeled}) 群で集計し min/median/max を pooled 出力。production 不変
  (既定 thresholds で decide を再実行し読むだけ)。
- **根拠**: 生の per-decision dump より群サマリの方が「分離カットがあるか」を直接読める。content を
  含まず集計数値のみ → privacy 安全。
- **結論**: 中心質量は全特徴で重なる。FP 低裾 (f4<2.38 / f6<0.37) のみが TP と非重複。

## D2: 抑制レバーは「スコア減点」ではなく「hard veto」

- **判断**: correction_after_pause の FP を落とすには `+0.15` 加点の除去では不十分
  (medium pause の素点 +0.35 が既に nudge 閾値 0.35 を満たす)。よって
  `f4<floor OR f6<floor` の **hard veto** (candidate を defer に落とす) を採用。
- **根拠**: 診断で FP の idle は medium 帯 (≈24s) に集中 → スコア減点では閾値を割らない。

## D3: veto は injectable (既定 None) で production 不変、採用は別ステップ

- **判断**: `InterventionThresholds.correction_f4_floor / correction_f6_floor: Option<f64>` を追加し
  `Default = None`。`decide()` の veto は None 時 `is_some_and` が false で candidate 不変。
- **保証**: snapshot byte-equal / schema drift なし / `correction_floor_default_off_keeps_nudge` テスト。
- **不変条件**: veto は `record_activation` の**前**に置く (defer に落とした nudge が cooldown/cap を
  誤消費しないため)。コードにコメントで固定。
- **採用 (production 変更) は別ステップ**: floor を既定へ入れる = 挙動変更 → policy/HMM_VERSION +
  golden 再生成 + 本 decisions 追記が必要。本タスクは counterfactual 試算まで。

## D4: counterfactual 結果 — f4≥2.38 が Pareto 最適

- f4≥2.38: FP 22→13 (9 件除去)、**TP 12 維持・recall 不変**、HIR 0.647→0.520、burden -26%。
- f6≥0.37 / both: TP を 1 件失う (診断の TP f6 下限 0.37 は丸め値で実値がわずかに下回る TP が 1 件)。
  → f4 単独に劣後。
- **過学習留保 (重要)**: floor 2.38 は P000 の TP 最小値そのもので **in-sample。「TP ゼロコスト」は
  構成上ほぼ恒真**。holdout / 別被験者で再検証するまで production 既定にしない。CLI 出力にも警告を明記。

## D5 (負債メモ): pooling の重複

- `pool_correction_floor_row` の HIR/precision/recall/dc/burden 算出は `compute_intervention_sweep` の
  プールロジックと式重複。3 つ目の pooled レポートが出たら `confusion_rates(&BinaryConfusion) ->
  (hir, precision, recall)` ヘルパへ切り出す (code-reviewer LOW、現状スコープ外として記録)。
