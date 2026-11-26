# env — 背景のステージの机上の検査・相対のタイミングの写像（案 D）

前の 6 回と同じ機械・版・`gse-replay` のビルド・仮想環境で回す（`.steering/20261122-rhythm-stage-relative-timing/design.md`）。所要の見積もりは design §4 にある（使い捨ての試作・P 40 の実測から）。
- 下見 0（`--ceiling`）は 2 段で数分。
- `go` の段ごとに約 2〜2.5 時間（下見 1 が 30〜45 分、スモークが約 5 分、本番が 1.3〜1.7 時間、ほかに各回の自己検査）。切り分けの読み（`--split`）と並べる表（`--compare`）は無い。

下見 1 と本番の前には、`gh run list` と `Get-CimInstance Win32_Process` を見て notes に記録する（G-GEAR は self-hosted の Windows CI の runner を兼ねる）。同じ入れ物で `run.sh` を 2 本同時に回さない（`work-selftest/`・`work-*`・`results/.partial-*` を共有し、排他の仕組みは無い）。

| 項目 | 値 |
|---|---|
| OS | Windows 11（10.0.26300）・G-GEAR |
| Python | 3.11.9。パッケージは `requirements.txt`（EH1 第 5 回と同じ版。numpy 2.4.6・scipy 1.17.1・scikit-learn 1.9.1・threadpoolctl 3.7.0 ほか）。版は `provenance.json` に記録する |
| gse-replay | 下見 0 は使わない。下見 1 以降は EH1 と同じビルド `C:/wt/_target-portrait-eh1/release/gse-replay.exe`（SHA-256 `71d09dab44526f2322a05833ae1a0fb33ffcc4908bfba796258276f083d78986`・`HMM_VERSION` 0.5.0）を `GSE_REPLAY` で渡す。`run.sh` が SHA-256 を照らし、違えば止まる |
| 実行ごとの記録 | `results/ceiling/provenance.json`・`results/<段>/<mode>/provenance.json`（`capabilities.json` も）。欄: git のコミット・計器の汚れ（`results/` は数えない）・`config.json` の SHA-256・`gse-replay` の SHA-256・seed・world と段・パッケージの版・並列の数 |

- 実行: `PYTHON=C:/wt/portrait-eh1-round3/experiments/20261010-portrait-eh1-round3/.venv/Scripts/python bash run.sh --ceiling [--jobs N]`。下見 1 以降は `GSE_REPLAY=C:/wt/_target-portrait-eh1/release/gse-replay.exe` も渡す（`bash run.sh --pilot | --smoke | --main --step <段>`）。自己検査だけなら `bash run.sh --selftest`（`GSE_REPLAY` を渡すと gse-replay の因果性の検査も回る）、変異は `bash run.sh --mutants`。
- 並列: 結果は並列の数に依らない（分類器の `random_state` を固定し、早期停止を使わない。`GroupKFold` は乱数を使わない）。
