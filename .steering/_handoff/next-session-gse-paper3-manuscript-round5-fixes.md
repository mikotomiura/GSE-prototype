# 引き継ぎ —— 論文 3 の本文の manuscript round 6 を回す

> 作成: 2026-11-19（Mac のセッション）。このメモを一次資料にしない。round 5 の採否は `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 32、直しの実施は判断 33（commit e6fdad49）。

## 0 入口の文

```
worktree /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning）で、.steering/_handoff/next-session-gse-paper3-manuscript-round5-fixes.md を読んで、論文 3 の本文の manuscript round 6 を回してください。
```

## 1 今の状態
- 対象は e6fdad49 の main.tex（本文 7,219 語・要旨 248 語・18 頁・警告 0）。round 5 の直し（判断 32 の A〜E・書き方の直し 1〜11）は入れ、数値はサブエージェントで照合済み（不一致 0・言い方の注意 3 件を直した）。点検は `.steering/20261107-gse-paper3-per-person-learning/paper-write/rewording-check-r5.md`。
- 判定の推移は major ×5（round 5 は R1 major・R2 minor・R3 minor・E 直してから回す・Codex major）。round 5 の記録は `.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-5/`。

## 2 やること
1. 本線（origin/main）の attack-me で round 6 を回す。round 5 の dir（brief・carryover・context・panel）を土台に round-6 を作る。carryover には round 5 の指摘と判断 32・33 の対応・使わなかった直しを書く（他の役の指摘は渡さない）。context-A の測った値は e6fdad49 で測り直す（本文 7,219 語）。規程は Chrome で照合し直す（curl は拒否される）。
2. Codex には既知の未決（round 5 の codex-input の 1〜25。25 は直したので外す）に、判断 32 の保留（中央値を本文に出さない・3〜7e-3 を要旨に残す・τ の値は「格子の中」までしか出さない）を足して添える。
3. 判定と直す順を出し、研究者に AskUserQuestion で問う。round 7 を回すかは推移を数えてから（manuscript で minor なら直して投稿へ進むことを推奨）。

## 3 守ること
- `papers/` に GSE の名前・内部のパス・ADR や判断の番号を書かない。投稿先や状態を公開物に書かない（outline.md の Target の行は公開のアーカイブを作るときに外す・判断 32）。
- 実データ・書き手ごとの値は開かない。CoAuthor・CS1 の記録も値も Codex に送らない。
- push は枝だけ・PR は出さない（[skip ci]）。返答は日本語。worktree の `.codex/budget.json` はコミットしない（台帳は本線のチェックアウト。11-19 は 3 回・127,324 tokens）。
- round 5 の `tmp/` は attack-me を閉じるまで残す。
