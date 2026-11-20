# 引き継ぎ —— 論文 3 の round 7 の計算 A（入れ替えの対照）と B（先頭の記号を除いた残り）を職場の HP Z2 で回す

> 作成: 2026-11-20（Mac のセッション）。このメモを一次資料にしない。条件は `experiments/20261112-selection-split-and-smoothing/conditions.md` の追記「入れ替えの対照（A）と先頭の記号を除いた残り（B）」、採否は `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 37・38。下敷きは `next-session-gse-paper3-sym-control-run-on-hp-z2.md`（§5 に前回の実行の記録）。

## 0 入口の文（職場の PC の Claude Code に最初に打ち込む）

```
GSE-prototype の枝 docs/gse-paper3-per-person-learning を取り出し（worktree C:/Users/SDS02/GSE-prototype-paper3 なら git pull）、.steering/_handoff/next-session-gse-paper3-round7-computations-run-on-hp-z2.md を読んで、experiments/20261112-selection-split-and-smoothing/run_r7.sh をこの PC で回し、結果を枝に push してください。条件とコードは変えず、門が赤なら直さずに止めて報告してください。
```

## 1 やること（これだけ）

- `run_r7.sh` を回して結果を持ち帰るだけ。notes・読み・本文は Mac のセッションが行う。条件・コードを変えない。結果の値を読んで解釈しない。
- 読む入力（repo の外・開かない・消さない・repo に入れない）: `~/gse-public-data/landscape/tau_mode_candidate_writer_values.coauthor.pkl`・`selection_split_smoothing_values.pkl`・`selection_split_smoothing_sym_values.pkl`（SHA-256 8596a3c7…）・`coauthor_work_obs`。
- 書く値: `~/gse-public-data/landscape/selection_split_smoothing_r7_values.pkl` と、A の前に書く `selection_split_smoothing_r7_values.pkl.partB`（どちらも repo の外・開かない）。
- CoAuthor の記録も値も、Codex を含む外部の LLM に送らない。

## 2 回す（約 1.5 時間の見込み）

前回と同じ機械・同じ版（Python 3.11.9・numpy 2.4.4・git-bash）。照らしはビットまで同じかを見るので、版が違えば止めて報告する。回す前に `results/` の JSON が CRLF になっていれば `git -c core.autocrlf=false checkout -- experiments/` で取り出し直す（P-REPRO-CURRENT は mode の `summary.json`、P-REPRO-RS は `sym_summary.json` を読む）。

```bash
cd <repo>/experiments/20261112-selection-split-and-smoothing
PYTHON=python JOBS=16 DATA_DIR="C:/Users/SDS02/gse-public-data" \
bash run_r7.sh 2>&1 | tee "C:/Users/SDS02/gse-public-data/selection_split_smoothing_r7_run.log"; echo "exit=${PIPESTATUS[0]}"
```

- 中身: selftest（合成・9 門・Mac で約 1 分）→ 変異 9 個（f1〜f9）→ r7:
  1. 入力 3 つの SHA-256・17 人と単位の数
  2. 倍率 1 の共通 4 構造（約 20 分）→ **P-REPRO-POOL1** → 本人の引き直し（4 構造 × k = 5・15）→ **P-REPRO-FIX** → **P-REPRO-CURRENT**
  3. 倍率 0.03 の共通 ar3（約 20 分）→ **P-REPRO-POOL03** → 本人' の引き直し → **P-REPRO-SYM** → **P-REPRO-RS**
  4. 時間の見積もり（4 時間を超えるなら止まる）→ w と v を除く共通 272 個（30 分前後）→ 入れ替えと本人'' の当てはめ → 集計
  5. provenance_r7
- 照らしは通るたびに「〜 通過」と出る。外れればその名前で止まる。

## 3 終わったら

1. `results/` に `r7_summary.json`・`r7_tables.md`・`r7_check.json`・`r7_timing.json`・`selftest_r7.json`・`mutations_r7/`・`provenance_r7.json` があり、`r7_summary.json` と `provenance_r7.json` の `run_id` が同じこと。
2. `r7_check.json` の `p_repro_pool1`・`p_repro_fix`・`p_repro_current`・`p_repro_pool03`・`p_repro_sym`・`p_repro_rs` の真偽と照らした数・最大の差、`r7_timing.json` の秒数を報告に写す（値の中身は読まない）。
3. `git status` で、変わったのが `results/` の下だけであること。
4. コミット（`data(experiments): 論文 3 の round 7 の計算 A・B の結果（HP Z2） [skip ci]`・本文に `Refs: .steering/20261111-gse-paper3-round3-computations/`）して push。PR は出さない。
5. 回した時刻・版・照らしの結果を、このメモの末尾（§5）に追記してコミットして push。

## 4 止まったとき

- selftest・変異が赤: 直さずに赤の門を報告する（合成の値だけ）。
- SHA-256・P-REPRO-* が外れた: 直さずに `r7_check.json` の真偽と最大の差だけを写して報告する。版の違いか改行を疑う。前回（ctrl）は、最頻値を当てはめと同じジョブで作ると 1 ulp ずれた。r7 は本人の引き直しと入れ替えを共通の当てはめと別のジョブで回し、共通の評価は sym.py と同じ形（同じジョブ・前回まで通過）にしている。外れたら、研究者に聞いてから、前回と同じく値を見ずに真偽だけで診断する。
- 時間の見積もりで止まった・A の途中で止まった: B の結果は A の前に `r7_summary.json`（`partial` 付き）と `.partB` に書いてある。`r7_timing.json` と `r7_check.json` を写し、`results/` をコミットして push してから報告する。
- 例外: メッセージに値が出うるので、研究者と Mac のセッションの間だけで扱う。

## 5 HP Z2 での実行の記録

（HP Z2 のセッションが記入する）

**2026-11-20（HP Z2・Python 3.11.9・numpy 2.4.4・git-bash・JOBS=16）**

- run_id `20261120T164346-1717`・git_head `9ac3a595`・dirty なし。16:43 に始めて 17:55 に終わった（exit 0）。コード・条件は変えていない。
- 入力の SHA-256 一致。selftest 9 門 緑。変異 f1〜f9 はどれも exit 3 で、名指しの門だけが赤（ログの判定）。
- P-REPRO-POOL1 通過（68・最大の差 0.0）・P-REPRO-FIX 通過（1122・0.0）・P-REPRO-CURRENT 通過（2・0.0）・P-REPRO-POOL03 通過（17・0.0）・P-REPRO-SYM 通過（272・0.0）・P-REPRO-RS 通過（2・0.0）。
- `r7_timing.json` の秒: pool_1 1123・replay_1 1194・full_03 1037・excl_03 13・replay_03 2313・pair_pool の見積り 111・pair_pool 209・pair_fit 3861。
- `r7_summary.json` と `provenance_r7.json` の run_id は同じ。結果は `da85da29`。値の中身は読んでいない。

## 6 Mac 側の状態（2026-11-20）

- 条件は `d98fde84`（コードより前）、コードは `2b1fc341`、/cross-review（Claude と Codex）の直しは `06fc7ec8`（判断 39）。Mac（Python 3.14・numpy 2.5）で selftest 9 門が緑、変異 9 個がそれぞれ名指しの門を赤にした（f2 は P-REPLAY03 も赤）。集計と表の書き出しは合成の値で通した。実データの読み込み・当て直しは Mac では通していない（pickle が HP Z2 にしかない）。
