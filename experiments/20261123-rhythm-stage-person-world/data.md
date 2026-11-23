# data — 背景のステージの机上の検査・相対のタイミングの写像（案 D）

揺れの形の計器（`experiments/20261015-rhythm-stage-speed-shape-world/data.md`・`1cf9fcb9`）の写しを、このタスクに合わせて直した。変えたのは段・seed・ラベル・候補・読みが無いことだけ（`.steering/20261122-rhythm-stage-relative-timing/design.md` §0）。

入力はすべて**合成**である。実在の人の打鍵・gse-dataset のログは使わない。

| 項目 | 値 |
|---|---|
| 生成器 | `scripts/gen_sessions.py`。揺れの形の生成器（`1cf9fcb9`）を**変えずに**写した。`baseline.py`・`replay_all.py`・`twins.py` も同じ。`selftest.py` が 4 つのファイルを写し元と SHA-256（LF の行末）で照らす（`gen_sessions.py` は `b6e9e0c9…618d0`） |
| world（段） | 2 段（design §1.3）。<br>・`g050`: `--world graded --t 0.5`（中間の world・揺れの形の c = 0 の端と同じ打鍵）。<br>・`f200`: `--world factor --c 2`（倍率だけの world・c = 2。セッションごとの倍率は burst の中の間隔だけに掛かる）。<br>段と world は `config.json` の `ceiling.steps`・`ceiling.worlds` にある。作業の場所の `world.json`（graded は `t`、factor は `c`）を `checks.py`・`ceiling.py` が段と照らし合わせる。`f200` は D_shuffled の跳びを `speed_jumps.json` に書く（記述だけ・factor では 0） |
| seed | `SEED` = 20261122（新しい値・design §9 の 1）。前の回の列（20261020・20261021 ほか）は結果を見ているので使わない。2 段とも同じ値 |
| 下見 0・下見 1・本番 | 下見 0（`--ceiling`）と下見 1（`--pilot --step`）は `SEED + 1` = 20261123・P 240 本。スモーク（`--smoke --step`）は `SEED + 2` = 20261124・P 12 本。本番（`--main --step`）は `SEED` = 20261122・P 240 本。<br>ほかの集合はスモークの大きさで作り使わない。下見 1 以降は `gse-replay`（EH1 のビルド）で秒ごとの F 系列を作る。スモークと本番は双子も作る |
| 使う集合 | P だけ（と、その双子） |
| ラベル | L300 だけ（判断 8） |
| 候補 | 案 D の 2 本（`D-run-hold-sec`・`D-all-hold-sec`）と錨の 4 本（`S-raw-hold-sec`・`S-raw-hold-sub`・`S-rank-hold-sec`・`S-rank-hold-sub`）。対照は PC1・候補ごとの PC-stall と PC0・PC-corr（記述） |
| 基準 | A（主）と A_speed（副）。下見 1 の λ は基準ごとに選ぶ（`pc_stall.lam.<段>.<基準>`・design §1.5） |
| 読むもの | 案 D は押下の時刻（`presses`）と動いていた秒（`active`）だけを読む（`keys`・`f1`・`f4` は読まない。`selftest.py` が `StageInput` の読みで確かめる）。錨は揺れの形と同じ |
| 置き場所 | `work-*/`（`.gitignore`。走り終えると消す）。コミットするのは集計した JSON だけ: `results/ceiling/`・`results/<段>/pilot/`・`results/<段>/main/`（`*-smoke/` は無視）。切り分けの読み（`split`）と並べる表（`compare`）は無い（判断 9） |
| 再生成 | `bash run.sh --ceiling`。続いて `go` の段（`g050` → `f200` の順）ごとに、`--pilot --step <段>` → `--apply-pilot` → `--smoke --step <段>` → `--main --step <段>`。<br>どれも自己検査を先に回す。`GSE_REPLAY` が要る（`env.md`）。<br>下見 1 の後に、この入れ物から `$PYTHON scripts/checks.py --apply-pilot config.json results/<段>/pilot/pilot.json <段>` で λ を書く（`pc_stall.lam.<段>`） |

- 合成の NDJSON も外部の LLM（Codex を含む）に渡さない。
- 自己検査は、写し元の生成器・基準・描画（揺れの形の計器）を SHA-256 で照合してから比べる。写し元の入れ物を変えると自己検査が落ちる。写し元の dir のファイルは読むだけで、`.pyc` を書かない。
- 自己検査の生成は `TEST_SEED` = 7 で、本番の列（`SEED`・`SEED + 1`・`SEED + 2`）を使わない。
- `selftest.py --mutants` は design §3.7 の 7 本の変異を 1 本ずつ入れ、どれも自己検査を落とすことを確かめる。
