# 引き継ぎ 1 / 3 —— 段 1 のロジスティックの罰の強さの決め方（S1-E8）を合成で詰める

> 作成: 2026-11-04（Mac のセッション）。このメモを一次資料にしない。順番は `next-session-gse-after-coauthor-ml-improve.md` §2（1 → 2 → 3）。前提の結果は `experiments/20261104-coauthor-ml-improve/notes.md`、事前登録の草案は `docs/preregistration-stage1.md` の S1-E8（「罰の強さ ＝（未定）」）。

## 0 入口の文（Mac の Claude Code に打ち込む）

```
.steering/_handoff/next-session-gse-stage1-penalty-choice.md を読み、段 1 のロジスティックの罰の強さの決め方を合成のデータで詰めてください。/start-task から始め、寄せる先は grill で私に聞いてください。
```

## 1 なぜこれを先にするか

- 段 1 で使うモデルの候補は S1-E8 の 2 つ（固定 baseline の再較正・表の特徴の罰つきロジスティック）だけで、罰の強さが空欄のまま。CoAuthor と CS1 の試験で分かった「1 人あたりのラベルが少ないと、本人の時間順の CV では λ が雑音で決まる」（合成の P-LAM で 1 単位 3 問だと 17 人中 9 人が 0.1 を選んだ・30 問では選べた・判断 10）は、手法の性質として段 1 にそのまま効く。
- 代理ラベルの見分けの結果（C の値）は使わない。使うのは選び方の性質だけ（notes の「読まないこと」）。

## 2 先に決めること（研究者・grill で 1 問ずつ・推奨と理由を添えて）

⚠️ 段 1 は 1 人ずつの確認で、ADR-046 D3 は人をまたぐ partial pooling を段 1 では使わないとしている。CoAuthor と CS1 の試験の λ = ∞（他の書き手で学んだ共通の係数に本人の切片）は、そのままでは段 1 に持ち込めない。

1. 寄せる先: (a) 0（ふつうの ridge）／(b) 固定 baseline（HMM 0.5.0・ADR-044）から作る係数／(c) 公開データ（CoAuthor・CS1）で学んだ係数（領域の移しの前提を名乗る必要がある）。推奨を出す前に ADR-044・ADR-046 D3・S1-E8 の本文を読む。
2. 罰の強さの決め方の候補: 事前に固定する／本人の時間順の CV で選ぶ（ラベルが下限以上の人だけ）／2 つを組み合わせる（下限未満は固定）。
3. 合成で動かす 1 人あたりのラベルの数の格子（段 1 の「約 50」・ADR-042 D5 を含む範囲。例 10・20・30・50・80・120）と、陽性の率（段 1 の探索で測る値が無いので幅で置く）。

## 3 進め方の骨格（/start-task → requirement → design → 条件のコミット → 計算 → notes）

- 合成だけ。O1 と段 1 の記録は使わない（O1 の 11-01 08:30 以降の記録を開かない）。
- 下敷き: `experiments/20261104-coauthor-ml-improve/scripts/logit.py`（罰つきの Newton 法・λ = ∞）と `selftest.py` の P-LAM の作り（書き手 17 人・特徴 5 つ・β の違いの有無の 2 条件）。段 1 の形（1 人・日のブロック・時間順の holdout・ADR-042 D1・D4）に合わせて作り直す。
- 量の候補: 選ばれる λ の分布、評価の時間順の holdout での対数損失と C の、選んだ λ と固定の λ の差。β が本人で違う条件と違わない条件の両方で（P-LAM と同じ形の陽性・陰性の対照）。
- 条件（`experiments/<日付>-stage1-penalty-synthetic/conditions.md`）を計算の前にコミットし、陽性対照と変異を付ける（reproducibility-discipline）。
- 出すもの: notes と、S1-E8 の「罰の強さ」と S1-E4 の下限に渡す案の文（値は研究者が決める・草案の本文は書き換えずに案として並べる）。

## 4 場面ごとの道具

- 設計の判断 → grill（AskUserQuestion・1 問ずつ）・必要なら /reimagine
- 実験 → reproducibility-discipline
- コード → 計算の前に code-reviewer、完了時に code-reviewer と /cross-review（Codex には条件・コード・集計値だけ）
- 外部の文献に新しく依拠するなら citation-ssot

## 5 枝

- `exp/gse-coauthor-ml-improve` の PR が main に入った後なら main から切る。入る前なら、その枝から worktree を切る（logit.py と P-LAM を使うため）。どちらにするかは始める時に研究者に聞く。
