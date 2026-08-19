# 設計 — G1 リブート (計器 ADR-013 + 運用 G-1)

⚠️ 本文書は **v1**。`/reimagine` で v2 を生成して比較する (`requirement.md` 運用メモ)。

## 0. 実測で分かった前提 (★ handoff の記述を 2 件訂正した)

| # | handoff の記述 | ★ 実測 |
|---|---|---|
| 1 | 事前登録は「第 14 版」 | **第 16 版** (`preregistration.md:19` / `analyze.py:49`) |
| 2 | 「`G1_BLOCKS_STARTED` が崩れると提出のブロック番号がずれる」 | **ずれない**。提出番号は `reconcile.rs:236 next_block_number` が `.age` 名と `manifest.jsonl` の**最大値+1** で決める。`G1_BLOCKS_STARTED` は**ローテート要否だけ**を決める |
| 3 | G-1 は「① session_end を書く ② ローテート ③ SessionStart」の **3 手順**が要る | ★★★ **`LogEntry::Rotate` が既に ①②③ を全部やる** (`logger.rs:1613` `write_meta_end` → `:1619` 新ファイル → `:1625` `write_meta_start`)。⚠️ **新しい LogEntry を足す必要は無い** |

→ ★ **3 により G-1 の修正は「`was_active` の枝から既存の `Rotate` を送る」だけ**になる。

## 1. 変更対象

| # | ファイル | 変更 |
|---|---|---|
| C1 | `src-tauri/src/capabilities.rs` (**新規**) | `capabilities` の単一情報源 (`#[cfg]` 反映) + `app_version` |
| C2 | `src-tauri/src/lib.rs` | `mod capabilities;` / `start_session` の G-1 修正 / 監視スレッドの `starve_window` + `dropped_delta` |
| C3 | `src-tauri/src/logger.rs` | `write_meta_start` に 2 フィールド / `HookHealth` に `dropped_delta` / `StarveWindow` variant |
| C4 | `src-tauri/src/input/liveness.rs` | micro 帯の窓集計 (**純関数**・両 OS でテスト可) |
| C5 | `src-tauri/src/schema_dto.rs` + `schema/current.json` | DTO 同期 → 再生成 → parity |
| C6 | `experiments/20260801-controlled-friction-task/` | 事前登録 第 17 版 / `config.json` / `analyze.py` / `data.md` / `protocol.md` / `consent.md` / `participant-guide.md` |
| C7 | `docs/adr/ADR-011,012,013` / `docs/architecture/domain-adapter-boundary.md` | handoff §6 の 8 件 |

## 2. C1: `capabilities.rs`

★ レイヤー判定 (`architecture-rules` ルール 4): OS API を**呼ばない**が `#[cfg]` は**反映する**宣言表。
`analysis/` ではなく **top-level** に置く (先例: `g1.rs` が `cfg!(target_os)` を持つ top-level 純モジュール)。

```rust
/// 全 OS 共通の候補集合 (16 行種)。★ 網羅テストの参照点。
pub const KNOWN_LINE_TYPES: &[&str] = &[ "meta", "session_start", "key", … ];

/// このビルドが**無条件に**出せる行種。
pub fn unconditional() -> Vec<&'static str>   // ime_shadow は #[cfg(windows)] でのみ push
/// 閾値ゲート付き。0 行 = 判定不能 (ADR-013 D1)。
pub const THRESHOLD_GATED: &[&str] = &["hook_health", "starve_window"];
/// 粗い semver のみ。⚠️ git SHA / ホスト名 / GUID を入れない (D6)。
pub fn app_version() -> &'static str { env!("CARGO_PKG_VERSION") }
```

⚠️ `"meta"` は `KNOWN_LINE_TYPES` に入れるが `unconditional()` には**入れない**
(その行自身が `meta` なので・D1)。

## 3. C3: `meta` 行 (additive)

```
{"type":"meta","session_start":…,"hmm_version":"0.4.0","app_version":"0.x.y","capabilities":{…}}
```
⚠️★★★ **`g1_mode` の位置とキー順を変えない。** 現行は `None` のとき 1 バイトも変わらない形で
手書きされており (`logger.rs:1079` 逐語)、ゴールデンと既存フィクスチャの非回帰がこれに依存する。
→ ★ **新フィールドは末尾に足す**。`g1_mode` の有無で分岐する 2 経路の**両方**に足す。

⚠️ **要確認 (実装 1 手目)**: ゴールデン 6 本が `meta` 行を含むか。
`--snapshot` は `FeatSnapshot` 列の比較なので**含まないはず**だが、**確認してから書く**
(`verify-before-claiming`)。含むなら「ゴールデン再生成が要るか」を Stop 条件として研究者に返す。

## 4. C4/C2: `starve_window`

### 何を 1 エピソードと数えるか

`liveness::step` は **フックが呼ばれた瞬間に `starved_ms` を 0 に戻す**。
→ ★ **エピソードの終わり = `starved_ms` が正から 0 に落ちた tick**。そのときの直前値がピーク。

```
micro エピソード ⇔ 0 < peak < th.log_after_ms   (= 30s。★ 定数を直書きせず th から取る)
```
⚠️ `peak >= log_after_ms` のものは `hook_health` 側 (Suspect) が既に記録している
→ ★ **2 つのトラックは閾値で分割され、二重計上しない**。

### 窓

`win_ms = 60_000` の固定窓。窓が閉じたとき `n_lt30 > 0` なら 1 行出す。
⚠️★★★ **`n_lt30 == 0` の窓は出さない** (D4・在席の連続タイムラインを作らない)。

### ⚠️ 実装上の罠 (★ ここを外すと窓が飛ぶ)

`lib.rs:2924` の `if health == prev_health && !rehook { continue; }` は
**1Hz ループの残りを全部飛ばす**。→ ★ **窓集計と送出はこの `continue` より前に置く。**

### 純関数の置き場

`input/liveness.rs` に `MicroStarveWindow` (時計もグローバルも触らない・`step` と同じ流儀)。
→ ★ 両 OS で境界をテストできる。

## 5. C2/C3: `dropped_delta`

⚠️ 現行の `prev_dropped` は **`tracing` に出した時だけ**更新される
(`lib.rs:2884-2891`: `if dropped > prev_dropped { … prev_dropped = dropped; }`)。
→ ★ これを流用すると「前回 **行** からの差分」にならない。
**`dropped_at_last_line` を別に持つ** (行を出した直後に更新)。

## 6. C2: G-1「閉じてから開く」

```rust
if g1_mode().is_some() {
    if !was_active {
        …従来どおり (blocks_started > 0 のときだけ Rotate)…
    } else {
        // ★ 新規: 既に active。Rotate 1 通で「session_end → 新ファイル → meta」が済む。
        // ⚠️ G1_BLOCKS_STARTED は**増やさない** (この枝は「新しい最初のブロック」ではない)。
    }
}
```

### 失敗時 (`try_send` が Err)

★ 既存の枝と**同じく fail-loud** にする。⚠️ ただし**巻き戻し方が違う**:

| 枝 | 巻き戻し |
|---|---|
| `!was_active` (既存) | `G1_BLOCKS_STARTED` を戻し `session_active = false` にして Err |
| `was_active` (新規) | ⚠️ **`session_active` は true のまま**にして Err。★ 前のセッションは**まだ開いている**のだから、false にすると「session_end の無い開きっぱなしのファイル」を計測停止扱いにしてしまう |

⚠️★ **未解決 (v2 で潰す)**: `engine.reset()` / `reset_signal` / `latest_feat` / `intervention` の
リセットは `was_active` 判定より**前**にある。Rotate が失敗して Err で戻ると、
**前のブロックの途中で解析状態だけがリセットされた**状態が残る。
→ v1 案は「判定を早める (`load` で先に覗く)」だが、⚠️ **swap との二重読みでレースを作る**。
★ **ここが `/reimagine` で一番見たい点である。**

## 7. テスト (ADR-013 D3 = acceptance)

| テスト名 | 何を固定するか |
|---|---|
| `capabilities_covers_every_line_type` | `include_str!("logger.rs")` の `"type":"<x>"` を走査し、`KNOWN_LINE_TYPES` に無い行種があれば落ちる。⚠️ 既知の限界: フィクスチャのリテラルも拾う (**過大側 = 見落とさない方向**) |
| `ime_shadow_in_capabilities_on_windows` / `…_absent_on_macos` | `#[cfg]` で対にする (両 OS の CI で走る) |
| `starve_window_omits_empty_windows` | `n_lt30 == 0` の窓が 1 行も出ない |
| `dropped_delta_is_per_line_difference` | 合成入力で「前回**行**からの差分」を固定 |
| `hook_health_semantics_unchanged` | ⚠️★★★ 出力条件 (状態変化 or rehook) と `starved_ms` の意味 (復帰行はピーク) が不変 |
| `every_capability_has_a_reachable_emitter` | 宣言した各要素に送出元がある (過大申告の逆アサート) |
| `double_start_closes_previous_session_then_rotates` | G1 で active 中に start → 旧ファイルに `session_end` 1 個 / 新ファイルに `meta` + `session_start` |
| `double_start_is_noop_outside_g1_mode` | ⚠️ 通常運用の挙動が 1 バイトも変わらない (判断 7) |

## 8. 検証手順 (`src-tauri/` から)

```bash
cargo test --workspace
cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json   # ×6
cargo run --bin emit_schema        # → schema/current.json と byte-equal
python scripts/check_schema_parity.py --dataset <gse-dataset>   # ⚠️ --dataset 必須
```
