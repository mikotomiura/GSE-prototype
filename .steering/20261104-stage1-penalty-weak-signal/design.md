# 設計

## アプローチ

前の実験の `sim.py` を外側から読み込む `weak.py` を書き、`sim.BETA` を倍率つきで置いてから前の `calib_a`・`one_rep` を呼ぶ。集計は前の `report.py` の `per_choice`・`combo_choice` を使う `report_weak.py`。条件は `experiments/20261104-stage1-penalty-weak-signal/conditions.md`（W0〜W4）。

## 変更対象

- 新規: `experiments/20261104-stage1-penalty-weak-signal/`（README・conditions・SEED・env・run.sh・mutate.sh・scripts/weak.py・selftest_weak.py・report_weak.py・check_mutations.py・results/・notes.md）
- 前の実験のファイルは変えない。

## テスト戦略

- 計算の前: W1（1 倍が前の one_rep と一致）・W2（倍率が C に効く）・変異 w1・w2 が名指しの門で赤。
- 計算の後: W4（1 倍の 36 セルが前の summary.json と一致）で、Pool の経路まで含めて外側の層が値を変えていないことを確かめる。
- 3 反復の配管の通し（scratchpad・W4 は反復の数が違うので FAIL が正しい）。規則の答えの欄は見ていない。
- 完了時に code-reviewer ＋ /cross-review（Codex には条件・コード・集計値だけ）。
