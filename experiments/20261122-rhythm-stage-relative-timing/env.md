# env — 背景のステージの机上の検査・揺れの形を分けた world（倍率だけ・漂いだけ）

前の 5 回と同じ機械・版・`gse-replay` のビルド・仮想環境で回す（`.steering/20261015-rhythm-stage-speed-shape-world/design.md`）。所要の見積もりは design §4 にある。
- 下見 0 は 4 段で約 10 分。
- `go` の段ごとに約 13 時間（下見 1 が約 4.8 時間、スモークが約 0.3 時間、本番が約 5 時間、読みが約 3.2 時間）。

下見 1 と本番の前には、`gh run list` と `Get-CimInstance Win32_Process` を見て notes に記録する。同じ機械の `a4_keytar` と並べて回すことは研究者が認めた（判断 5）。

| 項目 | 値 |
|---|---|
| OS | Windows 11（10.0.26300）・G-GEAR（self-hosted の Windows CI の runner を兼ねる） |
| Python | 3.11.9。パッケージは `requirements.txt`（EH1 第 5 回と同じ版。numpy 2.4.6・scipy 1.17.1・scikit-learn 1.9.1 ほか）。`split.py` は版を `config.json` の `split.versions` と照らし、違えば止まる |
| gse-replay | 下見 0 は使わない。下見 1 以降は EH1 と同じビルド `C:/wt/_target-portrait-eh1/release/gse-replay.exe`（SHA-256 `71d09dab44526f2322a05833ae1a0fb33ffcc4908bfba796258276f083d78986`・`HMM_VERSION` 0.5.0）を `GSE_REPLAY` で渡す |
| 実行ごとの記録 | 次の 2 つ（`provenance.json` の欄: git のコミット・計器の汚れ（`results/` は数えない）・`config.json` の SHA-256・`gse-replay` の SHA-256・seed・world と段と c・パッケージの版・並列の数）。<br>・`results/ceiling/provenance.json`・`results/<段>/<mode>/provenance.json`（`capabilities.json` も）<br>・`results/<段>/split/provenance.json`（読み） |

- 実行: `PYTHON=C:/wt/portrait-eh1-round3/experiments/20261010-portrait-eh1-round3/.venv/Scripts/python bash run.sh --ceiling [--jobs N]`。下見 1 以降は `GSE_REPLAY=C:/wt/_target-portrait-eh1/release/gse-replay.exe` も渡す（`bash run.sh --pilot | --smoke | --main | --split --step <段> --jobs 12`）。並べる表は `bash run.sh --compare`。
- 並列: 結果は並列の数に依らない（分類器の `random_state` を固定し、早期停止を使わない。`GroupKFold` は乱数を使わない）。
