# env —— 揺れの world の `res=sub` の赤の原因の切り分け

揺れの world（`experiments/20261014-rhythm-stage-speed-confound-world/`）と同じ機械・版・`gse-replay` のビルド・仮想環境で回す（`.steering/20261015-rhythm-stage-speed-cause-split/design.md` §1.1）。

| 項目 | 値 |
|---|---|
| OS | Windows 11（10.0.26300）・G-GEAR（self-hosted の Windows CI の runner を兼ねる） |
| Python | 3.11.9。パッケージは `requirements.txt`（揺れの world と同じ版・scikit-learn 1.9.1） |
| gse-replay | `C:/wt/_target-portrait-eh1/release/gse-replay.exe`（SHA-256 `71d09dab44526f2322a05833ae1a0fb33ffcc4908bfba796258276f083d78986`・`HMM_VERSION` 0.5.0）を `GSE_REPLAY` で渡す。`run.sh` が SHA-256 と `HMM_VERSION` を `config.json` と照合する |
| 実行ごとの記録 | `results/<段>/<mode>/provenance.json`（git のコミット・入れ物の汚れ・`config.json` の SHA-256・照合した揺れの world のファイルの SHA-256・`gse-replay` の SHA-256・seed・パッケージの版・並列の数）と `capabilities.json` |

- 実行: `PYTHON=C:/wt/portrait-eh1-round3/experiments/20261010-portrait-eh1-round3/.venv/Scripts/python GSE_REPLAY=C:/wt/_target-portrait-eh1/release/gse-replay.exe bash run.sh --smoke | --main --step <c100|c200> --jobs 12`。自己検査だけなら `bash run.sh --selftest`（`GSE_REPLAY` は要らない）。
- 回す前に `gh run list` で CI が走っていないこと、`Get-CimInstance Win32_Process` で同じ機械の別の重い処理が無いことを確かめ、notes に書く（design §4）。
- 並列: 結果は並列の数に依らない（揺れの world と同じ当てはめ・`GroupKFold` は乱数を使わない・`KBinsDiscretizer` は `subsample=None` で乱数を使わない）。
- 揺れの world のファイルの SHA-256 は、この機械の作業ツリーのバイト（改行は LF のまま）で取った。
