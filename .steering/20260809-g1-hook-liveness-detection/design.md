# 設計 — キーボードフックの silent death 検知

## アプローチ

★ **「フックとは独立した情報源」と「自前のフックが呼ばれた回数」を突き合わせる。**
3 層に分け、**判断だけを OS 非依存の純関数**に閉じ込める。

### 層 1: 測る（platform・新規 `input/liveness.rs`）

```rust
/// 最後の「システム全体の入力」からの経過 ms。★ フックとは無関係に OS が持っている値。
pub fn system_idle_ms() -> Option<u64>
```

- **Windows**: `GetLastInputInfo()` の `dwTime`（tick）と `GetTickCount64()` の**差**を取る。
  ★ epoch 変換をしない ＝ ⚠️ 32bit tick のラップアラウンドを踏まない。
- **macOS**: `None` を返す（D-4: 今回は配線しない ＝ 判定は常に `Ok`）。
- ⚠️★ **キーの内容も種別も読まない。**「最後に何か入力があった時刻」だけ（`data-privacy` 適合）。
- ⚠️ `GetLastInputInfo` は**マウスを含む** → 後述の「誤検知」を参照。

### 層 2: 判断する（★ OS 非依存の純関数・同ファイル内）

```rust
pub enum HookHealth { Ok, Suspect, Down }

pub fn assess(
    session_active: bool,
    hook_silence_ms: u64,        // 自前のフックが最後に呼ばれてからの経過
    system_idle_ms: Option<u64>, // OS 側の最終入力からの経過 (None = 判定不能)
    log_after_ms: u64,           // 既定 30_000
    down_after_ms: u64,          // 既定 120_000
) -> HookHealth
```

判定: **セッション中** かつ **OS 側には入力がある**（`system_idle_ms` が小さい）かつ
**自前のフックは沈黙している**（`hook_silence_ms` が閾値超え）→ `Suspect` / `Down`。

★ 閾値は**定数ではなく引数**（D-1）。境界を単体テストで固定できる。

### 層 3: 配線する（`lib.rs` に 1 Hz 監視スレッド）

★ **トレイのスレッドには載せない。** トレイは生成に失敗しうる（`Failed to build the tray icon`）ので、
そこに載せると**検知ごと消える**。独立スレッドにする。

| 状態 | すること |
|---|---|
| `Suspect` | `tracing::error!` を **1 回だけ**（★ 1 Hz で連発しない）＋ NDJSON に `hook_health` 行 |
| `Down` | `HOOK_ACTIVE=false` ＋ 再設置要求（下記）＋ `hook_health` 行 |
| 復帰（フックが呼ばれた） | `hook_health` 行（`alive:true`）＋ 内部状態を戻す |

★★ **トレイ (`tray.rs`) は 1 行も変えない。** `measure_state()` は既に `HOOK_ACTIVE` を見るので、
`HOOK_ACTIVE=false` にすれば **自動的に `⚠ GSE — 計測できていません` になる**（＝ 経路を増やさない）。

## ★ フックの生存信号をどう取るか（Step B で判明した穴）

⚠️ `CALLBACK_COUNT` は **macOS でしか `fetch_add` していない**（`hook_macos.rs:304`。
Windows 側には呼び出し回数の指標が**無い**）。

→ **`hook_windows.rs` のコールバックに `CALLBACK_COUNT.fetch_add(1, Relaxed)` を 1 行足す。**

- ★ `hook-constraints` Win-1 で **Atomic 操作は許可**されている唯一の 2 種のうちの 1 つ。
- ★ `LAST_KEY_MS` ではなく **単調増加カウンタ**を使う理由: `LAST_KEY_MS` は再設置時に **0 にリセット
  される**（`hook_windows.rs:230` 付近）ので「沈黙の長さ」の基準として不安定。
  ⚠️ ★ **これは memory `macos-tap-idle-away-probe-bug`（`LAST_KEY_MS=0` が idle/away を壊した）と同型の罠**。

## ★ 自動復旧（D-3）— 新しい経路を書かない

既存の「メッセージループを抜けてループ先頭で再設置」経路（`hook_windows.rs:227-236`）を**そのまま使う**。
起こし方は `PostThreadMessageW(hook_thread_id, WM_QUIT, 0, 0)` の 1 発。

- フックスレッド起動時に `GetCurrentThreadId()` を `HOOK_THREAD_ID: AtomicU32` に保存する。
- ⚠️★ **バックオフ必須**: 再設置要求は最短 N 秒に 1 回。★ 再設置しても直らない場合に
  1 Hz で unhook/re-hook を撃ち続けると、**入力を取りこぼし続ける**。

## NDJSON の新しい行型（D-2）

```json
{"type":"hook_health","t":…,"alive":false,"hook_silence_ms":137000,"system_idle_ms":1200,"action":"rehook"}
```

★★ **判断（真偽）ではなく、測った量を載せる。** 後から閾値を変えて**再解釈できる**ようにする
（⚠️ 今回まさに「後から見分けられない」ことで詰まったので、そこを設計で塞ぐ）。

消費側への影響（★ すべて一次資料で確認済み）:

| 消費側 | 影響 |
|---|---|
| `gse-replay` | ✅ **なし**。未知 `type` は `serde` エラー → **`continue` で読み飛ばす**（`replay.rs:1100-1104`）→ ゴールデン 15 本は byte-equal のまま |
| `validate_blocks.py` | ✅ **なし**。`FORBIDDEN_LINE_TYPES` は probe 3 種のみ＝**許可リスト方式ではない**（`:67`） |
| `analyze.py` | ✅ **なし**。`key` / `feat` / `ime_shadow` / `paste` しか読まない |
| `schema_dto.rs` / `emit_schema` | ⚠️ **要更新**。variant 追加 → `schema/current.json` 再生成 → byte-equal 検査 → gse-dataset parity |

## ⚠️★ 誤検知について（正直に書く）

`GetLastInputInfo` は **マウスも含む**。★ したがって
**「2 分間ずっと読んで・スクロールしていただけ」は `Down` に化けうる**。

- 緩和: 閾値を二段にし（ログ 30 s / トレイ 120 s）、**トレイ表示は保守的**にする（D-1）。
- ★ **NDJSON に測定値そのものを残す**ので、誤検知かどうかは**後から判定できる**。
- ⚠️ それでも「被験者の画面に ⚠ が誤って出る」ことは**ありうる**。
  ★ 文言は既存の 3 状態のまま増やさない（D-5・盲検と介入規制）。

## 既存パターンとの整合

| 既存 | 本タスクでの扱い |
|---|---|
| macOS の `CONSECUTIVE_TAP_FAILURES` ＋ 3 秒ポーリング再作成（`hook-constraints` mac-3） | ★ **同じ形**（コールバックでは直さず、別ループが直す）を Windows に持ち込む |
| `tray.rs` の 1 Hz 監視スレッド | ★ 同じ書式（`is_shutting_down()` で抜ける）で新スレッドを書く |
| `ime.rs` のポーリングスレッド | 同上 |
| 終了経路の一本化（`shutdown_and_exit`） | ★ **経路を増やさない**という同じ原則を再設置にも適用（既存経路を起こすだけ） |

## 変更対象ファイル

- **新規** `src-tauri/src/input/liveness.rs` — `system_idle_ms()` ＋ 純関数 `assess()` ＋ 単体テスト
- `src-tauri/src/input/mod.rs` — `pub mod liveness;`
- `src-tauri/src/input/hook.rs` — `HOOK_THREAD_ID: AtomicU32` を追加
- `src-tauri/src/input/hook_windows.rs` — コールバックに `CALLBACK_COUNT.fetch_add` 1 行 ／ スレッド ID 保存
- `src-tauri/src/lib.rs` — 監視スレッド起動、`LogEntry::HookHealth` 送信
- `src-tauri/src/logger.rs` — `LogEntry::HookHealth` の追加と書き出し
- `src-tauri/src/schema_dto.rs` — `LogEntryDto` に `HookHealth` variant
- `src-tauri/schema/current.json` — `emit_schema` で再生成
- ★ `src-tauri/src/tray.rs` — **変更しない**（`HOOK_ACTIVE` 経由で自動的に ⚠ になる）

## テスト戦略

```bash
cd src-tauri
cargo test --workspace                                   # 純関数の単体テスト
cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json
cargo run --bin emit_schema                              # → schema/current.json と byte-equal
```

- **`assess()` の単体テスト（5 ケース）**: 正常 ／ フック死 ／ ⚠️ **マウスのみ**
  （★ これも `Down` になることを**明示的に固定する** = 誤検知の存在を仕様として書き残す）／
  セッション非活性 ／ `system_idle_ms = None`（macOS）
- ★★ **わざと壊して赤を実測**: (1) 閾値比較の向きを反転、(2) `session_active` の判定を外す、
  (3) `None` を `Ok` ではなく `Down` に倒す — の 3 通り
- ゴールデン 15 snapshots が **byte-equal**（＝ `feat` 列に触れていない証拠）
- ⚠️★ **Windows 実機での「実際に発火する」確認はできない**（開発機は macOS）。
  → 受け入れ条件どおり **「未実施」と書く**。★ 「動くはず」と書かない。

## ⚠️ この設計で**やらないこと**（再掲・D-5）

- ブロックの自動やり直し（`protocol.md:1082`）
- 被験者向けの新しい文言・通知
- `HMM_VERSION` の bump（HMM の挙動は変えない）
- macOS 側の配線（純関数は共用できる形にするが、`CGEventSourceSecondsSinceLastEventType` は次タスク）
