// Windows keyboard hook via WH_KEYBOARD_LL + WinEvent for cross-process IME detection.

use std::sync::atomic::Ordering;
use std::sync::Mutex;
use std::thread;
use std::time::{SystemTime, UNIX_EPOCH};

use lazy_static::lazy_static;
use windows::Win32::Foundation::{HINSTANCE, HMODULE, HWND, LPARAM, LRESULT, WPARAM};
use windows::Win32::System::LibraryLoader::GetModuleHandleW;
use windows::Win32::UI::Accessibility::{SetWinEventHook, UnhookWinEvent, HWINEVENTHOOK};
use windows::Win32::UI::Input::KeyboardAndMouse::GetAsyncKeyState;
use windows::Win32::UI::WindowsAndMessaging::{
    CallNextHookEx, DispatchMessageW, PeekMessageW, SetWindowsHookExW, UnhookWindowsHookEx, HHOOK,
    KBDLLHOOKSTRUCT, MSG, PM_NOREMOVE, PM_REMOVE, WH_KEYBOARD_LL, WM_KEYDOWN, WM_KEYUP, WM_QUIT,
    WM_SYSKEYDOWN, WM_SYSKEYUP,
};

use super::{
    CALLBACK_COUNT, EVENT_SENDER, HOOK_ACTIVE, IME_ACTIVE, IME_CANDIDATE_NAV_COUNT,
    IME_COMPOSITION_START_MS, IME_OPEN, IME_SHADOW_ABANDON, IME_SHADOW_DWELL_MS, IME_SHADOW_READY,
    IME_STATE_DIRTY, LAST_KEY_MS, POLL_WAKE_TX, VK_DBE_ALPHANUMERIC, VK_DBE_DBCSCHAR,
    VK_DBE_HIRAGANA, VK_DBE_KATAKANA, VK_DBE_SBCSCHAR, VK_KANJI,
};
use crate::analysis::features::InputEvent;

/// 生存監視 (`input::liveness`) からの「フックを張り直せ」という要求。
///
/// ⚠️★★ **スレッド ID + `PostThreadMessageW(WM_QUIT)` は使わない。**
/// Windows のスレッド ID は**終了後に再利用される**ため、stale な ID へ投げると
/// **他プロセスのスレッド**のメッセージループを畳みうる (security-checker MEDIUM)。
/// フックスレッドは 1 ms 周期で `PeekMessageW` を回しているので、
/// フラグを見るだけで同じ再設置経路を起こせる。★ 宛先の曖昧さが原理的に消える。
static REINSTALL_REQUESTED: std::sync::atomic::AtomicBool =
    std::sync::atomic::AtomicBool::new(false);

/// フックスレッドへ「メッセージループを抜けて張り直せ」と伝える。
///
/// ⚠️★ 既存の再設置経路を**起こすだけ**で、復帰処理そのものはここに書かない
/// (`hook.rs::request_reinstall` の doc を参照)。
pub(super) fn request_reinstall() -> bool {
    if !HOOK_ACTIVE.load(Ordering::Relaxed) {
        // ⚠️ 未設置 (設置失敗のバックオフ中など) に要求しても意味が無い。
        //   ★ 要求を溜めると、次に成功したフックを入った瞬間に畳んでしまう
        //   (code-reviewer MEDIUM)。
        return false;
    }
    REINSTALL_REQUESTED.store(true, Ordering::Release);
    true
}

/// 張ってあるフックを外す。⚠️★ **張り直す前に必ず呼ぶ。**
///
/// 既に OS 側で外れていれば `Err` が返るだけなので、真の silent death 経路でも無害である。
fn unhook_all() {
    if let Some(h) = HOOK_HANDLE.lock().unwrap_or_else(|p| p.into_inner()).take() {
        // SAFETY: `h.0` は本スレッドが `SetWindowsHookExW` で得たハンドルで、
        // 外すのも同じスレッドである (Win32 の要件)。二重解放は `take()` が防ぐ。
        if let Err(e) = unsafe { UnhookWindowsHookEx(h.0) } {
            tracing::warn!("UnhookWindowsHookEx failed (already removed by the OS?): {e:?}");
        }
    }
    if let Some(h) = WINEVENT_HOOK_HANDLE
        .lock()
        .unwrap_or_else(|p| p.into_inner())
        .take()
    {
        // SAFETY: 同上 (`SetWinEventHook` の戻り値を同じスレッドで解放する)。
        if !unsafe { UnhookWinEvent(h.0) }.as_bool() {
            tracing::warn!("UnhookWinEvent failed (already removed by the OS?)");
        }
    }
}

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
            // Phase 2b: IME 変換セッション開始時刻を記録
            // IME_SHOW で初期化。IME_CHANGE は通常 IME_SHOW の後に飛ぶが、
            // IME によっては IME_SHOW なしに IME_CHANGE のみ発火する場合がある。
            // その際は defensive fallback として START_MS=0 なら現在時刻を store。
            if event == EVENT_OBJECT_IME_SHOW {
                let now = SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_millis() as u64;
                IME_COMPOSITION_START_MS.store(now, Ordering::Relaxed);
                // 前回セッションのカウンターをリセット
                IME_CANDIDATE_NAV_COUNT.store(0, Ordering::Relaxed);
                IME_SHADOW_ABANDON.store(false, Ordering::Relaxed);
            } else if IME_COMPOSITION_START_MS.load(Ordering::Relaxed) == 0 {
                let now = SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_millis() as u64;
                IME_COMPOSITION_START_MS.store(now, Ordering::Relaxed);
                IME_CANDIDATE_NAV_COUNT.store(0, Ordering::Relaxed);
                IME_SHADOW_ABANDON.store(false, Ordering::Relaxed);
            }
            if let Some(tx) = POLL_WAKE_TX.get() {
                let _ = tx.try_send(());
            }
        }
        EVENT_OBJECT_IME_HIDE => {
            // Phase 2b: dwell 計算 → shadow ready シグナル
            let start = IME_COMPOSITION_START_MS.load(Ordering::Relaxed);
            if start > 0 {
                let now = SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap_or_default()
                    .as_millis() as u64;
                IME_SHADOW_DWELL_MS.store(now.saturating_sub(start), Ordering::Relaxed);
                IME_COMPOSITION_START_MS.store(0, Ordering::Relaxed);
                IME_SHADOW_READY.store(true, Ordering::Release);
            }
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
        // ★ 「今回の脱出が生存監視の要求によるものか」をログの文言に反映するための印。
        //   ⚠️ 要求フラグ自体のクリアは**インストール成功の直後**に行う (下記)。
        let mut requested_reinstall = false;

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
                    tracing::warn!("GetModuleHandleW failed ({:?}), falling back to NULL", e);
                    HINSTANCE::default()
                }
            }
        };

        loop {
            unsafe {
                // --- Step 1: Install low-level keyboard hook ---
                let hook_id = SetWindowsHookExW(WH_KEYBOARD_LL, Some(hook_callback), hinstance, 0);

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
                        // ⚠️★ **張り直した直後に要求を捨てる** (cross-review)。
                        //   自然失効 (WM_QUIT) で先にループを抜けた場合、監視スレッドが立てた
                        //   要求が消費されずに残り、★ 次のインストール直後に即座に消費されて
                        //   **もう 1 往復の unhook → 2 秒 sleep → 再設置**が走る。
                        //   ★ 今張ったばかりのフックに対する要求ではないので、捨ててよい。
                        REINSTALL_REQUESTED.store(false, Ordering::Release);
                        tracing::info!("Keyboard hook installed");

                        // --- Step 3: Message loop (PeekMessageW ポーリング) ---
                        // GetMessageW (ブロッキング) ではなく PeekMessageW (ノンブロッキング)
                        // を使用する。WH_KEYBOARD_LL のコールバックはメッセージ処理中に
                        // 呼び出されるが、Tauri のマルチスレッド環境では GetMessageW が
                        // フックメッセージを正しく処理しないケースが確認されている。
                        // PeekMessageW ポーリングはスタンドアロン診断テストで実証済み。
                        loop {
                            // ★ 生存監視 (`input::liveness`) からの再設置要求。
                            //   ⚠️ ★ `PostThreadMessageW(WM_QUIT)` を使わない理由:
                            //   スレッド ID は**終了後に再利用される**ので、stale な ID へ投げると
                            //   **他プロセスのスレッド**のメッセージループを畳みうる
                            //   (security-checker MEDIUM)。フラグならその危険が原理的に無い。
                            if REINSTALL_REQUESTED.swap(false, Ordering::AcqRel) {
                                requested_reinstall = true;
                                break;
                            }
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

                        // ⚠️★★ **必ず先に外してから張り直す** (code-reviewer / security-checker とも HIGH)。
                        //   従来この経路は「OS が既にフックを外した後」しか走らなかったので
                        //   Unhook 無しでも露見しなかった。★ 2026-08-09 に足した生存監視は
                        //   **フックが生きている状態でも**再設置を起こす (マウスのみの作業は
                        //   誤検知しうる = `liveness.rs` のテストで仕様として固定済み) ため、
                        //   外さないと WH_KEYBOARD_LL が二重に積まれる。
                        //   → 1 打鍵で `hook_callback` が 2 回呼ばれ、**同一時刻の key 行が重複**して
                        //   IKI≈0 が量産され特徴量が壊れる (研究計器としての致命傷)。
                        //   ★ 既に OS が外していれば Err が返るだけで無害なので、
                        //     真の silent death 側の挙動は変わらない。
                        unhook_all();

                        // ⚠️★ `LAST_KEY_MS` は **0 に戻さない**。
                        //   0 は `probe_scheduler` の `driver_idle_ms` から「離席」に見え、
                        //   次の打鍵までプローブが抑止される (Phase1 で GATE2 を落とした形と同型)。
                        //   ★ macOS 側は既にリセットしない方針に統一済み。
                        //   ★ 誤検知由来の再設置が 60 秒おきに走ると、この差でラベル収量が静かに削れる。
                        if requested_reinstall {
                            tracing::warn!(
                                "Keyboard hook reinstall requested by the liveness monitor \
                                 (events stopped arriving). Re-installing in 2s..."
                            );
                            requested_reinstall = false;
                        } else {
                            tracing::warn!(
                                "Keyboard hook message loop exited (hook invalidated). \
                                 Re-installing in 2s..."
                            );
                        }
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
    // ★ 生存監視 (`input::liveness`) 用のカウンタ。⚠️ **OS がこのコールバックを呼んだこと**
    //   そのものを数えるので、`code < 0` やタイピング以外のキーでも加算する。
    //   ★ Atomic 1 回だけ = `hook-constraints` Win-1 (Atomic / try_send のみ) に適合。
    CALLBACK_COUNT.fetch_add(1, Ordering::Relaxed);

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

            // Phase 2b: IME 変換中のナビゲーション・放棄をカウント
            // 既知の制約: WH_KEYBOARD_LL はシステムグローバルなため、IME_ACTIVE 中に
            // 別ウィンドウで押された矢印/ESC もカウントされる。8s stale valve で緩和。
            // WinEvent IME_SHOW と hook_callback のタイミングずれにより、変換セッション
            // 最初の 1-2 キーが拾えない場合がある。Phase 2b は shadow-only なので許容。
            if is_press && IME_ACTIVE.load(Ordering::Relaxed) {
                match vk_code {
                    0x25 | 0x26 | 0x27 | 0x28 => {
                        // VK_LEFT/UP/RIGHT/DOWN — 候補ナビゲーション
                        IME_CANDIDATE_NAV_COUNT.fetch_add(1, Ordering::Relaxed);
                    }
                    0x1B => {
                        // VK_ESCAPE — 変換放棄
                        IME_SHADOW_ABANDON.store(true, Ordering::Relaxed);
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
                // ペースト検出: V(0x56) 押下時に Ctrl が「今まさに」押されていれば Ctrl+V とみなす。
                // 判定の瞬間に GetAsyncKeyState(VK_CONTROL) で実状態を読むことで、左右 Ctrl の
                // 区別や WH_KEYBOARD_LL のフォーカス越境による up 取りこぼし (Atomic 固着) を回避し、
                // macOS の per-event CGEvent flags 読みと検出セマンティクスを揃える。
                // GetAsyncKeyState は alloc/lock/blocking を伴わない軽量カーネル読み取りのため
                // hook-constraints (コールバック内は非ブロッキングのみ) に抵触しない。
                // クリップボードの中身には一切触れず、VK + 修飾キー状態のみで判定する。
                let is_paste = is_press && vk_code == 0x56 && {
                    // SAFETY: GetAsyncKeyState は任意の仮想キーコードに対し安全に呼べる純粋な
                    // 状態読み取り。0x11 = VK_CONTROL。最上位ビット (0x8000) が押下中を示す。
                    let ctrl = unsafe { GetAsyncKeyState(0x11) };
                    (ctrl as u16 & 0x8000) != 0
                };
                let event = InputEvent {
                    vk_code,
                    timestamp,
                    is_press,
                    is_repeat: false, // 分析スレッドで判定 (§4.1 Atomic flags 設計準拠)
                    is_backspace,
                    is_paste,
                };
                if let Some(sender) = EVENT_SENDER.get() {
                    if sender.try_send(event).is_err() {
                        // ⚠️★ ここでログを書かない (`hook-constraints` 共通-1: コールバック内は
                        //   Atomic と try_send のみ。ログはアロケーションとバッファ操作を伴う)。
                        //   ★ カウンタだけ上げ、監視スレッドが統計的に 1 回だけ報告する (共通-3)。
                        EVENTS_DROPPED.fetch_add(1, Ordering::Relaxed);
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
