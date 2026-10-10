# env — EH1 round 5 of the portrait

| 項目 | 値 |
|---|---|
| OS | Windows 11（10.0.26300）・16 論理コア・メモリ 31 GB（G-GEAR） |
| Python | 3.11.9。パッケージは `requirements.txt`（numpy 2.4.6・scipy 1.17.1・scikit-learn 1.9.1・pillow 12.3.0 ほか。第 2 回と同じ） |
| gse-replay | 第 1〜4 回と同じビルドを `GSE_REPLAY` で渡す（SHA-256 `71d09dab44526f2322a05833ae1a0fb33ffcc4908bfba796258276f083d78986`・`HMM_VERSION` = 0.5.0）。このブランチの `src-tauri/` は main（`72b6aca7`）のままで、第 2 回の木から `src-tauri/src/analysis/feat_offline/idle_trim.rs` などが足されている。同じビルドを使うのは、F の系列を第 2〜4 回と揃えるためである。本番の値は `results/v2/provenance.json` を正とする |
| 実行ごとの記録 | `results/v2/provenance.json`（git のコミット・バイナリの SHA-256・`HMM_VERSION`・パッケージの版・seed・並列の数）。反復は各 `results/replicate/replicate_<r>.json` に seed・対照と λ・`config.json` の SHA-256・計器のコミットと汚れを書く |

- 仮想環境は `.venv/`（`.gitignore`）。第 4・5 回は第 3 回の `.venv`（同じ `requirements.txt`）を `PYTHON` で渡した。`python -m venv .venv` → `.venv/Scripts/python -m pip install -r requirements.txt`。
- 実行: `GSE_REPLAY=C:/wt/_target-portrait-eh1/release/gse-replay.exe bash run.sh [--smoke] [--pilot | --pilot-replicate | --replicate] [--jobs N]`。
- 並列: `run.sh --jobs N` → `checks.py --jobs N`（既定 8。第 2 回の本番で 16 はメモリが尽きかけた。第 3 回は 6 で使えるメモリの最低が約 4.1 GB）。結果は並列の数に依らないように作ってある（seed はセッションと組から派生させ、分類器は `random_state` を固定し、早期停止を使わない）。
