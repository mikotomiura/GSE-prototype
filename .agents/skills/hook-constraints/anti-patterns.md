# hook-constraints: 違反パターンと症状

> Windows と macOS 両プラットフォームの違反パターンを記載。

## Windows 違反パターン

## 1. Mutex をコールバック内で取得する

```rust
// ❌ 違反
extern "system" fn callback(...) -> LRESULT {
    let mut engine = ENGINE.lock().unwrap();  // デッドロックリスク
    engine.register_keystroke(event);
    unsafe { CallNextHookEx(None, code, wparam, lparam) }
}
```

**症状**: キーボード入力が数秒フリーズ。Analysis スレッドが同じ Mutex を持ったままスリープすると即デッドロック。

**正しい実装**: `try_send` でチャネルに投げ、Analysis スレッドで Mutex を取る。

---

## 2. ブロッキング send を使う

```rust
// ❌ 違反
let _ = tx.send(event);  // 受け手が詰まるとここで止まる
```

**症状**: Analysis スレッドが重い処理をしているとき、フックが止まる。入力遅延が体感できる。

**正しい実装**: `tx.try_send(event)` でドロップを許容する。

---

## 3. ログをコールバック内に書く

```rust
// ❌ 違反
extern "system" fn callback(...) -> LRESULT {
    tracing::debug!("key pressed: vk={}", vk);  // 内部バッファ操作
    ...
}
```

**症状**: 大量入力時にログバッファが詰まり、入力遅延が増大。

**正しい実装**: チャネルで送った InputEvent を Analysis スレッド側でログ出力する。

---

## 4. CallNextHookEx を条件分岐で省略する

```rust
// ❌ 違反
extern "system" fn callback(...) -> LRESULT {
    if code < 0 { return LRESULT(0); }  // CallNextHookEx を呼ばずに return
    // ...
}
```

**症状**: IME、スクリーンリーダー、他のキーボードフックが動作しなくなる。

**正しい実装**:

```rust
extern "system" fn callback(...) -> LRESULT {
    if code >= 0 {
        // 処理
    }
    unsafe { CallNextHookEx(None, code, wparam, lparam) }  // 常に末尾で呼ぶ
}
```

---

## macOS 違反パターン

## 5. dispatch_sync_f をメインスレッドから呼ぶ

```rust
// ❌ 違反 — Tauri コマンドハンドラ（メインスレッド）から呼ぶ
#[tauri::command]
fn check_ime_state() {
    unsafe {
        dispatch_sync_f(dispatch_get_main_queue(), ptr, ime_callback);
        // ↑ メインスレッドが自分自身への同期ディスパッチを待つ → 即デッドロック
    }
}
```

**症状**: アプリが無応答になる。UI がフリーズしたまま戻らない。

**正しい実装**: IME ポーリングは専用スレッドを立てて、そこから `dispatch_sync_f` を呼ぶ。

```rust
// ✅ 正しい実装 — 専用ポーリングスレッドから呼ぶ
std::thread::spawn(|| {
    loop {
        unsafe { dispatch_sync_f(dispatch_get_main_queue(), ptr, ime_callback); }
        std::thread::sleep(Duration::from_millis(100));
    }
});
```

---

## 6. AXIsProcessTrustedWithOptions をバックグラウンドスレッドから直接呼ぶ

```rust
// ❌ 違反 — Hook Thread から直接呼ぶ
fn check_accessibility() -> bool {
    unsafe { AXIsProcessTrustedWithOptions(options) as bool }
    // ↑ バックグラウンドスレッドから呼ぶと、許可ダイアログが表示されないことがある
}
```

**症状**: Accessibility 許可が得られているはずなのにダイアログが出ない。TCC が不安定になる。

**正しい実装**: GCD の `dispatch_async_f` でメインスレッドに dispatch してから呼ぶ。

```rust
// ✅ 正しい実装 — GCD でメインスレッドへ
unsafe {
    dispatch_async_f(dispatch_get_main_queue(), ptr, |ctx| {
        let trusted = AXIsProcessTrustedWithOptions(options);
        // 結果を Atomic に格納
        AX_TRUSTED.store(trusted as bool, Ordering::Release);
    });
}
```

---

## 7. CGEventTap が無効化されたことを検知せずに放置する

```rust
// ❌ 違反 — 無効化イベントを無視する
extern "C" fn event_tap_callback(
    _proxy: CGEventTapProxy,
    event_type: CGEventType,
    event: CGEventRef,
    _: *mut c_void,
) -> CGEventRef {
    if event_type != kCGEventKeyDown && event_type != kCGEventKeyUp {
        return event;  // kCGEventTapDisabledByTimeout を無視
    }
    // ...
}
```

**症状**: 最初は動くが、重い処理後にキーボード入力が取得できなくなる。再起動まで機能しない。

**正しい実装**: `kCGEventTapDisabledByTimeout` / `kCGEventTapDisabledByUserInput` を検知してカウンタをインクリメントし、Hook Thread のポーリングループで再作成する。

---

## 8. Input Monitoring の失敗時に Accessibility フォールバックを省略する

```rust
// ❌ 違反 — 権限なし = 即 panic
fn start_hook() -> anyhow::Result<()> {
    let tap = create_event_tap().expect("Input Monitoring required");
    // ↑ macOS 管理者環境や ad-hoc signed では Input Monitoring が取得できない場合がある
    Ok(())
}
```

**症状**: ad-hoc signed ビルドや管理環境では起動直後にクラッシュ。

**正しい実装**: IM → Accessibility → ListenOnly の 3 段フォールバック。

```rust
// ✅ 正しい実装
let tap = create_head_insert_tap()
    .or_else(|_| {
        USING_ACCESSIBILITY_FALLBACK.store(true, Ordering::Release);
        create_tail_append_tap()
    })
    .or_else(|_| create_listen_only_tap())?;
```
