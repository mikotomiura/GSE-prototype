# 引き継ぎ —— 論文 3 の計算 A・B・D を職場の HP Z2 で回す

> 作成: 2026-11-12（Mac のセッション）。このメモを一次資料にしない。条件は `experiments/20261112-selection-split-and-smoothing/conditions.md`（A・B）と `experiments/20261112-sensitivity-ten-seeds/conditions.md`（D）、採否は `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 17・18。下敷きは `next-session-gse-paper3-objective-and-pause-run-on-hp-z2.md`（§7 に HP Z2 での実行の記録）。

## 0 入口の文（職場の PC の Claude Code に最初に打ち込む）

```
GSE-prototype の枝 docs/gse-paper3-per-person-learning を取り出し、.steering/_handoff/next-session-gse-paper3-r1-computations-run-on-hp-z2.md を読んで、experiments/20261112-selection-split-and-smoothing/run.sh と experiments/20261112-sensitivity-ten-seeds/run.sh をこの PC で順に回し、結果を枝に push してください。条件とコードは変えず、門が赤なら直さずに止めて報告してください。
```

## 1 やること（これだけ）

- 2 つの `run.sh` を順に回して結果を持ち帰るだけ。notes・読み・レビューは Mac のセッションが行う。
- 条件・コードを変えない。門が赤なら直さずに止めて、何が赤かだけを報告する。
- 結果の値を読んで解釈しない（`summary.json` と `tables.md` は、ファイルができたかと `run_id` の確かめまで）。
- 読む入力（repo の外・開かない・消さない・repo に入れない）:
  - `~/gse-public-data/landscape/tau_mode_candidate_writer_values.coauthor.pkl` と `.cs1.pkl`（最頻値の試験の本計算の値・計算 3 と同じ）
  - `~/gse-public-data/landscape/coauthor_work_obs` と `~/gse-public-data/cs1/work2021_obs`（記号）
  - manifest `C:/Users/SDS02/Desktop/GSE_ML_run/input_manifest.json`（SHA-256 e0163f1b…・最頻値の試験と同じ）
- A・B が書く値: `~/gse-public-data/landscape/selection_split_smoothing_values.pkl`（repo の外・開かない）。
- CoAuthor・CS1 の記録も値も、Codex を含む外部の LLM に送らない。

## 2 準備

1. 最頻値の試験と同じ機械・同じ版（Python 3.11.9・numpy 2.4.4・git-bash）。A・B の P-REPRO・P-REPRO-POOL・P-REPRO-R1・P-CURRENT は最頻値の試験の値とビットまで同じかを見るので、版が違えば止めて報告する。
2. コード: `git fetch origin && git checkout docs/gse-paper3-per-person-learning && git pull`（worktree `C:/Users/SDS02/GSE-prototype-paper3` なら `git pull`）。CRLF で取り出したファイルが残っていれば `git -c core.autocrlf=false checkout -- experiments/` で取り出し直す。
3. 入力の pickle が 2 つ、記号のディレクトリが 2 つ、manifest があること。無ければ止めて報告する。

## 3 回す

### 3.1 A・B（約 1.5 時間）

```bash
cd <repo>/experiments/20261112-selection-split-and-smoothing
PYTHON=python JOBS=16 DATA_DIR="C:/Users/SDS02/gse-public-data" \
INPUT_MANIFEST="C:/Users/SDS02/Desktop/GSE_ML_run/input_manifest.json" \
INPUT_MANIFEST_SHA256=e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406 \
bash run.sh 2>&1 | tee "C:/Users/SDS02/gse-public-data/selection_split_smoothing_run.log"; echo "exit=${PIPESTATUS[0]}"
```

- 中身: selftest（合成・13 門）→ 変異 10 個 → manifest の照合 → compute（pickle の SHA-256・P-REPRO・B2 の r1 と P-REPRO-R1・B1 の α = 1 の共通の当て直しと P-REPRO-POOL・残りの α 4 つ）→ ab（A の二分・P-CURRENT・B の集計と表）→ provenance。
- 見込み: B1 の共通の当て直しが主で約 80 分。「P-REPRO-POOL 通過（n 秒）」が出た時点で、n × 5 が 6 時間を超えると、コードが α = 3 → 0.03 の順に外す（timing.json の `alpha_cut`）。それでも超えればそこで止まる（止まったら報告）。

### 3.2 D（約 10 時間・A・B が終わってから）

```bash
cd <repo>/experiments/20261112-sensitivity-ten-seeds
PYTHON=python JOBS=16 bash run.sh 2>&1 | tee "C:/Users/SDS02/gse-public-data/sensitivity_ten_seeds_run.log"; echo "exit=${PIPESTATUS[0]}"
```

- 中身: selftest（4 門）→ 変異 8 個 → 本計算 55 本（最初の 1 本の時間で見積もり、24 時間を超えれば条件 D5 の順に削る。全部削っても超えれば止まる）→ report → provenance。実データは使わない（合成だけ）。
- 途中で止まっても、もう一度同じ命令で回せば、できた複製を照らして続きから回る（`results/replicates/` と `plan.json` を消さない）。

### 3.3 B1 の対称版（判断 19・D が終わってから・1 時間以下の見込み）

A・B の結果を見た後に足した計算（conditions.md の追記「B1 の対称版」）。本人の ar3 を倍率 0.03 の基で当て直す。

```bash
cd <repo>/experiments/20261112-selection-split-and-smoothing
PYTHON=python JOBS=16 DATA_DIR="C:/Users/SDS02/gse-public-data" \
bash run_sym.sh 2>&1 | tee "C:/Users/SDS02/gse-public-data/selection_split_smoothing_sym_run.log"; echo "exit=${PIPESTATUS[0]}"
```

- 中身: selftest（6 門）→ 変異 5 個 → sym（pickle と B の値の SHA-256・17 人と単位の数・倍率 1 の共通と本人の当て直しと P-REPRO-SELF・倍率 0.03 の共通と P-REPRO-B1・倍率 0.03 の本人・集計）→ provenance_sym。
- 「P-REPRO-SELF 通過（n 秒）」の n × 2 が 2 時間を超えると止まる（止まったら報告）。
- 書く値: `~/gse-public-data/landscape/selection_split_smoothing_sym_values.pkl`（repo の外・開かない）。
- 終わったら: `results/` に `sym_summary.json`・`sym_tables.md`・`sym_check.json`・`sym_timing.json`・`selftest_sym.json`・`mutations_sym/`・`provenance_sym.json` があること。`sym_check.json` の `p_repro_self`・`p_repro_b1` の真偽と照らした数を報告に写す。コミット（`data(experiments): B1 の対称版の結果（HP Z2） [skip ci]`）して push。

## 4 終わったら

1. A・B: `results/` に `summary.json`・`tables.md`・`repro_check.json`・`timing.json`・`selftest.json`・`mutations/`・`input_manifest_check.json`・`provenance.json` があり、`summary.json` と `provenance.json` の `run_id` が同じこと。`repro_check.json` の `pkl_sha256`・`p_repro`・`p_repro_r1`・`p_repro_pool` と、`summary.json` の `p_current` を報告に写す（値の中身でなく真偽と照らした数）。
2. D: `results/` に `replicates/`（55 本か、削った本数）・`plan.json`・`summary.json`・`tables.md`・`machine_check.json`・`selftest.json`・`mutations/`・`provenance.json` があること。`plan.json` の `estimate_hours`・`cuts_applied`・`first_rep_seconds` を報告に写す。
3. `git status` で、変わったのが 2 つの dir の `results/` の下だけであること。
4. コミット（A・B: `data(experiments): 計算 A・B の結果（HP Z2） [skip ci]`・D: `data(experiments): 計算 D の結果（HP Z2） [skip ci]`・本文に `Refs: .steering/20261111-gse-paper3-round3-computations/`）して push。PR は出さない。A・B が終わった時点で一度 push してよい。
5. 回した時刻・Python と numpy の版・照らしの結果を、このメモの末尾（§7）に追記してコミットして push。

## 5 止まったとき

- selftest・変異が赤: 直さずに、`results/selftest.json` か `mutations/` の赤の門を報告する（合成の値だけ）。
- pickle の SHA-256・P-REPRO・P-REPRO-R1・P-REPRO-POOL・P-CURRENT が外れた: 最頻値の試験の値とビットが揃わない。版の違いか取り出しの改行を疑い、直さずに報告する（`repro_check.json` の真偽と最大の差だけを写す）。
- manifest の照合が外れた: 記号のデータが違う。直さずに報告する。
- 例外: メッセージに値が出うるので、研究者と Mac のセッションの間だけで扱う。

## 6 Mac 側の状態（2026-11-12）

- 枝 `docs/gse-paper3-per-person-learning`。条件は `401133c2`、コードは `632a3ee5`、/cross-review の直しは `7a9d0554`。
- Mac（Python 3.14.4・numpy 2.5.2）で、A・B の selftest 13 門・変異 10 個、D の selftest 4 門・変異 8 個が通り、名指しの門がすべて赤になった。形だけ合わせた偽の値で、A・B の集計と表、D の report を最後まで通した（偽の値では P-CURRENT が止まることも見た）。実データの読み込み・共通の当て直しは Mac では通していない。

## 7 HP Z2 での実行の記録

記入: 2026-11-12（HP Z2 のセッション）。

### A・B

- 機械と版: HP Z2・Python 3.11.9・numpy 2.4.4・git-bash・`JOBS=16`。worktree `C:/Users/SDS02/GSE-prototype-paper3`、コードは `2a84c97a`。入力の pickle 2 つ・記号の dir 2 つ・manifest（SHA-256 e0163f1b… 一致）あり。2 つの dir の中身は LF で取り出されていた。
- 時刻: 開始 01:23:48 → selftest 13 門緑 → 変異 10 個（s1〜s10）すべて名指しの門が赤 → manifest の照合 → compute（P-REPRO-POOL 通過 1,289 秒・`alpha_cut` は空＝α を外していない）→ ab → provenance → 終わり 03:20:09。終了コード 0。`run_id` `20261112T012348-4213`（`summary.json` と `provenance.json` で同じ）。
- `repro_check.json`: `pkl_sha256` coauthor `a0d3627e281191a42e23d186034de79419931f73c02964f52e17d830d488f94c`・cs1 `08cdd31e567b164397473dbb0531a16f7b11729070317b78c0c9c6510d8bf7e6`。`p_repro` coauthor true・cs1 true。`p_repro_r1` coauthor true（照らした 140・最大の差 0.0）・cs1 true（92・0.0）。`p_repro_pool` true（68・0.0）。
- `summary.json` の `p_current`: true（照らした 100）。
- `provenance.json` の `git_dirty_paths` は `?? experiments/20261112-selection-split-and-smoothing/results/` だけ。
- 結果は `38b4be20` で push 済み。`summary.json`・`tables.md` の値は読んでいない。`selection_split_smoothing_values.pkl` は開いていない。

### D

- 03:20:27 に開始（A・B の push の後、裏のスクリプトが続けて起動。04:00 から HP Z2 がオフラインになるため、D のコミットはローカルに残し、オンラインに戻ってから push する）。記録はその後で追記する。
