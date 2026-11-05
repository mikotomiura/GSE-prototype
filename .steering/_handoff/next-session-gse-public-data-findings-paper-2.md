# 引き継ぎ —— 公開データの知見の論文（2）: 主張の確定・事前登録の草案

> 作成: 2026-11-05（Mac のセッション）。このメモを一次資料にしない。決めたことの一次は `.steering/20261105-public-data-findings-paper/decisions.md`（判断 1〜8）、文献は `docs/literature/20261105-public-data-findings-novelty.md`、投稿先は同じ steering の `paper-write/venue-fit.md`。

## 0 入口の文（Mac の Claude Code に打ち込む）

```
/Users/johnd/GSE-prototype-public-findings/.steering/_handoff/next-session-gse-public-data-findings-paper-2.md を読んで、公開データの知見の論文の続きをして。§2 の順で。
```

作業の場所: worktree `/Users/johnd/GSE-prototype-public-findings`・枝 `docs/public-data-findings-paper`（コミットは 1f6fe10b・e11340c2 と、この引き継ぎのコミット。push はまだ）。コミットの前に `git branch --show-current` を見る。

## 1 ここまでに決めたこと（要旨）

- 論文はまず知見 1（打鍵の推定の手前の上がりは、停滞にならない休止と揃えると見えない）で書く。知見 2（停滞の形）を別にするかは、濃くする計算の後で決める（判断 4）。
- 読者は行動ログで状態を推す研究者。変えたいのは評価の設計（判断 5）。
- 濃くする計算は 4 つとも足す: 揃えない比べとの対・同等性の検定・CS1 で手前の上がり・信号と学習器を広げる（判断 6）。回す前に事前登録を OSF で凍結する。
- O1 は使わない。計算は Mac（判断 7）。
- 投稿先は JEDM（判断 8）。次の候補は UMUAI。

## 2 次にやること（順に）

1. paper-write Step 0 の残り: JEDM の最近の論文 3〜5 本の本文の長さ・節の並び・方法の置き方を測る。JEDM のテンプレート（LaTeX）を取り、分量の決まりが無いかを確かめる。結果は `paper-write/venue-fit.md` に追記し、本文の語数の予算を `paper-write/length-log.md` に決める。
2. paper-write Step 1: 主張と新規性の初回案（持ち帰り 1 文・貢献 2〜4 個・強さ・主張しないこと）。新規性の比べは文献カードの [V413]（揃えない比べで 0.726）・[V414]・[V86] を軸にする。
3. /reimagine（判断 2）: 初回案を退避し、requirement.md だけから作り直して比べ、研究者に選んでもらう（AskUserQuestion）。
4. 事前登録の草案: 判断 6 の 4 つの計算。同等性の幅（例 AUC 0.55）・揃えない比べの窓と N 秒・時期や局面での説明の仕方・CS1 の停滞と対照の作り・広げる信号と学習器・取っておいた書き手（KLiCKe 1,498 人・CoAuthor 18 人・CS1 2019 年版 146 人・2021 年版 13 人）を使うかを先に決める。前の条件（各 experiments の `conditions.md`）を土台にする。
5. 事前登録の草案に attack-me（回す前に Codex を加えるかを研究者に聞く・推奨は加える・Codex には既知の未決の一覧を添える）→ OSF で凍結（研究者の手元）→ 計算。

## 3 未決・注意

- `check_citations.py` の違反 1 件（V386〜V412 の欠番）は意図どおり。S-DQ の枝 `docs/gse-daily-item-scale-literature` が使っている。この枝を S-DQ より先に main に入れることになったら、合流の順を研究者に聞く（判断 3）。
- メインが逐語を照合していない文献: [V417]・[V418]・[V420]・[V421]（provisional）。本文で引く前に照合する。
- UMUAI・BRM・IJHCS の規程の文は未照合（Springer と Elsevier は curl が止まるので Chrome で）。
- JEDM の序論では、教育のデータとの結びつきを論じる（CoAuthor は教育でない）。
- 外部の LLM（Codex を含む）に、公開データの書き手ごとの値を送らない。`~/gse-public-data` の書き手ごとの値は人が開かない。repo に出すのは集計値だけ。
- Mac の空きは 19 GB（91% 使用・2026-11-05）。中間を展開するときは空きを確かめる。
- 位置づけの言い方は ADR-047（「詰まる前に」を主張にしない・3 状態の名前を主張に使わない・「作業上の」認知状態）。
- 返答・問い・記録は日本語で。記号を多用しない。push は研究者の手元で。PR は研究者が確かめてから。docs だけの PR は `[skip ci]`。
