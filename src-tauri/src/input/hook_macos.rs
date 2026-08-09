// macOS keyboard hook via CGEventTap.
// Primary: kCGEventTapOptionListenOnly → requires Input Monitoring permission.
// Fallback: kCGEventTapOptionDefault → requires Accessibility permission.
//   ad-hoc 署名では Input Monitoring の TCC CDHash 認証が不安定なため、
//   10回連続失敗後に Accessibility 権限へ自動フォールバックする。
// Runs on a dedicated thread with its own CFRunLoop, mirroring the Windows WH_KEYBOARD_LL design.

use std::sync::atomic::{AtomicPtr, AtomicU32, Ordering};
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use core_foundation::base::TCFType;
use core_foundation::mach_port::CFMachPortRef;
use core_foundation::runloop::{kCFRunLoopDefaultMode, CFRunLoop};
use core_graphics::event::{
    CGEvent, CGEventFlags, CGEventTap, CGEventTapLocation, CGEventTapOptions, CGEventTapPlacement,
    CGEventType, EventField,
};

use super::{
    EVENT_SENDER, IME_ACTIVE, IME_COMPOSING, IME_OPEN, IME_STATE_DIRTY, JIS_KEYBOARD_SEEN,
    LAST_KEY_MS, POLL_WAKE_TX, VK_DBE_ALPHANUMERIC, VK_DBE_DBCSCHAR, VK_DBE_HIRAGANA,
    VK_DBE_KATAKANA, VK_DBE_SBCSCHAR, VK_KANJI,
};
use crate::analysis::features::InputEvent;

// Input Monitoring permission check/request.
// These are in the ApplicationServices framework, umbrella-linked via CoreGraphics.
#[link(name = "ApplicationServices", kind = "framework")]
extern "C" {
    fn CGPreflightListenEventAccess() -> bool;
    fn CGRequestListenEventAccess() -> bool;
    // Accessibility permission check.
    // Returns true if this process is trusted for Accessibility.
    fn AXIsProcessTrusted() -> bool;
    // Accessibility permission check with options.
    // Pass a CFDictionary with { kAXTrustedCheckOptionPrompt: true } to show
    // a native system dialog that adds the app to the Accessibility list.
    fn AXIsProcessTrustedWithOptions(options: core_foundation::base::CFTypeRef) -> bool;
}

// CGEventTapEnable: tap の有効/無効を切り替える CoreGraphics API。
// core-graphics 0.24 では crate 非公開 (public は CGEventTap::enable() のみで tap 実体が要る)
// のため、callback から失効した tap を即再有効化する目的で自前宣言する (F4)。
// TODO: core-graphics が CGEventTap::enable() 以外 (port 単独の再有効化 API) を公開したら
//       自前 extern を撤去して crate 側へ差し替える。
#[link(name = "CoreGraphics", kind = "framework")]
extern "C" {
    fn CGEventTapEnable(tap: CFMachPortRef, enable: bool);
}

/// 現在有効な CGEventTap の mach port (CFMachPortRef を `*mut c_void` として保持)。
///
/// tap 生成・有効化後に格納し、runloop 退出 (失効) 時に null クリアする。callback が
/// `TapDisabledByTimeout`/`ByUserInput` を受けたとき、この port を読んで
/// `CGEventTapEnable(port, true)` で**作り直さず即再有効化**する (F4 主修正)。
///
/// スレッド安全性は 2 つの性質を**別々の根拠**で担保する:
/// - **可視性**: `store(Release)` / `load(Acquire)` で書き込みが callback 側へ可視になる
///   (`Ordering` が保証するのはここまで。ライフタイム安全性の根拠ではない)。
/// - **ライフタイム安全性 (UAF 回避)**: 書き込み (hook スレッド本体) と読み出し (callback) は
///   同一 hook スレッド上で起き、callback は `CFRunLoop::run_current()` 実行中にのみ動作する
///   (Apple: イベントは「tap source を追加した run loop を回すスレッド」上の callback へ届く)。
///   port の store は run_current の前、null クリアは run_current から戻った後で行うため、
///   本体と callback は**時間的に排他** (本体が run_current でブロック中だけ callback が走る)。
///   よって port が指す `tap.mach_port` は callback 実行中 (格納〜null クリアの間) 常に生存する。
/// `AtomicPtr` は安全な共有セルとして用いる。
static TAP_PORT: AtomicPtr<std::ffi::c_void> = AtomicPtr::new(std::ptr::null_mut());

/// 直近で normal イベントを 1 件も挟まずに連続して tap 再有効化した回数 (F4)。
///
/// 病的ケース (tap を有効化してもカーネルが即再 disable する) で callback が
/// 再有効化を無限に繰り返すスラッシングを防ぐための上限カウンタ。normal イベントが
/// 1 件でも届けば tap 健全とみなして 0 にリセットし、tap 生成時にも 0 に戻す。
/// 上限超過後は再有効化を諦める — `LAST_KEY_MS` は保持されるため idle は増加し続け
/// away に倒れる (離席誤発火を起こさない fail-safe な縮退)。
static CONSECUTIVE_REENABLES: AtomicU32 = AtomicU32::new(0);

/// `CONSECUTIVE_REENABLES` の上限。event-driven な disable では 100 連続 (間に
/// normal イベント 0 件) は「恒常的に再 disable されている」ことを意味する。
const MAX_CONSECUTIVE_REENABLES: u32 = 100;

// GCD: メインスレッドへの dispatch に使用。
// AXIsProcessTrustedWithOptions のネイティブダイアログは NSApplication の
// ランループ (= メインスレッド) でのみ表示される。バックグラウンドの
// フックスレッドから直接呼ぶとダイアログが表示されない。
// ime_macos.rs の TIS クエリと同じパターン。
#[link(name = "System", kind = "dylib")]
extern "C" {
    #[allow(non_upper_case_globals)]
    static _dispatch_main_q: std::ffi::c_void;
    fn dispatch_sync_f(
        queue: *const std::ffi::c_void,
        context: *mut std::ffi::c_void,
        work: unsafe extern "C" fn(*mut std::ffi::c_void),
    );
}

struct AxPromptCtx {
    result: bool,
}

/// GCD メインスレッド上で AXIsProcessTrustedWithOptions を実行するコールバック。
unsafe extern "C" fn ax_prompt_main_thread(ctx: *mut std::ffi::c_void) {
    use core_foundation::base::TCFType;
    use core_foundation::boolean::CFBoolean;
    use core_foundation::dictionary::CFDictionary;
    use core_foundation::string::CFString;

    let ctx = &mut *(ctx as *mut AxPromptCtx);
    let key = CFString::new("AXTrustedCheckOptionPrompt");
    let value = CFBoolean::true_value();
    let dict = CFDictionary::from_CFType_pairs(&[(key.as_CFType(), value.as_CFType())]);
    ctx.result = AXIsProcessTrustedWithOptions(dict.as_CFTypeRef());
}

/// Accessibility 権限をネイティブダイアログでプロンプトする。
/// GCD dispatch_sync_f でメインスレッドに dispatch する。
/// フックスレッド (バックグラウンド) から呼ぶため deadlock しない。
fn ax_prompt_for_trust() -> bool {
    let mut ctx = AxPromptCtx { result: false };
    // SAFETY: dispatch_sync_f はメインキューにブロッキング dispatch する。
    // フックスレッドから呼ぶため deadlock しない (メインスレッドからは呼ばないこと)。
    // _dispatch_main_q は libSystem の公開グローバル変数。
    // ctx はスタック上に存在し、dispatch_sync_f は完了まで返らないため有効。
    unsafe {
        dispatch_sync_f(
            &_dispatch_main_q as *const _ as *const std::ffi::c_void,
            &mut ctx as *mut AxPromptCtx as *mut std::ffi::c_void,
            ax_prompt_main_thread,
        );
    }
    ctx.result
}

use super::{
    CALLBACK_COUNT, CONSECUTIVE_TAP_FAILURES, EVENTS_DROPPED, HOOK_ACTIVE,
    USING_ACCESSIBILITY_FALLBACK,
};

// ---------------------------------------------------------------------------
// macOS typing key filter (raw CGKeyCode)
//
// フック層でタイピングリズムに影響するキーのみを分析チャネルへ送信する。
// 矢印キー・ファンクションキー・修飾キー・IMEトグルキーは除外する。
// 共通コア（features.rs）は「バッファ内のイベントは全てタイピングキー」を前提とする。
//
// CGKeyCode レイアウト:
//   0x00..=0x09: 英字 (A,S,D,F,H,G,Z,X,C,V)
//   0x0A:        ISO § キー (ANSI キーボードには存在しない — 除外)
//   0x0B..=0x33: 英字・数字・記号・編集キー (B,Q,W,..,Tab,Space,`,Delete)
//   0x75:        Forward Delete
// ---------------------------------------------------------------------------
fn is_typing_key(mac_vk: u64) -> bool {
    matches!(mac_vk,
        0x00..=0x09   // kVK_ANSI_A .. kVK_ANSI_V (letters)
        | 0x0B..=0x33 // kVK_ANSI_B .. kVK_Delete (letters, digits, symbols, Return, Tab, Space, Backspace)
        | 0x75        // kVK_ForwardDelete
    )
}

// ---------------------------------------------------------------------------
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
        0x68 => VK_KANJI,            // kVK_JIS_Kana → かな toggle
        0x90 => VK_DBE_HIRAGANA,     // alternate かな on some JIS layouts
        0x91 => VK_DBE_KATAKANA,     // alternate カタカナ on some JIS layouts

        // Pass-through for unmapped keys.
        // Key identity is not critical for timing features (F1-F5).
        other => other as u32,
    }
}

// ---------------------------------------------------------------------------
// CGEventTap callback
// ---------------------------------------------------------------------------
fn handle_event(event_type: CGEventType, event: &CGEvent) {
    // F4: tap が OS 都合 (重い処理 / ユーザー入力割り込み) で無効化されたら
    // **作り直さず即再有効化**する。これらの disabled イベントは event mask に
    // 関わらず callback へ届く。CGEventType は PartialEq 未実装のため matches! で判定。
    if matches!(
        event_type,
        CGEventType::TapDisabledByTimeout | CGEventType::TapDisabledByUserInput
    ) {
        // スラッシング防止: normal イベントを挟まず連続再有効化した回数が上限未満の
        // ときだけ再有効化する。上限超過後は諦める (LAST_KEY_MS 保持 → idle 増加 →
        // away に倒れる fail-safe な縮退)。
        let n = CONSECUTIVE_REENABLES.fetch_add(1, Ordering::Relaxed);
        if n < MAX_CONSECUTIVE_REENABLES {
            let port = TAP_PORT.load(Ordering::Acquire);
            if !port.is_null() {
                // SAFETY: port は同一 hook スレッドで格納/null クリアされる有効な
                // CFMachPortRef (null チェック済み)。CGEventTapEnable は Apple 推奨の
                // 軽量な再有効化呼び出しで、tap の runloop スレッド (= この callback) から
                // 呼ぶのが正しい。ブロッキング I/O・ヒープ確保・ログは行わない。
                unsafe {
                    CGEventTapEnable(port as CFMachPortRef, true);
                }
            }
        }
        return;
    }

    // normal イベント到達 = tap 健全 → 連続再有効化カウンタをリセット。
    CONSECUTIVE_REENABLES.store(0, Ordering::Relaxed);

    // 診断用: コールバック到達カウンタ。0 のままなら「イベントが届いていない」。
    CALLBACK_COUNT.fetch_add(1, Ordering::Relaxed);

    let is_press = matches!(event_type, CGEventType::KeyDown);
    let is_release = matches!(event_type, CGEventType::KeyUp);

    if !is_press && !is_release {
        return;
    }

    let mac_vk = event.get_integer_value_field(EventField::KEYBOARD_EVENT_KEYCODE) as u64;
    let vk_code = macos_vk_to_vk(mac_vk);

    // macOS キーリピート検出: KeyDown のみ連射され KeyUp は最後の1回だけ。
    // リピートイベントは flight time 計算を狂わせるため InputEvent でマークする。
    let is_repeat =
        is_press && event.get_integer_value_field(EventField::KEYBOARD_EVENT_AUTOREPEAT) != 0;

    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64;

    // Update last keystroke timestamp for idle detection.
    // NOTE: 矢印キー等の非文字キーも LAST_KEY_MS を更新するが、
    // HMM（分析チャネル）には送られずサイレンス扱いとなる。そのため
    // 「UI 上は Active だが HMM 推論上は Incubation（沈黙）」という
    // 意図的な状態乖離が発生し得る（非文字キーだけの操作は稀なため許容）。
    LAST_KEY_MS.store(timestamp, Ordering::Relaxed);

    // IME mode tracking via JIS physical IME keys.
    // Mirrors the Windows VK_DBE_* handler in windows_impl.rs.
    // ANSI keyboards: these codes never arrive; TIS polling in ime_macos.rs
    // handles mode detection instead.
    if is_press {
        match vk_code {
            VK_DBE_ALPHANUMERIC | VK_DBE_SBCSCHAR => {
                JIS_KEYBOARD_SEEN.store(true, Ordering::Relaxed);
                IME_OPEN.store(false, Ordering::Release);
                IME_STATE_DIRTY.store(true, Ordering::Release);
            }
            VK_DBE_KATAKANA | VK_DBE_HIRAGANA | VK_DBE_DBCSCHAR => {
                JIS_KEYBOARD_SEEN.store(true, Ordering::Relaxed);
                IME_OPEN.store(true, Ordering::Release);
                IME_STATE_DIRTY.store(true, Ordering::Release);
            }
            VK_KANJI => {
                JIS_KEYBOARD_SEEN.store(true, Ordering::Relaxed);
                IME_OPEN.fetch_xor(true, Ordering::AcqRel);
                IME_STATE_DIRTY.store(true, Ordering::Release);
            }
            _ => {}
        }
    }
    // Also handle key-up for JIS IME keys (mirrors Surface Type Cover quirk handling)
    if is_release {
        match vk_code {
            VK_DBE_KATAKANA | VK_DBE_HIRAGANA | VK_DBE_DBCSCHAR => {
                IME_OPEN.store(true, Ordering::Release);
                IME_STATE_DIRTY.store(true, Ordering::Release);
            }
            VK_DBE_ALPHANUMERIC | VK_DBE_SBCSCHAR => {
                IME_OPEN.store(false, Ordering::Release);
                IME_STATE_DIRTY.store(true, Ordering::Release);
            }
            _ => {}
        }
    }

    // ── IME composition / candidate state machine ────────────────────────
    // Tracks whether the user is navigating the IME candidate window.
    // Only active when IME_OPEN is true (Japanese input mode).
    //
    // State transitions (on keyDown only):
    //   Letter/digit → COMPOSING (inline text being composed)
    //   Space while COMPOSING → IME_ACTIVE (candidate window shown)
    //   Enter/Escape → reset both (composition confirmed/cancelled)
    //   Letter while IME_ACTIVE → reset IME_ACTIVE (candidate accepted, new composition)
    //   Backspace while IME_ACTIVE → reset IME_ACTIVE (back to editing inline)
    //   IME mode switch to off → reset both
    if is_press {
        if IME_OPEN.load(Ordering::Acquire) {
            update_compose_state(vk_code);
        } else {
            // IME switched off → reset composition state.
            let was_composing = IME_COMPOSING.swap(false, Ordering::Release);
            let was_active = IME_ACTIVE.swap(false, Ordering::Release);
            if was_composing || was_active {
                tracing::debug!("IME compose state reset (IME_OPEN=false)");
            }
        }
    }

    // Send keystroke event to analysis thread (lock-free, non-blocking).
    // Filter at hook level: skip key repeats (cause Press/Release imbalance and
    // inflate backspace streak) and non-typing keys (arrows, function keys, IME
    // toggles — don't affect typing rhythm). IME tracking and
    // LAST_KEY_MS are already handled above.
    //
    // NOTE: キーリピート除外により、Backspace 長押し（hold-to-delete）は Press 1回
    // + Release 1回のみ分析スレッドに届く。結果として:
    //   - register_keystroke() の BS ストリークは長押しでは増加しない（閾値14に未達）
    //   - F3（修正率）も長押し削除を1回としかカウントしない
    // これは「長押し = 意図的な一括削除 ≠ フラストレーション」という設計判断に基づく。
    // 連打（タップ連射）のみが Stuck シグナルとして検出される。
    if !is_repeat && is_typing_key(mac_vk) {
        if let Some(sender) = EVENT_SENDER.get() {
            // macOS: kVK_Delete(Backspace) = 0x33, kVK_ForwardDelete = 0x75
            // OS 固有キーコードからフラグを生成し、共通コアにはフラグのみ渡す。
            let is_backspace = mac_vk == 0x33 || mac_vk == 0x75;
            // ペースト検出: V(0x56) 押下時に Command 修飾が立っていれば Cmd+V とみなす。
            // 修飾キーは FlagsChanged で来るため Atomic 追跡できないが、各 KeyDown が運ぶ
            // CGEvent::get_flags() を読めば現在の Command 状態が分かる。
            // クリップボードの中身には一切触れず、VK + 修飾フラグのみで判定する。
            let is_paste = is_press
                && vk_code == 0x56
                && event.get_flags().contains(CGEventFlags::CGEventFlagCommand);
            if sender
                .try_send(InputEvent {
                    vk_code,
                    timestamp,
                    is_press,
                    is_repeat,
                    is_backspace,
                    is_paste,
                })
                .is_err()
            {
                // ⚠️★ コールバック内でログを書かない (`hook-constraints` mac-1 / 共通-1)。
                //   ★ カウンタだけ上げ、監視スレッドが統計的に 1 回だけ報告する (共通-3)。
                EVENTS_DROPPED.fetch_add(1, Ordering::Relaxed);
            }
        }
    }

    // Wake the IME polling thread on every keypress
    let is_ime_mode_key = matches!(
        vk_code,
        VK_DBE_ALPHANUMERIC
            | VK_DBE_KATAKANA
            | VK_DBE_HIRAGANA
            | VK_DBE_SBCSCHAR
            | VK_DBE_DBCSCHAR
            | VK_KANJI
    );
    if is_press || (is_release && is_ime_mode_key) {
        if let Some(tx) = POLL_WAKE_TX.get() {
            let _ = tx.try_send(());
        }
    }
}

// ---------------------------------------------------------------------------
// IME composition state machine
// ---------------------------------------------------------------------------

/// Update IME_COMPOSING and IME_ACTIVE based on the current keyDown VK code.
/// Called only when IME_OPEN is true and the event is a keyDown.
fn update_compose_state(vk: u32) {
    let composing = IME_COMPOSING.load(Ordering::Relaxed);
    let active = IME_ACTIVE.load(Ordering::Relaxed);

    // VK_SPACE = 0x20, VK_RETURN = 0x0D, VK_ESCAPE = 0x1B, VK_BACK = 0x08, VK_TAB = 0x09
    match vk {
        // Letter keys (A-Z: 0x41-0x5A) and digit keys (0-9: 0x30-0x39)
        // → Start/continue composition.
        0x30..=0x39 | 0x41..=0x5A => {
            if active {
                // Typing a new character while candidates showing →
                // accept current candidate, start new composition.
                IME_ACTIVE.store(false, Ordering::Release);
                tracing::debug!("IME_ACTIVE → false (new char during candidate)");
            }
            if !composing {
                IME_COMPOSING.store(true, Ordering::Release);
                tracing::debug!("IME_COMPOSING → true (char typed in Japanese mode)");
            }
        }
        // Space → trigger conversion (show candidate window) if composing.
        0x20 => {
            if composing && !active {
                IME_ACTIVE.store(true, Ordering::Release);
                tracing::debug!("IME_ACTIVE → true (Space during composition → candidates)");
            }
            // If already active, Space cycles to next candidate — stay active.
        }
        // Enter → confirm composition/candidate selection.
        0x0D => {
            if composing || active {
                IME_COMPOSING.store(false, Ordering::Release);
                IME_ACTIVE.store(false, Ordering::Release);
                tracing::debug!("IME compose/active → false (Enter confirms)");
            }
        }
        // Escape → cancel composition.
        0x1B => {
            if composing || active {
                IME_COMPOSING.store(false, Ordering::Release);
                IME_ACTIVE.store(false, Ordering::Release);
                tracing::debug!("IME compose/active → false (Escape cancels)");
            }
        }
        // Backspace while candidating → back to inline editing.
        0x08 => {
            if active {
                IME_ACTIVE.store(false, Ordering::Release);
                tracing::debug!("IME_ACTIVE → false (Backspace exits candidate)");
            }
            // Stay composing (editing inline text).
        }
        // Arrow keys (Left/Up/Right/Down: 0x25-0x28) → candidate navigation.
        // Stay in current state.
        0x25..=0x28 => {}
        // IME mode keys — handled elsewhere, ignore here.
        _ if vk >= 0xF0 || vk == VK_KANJI => {}
        // Other keys → reset composition state (e.g., Tab, function keys).
        _ => {
            if composing || active {
                IME_COMPOSING.store(false, Ordering::Release);
                IME_ACTIVE.store(false, Ordering::Release);
                tracing::debug!("IME compose/active → false (other key: VK=0x{:02X})", vk);
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Public entry point
// ---------------------------------------------------------------------------

/// Install the CGEventTap and start listening on a dedicated thread with CFRunLoop.
///
/// Permission flow:
/// 1. Check `CGPreflightListenEventAccess()` — fast, no side-effects.
/// 2. If not granted, call `CGRequestListenEventAccess()` — opens System Settings.
/// 3. Unified loop: try creating the tap directly. If it fails, sleep and retry.
/// 4. **Smart permission detection**: At startup, if Input Monitoring is denied
///    but Accessibility is granted, skip ListenOnly and use Default tap directly.
/// 5. **Accessibility fallback**: If ListenOnly fails 3 times consecutively,
///    switch to `CGEventTapOptions::Default` (requires Accessibility permission).
///    ad-hoc 署名では Input Monitoring の TCC CDHash 認証が不安定なため、
///    異なる TCC パスを試すことで権限取得の成功率を向上させる。
///
/// `HOOK_ACTIVE` is set to true only after a successful tap installation.
pub fn start() {
    thread::spawn(|| {
        // --- Step 1: Smart permission detection ---
        // 両方の権限を起動時にチェックし、最適なパスを即座に選択する。
        // SAFETY: CGPreflightListenEventAccess / AXIsProcessTrusted は
        // pure read-only の TCC チェック。メモリ安全性への影響なし。
        let im_granted = unsafe { CGPreflightListenEventAccess() };
        let ax_trusted = unsafe { AXIsProcessTrusted() };

        // スマート権限検出:
        // Input Monitoring が拒否されているが Accessibility が付与済みなら、
        // ListenOnly の無駄な失敗を待たず、即座に Default tap を使用する。
        // ad-hoc 署名では Input Monitoring の TCC CDHash 認証が不安定なため、
        // Accessibility が使えるなら最初からそちらを選ぶ。
        let mut use_accessibility = if !im_granted && ax_trusted {
            tracing::info!(
                "Input Monitoring denied but Accessibility granted. \
                 Using Default tap (Accessibility) directly — skipping ListenOnly."
            );
            USING_ACCESSIBILITY_FALLBACK.store(true, Ordering::Release);
            true
        } else {
            if !im_granted {
                // --- Step 2: Request Input Monitoring permission ---
                tracing::warn!(
                    "Input Monitoring permission not granted. \
                     Opening System Settings > Privacy & Security > Input Monitoring..."
                );
                // SAFETY: CGRequestListenEventAccess はシステムダイアログ表示のみ。
                unsafe { CGRequestListenEventAccess() };
                tracing::info!("Polling for Input Monitoring permission...");
            }
            false
        };

        let mut consecutive_failures: u32 = 0;

        // --- Step 3: Resilient tap creation loop (never gives up) ---
        //
        // ListenOnly (Input Monitoring) → 10回失敗後 → Default (Accessibility) にフォールバック。
        //
        // HeadInsertEventTap + ListenOnly: イベントチェーンの先頭で受動的に傍受。
        // rdev クレート等の実績ある実装と同じ組み合わせ。
        //
        // Default (Accessibility fallback): 同じ HeadInsertEventTap だが active tap として作成。
        // コールバックは event.clone() を返してイベントを変更せずに通過させる。
        // Input Monitoring とは異なる TCC カテゴリ (kTCCServiceAccessibility) を使用するため、
        // ad-hoc 署名の CDHash 問題を回避できる可能性がある。
        //
        // 自動復旧: CFRunLoop が終了した場合はループ先頭に戻ってタップを再作成する。
        loop {
            // --- Accessibility fallback trigger ---
            // 3回失敗で切替。input_monitoring_granted=false の場合、
            // ListenOnly が成功する可能性はゼロなので早期に切り替える。
            if !use_accessibility && consecutive_failures >= 3 {
                tracing::warn!(
                    "Input Monitoring (ListenOnly) failed {} times. \
                     Switching to Accessibility permission fallback (Default tap)...",
                    consecutive_failures
                );
                use_accessibility = true;
                USING_ACCESSIBILITY_FALLBACK.store(true, Ordering::Release);
                // ネイティブダイアログで Accessibility 権限をプロンプトする。
                // AXIsProcessTrustedWithOptions は:
                //   1. ネイティブのシステムダイアログを表示
                //   2. アプリを Accessibility リストに自動追加
                //   3. ユーザーに「システム設定を開く」ボタンを提供
                // URL scheme で System Settings を開く方式より確実。
                let ax_trusted = ax_prompt_for_trust();
                if !ax_trusted {
                    tracing::info!(
                        "Accessibility permission not granted. \
                         Native prompt dialog shown. Also opening System Settings as fallback."
                    );
                    // ネイティブダイアログが抑制された場合のフォールバック:
                    // System Settings の Accessibility ペインを直接開く。
                    if let Err(e) = std::process::Command::new("open")
                        .arg("x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility")
                        .spawn()
                    {
                        tracing::warn!("Failed to open System Settings: {}", e);
                    }
                }
                // リセットして Accessibility モードでのリトライを開始
                consecutive_failures = 0;
                CONSECUTIVE_TAP_FAILURES.store(0, Ordering::Relaxed);
            }

            let mode_label = if use_accessibility {
                "Accessibility"
            } else {
                "Input Monitoring"
            };

            let tap_options = if use_accessibility {
                CGEventTapOptions::Default
            } else {
                CGEventTapOptions::ListenOnly
            };

            // Accessibility fallback では event を pass-through するため clone が必要。
            // use_accessibility を closure に move (Copy) でキャプチャする。
            let ax_mode = use_accessibility;
            let tap = CGEventTap::new(
                CGEventTapLocation::Session,
                CGEventTapPlacement::HeadInsertEventTap,
                tap_options,
                vec![CGEventType::KeyDown, CGEventType::KeyUp],
                move |_proxy, event_type, event| {
                    if ax_mode {
                        // Default (active) tap: panic 時にイベントが消費されてシステム全体の
                        // キー入力が無応答になるリスクを回避するため catch_unwind で保護する。
                        // ListenOnly では戻り値が無視されるため不要。
                        let cloned = event.clone();
                        let _ = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                            handle_event(event_type, event);
                        }));
                        // core-graphics の CGEvent::clone() は内部で CGEventCreateCopy() を呼び、
                        // O(1) のリファレンスカウント操作のみでブロッキングなし。
                        // &CGEvent → Option<CGEvent> 変換のため clone は API 制約上不可避。
                        Some(cloned)
                    } else {
                        handle_event(event_type, event);
                        None // ListenOnly: 戻り値は無視される
                    }
                },
            );

            match tap {
                Ok(tap) => {
                    // タップ作成成功 → 連続失敗カウンタをリセット
                    consecutive_failures = 0;
                    CONSECUTIVE_TAP_FAILURES.store(0, Ordering::Relaxed);

                    let loop_source = match tap.mach_port.create_runloop_source(0) {
                        Ok(source) => source,
                        Err(_) => {
                            tracing::error!(
                                "Failed to create CFRunLoop source from CGEventTap, \
                                 retrying in 2s..."
                            );
                            HOOK_ACTIVE.store(false, Ordering::Relaxed);
                            // F4: LAST_KEY_MS は最後の物理打鍵時刻 (セッション非依存)。
                            // OS 都合の一時失効はキーボード活動と無関係なので 0 に倒さず保持し、
                            // idle/away の連続性を保つ (離席中のプローブ誤発火を防ぐ)。
                            // 防衛的: この tap は使わず作り直すため TAP_PORT を null クリアし
                            // (stale port を callback が触らないよう不変条件を経路非依存にする)、
                            // 連続再有効化カウンタもリセットする。
                            TAP_PORT.store(std::ptr::null_mut(), Ordering::Release);
                            CONSECUTIVE_REENABLES.store(0, Ordering::Relaxed);
                            std::thread::sleep(std::time::Duration::from_secs(2));
                            continue;
                        }
                    };

                    let run_loop = CFRunLoop::get_current();
                    // SAFETY: kCFRunLoopDefaultMode は CoreFoundation 定数。常に有効。
                    run_loop.add_source(&loop_source, unsafe { kCFRunLoopDefaultMode });

                    // タップを有効化してから HOOK_ACTIVE をセット。
                    // 50ms 待機でカーネルレベルのタップ活性化を確実にする。
                    tap.enable();
                    thread::sleep(Duration::from_millis(50));
                    HOOK_ACTIVE.store(true, Ordering::Release);
                    // F4: callback (TapDisabled*) から即再有効化できるよう mach port を公開する。
                    // tap はこの loop iteration の間 (run_current 中) 生存しており、退出時に
                    // null クリアするため callback が stale port を触ることはない。
                    TAP_PORT.store(
                        tap.mach_port.as_concrete_TypeRef() as *mut std::ffi::c_void,
                        Ordering::Release,
                    );
                    // ⚠️★★ **`CALLBACK_COUNT` を 0 に戻さない。**
                    //   2026-08-09 以降、このカウンタは `input::liveness` が
                    //   「フックが呼ばれ続けているか」を見る**単調増加の生存信号**になった。
                    //   ★ ここで 0 に戻すと、監視スレッドから見て値が「変化した」ように見え、
                    //   ⚠️ **タップ再作成が偽の生存シグナルになる**
                    //   (= 死んでいるのに Ok と判定する)。
                    //   ★ `LAST_KEY_MS` を 0 に戻さないのと同じ理由である (F4)。
                    //   「このタップで何回呼ばれたか」を診断したい場合は、
                    //   ★ 差分で見ること (get_diagnostics は累計を出す)。
                    CONSECUTIVE_REENABLES.store(0, Ordering::Relaxed);
                    tracing::info!(
                        "CGEventTap installed via {} (macOS keyboard hook active)",
                        mode_label
                    );

                    CFRunLoop::run_current();

                    // CFRunLoopRun returned — tap was disabled or invalidated.
                    HOOK_ACTIVE.store(false, Ordering::Relaxed);
                    // F4: LAST_KEY_MS は 0 に倒さない (上の理由と同じ)。失効前の最終打鍵時刻を
                    // 保持することで Dashboard idle カウンタの突然の 0 リセット・離席判定の崩れ・
                    // ランダムプローブの離席中誤発火を防ぐ。
                    // TAP_PORT は無効化された tap を指したままなので null クリアし、
                    // 次の callback が stale port へ CGEventTapEnable を呼ばないようにする。
                    TAP_PORT.store(std::ptr::null_mut(), Ordering::Release);
                    tracing::warn!(
                        "CGEventTap CFRunLoop exited (tap invalidated by macOS). \
                         Re-creating in 2s..."
                    );
                    std::thread::sleep(std::time::Duration::from_secs(2));
                }
                Err(_) => {
                    consecutive_failures += 1;
                    CONSECUTIVE_TAP_FAILURES.store(consecutive_failures, Ordering::Relaxed);

                    // --- 定期リプロンプト (Accessibility フォールバック中、10回ごと) ---
                    // macOS はダイアログ表示を頻繁すぎると抑制する可能性があるため、
                    // 10回間隔 (約30-50秒) で再プロンプトする。抑制されても
                    // AXIsProcessTrustedWithOptions は現在の trust 状態を返すだけで副作用なし。
                    if use_accessibility
                        && consecutive_failures > 0
                        && consecutive_failures % 10 == 0
                    {
                        // SAFETY: AXIsProcessTrusted は pure read-only チェック。
                        let ax_now = unsafe { AXIsProcessTrusted() };
                        if !ax_now {
                            tracing::info!(
                                "Re-prompting for Accessibility permission (attempt {})",
                                consecutive_failures
                            );
                            ax_prompt_for_trust();
                        }

                        // Input Monitoring が別途付与された場合、ListenOnly に復帰する。
                        // CGPreflightListenEventAccess は副作用ゼロの read-only チェック。
                        let im_now = unsafe { CGPreflightListenEventAccess() };
                        if im_now {
                            tracing::info!(
                                "Input Monitoring now granted! \
                                 Switching back from Accessibility fallback."
                            );
                            use_accessibility = false;
                            USING_ACCESSIBILITY_FALLBACK.store(false, Ordering::Release);
                            consecutive_failures = 0;
                            CONSECUTIVE_TAP_FAILURES.store(0, Ordering::Relaxed);
                        }
                    }

                    // Backoff strategy:
                    //   1-5回: 2秒間隔 (TCC 伝播待ち / 権限付与待ち)
                    //   6-20回: 5秒間隔 (長めの権限待ち)
                    //   21回以降: 10秒間隔 (CPU 節約しつつ永続的にリトライ)
                    let sleep_secs = if consecutive_failures <= 5 {
                        if consecutive_failures == 1 || im_granted {
                            tracing::warn!(
                                "CGEventTap creation failed via {} (attempt {}), retrying in 2s...",
                                mode_label,
                                consecutive_failures
                            );
                        }
                        2
                    } else if consecutive_failures <= 20 {
                        if consecutive_failures == 6 {
                            tracing::warn!(
                                "CGEventTap creation still failing via {} after 5 attempts. \
                                 Retrying every 5s. Try toggling the permission off then on.",
                                mode_label
                            );
                        }
                        5
                    } else {
                        if consecutive_failures == 21 {
                            tracing::error!(
                                "CGEventTap creation failed 20+ times via {}. Slowing to 10s. \
                                 Try: tccutil reset ListenEvent → restart app",
                                mode_label
                            );
                        }
                        10
                    };

                    std::thread::sleep(std::time::Duration::from_secs(sleep_secs));
                }
            }
        }
    });
}
