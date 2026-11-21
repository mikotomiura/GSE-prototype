# 引き継ぎ —— 段 1 の罰の強さ（S1-E8）を決めた後

> 作成: 2026-11-04（Mac のセッション）。このメモを一次資料にしない。結果は `experiments/20261104-stage1-penalty-synthetic/notes.md`・`experiments/20261104-stage1-penalty-weak-signal/notes.md`、判断は `.steering/20261104-stage1-penalty-synthetic/decisions.md`（判断 1〜11）と `.steering/20261104-stage1-penalty-weak-signal/decisions.md`（判断 1〜8）。

## 0 状態

- 枝 `exp/gse-stage1-penalty-synthetic`（worktree `~/GSE-prototype-stage1-penalty`・`exp/gse-coauthor-ml-improve` の b1771098 から切った）。push 済み（fe3f4ef0）。PR は出していない。
- PR は `exp/gse-coauthor-ml-improve`（main に未取り込み・PR なし）が main に入った後に、研究者に確かめてから出す。先に出すと、そちらのコミットが差分に混ざる。
- `docs/preregistration-stage1.md` の S1-E8 に、罰の強さ τ = 0.25（λ = 16・対数尤度の和 − (λ/2)‖β‖²・本人の CV では選ばない）を入れた。最終の値は結果を見た後の選びで、前の実験で凍結した規則の答えと一致する（本文に経緯を書いた）。S1-E3 の決め方に、固定の罰の傾きが信号の強さで動くことの注を足した。
- 事前登録の直しの最後の版（fe3f4ef0）は、2 巡目のレビューにかけていない。

## 1 結果の要点（数字は notes を見る）

- 凍結した規則（前の実験の C4）の答えは τ = 0.25 の固定・CV なし。本人の CV は 10 件では選びが雑音で決まる。
- 弱い信号の確かめ: 傾きが 1 に最も近い τ は、真のモデルの C ≈ 0.72・0.62・0.56 で 0.5・0.25・0.125 と動いた。どの固定の τ も、3 つの強さすべてで傾きを [0.8, 1.25] に入れられない。τ = 0.25 は 3 つの強さを通した最悪で、傾きの外れと後悔の最大が最も小さい。

## 2 次のセッション

研究者が 2026-11-04 に決めた順番（`~/GSE-prototype-coauthor-ml/.steering/_handoff/next-session-gse-after-coauthor-ml-improve.md` §2）では、1（本件）が済んだので、次は 2: 時系列の段の組み方（τ の格子を広げる・共通の構造を先に選ぶ形）。入口は `~/GSE-prototype-coauthor-ml/.steering/_handoff/next-session-gse-timeseries-tau-extend.md` の §0。その後が 3（V-recal の分け・`next-session-gse-vrecal-split.md`）。

## 3 本件から残った問い（順番の外・研究者が決める）

- S1-E3 の較正の切片と傾きの許容の範囲（値は空欄）。日の揺れ（`experiments/20261103-mhd-dryrun-v2/notes.md` §2.3）・罰による縮み・信号の強さで傾きが動くことを並べ、範囲の根拠を予測の使い道（介入の判断を反転させないか・ADR-019 D3）の要件に結び付ける。縮みに合わせて許容を広げると、その分の誤較正を昇格させる（Codex の指摘）。
- S1-E8 の表の特徴の一覧（値は空欄）。確定する前に、語・文の境界のリズム特徴の検討を終えて記録する（ADR-019 D6・ADR-044 D3）。
- 合成の範囲: 信号の強さは 3 点、係数の形と特徴の相関は 1 つ。

## 4 守ること

- 合成だけで決めた。O1 の 11-01 08:30 以降の記録・段 1 の記録・公開データの C の値を使わない。
- Codex には条件・コード・集計値だけを渡す。
- 前の実験の notes・decisions の本文は書き換えず、追記と判断の追加で置き換えを示す。
