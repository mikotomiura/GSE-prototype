# 引き継ぎ —— 論文 3 の本文の manuscript round 5 を回す

> 作成: 2026-11-19（Mac のセッション）。このメモを一次資料にしない。採否は `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 30・31。

## 0 入口の文

```
worktree /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning）で、.steering/_handoff/next-session-gse-paper3-manuscript-round5.md を読んで、論文 3 の本文の manuscript round 5 を回してください。
```

## 1 今の状態
- 対象は cc30d57f（round 4 の直し・判断 30 の A〜C と書き方の直し 1〜11）。本文 7,013 語・要旨 250 語・17 頁。点検は `.steering/20261107-gse-paper3-per-person-learning/paper-write/rewording-check-r4.md`。
- 判定の推移は major ×4。round 4 の記録は `.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-4/`。

## 2 やること
1. 本線（origin/main）の attack-me の手順で round 5 を回す。round 4 の dir（brief・carryover・context）を土台に round-5 を作る。carryover には round 4 の指摘と判断 31 の直し・使わなかった直しを書く。
2. Codex には既知の未決の一覧（round 4 の codex-input の 1〜20）に、判断 30・31 の保留（要旨に逆転を入れない・図 1 の範囲・題・R1 N7・R1 N12・4.4 の二分の「edge」の文）を足して添える。round 4 の Codex は 42,536 tokens で上限 30,000 を超えた。台帳は本線のチェックアウトで読む。
3. 判定と直す順を出し、研究者に AskUserQuestion で問う（推移を数えてから: memory「attack-me は判定の推移を見てから回す」）。

## 3 守ること
- `papers/` に GSE の名前・内部のパス・ADR や判断の番号を書かない。投稿先や状態を公開物に書かない（outline.md 冒頭の Target の行は既存。扱いは研究者に確かめる）。
- 実データ・書き手ごとの値は開かない。CoAuthor・CS1 の記録も値も Codex に送らない。
- push は枝だけ・PR は出さない（[skip ci]）。返答は日本語。worktree の `.codex/budget.json` はコミットしない。
