# 引き継ぎ —— 構造の足りなさの仮説を確かめる試験の本計算を、職場の HP Z2 で回す

> 作成: 2026-11-07（Mac のセッション）。このメモを一次資料にしない。条件は `experiments/20261107-structure-deficit-test/conditions.md`（末尾の「条件の後の変更」を含む）、判断は `.steering/20261107-gse-structure-deficit-test/decisions.md`。下敷きは前の試験の `next-session-gse-tau-mode-candidate-run-on-hp-z2.md`（§7 に前の試験の HP Z2 の記録）。

## 0 入口の文（職場の PC の Claude Code に最初に打ち込む）

```
GSE-prototype の枝 exp/gse-structure-deficit-test を取り出し、.steering/_handoff/next-session-gse-structure-deficit-run-on-hp-z2.md を読んで、構造の足りなさの試験の run.sh をこの PC で回し、結果を枝に push してください。条件とコードは変えず、門が赤なら直さずに止めて報告してください。入力のデータは前の試験（tau-mode-candidate）で使ったものをそのまま使います。
```

## 1 やること（これだけ）

この PC では `run.sh` を回して結果を持ち帰るだけにする。notes・読み・レビューは Mac のセッションが行う。

- 条件・コードを変えない。門（manifest・P-D1・selftest・変異・P-Q・P-REPRO）が赤なら、直さずに止めて、何が赤かだけを報告する。
- 結果の値を読んで解釈しない（`results/summary.json` を開くのは、ファイルができたかと `run_id` の確かめまで。`repro_check.json` と `q_gate.json` は外れた数と節の名前を見てよい）。
- 書き手ごとの値は repo の外 `~/gse-public-data/landscape/structure_deficit_writer_values.<組>.<データ>.pkl` に書かれる。開かない。repo に入れない。前の試験の書き手ごとの値・共通の母数も消さない・開かない。
- CoAuthor・CS1 の記録も値も、Codex を含む外部の LLM に送らない。

## 2 準備

1. 前の試験と同じ機械・同じ版で回す（P-REPRO は同じ版でないと照らせない）: Python 3.11.9（`python`）・numpy 2.4.4・git-bash。違えば止めて報告する。
2. コード: 前の試験で使った clone で `git fetch origin && git checkout exp/gse-structure-deficit-test`（Mac のコミットは §6）。`run.sh`・`mutate.sh` が LF であること（ディレクトリの `.gitattributes` で固定）。
   - この枝には前の 3 つの試験のディレクトリもある。P-SAME は `experiments/20261104-timeseries-tau-extend/scripts/ml.py` と `experiments/20261104-coauthor-ml-improve/scripts/ml.py` を別のプロセスで呼び、P-REPRO は両方の `results/summary.json` と照らし、P-D1 と manifest の照合は `experiments/20261106-tau-mode-candidate/scripts/` の門を使う。どれも変えない。
3. データ: 前の試験と同じ `C:/Users/SDS02/gse-public-data`（以下 `DATA_DIR`）と manifest `C:/Users/SDS02/Desktop/GSE_ML_run/input_manifest.json`。manifest の SHA-256 は `e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406`（run.sh が照らす）。
4. スリープ: AC のスリープ・休止が 0 のままかを確かめる（本計算は半日を超える見込み・§3）。
5. 空き容量: `DATA_DIR` のドライブに 2 GB 以上（書き手ごとの値の pkl が 12 個）。

## 3 回す

git-bash で:

```bash
cd <repo>/experiments/20261107-structure-deficit-test
PYTHON=python DATA_DIR="C:/Users/SDS02/gse-public-data" \
INPUT_MANIFEST="C:/Users/SDS02/Desktop/GSE_ML_run/input_manifest.json" \
INPUT_MANIFEST_SHA256=e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406 \
JOBS=16 bash run.sh 2>&1 | tee "$DATA_DIR/structure_deficit_run.log"; echo "exit=${PIPESTATUS[0]}"
```

- 中身: manifest の照合 → 門の selftest（`check_same_cs1.py`・`repro_check.py`）→ P-D1 の門 2 つ → selftest（合成・19 対照）→ 変異 16 個（合成）→ P-Q（`results/q_gate.json`・q = 5 の作り直しが全行で obs と一致しなければ止まる）→ 組 q5_o（CoAuthor → CS1）→ P-REPRO（`results/repro_check.json`・外れれば終了コード 3 で止まり、残りの組に進まない）→ 残りの 5 組（q5_p・q3_o・q3_p・q7_o・q7_p）→ provenance。
- 見込み（MAC の値は §6）: selftest と変異は Mac でそれぞれ約 23 分。本計算は `results/timing.json`（Mac で作った見積もり）で約 10.7 時間、上側で約 16 時間（1 組は CoAuthor 約 0.4 時間・CS1 約 1.3〜1.5 時間。S0 の段と、列で反復の回数が変わる分は入っていない）。金曜の夜に始めれば週末のうちに終わる見込み。
- 見積もりを大きく超えても途中で止めない。止まったように見えるときは CPU の使用率を見るだけにして、研究者に報告する（条件 D6）。`summary.json` は組とデータごとに書き足されるので、途中で落ちても済んだ組は残る。
- P-Q が外れたら `q_gate.json` の `mismatched` を報告する（境界の丸めの可能性。直さない）。

## 4 終わったら

1. `results/` に `summary.json`（`groups` に 6 組）・`selftest.json`（`mutations` 欄つき）・`check_same_coauthor.json`・`check_same_cs1.json`・`input_manifest_check.json`・`q_gate.json`・`repro_check.json`・`provenance.json`・`timing.json`（Mac で作った・元からある）があり、`summary.json` と `provenance.json` の `run_id` が同じこと。`results/mutations/` は合成だけで、repo に入れてよい。
2. `repro_check.json` の `tau`・`mli` それぞれの `cells`・`mismatched`・`max_rel_diff`・`mismatched_sections` と、`q_gate.json` の `rows`・`mismatched` を報告に写す。
3. `git status` で、変わったのが `experiments/20261107-structure-deficit-test/results/` の下だけであること。それ以外が変わっていれば止めて報告する。
4. コミット（`docs(experiments): structure-deficit-test の本計算の結果（HP Z2） [skip ci]`・本文に `Refs: .steering/20261107-gse-structure-deficit-test/`）して push。PR は出さない。push できなければ `results/` を zip にして Drive の `GSE_ML-run_results` に置く（研究者が手で）。
5. 回した時間（各段の時刻）・JOBS・Python と numpy の版・P-Q と P-REPRO の値・止まった場合の段と赤の内容を、このメモの末尾（§7）に追記してコミットする。

## 5 止まったとき

- manifest・P-D1 が赤: データの取り違えか消失。直らなければ止めて報告。
- selftest・変異が赤: 直さずに、`results/selftest.json` の赤の対照と値を報告する（合成のデータだけ）。P-SAME が「前の試験のコードが走らない」なら `stderr` の末尾を報告する。
- P-Q・P-REPRO が赤: 外れた数と節の名前だけを報告する。
- 本計算が例外: 例外のメッセージに番号や値が出うるので、研究者と Mac のセッションの間だけで扱う。直さずに報告する。

## 6 Mac 側の状態（2026-11-07）

- 枝 `exp/gse-structure-deficit-test`（`exp/gse-tau-mode-candidate` の `05a65021` から）。条件と SEED は `3d7f9f07`、コードと合成の門は `507f81b5`、計算の前のレビューへの対応は `00518580`・`79eb19a9`、変異の門の直しと時間の見積もりは `eb8bdfd9`（判断 11・12）。origin に push 済み（2026-11-07・研究者の確認の後）。HP Z2 では `git fetch origin` の後に、この枝の先頭がこのメモを足したコミット以降であることを確かめる。
- Mac（Python 3.14.4・numpy 2.5.2）の合成の門（`eb8bdfd9`）: selftest 19 対照すべて緑（約 23 分・P-EM2 の目的の減少 0）、変異 16 個すべてが名指しの対照を赤にした（約 23 分）。HP Z2 は前の試験の実測から、どちらも Mac と同じかやや速い見込み。

## 7 HP Z2 での実行の記録（職場の PC のセッションが追記）

記入: 2026-11-10（HP Z2 のセッション）。

- 機械と版: HP Z2・Python 3.11.9・numpy 2.4.4・git-bash・`JOBS=16`。コードは `48137cbe`（`provenance.json` の `git_dirty_paths` は空）。`run_id` は `20261109T122107-1576`（`summary.json` と `provenance.json` で同じ）。終了コード 0。
- 準備: 枝の取り出しの前に、追跡されていない `experiments/20261106-tau-mode-candidate/tables.md`（枝のコミット済みの版と中身が違う）が取り出しを妨げたので、消さずに repo の外 `~/gse-untracked-backup/20261106-tau-mode-candidate/tables.md.local` に移した。AC のスリープ・休止は 0、C: の空きは 230 GB。
- 各段の時刻（2026-11-09 開始。結果のファイルと書き手ごとの値の pkl の更新時刻から）:
  - 開始 12:21:07 → manifest の照合・門の selftest・P-SAME（CoAuthor・CS1）12:21
  - selftest（合成・19 対照）すべて緑 〜12:37 → 変異 16 個すべてが名指しの対照を赤にした 12:52 → P-Q 12:52
  - q5_o: CoAuthor 13:19・CS1 14:58 → P-REPRO 14:58
  - q5_p: 15:33・17:08 / q3_o: 17:44・19:10 / q3_p: 19:42・21:26 / q7_o: 21:50・23:02 / q7_p: 23:31・2026-11-10 01:01
  - provenance と終了 2026-11-10 01:01:39（全体で約 12 時間 40 分）
- P-Q（`q_gate.json`）: coauthor `rows` 588227・`mismatched` 0、cs1 `rows` 2794277・`mismatched` 0。
- P-REPRO（`repro_check.json`・`tolerance_rel` 1e-09）: tau `cells` 6741・`mismatched` 0・`max_rel_diff` 0.0・`mismatched_sections` []、mli `cells` 1363・`mismatched` 0・`max_rel_diff` 0.0・`mismatched_sections` []。
- 止まった段・赤: なし。
- 結果は `51ab4d46` で push 済み（`results/` の下だけ。`results/mutations/` を含む）。書き手ごとの値の pkl 12 個は `~/gse-public-data/landscape/` にあり、開いていない・repo に入れていない。`summary.json` は `run_id` と `groups` の 6 組の名前の確かめまでで、値は読んでいない。
