# data-privacy: 匿名化変換パターン（将来の ML 収集実装時に参照）

## VK コード → キー種別カテゴリへの変換

ML 学習に必要なのは「どんな種類のキーを押したか」であり、「どのキーを押したか」ではない。

```rust
/// VK コードをプライバシーセーフなカテゴリに変換
pub enum KeyCategory {
    Alphabetic,     // VK_A..VK_Z → 文字キー（どの文字かは不明）
    Numeric,        // VK_0..VK_9, numpad
    Backspace,      // VK_BACK
    Delete,         // VK_DELETE
    Space,          // VK_SPACE
    Enter,          // VK_RETURN
    Navigation,     // 矢印キー、Home/End/PgUp/PgDown
    Modifier,       // Shift, Ctrl, Alt, Win
    Punctuation,    // 記号類
    Function,       // F1..F12
    Escape,         // VK_ESCAPE
    Other,          // 上記以外
}

impl KeyCategory {
    pub fn from_vk(vk: u32) -> Self {
        match vk {
            0x41..=0x5A => Self::Alphabetic,
            0x30..=0x39 | 0x60..=0x69 => Self::Numeric,
            0x08 => Self::Backspace,
            0x2E => Self::Delete,
            0x20 => Self::Space,
            0x0D => Self::Enter,
            0x25..=0x28 | 0x24 | 0x23 | 0x21 | 0x22 => Self::Navigation,
            0x10 | 0x11 | 0x12 | 0x5B | 0x5C => Self::Modifier,
            0x1B => Self::Escape,
            0x70..=0x7B => Self::Function,
            _ => Self::Other,
        }
    }
}
```

## 匿名化ログレコードの例

元の InputEvent:
```json
{"type": "key", "vk_code": 65, "timestamp_ms": 1234567890, "is_press": true}
```

匿名化後:
```json
{"type": "key", "category": "Alphabetic", "timestamp_ms": 1234567890, "is_press": true}
```

## 送信前チェックリスト

- [ ] VK コードが全てカテゴリに変換されているか
- [ ] ウィンドウタイトル・プロセス名が含まれていないか
- [ ] タイムスタンプが相対値（セッション開始からの差分ms）に変換されているか
- [ ] ユーザー識別子が匿名 ID になっているか（メールアドレス等は不可）
