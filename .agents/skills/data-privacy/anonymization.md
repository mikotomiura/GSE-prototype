# data-privacy: 匿名化変換パターン（将来の ML 収集実装時に参照）

## VK コード → キー種別カテゴリへの変換

ML 学習に必要なのは「どんな種類のキーを押したか」であり、「どのキーを押したか」ではない。

> ⚠️★★★ **SSOT は本ファイルではなく `src-tauri/src/analysis/anonymize.rs` の実装である。**
> 本節は意図の説明であり、レンジが食い違ったら**実装が正**。
>
> ★ **2026-08-23 修正**: 旧版は enum に `Punctuation` を宣言しながら **`from_vk` が 1 つも
> 割り当てていなかった**（＝ 記号がすべて `Other` へ落ちていた）。⚠️ その結果、匿名化後に
> `is_text_producing` を復元できず `manual_insert` 系が過小評価されていた
> （`manual_contribution_ratio` は `research-positioning.md §5` **H-Y の主要アウトカム**）。
> → ★ **ADR-014 判断 6 で `Punctuation` を実装し、`Tab` も足した。**

```rust
/// VK コードをプライバシーセーフなカテゴリに変換
pub enum KeyCategory {
    Alphabetic,     // VK_A..VK_Z → 文字キー（どの文字かは不明）
    Numeric,        // VK_0..VK_9, numpad 0-9
    Punctuation,    // 記号類 + テンキー演算子（★ どの記号かは残さない・19 VK を畳む）
    Tab,            // VK_TAB
    Backspace,      // VK_BACK
    Delete,         // VK_DELETE
    Space,          // VK_SPACE
    Enter,          // VK_RETURN
    Navigation,     // 矢印キー、Home/End/PgUp/PgDown
    Modifier,       // Shift, Ctrl, Alt, Win
    Function,       // F1..F12
    Escape,         // VK_ESCAPE
    Other,          // 上記以外（★ text-producing なキーは 1 つも含まない）
}

impl KeyCategory {
    pub fn from_vk(vk: u32) -> Self {
        match vk {
            0x41..=0x5A => Self::Alphabetic,
            0x30..=0x39 | 0x60..=0x69 => Self::Numeric,
            // OEM 句読点/記号 + テンキー演算子。いずれも is_text_producing == true。
            0x6A..=0x6F | 0xBA..=0xC0 | 0xDB..=0xDF | 0xE2 => Self::Punctuation,
            0x09 => Self::Tab,
            0x08 => Self::Backspace,
            0x2E => Self::Delete,
            0x20 => Self::Space,
            0x0D => Self::Enter,
            0x21..=0x28 => Self::Navigation,
            0x10 | 0x11 | 0x12 | 0x5B | 0x5C => Self::Modifier,
            0x1B => Self::Escape,
            0x70..=0x7B => Self::Function,
            _ => Self::Other,
        }
    }
}
```

### ⚠️★★★ 不変条件（★ テストで固定してある）

| # | 不変条件 | どこで固定しているか |
|---|---|---|
| 1 | **`is_text_producing` が true な VK は 1 つ残らず非 `Other`** | `anonymize.rs` `every_text_producing_vk_has_a_non_other_category` |
| 2 | **`Punctuation` は 19 個の VK を畳む**（★ 分割すると識別性が上がる） | `anonymize.rs` `punctuation_folds_many_distinct_keys` |
| 3 | **匿名化後の replay が生ログと同じ特徴量を再現する** | `replay.rs` `replay_anonymized_matches_raw_features` |
| 4 | **匿名化後の text-producing 件数が raw と完全一致** | `replay.rs` `anonymized_metrics_text_producing_matches_raw_exactly` |

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
