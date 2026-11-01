# 設計

- 実験: `experiments/20261101-klicke-early-stall-trigger/`（条件は `conditions.md`）。
- 流れ: 取得（curl・SHA-256 照合）→ 1 本ずつ zip から読んで変換（`scripts/convert_klicke.py`）→ `gse-replay`（既定）→ `add_feat.py` → `gse-replay --features` → 読む項目だけ残す → 解析（`scripts/analyze_item2.py`）。
- 中間は `~/gse-public-data/klicke/work/`（repo の外）。1 本ずつ処理して大きいファイルを消す（ディスクの空きが少ない）。
- 検証: θ と onset の Python 再現を replay と全件照合する。変換の自己検査（合成の小さな CSV）。
- 計算は Mac（CoAuthor と同じ規模・G-GEAR は使わない）。
