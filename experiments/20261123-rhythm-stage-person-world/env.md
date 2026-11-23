# env — 背景のステージの机上の検査・人ごとのリズムの型の world（個人の再識別・個人ごとの読み手）

前のタスク（`experiments/20261122-rhythm-stage-relative-timing/`）と同じ機械・版・`gse-replay` のビルド・仮想環境で回す（`.steering/20261123-rhythm-stage-person-world/design.md`）。所要の見積もりは design §4 にある（推論・段あたり 2.5〜3.5 時間、4 段で 8〜14 時間）。

- 下見 0（`--ceiling`）と下見 1k（`--pilot-k`）は `gse-replay` を使わない。下見 1（`--pilot`）・スモーク・本番は使う。
- 段の順は m049 → m068 → r049 → r068。r の段は、同じ ICC の m の段の下見 1（`results/<m の段>/pilot/pilot.json` の PC-raw の AUC）を k の目標にする。順番は `run.sh` が守らせる（前の段の `results/<段>/main/summary.json` が無いと止まる）。
- 下見 1・本番の前には、`gh run list` と `Get-CimInstance Win32_Process` を見て notes に記録する（G-GEAR は self-hosted の Windows CI の runner を兼ねる）。同じ入れ物で `run.sh` を 2 本同時に回さない（`work-selftest/`・`work-*`・`results/.partial-*` を共有し、排他の仕組みは無い）。計測の run の最中は push だけにし、PR を出さない。

| 項目 | 値 |
|---|---|
| OS | Windows 11（10.0.26300）・G-GEAR |
| Python | 3.11.9。パッケージは `requirements.txt`（前のタスクと同じ版。numpy 2.4.6・scipy 1.17.1・scikit-learn 1.9.1・threadpoolctl 3.7.0 ほか）。版は `provenance.json` に記録する |
| gse-replay | 下見 1 以降は EH1 と同じビルド `C:/wt/_target-portrait-eh1/release/gse-replay.exe`（SHA-256 `71d09dab44526f2322a05833ae1a0fb33ffcc4908bfba796258276f083d78986`・`HMM_VERSION` 0.5.0）を `GSE_REPLAY` で渡す。`run.sh` が SHA-256 を照らし、違えば止まる |
| 実行ごとの記録 | `results/<段>/<mode>/provenance.json`（`capabilities.json` も）。欄: git のコミット・計器の汚れ（`results/` は数えない）・`config.json` の SHA-256・`gse-replay` の SHA-256・seed・段の world と k・パッケージの版・並列の数 |

- 実行（段ごと）: `PYTHON=C:/wt/portrait-eh1-round3/experiments/20261010-portrait-eh1-round3/.venv/Scripts/python bash run.sh --pilot-k --step r049`（r の段だけ）→ `--apply-pilot --step <段>`（k を書く）→ `--ceiling --step <段>` → `GSE_REPLAY=... bash run.sh --pilot --step <段>` → `--apply-pilot --step <段>`（λ を書く）→ `--smoke --step <段>` → `--main --step <段>`。m の段は `--ceiling` から始める。
- 自己検査だけなら `bash run.sh --selftest`（`GSE_REPLAY` を渡すと gse-replay の因果性の検査も回る）、変異は `bash run.sh --mutants`（新しい 14 本と前の 7 本）。
- 並列: 結果は並列の数に依らない（分類器の `random_state` を固定し、早期停止を使わない。分割と並べ替えと bootstrap は `derive_rng(seed, 名前)` から引く）。
