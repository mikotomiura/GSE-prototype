---
name: hook-constraints
description: >
  GSE の WH_KEYBOARD_LL フックコールバック・WinEvent コールバック（Windows）および
  CGEventTap コールバック・GCD dispatch（macOS）内での実装制約。
  hook.rs / hook_windows.rs / hook_macos.rs / ime.rs / ime_macos.rs を
  書く・修正する・デバッグするときに必須参照。
  以下の状況で必須参照:
  - hook_windows.rs の LowLevelKeyboardProc コールバック内にコードを追加するとき
  - hook_macos.rs の CGEventTap コールバック内にコードを追加するとき
  - ime_macos.rs で dispatch_sync_f を呼ぶコードを書くとき
  - TCC 権限 (Input Monitoring / Accessibility) のフォールバックロジックを修正するとき
  - フックスレッドから他スレッドへデータを渡すコードを書くとき
  - LAST_KEY_MS / IME_OPEN / IME_ACTIVE / CONSECUTIVE_TAP_FAILURES などの Atomic フラグを操作するとき
  - フックコールバックで「なぜこれはできないのか」を確認したいとき
allowed-tools: Read, Grep, Glob
---

# フックコールバック制約

## このスキルの目的

OS レベルのキーボードフック・WinEvent コールバック（Windows）および
CGEventTap コールバック（macOS）は極めて厳しい制約下で動作する。
違反するとシステム全体のキーボード入力が遅延・フリーズする。
何ができて何ができないかを明確にする。

## 適用範囲

### 適用するもの
- `src-tauri/src/input/hook_windows.rs` の `LowLevelKeyboardProc` コールバック
- `src-tauri/src/input/hook_macos.rs` の CGEventTap コールバック
- `src-tauri/src/input/ime_windows.rs` の WinEvent コールバック
- `src-tauri/src/input/ime_macos.rs` の GCD dispatch 呼び出し
- フックスレッドで動作するすべてのコード

### 適用しないもの
- Analysis スレッド（1Hz ゲート駆動、制約なし）
- Logger スレッド（バックグラウンド I/O、制約なし）

---

## Windows 固有ルール

### Win-1: コールバック内で許可されるのは 2 種類のみ

```
✅ 許可: Atomic 操作 (load / store / fetch_add など)
✅ 許可: crossbeam channel の try_send（ノンブロッキング）
❌ 禁止: それ以外すべて
```

```rust
// ✅ 良い例（Windows hook コールバック）
extern "system" fn low_level_keyboard_proc(code: i32, wparam: WPARAM, lparam: LPARAM) -> LRESULT {
    if code >= 0 {
        LAST_KEY_MS.store(now_ms(), Ordering::Relaxed);
        let _ = TX.get().map(|tx| tx.try_send(event));
    }
    unsafe { CallNextHookEx(None, code, wparam, lparam) }
}
```

### Win-2: CallNextHookEx は必ず呼ぶ

処理の有無に関わらず、コールバック末尾で `CallNextHookEx` を呼ぶ。
呼ばないと他のアプリのキーボードフックが動作しなくなる。

```rust
// ✅ 必ず末尾に（条件分岐で省略しない）
unsafe { CallNextHookEx(None, code, wparam, lparam) }
```

---

## macOS 固有ルール

### mac-1: CGEventTap コールバック内の制約（Windows と同じ）

```
✅ 許可: Atomic 操作
✅ 許可: crossbeam channel の try_send（ノンブロッキング）
✅ 許可: CGKeyCode → VK マッピングテーブルの読み取り（読み取り専用）
❌ 禁止: Mutex::lock(), ブロッキング send, I/O, ヒープアロケーション, tracing ログ
```

```rust
// ✅ 良い例（macOS CGEventTap コールバック）
extern "C" fn event_tap_callback(
    _proxy: CGEventTapProxy,
    event_type: CGEventType,
    event: CGEventRef,
    user_info: *mut c_void,
) -> CGEventRef {
    let vk = cgkeycode_to_vk(keycode);  // テーブル読み取り: OK
    LAST_KEY_MS.store(now_ms(), Ordering::Relaxed);  // Atomic: OK
    let _ = tx.try_send(input_event);  // try_send: OK
    event  // 必ず event を返す（または null でイベントを消費）
}
```

### mac-2: dispatch_sync_f はメインスレッドから呼ばない

`dispatch_sync_f` でメインキューにディスパッチする場合、**必ず別スレッドから呼ぶ**。
メインスレッドから `dispatch_sync_f(main_queue, ...)` を呼ぶとデッドロックする。

```rust
// ✅ 良い例 — IME ポーリングスレッドから呼ぶ
std::thread::spawn(|| {
    loop {
        unsafe {
            dispatch_sync_f(dispatch_get_main_queue(), ptr, callback);
        }
        std::thread::sleep(Duration::from_millis(100));
    }
});

// ❌ 悪い例 — Tauri コマンドハンドラ（メインスレッド）から呼ぶ
#[tauri::command]
fn check_ime() {
    unsafe { dispatch_sync_f(dispatch_get_main_queue(), ptr, callback); }  // デッドロック！
}
```

### mac-3: CGEventTap が無効化されたら自動再作成する

macOS はアプリが重い処理をすると CGEventTap を自動的に無効化する。
無効化を検知したら 3 秒ポーリングで再作成する（ブロッキングしない）。

```rust
// ✅ 良い例 — タップ無効化の検知と再作成ループ
if event_type == kCGEventTapDisabledByTimeout || event_type == kCGEventTapDisabledByUserInput {
    CONSECUTIVE_TAP_FAILURES.fetch_add(1, Ordering::Relaxed);
    // コールバック内では再作成しない。Hook Thread のポーリングループで対処。
}

// Hook Thread のメインループ
loop {
    if !tap_is_enabled() {
        recreate_event_tap();
    }
    std::thread::sleep(Duration::from_secs(3));
}
```

### mac-4: TCC 権限フォールバックチェーン

Input Monitoring → Accessibility の順でフォールバックする。
両方なければ ListenOnly モードに落とす（部分的な機能のみ）。

```
Input Monitoring 許可あり → CGEventTap (HeadInsertEventTap) — フル機能
Input Monitoring なし + Accessibility 許可あり → CGEventTap (TailAppendEventTap) — フル機能
どちらもなし → ListenOnly (CGEventTap passive) — キー種別のみ取得
```

```rust
// ✅ フォールバックチェーンの実装パターン
let tap = if has_input_monitoring() {
    create_head_insert_tap()
} else if has_accessibility() {
    USING_ACCESSIBILITY_FALLBACK.store(true, Ordering::Release);
    create_tail_append_tap()
} else {
    create_listen_only_tap()
};
```

### mac-5: AXIsProcessTrustedWithOptions はメインスレッドで呼ぶ

`AXIsProcessTrustedWithOptions` (Accessibility 許可チェック + ダイアログ表示) は
**必ず GCD でメインスレッドに dispatch してから呼ぶ**。

```rust
// ✅ 良い例 — GCD でメインスレッドに dispatch
unsafe {
    dispatch_async_f(dispatch_get_main_queue(), ptr, |ctx| {
        let trusted = AXIsProcessTrustedWithOptions(options);
        // ...
    });
}

// ❌ 悪い例 — バックグラウンドスレッドから直接呼ぶ
std::thread::spawn(|| {
    let trusted = unsafe { AXIsProcessTrustedWithOptions(options) };  // UI が表示されない
});
```

---

## 共通ルール

### 共通-1: 禁止操作一覧（Win/mac 共通）

| 禁止操作 | 理由 |
|---|---|
| `Mutex::lock()` | デッドロック・ブロッキングのリスク |
| `channel.send()` (ブロッキング) | 受け手が詰まるとフック全体が止まる |
| `std::fs::write()` 等の I/O | システムコール = レイテンシ増大 |
| `Vec::push()` 等のヒープアロケーション | アロケータが内部 Mutex を持つ |
| `tracing::info!()` 等のログ | バッファ操作・アロケーションを伴う |
| `thread::sleep()` | 論外 |
| `Arc<Mutex<T>>` の lock 取得 | ロック取得がブロッキング |

### 共通-2: グローバル Atomic 変数の Ordering

```rust
// LAST_KEY_MS: 近似値で十分 → Relaxed で OK
LAST_KEY_MS.store(now_ms(), Ordering::Relaxed);

// IME_OPEN / IME_ACTIVE: Analysis スレッドとの可視性保証が必要
// → store は Release、load は Acquire
IME_OPEN.store(true, Ordering::Release);     // ime.rs 内
let open = IME_OPEN.load(Ordering::Acquire); // analysis/engine.rs 内

// [macOS] CONSECUTIVE_TAP_FAILURES: カウンタ → SeqCst 不要、Relaxed で OK
CONSECUTIVE_TAP_FAILURES.fetch_add(1, Ordering::Relaxed);
```

### 共通-3: イベントドロップは許容する

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

## チェックリスト

**共通**
- [ ] コールバック内に Mutex::lock() がないか
- [ ] コールバック内にブロッキング channel send がないか
- [ ] コールバック内に I/O 操作がないか
- [ ] コールバック内にヒープアロケーションがないか
- [ ] コールバック内に tracing ログがないか
- [ ] IME フラグの Ordering が Acquire/Release になっているか

**Windows のみ**
- [ ] CallNextHookEx をすべてのコードパスで呼んでいるか

**macOS のみ**
- [ ] dispatch_sync_f をメインスレッドから呼んでいないか
- [ ] AXIsProcessTrustedWithOptions を GCD メインスレッド経由で呼んでいるか
- [ ] CGEventTap 無効化時の再作成ループがあるか
- [ ] TCC フォールバックチェーン（IM → AX → ListenOnly）を維持しているか

---

## 補足資料

- `anti-patterns.md` — やってしまいがちな違反パターンと症状（Win/mac 両方）

## 関連する他の Skill

- `rust-standards` — unsafe 隔離・Atomic Ordering の一般規則
- `architecture-rules` — input/ モジュールの責務範囲
