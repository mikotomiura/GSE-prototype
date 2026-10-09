# env — EH1 of the portrait

| 項目 | 値 |
|---|---|
| OS | Windows 11（10.0.26300）・16 論理コア |
| Python | 3.11.9。パッケージは `requirements.txt`（numpy 2.4.6・scipy 1.17.1・scikit-learn 1.9.1・pillow 12.3.0 ほか） |
| Rust | rustc 1.98.1・cargo 1.98.1。`src-tauri/Cargo.lock`（SHA-256 の先頭 `fdb24cda2ef40acd`） |
| gse-replay | `run.sh` が `cargo build --release --bin gse-replay` でビルドする（target は worktree の外）。`src-tauri/` はこのブランチで変えていない（`82859a27` の親の木のまま）。計器を作った機械でのビルドは SHA-256 `fead27428148c64a28f36cf88a51c32224ac57674cb6e0683cf087b2dd3f04c9`。`HMM_VERSION` = 0.5.0。⚠️ 本番は Windows の別の機器で回す（判断 5）ので、本番の値は `results/<world>/provenance.json` を正とする |
| 実行ごとの記録 | `results/<world>/provenance.json`（git のコミット・バイナリの SHA-256・`HMM_VERSION`・パッケージの版） |

- 仮想環境は `.venv/`（`.gitignore`）。`python -m venv .venv` → `.venv/Scripts/python -m pip install -r requirements.txt`。
- 並列: `checks.py --jobs 16`（セッションごとの実行は ProcessPool・分類器は joblib。各ジョブは 1 スレッド）。結果が並列の数に依らないように作った（seed はセッションと組から派生させ、分類器は `random_state` を固定し、早期停止を使わない）。⚠️ 並列の数を変えて同じ結果になるかは確かめていない。
