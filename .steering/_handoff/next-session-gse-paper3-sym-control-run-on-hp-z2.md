# 引き継ぎ —— 論文 3 の対称版の対照と選ばれた τ を職場の HP Z2 で回す

> 作成: 2026-11-19（Mac のセッション）。このメモを一次資料にしない。条件は `experiments/20261112-selection-split-and-smoothing/conditions.md` の追記「対称版の対照と選ばれた τ」、採否は `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 34（A・C）。下敷きは `next-session-gse-paper3-r1-computations-run-on-hp-z2.md`（§3.3 と §7 に対称版の実行の記録）。

## 0 入口の文（職場の PC の Claude Code に最初に打ち込む）

```
GSE-prototype の枝 docs/gse-paper3-per-person-learning を取り出し（worktree C:/Users/SDS02/GSE-prototype-paper3 なら git pull）、.steering/_handoff/next-session-gse-paper3-sym-control-run-on-hp-z2.md を読んで、experiments/20261112-selection-split-and-smoothing/run_ctrl.sh をこの PC で回し、結果を枝に push してください。条件とコードは変えず、門が赤なら直さずに止めて報告してください。
```

## 1 やること（これだけ）

- `run_ctrl.sh` を回して結果を持ち帰るだけ。notes・読み・本文は Mac のセッションが行う。条件・コードを変えない。結果の値を読んで解釈しない。
- 読む入力（repo の外・開かない・消さない・repo に入れない）: `~/gse-public-data/landscape/tau_mode_candidate_writer_values.coauthor.pkl`・`selection_split_smoothing_values.pkl`・`selection_split_smoothing_sym_values.pkl`（対称版の値・SHA-256 8596a3c7…）・`coauthor_work_obs`。
- 書く値: `~/gse-public-data/landscape/selection_split_smoothing_ctrl_values.pkl`（repo の外・開かない）。
- CoAuthor の記録も値も、Codex を含む外部の LLM に送らない。

## 2 回す（約 30 分）

対称版と同じ機械・同じ版（Python 3.11.9・numpy 2.4.4・git-bash）。照らしはビットまで同じかを見るので、版が違えば止めて報告する。回す前に `results/` の JSON が CRLF になっていれば `git -c core.autocrlf=false checkout -- experiments/` で取り出し直す（P-REPRO-SYMSUM は `sym_summary.json` を読む）。

```bash
cd <repo>/experiments/20261112-selection-split-and-smoothing
PYTHON=python JOBS=16 DATA_DIR="C:/Users/SDS02/gse-public-data" \
bash run_ctrl.sh 2>&1 | tee "C:/Users/SDS02/gse-public-data/selection_split_smoothing_ctrl_run.log"; echo "exit=${PIPESTATUS[0]}"
```

- 中身: selftest（合成・5 門）→ 変異 5 個（z1〜z5）→ ctrl（入力 3 つの SHA-256・17 人と単位の数・P-REPRO-SYMSUM（数秒）・倍率 1 の共通と最頻値と P-REPRO-MODE1・倍率 0.03 の共通と最頻値と P-REPRO-B1・集計）→ provenance_ctrl。本人の当てはめは回さない。
- 「P-REPRO-MODE1 通過（n 秒）」の n × 2 が 1.5 時間を超えると止まる（止まったら報告）。

## 3 終わったら

1. `results/` に `ctrl_summary.json`・`ctrl_tables.md`・`ctrl_check.json`・`ctrl_timing.json`・`selftest_ctrl.json`・`mutations_ctrl/`・`provenance_ctrl.json` があり、`ctrl_summary.json` と `provenance_ctrl.json` の `run_id` が同じこと。
2. `ctrl_check.json` の `p_repro_symsum`・`p_repro_mode1`・`p_repro_b1` の真偽と照らした数・最大の差を報告に写す（値の中身は読まない）。
3. `git status` で、変わったのが `results/` の下だけであること。
4. コミット（`data(experiments): 対称版の対照と選ばれた τ の結果（HP Z2） [skip ci]`・本文に `Refs: .steering/20261111-gse-paper3-round3-computations/`）して push。PR は出さない。
5. 回した時刻・版・照らしの結果を、このメモの末尾（§5）に追記してコミットして push。

## 4 止まったとき

- selftest・変異が赤: 直さずに赤の門を報告する（合成の値だけ）。
- SHA-256・P-REPRO-SYMSUM・P-REPRO-MODE1・P-REPRO-B1 が外れた: 直さずに `ctrl_check.json` の真偽と最大の差だけを写して報告する。版の違いか改行を疑う。
- 例外: メッセージに値が出うるので、研究者と Mac のセッションの間だけで扱う。

## 5 HP Z2 での実行の記録

（HP Z2 のセッションが記入する）

## 6 Mac 側の状態（2026-11-19）

- 条件は `927da1d7`（コードより前）。Mac（Python 3.14・numpy 2.5）で selftest 5 門が緑、変異 5 個がそれぞれ名指しの門だけを赤にした（`SELFTEST_ONLY=1`）。実データの読み込み・共通の当て直しは Mac では通していない（pickle が HP Z2 にしかない）。
