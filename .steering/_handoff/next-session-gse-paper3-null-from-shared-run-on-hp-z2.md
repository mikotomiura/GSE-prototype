# 引き継ぎ —— 論文 3 の計算 (f)（共通のモデルそのものから作る帰無）を職場の HP Z2 で回す

> 作成: 2026-11-13（Mac のセッション）。このメモを一次資料にしない。条件は `experiments/20261113-null-from-shared/conditions.md`、採否は `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 24・25。下敷きは `next-session-gse-paper3-r1-computations-run-on-hp-z2.md`（§7 に HP Z2 での実行の記録）。

## 0 入口の文（職場の PC の Claude Code に最初に打ち込む）

```
GSE-prototype の枝 docs/gse-paper3-per-person-learning を取り出し、.steering/_handoff/next-session-gse-paper3-null-from-shared-run-on-hp-z2.md を読んで、experiments/20261113-null-from-shared/run.sh をこの PC で回し、結果を枝に push してください。条件とコードは変えず、門が赤なら直さずに止めて報告してください。
```

## 1 やること（これだけ）

- `run.sh` を 1 回回して結果を持ち帰るだけ。notes・読み・レビューは Mac のセッションが行う。
- 条件・コードを変えない。門が赤なら直さずに止めて、何が赤かだけを報告する。
- 結果の値を読んで解釈しない（`gate.json`・`summary.json`・`tables.md` は、ファイルができたかと `run_id` の確かめまで）。
- 読む入力（repo の外・開かない・消さない・repo に入れない）:
  - `~/gse-public-data/landscape/coauthor_work_obs`（CoAuthor の記号）
  - manifest `C:/Users/SDS02/Desktop/GSE_ML_run/input_manifest.json`（SHA-256 e0163f1b…・A・B と同じ）
- 書く値: `~/gse-public-data/landscape/null_from_shared_m0.npz`（実データの全員の共通の母数・repo の外・開かない・送らない）。
- CoAuthor の記録も m0 も合成の系列も、Codex を含む外部の LLM に送らない。

## 2 準備

1. A・B・D と同じ機械・同じ版（Python 3.11.9・numpy 2.4.4・git-bash）。
2. コード: `git fetch origin && git checkout docs/gse-paper3-per-person-learning && git pull`（worktree `C:/Users/SDS02/GSE-prototype-paper3` なら `git pull`）。CRLF で取り出したファイルが残っていれば `git -c core.autocrlf=false checkout -- experiments/` で取り出し直す（読み込むコードの SHA-256 を照らすので、改行が変わると止まる）。
3. 記号のディレクトリと manifest があること。無ければ止めて報告する。
4. D の `results/replicates/`（55 本）が repo にあること（report が D の同じ番号の複製と並べる）。

## 3 回す（約 11 時間）

```bash
cd <repo>/experiments/20261113-null-from-shared
PYTHON=python JOBS=16 DATA_DIR="C:/Users/SDS02/gse-public-data" \
INPUT_MANIFEST="C:/Users/SDS02/Desktop/GSE_ML_run/input_manifest.json" \
INPUT_MANIFEST_SHA256=e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406 \
bash run.sh 2>&1 | tee "C:/Users/SDS02/gse-public-data/null_from_shared_run.log"; echo "exit=${PIPESTATUS[0]}"
```

- 中身: selftest（11 門・偽の m0・P-RUN は小さな形で門・本計算・再開・report を通すので 2〜3 分）→ 変異 8 個（各 2〜3 分） → manifest の照合 → m0 の当てはめ（実データ・ar3 を基の倍率 1・0.3・0.1・0.03 で）→ 門（倍率ごとに差 0 の合成 3 種で b = 最頻値 − 共通 を測り、倍率を 1 つ選ぶ）→ 較正（4 段）→ 本計算 55 本 → report → provenance。
- 見込み: m0 は数分〜数十分、門 12 本は各 3〜4 分、較正は約 50 分、本計算は 1 本約 10 分で約 9.5 時間。最初の 1 本の時間 × 55 が 24 時間を超えると D と同じ順に削り、全部削っても超えれば止まる。
- 門で止まると exit 5 と「門で止まった」が出る（3 種とも b > 0 になる倍率が無い）。これは条件どおりの止まり方で、欠陥ではない。そのまま結果をコミットして push し、報告する（本計算には入っていない）。
- 途中で止まっても、もう一度同じ命令で回せば、m0・門・較正・できた複製を照らして続きから回る（`results/` の `m0_fit.json`・`gate_parts/`・`gate.json`・`calibration.json`・`replicates/`・`plan.json` と npz を消さない。門も 1 本ずつ書くので途中から続く）。

## 4 終わったら

1. `results/` に `m0_fit.json`・`gate_parts/`（12 本）・`gate.json`・`calibration.json`・`replicates/`（55 本か、削った本数）・`plan.json`・`summary.json`・`tables.md`・`selftest.json`・`mutations/`・`input_manifest_check.json`・`provenance.json` があり、`summary.json` と `provenance.json` の `run_id` が同じこと（門で止まったときは `summary.json` と `tables.md` と `calibration.json` と `replicates/` は無い）。
2. 報告に写すもの（値の中身でなく）: `m0_fit.json` の `checks` の真偽と `seconds`・`seconds_each`、`gate.json` の `chosen`（選ばれた倍率の文字か null）と `seconds`、`plan.json` の `estimate_hours`・`cuts_applied`・`first_rep_seconds`。
3. `git status` で、変わったのが `experiments/20261113-null-from-shared/results/` の下だけであること。npz が repo に入っていないこと。
4. コミット（`data(experiments): 計算 (f) の結果（HP Z2） [skip ci]`・本文に `Refs: .steering/20261111-gse-paper3-round3-computations/`）して push。PR は出さない。
5. 回した時刻・Python と numpy の版・照らしの結果を、このメモの末尾（§7）に追記してコミットして push。

## 5 止まったとき

- npz の置き場が repo の中と出た: `DATA_DIR`・`M0` の設定を確かめる（D0 の守り）。
- 「m0 を作り直すのに古い … が残っている」と出た: 前の回の結果が残っている。消さずに報告する。
- selftest・変異が赤: 直さずに、`results/selftest.json` か `mutations/` の赤の門を報告する（合成の値だけ）。
- 読み込むコードの SHA-256 が違うと出た: 取り出しの改行を疑い、§2 の 2 で取り出し直してから回し直す。それでも止まれば報告する。
- manifest の照合が外れた: 直さずに報告する（`input_manifest_check.json` の件数だけ）。
- m0 の形か行の和が条件と違う: 直さずに報告する（値は表示されない）。
- 「選んだ m0 に確率 0 のセルがある」と出た: 直さずに報告する。
- 較正が ±10% に入らない: 直さずに報告する（`calibration.json` の `ok` の真偽だけ）。

## 6 守ること

- 条件・コード・SEED を変えない。結果を見て読みを書かない。
- push は枝だけ。PR は出さない（[skip ci]）。
- npz・CoAuthor の記録を repo に入れない・開かない・外部に送らない。

## 7 HP Z2 での実行の記録（HP Z2 のセッションが追記する）


記入: 2026-11-18（HP Z2 のセッション）。

- 機械と版: HP Z2・Python 3.11.9・numpy 2.4.4・git-bash・`JOBS=16`。worktree `C:/Users/SDS02/GSE-prototype-paper3`、コードは `52eab98a`（`provenance.json` の `git_dirty_paths` は空）。`run_id` は `20261118T124517-101`（`summary.json` と `provenance.json` で同じ）。終了コード 0。結果のコミットは `c89be93f`。
- 準備: この試験のディレクトリに `.gitattributes` が無く、`core.autocrlf=true` の HP Z2 では run.sh・SEED・scripts が CRLF で取り出されていた。§2 の 2 のとおり `git -c core.autocrlf=false checkout -- experiments/` で LF に取り出し直した（作業ツリーの変更は 0）。manifest の SHA-256 は `e0163f1b…` で一致。AC のスリープ・休止は 0、C: の空きは 227 GB。前の回の結果・npz の残りは無かった。
- 時刻（各段の終わりはファイルの更新時刻）: 開始 12:45:17 → selftest 11 門緑（12:46:44）→ 変異 8 個（n1〜n8）すべて名指しの門が赤（12:58:25）→ manifest の照合（12:58:37・2,678 ファイル・外れ 0・余り 0）→ m0 の当てはめ（13:15:51）→ 門 12 本（14:26:55）→ 較正（15:16:24）→ 本計算 55 本（23:37:51）→ report → provenance → 終わり 23:37:58（約 10 時間 53 分）。
- `m0_fit.json`: `checks` は 4 倍率（1・0.3・0.1・0.03）とも `shape`・`finite_nonneg`・`rows_sum_1` が true、`has_zero_cell` が false。`seconds` 1,033、`seconds_each` は 1: 952・0.3: 1,000・0.1: 1,028・0.03: 1,031。
- `gate.json`: `chosen` は `"0.03"`、`seconds` 4,263。
- `calibration.json`: 4 段とも `ok` が true（`seconds` 2,969）。
- `plan.json`: `estimate_hours` 8.13、`cuts_applied` 0、`first_rep_seconds` 532。複製は 55 本（1 本 447〜625 秒）。
- `git status`: 変わったのは `experiments/20261113-null-from-shared/results/` の下だけ。npz は repo に無い（`null_from_shared_m0.npz` は `DATA_DIR/landscape/` に書かれ、開いていない）。
- 次から: Windows で取り出すなら、この試験のディレクトリにも `.gitattributes`（*.sh・SEED・*.py・*.json）を足すのを勧める（採否は研究者）。
