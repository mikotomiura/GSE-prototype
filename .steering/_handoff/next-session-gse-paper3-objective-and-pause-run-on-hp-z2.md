# 引き継ぎ —— 他人で選ぶ目的を平均に替えた集計と休止の秒の割合を、職場の HP Z2 で回す

> 作成: 2026-11-11（Mac のセッション）。このメモを一次資料にしない。条件は `experiments/20261111-objective-and-pause/conditions.md`、採否は `.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-4/verdict.md` §8。下敷きは `next-session-gse-paper3-mode-in-selection-run-on-hp-z2.md`（計算 3・§7 に HP Z2 での実行の記録）。

## 0 入口の文（職場の PC の Claude Code に最初に打ち込む）

```
GSE-prototype の枝 docs/gse-paper3-per-person-learning を取り出し、.steering/_handoff/next-session-gse-paper3-objective-and-pause-run-on-hp-z2.md を読んで、experiments/20261111-objective-and-pause/run.sh をこの PC で回し、結果を枝に push してください。条件とコードは変えず、門が赤なら直さずに止めて報告してください。当てはめは回しません（最頻値の試験が残した書き手ごとの値と、同じ記号のデータを読むだけ）。
```

## 1 やること（これだけ）

- `run.sh` を回して結果を持ち帰るだけ。notes・読み・レビューは Mac のセッションが行う。
- 条件・コードを変えない。門（selftest・変異・P-REPRO・P-SAMESEL・P-NEVAL）が赤なら、直さずに止めて、何が赤かだけを報告する。
- 結果の値を読んで解釈しない（`results/summary.json` と `tables.md` は、ファイルができたかと `run_id` の確かめまで）。
- 読む入力（repo の外・開かない・消さない・repo に入れない）:
  - `~/gse-public-data/landscape/tau_mode_candidate_writer_values.coauthor.pkl` と `.cs1.pkl`（計算 3 と同じ）
  - `~/gse-public-data/landscape/coauthor_work_obs` と `~/gse-public-data/cs1/work2021_obs`（最頻値の試験の本計算が読んだ記号。休止の秒を数えるのに使う）
- CoAuthor・CS1 の記録も値も、Codex を含む外部の LLM に送らない。

## 2 準備

1. 計算 3 と同じ機械・同じ版（Python 3.11.9・numpy 2.4.4・git-bash）。P-REPRO と P-SAMESEL は計算 3 の集計と JSON として同じかを見るので、版が違えば止めて報告する。
2. コード: `git fetch origin && git checkout docs/gse-paper3-per-person-learning && git pull`。2026-11-11 に計算 3 と最頻値の試験と、この試験に `.gitattributes`（LF の固定）を足した。前に CRLF で取り出した作業ツリーなら、`git -c core.autocrlf=false checkout -- experiments/` で取り出し直してから回す（計算 3 の §7 の件）。
3. 入力の pickle が 2 つ、記号のディレクトリが 2 つあること。無ければ止めて報告する。

## 3 回す

git-bash で:

```bash
cd <repo>/experiments/20261111-objective-and-pause
PYTHON=python DATA_DIR="C:/Users/SDS02/gse-public-data" bash run.sh 2>&1 | tee "$DATA_DIR/objective_and_pause_run.log"; echo "exit=${PIPESTATUS[0]}"
```

- 中身: selftest（合成の値・5 門）→ 変異 3 個（名指しの門が赤）→ P-REPRO（pickle）→ 集計（中央値・平均・最頻値なし）→ P-NEVAL（記号を読み、評価の単位の記号の数が pickle と同じ）→ P-SAMESEL（中央値の目的の集計が計算 3 の summary と同じ）→ provenance。
- 見込み: 数分〜十数分（記号の読み込みが主）。1 時間を超えたら止めて報告する。

## 4 終わったら

1. `results/` に `summary.json`・`tables.md`・`checks.json`・`selftest.json`・`mutations/`・`provenance.json` があり、`summary.json` と `provenance.json` の `run_id` が同じこと。
2. `checks.json` の `p_repro`（coauthor・cs1）・`p_neval`（coauthor・cs1）・`p_samesel` と `pkl_sha256` を報告に写す。偽があれば run.sh はそこで止まっている（終了コード 1）。結果はコミットせず、報告の頭に何が外れたかを書く。
3. `git status` で、変わったのが `experiments/20261111-objective-and-pause/results/` の下だけであること。
4. コミット（`data(experiments): 目的を平均に替えた選びと休止の秒の割合の結果（HP Z2） [skip ci]`・本文に `Refs: .steering/20261111-gse-paper3-round3-computations/`）して push。PR は出さない。
5. 回した時刻・Python と numpy の版・照らしの結果を、このメモの末尾（§7）に追記してコミットして push。

## 5 止まったとき

- selftest・変異が赤: 直さずに、`results/selftest.json` の赤の門を報告する（合成の値だけ）。
- P-REPRO・P-SAMESEL が外れた: pickle か計算 3 の集計と違う。版の違いか取り出しの改行を疑い、直さずに報告する。
- P-NEVAL が外れた: 記号のデータが最頻値の試験の本計算のものと違う。直さずに報告する。
- 例外: メッセージに値が出うるので、研究者と Mac のセッションの間だけで扱う。

## 6 Mac 側の状態（2026-11-11）

- 枝 `docs/gse-paper3-per-person-learning`。条件は `8ea112c4`、コードと合成の門は `eb764c9c`。
- Mac（Python 3.14.4・numpy 2.5.2）で selftest 5 門が緑、変異 3 個がすべて名指しの門を赤にした（`SELFTEST_ONLY=1 bash run.sh`）。計算 3 の selftest の合成の書き手で、集計の道（中央値・平均・最頻値なし・選びの違い・最頻値 − 共通）を通した。休止の秒の数えは実データが要るので Mac では通していない。

## 7 HP Z2 での実行の記録

（職場の PC のセッションが追記する）
