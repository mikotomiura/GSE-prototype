# data — EH1 round 3 of the portrait

入力はすべて**合成**である。実在の人の打鍵・gse-dataset のログは使わない。

| 項目 | 値 |
|---|---|
| 生成器 | `scripts/gen_sessions.py`（第 1 回・第 2 回と同じ。world v2 = `config.json` の `segments_v2`） |
| seed | `SEED` = 20261009（区間・打鍵・セッションの鍵・ブートストラップ・並べ替え・PC-cal の抽選はここから派生）。生成器と seed が第 2 回と同じなので、world v2 の記録は第 2 回と同じになる。下見（`--pilot`・design §3.9）だけは `SEED + 1` = 20261010・P 40 本（ほかの集合はスモークの大きさ・使わない） |
| 使う集合 | P だけ（240 本）。生成器はほかの集合（O・J・D・Jsh）も作るが、第 3 回の `checks.py` は使わない（記録を第 2 回と揃えるため、生成器は変えていない） |
| 置き場所 | `work-v2/`・`work-v2-smoke/`・`work-pilot-v2/`（`.gitignore`）。NDJSON（meta・session_start・session_meta・key の 4 種の行だけ）・ラベル（`labels/*.npz`）・`gse-replay` の出力から抜いた秒ごとの F 系列（`feat/*.npz`）。コミットしない |
| 再生成 | `bash run.sh`（本番）・`bash run.sh --smoke`・`bash run.sh --pilot` |

- `gse-replay` に渡す NDJSON の `meta.capabilities` は `key`・`session_meta`・`session_start` を `unconditional` と宣言する（合成なので、宣言どおりに行がある）。`run.sh` の Step 0（`capabilities_gate.py --require key`）はこれで通す。
- 停滞のラベルは NDJSON に書かず、別ファイル（`labels/*.npz` の `seg`）に置く。`gse-replay` はラベルを見ない。ラベルを読むのは `checks.py` と、E1-1 の例外として宣言した PC-cal・神託だけである（design §1.4）。
