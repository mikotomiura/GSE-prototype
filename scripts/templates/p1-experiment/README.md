# P1 の事前登録（雛形）— `experiments/<YYYYMMDD>-p1-<名前>/README.md`

★ これは**雛形**（`scripts/templates/p1-experiment/README.md`）である。P1 の実データが届いた日に、
`experiments/<その日の日付>-p1-<名前>/README.md` へ**写して**埋める（★ `experiments/` の実体は P1 を始める日に作る）。

- ⚠️ この雛形の値は**すべて `（未記入）`** である。値を推測で埋めない（★ 埋めるのは、その値を**見る前**か、宣言する時点）。
- ⚠️ 事前登録は**探索を 1 度も回す前**に書く。書いたあとで値を直さない（直すなら新しい日付の版として追記し、経緯を残す）。
- 規約の SSOT は `docs/experiment-tracking.md`、発火層は `reproducibility-discipline` skill、
  P1 の解析パラメータの契約は `docs/preregistration-p1-episode.md`（★ 本書はその**実行記録**であり、契約を書き換えない）。

## 1. 目的

| 項目 | 値 |
|---|---|
| この実験で確かめること（1 文） | （未記入） |
| 検証する仮説（`docs/research-positioning.md` §4.1 の H? か事前登録の項目番号） | （未記入） |
| 関連する事前登録（PreReg-?） | （未記入） |
| 借用した手法の出典（`docs/references.md` の `[n]`） | （未記入） |

## 2. 事前宣言（★ 凍結された解析パラメータ）

| 項目 | 値 | 照合先 |
|---|---|---|
| 事前宣言の文書の版（`docs/preregistration-p1-episode.md`） | （未記入） | ─ |
| 凍結 JSON の版（`src-tauri/prereg/p1-episode.json` の `version`） | （未記入） | `provenance.json` の `prereg_version` |
| 凍結 JSON の sha256 先頭 16 桁 | （未記入） | `provenance.json` の `frozen_json_sha256_prefix` |

## 3. ⚠️★★★ PG-1（宣言ゲート・事前宣言 §2.3）

「一人あたり episode 数の下限」を、**探索（`--stage search`）を 1 度も回す前**に宣言するゲート。
`scripts/p1-repro.sh` は既定（`--stage pg1`）でここの**手前で止まる**。

| 項目 | 値 |
|---|---|
| 宣言日時（UTC・★ 探索を 1 度も回す前であること） | （未記入） |
| 見たもの（★ **参加者ごとの episode 数の分布だけ**。`pg1_distribution.json`。⚠️ 転帰も予測成績も見ない） | （未記入） |
| 下限の値（一人あたり episode 数・凍結 JSON の新版の `pg1.min_episodes_per_participant`） | （未記入） |
| 下回った参加者の扱い | （未記入） |
| 宣言した新版（事前宣言の文書の版・凍結 JSON の版と sha256 先頭 16 桁） | （未記入） |
| PG-1 を通してから探索を回したか（通した / 通していない） | （未記入） |

- ⚠️ **PG-1 を通していない探索結果は `INCONCLUSIVE` として報告する**（★ 「良かった一式」を選ばない・事前宣言 §2.3）。
  WP2 の freeze には使わない。
- ⚠️ 下限の値は**分布を見てから**宣言する。分布を見る前に値を書き込まない。
- ★ 下限の値は凍結 JSON の新版（`pg1.min_episodes_per_participant`）として宣言する。
  ⚠️ 宣言後は `gse-replay` を**作り直す**（★ 古い binary が埋め込む凍結 JSON の hash が違うと `p1-repro.sh` が exit 3 で止める）。

## 4. 乱数と環境の固定

| 項目 | 値 | 照合先 |
|---|---|---|
| seed（凍結 JSON の `search_protocol.seed`） | （未記入） | `provenance.json` の `search_seed` |
| `HMM_VERSION`（封筒 `config.hmm_version`） | （未記入） | `provenance.json` の `hmm_version` |
| 実行した repo の commit（と作業ツリーが clean か） | （未記入） | `provenance.json` の `repo_commit` / `repo_clean` |
| lockfile（`src-tauri/Cargo.lock`）の sha256 | （未記入） | `provenance.json` の `cargo_lock_sha256` |
| 実行環境（OS・rustc・python・duckdb の版） | （未記入） | ─ |

## 5. 入力

| 項目 | 値 | 照合先 |
|---|---|---|
| 入力の commit（`gse-dataset` の commit hash） | （未記入） | `provenance.json` の `input_commit`（★ `GSE_DATASET` を渡す） |
| 入力のレイアウト（`<ndjson-root>/<P-ID>/<session>.ndjson`）の置き場 | （未記入） | ─ |
| 参加者数・セッション数 | （未記入） | `provenance.json` の `n_participants` / `n_sessions` |

⚠️ 生 NDJSON・キーストローク内容は repo にコミットしない（`data-privacy` SSOT）。ここに書くのは commit hash と件数だけ。

## 6. 1 コマンド再現

```bash
# ★ repo 直下から。<workdir> は repo の外・空か未作成（★ 特徴行は共有禁止）。
# 1) 既定 = PG-1 の手前まで: 3 極 → 参加者ごとの episode 数の分布 → episode DB
GSE_DATASET=<gse-dataset のクローン> GSE_REPLAY_BIN=src-tauri/target/release/gse-replay \
  bash scripts/p1-repro.sh <ndjson-root> <workdir>

# 2) PG-1 を宣言（凍結 JSON の新版）して gse-replay を作り直したあとで:
#    ★ <workdir> は新しい空のディレクトリ。--labels は転帰の CSV（外から渡す）
GSE_DATASET=<gse-dataset のクローン> GSE_REPLAY_BIN=src-tauri/target/release/gse-replay \
  bash scripts/p1-repro.sh <ndjson-root> <workdir-search> --stage search --labels <labels.csv>
```

- ★ 成功した実行にだけ `<workdir>/provenance.json` が付く。**無い `<workdir>` は完了していない**（結果として読まない・使い回さない）。
- ⚠️ `--stage search` は PG-1 が宣言されていなければ **exit 6** で止まる（★ 握りつぶさない）。

## 7. 成果物の置き場

| 項目 | 値 |
|---|---|
| `<workdir>` の実パス（★ **repo の外**） | （未記入） |

- ⚠️ `<workdir>` の成果物（`features/`・`episodes.duckdb`・`pg1_distribution.json`・`grid/`・`select_table.json`）は
  **repo にコミットしない・`gse-dataset` へ共有しない**（★ 時刻は絶対 epoch ms で個人を同定しうる。
  `scripts/check_no_feature_output.sh` が特徴行の混入を止める）。
- ★ 残してよいのは、この README（値を埋めたもの）と `provenance.json` の写しだけ。
