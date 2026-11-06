# 引き継ぎ —— τ の 3 本の枝を main に入れ、論文 3 を始める（Mac）

> 作成: 2026-11-07（Mac）。このメモを一次資料にしない。結果と読みは `experiments/20261106-tau-mode-candidate/notes.md`、判断は `.steering/20261106-gse-tau-mode-candidate/decisions.md`（判断 1〜12）。研究者が 2026-11-07 に「PR を済ませて論文 3」を選んだ。

## 0 入口の文（Mac の Claude Code に打ち込む）

```
.steering/_handoff/next-session-gse-tau-trio-pr-then-paper3.md を読み、τ の 3 本の枝を main に入れる順番を確かめてから PR を出し、その後で論文 3 を別の worktree で始めてください。push・PR・マージは私が確かめてから。
```

worktree は `/Users/johnd/GSE-prototype-tau-mode`（枝 `exp/gse-tau-mode-candidate`）。

## 1 枝の関係（2026-11-07 に `git fetch` の後で数えた）

- `exp/gse-coauthor-ml-improve` ⊂ `exp/gse-timeseries-tau-extend` ⊂ `exp/gse-tau-mode-candidate`（一直線）。
- main より先: 15 / 29 / 34 コミット。3 本とも main から 61 コミット遅れている。開いている PR は無い。
- `exp/gse-tau-mode-candidate` には未 push のコミットが 2 つある（`fe60aea6`・`9efa5b0e`・notes と判断 12）。
- 作業ツリーの `.codex/budget.json` は 11-06 の Codex の実行で変わっている（未コミット）。枝の差分にも `.codex/budget.json` が入っている（8 行足し・3 行消し）。

## 2 PR（研究者に確かめながら）

1. 順番を AskUserQuestion で研究者に聞く。推奨は「3 本を 1 つの PR にまとめる」か「下から 3 本を順に入れる」の二択で、推奨と理由を添える（3 本は一直線で、上だけ出すと下の 2 本も入る）。
2. main を取り込む（rebase か merge かも研究者に聞く。rebase は研究者の `!` で）。61 コミット分の衝突、特に `.codex/budget.json`・`docs/references.md`・`.steering/_handoff/` を見る。`.codex/budget.json` は main の値を正とし、枝の変更を落とすかを研究者に確かめる。
3. docs と experiments だけの PR なので `[skip ci]`（memory: push だけで止め、PR は確かめてから）。G-GEAR は 11 月ふさがり。
4. マージの後、3 本の worktree を片づけるかを研究者に聞く。

## 3 論文 3（1 人ごとの学習の効き）

- 別の worktree・別のセッションで始めてよい（PR の後なら main から切る）。`paper-write` Skill の Step 0〜1 から。誰に読ませて何を変えるかを先に研究者に聞いて、投稿先はそれから選ぶ。無料の道を既定にする。
- 材料: 前の 2 つの試験（`20261103-coauthor-per-person/`・`20261104-coauthor-ml-improve/`）、τ の 2 つの試験（`20261104-timeseries-tau-extend/`・`20261106-tau-mode-candidate/`）。
- 限界の節の書き換え案は、`20261106-tau-mode-candidate/notes.md` の「論文 3 へのつなぎ」にある。対象は CoAuthor の ar で、選ばれた τ が 10^5 以上の行に限る。中央値で比べた読みであって、書き手ごとの配分ではない。CS1 は但し書きを残す。主の表は変えず、a・b の表は補足資料に置く。
- 公開 repo は GSE-prototype とは別にする。入れるのは集計値と合成の検査だけで、書き手ごとの値・CoAuthor と CS1 の記録・npz は入れない。README は図と日本語版つき。
- 公開データの知見の論文（`/Users/johnd/GSE-prototype/.steering/_handoff/next-session-gse-public-data-findings-paper.md`）とは境を合わせ、そちらでは 1 人ごとの学習を扱わない。

## 4 並行: 仮説を確かめる試験（研究者が 2026-11-07 に決めた）

- 論文 3 が進み始めたら、並行して「構造の族（ar の次数・状態の数）と量子化の列を増やし、前回の読みの仮説（B で本人が勝っていたのは構造の足りなさの補い）を確かめる試験」を回す。
- 論文 3 の範囲は今ある 4 つの試験で凍結する。この試験の結果は論文 3 に入れない。論文 3 では仮説を「同じ向きだが確かめていない」と書き、試験は次の論文か改訂の材料にする。
- 分け方: 条件・コード・合成の門は Mac で、別の worktree・別のセッションで書く（論文 3 のセッションとチェックアウトを共有しない）。条件と SEED はコードより前にコミットし、設計は `/reimagine` で比べる。本計算は職場の PC（HP Z2）で回す。G-GEAR は 11 月ふさがり。
- 前と同じく、書き手ごとの値は repo の外に置いて開かない。段 1 の候補の採否の根拠にしない（ADR-047 D2・D6）。

## 5 守ること

- 書き手ごとの値と共通の母数の npz は開かない（職場の PC の分も Mac に持ち込まない）。repo に出すのは集計値だけ。
- 結果を段 1 の候補の採否や ADR-047 の根拠にしない（D2・D6）。
- 返答・問いは日本語で。決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて。記号を多用しない。
