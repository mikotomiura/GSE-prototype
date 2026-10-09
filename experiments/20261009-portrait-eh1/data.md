# data — EH1 of the portrait

入力はすべて**合成**である。実在の人の打鍵・gse-dataset のログは使わない。

| 項目 | 値 |
|---|---|
| 生成器 | `scripts/gen_sessions.py`（`config.json` の `segments` = world v1・`segments_v2` = world v2） |
| seed | `SEED` = 20261009（区間・打鍵・セッションの鍵・ブートストラップ・並べ替えはここから派生） |
| 集合 | P 240・O 40 組・J 40・D（並べ替え 20 組・終点違い 20 組・観測なし 5・打ち続け 5・スリープ 5） |
| 置き場所 | `work-<world>/`（`.gitignore`）。NDJSON（key 行と meta 行だけ）・ラベル（`labels/*.npz`）・`gse-replay` の出力から抜いた秒ごとの F 系列（`feat/*.npz`）。**コミットしない** |
| 再生成 | `bash run.sh --world v1`・`bash run.sh --world v2`（同じ seed から同じ記録ができる） |

- `gse-replay` に渡す NDJSON の `meta.capabilities` は `key`・`session_meta`・`session_start` を `unconditional` と宣言する（合成なので、宣言どおりに行がある）。`run.sh` の Step 0（`capabilities_gate.py --require key`）はこれで通す。
- 停滞のラベルは NDJSON に書かず、別ファイル（`labels/*.npz` の `seg`）に置く。`gse-replay` はラベルを見ない。
