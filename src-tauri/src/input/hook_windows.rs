// Windows keyboard hook via WH_KEYBOARD_LL + WinEvent for cross-process IME detection.

use std::sync::atomic::Ordering;
use std::sync::Mutex;
use std::thread;
use std::time::{SystemTime, UNIX_EPOCH};

use lazy_static::lazy_static;
use windows::Win32::Foundation::{HINSTANCE, HMODULE, HWND, LPARAM, LRESULT, WPARAM};
use windows::Win32::System::LibraryLoader::GetModuleHandleW;
use windows::Win32::UI::Accessibility::{SetWinEventHook, HWINEVENTHOOK};
use windows::Win32::UI::WindowsAndMessaging::{
    CallNextHookEx, DispatchMessageW, PeekMessageW, SetWindowsHookExW, HHOOK, KBDLLHOOKSTRUCT,
    MSG, PM_NOREMOVE, PM_REMOVE, WH_KEYBOARD_LL, WM_KEYDOWN, WM_KEYUP, WM_QUIT, WM_SYSKEYDOWN,
    WM_SYSKEYUP,
};

use super::{
    EVENT_SENDER, HOOK_ACTIVE, IME_ACTIVE, IME_OPEN, IME_STATE_DIRTY, LAST_KEY_MS, POLL_WAKE_TX,
    VK_DBE_ALPHANUMERIC, VK_DBE_DBCSCHAR, VK_DBE_HIRAGANA, VK_DBE_KATAKANA, VK_DBE_SBCSCHAR,
    VK_KANJI,
};
use crate::analysis::features::InputEvent;

/// タイピングリズムに関連するキーかどうかを判定する（Windows固有のVKコード）。
fn is_typing_key(vk_code: u32) -> bool {
    matches!(
        vk_code,
        0x41..=0x5A       // Letters A-Z
        | 0x30..=0x39     // Digits 0-9
        | 0x60..=0x6F     // Numpad keys
        | 0xBA..=0xC0     // Symbol / punctuation keys (OEM)
        | 0xDB..=0xDF
        | 0x08            // Backspace
        | 0x0D            // Enter
        | 0x20            // Space
        | 0x09            // Tab
        | 0x2E            // Delete
    )
}

// IME WinEvent constants (winuser.h, Windows 8+)
const EVENT_OBJECT_IME_CHANGE: u32 = 0x8016;
const EVENT_OBJECT_IME_SHOW: u32 = 0x8017;
const EVENT_OBJECT_IME_HIDE: u32 = 0x8018;
const WINEVENT_OUTOFCONTEXT: u32 = 0x0000;
const WINEVENT_SKIPOWNPROCESS: u32 = 0x0002;

// Wrapper to make HHOOK Send+Sync for lazy_static.
// SAFETY: HHOOK / HWINEVENTHOOK はインストールスレッドでのみ操作される。
// lazy_static Mutex で排他制御されており、他スレッドからの直接操作は行わない。
// これらのハンドルをインストールスレッド以外から UnhookWindowsHookEx 等で
// 操作してはならない。
struct ThreadSafeHook(#[allow(dead_code)] HHOOK);
unsafe impl Send for ThreadSafeHook {}
unsafe impl Sync for ThreadSafeHook {}

struct ThreadSafeWinEventHook(#[allow(dead_code)] HWINEVENTHOOK);
unsafe impl Send for ThreadSafeWinEventHook {}
unsafe impl Sync for ThreadSafeWinEventHook {}

lazy_static! {
    static ref HOOK_HANDLE: Mutex<Option<ThreadSafeHook>> = Mutex::new(None);
    static ref WINEVENT_HOOK_HANDLE: Mutex<Option<ThreadSafeWinEventHook>> = Mutex::new(None);
}

/// WinEvent callback for cross-process IME composition detection.
unsafe extern "system" fn win_event_callback(
    _hook: HWINEVENTHOOK,
    event: u32,
    _hwnd: HWND,
    _id_object: i32,
    _id_child: i32,
    _id_event_thread: u32,
    _dwms_event_time: u32,
) {
    match event {
        EVENT_OBJECT_IME_SHOW | EVENT_OBJECT_IME_CHANGE => {
            IME_ACTIVE.store(true, Ordering::Relaxed);
            IME_OPEN.store(true, Ordering::Release);
            IME_STATE_DIRTY.store(true, Ordering::Release);
            if let Some(tx) = POLL_WAKE_TX.get() {
                let _ = tx.try_send(());
            }
        }
        EVENT_OBJECT_IME_HIDE => {
            IME_ACTIVE.store(false, Ordering::Relaxed);
        }
        _ => {}
    }
}

/// Install WH_KEYBOARD_LL + WinEvent hooks and run the message loop.
/// Called from `init_hook()` in the shared `hook.rs`.
///
/// 自動復旧: メッセージループが終了した場合（Windows がフックを無効化した場合）は
/// スレッドを終了せず、ループ先頭に戻ってフックを再インストールする。
/// フックのインストール失敗時もバックオフ付きでリトライを継続する。
/// これにより、スリープ復帰・セキュリティソフトの一時的なブロック等から自動復旧する。
pub(super) fn start() {
    thread::spawn(|| {
        let mut consecutive_failures: u32 = 0;

        // --- Step 0: メッセージキューの事前初期化 ---
        // WH_KEYBOARD_LL はインストールスレッドにメッセージキューを要求する。
        // PeekMessageW を呼ぶことでキューが確実に作成される。
        // これを省略すると、一部の Windows 11 環境でフックが
        // インストールされてもコールバックが呼ばれない問題が起きる。
        // SAFETY: PeekMessageW は zeroed MSG 構造体で安全に呼び出せる。
        // メッセージキューの事前初期化のみが目的。
        unsafe {
            let mut msg = MSG::default();
            let _ = PeekMessageW(&mut msg, None, 0, 0, PM_NOREMOVE);
        }
        tracing::info!("Hook thread message queue initialized");

        // --- Step 0b: モジュールハンドル取得 ---
        // HINSTANCE::default() (NULL) の代わりに実モジュールハンドルを使用する。
        // Windows 11 の一部環境で NULL を渡すとフックが無効になるケースがある。
        // SAFETY: GetModuleHandleW(None) は現在のプロセスモジュールハンドルを返す。常に安全。
        let hinstance = unsafe {
            match GetModuleHandleW(None) {
                Ok(h) => {
                    tracing::info!("Module handle obtained: {:?}", h.0);
                    HINSTANCE(h.0 as *mut _)
                }
                Err(e) => {
                    tracing::warn!(
                        "GetModuleHandleW failed ({:?}), falling back to NULL",
                        e
                    );
                    HINSTANCE::default()
                }
            }
        };

        loop {
            unsafe {
                // --- Step 1: Install low-level keyboard hook ---
                let hook_id = SetWindowsHookExW(
                    WH_KEYBOARD_LL,
                    Some(hook_callback),
                    hinstance,
                    0,
                );

                match hook_id {
                    Ok(h) => {
                        consecutive_failures = 0;
                        {
                            let mut handle =
                                (*HOOK_HANDLE).lock().unwrap_or_else(|p| p.into_inner());
                            *handle = Some(ThreadSafeHook(h));
                        }

                        // --- Step 2: Install WinEvent hook for cross-process IME composition ---
                        let ime_hook = SetWinEventHook(
                            EVENT_OBJECT_IME_CHANGE,
                            EVENT_OBJECT_IME_HIDE,
                            HMODULE::default(),
                            Some(win_event_callback),
                            0,
                            0,
                            WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS,
                        );

                        if ime_hook.is_invalid() {
                            tracing::warn!("Failed to install IME WinEvent hook");
                        } else {
                            tracing::info!(
                                "IME WinEvent hook installed (cross-process IME detection active)"
                            );
                            let mut handle = (*WINEVENT_HOOK_HANDLE)
                                .lock()
                                .unwrap_or_else(|p| p.into_inner());
                            *handle = Some(ThreadSafeWinEventHook(ime_hook));
                        }

                        // フック成功 → HOOK_ACTIVE を true に
                        HOOK_ACTIVE.store(true, Ordering::Relaxed);
                        tracing::info!("Keyboard hook installed");

                        // --- Step 3: Message loop (PeekMessageW ポーリング) ---
                        // GetMessageW (ブロッキング) ではなく PeekMessageW (ノンブロッキング)
                        // を使用する。WH_KEYBOARD_LL のコールバックはメッセージ処理中に
                        // 呼び出されるが、Tauri のマルチスレッド環境では GetMessageW が
                        // フックメッセージを正しく処理しないケースが確認されている。
                        // PeekMessageW ポーリングはスタンドアロン診断テストで実証済み。
                        loop {
                            let mut msg = MSG::default();
                            if PeekMessageW(&mut msg, None, 0, 0, PM_REMOVE).as_bool() {
                                if msg.message == WM_QUIT {
                                    break;
                                }
                                let _ = DispatchMessageW(&msg);
                            } else {
                                thread::sleep(std::time::Duration::from_millis(1));
                            }
                        }

                        // メッセージループ終了 = フック無効化
                        // スレッドを終了せず、ループ先頭に戻ってフックを再インストール
                        HOOK_ACTIVE.store(false, Ordering::Relaxed);
                        LAST_KEY_MS.store(0, Ordering::Relaxed);
                        tracing::warn!(
                            "Keyboard hook message loop exited (hook invalidated). \
                             Re-installing in 2s..."
                        );
                        thread::sleep(std::time::Duration::from_secs(2));
                        // loop continues → re-install hook
                    }
                    Err(e) => {
                        consecutive_failures += 1;
                        HOOK_ACTIVE.store(false, Ordering::Relaxed);

                        // バックオフ戦略 (macOS と同様):
                        //   1-5回: 2秒間隔
                        //   6-20回: 5秒間隔
                        //   21回以降: 10秒間隔 (CPU 節約)
                        let sleep_secs = if consecutive_failures <= 5 {
                            tracing::error!(
                                "Failed to install keyboard hook (attempt {}): {:?}",
                                consecutive_failures,
                                e
                            );
                            2
                        } else if consecutive_failures <= 20 {
                            if consecutive_failures == 6 {
                                tracing::error!(
                                    "Keyboard hook installation still failing after 5 attempts. \
                                     Continuing to retry every 5s. \
                                     Check if antivirus software is blocking keyboard hooks."
                                );
                            }
                            5
                        } else {
                            if consecutive_failures == 21 {
                                tracing::error!(
                                    "Keyboard hook installation failed 20+ times. \
                                     Slowing retries to 10s. \
                                     Try: (1) Restart the app as administrator \
                                     (2) Temporarily disable antivirus \
                                     (3) Restart your PC"
                                );
                            }
                            10
                        };

                        thread::sleep(std::time::Duration::from_secs(sleep_secs));
                    }
                }
            }
        }
    });
}

unsafe extern "system" fn hook_callback(code: i32, wparam: WPARAM, lparam: LPARAM) -> LRESULT {
    if code >= 0 {
        let event_type = wparam.0 as u32;
        let is_press = event_type == WM_KEYDOWN || event_type == WM_SYSKEYDOWN;
        let is_release = event_type == WM_KEYUP || event_type == WM_SYSKEYUP;

        if is_press || is_release {
            let vk_code = (*(lparam.0 as *const KBDLLHOOKSTRUCT)).vkCode;
            let timestamp = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap_or_default()
                .as_millis() as u64;

            LAST_KEY_MS.store(timestamp, Ordering::Relaxed);

            // IME mode tracking via VK_DBE_* keys.
            if is_press {
                match vk_code {
                    VK_DBE_ALPHANUMERIC | VK_DBE_SBCSCHAR => {
                        IME_OPEN.store(false, Ordering::Release);
                        IME_STATE_DIRTY.store(true, Ordering::Release);
                    }
                    VK_DBE_KATAKANA | VK_DBE_HIRAGANA | VK_DBE_DBCSCHAR => {
                        IME_OPEN.store(true, Ordering::Release);
                        IME_STATE_DIRTY.store(true, Ordering::Release);
                    }
                    VK_KANJI => {
                        let current = IME_OPEN.load(Ordering::Relaxed);
                        IME_OPEN.store(!current, Ordering::Release);
                        IME_STATE_DIRTY.store(true, Ordering::Release);
                    }
                    _ => {}
                }
            }

            // Surface Type Cover: VK_DBE_HIRAGANA fires ONLY as key-UP.
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

            // Send typing keys to analysis thread (filter non-typing keys).
            // CLAUDE.md 制約 (3): フックコールバック内は Atomic + channel send のみ。
            // リピート検出は分析スレッド側で HashSet を使って実行する。
            // フックコールバックからは is_repeat = false 固定で全イベントを送信。
            if is_typing_key(vk_code) {
                let is_backspace = vk_code == 0x08 || vk_code == 0x2E;
                let event = InputEvent {
                    vk_code,
                    timestamp,
                    is_press,
                    is_repeat: false, // 分析スレッドで判定 (§4.1 Atomic flags 設計準拠)
                    is_backspace,
                };
                if let Some(sender) = EVENT_SENDER.get() {
                    if let Err(e) = sender.try_send(event) {
                        tracing::warn!("InputEvent dropped (channel full): {}", e);
                    }
                }
            }

            // Wake IME polling thread.
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
    }

    CallNextHookEx(None, code, wparam, lparam)
}
