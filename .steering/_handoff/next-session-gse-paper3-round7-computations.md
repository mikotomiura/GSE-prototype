# 引き継ぎ —— 論文 3 の round 7 の計算 A・B（条件 → コード → HP Z2）と round 8

> 作成: 2026-11-20（Mac のセッション）。このメモを一次資料にしない。採否は `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 37、指摘は `.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-7/verdict.md`（Y1・Y5）。

## 0 入口の文

```
worktree /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning）で、.steering/_handoff/next-session-gse-paper3-round7-computations.md を読んで、論文 3 の round 7 の計算 A（入れ替えの対照）と B（先頭の記号を除いた残り）の条件とコードを書き、HP Z2 の引き継ぎを作ってください。
```

## 1 今の状態
- 本文（main.tex）は round 7 の書き方の直し 1〜13 と C（EM の要約・限界の 1 句）を入れた版。A と B の値は `\PENDING{A: ...}`（序論・4.4 の対照の段・決定の段・結論の 4 か所）と `\PENDING{B: ...}`（3.4 の採点の文）で置いてある。本文 7,770 語（round 7 の版 7,502）・要旨 248 語・19 頁。round 8 の前に削る（outline.md 末尾）。
- context-B の限界の「重ならない窓では利得は 2 桁落ちない」は古い（監査役 3-2）。round 8 で直す。

## 2 やること
1. 条件を先に書いてコミットする（reproducibility-discipline・置き場は `experiments/20261112-selection-split-and-smoothing/` の conditions.md に追記するか新しい dir。既存の sym.py・ctrl.py を読んでから決める）。
   - A 入れ替えの対照: α = 0.03・構造 ar3・対称 2 段で書き手 w に選ばれた τ（sym_picks・保存済みの値から決まる）で、w の事前（0.03 × 基 + τ S̄_{-w}）を、別の書き手 v の同じ長さの k 単位（k = 5・15）に当てはめ、w の held-out で採点する。本人' − 入れ替え の中央値を出す。決めること: v の選び方（全員の平均か、決めた規則の数人か）、S̄ から v を外すか（外すと共通の当て直しが組ごとに要り重い。外さないなら v のデータが事前に 1/16 程度入ることを断る）、−∞ の扱い、読みの形（結果より前）。設計の判断が要れば研究者に AskUserQuestion で問う。
   - B 先頭の記号を除いた残り: Eval に先頭の位置を外した量を足し（D.M の各系列の 0 番目を外す）、固定の平滑の 2 段の残り（mode の em_writer の再生・CoAuthor は HP Z2 で約 28 分）と対称版（sym.py の再生・約 1.5 時間）の k = 5・15 を出す。乱数の再生で保存済みの全記号の量とビットまで一致することを照らしにする。
   - 門と変異を合成で作り、Mac で selftest を通す。
2. HP Z2 の引き継ぎを書く（下敷き: `next-session-gse-paper3-sym-control-run-on-hp-z2.md`）。入力の pickle と記号は HP Z2 にしかない。
3. 結果が来たら notes → 本文の `\PENDING` を埋める → 数値の照合（Opus・読むだけ）→ 削る → round 8（同じ dir 構成で round-8。Codex の既知の一覧は round 7 の 27 件から直したものを外す）。

## 3 守ること
- `papers/` に GSE の名前・内部のパス・判断の番号を書かない。投稿先や状態を公開物に書かない。
- 実データ・書き手ごとの値は開かない。CoAuthor の記録も値も Codex に送らない。
- push は枝だけ・PR は出さない（[skip ci]）。worktree の `.codex/budget.json` はコミットしない（台帳は本線。11-20 は 7 回・299,859 tokens）。
- round 7 の `tmp/` は attack-me を閉じるまで残す。
