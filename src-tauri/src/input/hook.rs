use std::sync::atomic::{AtomicBool, AtomicU32, AtomicU64, Ordering};
use std::sync::OnceLock;

use crossbeam_channel::Sender;

use crate::analysis::features::InputEvent;

// ---------------------------------------------------------------------------
// Japanese IME mode VK codes — shared between platforms.
// Windows: captured by WH_KEYBOARD_LL before IME engine.
// macOS: detected via JIS HID keycodes in CGEventTap callback.
// ---------------------------------------------------------------------------
pub const VK_DBE_ALPHANUMERIC: u32 = 0xF0; // 英数: Switch to alphanumeric (A mode)
pub const VK_DBE_KATAKANA: u32 = 0xF1; // カタカナ: Switch to katakana
pub const VK_DBE_HIRAGANA: u32 = 0xF2; // ひらがな: Switch to hiragana (あ mode)
pub const VK_DBE_SBCSCHAR: u32 = 0xF3; // 半角: Single-byte character mode
pub const VK_DBE_DBCSCHAR: u32 = 0xF4; // 全角: Double-byte character mode
pub const VK_KANJI: u32 = 0x19; // 半角/全角: Half-width / full-width toggle

// ---------------------------------------------------------------------------
// Shared atomic state — accessed by both platform implementations and
// the analysis/IME polling threads.
// ---------------------------------------------------------------------------

/// Cross-process IME composition state.
/// Windows: updated by WinEvent hook (EVENT_OBJECT_IME_SHOW/HIDE).
/// macOS: updated by CGEventTap keystroke state machine.
pub static IME_ACTIVE: AtomicBool = AtomicBool::new(false);

/// Returns true if an IME is currently composing text in the foreground application.
pub fn is_ime_active() -> bool {
    IME_ACTIVE.load(Ordering::Relaxed)
}

/// Japanese IME input mode: true = あ/カ (Japanese), false = A (alphanumeric/coding).
/// The analysis thread reads this for HMM β-selection (writing vs coding baselines).
pub static IME_OPEN: AtomicBool = AtomicBool::new(false);

/// Returns true if the Japanese IME is currently in Japanese-input mode.
pub fn is_ime_open() -> bool {
    IME_OPEN.load(Ordering::Relaxed)
}

/// Dirty flag: set by hook callback when a VK_DBE_* / VK_KANJI key is pressed.
/// The IME open polling thread reads this to emit LogEntry::ImeState with a fresh timestamp.
pub static IME_STATE_DIRTY: AtomicBool = AtomicBool::new(false);

/// Unix epoch millisecond timestamp of the most recent keypress.
/// Windows: updated by WH_KEYBOARD_LL callback.
/// macOS: updated by CGEventTap callback.
pub static LAST_KEY_MS: AtomicU64 = AtomicU64::new(0);

/// Returns the Unix epoch millisecond timestamp of the last keypress.
pub fn last_key_ms() -> u64 {
    LAST_KEY_MS.load(Ordering::Relaxed)
}

// ---------------------------------------------------------------------------
// Windows-specific atomics — IME Shadow Features (Phase 2b)
// ---------------------------------------------------------------------------

/// IME 変換ウィンドウ表示時刻 (epoch ms)。WinEvent IME_SHOW で store。
#[cfg(target_os = "windows")]
pub static IME_COMPOSITION_START_MS: AtomicU64 = AtomicU64::new(0);

/// 計算済み IME 変換滞在時間 (ms)。WinEvent IME_HIDE で store。
#[cfg(target_os = "windows")]
pub static IME_SHADOW_DWELL_MS: AtomicU64 = AtomicU64::new(0);

/// IME 変換中の候補ナビゲーション回数 (矢印キー)。hook_callback で fetch_add。
#[cfg(target_os = "windows")]
pub static IME_CANDIDATE_NAV_COUNT: AtomicU32 = AtomicU32::new(0);

/// IME 変換中に ESC で放棄したかどうか。hook_callback で store(true)。
#[cfg(target_os = "windows")]
pub static IME_SHADOW_ABANDON: AtomicBool = AtomicBool::new(false);

/// IME Shadow データの emit 準備完了フラグ。WinEvent IME_HIDE で store(true, Release)。
/// IME Monitor スレッドが swap(false, AcqRel) で読み取り、LogEntry::ImeShadow を送出。
///
/// **Ordering 設計**: READY の Release store は、先行する DWELL_MS / NAV_COUNT /
/// ABANDON への Relaxed store をすべて可視にするフェンスとして機能する。
/// Monitor 側の AcqRel swap の Acquire 部分がこの Release と対になり、
/// READY=true が見えた時点で他の shadow atomics も最新値が保証される。
/// 100ms ポーリング間隔のため、高速な連続 IME セッションではデータロスの
/// 可能性があるが、Phase 2b は shadow-only データ収集段階のため許容する。
#[cfg(target_os = "windows")]
pub static IME_SHADOW_READY: AtomicBool = AtomicBool::new(false);

// ---------------------------------------------------------------------------
// macOS-specific atomics
// ---------------------------------------------------------------------------

/// IME inline composition state (macOS only): true when the user is actively typing
/// romaji that the IME is converting to kana (marked/underlined text).
#[cfg(target_os = "macos")]
pub static IME_COMPOSING: AtomicBool = AtomicBool::new(false);

/// Set to true once any JIS IME key has been observed (macOS only).
/// Disables TIS polling to avoid per-app input source interference.
#[cfg(target_os = "macos")]
pub static JIS_KEYBOARD_SEEN: AtomicBool = AtomicBool::new(false);

/// true when the keyboard hook is successfully installed.
/// Read by `get_hook_status` Tauri command to report hook state.
/// Windows: SetWindowsHookExW 成功時に true、フック無効化時に false。
/// macOS: CGEventTap インストール成功時に true。
///
/// ⚠️★★ **これは「設置できた」しか意味しない。**「イベントが届いている」ではない。
/// 2026-08-09 の Windows 実機で、OS が低レベルフックを黙って外したあとも本フラグは
/// `true` のままで、5 分間 0 打のブロックが「正常」として提出された
/// (`windows-verification.md` §5-7)。★ 届いているかどうかは `HOOK_STARVED` を見ること。
pub static HOOK_ACTIVE: AtomicBool = AtomicBool::new(false);

/// ⚠️★★ true = 「設置済みなのにイベントが届いていない」と監視スレッドが判断した状態。
///
/// `input::liveness` の純関数が `HookHealth::Down` を返したときに立つ。
/// ★ `HOOK_ACTIVE` とは**別概念**なので同じフラグに混ぜない
/// (混ぜるとフックスレッドと監視スレッドが同じ Atomic を奪い合う)。
/// トレイはこの 2 つの AND を「計測中」として表示する。
pub static HOOK_STARVED: AtomicBool = AtomicBool::new(false);

/// キーボードフックのコールバックが呼ばれた回数（診断 + 生存監視）。
///
/// 0 のままなら「フックは作成されたがイベントが届いていない」ことを示す。
/// ★ 2026-08-09 以降は Windows でも加算する (`input::liveness` の生存判定が読む)。
/// ⚠️ ★ `LAST_KEY_MS` を生存判定に使わない理由: あちらは**再設置時に 0 へリセットされる**ので
/// 「沈黙の長さ」の基準にできない (memory `macos-tap-idle-away-probe-bug` と同型の罠)。
pub static CALLBACK_COUNT: AtomicU64 = AtomicU64::new(0);

/// ⚠️★★ 分析スレッドへ渡せずに**捨てた**打鍵イベントの累計。
///
/// ★ `CALLBACK_COUNT` は「OS がフックを呼んだ回数」であって
/// **「記録できた回数」ではない**。channel が詰まれば呼ばれても記録は失われる
/// (security-checker MEDIUM: それを数えないと、本機能が目的とする
/// 「打っているのに記録されていない」の一部を素通りさせる)。
///
/// ⚠️ ★ コールバック内でログを書けないので (`hook-constraints` 共通-1: ログ禁止)、
/// **カウンタだけ上げて、監視スレッドが統計的に 1 回だけ報告する** (共通-3 のパターン)。
pub static EVENTS_DROPPED: AtomicU64 = AtomicU64::new(0);

/// macOS: CGEventTap 作成の連続失敗回数（診断用）。
/// TCC 権限が付与されていない、またはコード署名の問題を示す。
#[cfg(target_os = "macos")]
pub static CONSECUTIVE_TAP_FAILURES: AtomicU32 = AtomicU32::new(0);

/// macOS: Input Monitoring 失敗時に Accessibility 権限へフォールバックしたかどうか。
/// ad-hoc 署名では Input Monitoring の TCC CDHash 認証が不安定なため、
/// 10回連続失敗後に CGEventTapOptions::Default（Accessibility 権限）へ切り替える。
#[cfg(target_os = "macos")]
pub static USING_ACCESSIBILITY_FALLBACK: AtomicBool = AtomicBool::new(false);

// ---------------------------------------------------------------------------
// Lock-free channels — shared between platforms
// ---------------------------------------------------------------------------

/// Lock-free sender for keystroke events → analysis thread.
pub static EVENT_SENDER: OnceLock<Sender<InputEvent>> = OnceLock::new();

/// Lock-free wake signal sender for the IME open polling thread.
pub static POLL_WAKE_TX: OnceLock<Sender<()>> = OnceLock::new();

/// Store the polling thread's wake channel sender.
/// Must be called before `init_hook` so the sender is ready when the hook fires.
pub fn set_poll_wake_sender(tx: Sender<()>) {
    let _ = POLL_WAKE_TX.set(tx);
}

// ---------------------------------------------------------------------------
// Platform-specific hook implementations
// ---------------------------------------------------------------------------

#[cfg(target_os = "windows")]
#[path = "hook_windows.rs"]
mod hook_windows;

#[cfg(target_os = "macos")]
#[path = "hook_macos.rs"]
mod hook_macos;

/// Install the platform-specific keyboard hook and begin delivering InputEvents to `sender`.
/// Spawns a dedicated background thread; returns immediately.
pub fn init_hook(sender: Sender<InputEvent>) {
    let _ = EVENT_SENDER.set(sender);

    #[cfg(target_os = "windows")]
    hook_windows::start();

    #[cfg(target_os = "macos")]
    hook_macos::start();
}

/// フックの再設置を要求する (silent death からの復帰・`decisions.md` D-3)。
///
/// ⚠️★★ **新しい復帰経路は書かない。** 既存の「メッセージループを抜けて
/// ループ先頭で再設置する」経路 (`hook_windows.rs` の `Keyboard hook message loop exited`)
/// を**起こすだけ**である。★ 経路を増やすと、どれか 1 つが静かに壊れる。
///
/// 戻り値: 要求を送れたら `true`。macOS はタップ失効の再作成を自前で持つので `false`。
pub fn request_reinstall() -> bool {
    #[cfg(target_os = "windows")]
    {
        hook_windows::request_reinstall()
    }
    #[cfg(not(target_os = "windows"))]
    {
        false
    }
}
