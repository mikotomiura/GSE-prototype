# 20261104-stage1-penalty-synthetic

段 1 の C4 のトラックの罰つきロジスティック（S1-E8）の罰の強さの決め方（固定・時間順の CV・下限で切り替える組み合わせ）を、合成のデータだけで比べる。S1-E8 の罰の強さと S1-E4 の件数の下限に渡す案の値を、計算の前に凍結した規則（conditions C4）で出す。

- 条件: `conditions.md`（計算の前にコミット）・SEED: `SEED`
- 再現: `bash run.sh`（selftest → 変異 → 本計算 → report → provenance。Mac で約 10 分）
- 結果: `results/summary.json`・`results/proposal.json`・`results/tables.md`（反復ごとの値は `results/raw/`・git に入れない）
- 記録: `notes.md`・作業記録は `.steering/20261104-stage1-penalty-synthetic/`
- 仮説・事前登録: `docs/preregistration-stage1.md` S1-E8・S1-E4（草案の値の案。仮説の検証ではない）
- 借用: 当てはめは `experiments/20261104-coauthor-ml-improve/scripts/logit.py` の写し。1-SE 規則の出典は notes で登録する
