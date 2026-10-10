# data — EH1 round 5 of the portrait

入力はすべて**合成**である。実在の人の打鍵・gse-dataset のログは使わない。

| 項目 | 値 |
|---|---|
| 生成器 | `scripts/gen_sessions.py`（第 1〜4 回と同じ。world v2 = `config.json` の `segments_v2`） |
| seed | `SEED` = 20261009（区間・打鍵・セッションの鍵・ブートストラップ・並べ替え・PC-cal・形の PC・先読みの PC の抽選はここから派生）。生成器と seed が第 2〜4 回と同じなので、本番の world v2 の記録は第 2〜4 回と同じになる。本番用の下見（`--pilot`）は `SEED + 1` = 20261010・P 40 本。反復用の下見（`--pilot-replicate`）は `SEED + 2` = 20261011・P 240 本。反復（`--replicate`）の `r` 回目は `SEED + 100 + r`（20261109〜20261128）・P 240 本（design §3.9・§3.10）。下見と反復では、ほかの集合はスモークの大きさで作り、使わない（P の各セッションは `derive_rng(seed, "P", i)` から作られ、ほかの集合の大きさに依らない） |
| 使う集合 | P だけ。生成器はほかの集合（O・J・D・Jsh）も作るが、第 5 回の `checks.py` は使わない（記録を第 2 回と揃えるため、生成器は変えていない） |
| 置き場所 | `work-v2/`・`work-v2-smoke/`・`work-pilot-v2/`・`work-pilot-replicate/`・`work-replicate/`（`.gitignore`。反復の work は回ごとに作り直して消す）。NDJSON（meta・session_start・session_meta・key の 4 種の行だけ）・ラベル（`labels/*.npz`）・`gse-replay` の出力から抜いた秒ごとの F 系列（`feat/*.npz`）。コミットしない |
| 再生成 | `bash run.sh`（本番）・`bash run.sh --smoke`・`bash run.sh --pilot`・`bash run.sh --pilot-replicate`・`bash run.sh --replicate` |

- `gse-replay` に渡す NDJSON の `meta.capabilities` は `key`・`session_meta`・`session_start` を `unconditional` と宣言する（合成なので、宣言どおりに行がある）。`run.sh` の Step 0（`capabilities_gate.py --require key`）はこれで通す。
- 停滞のラベルは NDJSON に書かず、別ファイル（`labels/*.npz` の `seg`）に置く。`gse-replay` はラベルを見ない。ラベルを読むのは `checks.py` と、E1-1 の例外として宣言した PC-cal・形の PC・先読みの PC・神託だけである（design §1.4）。
