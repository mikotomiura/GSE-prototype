# 引き継ぎ —— 論文 3（1 人ごとの学習の効き）を始める（Mac）

> 作成: 2026-11-07（Mac）。このメモを一次資料にしない。研究者が 2026-11-07 に「PR を済ませて論文 3」「仮説の試験は並行・論文 3 の範囲は凍結」を選んだ。PR の段取りは `next-session-gse-tau-trio-pr-then-paper3.md`、並行の試験は `next-session-gse-hypothesis-structure-test.md`。

## 0 入口の文（Mac の Claude Code に打ち込む）

```
.steering/_handoff/next-session-gse-paper3-per-person-learning.md を読み、論文 3（1 人ごとの学習の効き）を paper-write の Step 0〜1 から始めてください。誰に読ませて何を変えるかを先に私に聞いてください。push と PR は私が確かめてから。
```

## 1 始める前に

- τ の 3 本の枝（`exp/gse-coauthor-ml-improve` ⊂ `exp/gse-timeseries-tau-extend` ⊂ `exp/gse-tau-mode-candidate`）が main に入っているかを `git fetch` の後で確かめる。入っていれば main から新しい worktree を切る。入っていなければ研究者に聞く（`exp/gse-tau-mode-candidate` から切るか、PR を待つか）。
- 新しい worktree・新しいセッションで行う。仮説の試験のセッションとチェックアウトを共有しない。コミットの前に `git branch --show-current`。
- `paper-write` Skill（main の `.claude/skills/paper-write/`）を Read してから手を動かす。attack-me・/cross-review には毎回 Codex を加える。

## 2 論文の範囲（凍結）

- 材料は次の 4 つの試験だけにする。仮説の試験（構造の族と量子化の列を増やす）の結果は入れない。
  1. `experiments/20261103-coauthor-per-person/`（B: 本人の EM が共通に勝つ）
  2. `experiments/20261104-coauthor-ml-improve/`（構造をそろえ、2 段の組み方を作る）
  3. `experiments/20261104-timeseries-tau-extend/`（τ の格子を 10^6 と ∞ まで広げる）
  4. `experiments/20261106-tau-mode-candidate/`（大きい τ の差を本人の寄与と、最頻値と共通の違いに分ける）
- 主張の芯（notes に書いた範囲を越えない）: 他人の基準で構造と τ を選ぶ 2 段の組み方では、どこでも ar3 が選ばれ、同じ構造の共通に対する本人の差は CoAuthor で約 1e-3 以下、CS1 で 0。hmm3 では本人の上積みが大きい（CoAuthor で最大 +0.19）。「1 人ごとに学ぶ効きは、構造を良くすると小さい」。
- 仮説（B で本人が勝っていたのは構造の足りなさの補い）は「同じ向きだが確かめていない」と書く（族 2 つ・量子化 1 つ）。
- 限界の節: `20261106-tau-mode-candidate/notes.md` の「論文 3 へのつなぎ」の書き換え案を使う。対象は CoAuthor の ar で、選ばれた τ が 10^5 以上の行に限る。中央値で比べた読みであって、書き手ごとの配分ではない。CS1 は前の但し書きを残す。主の表は変えず、a・b の表は補足資料に置く。
- 読まないこと（4 つの試験の notes にあるもの）を守る: EM の状態に名前を付けない・閾値と検定を置かない・セッションと課題は日ではない・CS1 を日本語や GSE の参加者へ広げない・26 記号の量子化の列を予測できることは作業上の認知状態の構造ではない。

## 3 決めること（AskUserQuestion で 1 問ずつ・推奨と理由を添えて）

1. 誰に読ませて何を変えるか（投稿先はそれから選ぶ・格と通りやすさから並べない）。
2. 投稿先と形式（無料の道を既定にする。購読誌＋プレプリントなど）。
3. 原稿の言語と組版（MacTeX。共著者への相談があれば .docx は pandoc）。

## 4 公開物

- 公開する repo は GSE-prototype とは別の新しい repo にする（研究者の指示）。GSE-prototype は公開しない。
- 入れるのは集計値（各試験の `results/summary.json` 由来の表）と合成の検査だけ。書き手ごとの値・CoAuthor と CS1 の記録・共通の母数の npz は入れない。
- README は図と gif と日本語版つきを既定にする（手本は Affective-Tactility-Works-public）。公開の前に、コミットのメッセージ・派生値・図・作者メールから値が漏れないかを陽性対照つきで確かめる。
- 公開データの知見の論文（`/Users/johnd/GSE-prototype/.steering/_handoff/next-session-gse-public-data-findings-paper.md`）とは境を合わせ、そちらでは 1 人ごとの学習を扱わない。

## 5 守ること

- 書き手ごとの値と npz は開かない。repo に出すのは集計値だけ。
- 結果を段 1 の候補の採否や ADR-047 の根拠にしない（D2・D6）。
- 本文は簡潔にし、細部は補足資料へ。引用は citation-ssot（`docs/references.md` に append-only）。
- 返答・問いは日本語で。記号を多用しない。
