# env — 背景のステージの机上の検査

| 項目 | 値 |
|---|---|
| OS | Windows 11（10.0.26300）・G-GEAR（self-hosted の Windows CI の runner を兼ねる） |
| Python | 3.11.9。パッケージは `requirements.txt`（EH1 第 5 回と同じ版。numpy 2.4.6・scipy 1.17.1・scikit-learn 1.9.1 ほか） |
| gse-replay | 下見 0 は使わない（基準のモデルは打鍵の時刻だけから作る）。本番は EH1 と同じビルド `C:/wt/_target-portrait-eh1/release/gse-replay.exe`（SHA-256 `71d09dab44526f2322a05833ae1a0fb33ffcc4908bfba796258276f083d78986`・`HMM_VERSION` 0.5.0）を `GSE_REPLAY` で渡す（design §1.1） |
| 実行ごとの記録 | `results/<mode>/provenance.json`（git のコミット・計器の汚れ・`config.json` の SHA-256・`gse-replay` のパスと SHA-256・seed・world・パッケージの版・並列の数）と `capabilities.json`（入力の能力の門） |

- 仮想環境は `.venv/`（`.gitignore`）。下見 0 は EH1 第 3 回の `.venv`（同じ `requirements.txt`・`pip freeze` が一致することを 2026-10-12 に確かめた）を `PYTHON` で渡した。新しく作るなら `python -m venv .venv` → `.venv/Scripts/python -m pip install -r requirements.txt`。
- 実行: `PYTHON=C:/wt/portrait-eh1-round3/experiments/20261010-portrait-eh1-round3/.venv/Scripts/python bash run.sh --ceiling [--jobs N]`。下見 1 以降は `GSE_REPLAY=C:/wt/_target-portrait-eh1/release/gse-replay.exe` も渡す（`bash run.sh --pilot | --smoke | --main --jobs 16`）。本番は self-hosted の CI が走っていない時に回す（design §4）。
- 並列: 結果は並列の数に依らない（分類器の `random_state` を固定し、早期停止を使わない。`GroupKFold` は乱数を使わない）。
