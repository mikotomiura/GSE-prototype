# 環境

- macOS（Darwin 27.0.0・Apple Silicon）・python3（標準ライブラリだけ・`-I` で実行）。
- `gse-replay` は回さない。C0 の停滞の始まりは、停滞の分解の中間に入っている値（`gse-replay` SHA-256 `26cae610383fb6de01651cc904895efa72a691c3dd1e27689a14a4ca51c33bb3`・HMM_VERSION 0.5.0・p1-episode 1.2.0 の既定・極 baseline）を使う。
- 停滞の分解の `types_core.py`・`o1/analyze_o1.py` と、T2 の `analyze_item2.py` を読み込んで使う（SHA-256 は `results/provenance.json`）。
- 乱数を使わない（SEED なし）。
