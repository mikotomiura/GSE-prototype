# 次のセッション（Mac）: 照合の論文 —— 段 1: `main_a4.json` が届いたら A4 を入れる

作成 2026-10-24（判断 79 の後）。この機械は Mac。G-GEAR の作業はこのセッションでしない。

執筆は届いた結果ごとに段で進める（研究者 2026-10-24）。このセッションは **段 1（A4）だけ**を行う。

| 段 | 届くもの（G-GEAR の計算の順・`run.sh` の data の段） | 書く所 |
|---|---|---|
| 済み | `main.json`・`enja15_main.json`・探索 3〜5 | §7・序論・考察・結論・抄録（判断 79） |
| **1（このセッション）** | `main_a4.json` | 表 2 の A4 の行・§7.4・§7.5・付録 E の KeyTAR |
| 2 | `exploratory_unicity.json`・`exploratory_dp.json` | §7.7 の角括弧・付録 D の表 |
| 3 | `main_all.json`（全員の付録・11 月中旬の見込み） | 付録 E の Results on all writers |
| 完成 | ― | 「草稿の完成」の 6 項目 → attack-me round 3 |

段 2 と段 3 の引き継ぎは、各段を終えたセッションが書く。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-manuscript-a4.md を読んで、照合の論文に A4 の結果を入れて。
```

## 始める条件（揃っていなければ書かずに止まる）

- G-GEAR の `main_a4` の段が終了コード 0 で終わり、`results/main_a4.json` が原稿の枝に merge されている。merge の手順は 7a515f81 と d3b7df70 と同じ（freeze の枝に results の commit → 原稿の枝へ merge）。
- notes.md に、`main_a4` の段の終了時刻と SHA-256 の記録がある。
- **A4 の 499 人の版**（CPU で生成した 1 人を除いた版・逸脱 D3 の約束）が出ている。⚠️ 2026-10-24 に確かめたところ、`run_main.py` と `aggregate.py` には 1 人を除く集計が無い（`reference_rows` は A4 のセルをそのまま返すだけ）。書き手の ID は `raw/derived_a4_cpu_fallback_writers.json`（G-GEAR・git に入らない）にあるので、除いた版は G-GEAR でキャッシュから集計し直すしかない。無ければ、研究者に G-GEAR の作業として頼むかを AskUserQuestion で聞く。Mac で書き手の ID を扱わない。

## やること

1. `main_a4.json` の構造を見る（`main500.reference_A4` に A4 のセル。鍵は `full|<form>|A4|<N>` の形の見込み）。値を開くのはこの段から。
2. `main.json` と `main_a4.json` の A4 以外のセルが一致することを確かめる（notes.md の約束・`json` で全セルを比べ、違いの数を書く）。一致しなければ書かずに止まり、研究者に報告する。
3. `make_tables.py` に A4 の行を作る関数を足す（全体と 499 人の版。表 2 は N = 1,000 と 10、付録 E は全部の N と形）。`python3 -I make_tables.py ../../../experiments/20261012-public-keystroke-matching/results sections/generated`。
4. 角括弧を埋める:
   - `results.tex` の表 2 の 2 行（`A4 on R0 to R3-t`）
   - §7.4 の KeyTAR の文（全体と 499 人の版。KeyTAR は参考であって上限ではない・§5.3 を参照するだけで但し書きを繰り返さない）
   - §7.5 の予測（10 倍の 1/N 未満か）。外れても結論は変えない（登録の文）
   - 付録 E の Results on all writers の段落のうち KeyTAR の部分（全員の付録の角括弧は残す）
5. 書いた数値を集計の値と照らす（判断 79 で書いた後に誤りを 2 つ見つけた）。`verify-before-claiming` を読んでから。
6. 頁を測る（`paper-write/length-log.md` の数え方）。今は 12 頁目の右段 0.85 で終わり、余白は約 8 行。超えたら、判断 79 で選ばなかった候補（§8.2 合意の段落を縮める）を AskUserQuestion で聞く。
7. ビルド（エラー 0・未定義 0）・文体の門（違反 0）・`length-log.md` に 1 行・decisions.md に判断 80・tasklist.md・commit・push。
8. 段 2 の引き継ぎを書く（`exploratory_unicity.json`・`exploratory_dp.json` が届いたら）。

A4 は脅威モデルの外の参考で、最も強い攻撃者に入らない。§7.1〜§7.3 の結論と抄録・序論・結論は A4 の値で変えない。A4 の値が予測と大きく違って文を変えたくなったら、変える前に研究者に聞く。

## 読む物

- `paper-write`（`/Users/johnd/GSE-wt-paper-write-skill/.claude/skills/paper-write/SKILL.md`）と `verify-before-claiming`。書く前に読む。
- 判断 79（`../20261012-public-keystroke-matching-prereg/decisions.md`）・notes.md の D3 と「A4 の実行の記録」。
- 詰まった所は `/Users/johnd/GSE-wt-paper-write-skill/.steering/20261024-paper-write-skill/field-trial.md` の続きに書く。Skill はまだ直さない。

## 守ること

- 脅威モデル・攻撃者・手順は凍結した事前登録から変えない。変えるときは notes.md の「逸脱」に書く。
- A4 の復元の中身・キャッシュを開かない（集計の JSON だけを読む）。打鍵の記録・本文を外部 LLM（Codex を含む）に送らない。
- 引用は citation-ssot（[V299]–[V325] は別の枝。今は [V329] まで）。公開する原稿に内部の番号・GSE を書かない。
- 応答は日本語。決めてほしいことは推奨と理由を添えて AskUserQuestion で聞く。
- worktree で作業し、コミット前に `git branch --show-current`。`git add -A` を使わない。push だけで止める。G-GEAR で計算している間は PR を出さない。

## 別の手続き（研究者）

500 人の結果が出たので、The Learning Agency Lab への通知（`reply-drafts-20261013.md` の下書き 5・「結果が出たらすぐ」）を送る条件は揃っている。送ったら日付と応答を ethics.tex の角括弧に入れる（段とは別に）。
