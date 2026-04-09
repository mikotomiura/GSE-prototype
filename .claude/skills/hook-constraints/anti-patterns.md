# hook-constraints: 違反パターンと症状

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
