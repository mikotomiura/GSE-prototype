# 引き継ぎ —— 最頻値を他人で選ぶ候補と比べの相手に置く集計を、職場の HP Z2 で回す

> 作成: 2026-11-11（Mac のセッション）。このメモを一次資料にしない。条件は `experiments/20261111-mode-in-selection/conditions.md`、判断は `.steering/20261111-gse-paper3-round3-computations/decisions.md`。下敷きは `next-session-gse-tau-mode-candidate-run-on-hp-z2.md`（§7 に最頻値の試験の HP Z2 での実行の記録）。

## 0 入口の文（職場の PC の Claude Code に最初に打ち込む）

```
GSE-prototype の枝 docs/gse-paper3-per-person-learning を取り出し、.steering/_handoff/next-session-gse-paper3-mode-in-selection-run-on-hp-z2.md を読んで、experiments/20261111-mode-in-selection/run.sh をこの PC で回し、結果を枝に push してください。条件とコードは変えず、門が赤なら直さずに止めて報告してください。当てはめは回しません（最頻値の試験が残した書き手ごとの値を読むだけ）。
```

## 1 やること（これだけ）

- `run.sh` を回して結果を持ち帰るだけ。notes・読み・レビューは Mac のセッションが行う。
- 条件・コードを変えない。門（selftest・変異・P-REPRO）が赤なら、直さずに止めて、何が赤かだけを報告する。
- 結果の値を読んで解釈しない（`results/summary.json` と `tables.md` は、ファイルができたかと `run_id` の確かめまで）。
- 読む入力は repo の外の `~/gse-public-data/landscape/tau_mode_candidate_writer_values.coauthor.pkl` と `.cs1.pkl`（最頻値の試験の本計算 run_id 20261106T205818-149 が書いた書き手ごとの値）。開かない。消さない。repo に入れない。
- CoAuthor・CS1 の記録も値も、Codex を含む外部の LLM に送らない。

## 2 準備

1. 最頻値の試験と同じ機械・同じ版（Python 3.11.9・numpy 2.4.4・git-bash）。P-REPRO は、pickle に最頻値の試験の集計を当て直して、その summary.json と JSON として同じかを見る。版が違うと区間の乱数や丸めが違いうるので、違えば止めて報告する。
2. コード: `git fetch origin && git checkout docs/gse-paper3-per-person-learning`。`run.sh` が LF であること。
3. 入力の pickle が 2 つあること（`ls -l "$DATA_DIR/landscape/tau_mode_candidate_writer_values".*.pkl`）。無ければ止めて報告する（条件 D1 の回し直しは研究者に確かめてから）。

## 3 回す

git-bash で:

```bash
cd <repo>/experiments/20261111-mode-in-selection
PYTHON=python DATA_DIR="C:/Users/SDS02/gse-public-data" bash run.sh 2>&1 | tee "$DATA_DIR/mode_in_selection_run.log"; echo "exit=${PIPESTATUS[0]}"
```

- 中身: selftest（合成の値・6 門）→ 変異 4 個（名指しの門が赤）→ P-REPRO（CoAuthor → CS1）→ 集計 → provenance。
- 見込み: 数分（当てはめは無い）。Mac では selftest と変異が数秒で通った。

## 4 終わったら

1. `results/` に `summary.json`・`tables.md`・`repro_check.json`・`selftest.json`・`mutations/`・`provenance.json` があり、`summary.json` と `provenance.json` の `run_id` が同じこと。
2. `repro_check.json` の `p_repro`（coauthor・cs1 の真偽）と `pkl_sha256` を報告に写す。偽なら run.sh はそこで止まっている（終了コード 1）。結果はコミットせず、報告の頭に「P-REPRO が外れた」と書く。
3. `git status` で、変わったのが `experiments/20261111-mode-in-selection/results/` の下だけであること。
4. コミット（`data(experiments): 最頻値を候補と相手に置いた集計の結果（HP Z2） [skip ci]`・本文に `Refs: .steering/20261111-gse-paper3-round3-computations/`）して push。PR は出さない。
5. 回した時刻・Python と numpy の版・P-REPRO の結果を、このメモの末尾（§7）に追記してコミットする。

## 5 止まったとき

- selftest・変異が赤: 直さずに、`results/selftest.json` の赤の門を報告する（合成の値だけ）。
- P-REPRO が外れた: pickle が最頻値の試験の本計算のものと違うか、版が違う。直さずに報告する（Mac のセッションと研究者で、最頻値の試験の run.sh を回し直すかを決める）。
- 例外: メッセージに値が出うるので、研究者と Mac のセッションの間だけで扱う。

## 6 Mac 側の状態（2026-11-11）

- 枝 `docs/gse-paper3-per-person-learning`。条件は `51b7656c`。コードのコミットは（コミットの後に追記する）。push は研究者が確かめてから行う。
- Mac（Python 3.14.4・numpy 2.5.2）で selftest 6 門が緑、変異 4 個がすべて名指しの門を赤にした（`SELFTEST_ONLY=1 bash run.sh`）。

## 7 HP Z2 での実行の記録

（職場の PC のセッションが追記する）
