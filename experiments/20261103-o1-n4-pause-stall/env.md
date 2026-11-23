# 環境

- macOS（Darwin 27.0.0・Apple Silicon）・python3（`-I` で実行）・numpy 2.5.2（混合の EM だけに使う。c1c2c6 は標準ライブラリだけだった）。
- `gse-unpack` SHA-256 `c9475ded4858b0336c21754839f1389e2169284dea89d3402a87b841a4fdc282`・`gse-replay` SHA-256 `26cae610383fb6de01651cc904895efa72a691c3dd1e27689a14a4ca51c33bb3`（HMM_VERSION 0.5.0・p1-episode 1.2.0 の既定・極 baseline）。
- 乱数: `SEED`（記号の並べ替えと混合の初期値）。陽性対照の合成の標本は固定の種 20261103。
