//! 日本語 IME の**モードキー**(`VK_DBE_*` / `VK_KANJI`) の意味を決める純粋な判定。
//!
//! ⚠️★★★ **OS 非依存にしてある。`#[cfg]` を付けないこと。**
//!   ★ そうすると **両 OS の CI でこの表が検証される** (`ime_cloak` / `ime_compose` と同じ方針)。
//!   ⚠️ `hook_windows.rs` / `hook_macos.rs` のテストモジュールは**相手側の OS では 1 行も走らない**ので、
//!   判断をあちらに置くと片方の CI しか見ない (＝ 下記の欠陥がまさにそれで生まれた)。
//!
//! # ⚠️★★★ なぜこのモジュールが要ったか (2026-09-12)
//!
//! ★ もともと同じ遷移表が **2 か所に複製**されていた ——
//! `hook_windows.rs` には純関数として、`hook_macos.rs` にはコールバック内のインライン `match` として。
//! ⚠️ **macOS 側の複製は無テストで、しかも意味がずれていた。**
//!
//! ★ ずれの中身: macOS は `kVK_JIS_Kana` (`0x68` = **かな** キー) を [`VK_KANJI`] へ写像していた。
//! ⚠️ [`VK_KANJI`] は **Windows の「半角/全角」キー**であり**本物のトグル**なので、
//! 表は `Toggle` を返す。→ ⚠️★★★ **macOS で かな を偶数回押すと `IME_OPEN` が実体と反転したまま残り、
//! その間の日本語変換が `ime_shadow` から丸ごと欠測していた** (実測: 変換を確定したのに 0 行)。
//!
//! ★ **macOS の かな キーはトグルではない** —— 押すと**無条件に日本語へ切り替わる**。
//! → ★ 写像を [`VK_DBE_HIRAGANA`] (「ひらがなモードへ切り替え」＝ `Set(true)`) に直した。
//!   ⚠️ 同じ表の隣の行が `0x90 => VK_DBE_HIRAGANA // alternate かな` と**既に正しく書いていた**ので、
//!   本来の意味はもともと表の中にあった。
//!
//! ⚠️★★★ **[`VK_KANJI`] は Windows 専用である。** macOS には「半角/全角」キーが存在しない
//! (JIS でも 英数 / かな の**別々のキー**になっている)。
//! → ★ `hook_macos.rs` の回帰テスト `macos_never_maps_any_key_to_the_windows_toggle` が機械で守る。

// ⚠️ 定数は `input::hook` にある (`input` 直下ではない)。
//   ★ `hook_macos.rs` / `hook_windows.rs` は `#[path]` で `hook` の子として取り込まれるので
//     あちらの `super::` は `hook` を指すが、**このモジュールは `input` の直下**である。
use super::hook::{
    VK_DBE_ALPHANUMERIC, VK_DBE_DBCSCHAR, VK_DBE_HIRAGANA, VK_DBE_KATAKANA, VK_DBE_SBCSCHAR,
    VK_KANJI,
};

/// IME モードキーの **押下** 時、`IME_OPEN` をどう遷移させるべきか。
#[derive(Debug, PartialEq, Eq)]
pub enum ImeOpenTransition {
    /// 明示的な値に設定する。
    Set(bool),
    /// 現在値をトグルする ([`VK_KANJI`] ＝ Windows の「半角/全角」)。
    ///
    /// ⚠️★★★ **macOS ではこれを返してはならない** (上記モジュール doc)。
    ///
    /// ⚠️★ `load` してから呼び出し側で `store(!current)` する形にしない。
    /// `IME_OPEN` は IME ポーリングスレッド (`ime_windows.rs`) からも書かれるため、
    /// load → store の間に他スレッドの書き込みが挟まると失われる (非アトミック RMW)。
    /// 呼び出し側は `IME_OPEN.fetch_xor(true, Ordering::AcqRel)` を使うこと。
    Toggle,
    /// このキーは IME モードに関係しない。
    None,
}

/// 押下時の遷移表。
pub fn ime_open_after_press(vk_code: u32) -> ImeOpenTransition {
    match vk_code {
        VK_DBE_ALPHANUMERIC | VK_DBE_SBCSCHAR => ImeOpenTransition::Set(false),
        VK_DBE_KATAKANA | VK_DBE_HIRAGANA | VK_DBE_DBCSCHAR => ImeOpenTransition::Set(true),
        VK_KANJI => ImeOpenTransition::Toggle,
        _ => ImeOpenTransition::None,
    }
}

/// IME モードキーの **離す** 時、`IME_OPEN` をどう遷移させるべきか。
///
/// ⚠️ Surface Type Cover は `VK_DBE_HIRAGANA` を key-UP でしか発火しないため、
/// press 側と異なり [`VK_KANJI`] を含まない別の遷移表になっている。
pub fn ime_open_after_release(vk_code: u32) -> Option<bool> {
    match vk_code {
        VK_DBE_KATAKANA | VK_DBE_HIRAGANA | VK_DBE_DBCSCHAR => Some(true),
        VK_DBE_ALPHANUMERIC | VK_DBE_SBCSCHAR => Some(false),
        _ => None,
    }
}

/// このキーが IME モードキー (`VK_DBE_*` / [`VK_KANJI`]) かどうか。
/// key-up でも IME ポーリングスレッドを起こす必要があるかの判定に使う
/// (Surface Type Cover の `VK_DBE_HIRAGANA` は key-up でしか発火しないため)。
pub fn is_ime_mode_key(vk_code: u32) -> bool {
    matches!(
        vk_code,
        VK_DBE_ALPHANUMERIC
            | VK_DBE_KATAKANA
            | VK_DBE_HIRAGANA
            | VK_DBE_SBCSCHAR
            | VK_DBE_DBCSCHAR
            | VK_KANJI
    )
}

// ---------------------------------------------------------------------------
// Tests — ⚠️★ `#[cfg(target_os)]` を付けない。**両 OS の CI で走らせる。**
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn press_of_alphanumeric_keys_closes_ime() {
        assert_eq!(
            ime_open_after_press(VK_DBE_ALPHANUMERIC),
            ImeOpenTransition::Set(false)
        );
        assert_eq!(
            ime_open_after_press(VK_DBE_SBCSCHAR),
            ImeOpenTransition::Set(false)
        );
    }

    #[test]
    fn press_of_japanese_keys_opens_ime() {
        assert_eq!(
            ime_open_after_press(VK_DBE_HIRAGANA),
            ImeOpenTransition::Set(true)
        );
        assert_eq!(
            ime_open_after_press(VK_DBE_KATAKANA),
            ImeOpenTransition::Set(true)
        );
        assert_eq!(
            ime_open_after_press(VK_DBE_DBCSCHAR),
            ImeOpenTransition::Set(true)
        );
    }

    #[test]
    fn press_of_kanji_key_returns_toggle() {
        assert_eq!(ime_open_after_press(VK_KANJI), ImeOpenTransition::Toggle);
    }

    #[test]
    fn press_of_typing_key_does_not_change_ime_state() {
        assert_eq!(ime_open_after_press(0x41), ImeOpenTransition::None);
    }

    #[test]
    fn release_of_japanese_keys_opens_ime() {
        assert_eq!(ime_open_after_release(VK_DBE_HIRAGANA), Some(true));
        assert_eq!(ime_open_after_release(VK_DBE_KATAKANA), Some(true));
        assert_eq!(ime_open_after_release(VK_DBE_DBCSCHAR), Some(true));
    }

    #[test]
    fn release_of_alphanumeric_keys_closes_ime() {
        assert_eq!(ime_open_after_release(VK_DBE_ALPHANUMERIC), Some(false));
        assert_eq!(ime_open_after_release(VK_DBE_SBCSCHAR), Some(false));
    }

    #[test]
    fn release_of_kanji_key_does_not_change_ime_state() {
        assert_eq!(ime_open_after_release(VK_KANJI), None);
    }

    #[test]
    fn ime_mode_key_matches_all_dbe_and_kanji_keys() {
        for vk in [
            VK_DBE_ALPHANUMERIC,
            VK_DBE_KATAKANA,
            VK_DBE_HIRAGANA,
            VK_DBE_SBCSCHAR,
            VK_DBE_DBCSCHAR,
            VK_KANJI,
        ] {
            assert!(is_ime_mode_key(vk));
        }
    }

    #[test]
    fn ime_mode_key_excludes_typing_keys() {
        assert!(!is_ime_mode_key(0x41), "A キーは IME モードキーではない");
    }

    /// ⚠️★★★ **かな キーは「日本語へ切り替える」であり、トグルではない。**
    ///
    /// ★ 2026-09-12 の macOS 実機検証で見つかった欠陥の回帰テスト。
    /// ⚠️ `Set(true)` は**何回押しても日本語のまま**という性質を持つので、
    /// ★ 「偶数回押すと反転する」という壊れ方が**構造的に起こりえない**ことを固定する。
    #[test]
    fn the_kana_key_is_idempotent_not_a_toggle() {
        let t = ime_open_after_press(VK_DBE_HIRAGANA);
        assert_eq!(t, ImeOpenTransition::Set(true));
        assert_ne!(
            t,
            ImeOpenTransition::Toggle,
            "⚠️ かな を Toggle にすると偶数回押下で IME_OPEN が実体と反転する \
             (2026-09-12 実測: その間の変換が ime_shadow から丸ごと欠測した)"
        );
    }
}
