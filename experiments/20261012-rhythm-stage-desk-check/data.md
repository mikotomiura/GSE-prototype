# data — 背景のステージの机上の検査

入力はすべて**合成**である。実在の人の打鍵・gse-dataset のログは使わない。

| 項目 | 値 |
|---|---|
| 生成器 | `scripts/gen_sessions.py`。EH1 第 5 回（`experiments/20261010-portrait-eh1-round5/scripts/gen_sessions.py`）の写しに `--world v3`・`v4` を足しただけ（design §1.6）。world v1・v2 の出力が EH1 第 5 回の生成器と同じことを `selftest.py` が SHA-256 で確かめる（NDJSON と `sessions.json` はバイト、ラベルの npz は配列の中身） |
| world | v2 = `config.json` の `segments_v2`（EH1 第 2〜5 回と同じ）。v3 = `segments_v3`（v2 の STRUGGLE の `flight_median_ms`・`flight_sigma` を FLOW と同じ 150・0.25 にし、world v1 の訂正の後の間 `p_pause_after_bs` 0.6・`pause_after_bs_min_ms` 2000・`pause_after_bs_extra_ms` 3000 を戻した）。訂正の後の間は、最後の打鍵が Backspace だったバーストの後の間にだけ効く（生成器の v1 からの作り。自己検査の実測で、STRUGGLE の Backspace の後の 1 s 以上の間のうち 2 s 以上の割合は v2 0.48 → v3 0.81） |
| world v4 | `segments_v4`（研究者の判断 16）: v2 の STRUGGLE の `flight_median_ms`・`flight_sigma` を FLOW と同じ 150・0.25 にしただけ（訂正の後の間は入れない）。停滞は Backspace の率と区間の構造にだけ残る。自己検査の実測で、STRUGGLE の Backspace の後の 1 s 以上の間のうち 2 s 以上の割合は 0.43（FLOW 0.43） |
| seed | `SEED` = 20261009（EH1 と同じ）。下見 0（`--ceiling`）は `SEED + 1` = 20261010・P 40 本（design §3.0・§3.8）。下見 0 ではほかの集合（O・J・D・Jsh）はスモークの大きさで作り、使わない（P の各セッションは `derive_rng(seed, "P", i)` から作られ、ほかの集合の大きさに依らない） |
| 下見 1・本番 | 下見 1（`--pilot`）は `SEED + 1` = 20261010・P 40 本、スモーク（`--smoke`）は `SEED`・P 12 本、本番（`--main`）は `SEED` = 20261009・P 240 本。どれも world v4 で、ほかの集合はスモークの大きさで作り使わない。下見 1 以降は `gse-replay`（EH1 のビルド）で秒ごとの F 系列を作る（`feat/*.npz`）。スモークと本番は P の各セッションの双子（`twins/`・`scripts/twins.py`・秒ごとの打鍵の数を保ち、秒の中の時刻を引き直す）も作って `gse-replay` に通す |
| 使う集合 | P だけ（と、その双子） |
| 読むもの | 下見 0 は `labels/*.npz` の打鍵の時刻（`presses_ms`）とセグメントの符号（`seg`）だけを読む。キーの種類・`gse-replay` の出力は読まない（基準のモデル A・A_speed は打鍵の時刻だけから作る・design §1.5）。ステージの写像は打鍵の時刻・秒ごとの有無・F 系列の `keys`・`f1`・`f4` だけを読む（`stage.ALLOWED_INPUT`・design §1.2）。`seg` は陽性対照（PC1・PC-stall）と判定だけが、`f3` は PC-corr だけが読む。`twins.py` は双子を書くためだけに元の NDJSON のキーの種類を写す（ステージは読まない） |
| 置き場所 | `work-ceiling-*/`・`work-pilot/`・`work-main-smoke/`・`work-main/`・`work-selftest/`（`.gitignore`。走り終えると消す）。コミットするのは `results/ceiling/`・`results/pilot/`・`results/main/` の集計した JSON だけ（`results/main-smoke/` は無視） |
| 再生成 | `bash run.sh --ceiling`・`--pilot`・`--smoke`・`--main`（どれも自己検査を先に回す。下見 1 以降は `GSE_REPLAY` が要る・`env.md`） |

- 合成の NDJSON も外部の LLM（Codex を含む）に渡さない（引き継ぎ §3）。
