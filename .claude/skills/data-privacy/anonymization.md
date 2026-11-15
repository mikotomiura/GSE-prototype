# data-privacy: 匿名化変換パターン（将来の ML 収集実装時に参照）

## VK コード → キー種別カテゴリへの変換

ML 学習に必要なのは「どんな種類のキーを押したか」であり、「どのキーを押したか」ではない。

> ⚠️★★★ **SSOT は本ファイルではなく `src-tauri/src/analysis/anonymize.rs` の実装である。**
> 本節は意図の説明であり、レンジが食い違ったら**実装が正**。
>
> ★ **2026-08-23 修正**: 旧版は enum に `Punctuation` を宣言しながら **`from_vk` が 1 つも
> 割り当てていなかった**（＝ 記号がすべて `Other` へ落ちていた）。⚠️ その結果、匿名化後に
> `is_text_producing` を復元できず `manual_insert` 系が過小評価されていた
> （`manual_contribution_ratio` は 2026-11-15 より前の `research-positioning.md §5` **H-Y の主要アウトカム**だった・`docs/history/research-positioning-2026-11-15.md`）。
> → ★ **ADR-014 判断 6 で `Punctuation` を実装し、`Tab` も足した。**

```rust
/// VK コードをプライバシーセーフなカテゴリに変換
pub enum KeyCategory {
    Alphabetic,           // VK_A..VK_Z → 文字キー（どの文字かは不明）
    Numeric,              // VK_0..VK_9, numpad 0-9
    Punctuation,          // 語内の記号 + テンキー演算子（★ 17 VK を畳む）
    SentencePunctuation,  // 0xBE '.' / 0xBC ','（★ boundary keys の「文間」）
    Tab,                  // VK_TAB
    Backspace,            // VK_BACK
    Delete,               // VK_DELETE
    Space,                // VK_SPACE
    Enter,                // VK_RETURN
    Navigation,           // 矢印キー、Home/End/PgUp/PgDown
    Modifier,             // Shift, Ctrl, Alt, Win
    Function,             // F1..F12
    Escape,               // VK_ESCAPE
    Other,                // 上記以外（★ text-producing なキーは 1 つも含まない）
}

impl KeyCategory {
    pub fn from_vk(vk: u32) -> Self {
        match vk {
            0x41..=0x5A => Self::Alphabetic,
            0x30..=0x39 | 0x60..=0x69 => Self::Numeric,
            // ⚠️ Punctuation より **先に** 判定する（レンジが重なる）。
            0xBC | 0xBE => Self::SentencePunctuation,
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

### ⚠️★★★ 適用点 — **2026-08-23 に `logger` の書き出し境界へ前倒しした**

★ 旧: 量子化は **transfer 境界（`gse-package`）** でのみ効き、**ローカル NDJSON には生 VK が残っていた**。
⚠️ `consent.md` の記録項目表は「キーの**種類**」と約束しており、文言とずれていた（ADR-014 判断 6）。
→ ★ **`logger.rs` の `writeln!` で `KeyCategory::from_vk()` を通す。**

★ **旧ログ（`vk` を持つ）はそのまま読める** —— `replay.rs` の `resolve_key_vk` が
`vk` を優先し、無ければ `category` を代表 VK へ逆写像する。

### ⚠️★★★ `SentencePunctuation` を分けている理由（★ 消さないこと）

★ `personalization-and-online-learning.md §5.2` は **boundary keys を「採用（弁別の前提条件）」** に
格上げしており（[P121] N=475・2 独立文脈）、その接地は散文の階層
**語内 < 語間 < 文間 < 段落間** である。
⚠️ `Punctuation` へ一括で畳むと **「文間」の段だけが失われる**（`[` `=` `-` と同じラベルになる）。
⚠️★★★ **収集後は取り返せない。**

⚠️ **完全な文末判定ではない**: 修飾キー状態を記録していないので `.` と `>` は区別できない。
★ 0xBE は文末の**代理**である（日本語ローマ字入力では `。` が 0xBE から出るので代理としては強い）。

### ⚠️★★★ 不変条件（★ テストで固定してある）

| # | 不変条件 | どこで固定しているか |
|---|---|---|
| 1 | **`is_text_producing` が true な VK は 1 つ残らず非 `Other`** | `anonymize.rs` `every_text_producing_vk_has_a_non_other_category` |
| 2 | **`Punctuation` は 17 VK / `SentencePunctuation` は 2 VK ちょうど** | `anonymize.rs` `punctuation_folds_many_distinct_keys` |
| 3 | **カテゴリ数は 14** | `anonymize.rs` `category_count_is_stable` |
| 4 | ⚠️★★★ **`logger` の `key` 行に生 VK が 1 つも出ない** | `logger.rs` `key_line_records_category_and_never_raw_vk` |
| 5 | **匿名化後の replay が生ログと同じ特徴量を再現する** | `replay.rs` `replay_anonymized_matches_raw_features` |
| 6 | **匿名化後の text-producing 件数が raw と完全一致** | `replay.rs` `anonymized_metrics_text_producing_matches_raw_exactly` |

## 匿名化ログレコードの例

元の InputEvent:
```json
{"type": "key", "vk_code": 65, "timestamp_ms": 1234567890, "is_press": true}  // in-memory
```

匿名化後:
```json
{"type":"key","t":1234567890,"category":"alphabetic","press":true}  // ★ logger が書く実形
```

## 送信前チェックリスト

- [ ] VK コードが全てカテゴリに変換されているか
- [ ] ウィンドウタイトル・プロセス名が含まれていないか
- [ ] タイムスタンプが相対値（セッション開始からの差分ms）に変換されているか
- [ ] ユーザー識別子が匿名 ID になっているか（メールアドレス等は不可）
