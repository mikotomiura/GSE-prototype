// macOS IME monitoring: ImeMonitor + IME open polling + TIS (Text Input Source) detection.
//
// ImeMonitor: reads IME_ACTIVE atomic set by the CGEventTap callback's
// keystroke state machine. When true, the HMM engine is paused.
//
// IME open polling: two detection paths:
//   Path A — JIS physical keys (fast, ~5ms): trust IME_OPEN set by hook callback.
//   Path B — ANSI/US keyboards (100ms TIS poll): menu-bar switch fallback.
//
// TIS detection: polls TISCopyCurrentKeyboardInputSource() via dispatch_sync_f
// to main GCD queue (required by HIToolbox). Checks if the input source ID
// contains "inputmethod.Japanese".

use std::ffi::c_void;
use std::sync::atomic::Ordering;
use std::time::{SystemTime, UNIX_EPOCH};

use core_foundation::base::{CFRelease, TCFType};
use core_foundation::string::CFString;
use crossbeam_channel::Sender;

use crate::logger::LogEntry;

// ---------------------------------------------------------------------------
// ImeMonitor — reads keystroke-based composition state from CGEventTap
// ---------------------------------------------------------------------------

pub struct ImeMonitor;

impl ImeMonitor {
    pub fn new() -> Self {
        tracing::info!(
            "IME Monitor: keystroke-based composition detection enabled \
             (CGEventTap state machine)"
        );
        Self
    }

    pub fn is_candidate_window_open(&self) -> bool {
        crate::input::hook::IME_ACTIVE.load(Ordering::Acquire)
    }
}

// ---------------------------------------------------------------------------
// spawn_ime_open_polling_thread — IME open/close state machine
// ---------------------------------------------------------------------------

pub fn spawn_ime_open_polling_thread(
    log_tx: Sender<LogEntry>,
    wake_rx: crossbeam_channel::Receiver<()>,
) {
    std::thread::spawn(move || {
        let mut last_state: Option<bool> = None;

        loop {
            let woke_by_key = wake_rx
                .recv_timeout(std::time::Duration::from_millis(100))
                .is_ok();

            if woke_by_key {
                std::thread::sleep(std::time::Duration::from_millis(5));
            }

            let dirty = crate::input::hook::IME_STATE_DIRTY.swap(false, Ordering::AcqRel);
            let jis_keyboard_seen = crate::input::hook::JIS_KEYBOARD_SEEN.load(Ordering::Acquire);

            let current_state = match select_ime_source(dirty, jis_keyboard_seen) {
                ImeSource::HookFlag => crate::input::hook::IME_OPEN.load(Ordering::Acquire),
                ImeSource::TisQuery => is_japanese_ime_open(),
            };

            if last_state.map_or(true, |prev| prev != current_state) {
                last_state = Some(current_state);
                crate::input::hook::IME_OPEN.store(current_state, Ordering::Relaxed);
                let active = crate::input::hook::IME_ACTIVE.load(Ordering::Acquire);
                emit_ime_state(&log_tx, current_state, active);
            }
        }
    });
}

// ---------------------------------------------------------------------------
// IME state source selection (pure — テストできる形に切り出す)
// ---------------------------------------------------------------------------
//
// Path A (JIS 物理キー): hook_callback が VK_DBE_* / VK_KANJI を検知して IME_OPEN を
// 直接更新した (dirty) か、そもそも JIS キーボードが確認されている場合は、その値を信頼する。
// Path B (ANSI/US キーボード): どちらでもない場合のみ、100ms 毎の TIS ポーリングにフォールバックする。

/// どちらの情報源から IME 開閉状態を読むべきか。
enum ImeSource {
    /// hook_callback が更新した `IME_OPEN` を信頼する (Path A)。
    HookFlag,
    /// `is_japanese_ime_open()` (TIS) にフォールバックする (Path B)。
    TisQuery,
}

/// `dirty` (直近の VK_DBE_* / VK_KANJI 検知) または `jis_keyboard_seen` のいずれかが
/// true なら `IME_OPEN` を信頼できる。どちらも false のときだけ TIS 問い合わせが要る。
fn select_ime_source(dirty: bool, jis_keyboard_seen: bool) -> ImeSource {
    if dirty || jis_keyboard_seen {
        ImeSource::HookFlag
    } else {
        ImeSource::TisQuery
    }
}

fn emit_ime_state(log_tx: &Sender<LogEntry>, on: bool, active: bool) {
    let ts = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64;
    let _ = log_tx.try_send(LogEntry::ImeState {
        timestamp: ts,
        on,
        active,
    });
    tracing::debug!(
        "IME open: {}, active: {} (polling)",
        if on { "ON (あ)" } else { "OFF (A)" },
        active,
    );
}

// ---------------------------------------------------------------------------
// TIS FFI declarations (Carbon framework)
// ---------------------------------------------------------------------------

#[allow(non_camel_case_types)]
type TISInputSourceRef = *const c_void;
#[allow(non_camel_case_types)]
type CFStringRef = *const c_void;

#[link(name = "Carbon", kind = "framework")]
extern "C" {
    fn TISCopyCurrentKeyboardInputSource() -> TISInputSourceRef;
    fn TISGetInputSourceProperty(source: TISInputSourceRef, key: CFStringRef) -> *const c_void;
    #[allow(non_upper_case_globals)]
    static kTISPropertyInputSourceID: CFStringRef;
}

#[link(name = "System", kind = "dylib")]
extern "C" {
    #[allow(non_upper_case_globals)]
    static _dispatch_main_q: c_void;
    fn dispatch_sync_f(
        queue: *const c_void,
        context: *mut c_void,
        work: unsafe extern "C" fn(*mut c_void),
    );
}

struct TisQueryCtx {
    result: bool,
}

unsafe extern "C" fn tis_query_main_thread(ctx: *mut c_void) {
    let ctx = &mut *(ctx as *mut TisQueryCtx);

    let source = TISCopyCurrentKeyboardInputSource();
    if source.is_null() {
        ctx.result = false;
        return;
    }

    let id_ref = TISGetInputSourceProperty(source, kTISPropertyInputSourceID);

    ctx.result = if id_ref.is_null() {
        false
    } else {
        let cf_str = CFString::wrap_under_get_rule(id_ref as core_foundation::string::CFStringRef);
        let id_str = cf_str.to_string();
        id_str.contains("inputmethod.Japanese")
    };

    CFRelease(source);
}

/// Returns true if the current system keyboard input source is a Japanese IME.
/// Safe to call from any thread — internally dispatches to the main GCD queue.
fn is_japanese_ime_open() -> bool {
    let mut ctx = TisQueryCtx { result: false };
    unsafe {
        dispatch_sync_f(
            &_dispatch_main_q as *const c_void,
            &mut ctx as *mut TisQueryCtx as *mut c_void,
            tis_query_main_thread,
        );
    }
    ctx.result
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    /// dirty (VK_DBE_* / VK_KANJI を直近検知) なら、JIS キーボードでなくても IME_OPEN を信頼する。
    #[test]
    fn hook_flag_wins_when_dirty() {
        assert!(matches!(
            select_ime_source(true, false),
            ImeSource::HookFlag
        ));
    }

    /// JIS キーボード確認済みなら、dirty でなくても IME_OPEN を信頼する (Path A)。
    #[test]
    fn hook_flag_wins_when_jis_keyboard_seen() {
        assert!(matches!(
            select_ime_source(false, true),
            ImeSource::HookFlag
        ));
    }

    /// dirty でも JIS キーボードでもないときだけ、TIS 問い合わせ (Path B) にフォールバックする。
    /// ★ ここが ANSI/US キーボードでの唯一の検出経路なので、条件を緩めてはならない。
    #[test]
    fn tis_query_only_when_neither_signal_present() {
        assert!(matches!(
            select_ime_source(false, false),
            ImeSource::TisQuery
        ));
    }

    /// 両方 true でも HookFlag 優先 (TIS 問い合わせをしない = dispatch_sync_f を避けられる)。
    #[test]
    fn hook_flag_wins_when_both_signals_present() {
        assert!(matches!(select_ime_source(true, true), ImeSource::HookFlag));
    }
}
