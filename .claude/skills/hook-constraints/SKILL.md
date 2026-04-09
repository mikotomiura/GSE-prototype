---
name: hook-constraints
description: >
  GSE の WH_KEYBOARD_LL フックコールバックおよび WinEvent コールバック内での
  実装制約。hook.rs / ime.rs を書く・修正する・デバッグするときに必須参照。
  以下の状況で必須参照:
  - hook.rs の LowLevelKeyboardProc コールバック内にコードを追加するとき
  - ime.rs の WinEvent コールバック内にコードを追加するとき
  - フックスレッドから他スレッドへデータを渡すコードを書くとき
  - LAST_KEY_MS / IME_OPEN / IME_ACTIVE などの Atomic フラグを操作するとき
  - フックコールバックで「なぜこれはできないのか」を確認したいとき
allowed-tools: Read, Grep, Glob
---

# フックコールバック制約

## このスキルの目的

OS レベルのキーボードフック・WinEvent コールバックは極めて厳しい制約下で動作する。
違反するとシステム全体のキーボード入力が遅延・フリーズする。
何ができて何ができないかを明確にする。

## 適用範囲

### 適用するもの
- `src-tauri/src/input/hook.rs` の `LowLevelKeyboardProc` コールバック
- `src-tauri/src/input/ime.rs` の WinEvent コールバック
- フックスレッドで動作するすべてのコード

### 適用しないもの
- Analysis スレッド（1Hz ゲート駆動、制約なし）
- Logger スレッド（バックグラウンド I/O、制約なし）

---

## 主要なルール

### ルール 1: コールバック内で許可されるのは 2 種類のみ

```
✅ 許可: Atomic 操作 (load / store / fetch_add など)
✅ 許可: crossbeam channel の try_send（ノンブロッキング）
❌ 禁止: それ以外すべて
```

```rust
// ✅ 良い例（hook コールバック）
extern "system" fn low_level_keyboard_proc(code: i32, wparam: WPARAM, lparam: LPARAM) -> LRESULT {
    if code >= 0 {
        // Atomic store: OK
        LAST_KEY_MS.store(now_ms(), Ordering::Relaxed);
        // try_send: OK（失敗しても無視）
        let _ = TX.get().map(|tx| tx.try_send(event));
    }
    unsafe { CallNextHookEx(None, code, wparam, lparam) }
}
```

---

### ルール 2: 禁止操作と理由

| 禁止操作 | 理由 |
|---|---|
| `Mutex::lock()` | デッドロック・ブロッキングのリスク |
| `channel.send()` (ブロッキング) | 受け手が詰まるとフック全体が止まる |
| `std::fs::write()` 等の I/O | システムコール = レイテンシ増大 |
| `Vec::push()` 等のヒープアロケーション | アロケータが内部 Mutex を持つ |
| `tracing::info!()` 等のログ | バッファ操作・アロケーションを伴う |
| `thread::sleep()` | 論外 |
| 他スレッドの状態を `Arc<Mutex<T>>` で読む | ロック取得がブロッキング |

---

### ルール 3: グローバル Atomic 変数の Ordering

GSE でのパターン:

```rust
// LAST_KEY_MS: 近似値で十分 → Relaxed で OK
LAST_KEY_MS.store(now_ms(), Ordering::Relaxed);

// IME_OPEN / IME_ACTIVE: Analysis スレッドとの可視性保証が必要
// → store は Release、load は Acquire
IME_OPEN.store(true, Ordering::Release);     // ime.rs 内
let open = IME_OPEN.load(Ordering::Acquire); // analysis/engine.rs 内
```

---

### ルール 4: イベントドロップは許容する

チャネルが満杯のときは `try_send` の失敗を無視する。
警告ログは Analysis スレッドで統計的に記録する（コールバック内では書かない）。

```rust
// ✅ 良い例
let _ = tx.try_send(event);  // 失敗は無視

// ❌ 悪い例
if tx.try_send(event).is_err() {
    tracing::warn!("dropped");  // コールバック内でのログ禁止
}
```

---

### ルール 5: CallNextHookEx は必ず呼ぶ

処理の有無に関わらず、コールバック末尾で `CallNextHookEx` を呼ぶ。
呼ばないと他のアプリのキーボードフックが動作しなくなる。

```rust
// ✅ 必ず末尾に
unsafe { CallNextHookEx(None, code, wparam, lparam) }
```

---

## チェックリスト

- [ ] コールバック内に Mutex::lock() がないか
- [ ] コールバック内にブロッキング channel send がないか
- [ ] コールバック内に I/O 操作がないか
- [ ] コールバック内にヒープアロケーションがないか
- [ ] コールバック内に tracing ログがないか
- [ ] IME フラグの Ordering が Acquire/Release になっているか
- [ ] CallNextHookEx を呼んでいるか

---

## 補足資料

- `anti-patterns.md` — やってしまいがちな違反パターンと症状

## 関連する他の Skill

- `rust-standards` — unsafe 隔離・Atomic Ordering の一般規則
- `architecture-rules` — input/ モジュールの責務範囲
