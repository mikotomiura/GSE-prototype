# 引き継ぎ —— 4 つの試験の枝を順に PR してマージする（Mac）

> 作成: 2026-11-10（Mac のセッション）。このメモを一次資料にしない。枝の状態は git で確かめ直す。研究者の選択は `.steering/20261107-gse-structure-deficit-test/tasklist.md` の「結果の後」の最後の行に記録してある。

## 0 入口の文（Mac の Claude Code に打ち込む）

```
.steering/_handoff/next-session-gse-four-experiment-prs.md を読み、4 つの試験の枝を下から順に PR してマージしてください。push・PR・マージの前に、1 本ごとに私に確かめてください。
```

この引き継ぎは `exp/gse-structure-deficit-test` の枝（worktree `/Users/johnd/GSE-prototype-structure-deficit`）にある。

## 1 枝と順（2026-11-10 に `git merge-base --is-ancestor` で確かめた）

積み重なりの順で、PR もこの順に出す。下の枝が上の枝の祖先になっている。

| 順 | 枝 | worktree | origin/main より先 | 未 push |
|---|---|---|---|---|
| 1 | `exp/gse-coauthor-ml-improve` | `/Users/johnd/GSE-prototype-coauthor-ml` | 15 | 0 |
| 2 | `exp/gse-timeseries-tau-extend` | `/Users/johnd/GSE-prototype-tau-extend` | 29 | 0 |
| 3 | `exp/gse-tau-mode-candidate` | `/Users/johnd/GSE-prototype-tau-mode` | 39 | 1（`05a65021`） |
| 4 | `exp/gse-structure-deficit-test` | `/Users/johnd/GSE-prototype-structure-deficit` | 56 | 8 |

- 4 本とも origin/main から 170 コミット遅れた同じ main の上にある。
- 前のセッションの問いでは順を逆（tau-mode が先）に書いた。研究者が選んだのは「下の 3 本を先に 1 本ずつ」なので、上の表の順がそれに当たる。

## 2 1 本ごとの手順

1. 最初に `git fetch origin` を実行する。表の数が変わっていないか、他のセッションがその worktree を触っていないかを確かめる（`git -C <wt> status -s` と `log -3`）。
2. その枝に origin/main を merge する。衝突しそうなのは `.codex/budget.json` だけ（4 本の差分のうち experiments と .steering の外にあるのはこれだけ。structure-deficit で確かめた）。台帳の衝突は、ファイルの中の `_comment_merge_*` の先例に従って和を採り、コメントを 1 つ足す。history は消さない。
3. 前の枝のマージの後は、次の枝に origin/main を取り込み直す。下の枝が squash でマージされると、上の枝に同じ内容の別コミットが残るので、マージは merge コミットか rebase で行う（squash にしない）。どれにするかは最初の PR の前に研究者に確かめる。
4. docs と実験の記録だけなので、`[skip ci]` で CI を起動させない（memory: feedback-push-only-no-pr-during-runs）。
5. push と PR の作成とマージは、1 本ずつ研究者に確かめてから行う。
6. `results/summary.json` が大きい（tau-mode 約 8.9 MB・structure-deficit と tau-extend 約 4.3 MB）。前の試験と同じくコミット済みのものなので足し引きはしない。ただし GitHub の 100 MB の制限には遠い。

## 3 PR の本文に入れること

- 各試験の notes の「言えること・言えないこと」を 3〜5 行で写す（新しい読みを足さない）。
- 結果を段 1 の候補の採否や ADR-047 の根拠にしないこと。
- structure-deficit-test は判断 13〜15 でレビューを 2 巡通したこと（Codex を含む）。

## 4 守ること

- pkl・holdout・書き手ごとの記録を開かない。PR の本文に書き手・セッション・課題の番号を書かない。
- notes・tables・条件は変えない（merge の衝突があっても内容は変えない）。
- 返答・問いは日本語で。決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて。
