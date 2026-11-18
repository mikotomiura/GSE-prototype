# 引き継ぎ —— 論文 3 の本文の attack-me round 4（stage manuscript）

> 作成: 2026-11-19（Mac のセッション）。このメモを一次資料にしない。採否は `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 27〜29。

## 0 入口の文

```
worktree /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning）で、.steering/_handoff/next-session-gse-paper3-manuscript-round4.md を読んで、論文 3 の本文の attack-me round 4（stage manuscript・対象 d6587f21）を回してください。
```

## 1 今の状態

- round 3 の直し（判断 27）を入れた版が d6587f21。本文 6,939 語・要旨 250 語・図表 6（図 3・表 3）・17 頁・警告 0。数値は独立に照合した（判断 28）。
- 判定の推移 major → major → major。round 3 の重い指摘は書き方で、R1・R3 は「直せば minor の見込み」。
- 主な変更: 要旨と結論で 5e-4（固定の平滑・帰無で同程度・post hoc）と 7e-3（合成で確かめていない）を分けた／残り ÷ 平滑の利得の比（帰無 0.6〜1.0・実データ 0.55〜0.97）／節の順を 4.4 平滑の確かめ → 4.5 帰無に／方法の冒頭に作った数の例の図（図 1）／語の統一（own chain・gain・remainder・base smoothing・held-out units・writer。構造の略号は「3-state AR-HMM」などの語に）／推奨を「使ったもの (1)(2)」と「必要だが満たせなかったもの (3)(4)」に／結論を決定と重ならない窓での逆転に絞った。
- 補足資料 S1〜S16 は未作成。round 3 で本文から移した文は `papers/per-person-learning/manuscript/outline.md` の末尾。

## 2 やること

1. attack-me を本線の版の手順で読む: `git -C /Users/johnd/GSE-prototype show origin/main:.claude/skills/attack-me/SKILL.md`（worktree の写しは古い）。paper-write も同じく本線の版。
2. round 3 の dir（`.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-3/`）の context-A・context-B・brief・carryover を土台に round-4 を作る。carryover には round 3 の指摘（verdict §2〜§4）と、判断 27・28 の直し・言い換えの点検（`paper-write/rewording-check-r3.md`）を渡す。
3. Codex を加える（memory「attack-me と /cross-review は毎回 Codex を加える」）。既知の未決の一覧を添え、判定に数えないよう頼む（memory「Codex には既知の未決を渡す」）。予算は本線の台帳（`/Users/johnd/GSE-prototype/.codex/budget.json`）で読み、wrapper も本線から回す。round 3 は 1 回の上限 30,000 を超えた（41,523）。
4. 指摘を一次で裏取りし、verdict を書き、判定の推移を数えてから Step 5 で研究者に問う（memory「attack-me は判定の推移を見てから回す」）。

## 3 既知の未決（round 4 でも判定に数えない）

round 3 の context-A の 1〜9 と同じ。ただし 9 のうち「方法の細部を補足へ」は一部済み（同点・格子の値）。ほかに、閾が 5 種の最大であることの不確かさは本文に 1 句を入れた（3.6・限界）。

## 4 守ること

- `papers/` に GSE の名前・内部のパス・ADR や判断や条件の番号を書かない。投稿先や状態を公開物に書かない。
- 実データ・書き手ごとの値・m0 の npz は開かない。CoAuthor・CS1 の記録も値も外部の LLM（Codex を含む）に送らない。
- push は枝だけにし、PR は出さない（[skip ci]）。返答は日本語。
