# 次のセッション（Mac）: 照合の論文 —— A4 と探索的な分析 1・2 の値を入れる

作成 2026-10-24（判断 79 の後）。この機械は Mac。G-GEAR の作業はこのセッションでしない。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-manuscript-a4.md を読んで、照合の論文に A4 の結果を入れて。
```

## 今の状態

- §7（A4 以外）・序論の 3 段落・§8 の冒頭と持ち帰り・結論・抄録を書いた（判断 79・`../20261012-public-keystroke-matching-prereg/decisions.md`）。
- 表の値は `papers/keystroke-log-release-matching/manuscript/make_tables.py` が集計の JSON から `sections/generated/*.tex` に書く。手で写さない。結果を差し替えたら `python3 -I make_tables.py ../../../experiments/20261012-public-keystroke-matching/results sections/generated` を回す。
- 本文は 12 頁目の右段 0.85 で終わる（上限 12 頁・余白は約 8 行）。`paper-write/length-log.md`。
- ビルド: エラー 0・未定義 0・overfull 2。文体の門 違反 0。

## 残っている角括弧（届いたら埋める）

1. `main_a4.json`（G-GEAR で計算中）: 表 2 の A4 の 2 行（`results.tex`）・§7.4 の KeyTAR の文・§7.5 の予測（10 倍の 1/N 未満か）・付録 E の KeyTAR の全行（353 番目の書き手 1 人を含む版と除いた版・逸脱 D3）。`make_tables.py` に A4 の行を作る関数を足す（`main_a4.json` の `reference_A4` の構造をまず見る）。届いたら、`main.json` と `main_a4.json` の A4 以外のセルが一致することを確かめる（notes.md の記録どおり）。
2. `exploratory_unicity.json`・`exploratory_dp.json`: §7.7 の角括弧・付録 D の表。
3. `main_all.json`（全員の付録・11 月中旬の見込み）: 付録 E の「Results on all writers」。待たない。
4. 公開元への通知の日付と応答（ethics.tex）・Open science の匿名リンク: 草稿の完成でも残してよい 3 つのうちの 2 つ。

A4 は脅威モデルの外の参考で、最も強い攻撃者に入らないので、§7.1〜§7.3 の結論は A4 の値で変わらない。A4 の文を足して 12 頁を超えたら、判断 79 で選ばなかった候補（§8.2 合意の段落を縮める）を研究者に聞く。

## その後（草稿の完成から）

`next-session-public-keystroke-matching-manuscript-after-attack-me.md` の「草稿の完成」の 6 項目 → attack-me round 3（編集者の役 E を含む）→ 下書き 5（The Learning Agency Lab への通知・結果が出たらすぐ）を研究者が送る → 下書き 4（Dr. Tian）。

- 下書き 5 は「結果が出たらすぐ」の約束なので、500 人の結果が出た今、送る時期を研究者に確かめる。

## 守ること

- 脅威モデル・攻撃者・手順は凍結した事前登録から変えない。変えるときは notes.md の「逸脱」に書く。
- A4 の復元の中身・キャッシュを開かない。打鍵の記録・本文を外部 LLM（Codex を含む）に送らない。
- 引用は citation-ssot（[V299]–[V325] は別の枝。今は [V329] まで）。公開する原稿に内部の番号・GSE を書かない。
- 書く前に `paper-write`（`/Users/johnd/GSE-wt-paper-write-skill/.claude/skills/paper-write/SKILL.md`）と `verify-before-claiming` を読む。書いた主張の数値は集計の値と照らす（判断 79 で 2 つ誤りを見つけた）。
- 応答は日本語。決めてほしいことは推奨と理由を添えて AskUserQuestion で聞く。
- worktree で作業し、コミット前に `git branch --show-current`。`git add -A` を使わない。push だけで止める。G-GEAR で計算している間は PR を出さない。
