# 設計: Phase 2b IME Shadow Features

## 実装アプローチ

**Atomic + Monitor Emit パターン**: フックコールバック内ではAtomic操作のみ行い、
LogEntry の組み立て・送信は既存の IME Monitor スレッドに委譲する。

### なぜこのパターンか

1. **フックコールバック制約の遵守**: `hook_windows.rs` の WinEvent / LowLevelKeyboardProc
   コールバック内は Atomic + channel send のみ (CLAUDE.md §技術的制約 4)
2. **既存チャネルの再利用**: IME Monitor スレッドは既に `log_tx_for_monitor` を持ち、
   `ImeState` ログを送出している。ImeShadow も同経路で送出する
3. **新 OnceLock 不要**: フックスレッドに log_tx を渡す新チャネルを追加しない

### データフロー

```
WinEvent IME_SHOW  → IME_COMPOSITION_START_MS.store(now)
WinEvent IME_HIDE  → IME_SHADOW_DWELL_MS.store(now - start)
                     IME_SHADOW_READY.store(true)

hook_callback      → IME_ACTIVE && arrow key → IME_CANDIDATE_NAV_COUNT.fetch_add(1)
                     IME_ACTIVE && ESC key   → IME_SHADOW_ABANDON.store(true)

IME Monitor Thread → active→false 遷移検出時:
                     if IME_SHADOW_READY.swap(false) {
                       dwell = IME_SHADOW_DWELL_MS.swap(0)
                       nav   = IME_CANDIDATE_NAV_COUNT.swap(0)
                       abn   = IME_SHADOW_ABANDON.swap(false)
                       log_tx.try_send(LogEntry::ImeShadow { ... })
                     }
```

### Safety Valve との連携

IME Monitor の 8 秒スタレ検出で IME_ACTIVE を強制リセットする場合も、
`IME_SHADOW_READY` をチェックして溜まった shadow データを emit する。
WinEvent IME_HIDE が来なかった（取りこぼした）場合は dwell を現在時刻 - start で計算。

## 変更対象

### 修正するファイル

| ファイル | 変更内容 |
|---|---|
| `src-tauri/src/input/hook.rs` | Windows 専用 Atomic 5 個追加 + AtomicU32 import を非条件化 |
| `src-tauri/src/input/hook_windows.rs` | WinEvent: IME_SHOW/HIDE で shadow Atomic 更新。hook_callback: arrow/ESC カウント |
| `src-tauri/src/logger.rs` | `LogEntry::ImeShadow` バリアント追加 + match アーム追加 |
| `src-tauri/src/schema_dto.rs` | `LogEntryDto::ImeShadow` バリアント追加 |
| `src-tauri/src/lib.rs` | IME Monitor スレッドの active→false 遷移で ImeShadow emit |
| `src-tauri/src/bin/replay.rs` | `ReplayEvent::ImeShadow` 読み飛ばしバリアント追加 |
| `src-tauri/schema/current.json` | `cargo run --bin emit_schema` で再生成 |

### 新規作成するファイル
- なし

### 削除するファイル
- なし

## 新規 Atomic 変数 (すべて `#[cfg(target_os = "windows")]`)

| 名前 | 型 | 用途 | 書き手 | 読み手 |
|---|---|---|---|---|
| `IME_COMPOSITION_START_MS` | AtomicU64 | IME_SHOW 時刻 | WinEvent | WinEvent (HIDE時に差分計算) |
| `IME_SHADOW_DWELL_MS` | AtomicU64 | 計算済み dwell | WinEvent | IME Monitor |
| `IME_CANDIDATE_NAV_COUNT` | AtomicU32 | 矢印キー回数 | hook_callback | IME Monitor |
| `IME_SHADOW_ABANDON` | AtomicBool | ESC 押下有無 | hook_callback | IME Monitor |
| `IME_SHADOW_READY` | AtomicBool | emit 準備完了 | WinEvent | IME Monitor |

## LogEntry::ImeShadow

```rust
/// IME 変換セッションの影ログ (Phase 2b, Windows のみ)
/// HMM には統合しない。Phase 3 のデータ判断材料として蓄積。
ImeShadow {
    timestamp: u64,
    dwell_ms: u64,
    candidate_nav_count: u32,
    abandon: bool,
},
```

NDJSON 出力:
```json
{"type":"ime_shadow","t":1713345600000,"dwell_ms":1234,"nav":3,"abandon":false}
```

## 影響範囲

| 領域 | 影響 | 対処 |
|---|---|---|
| macOS ビルド | 新 Atomic は `#[cfg(windows)]` ゲート | CI で検証 |
| ゴールデンスナップショット | 既存 fixture に ime_shadow 行なし → 差分なし | replay.rs に読み飛ばし追加 |
| schema/current.json | 新バリアント追加 → drift | emit_schema 再生成 |
| HMM 推論 | 変更なし | Phase 0 snapshot で回帰確認 |

## 既存パターンとの整合性

- **Atomic 宣言**: `IME_ACTIVE`, `IME_OPEN` と同じ位置・命名規則に従う
- **LogEntry バリアント追加**: `ReviewMarker` 追加時と同じ手順 (logger + schema_dto + replay)
- **WinEvent 拡張**: 既存の IME_SHOW/HIDE ハンドラを拡張
- **Monitor emit**: 既存の ImeState emit パターンに ImeShadow を追加

## テスト戦略

- **単体テスト (logger.rs)**: ImeShadow の NDJSON フォーマット検証
- **回帰テスト**: `cargo test` 全通過 (既存 69 テスト)
- **ゴールデンスナップショット**: `gse-replay --snapshot` で既存 fixture の差分なし確認
- **schema drift**: `cargo run --bin emit_schema` → `schema/current.json` 一致確認
- **macOS ビルド**: CI matrix で検証 (ローカルでは `#[cfg]` ゲートの正しさを確認)

## レビューで追加した改善

1. **Atomic ordering コメント** (HIGH): `IME_SHADOW_READY` の Release/Acquire フェンス設計意図を hook.rs に明記
2. **IME_CHANGE defensive fallback** (MEDIUM): `EVENT_OBJECT_IME_CHANGE` で `START_MS=0` の場合のみ現在時刻を store
3. **Stale リセット emit** (MEDIUM): `emit_ime_shadow` に stale 経路を追加 — `READY=false` でも `START_MS > 0` なら独自に dwell 計算して emit
4. **既知の制約コメント** (MEDIUM): フックのグローバル性・WinEvent タイミングずれを hook_windows.rs に記録

## ロールバック計画

全変更は単一コミット。git revert で即座に戻せる。
HMM パラメータ・既存 LogEntry には一切変更がないため、revert 後の
データ互換性問題は発生しない。
