# data — 背景のステージの机上の検査・揺れの world（速さの倍率と漂いの 3 段）

中間の world（`experiments/20261014-rhythm-stage-graded-world/data.md`・`424d9500`）の写しを、このタスクに合わせて直した。変えたのは world・段の名前と値・seed だけ（`.steering/20261014-rhythm-stage-speed-confound-world/design.md` §0）。

入力はすべて**合成**である。実在の人の打鍵・gse-dataset のログは使わない。

| 項目 | 値 |
|---|---|
| 生成器 | `scripts/gen_sessions.py`。中間の world の生成器（`424d9500`・SHA-256 `8bd3ffa9…fafd4`）の写しに `--world confound --c C`（design §1.3）を足しただけ。world v1〜v4・graded の出力（`world.json` を含む）が写し元と同じこと、`--c 0` の打鍵と区間が `--world graded --t 0.5` と同じことを `selftest.py` が確かめる（NDJSON と `sessions.json` はバイト、ラベルの npz は配列の中身） |
| world（段） | 区間の設定は `graded_segments(cfg, 0.5)`（STRUGGLE の `flight_median_ms` 219.08902300206645・`flight_sigma` 0.3、ほかは v4）。FLOW と STRUGGLE のバーストの中の打鍵の間隔を `lognormal(ln m + z(τ), σ)` で引く。`z(τ) = c · δ · (u + d(⌊τ/1000⌋))`（`δ` = ln(219.089… / 150) ≈ 0.3788・`u` は単位ごとの N(0, 1)・`d` は時定数 300 s の 1 秒ごとの定常な単位の OU の列）。`u` と `d` は区間と打鍵の乱数とは別の流れ `derive_rng(seed, "speed", <組>, i)` から引く。段は c = 0.5・1・2（`config.json` の `ceiling.steps`・`c050`・`c100`・`c200`）。作業の場所の `world.json` に `{"world": "confound", "c": c}` を書き、`checks.py`・`ceiling.py` が段と照らし合わせる。D_shuffled の b の区間の境目での `z` の跳びを `speed_jumps.json` に書く（記述だけ） |
| seed | `SEED` = 20261020（判断 1）。3 段とも同じ値。P の各セッションは `derive_rng(seed, "P", i)` から作られ、ほかの集合（O・J・D・Jsh）の大きさに依らない。段ごとに打鍵の数が変わるので、同じ seed でも区間と打鍵の乱数を引く位置はずれる（段の間で対になるのは速さの列の形だけ・design §1.3） |
| 下見 0・下見 1・本番 | 下見 0（`--ceiling`）と下見 1（`--pilot --step`）は `SEED + 1` = 20261021・P 240 本、スモーク（`--smoke --step`）は `SEED + 2` = 20261022・P 12 本、本番（`--main --step`）は `SEED` = 20261020・P 240 本。ほかの集合はスモークの大きさで作り使わない。下見 1 以降は `gse-replay`（EH1 のビルド）で秒ごとの F 系列を作る（`feat/*.npz`）。スモークと本番は P の各セッションの双子（`twins/`・`scripts/twins.py`）も作って `gse-replay` に通す |
| 使う集合 | P だけ（と、その双子） |
| 読むもの | 下見 0 は `labels/*.npz` の打鍵の時刻（`presses_ms`）とセグメントの符号（`seg`）だけを読む。ステージの写像は打鍵の時刻・秒ごとの有無・F 系列の `keys`・`f1`・`f4` だけを読む（`stage.ALLOWED_INPUT`）。`seg` は陽性対照（PC1・PC-stall・PC1-1800・PCl）と判定だけが、`f3` は PC-corr だけが読む。`twins.py` は双子を書くためだけに元の NDJSON のキーの種類を写す（ステージは読まない） |
| 置き場所 | `work-ceiling-<段>/`・`work-<段>-pilot/`・`work-<段>-main-smoke/`・`work-<段>-main/`・`work-selftest/`（`.gitignore`。走り終えると消す）。コミットするのは `results/ceiling/`・`results/<段>/pilot/`・`results/<段>/main/` の集計した JSON だけ（`results/<段>/main-smoke/` は無視） |
| 再生成 | `bash run.sh --ceiling`、続いて `go` の段ごとに `bash run.sh --pilot --step <段>`・`--smoke --step <段>`・`--main --step <段>`（どれも自己検査を先に回す。`GSE_REPLAY` が要る・`env.md`）。下見 1 の後に、この入れ物から `$PYTHON scripts/checks.py --apply-pilot config.json results/<段>/pilot/pilot.json <段>` で λ を書く（別の段・seed・大きさ・規則の `pilot.json` と、L300 の分が止まった下見は拒む。L1800 の分だけが止まったときは `lam.<段>` だけを書く） |

- 合成の NDJSON も外部の LLM（Codex を含む）に渡さない。
- 自己検査は、写し元の生成器（`experiments/20261014-rhythm-stage-graded-world/scripts/gen_sessions.py`）を SHA-256 で照合してから比べる。写し元の入れ物を変えると自己検査が落ちる。
