# 環境

- macOS（Darwin 27.0.0・Apple Silicon）・python3 3.14.4（`-I` で実行）・numpy 2.5.2（ロジスティック回帰と n4 の混合の EM）。scikit-learn は使わない（判断 6）。
- `gse-unpack` SHA-256 `c9475ded4858b0336c21754839f1389e2169284dea89d3402a87b841a4fdc282`・`gse-replay` SHA-256 `26cae610383fb6de01651cc904895efa72a691c3dd1e27689a14a4ca51c33bb3`（HMM_VERSION 0.5.0・p1-episode 1.2.0 の既定）。
- 乱数: `SEED`（20261116。無作為の窓・対照の引き方・分割・本の復元抽出）。n4 の混合の初期値も同じ SEED を渡す。記号は n4 の塩。
