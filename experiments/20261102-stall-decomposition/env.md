# 環境

- macOS（Darwin 27.0.0・Apple Silicon）・python3（標準ライブラリだけ・`-I` で実行）。
- `gse-replay`: T2（`../20261101-klicke-early-stall-trigger/env.md`）で作ったリリースビルド。SHA-256 `26cae610383fb6de01651cc904895efa72a691c3dd1e27689a14a4ca51c33bb3`（`run.sh` が照合する）。HMM_VERSION 0.5.0。停滞の始まりのパラメータは `src-tauri/prereg/p1-episode.json`（1.2.0・frozen）の既定（SHA-256 は `o1/results/provenance.json`）。
- 公開データの側は俯瞰の `analyze_landscape.py` と T2 の `analyze_item2.py` を読み込んで使う（SHA-256 は各 `provenance.json`）。
