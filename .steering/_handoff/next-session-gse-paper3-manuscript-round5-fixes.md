# 引き継ぎ —— 論文 3 の round 6 の直し（計算 2 つと書き方 1〜12）と round 7

> 作成: 2026-11-19（Mac のセッション）。このメモを一次資料にしない。round 6 の採否は `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 34。指摘と対応の案は `.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-6/verdict.md` §5（commit 60cceb90）。

## 0 入口の文

```
worktree /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning）で、.steering/_handoff/next-session-gse-paper3-manuscript-round5-fixes.md を読んで、論文 3 の round 6 の直し（判断 34）を入れ、round 7 を回してください。
```

## 1 今の状態
- 本文は e6fdad49 の main.tex（本文 7,219 語・要旨 248 語・18 頁）。round 6 の判定は major（R1 minor・R2 major・R3 minor・E 直してから回す・Codex major）。推移 major ×6。
- 研究者は判断 34 で A〜F・直し 1〜12・round 7 を回す、をすべて推奨案で選んだ。

## 2 やること
1. 計算（reproducibility-discipline に従う。条件を先にコミット・書き手ごとの値は開かない・集計の中央値だけを出す）:
   - A: 15-session の「最頻値 − 共通（α = 0.03）」の held-out の差の中央値（k は両側の当て直しと同じ列）。最頻値は基底の平滑を外した共通の数え上げなので α に依らない。置き場は `experiments/20261112-selection-split-and-smoothing/` の続きか新しい実験 dir（既存の run_sym.sh と scripts を読んでから決める）。
   - C: 両側の当て直し（α = 0.03・構造 3-state AR-HMM 固定）を、選ばれた τ を記録するように回し直し、k = 5・15 の τ と重み（訓練の記号の中央値で換算）の中央値を出す。前回は約 1.5 時間（results/sym_timing.json）。既存の残りの値が再現することも確かめる。
2. 本文の直し: 判断 34 の A〜F（A・C は計算の値で書く）と verdict §5 の書き方の直し 1〜12。足す文には同じ節で削る箇所を添え、細部は補足へ移す（outline.md 末尾に記録）。直した後に言い換えの点検（paper-write Step 3b・rewording-check-r6.md）と、数値のサブエージェントの照合（Opus・読むだけ）。
3. round 7: 本線（origin/main）の attack-me で、round 6 の dir を土台に作る（carryover は round 6 の指摘と判断 34 の対応・他の役の指摘は渡さない・context-A は直した版で測り直す・規程は Chrome で照合）。Codex には round 6 の codex-input の一覧（26 件）から直したもの（τ の範囲までの保留・要旨の 3〜7e-3 の保留）を外し、新しい保留を足す。判定と直す順を出し、研究者に AskUserQuestion で問う。manuscript で minor なら直して投稿へ進むことを推奨（attack-me Step 5）。
- 応答の取り出し: 査読者役は SubagentHandback で返すので、トランスクリプトの最後の text ではなく Handback の tool_use の入力から取り出す（round 6 で最初の取り出しが空になった）。

## 3 守ること
- `papers/` に GSE の名前・内部のパス・ADR や判断の番号を書かない。投稿先や状態を公開物に書かない。
- 実データ・書き手ごとの値は開かない（計算は集計値だけを印字する）。CoAuthor・CS1 の記録も値も Codex に送らない。
- push は枝だけ・PR は出さない（[skip ci]）。返答は日本語。worktree の `.codex/budget.json` はコミットしない（台帳は本線のチェックアウト。11-19 は 4 回・170,835 tokens）。
- round 5・6 の `tmp/` は attack-me を閉じるまで残す。
