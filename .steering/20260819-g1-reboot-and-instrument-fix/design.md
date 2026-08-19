# 設計 v2 — G1 リブート (計器 ADR-013 + 運用 G-1)

★ `requirement.md` のみに立脚してゼロから再生成した案。

## 0. 設計の芯 — ★ 「壊しうる場所」を先に実測で潰す

要件の Stop 条件は 2 つとも「**既存の意味論を動かしたら止めろ**」である。
→ ★ **設計の主題は機能追加ではなく「非回帰の証明経路をどう作るか」**である。

### 0.1 実測で潰した不安 (★ 設計前に確かめた)

| # | 事前の不安 | ★ 実測結果 | 帰結 |
|---|---|---|---|
| A | `meta` 行に足すとゴールデン 6 本が壊れる | ★ **壊れない**。`tests/snapshots/*.json` は `FeatSnapshot` の配列で、`meta` も `hmm_version` も**含まない** | ★ ADR-013 D1 の形 (meta 行に足す) をそのまま採れる |
| B | `meta` の読み手が文字列一致で壊れる | ★ **壊れない**。`anonymize.rs:111` は `serde_json::from_str`、`validate_blocks.py:409` も JSON パース | additive は安全 |
| C | G-1 は新しい `LogEntry` が要る | ★ **要らない**。`LogEntry::Rotate` が `logger.rs:1613-1625` で **`session_end` 書き込み → 新ファイル → `meta` 書き込み**を既に全部やる | ★ **修正は「Rotate を送る枝を 1 本増やす」だけ** |
| D | `app_version` の桁が細かいとフィンガープリントになる | `Cargo.toml:3 version = "0.1.26"` ＝ **粗い semver** | `env!("CARGO_PKG_VERSION")` をそのまま使える (D6 適合) |

### 0.2 ★ 既存の検査を「第 2 のゲート」として使う (v2 の要点)

⚠️ `validate_blocks.py:939` に **「1 ファイルに `session_start` が 2 本あれば FAIL」** が既にある
(★ P010 block07 を受けて置かれた検査)。
→ ★★★ **G-1 の修正が効いたことを、Rust のテストとは独立に、解析側の検査で確かめられる。**
★ v2 はこれを acceptance に組み込む (`python validate_blocks.py --selftest`)。

---

## 1. アプローチ

### 1.1 G-1: **「触る前に断る」** (guard-first)

⚠️★★★ **v2 の中心的な設計判断。**
`start_session` は `swap` より前に `engine.reset()` / `reset_signal` / `latest_feat` /
`intervention` を**必ず**書き換える。この順序には理由があり動かせない
(`lib.rs:1974-1978` 逐語: 「分析スレッドが `active=true` を Acquire で読んだ時点で、
それより前に Release された `reset=true` も可視であることが保証される。逆順だと …
**前セッションの沈黙時間が初回更新に混入する**」)。

→ ⚠️ したがって「送信に失敗したら巻き戻す」形では、**巻き戻せない副作用が既に出ている**。

★ **v2 の解**: **失敗しうる条件を、状態を触る前に検査して弾く。**

```rust
// ★ 何も触る前に (g1_start_gate の直後):
//   これから最大 2 通 (Rotate + SessionStart) 送る。bounded(512) の残量が足りなければ
//   ここで Err を返す。⚠️ この時点ではまだ engine も session_active も触っていない。
guard_log_capacity(&log, NEEDED_SLOTS)?;
```

crossbeam の `Sender::capacity()` / `len()` は残量を返す (`bounded(512)`・`logger.rs:1192`)。

★ **残る失敗は `Disconnected` だけ**で、それはロガースレッドが死んでいる状態＝どの道記録できない。
→ ★ 既存の枝と同じ fail-loud (`Err` を返して画面に出す) を維持する。

### 1.2 分岐を**純関数**に出す

```rust
/// ★ 副作用ゼロ・OS 非依存。両 OS でテストできる。
pub enum StartAction { NoRotate, RotateForNewBlock, RotateForRestart }

pub fn decide_start_action(g1: bool, was_active: bool, blocks_started: u64) -> StartAction
```

| `g1` | `was_active` | `blocks_started` | → |
|---|---|---|---|
| false | * | * | `NoRotate` (⚠️★ 通常運用は 1 バイトも変えない・判断 7) |
| true | false | 0 | `NoRotate` (起動時のファイルをそのまま使う) |
| true | false | >0 | `RotateForNewBlock` (従来どおり。★ カウンタを増やす) |
| true | **true** | * | ★ **`RotateForRestart`** (⚠️ **カウンタを増やさない**) |

⚠️★ **なぜ `RotateForRestart` でカウンタを増やさないか**: `G1_BLOCKS_STARTED` の唯一の役目は
「**このプロセスで最初のブロックか**」の判定 (`blocks_started > 0`) である。二度押しは
「新しい最初のブロック」ではない。★ 増やさなくてもファイルは 1 本ずつ増える
(検算: block1 → file1 / 二度押し → file2 / block2 は `blocks_started=1>0` → file3。**衝突も孤児も無い**)。

★ **`!was_active` を外さない** (判断 8)。既存の code-review HIGH は「数える」ことへの指摘であり、
`RotateForRestart` は数えないので両立する。

### 1.3 ADR-013 は **ADR の字面どおり**に実装する

★ 0.1-A/B で「meta 行に足しても壊れない」ことが実測できたので、
**別行 (`{"type":"capabilities",…}`) を新設する案は採らない** (§6 却下案)。
Accepted な ADR の形を、根拠なく変えない。

---

## 2. 変更対象ファイル

| # | ファイル | 変更 | 種別 |
|---|---|---|---|
| C1 | `src-tauri/src/capabilities.rs` **(新規)** | 行種の単一情報源 (`#[cfg]` 反映) / `app_version()` / JSON 断片生成 | 新規 |
| C2 | `src-tauri/src/lib.rs` | `mod capabilities;` / `decide_start_action` 適用 / 容量ガード / `starve_window` 送出 / `dropped_delta` | 変更 |
| C3 | `src-tauri/src/logger.rs` | `write_meta_start` に 2 フィールド追記 / `HookHealth` に `dropped_delta` / `StarveWindow` variant + 整形 | 変更 |
| C4 | `src-tauri/src/input/liveness.rs` | micro 帯の窓集計 (**純関数**) | 変更 |
| C5 | `src-tauri/src/schema_dto.rs` → `schema/current.json` | DTO 同期 → `emit_schema` 再生成 → parity | 変更 |
| C6 | `experiments/20260801-controlled-friction-task/` | 第 17 版 / `config.json` / `analyze.py` / `data.md` / `protocol.md` / `consent.md` / `participant-guide.md` | 変更 |
| C7 | `docs/adr/ADR-011,-012,-013` / `docs/architecture/domain-adapter-boundary.md` | handoff §6 の 8 件 + D5 ゲートの改訂 | 変更 |

### C1 の置き場 (`architecture-rules` ルール 4 の手順)

1. **レイヤー判定**: OS API を**呼ばない**が `#[cfg]` を**反映する**宣言表 → `input/` でも `analysis/` でもない
2. **ディレクトリ**: **top-level** (`src-tauri/src/capabilities.rs`)。★ 先例は `g1.rs`
   (top-level・`cfg!(target_os)` を持つ・OS API 非依存の純判定モジュール)
3. **命名**: `snake_case.rs` ✓
4. **`lib.rs` に `mod capabilities;`** を追加 (`src-tauri/src/` 直下は `mod.rs` ではなく `lib.rs` が宣言する)
5. **docs**: `docs/repository-structure.md` のモジュール表に 1 行足す

---

## 3. 各変更の仕様

### 3.1 `capabilities.rs`

```rust
/// 全 OS 共通の候補集合 (16 行種)。★ 網羅テストの参照点であり、宣言そのものではない。
pub const KNOWN_LINE_TYPES: &[&str] = &[
    "meta", "session_start", "key", "paste", "feat", "ime_state", "hook_health",
    "user_label", "review_marker", "ime_shadow", "intervention_decision",
    "intervention_response", "session_meta", "probe_assignment", "realtime_label",
    "vignette_response",
    // ★ 本タスクで 1 種増える
    "starve_window",
];

/// 閾値ゲート付き (0 行 = 判定不能・ADR-013 D1)。
pub const THRESHOLD_GATED: &[&str] = &["hook_health", "starve_window"];

/// このビルドが無条件に出せる行種。⚠️ `meta` 自身は載せない (その行が meta だから)。
pub fn unconditional() -> Vec<&'static str>;   // ime_shadow は #[cfg(windows)] のみ

/// ★ 粗い semver のみ。⚠️ git SHA / ホスト名 / ビルド時刻 / GUID を入れない (D6)。
pub fn app_version() -> &'static str { env!("CARGO_PKG_VERSION") }
```

### 3.2 `meta` 行 (additive・末尾に足す)

```
{"type":"meta","session_start":…,"hmm_version":"0.4.0","g1_mode":"marker",
 "app_version":"0.1.26","capabilities":{"unconditional":[…],"threshold_gated":[…]}}
```
⚠️★★★ **`g1_mode` の位置とキー順は動かさない。** 2 経路 (`None` / `Some`) の**両方**の末尾に足す。

### 3.3 `starve_window`

**エピソードの定義**: `liveness::step` は**フックが呼ばれた瞬間に `starved_ms` を 0 に戻す**
→ ★ **エピソードの終わり = 正の値から 0 に落ちた tick**。その直前値がピーク。

```
micro ⇔ 0 < peak < th.log_after_ms     (★ 30_000 を直書きせず th から取る)
```
⚠️ `peak >= log_after_ms` は `hook_health` (Suspect) が既に記録済み → **二重計上しない**
(★ 2 トラックは閾値で分割される)。

**窓**: `win_ms = 60_000`。⚠️★★★ **`n_lt30 == 0` の窓は出力しない** (D4)。

⚠️★★ **実装上の罠**: `lib.rs:2924` の `if health == prev_health && !rehook { continue; }` は
1Hz ループの残りを全部飛ばす。→ ★ **窓集計と送出はこの `continue` より前に置く。**

**置き場**: `input/liveness.rs` に純関数の累算器 (時計もグローバルも触らない・`step` と同じ流儀)。
★ 窓の進行は**実測経過 `tick_ms` の累積**で決める (壁時計を読まない) → 決定的にテストできる。

### 3.4 `dropped_delta`

⚠️ 現行の `prev_dropped` は **`tracing` に出したときだけ**更新される (`lib.rs:2884-2891`)。
→ ★ 流用すると「前回**行**からの差分」にならない。**`dropped_at_last_line` を別に持ち、
`hook_health` 行を送った直後に更新する。**

### 3.5 G-1 (§1.1 / §1.2)

`RotateForRestart` の枝は `Rotate` を 1 通送るだけ。⚠️ ローテート先パスは既存と同じく
`logger::next_session_path()` で、一意化は**ロガースレッド側**が行う (`logger.rs:1604`)。

---

## 4. 既存パターンとの整合性

| 既存パターン | v2 での踏襲 |
|---|---|
| 「純関数 + 引数で閾値」(`liveness::step` / `health`) | `decide_start_action` / 窓集計器を同じ形にする |
| 「プラットフォーム分岐を引数に追い出す」(`g1::folder_up`) | `capabilities` は `#[cfg]` を**表の構築時 1 箇所**に閉じる |
| 「数えるのではなく突き合わせる」(`submission.rs:23`) | ★ 新しい永続カウンタを作らない (判断 4) |
| fail-loud + 巻き戻し (`lib.rs:2020-2033`) | ★ **触る前に断る**へ強化 (巻き戻せない副作用を作らない) |
| additive schema versioning (ADR-005) | `required` を増やさない・型を変えない |

---

## 5. テスト戦略 (= ADR-013 D3 の acceptance)

| # | テスト名 | 何を固定するか | 置き場 |
|---|---|---|---|
| 1 | `capabilities_covers_every_line_type` | `include_str!("logger.rs")` の `"type":"<x>"` 走査 → `KNOWN_LINE_TYPES` に無ければ落ちる。⚠️ 既知の限界: フィクスチャのリテラルも拾う (**過大側＝見落とさない方向**) | `capabilities.rs` |
| 2a | `ime_shadow_declared_on_windows` | `#[cfg(target_os="windows")]` | 同上 |
| 2b | `ime_shadow_not_declared_on_macos` | `#[cfg(target_os="macos")]` | 同上 |
| 3 | `every_capability_has_a_reachable_emitter` | 宣言の各要素に送出元がある (**過大申告の逆アサート**) | 同上 |
| 4 | `starve_window_omits_empty_windows` | `n_lt30 == 0` の窓が 1 行も出ない | `liveness.rs` |
| 5 | `starve_window_counts_only_micro_episodes` | `peak >= log_after_ms` を数えない (二重計上しない) | 同上 |
| 6 | `dropped_delta_is_per_line_difference` | 合成入力で「前回**行**からの差分」 | `lib.rs` or `logger.rs` |
| 7 | `hook_health_semantics_unchanged` | ⚠️★★★ 出力条件 (状態変化 or rehook) と `starved_ms` の意味 (復帰行はピーク) が不変 | `liveness.rs` |
| 8 | `decide_start_action_*` (表 §1.2 の 4 行) | ★ 通常運用が `NoRotate` であること / 二度押しが `RotateForRestart` であること | `lib.rs` |
| 9 | `double_start_rotates_and_closes_previous` | ロガー結合: 旧ファイルに `session_end` 1 個・新ファイルに `meta` + `session_start` | `logger.rs` tests |
| 10 | `log_capacity_guard_rejects_when_full` | 容量不足で**何も触らずに** Err | `lib.rs` |
| 11 | schema parity | `emit_schema` == `schema/current.json` かつ `check_schema_parity.py --dataset …` exit 0 | CI + 手動 |
| 12 | ★ **独立ゲート** `validate_blocks.py --selftest` | 「1 ファイルに `session_start` 2 本 → FAIL」が緑のまま (★ 解析側から G-1 を検算) | Python |

⚠️ 3 の**既知の限界**は正直に書く: 「送出元がある」ことしか言えず、**バグで一度も呼ばれない**
可能性は残る (ADR-013 Consequences 逐語)。→ ★ だから `app_version` を併記する。

---

## 6. 却下した案 (★ 記録する)

| 却下案 | 理由 |
|---|---|
| **`capabilities` を別行 `{"type":"capabilities",…}` にする** | ★ byte-equality の不安が動機だったが、**0.1-A で実測し不安が消えた**。Accepted な ADR-013 D1 の形を根拠なく変えない |
| **`LogEntry::SessionEnd` を新設して 3 通送る** (handoff §2 の字面) | ★ 0.1-C の実測で **`Rotate` が既に全部やる**と判明。⚠️ 新設すると `session_end` を書く経路が 2 本になり `block_closed` の不変条件が二重化する |
| **失敗したら巻き戻す** (v1 案) | ⚠️ `engine.reset()` 等は `swap` より前で**巻き戻せない**。→ **触る前に断る**へ (§1.1) |
| **`!was_active` を外して無条件ローテート** | ⚠️ code-review HIGH の再導入 (判断 8) |
| **`log_after_ms` を下げて micro 帯を見る** | ⚠️ `hook_health` の意味論が変わる ＝ **要件の Stop 条件** (ADR-013 D4) |
| **`starve_window` を毎分無条件に出す** | ⚠️ 在席の連続タイムラインになる (D4 / security-checker MEDIUM) |

---

## 7. 検証手順 (`src-tauri/` から)

```bash
cd src-tauri
cargo test --workspace
for f in minimal deep_silence category_coverage phase1_ime_heavy argumentative_ime_mixed vibe_coding_ime_mixed; do
  cargo run --bin gse-replay -- tests/fixtures/$f.ndjson --snapshot tests/snapshots/$f.json
done
cargo run --bin emit_schema      # → schema/current.json と byte-equal
cd .. && PYTHONUTF8=1 python scripts/check_schema_parity.py --dataset <gse-dataset>   # ⚠️ --dataset 必須
PYTHONUTF8=1 python experiments/20260801-controlled-friction-task/validate_blocks.py --selftest
PYTHONUTF8=1 python experiments/20260801-controlled-friction-task/analyze.py --selftest
```

## 設計判断の履歴

- 実行回数: 1 回目
- 採用: **v2**
- 根拠: v1 が「未解決」と自認した巻き戻せない副作用を、回避ではなく**消去**している (guard-first)。
  設計前に 4 件を実測しており、handoff §2 の「3 手順が要る」が不要と判明して変更面積が減った。
  `validate_blocks.py --selftest` を解析側の独立ゲートに使う点も v1 に無い。
