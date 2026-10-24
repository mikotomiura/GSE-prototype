# 次のセッション（Mac）: 照合の論文 —— 結果を開いて §7 を書く（A4 以外から）

作成 2026-10-24（判断 78 の後）。この機械は Mac。G-GEAR では `main_a4.json` の段が続けて走っている。G-GEAR の作業はこのセッションでしない。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-manuscript-results.md を読んで、照合の論文の結果を A4 以外から書いて。
```

## 今の状態

- 500 人の本計算と探索的な分析 3〜5 が終わった。commit 7a515f81（ブランチ `docs/public-keystroke-matching-freeze`）に `experiments/20261012-public-keystroke-matching/results/` の `main.json`・`exploratory_tail.json`・`exploratory_margin.json`・`exploratory_score_band.json` がある。実行の記録は同じ commit の `notes.md`。
- この commit は原稿の枝（`docs/public-keystroke-matching-manuscript`）に merge 済み（d3b7df70）。原稿の worktree でそのまま読める。
- 結果の前の組み直し（paper-write の Step 0〜5）は済んだ（判断 78）。記録は `.steering/20261020-public-keystroke-matching-manuscript/paper-write/`（venue-fit.md・split-plan.md・length-log.md）。結果の節（results.tex）には柱ごとの角括弧の計画があり、R5/R6 の定義と結果の表の場所は付録 E（appendix-results.tex）にある。
- 頁は、結果を入れた見込みで約 12.95 頁。上限 12 頁を約 1 頁超える。残りの 1 頁は結果を見てから詰める（判断 78 の追記）。候補は length-log.md の「足りない約 1 頁の候補」。
- 研究者の決定（2026-10-24）: 結果の執筆は、このセッションとは別の新しいセッションで、`main.json` から始める。A4 の行は角括弧のまま残し、`main_a4.json` が届いたら埋める。A4 は脅威モデルの外の参考で、いちばん強い攻撃者の最大値に入らないので、先に書いた結論は A4 の結果で変わらない。

## 何をするか

結果が出た後の手順は `.steering/_handoff/next-session-public-keystroke-matching-manuscript-after-attack-me.md` の「結果が出たら」と「草稿の完成」の 6 項目に従う。今回はその最初の段で、届いた分だけを書く。

1. 結果を開く前に、§6.7 の LaTeX のコメント（結果を開く前に手順を固定したかの確認）を、G-GEAR の記録（notes.md）で確かめる。探索的な分析の手順は付録 D（appendix-exploratory.tex）に移してある。
2. `main.json` を開き、§7 を A0〜A3 から書く。予測（判断 65）を結果と並べる。ENJA15 の短い小節は `enja15_main.json` が届いているかを確かめてから（無ければ角括弧のまま）。
3. 探索的な分析 3〜5 の表を付録に入れる。1・2（`exploratory_unicity.json`・`exploratory_dp.json`）は届いているかを確かめ、無ければ角括弧のまま。
4. 結果を書いた後に、§1 の方法・害・貢献の段落、§8.3 持ち帰り、§9 結論、抄録を書く（区間は正答率だけ）。outline.md の Claim and contributions の強さ（実測で確立 / 条件つき / 可能性）をここで決める。
5. 頁を測り直し（length-log.md の数え方）、約 1 頁を詰める。候補のうち手順の記述を本文から外すものは、移す前に AskUserQuestion で聞く。
6. ビルド（エラー 0・未定義 0）と文体の門（違反 0）を通し、commit・push する。

書くときは `paper-write` Skill（`/Users/johnd/GSE-wt-paper-write-skill/.claude/skills/paper-write/SKILL.md`）の Step 3 の後半（何が分かったか・なぜ効くか）と Step 6 に従う。詰まった所は `/Users/johnd/GSE-wt-paper-write-skill/.steering/20261024-paper-write-skill/field-trial.md`（ブランチ `chore/paper-write-skill`）の「試し 1」の続きに書く。Skill はまだ直さない。

## 守ること

- 脅威モデル・攻撃者・手順は凍結した事前登録から変えない。変えるときは notes.md の「逸脱」に書く。
- A4 の復元の中身・キャッシュを開かない。打鍵の記録・本文を外部 LLM（Codex を含む）に送らない。
- 引用は citation-ssot（[V299]–[V325] は別の枝が使う。今は [V329] まで使った）。`narayanan2008robust` は中央の書誌に未登録。公開する原稿に内部の番号・GSE を書かない。
- 外部のサービス（OpenAlex など）に研究者のメールアドレスを付けない（判断 78 に記録した誤り）。
- 応答は日本語。絵文字・★・⚠️ を多用しない。決めてほしいことは推奨と理由を添えて AskUserQuestion で聞く。
- worktree で作業し、コミット前に `git branch --show-current`。`git add -A` を使わない。push だけで止める。G-GEAR で `main_a4.json` を計算している間は PR を出さない。
- attack-me round 3 と下書き 4（Dr. Tian）は草稿の完成の後。
