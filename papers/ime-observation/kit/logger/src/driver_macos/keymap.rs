//! Key-code handling of the macOS driver: which physical keys are observed, and how a macOS virtual
//! key code is mapped to the Windows virtual-key space that the rest of the logger uses.
//!
//! The text between the excerpt markers is pinned by the manifest and is not edited by hand. The
//! wrappers after it are the only items the parent module uses.

use crate::input::hook::{VK_DBE_ALPHANUMERIC, VK_DBE_HIRAGANA, VK_DBE_KATAKANA};

// @excerpt-begin is_observed_key
/// ★★★ **分析チャネルへ送るキー**かどうか（macOS の生 `CGKeyCode`）。
///
/// ## ⚠️★★★ 2026-08-23: `is_typing_key` から改名し、**広げた**（ADR-016 **D8**）
///
/// ★ Windows 側 `hook_windows.rs::is_observed_key` と**対**である。狙いは同じ ——
/// 「打鍵が薄い作業」を「離席」と取り違えないために、**Esc / 矢印 / F1–F12 も種類だけ記録する**。
/// ⚠️ 特徴量へ流す集合は [`crate::analysis::key_gate::is_feature_key`] のままで**変えない**。
///
/// ## ⚠️★★★ Windows と**同じにできない** 2 つ（★ 対のテストで固定してある）
///
/// | 何 | ⚠️ macOS でどうなるか | ★ なぜ入れないか |
/// |---|---|---|
/// | **修飾キー** | ❌ **そもそも届かない** | ★ tap の mask が `KeyDown`/`KeyUp` だけで、修飾は `FlagsChanged` で来る。⚠️ mask に足すと `LAST_KEY_MS` と IME 状態機械へ波及し、**特徴量経路に触れる** |
/// | **テンキー** | ❌ **入れない** | ⚠️★★★ [`macos_vk_to_vk`] の既定が `other => other as u32` の**素通し**であり、`kVK_ANSI_Keypad0`(0x52) は **`0x52` = `VK_R`（英字！）** に化ける。★ 明示写像を足して `0x60..=0x6F` にすると **`is_feature_key` の中**に入り、⚠️ **macOS の特徴量が変わる**（= `HMM_VERSION` bump）。→ ★ **どちらの道も塞がっている** |
///
/// ⚠️ **この非対称は「決めた状態」であって「気付いていない穴」ではない。**
/// ★ 研究者へ返す事項として `.steering/20260823-o1-instrument-r3a/decisions.md` D-A に記録した。
fn is_observed_key(mac_vk: u64) -> bool {
    matches!(mac_vk,
        // ── ★ 従来から通していた集合 (⚠️ 特徴量に入る) ──────────────────
        0x00..=0x09   // kVK_ANSI_A .. kVK_ANSI_V (letters)
        | 0x0B..=0x33 // kVK_ANSI_B .. kVK_Delete (letters, digits, symbols, Return, Tab, Space, Backspace)
        | 0x75        // kVK_ForwardDelete
        // ── ★ 2026-08-23 に足した観測のみの集合 (⚠️ 特徴量には流れない) ──
        // ⚠️ すべて `macos_vk_to_vk` に**明示写像がある**ものだけを入れる
        //   (★ 素通しに落ちると英字・数字の VK に化けて特徴量を汚す)。
        | 0x35        // kVK_Escape           → 0x1B
        | 0x7B..=0x7E // kVK_LeftArrow..DownArrow → 0x25..0x28
        // F1..F12 (⚠️ mac の keycode は連続していない)
        | 0x7A | 0x78 | 0x63 | 0x76 | 0x60 | 0x61
        | 0x62 | 0x64 | 0x65 | 0x6D | 0x67 | 0x6F
    )
}

// ---------------------------------------------------------------------------
// @excerpt-end is_observed_key

// @excerpt-begin macos_vk_to_vk
// macOS CGKeyCode → Windows VK equivalent mapping
//
// `EventField::KEYBOARD_EVENT_KEYCODE` returns the macOS *virtual key code*
// (CGKeyCode / kVK_* constants from HIToolbox/Events.h), which is DIFFERENT
// from the USB HID keycode.  Notable differences:
//   kVK_ANSI_A = 0x00  (HID 'A' = 0x04)
//   kVK_Delete (Backspace) = 0x33  (HID Backspace = 0x2A)
//   kVK_ForwardDelete = 0x75      (HID Delete = 0x4C)
//
// GSE-critical mappings (affect F3, F6, backspace streak detection):
//   macOS 0x33 (Backspace)    → Windows 0x08 (VK_BACK)
//   macOS 0x75 (ForwardDel)   → Windows 0x2E (VK_DELETE)
// ---------------------------------------------------------------------------
fn macos_vk_to_vk(mac_vk: u64) -> u32 {
    match mac_vk {
        // ── Letters (kVK_ANSI_* → Windows VK_*) ─────────────────────────────
        0x00 => 0x41, // kVK_ANSI_A
        0x0B => 0x42, // kVK_ANSI_B
        0x08 => 0x43, // kVK_ANSI_C
        0x02 => 0x44, // kVK_ANSI_D
        0x0E => 0x45, // kVK_ANSI_E
        0x03 => 0x46, // kVK_ANSI_F
        0x05 => 0x47, // kVK_ANSI_G
        0x04 => 0x48, // kVK_ANSI_H
        0x22 => 0x49, // kVK_ANSI_I
        0x26 => 0x4A, // kVK_ANSI_J
        0x28 => 0x4B, // kVK_ANSI_K
        0x25 => 0x4C, // kVK_ANSI_L
        0x2E => 0x4D, // kVK_ANSI_M
        0x2D => 0x4E, // kVK_ANSI_N
        0x1F => 0x4F, // kVK_ANSI_O
        0x23 => 0x50, // kVK_ANSI_P
        0x0C => 0x51, // kVK_ANSI_Q
        0x0F => 0x52, // kVK_ANSI_R
        0x01 => 0x53, // kVK_ANSI_S
        0x11 => 0x54, // kVK_ANSI_T
        0x20 => 0x55, // kVK_ANSI_U
        0x09 => 0x56, // kVK_ANSI_V
        0x0D => 0x57, // kVK_ANSI_W
        0x07 => 0x58, // kVK_ANSI_X
        0x10 => 0x59, // kVK_ANSI_Y
        0x06 => 0x5A, // kVK_ANSI_Z

        // ── Digits ───────────────────────────────────────────────────────────
        0x12 => 0x31, // kVK_ANSI_1
        0x13 => 0x32, // kVK_ANSI_2
        0x14 => 0x33, // kVK_ANSI_3  (output 0x33 = VK_3, NOT Backspace)
        0x15 => 0x34, // kVK_ANSI_4
        0x17 => 0x35, // kVK_ANSI_5
        0x16 => 0x36, // kVK_ANSI_6
        0x1A => 0x37, // kVK_ANSI_7
        0x1C => 0x38, // kVK_ANSI_8
        0x19 => 0x39, // kVK_ANSI_9
        0x1D => 0x30, // kVK_ANSI_0

        // ── CRITICAL: editing keys for F3/F6/backspace-streak ─────────────
        0x33 => 0x08, // kVK_Delete (Backspace)  → VK_BACK
        0x75 => 0x2E, // kVK_ForwardDelete       → VK_DELETE

        // ── Control/whitespace ────────────────────────────────────────────
        0x24 => 0x0D, // kVK_Return  → VK_RETURN
        0x30 => 0x09, // kVK_Tab     → VK_TAB
        0x31 => 0x20, // kVK_Space   → VK_SPACE
        0x35 => 0x1B, // kVK_Escape  → VK_ESCAPE

        // ── Arrow keys ───────────────────────────────────────────────────
        0x7B => 0x25, // kVK_LeftArrow  → VK_LEFT
        0x7C => 0x27, // kVK_RightArrow → VK_RIGHT
        0x7D => 0x28, // kVK_DownArrow  → VK_DOWN
        0x7E => 0x26, // kVK_UpArrow    → VK_UP

        // ── Function keys ─────────────────────────────────────────────────
        0x7A => 0x70, // kVK_F1
        0x78 => 0x71, // kVK_F2
        0x63 => 0x72, // kVK_F3
        0x76 => 0x73, // kVK_F4
        0x60 => 0x74, // kVK_F5
        0x61 => 0x75, // kVK_F6
        0x62 => 0x76, // kVK_F7
        0x64 => 0x77, // kVK_F8
        0x65 => 0x78, // kVK_F9
        0x6D => 0x79, // kVK_F10
        0x67 => 0x7A, // kVK_F11
        0x6F => 0x7B, // kVK_F12

        // ── Symbols / punctuation ─────────────────────────────────────────
        0x18 => 0xBB, // kVK_ANSI_Equal          → VK_OEM_PLUS
        0x1B => 0xBD, // kVK_ANSI_Minus          → VK_OEM_MINUS
        0x21 => 0xDB, // kVK_ANSI_LeftBracket    → VK_OEM_4
        0x1E => 0xDD, // kVK_ANSI_RightBracket   → VK_OEM_6
        0x27 => 0xDE, // kVK_ANSI_Quote          → VK_OEM_7
        0x29 => 0xBA, // kVK_ANSI_Semicolon      → VK_OEM_1
        0x2A => 0xDC, // kVK_ANSI_Backslash      → VK_OEM_5
        0x2B => 0xBC, // kVK_ANSI_Comma          → VK_OEM_COMMA
        0x2C => 0xBF, // kVK_ANSI_Slash          → VK_OEM_2
        0x2F => 0xBE, // kVK_ANSI_Period         → VK_OEM_PERIOD
        0x32 => 0xC0, // kVK_ANSI_Grave          → VK_OEM_3

        // ── JIS IME toggle keys (CGKeyCode values for JIS keyboards) ──────
        0x66 => VK_DBE_ALPHANUMERIC, // kVK_JIS_Eisu → 英数 (alphanumeric)
        // ⚠️★★★ **かな は「トグル」ではない。無条件に日本語へ切り替えるキーである。**
        //   ★ 2026-09-12 の macOS 実機検証まで、ここは `VK_KANJI` (= Windows の「半角/全角」)
        //     へ写像しており、遷移表が `Toggle` を返していた。
        //   ⚠️ その結果 **かな を偶数回押すと `IME_OPEN` が実体と反転したまま残り**、
        //     その間の日本語変換が `ime_shadow` から**丸ごと欠測**していた
        //     (実測: OS の入力ソースは日本語のまま、GSE だけが true/false を交互に往復した)。
        //   ★ 下の `0x90` が最初から `VK_DBE_HIRAGANA` だったとおり、正しい意味は表の中にあった。
        //   ⚠️ macOS に「半角/全角」キーは**存在しない** (JIS でも 英数 / かな の別キー)。
        //     → ★ `VK_KANJI` は Windows 専用であり、macOS からは**二度と生やさない**
        //       (回帰テスト `macos_never_maps_any_key_to_the_windows_toggle`)。
        0x68 => VK_DBE_HIRAGANA, // kVK_JIS_Kana → かな (日本語モードへ切り替え)
        0x90 => VK_DBE_HIRAGANA, // alternate かな on some JIS layouts
        0x91 => VK_DBE_KATAKANA, // alternate カタカナ on some JIS layouts

        // Pass-through for unmapped keys.
        // Key identity is not critical for timing features (F1-F5).
        other => other as u32,
    }
}

// ---------------------------------------------------------------------------
// @excerpt-end macos_vk_to_vk

/// Whether a macOS virtual key code belongs to the observed set.
pub(super) fn observed(mac_vk: u64) -> bool {
    is_observed_key(mac_vk)
}

/// Maps a macOS virtual key code to the Windows virtual-key space.
pub(super) fn to_vk(mac_vk: u64) -> u32 {
    macos_vk_to_vk(mac_vk)
}
