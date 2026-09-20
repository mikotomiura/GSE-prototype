# タスク 2 — Mh-D 特徴量の Tier 別オフライン実装（T0 / T1 / Q ＋ stall onset）

> ⚠️★★★ **このファイルを一次資料にしない。**
> ★ 一次は `docs/adr/ADR-030-stall-onset-and-decision-episode.md`（**D2 / D3 / D4 / D10 / D11**）／
> `docs/adr/ADR-032-instrument-change-arbitration.md`（**D5 / D9 / §Migration M7**）／
> `docs/loop-engineering.md`（Loop の単一 SSOT）。

## 背景

★ `ADR-030 D10` が accept したのは **特徴リストではなく 3 つ**である —— **Tier の枠**・**投資順序**・
**特徴量重要度を 1 つの数値にしないこと**。⚠️ 逐語「**特徴を増やせば精度が上がるとは仮定しない。**」

★ `ADR-030 D11` が **計器を変えない範囲 / 変える範囲**の仕切りを引いた（★ 2026-09-13 実測に基づく）:

| 範囲 | 計器変更 | 根拠（一次） |
|---|---|---|
| **`T0` / `T1a` / `T1b` / `T1d` / `Q`** | ✅ **不要** | `key` 行が 1 打鍵ごとに `t` を持つ（`logger.rs:1634-1638`）／ `KeyCategory` **14 種**で `sentence_punctuation` 分離済み（`anonymize.rs:93-110`）／ `ime_shadow{dwell_ms, nav, abandon}` 在り ／ `capabilities` ＋ `hook_health` 在り |
| **`T1c` のうち `delete run` / `rewrite` / `再削除` / `loop depth` / `局所 recurrence`** | ✅ **不要** | ★ `key` 行だけで今日作れる |
| ⚠️ **`T1c` のうち `undo` / `redo` 往復だけ** | **要** | ⚠️ ADR-014 判断 6 で生 VK を `KeyCategory` へ量子化済み ＝ `Ctrl+Z` と `Ctrl+A` が同じ |
| ⚠️ **`T2` / `T3`** | **要** | ADR-032 **D3 で `T2` は解かない** ／ **D4 で `T3` は不採** |

→ ★★★ **本タスクは「変えない範囲」だけを実装する。**
⚠️ 計器変更（`undo`/`redo`・`key.mod`）は **ADR-032 が Accepted になり、同意 §3 の改訂が通ってから**
（★ ADR-032 §Migration **M4 / M5**）。★ **本タスクでは 1 バイトも触らない。**

## ゴール

★ `gse-replay --features` が、NDJSON セッション 1 本から **1 Hz tick 単位の特徴行**を出力し、
その各行に **T0 / T1a / T1b / T1c / T1d / Q** の各 Tier のフィールドが載っていること。
★ 併せて `ADR-030 D2 / D3 / D4` の **`stall onset`（`t0`）検出器をオフライン側に**実装すること。

★ Done は **exit code と test 名で言える**:
- `cargo test --manifest-path src-tauri/Cargo.toml --workspace` が exit 0
- ゴールデン replay（`--snapshot`）が exit 0 のまま（★ **既存の推定経路を 1 mm も動かさない**ことの証拠）
- 各 issue の `acceptance.sh` が exit 0（★ **当該 Tier のフィールドが実際に出力に出ていること**を検査）

## スコープ

### 含むもの
- `gse-replay --features`（新モード。⚠️ 既存モードと相互排他）
- `src-tauri/src/analysis/feat_offline/`（OS 非依存の純関数。Tier ごとに 1 ファイル）
- `T0` / `T1b` / `T1a` / `T1c` / `T1d` / `Q` の各特徴
- `stall onset`（`t0`）検出器（ADR-030 D2 / D3 / D4）

### 含まないもの
- ⚠️★★★ **`features.rs` / `engine.rs` の変更**（★ ADR-030 **D1** 逐語「検出器は**オフライン側**に置く」）
- ⚠️★★★ **`HMM_VERSION` の bump**／ゴールデン snapshot の再生成
- ⚠️★★★ **`schema_dto.rs` / `logger.rs` / `capabilities.rs` の変更**（＝ 計器変更。ADR-032 M5 待ち）
- ⚠️★★★ **`undo` / `redo` 往復**・**`key.mod`**（★ ADR-032 が Accepted になってから）
- ⚠️ **`T2`**（cross-channel）／ **`T3`**（domain-local events）
- ⚠️ **`capability matrix`**（ADR-032 M7）—— ★ **Loop に載せない**。研究者判断 2026-09-14 で
  「**実装 issue だけ Loop、matrix は対話で行う**」と決めた（→ `decisions.md` 判断 4）
- ⚠️ モデル学習・性能評価・`docs/preregistration-v0.3.md` の変更

## 受け入れ条件

- [ ] AC1: `gse-replay --features <ndjson>` が 1 Hz tick 単位の JSON を出力し、exit 0
- [ ] AC2: `--features` は既存モード（`--snapshot` / `--metrics` / `--segments` / `--intervention` 等）と**相互排他**
- [ ] AC3: 各 Tier のフィールドが出力に出ており、**手計算と一致する**（★ 各 issue の `acceptance.sh`）
- [ ] AC4: ゴールデン replay が exit 0 のまま（★ `OK: 15 snapshots match`）
- [ ] AC5: `cargo test` / `cargo check` / `cargo clippy -D warnings` がすべて exit 0
- [ ] AC6: `analysis/` に OS 依存 API が 1 つも入っていない（★ `architecture-rules`）
- [ ] AC7: ⚠️ `Q` が**状態特徴として使われていない**（★ `.idea/survey:194` 逐語「**欠測を 0 として入力せず、推論の抑制・abstention に使う**」）
- [ ] AC8: ⚠️ `Q` の欠測理由に**被験者由来のもの（一時停止・区間削除）が 1 つも入っていない**（★ ADR-030 D10 の囲み）

## ベースライン（★ 2026-09-14 実測・⚠️ 予測ではない）

| コマンド | exit | 備考 |
|---|---|---|
| `cargo test --manifest-path src-tauri/Cargo.toml --workspace` | **0** | 670 passed / 0 failed |
| `cargo check --manifest-path src-tauri/Cargo.toml --workspace --all-targets` | **0** | — |
| `cargo clippy --manifest-path src-tauri/Cargo.toml --workspace --all-targets -- -D warnings` | **0** | — |
| `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json` | **0** | `OK: 15 snapshots match`。⚠️ `session hmm_version = 0.2.0, current engine = 0.5.0` の**警告は出る**（★ これが既存のベースライン。⚠️「無視してよい」と断定しない） |
| `cargo run --bin emit_schema` ⇄ `src-tauri/schema/current.json` | 一致 | SCHEMA PARITY OK |

## 関連ドキュメント

- `docs/adr/ADR-030-stall-onset-and-decision-episode.md` — D2 / D3 / D4（`t0`）・D10（Tier 枠・投資順序）・D11（仕切り）
- `docs/adr/ADR-032-instrument-change-arbitration.md` — D5（`capability matrix` が先）・§Migration M7
- `.idea/20260910-mhd-feature-work-behavior-literature-gap-survey.md` §6.1 / §6.3 / §11
- `docs/loop-engineering.md` — Loop の単一 SSOT（Done/Stop・budget・events 契約・モデル割当）

## 運用メモ
- /reimagine 適用: No
- 理由: ★ 枠（Tier）・順序・仕切りは **ADR-030 D10 / D11 で accept 済み**であり、
  ⚠️ 本タスクで代替案を作ることは「蒸し返さない」に反する（★ 引き継ぎ §4-5）。
  ★ 残っていた設計分岐（出力単位 / baseline / 置き場）は grill で閉じた（→ `decisions.md`）。
