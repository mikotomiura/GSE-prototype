# 引き継ぎ —— 論文 3 の本文に manuscript round 5 の直しを入れ、round 6 を回す

> 作成: 2026-11-19（Mac のセッション）。このメモを一次資料にしない。採否は `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 32、指摘と直す順は `.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-5/verdict.md`（commit 50404c7b）。

## 0 入口の文

```
worktree /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning）で、.steering/_handoff/next-session-gse-paper3-manuscript-round5-fixes.md を読んで、論文 3 の本文に round 5 の直しを入れてから round 6 を回してください。
```

## 1 今の状態
- 対象は cc30d57f の main.tex（本文 7,013 語・要旨 250 語・17 頁）。round 5 の判定は major（R1 major・R2 minor・R3 minor・E 直してから回す・Codex major）。推移 major ×5。
- 研究者の選択は判断 32（A〜E・書き方の直し 1〜11 を全部・直した後に round 6・outline.md の Target の行は公開のときに外す）。

## 2 やること
1. 判断 32 の E: 推奨 (2) の版（両側の当て直し・α = 0.03・3-state AR-HMM・15-session）で選ばれた τ を保存済みの集計から引く。置き場の候補は `experiments/20261112-selection-split-and-smoothing/results/`（notes.md 65 行は「7 つの k すべてで 17 人とも格子の中・τ = ∞ は 0 人」まで）。重みは中央値の学習記号数で N/(N+τ)。値が無ければ限界にその旨を書く（新しい計算はしない）。
2. 判断 32 の A〜D と verdict §5 の 1〜11 を本文に入れる。足す文には同じ節で削る箇所を添える（paper-write Step 4）。要旨は 250 語以下を保つ。
3. 言い換えの点検（paper-write Step 3b）を `paper-write/rewording-check-r5.md` に。数値はサブエージェント（Opus・読むだけ）で集計の記録と独立に照合する（判断 31 と同じやり方）。
4. 語数を測り `paper-write/length-log.md` に 1 行。判断 33 として記録し、コミット・枝に push（[skip ci]）。
5. round 6 を本線の attack-me で回す（round 5 の dir を土台に・carryover に round 5 の指摘と判断 32 の対応を書く）。Codex には既知の未決（round 5 の codex-input の 1〜25）に判断 32 の保留を足して添える（25 は直したら外す）。

## 3 守ること
- `papers/` に GSE の名前・内部のパス・ADR や判断の番号を書かない。投稿先や状態を公開物に書かない（outline.md の Target の行は公開のアーカイブを作るときに外す）。
- 実データ・書き手ごとの値は開かない。CoAuthor・CS1 の記録も値も Codex に送らない。
- push は枝だけ・PR は出さない（[skip ci]）。返答は日本語。worktree の `.codex/budget.json` はコミットしない（台帳は本線のチェックアウト。11-19 は 3 回・127,324 tokens）。
- round 5 の `tmp/` は attack-me を閉じるまで残す。
