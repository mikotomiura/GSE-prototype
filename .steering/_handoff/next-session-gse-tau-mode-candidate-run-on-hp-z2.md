# 引き継ぎ —— τ の候補に最頻値を足す試験の本計算を、職場の HP Z2 で回す

> 作成: 2026-11-06（Mac のセッション）。このメモを一次資料にしない。条件は `experiments/20261106-tau-mode-candidate/conditions.md`（末尾に判断 10 の「条件の後の変更」）、判断は `.steering/20261106-gse-tau-mode-candidate/decisions.md`（判断 1〜11）。下敷きは前の試験の `next-session-gse-timeseries-tau-extend-run-on-hp-z2.md`（§7 に前の試験の HP Z2 での実行の記録）。

## 0 入口の文（職場の PC の Claude Code に最初に打ち込む）

```
GSE-prototype の枝 exp/gse-tau-mode-candidate を取り出し、.steering/_handoff/next-session-gse-tau-mode-candidate-run-on-hp-z2.md を読んで、τ の候補に最頻値を足す試験の run.sh をこの PC で回し、結果を枝に push してください。条件とコードは変えず、門が赤なら直さずに止めて報告してください。入力のデータは前の試験（timeseries-tau-extend）で使ったものをそのまま使います。
```

## 1 やること（これだけ）

この PC では `run.sh` を回して結果を持ち帰るだけにする。notes・読み・レビューは Mac のセッションが行う。

- 条件・コードを変えない。門（manifest・P-D1・selftest・変異・P-REPRO）が赤なら、直さずに止めて、何が赤かだけを報告する。
- 結果の値を読んで解釈しない（`results/summary.json` を開くのは、ファイルができたかと `run_id` の確かめまで。`repro_check.json` は外れた数と節の名前を見てよい）。
- 次の 2 つは repo の外に書かれる。開かない。repo に入れない。
  - `~/gse-public-data/landscape/tau_mode_candidate_writer_values.*.json` と同じ名前の `.pkl`（書き手ごとの値・pkl は集計の前に書く控え）
  - `~/gse-public-data/landscape/tau_mode_candidate_pool_params.*.npz`（共通の母数・判断 6。次の試験で使うかもしれないので消さない）
- 前の試験の書き手ごとの値 `timeseries_tau_extend_writer_values.*.json` も消さない・開かない。
- CoAuthor・CS1 の記録も値も、Codex を含む外部の LLM に送らない。

## 2 準備

1. 前の試験と同じ機械・同じ版で回す（P-REPRO は同じ版でないと照らせない）。前の試験の記録: Python 3.11.9（`python`）・numpy 2.4.4・git-bash。`python --version`・`python -c "import numpy;print(numpy.__version__)"` で確かめ、違えば止めて報告する。
2. コード: 前の試験で使った clone で `git fetch origin && git checkout exp/gse-tau-mode-candidate`（Mac のコミットは §6）。`run.sh`・`mutate.sh` が LF であること（ディレクトリの `.gitattributes` で固定）。
   - 前の試験のディレクトリ `experiments/20261104-timeseries-tau-extend/`（`scripts/` と `results/summary.json`）もこの枝にある。P-SAME は前の試験の `scripts/ml.py` を別のプロセスで呼び、P-REPRO は前の試験の `results/summary.json` と照らす。どちらも変えない。P-SUBSET が呼ぶ `experiments/20261104-coauthor-ml-improve/scripts/` も同じ。
3. データ: 前の試験と同じ `C:/Users/SDS02/gse-public-data`（以下 `DATA_DIR`）と manifest `C:/Users/SDS02/Desktop/GSE_ML_run/input_manifest.json`。manifest の SHA-256 は `e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406`（run.sh が照らす）。
4. スリープ: AC のスリープ・休止が 0 のままかを確かめる。
5. 空き容量: 共通の母数の npz は 2 つ合わせて数 MB の見込み（書き手 28 人 × 4 構造で、いちばん大きい ar3 の C が 3 × 26 × 26 の数 2 つ分）。`DATA_DIR` のドライブに 1 GB 以上の空きがあることを確かめる。

## 3 回す

git-bash で:

```bash
cd <repo>/experiments/20261106-tau-mode-candidate
PYTHON=python DATA_DIR="C:/Users/SDS02/gse-public-data" \
INPUT_MANIFEST="C:/Users/SDS02/Desktop/GSE_ML_run/input_manifest.json" \
INPUT_MANIFEST_SHA256=e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406 \
JOBS=16 bash run.sh 2>&1 | tee "$DATA_DIR/tau_mode_candidate_run.log"; echo "exit=${PIPESTATUS[0]}"
```

- run.sh・mutate.sh は Python を `-I -X utf8` で呼ぶ。`JOBS=16`（各プロセス 1 スレッド）。
- 中身: manifest の照合 → 変換と門の selftest（`repro_check.py --selftest` を含む）→ P-D1 の門 2 つ → selftest（合成・26 対照）→ 変異 23 個（合成）→ 本計算（CoAuthor → CS1・EM だけ）→ provenance → P-REPRO（`results/repro_check.json`）。
- 見込み: selftest は Mac で 1129 秒（約 19 分・26 対照）。変異 23 個は Mac で 3000 秒（約 50 分）。HP Z2 は前の試験で Mac よりやや速かったが、同じ程度と見ておく。本計算は前の試験の HP Z2 の実測（約 1 時間 55 分）に、足した計算（上側に見て約 1.5 分）を足した約 1.9 時間（`results/timing.json`）。合わせて約 3 時間を見込む。
- 見積もりを大きく超えても（例えば本計算が 4 時間を超えても）途中で止めない。止まったように見えるときは CPU の使用率を見るだけにして、研究者に報告する（条件 D6）。
- 最後の P-REPRO が外れると終了コードは 3 になる（それより前の門が赤なら `set -e` で止まり 1 か 3）。

## 4 終わったら

1. `results/` に `summary.json`・`selftest.json`（`mutations` 欄つき）・`check_same_coauthor.json`・`check_same_cs1.json`・`input_manifest_check.json`・`provenance.json`・`repro_check.json`・`timing.json`（Mac の合成・元からある）があり、`summary.json` と `provenance.json` の `run_id` が同じこと。`results/mutations/` は変異のログで、repo に入れてよい（合成だけ）。
2. `repro_check.json` の `passed`・`cells`・`mismatched`・`max_rel_diff`・`mismatched_sections` を報告に写す（書き手の値ではない）。`passed` が false なら、結果はコミットしてよいが「P-REPRO が外れた」と報告の頭に書く（Mac で原因を調べる・notes に使わない）。
3. `provenance.json` の `pool_params_file_sha256` に 2 つの値（coauthor・cs1）が入っていることを確かめる（null なら npz が書けていない。報告する）。
4. `git status` で、変わったのが `experiments/20261106-tau-mode-candidate/results/` の下だけであること。それ以外が変わっていれば止めて報告する。
5. コミット（`docs(experiments): tau-mode-candidate の本計算の結果（HP Z2） [skip ci]`・本文に `Refs: .steering/20261106-gse-tau-mode-candidate/`）して push。PR は出さない。push できなければ `results/` を zip にして Drive の `GSE_ML-run_results` に置く（研究者が手で）。
6. 回した時間（各段の時刻）・JOBS・Python と numpy の版・P-REPRO の値・止まった場合の段と赤の内容を、このメモの末尾（§7）に追記してコミットする。

## 5 止まったとき

- manifest・P-D1 が赤: データの取り違えか消失。直らなければ止めて報告。
- selftest・変異が赤: 直さずに、`results/selftest.json` の赤の対照と値を報告する（合成のデータだけ）。P-SAME・P-SUBSET が「前の試験のコードが走らない」なら、`stderr` の末尾を報告する。
- 本計算が例外: 例外のメッセージに番号や値が出うるので、研究者と Mac のセッションの間だけで扱う。直さずに報告する。とくに「NaN」を含む例外（`差に NaN がある`・`NaN を JSON に書こうとした`・`確率 0 の前に非有限の対数確率がある`）は、最頻値の扱いの穴を示すので、段と文だけを報告する。

## 6 Mac 側の状態（2026-11-06）

- 枝 `exp/gse-tau-mode-candidate`（前の試験の枝の先端 `2911f940` から）。条件は `ac7e79dd`、コードと合成の門は `18792a84`。push は研究者の手元で行う（この枝が origin に上がっていることを、HP Z2 で取り出す前に研究者が確かめる）。
- Mac（Python 3.14.4・numpy 2.5.2）で、合成の selftest は 26 対照すべて緑（1129 秒・run_id `mac-20261106T190541`）、変異 23 個はすべて当たり（終了コード 3・名指しの対照が赤・3000 秒）。Mac の結果のファイルは repo に入れていない（HP Z2 の run.sh が同じものを `results/` に書く）。
- 計算の前の code-reviewer の指摘と直し: HIGH なし、MEDIUM 4 件を判断 11 で直した（P-AB を em_rows の書き手ごとの差で照らす・P-NEGINF で押下の上書きと頭の記号の道を試す・変異 m27 を足す・書き手ごとの値を JSON の前に pickle で控える・repro_check の ±∞ の比の穴を塞ぐ）。直していないのは timing.py の区間の数え上げだけ（効きは小さい）。

## 7 HP Z2 での実行の記録（職場の PC のセッションが追記）

- 実行: 2026-11-06（HP Z2・git-bash）。`run_id` `20261106T205818-149`（`summary.json` と `provenance.json` で一致）。終了コード 0。
- 版: Python 3.11.9（`python`）・numpy 2.4.4（前の試験と同じ）。JOBS=16。AC のスリープ・休止は 0 のままだった。C: の空きは 231 GB。
- データ: 前の試験と同じ `C:/Users/SDS02/gse-public-data`。manifest の SHA-256 は一致。
- 各段の時刻（ログの時刻とファイルの更新時刻から）:
  - 開始 20:58:18 → manifest の照合・P-D1 の門 2 つ 20:58〜20:58:39（緑）
  - selftest（26 対照・`repro_check.py --selftest` を含む）20:58〜21:08 頃（605.7 秒・`all_passed` true）
  - 変異 23 個 21:08〜21:34:15（約 26 分・23 個すべて `hit` true・終了コード 3）
  - 本計算 21:34〜23:27（CoAuthor は 22:03 まで・CS1 は 23:27 まで。合わせて約 1 時間 53 分）
  - provenance・P-REPRO 23:27:20 → 終了 23:27:20
- P-REPRO（`results/repro_check.json`）: `passed` true・`cells` 72332・`mismatched` 0・`max_rel_diff` 0.0・`mismatched_sections` []（`tolerance_rel` 1e-09）。
- `provenance.json` の `pool_params_file_sha256`: coauthor・cs1 の 2 つとも値が入っている（null なし）。npz は `DATA_DIR/landscape/` に 2 つ（約 2.2 MB・2.0 MB）。
- 止まった段・赤: なし。
- 結果のコミット `cdc1f0f7`（push 済み・PR は出していない）。`results/mutations/*.log` は .gitignore（`*.log`）で除かれ、`.exit` と `.json` だけが入った。
