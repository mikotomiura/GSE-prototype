# 封筒 issue（起票 2 / 5）—— `--features` 出力に由来の封筒を足し、共有の門を置く

> ★ 一次: `.steering/20260914-mhd-feature-offline-tiers/blockers.md` 起票 2 / 起票 5 ／
> 同 `decisions.md` 判断 25 #14 ／ `src-tauri/src/bin/replay.rs` ／
> `.steering/20260914-mhd-feature-offline-tiers/issues/*-acceptance.sh` ／ `docs/glossary.md`。

## 背景

`gse-replay --features` の出力は**トップレベルが `FeatureRow` の配列**である
（`bin/replay.rs:1146-1160` が `build_feature_rows` の戻り値をそのまま `to_writer_pretty` する）。

1. **起票 2**: セッション単位の事実（`capabilities` / `app_version` / 入力の同一性）を持たないため、
   ⚠️ **複数セッションの出力を結合すると、どの行がどの計器条件で取れたか失われる**。
2. **起票 5**: 「`--features` 出力は `gse-dataset` へ共有しない」という規約は
   `docs/glossary.md`（特徴行の行）と `--features` の usage に**文字としては在る**が、
   ⚠️ **機械的な門が無い**。`.gitignore` は名前依存で `feat.json` / `features.json` /
   `src-tauri/rows.json` / `experiments/x/feat.json` / `out.ndjson` は**いずれも NOT ignored**
   （2026-09-15 実測。2026-09-20 に再確認）。

★ 研究者判断 2026-09-18（判断 25 #14）の逐語: **「封筒を足す小 issue」**。
出力を **`{ provenance, config, rows }`** にし、**全 acceptance の前提（配列）を 1 度だけ書き換える**。

⚠️★★★ **封筒は全 acceptance の前提を書き換えるので、004 / 006 を回す前にやる**
（★ 起票 2 の逐語「途中で変えると走り終えた issue の検査が全部無効になる」）。

## ゴール

1. `gse-replay <session.ndjson> --features` の出力が `{ provenance, config, rows }` になる。
2. `provenance` に **NDJSON から読める由来**と **「共有しない」のマーカー**が載る。
3. `config` に**この出力を再現するのに要る設定値**が載る（判断 25 #13 の事前宣言＋CLI 注入の受け皿）。
4. 既存 8 本の `issues/*-acceptance.sh` が**封筒を剥がす 1 行**だけで通る。
5. **共有の門**が本リポの CI で走り、`gse-dataset` のクローンにも向けられる。

## スコープ

### 含むもの

- `src-tauri/src/bin/replay.rs` —— `--features` の出力を封筒でくるむ。usage の更新。
- `src-tauri/src/analysis/feat_offline/` —— `Quality` から `capabilities` を外す（封筒へ移す）。
- `.steering/20260914-mhd-feature-offline-tiers/issues/00{1..8}-acceptance.sh` —— **8 本すべて**。
- `scripts/check_no_feature_output.sh`（新規）—— 共有の門。
- `.github/workflows/ci.yml` —— 上記を CI に載せる。
- `.steering/20260920-envelope-issues/envelope-acceptance.sh`（新規）—— 封筒自体の検査。
- `docs/glossary.md` —— 「封筒」「共有の門」を定義。

### 含まないもの

- ⚠️ **起票 1（`meta` に `os` が無い）**。★ 計器変更（`logger.rs` / `schema_dto.rs`）で **ADR-032 の領域**。
  → ★ 封筒に載せられるのは **いま NDJSON から読めるもの**だけ（**`os` は読めない**）。
- ⚠️ **issue 004（`T1c`）/ 006（`T1d`）の実装**。★ `grep -c 未裁定` が 0 になるまで着手禁止（判断 26）。
  ★ 本タスクは 004 / 006 の acceptance の**配列前提だけ**を直す（実装はしない）。
- ⚠️ **事前宣言値の凍結 / CLI 注入**（判断 25 #13）。★ 本タスクは `config` という**受け皿を作るだけ**で、
  値は現行の `StallOnsetConfig::default()` のまま。
- ⚠️ **`gse-dataset` リポへの変更**（`.github` を新設する等）。★ 別リポ。
- ⚠️ ADR 本文・事前登録 `§3`・被験者向け文書。

## 受け入れ条件

- [ ] AC1: `--features` の出力のトップレベルが `provenance` / `config` / `rows` の 3 キーを持つ object。
- [ ] AC2: `provenance` が meta 由来の事実（`session_start` / `hmm_version` / `app_version` /
      `g1_mode` / `o1_mode` / `keyboard_layout` / `capabilities`）と入力の同一性
      （`source_basename` / `source_sha256`）と `sharing` マーカーを持つ。
- [ ] AC3: `rows[].quality` に `capabilities` が**無い**（封筒へ移した）。
- [ ] AC4: `config` が `StallOnsetConfig` の 6 フィールド ＋ `max_feature_ticks` ＋
      `hmm_version` / `engine_tick_ms` / `pause_threshold_ms` を持つ。
- [ ] AC5: 同じ入力から **2 回実行してバイト単位で同一**の出力が出る（生成時刻を載せない）。
- [ ] AC6: 既存 8 本の acceptance が**封筒剥がしの 1 行**で通る。
      ★ merge 済み 6 本（001 / 002 / 003 / 005 / 007 / 008）を**実測で緑**にする。
      ⚠️ 004 / 006 は blocked のままで、`.revision` / `.restart` が無いことによる赤は許容する
      （★ ただし「配列が来ない」で赤になってはいけない）。
- [ ] AC7: `envelope-acceptance.sh` が封筒自体を検査し、**突然変異で赤になる**ことを実測する。
- [ ] AC8: `scripts/check_no_feature_output.sh` が (a) `sharing` マーカー (b) 封筒を剥がした
      行の形 の**両方**で検出し、**ファイル名に依存しない**。突然変異で赤になることを実測する。
- [ ] AC9: CI に (a) が載る。
- [ ] AC10: `docs/glossary.md` に「封筒」「共有の門」が定義される。
- [ ] AC11: `blockers.md` の起票 2 / 起票 5 を**閉じる**（⚠️ 消さない）。

## 関連ドキュメント

- `.steering/20260914-mhd-feature-offline-tiers/blockers.md` 起票 2 / 起票 5（一次）
- `.steering/20260914-mhd-feature-offline-tiers/decisions.md` 判断 25 #14（研究者判断・一次）
- `docs/glossary.md` 「特徴行」の行（規約の逐語）
- `docs/adr/ADR-030-*`（`stall onset` の定義）/ ADR-013（`capabilities`）

## 運用メモ

- /reimagine 適用: **No**
- 理由: 出力形状は判断 25 #14 が逐語で `{ provenance, config, rows }` と指定しており、
  設計の自由度は「封筒に何を載せるか」だけ。それは grill（2026-09-20）で確定済み。
