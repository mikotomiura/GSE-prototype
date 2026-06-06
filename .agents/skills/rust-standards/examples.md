# rust-standards: 具体的な実装例

## 1. unsafe 隔離パターン

Win32 API を呼ぶ場合は、必ずラッパー構造体またはラッパー関数に閉じ込める。

```rust
/// キーボードフックのラッパー。Drop で自動解除。
pub struct KeyboardHook {
    handle: HHOOK,
}

impl KeyboardHook {
    pub fn install(proc: HOOKPROC) -> anyhow::Result<Self> {
        // SAFETY: proc は 'static な extern "system" fn。
        // module handle は NULL で現プロセスのフックを登録。
        let handle = unsafe {
            SetWindowsHookExW(WH_KEYBOARD_LL, proc, None, 0)
        }.context("SetWindowsHookExW failed")?;
        Ok(Self { handle })
    }
}

impl Drop for KeyboardHook {
    fn drop(&mut self) {
        // SAFETY: handle は install() で取得した有効な HHOOK
        unsafe { UnhookWindowsHookEx(self.handle) };
    }
}
```

---

## 2. anyhow エラーチェイン

エラーが発生した箇所の文脈を `.context()` で付加することで、
ログに表示されるエラーメッセージが追跡可能になる。

```rust
use anyhow::{Context, Result};

fn start_wall_server(port: u16) -> Result<WallServerInfo> {
    let server = tiny_http::Server::http(format!("0.0.0.0:{}", port))
        .map_err(|e| anyhow::anyhow!("tiny_http error: {}", e))
        .context("failed to bind wall server")?;

    let token = generate_token().context("token generation failed")?;

    tracing::info!("wall server started: port={} token={}", port, token);
    Ok(WallServerInfo { port, token })
}
```

---

## 3. tracing の使い分け

| マクロ | 使う場面 | 例 |
|---|---|---|
| `tracing::error!` | 復旧不可能なエラー、機能停止 | フック登録失敗 |
| `tracing::warn!` | 劣化動作・ドロップ発生 | チャネル満杯でイベントドロップ |
| `tracing::info!` | セッション開始/終了などの重要イベント | セッション開始 |
| `tracing::debug!` | 詳細な内部状態（通常は無効） | 特徴量の値 |

```rust
// チャネル満杯の警告例
if let Err(_) = tx.try_send(event) {
    tracing::warn!("input channel full, dropping event: vk={:?}", event.vk_code);
}
```

---

## 4. Atomic の Ordering 選択

GSE でのパターン:

```rust
// LAST_KEY_MS: 近似値で十分 → Relaxed
LAST_KEY_MS.store(now_ms, Ordering::Relaxed);
let t = LAST_KEY_MS.load(Ordering::Relaxed);

// IME_OPEN / IME_ACTIVE: スレッド間の可視性保証が必要 → Acquire/Release
IME_OPEN.store(true, Ordering::Release);
let open = IME_OPEN.load(Ordering::Acquire);
```
