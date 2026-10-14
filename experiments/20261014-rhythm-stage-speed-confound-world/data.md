# data — 背景のステージの机上の検査・中間の world（打鍵の間隔の 3 段）

第 2 回（`experiments/20261013-rhythm-stage-round2/data.md`）の写しを、このタスクに合わせて直した。変えたのは world の段・seed・段ごとの置き場所だけ（`.steering/20261014-rhythm-stage-graded-world/design.md` §0）。

入力はすべて**合成**である。実在の人の打鍵・gse-dataset のログは使わない。

| 項目 | 値 |
|---|---|
| 生成器 | `scripts/gen_sessions.py`。EH1 第 5 回（`experiments/20261010-portrait-eh1-round5/scripts/gen_sessions.py`）の写しに `--world v3`・`v4`（第 1 回）と `--world graded --t T`（このタスク・design §1.3）を足しただけ。world v1・v2 の出力が EH1 第 5 回の生成器と同じこと、`--t 0` が `--world v4` と、`--t 1` が `--world v2` と同じ出力になることを `selftest.py` が SHA-256 で確かめる（NDJSON と `sessions.json` はバイト、ラベルの npz は配列の中身） |
| world（段） | `segments_v4` を写し、STRUGGLE の `flight_median_ms` = 150^(1−t) × 320^t と `flight_sigma` = (1−t) × 0.25 + t × 0.35 だけを置き換える（v4 と v2 の違いはこの 2 つだけ）。段は t = 0.25・0.5・0.75（`config.json` の `ceiling.steps`・`t025`・`t050`・`t075`）。値は計器が式から作り、`config.json` には書かない。作業の場所の `world.json` に `world`・`t` を書き、`checks.py`・`ceiling.py` が段と照らし合わせる。自己検査の実測（スモークの大きさ）で、STRUGGLE の 1 s 未満の押下どうしの間隔の中央値は v4 150・t 0.25 181・0.5 219・0.75 264・v2 317 ms |
| seed | `SEED` = 20261016（`experiments/*/SEED` と第 2 回の +1・+2 のどれとも重ならない・design §0）。3 段とも同じ値。P の各セッションは `derive_rng(seed, "P", i)` から作られ、ほかの集合（O・J・D・Jsh）の大きさに依らない。段ごとに打鍵の数が変わるので、同じ seed でも乱数を引く位置は最初の STRUGGLE の区間からずれる（段の間は対にならない・design §1.3） |
| 下見 0・下見 1・本番 | 下見 0（`--ceiling`）と下見 1（`--pilot --step`）は `SEED + 1` = 20261017・P 240 本、スモーク（`--smoke --step`）は `SEED + 2` = 20261018・P 12 本、本番（`--main --step`）は `SEED` = 20261016・P 240 本。ほかの集合はスモークの大きさで作り使わない。下見 1 以降は `gse-replay`（EH1 のビルド）で秒ごとの F 系列を作る（`feat/*.npz`）。スモークと本番は P の各セッションの双子（`twins/`・`scripts/twins.py`）も作って `gse-replay` に通す |
| 使う集合 | P だけ（と、その双子） |
| 読むもの | 下見 0 は `labels/*.npz` の打鍵の時刻（`presses_ms`）とセグメントの符号（`seg`）だけを読む。ステージの写像は打鍵の時刻・秒ごとの有無・F 系列の `keys`・`f1`・`f4` だけを読む（`stage.ALLOWED_INPUT`）。`seg` は陽性対照（PC1・PC-stall・PC1-1800・PCl）と判定だけが、`f3` は PC-corr だけが読む。`twins.py` は双子を書くためだけに元の NDJSON のキーの種類を写す（ステージは読まない） |
| 置き場所 | `work-ceiling-<段>/`・`work-<段>-pilot/`・`work-<段>-main-smoke/`・`work-<段>-main/`・`work-selftest/`（`.gitignore`。走り終えると消す）。コミットするのは `results/ceiling/`・`results/<段>/pilot/`・`results/<段>/main/` の集計した JSON だけ（`results/<段>/main-smoke/` は無視） |
| 再生成 | `bash run.sh --ceiling`、続いて `go` の段ごとに `bash run.sh --pilot --step <段>`・`--smoke --step <段>`・`--main --step <段>`（どれも自己検査を先に回す。`GSE_REPLAY` が要る・`env.md`）。下見 1 の後に、この入れ物から `$PYTHON scripts/checks.py --apply-pilot config.json results/<段>/pilot/pilot.json <段>` で λ を書く（別の段・seed・大きさ・規則の `pilot.json` と、L300 の分が止まった下見は拒む。L1800 の分だけが止まったときは `lam.<段>` だけを書く） |

- 合成の NDJSON も外部の LLM（Codex を含む）に渡さない。
