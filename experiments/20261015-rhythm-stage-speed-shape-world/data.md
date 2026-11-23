# data — 背景のステージの机上の検査・揺れの形を分けた world（倍率だけ・漂いだけ）

揺れの world（`experiments/20261014-rhythm-stage-speed-confound-world/data.md`・`7d38df98`）の写しを、このタスクに合わせて直した。変えたのは world・段の名前と値・下見 1 の第 3 の部分・本番の後の読みだけ（`.steering/20261015-rhythm-stage-speed-shape-world/design.md` §0）。

入力はすべて**合成**である。実在の人の打鍵・gse-dataset のログは使わない。

| 項目 | 値 |
|---|---|
| 生成器 | `scripts/gen_sessions.py`。揺れの world の生成器（`7d38df98`・SHA-256 `d391f2fd…353e23`）の写しに、`--world factor --c C` と `--world drift --c C` を足しただけ（design §1.2）。次を `selftest.py` が確かめる（NDJSON と `sessions.json` はバイト、ラベルの npz は配列の中身）。<br>・world v1〜v4・graded の出力が中間の world の生成器と同じ。<br>・confound の出力（`world.json`・`speed_jumps.json` を含む）が揺れの world の生成器と同じ。<br>・`--c 0` の打鍵と区間が `--world graded --t 0.5` と同じ。 |
| world（段） | 区間の設定は `graded_segments(cfg, 0.5)`（揺れの world と同じ）。FLOW と STRUGGLE のバーストの中の打鍵の間隔を `lognormal(ln m + z(τ), σ)` で引く。<br>・倍率だけの world（`factor`）: `z(τ) = c · δ · u`<br>・漂いだけの world（`drift`）: `z(τ) = c · δ · d(⌊τ/1000⌋)`<br>`δ`・`u`・`d` と乱数の流れ `derive_rng(seed, "speed", <組>, i)` は揺れの world と同じで、引く順は world に依らない。段は `f100`・`f200`（factor・c = 1・2）と `d100`・`d200`（drift・c = 1・2）。world は `config.json` の `ceiling.worlds` にある。作業の場所の `world.json` に `{"world": "factor" か "drift", "c": c}` を書き、`checks.py`・`ceiling.py` が段と照らし合わせる。D_shuffled の跳びを `speed_jumps.json` に書く（記述だけ・factor では 0） |
| seed | `SEED` = 20261020（揺れの world と同じ値・design §1.2）。4 段とも同じ値。同じ単位の `u`（factor）と `d` の列（drift）は、揺れの world の同じ単位のものと同じ値になる。打鍵の数が変わるので、区間と打鍵の乱数を引く位置は world と段ごとにずれる |
| 下見 0・下見 1・本番 | 下見 0（`--ceiling`）と下見 1（`--pilot --step`）は `SEED + 1` = 20261021・P 240 本。スモーク（`--smoke --step`）は `SEED + 2` = 20261022・P 12 本。本番（`--main --step`）と読みの作り直し（`--split --step`）は `SEED` = 20261020・P 240 本。<br>ほかの集合はスモークの大きさで作り使わない。下見 1 以降は `gse-replay`（EH1 のビルド）で秒ごとの F 系列を作る。スモークと本番は双子も作る |
| 使う集合 | P だけ（と、その双子） |
| 読むもの | 揺れの world と同じ。加えて、`r` の側の対照（PCrl・PCrv）が `seg` を読む（陽性対照として宣言したもの・design §1.3） |
| 置き場所 | `work-*/`（`.gitignore`。走り終えると消す。読みが失敗したときは `work-<段>-main/` を残す）。コミットするのは集計した JSON だけ: `results/ceiling/`・`results/<段>/pilot/`・`results/<段>/main/`・`results/<段>/split/`・`results/compare/`（`*-smoke/` は無視） |
| 再生成 | `bash run.sh --ceiling`。続いて `go` の段ごとに、`--pilot --step <段>` → `--apply-pilot` → `--smoke --step <段>` → `--main --step <段>`。最後に `--compare`。<br>どれも自己検査を先に回す。`GSE_REPLAY` が要る（`env.md`）。<br>下見 1 の後に、この入れ物から `$PYTHON scripts/checks.py --apply-pilot config.json results/<段>/pilot/pilot.json <段>` で λ を書く（`pc_stall.lam`・`lam_1800`・`pc_r.lam` の `<段>`） |

- 合成の NDJSON も外部の LLM（Codex を含む）に渡さない。
- 自己検査は、写し元の生成器と描画（中間の world・揺れの world）を SHA-256 で照合してから比べる。写し元の入れ物を変えると自己検査が落ちる。
- `compare.py` が読む前のタスクの結果の JSON も、`config.json` の `compare.prev_sha256` で照合する。
