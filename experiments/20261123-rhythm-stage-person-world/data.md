# data — 背景のステージの机上の検査・人ごとのリズムの型の world（個人の再識別・個人ごとの読み手）

前のタスクの計器（`experiments/20261122-rhythm-stage-relative-timing/data.md`）の写しに、人の層を足した（`.steering/20261123-rhythm-stage-person-world/design.md` §1）。

入力はすべて**合成**である。実在の人の打鍵・gse-dataset のログは使わない。合成した「人」「型」「停滞」は打鍵の統計の型であり、実在の人の打鍵や認知の状態ではない。

| 項目 | 値 |
|---|---|
| 生成器 | `scripts/gen_sessions.py`。前の生成器に `--world person-m`・`person-r`（`--icc`、person-r は `--k` も）を足した。既存の world（v1〜v4・graded・confound・factor・drift）が書く列は写し元とバイトで一致する（`selftest.py` の G0）。`baseline.py`・`replay_all.py`・`twins.py` は前のまま（SHA-256 で照合） |
| world（段） | 4 段（`config.json` の `person.steps`）。<br>・`m049`・`m068`: `person-m`（人ごとの速さの倍率だけ・ICC 0.494 / 0.679）。<br>・`r049`・`r068`: `person-r`（速さは人に結び付かず、3 つの型の次元だけが人に結び付く・同じ ICC・k は下見 1k で選び `person.k.<段>` に書く）。<br>土台は g(0.5)（`speed_confound.base_t`）。40 人 × 6 本 = 240 本・3 時間。P 以外の集合（O・J・D）は作らない |
| 乱数の流れ | 人の層の world だけ、区間の並び（`derive_rng(seed, "seq", i)`）・打鍵（`"keys", i, 区間`）・人の潜在値（`"pz", p`）・セッションの揺れ（`"pe", p, s`）を別の流れから引く。段の間・k の格子の点の間で区間の並びとラベルと z・ε が同じ（G1） |
| seed | `SEED` = 20261125（新しい値）。下見 0（`--ceiling`）・下見 1k・下見 1 は `SEED + 1`、スモークは `SEED + 2`、本番は `SEED`（`person.seed_offsets`）。自己検査の生成は `TEST_SEED` = 7 で、これらを使わない |
| 使う集合 | P だけ（双子は作らない） |
| ラベル | L300 だけ |
| 候補 | 前のタスクの 6 本（案 D の 2 本と錨の 4 本）と、それぞれの `without_smooth` の変種（`~ws`・同じ画の特徴の部分集合） |
| 対照 | (5): `PC1-id`・`PCp-<候補>`・`PC0-id-<候補>`・`PC-raw`。(6): `PC1-pers`・`PCps-<候補>`・`PC0p-<候補>`。人の番号は名前（`P<i>` の `i // 6`）だけから読み、生成の潜在値は読まない（R1） |
| 基準 | (5) は A（主）と A_speed（副）・(6) は A |
| 置き場所 | `work-*/`（`.gitignore`。走り終えると消す）。コミットするのは集計した JSON だけ: `results/<段>/ceiling/`・`results/<段>/pilot-k/`・`results/<段>/pilot/`・`results/<段>/main/`（`*-smoke/` は無視） |
| 再生成 | `env.md` の「実行（段ごと）」 |

- 合成の NDJSON も外部の LLM（Codex を含む）に渡さない。
- 自己検査は、前のタスクの生成器の出力・基準・描画を写し元（揺れの形の計器・SHA-256 で固定）と比べる。写し元の dir のファイルは読むだけで、`.pyc` を書かない。
- 自己検査の生成は `TEST_SEED` = 7 だけを使う。
- `selftest.py --mutants` は design §3.7 の変異 14 本（と前の 7 本）を 1 本ずつ入れ、どれも自己検査を落とすことを確かめる。
