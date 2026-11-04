# 引き継ぎ —— τ の格子を広げる試験の本計算を、職場の HP Z2 で回す

> 作成: 2026-11-05（Mac のセッション）。このメモを一次資料にしない。条件は `experiments/20261104-timeseries-tau-extend/conditions.md`（末尾に判断 6 の「条件の後の変更」）、判断は `.steering/20261104-gse-timeseries-tau-extend/decisions.md`（判断 1〜6）。下敷きは前回の `next-session-gse-coauthor-ml-run-on-hp-z2.md`（§7 に前回の HP Z2 での実行の記録）。

## 0 入口の文（職場の PC の Claude Code に最初に打ち込む）

```
GSE-prototype の枝 exp/gse-timeseries-tau-extend を取り出し、.steering/_handoff/next-session-gse-timeseries-tau-extend-run-on-hp-z2.md を読んで、τ の格子を広げる試験の run.sh をこの PC で回し、結果を枝に push してください。条件とコードは変えず、門が赤なら直さずに止めて報告してください。入力のデータは前回の試験（coauthor-ml-improve）で展開したものをそのまま使います。
```

## 1 やること（これだけ）

この PC では `run.sh` を回して結果を持ち帰るだけにする。notes・読み・レビューは Mac のセッションが行う。

- 条件・コード・格子を変えない。門（manifest・P-D1・selftest・変異・P-REPRO）が赤なら、直さずに止めて、何が赤かだけを報告する。
- 結果の値を読んで解釈しない（`results/summary.json` を開くのは、ファイルができたかと `run_id` の確かめまで。`repro_check.json` は外れたセルの数を見てよい）。
- `~/gse-public-data/landscape/timeseries_tau_extend_writer_values.*.json`（書き手ごとの値）を開かない。repo に入れない。
- CoAuthor・CS1 の記録も値も、Codex を含む外部の LLM に送らない。

## 2 準備

1. 前回と同じ機械・同じ版で回す（P-REPRO は同じ版でないと照らせない）。前回の記録: Python 3.11.9（`python`）・numpy 2.4.4・git-bash。`python --version`・`python -c "import numpy;print(numpy.__version__)"` で確かめ、違えば止めて報告する（版が違うと P-REPRO が外れうる）。
2. コード: 前回 HTTPS で clone した repo で `git fetch origin && git checkout exp/gse-timeseries-tau-extend`（Mac のコミットは §6）。`run.sh`・`mutate.sh` が LF であること（ディレクトリの `.gitattributes` で固定）。
   - 前回の試験のディレクトリ `experiments/20261104-coauthor-ml-improve/`（`scripts/` と `results/summary.json`）もこの枝に入っている。P-SUBSET は前回の `scripts/ml.py` を別のプロセスで呼び、P-REPRO は前回の `results/summary.json` と照らす。どちらも変えない。
3. データ: 前回展開した `C:/Users/SDS02/gse-public-data`（以下 `DATA_DIR`）と manifest `C:/Users/SDS02/Desktop/GSE_ML_run/input_manifest.json` をそのまま使う。manifest の SHA-256 は `e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406`（run.sh が照らす）。消えていれば前回のメモ §2-3・§2-4 のとおり Drive から取り直して展開する。
4. スリープ: 前回は AC のスリープ・休止が元から 0 だった。変わっていないことを確かめる。

## 3 回す

git-bash で:

```bash
cd <repo>/experiments/20261104-timeseries-tau-extend
PYTHON=python DATA_DIR="C:/Users/SDS02/gse-public-data" \
INPUT_MANIFEST="C:/Users/SDS02/Desktop/GSE_ML_run/input_manifest.json" \
INPUT_MANIFEST_SHA256=e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406 \
JOBS=16 bash run.sh 2>&1 | tee "$DATA_DIR/timeseries_tau_extend_run.log"; echo "exit=${PIPESTATUS[0]}"
```

- run.sh・mutate.sh は Python を `-I -X utf8` で呼ぶ。`JOBS=16`（各プロセス 1 スレッド）。
- 中身: manifest の照合 → 変換と門の selftest（`repro_check.py --selftest` を含む）→ P-D1 の門 2 つ → selftest（合成・17 対照）→ 変異 11 個（合成）→ 本計算（CoAuthor → CS1・EM だけ）→ provenance → P-REPRO（`results/repro_check.json`）。
- 見込み（Mac の実測と合成の見積もり・HP Z2 の実測ではない）: selftest は Mac で 11 分・変異は Mac で 18 分（selftest の 6 プロセスの並列は HP Z2 でも同じ）。本計算は前回の HP Z2 の実測に比を掛けて約 1.0 時間、合成の絶対の見積もりで約 1.4 時間（`results/timing.json`）。合わせて 1.5〜2 時間を見込む。
- 見積もりを大きく超えても（例えば本計算が 4 時間を超えても）途中で止めたり格子を変えたりしない。止まったように見えるときは CPU の使用率を見るだけにして、研究者に報告する（conditions D6）。
- 最後の P-REPRO が外れると終了コードは 3 になる（それより前の門が赤なら `set -e` で止まり 1 か 3）。

## 4 終わったら

1. `results/` に `summary.json`・`selftest.json`（`mutations` 欄つき）・`check_same_coauthor.json`・`check_same_cs1.json`・`input_manifest_check.json`・`provenance.json`・`repro_check.json`・`timing.json`（Mac の合成・元からある）があり、`summary.json` と `provenance.json` の `run_id` が同じこと。`results/mutations/` は変異のログで、repo に入れてよい（合成だけ）。
2. `repro_check.json` の `passed`・`cells`・`mismatched`・`max_rel_diff` を報告に写す（値は外れたセルの数と最大の差だけで、書き手の値ではない）。`passed` が false なら、結果はコミットしてよいが「P-REPRO が外れた」と報告の頭に書く（Mac で原因を調べる・notes に使わない）。
3. `git status` で、変わったのが `experiments/20261104-timeseries-tau-extend/results/` の下だけであること。それ以外が変わっていれば止めて報告する。
4. コミット（`docs(experiments): timeseries-tau-extend の本計算の結果（HP Z2） [skip ci]`・本文に `Refs: .steering/20261104-gse-timeseries-tau-extend/`）して push。PR は出さない。push できなければ `results/` を zip にして Drive の `GSE_ML_run` に置く（研究者が手で）。
5. 回した時間（各段の時刻）・JOBS・Python と numpy の版・P-REPRO の 4 つの値・止まった場合の段と赤の内容を、このメモの末尾（§7）に追記してコミットする。

## 5 止まったとき

- manifest・P-D1 が赤: データの取り違えか消失。展開をやり直す。直らなければ止めて報告。
- selftest・変異が赤: 直さずに、`results/selftest.json` の赤の対照と値を報告する（Mac で原因を見る）。P-SUBSET が「前回のコードが走らない」なら、`selftest.json` の `stderr` の末尾を報告する（合成のデータだけなので外に出してよいが、研究者と Mac のセッションの間だけで扱う）。
- 本計算が例外: 例外のメッセージに番号や値が出うるので、研究者と Mac のセッションの間だけで扱う。直さずに報告する。

## 6 Mac 側の状態（2026-11-05）

- 枝 `exp/gse-timeseries-tau-extend`。条件は `eb7a1884`、コードと合成の門は `e2ac9d74`（その後はこのメモの追加だけ）。push は研究者の手元で行う（この枝が origin に上がっていることを、HP Z2 で取り出す前に研究者が確かめる）。
- Mac（Python 3.14.4・numpy 2.5.2）で、合成の selftest 17 対照すべて緑（678 秒）、変異 11 個すべてが名指しの対照を赤にした（終了コード 3・1,055 秒）。P-SUBSET（前回の 6 構造の em_writer と今回の 4 構造の em_writer の重なる 192 セルが完全に一致）も Mac で緑。
- 計算の前の code-reviewer の HIGH 1 件（m11 で落ちる）は直した。残した MEDIUM・LOW は tasklist に書いた。
- このメモの後の作業（Mac）: 結果が戻ったら P-REPRO を確かめ → notes.md（4 つ組・各表・言える範囲・逸脱）→ code-reviewer・/cross-review → push（PR は研究者が確かめてから・`[skip ci]`）。

## 7 HP Z2 での実行の記録（職場の PC のセッションが追記）

（未記入）
