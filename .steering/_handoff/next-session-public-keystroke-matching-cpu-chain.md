# 次のセッション: 公開データでの照合の論文 —— CPU の本計算の一続きを見守る・再開する

作成 2026-10-21（G-GEAR）。前の引き継ぎ `next-session-public-keystroke-matching-after-reboot-3.md` の続き。投稿の目標は PoPETs 2027 Issue 3（締切 2026-11-30 AoE）。

## 新しいセッションで最初に打ち込む文

```
C:\GSE-wt-matching-prereg\.steering\_handoff\next-session-public-keystroke-matching-cpu-chain.md を読んで、CPU の本計算の一続きの様子を確かめて
```

## 今の状態

- worktree `C:\GSE-wt-matching-prereg`・ブランチ `docs/public-keystroke-matching-freeze`。
- A4 は 500/500（D3）。ENJA15 は済み（`results/enja15_main.json`・コミット `578f2cda`）。
- 500 人の本計算は 1 回目が Windows Update の再起動で 19 時間後に止まった。`run_main.py --cache-dir` で再開できるようにした（逸脱 D4・コミット `e7206812`・レビュー済み）。研究者は Windows Update を一時停止した（2026-10-21）。
- 2026-10-21 05:55:08 UTC に `raw/main_chain/run_chain.sh`（git の外）で一続きを始めた（コミット `accfea3f` のコード。04:25 の 1 回目は探索的な分析 3〜5 を足すために止めた）。段の順: main500（`results/main.json` と探索的な分析 3〜5 の `results/exploratory_{tail,margin,score_band}.json`・916 件・約 53 時間）→ explore35（探索のファイルが無いときだけキャッシュから集計し直す）→ main_a4（`main_a4.json`・全件を計算し直す）→ unicity（`exploratory_unicity.json`）→ dp（`exploratory_dp.json`）→ all（`main_all.json`・標本の件を使い回す・約 10 日）。
- 500 人の段は 2026-10-24 06:21:45 UTC に終わった（約 72 時間・1 時間に約 12.6 件）。`main.json` と探索 3〜5 はコミット済み。同じ時刻に main_a4 を始めた（指紋 `628d6e4e756e4b71`・916 件）。いまの速さでの見込み: main_a4 は 10-27 ごろ、R-DP は 11-01 ごろ、全員の付録は 11-16 ごろ（研究者に Windows Update の一時停止を 11-16 より先まで、とお願いした）。

## 様子の見方

- 段の始まりと終わり: `results/.tmp/chain.log`（`start` / `exit <段> <コード>` / `done`）。
- 段ごとのログ: `results/.tmp/chain_<段>.log`（起動時に `cache …: N of M tasks done`）。
- 進み具合: `raw/derived/main_cache/<指紋>/` の `.pkl` の数（main500 は `33fa95833296d7a5`・916 件で終わり。古い `feb23d233506a9d2` は使わない）。中身は読まない。
- プロセス: PowerShell で `run_main` を含む python。

## 止まったとき

- 同じコマンドで再開する: `bash /c/GSE-wt-matching-prereg/experiments/20261012-public-keystroke-matching/raw/main_chain/run_chain.sh >> results/.tmp/chain.log 2>&1`（実験のフォルダで）。出力のある段は飛ばし、終わった件はキャッシュから読む。起動時の `N of M tasks done` の N が `.pkl` の数と合うことを確かめる。
- 再起動が原因なら `notes.md` の「CPU の本計算の実行の記録」に時刻とイベント（System の 1074）を足す。
- 一続きのあいだ `scripts/` の読み込まれるコード（`aggregate.py` は除く）・`config.json`・データ・A4 の復元を変えない（指紋が変わり、キャッシュが使えなくなる）。走っている最中に `run_chain.sh` を書き換えない（bash は台本を読みながら実行する）。

## 終わったら

- `main.json` と `main_a4.json` の A4 以外のセルが一致することを確かめる（notes.md 316 行）。
- A4 の正答率は、CPU の塊を含む全体と、その書き手 1 人を除いた 499 人の両方（D3）。
- 探索的な分析 3〜5 の結果（集計だけ）を commit し、manuscript のブランチへ戻す（引き継ぎ `next-session-public-keystroke-matching-exploratory-3-5-ggear.md` の 3。push は研究者に確かめてから）。
- 結果の JSON は集計だけ。コミットは段ごとに。

## 守ること

- 記録・本文・A4 の復元・キャッシュの中身を Claude 自身も読まない（数・ハッシュ・分布だけ）。外部 LLM に送らない。
- 凍結の後の変更は `notes.md` の「逸脱」に。
- 応答は日本語。`git add -A`・`git add <dir>` を使わない。
