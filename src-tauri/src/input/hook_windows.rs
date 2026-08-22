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
    CallNextHookEx, DispatchMessageW, PeekMessageW, SetWindowsHookExW, UnhookWindowsHookEx,
    EVENT_OBJECT_CLOAKED, EVENT_OBJECT_IME_CHANGE, EVENT_OBJECT_IME_HIDE, EVENT_OBJECT_IME_SHOW,
    EVENT_OBJECT_UNCLOAKED, HHOOK, KBDLLHOOKSTRUCT, MSG, PM_NOREMOVE, PM_REMOVE, WH_KEYBOARD_LL,
    WM_KEYDOWN, WM_KEYUP, WM_QUIT, WM_SYSKEYDOWN, WM_SYSKEYUP,
};

use super::{
    CloakEvent, CALLBACK_COUNT, CLOAK_EVENT_TX, EVENTS_DROPPED, EVENT_SENDER, HOOK_ACTIVE,
    IME_ACTIVE, IME_CANDIDATE_NAV_COUNT, IME_COMPOSITION_START_MS, IME_OPEN, IME_SHADOW_ABANDON,
    IME_SHADOW_DWELL_MS, IME_SHADOW_READY, IME_STATE_DIRTY, LAST_KEY_MS, LEGACY_IME_EVENT_MS,
    POLL_WAKE_TX, VK_DBE_ALPHANUMERIC, VK_DBE_DBCSCHAR, VK_DBE_HIRAGANA, VK_DBE_KATAKANA,
    VK_DBE_SBCSCHAR, VK_KANJI,
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
    // ⚠️★ cloak 用の 2 本目も**必ず**外す。★ 外し忘れると再設置のたびに積み上がり、
    //   1 回の cloak で `cloak_event_callback` が複数回呼ばれる (= dwell が壊れる)。
    if let Some(h) = CLOAK_HOOK_HANDLE
        .lock()
        .unwrap_or_else(|p| p.into_inner())
        .take()
    {
        // SAFETY: 同上。
        if !unsafe { UnhookWinEvent(h.0) }.as_bool() {
            tracing::warn!("UnhookWinEvent (cloak) failed (already removed by the OS?)");
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

// ---------------------------------------------------------------------------
// IME mode decisions (pure — テストできる形に切り出す)
// ---------------------------------------------------------------------------
//
// ⚠️ VK_DBE_* / VK_KANJI の分岐そのものは `hook_callback` 内の Atomic 読み書きと
// 一体化していたため無テストだった。判定だけを純関数として切り出す
// (`hook_macos.rs` の「Permission decisions (pure)」節と同じ方針)。

/// IME モードキーの **押下** 時、`IME_OPEN` をどう遷移させるべきか。
#[derive(Debug, PartialEq, Eq)]
enum ImeOpenTransition {
    /// 明示的な値に設定する。
    Set(bool),
    /// 現在値をトグルする (VK_KANJI)。
    ///
    /// ⚠️★ `load` してから呼び出し側で `store(!current)` する形にしない。
    /// `IME_OPEN` は IME ポーリングスレッド (`ime_windows.rs`) からも書かれるため、
    /// load → store の間に他スレッドの書き込みが挟まると失われる (非アトミック RMW)。
    /// 呼び出し側は `IME_OPEN.fetch_xor(true, Ordering::AcqRel)` を使うこと
    /// (`hook_macos.rs` の VK_KANJI 処理と同じアトミック手段)。
    Toggle,
    /// このキーは IME モードに関係しない。
    None,
}

fn ime_open_after_press(vk_code: u32) -> ImeOpenTransition {
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
/// press 側と異なり VK_KANJI を含まない別の遷移表になっている。
fn ime_open_after_release(vk_code: u32) -> Option<bool> {
    match vk_code {
        VK_DBE_KATAKANA | VK_DBE_HIRAGANA | VK_DBE_DBCSCHAR => Some(true),
        VK_DBE_ALPHANUMERIC | VK_DBE_SBCSCHAR => Some(false),
        _ => None,
    }
}

/// IME 変換候補のナビゲーション/放棄キー分類 (Phase 2b shadow metrics 用)。
#[derive(Debug, PartialEq, Eq)]
enum ImeNavAction {
    /// VK_LEFT/UP/RIGHT/DOWN — 候補ナビゲーション。
    Navigate,
    /// VK_ESCAPE — 変換放棄。
    Abandon,
    /// 上記以外。
    Other,
}

fn classify_ime_nav_key(vk_code: u32) -> ImeNavAction {
    match vk_code {
        0x25 | 0x26 | 0x27 | 0x28 => ImeNavAction::Navigate,
        0x1B => ImeNavAction::Abandon,
        _ => ImeNavAction::Other,
    }
}

/// このキーが IME モードキー (VK_DBE_* / VK_KANJI) かどうか。
/// key-up でも IME ポーリングスレッドを起こす必要があるかの判定に使う
/// (Surface Type Cover の VK_DBE_HIRAGANA は key-up でしか発火しないため)。
fn is_ime_mode_key(vk_code: u32) -> bool {
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

// IME WinEvent constants: `windows` crate の生成バインディングを使う。
//
// ⚠️★★★ **2026-08-22 修正 (収集開始前)**: ここは自前 `const` で
//   `IME_CHANGE = 0x8016 / IME_SHOW = 0x8017 / IME_HIDE = 0x8018`
// と書かれており、**3 つとも別のイベントを指していた**:
//   0x8016 = EVENT_SYSTEM_ARRANGMENTPREVIEW / 0x8017 = EVENT_OBJECT_CLOAKED /
//   0x8018 = EVENT_OBJECT_UNCLOAKED
// 正しい値は 0x8027 / 0x8028 / 0x8029 (winuser.h)。
// → **背景ウィンドウの cloak (UWP のサスペンド・仮想デスクトップ切替等) で
//    `IME_ACTIVE` / `IME_OPEN` が立っていた**。詳細と影響範囲は
//    `.steering/20260821-workspace-behavior-triage/findings-instrument-defects.md`。
//
// ★ 自前 const を置かず crate から import するのは、**同じ事故を再発させないため**。
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
    /// ★ cloak/uncloak 用の 2 本目 (`cloak_event_callback` の doc を参照)。
    static ref CLOAK_HOOK_HANDLE: Mutex<Option<ThreadSafeWinEventHook>> = Mutex::new(None);
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
    // ⚠️★★★ **文書化された経路が生きている端末では cloak 経路を黙らせる** (`hook.rs` の
    //   `LEGACY_IME_EVENT_MS` doc を参照)。★ ここは「いつ届いたか」だけを刻む。
    //   ⚠️ 不可逆ラッチにしない —— 単発の混入で cloak 経路が永久に黙るのを避けるため。
    LEGACY_IME_EVENT_MS.store(
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as u64,
        Ordering::Release,
    );
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

/// ⚠️★★★ **cloak/uncloak 用の 2 本目の WinEvent コールバック。**
///
/// ## なぜ 2 本目を張るのか (★ 範囲を広げないのか)
///
/// ★ `SetWinEventHook` の `eventMin`/`eventMax` は**単一の連続区間**しか取れない。
/// `EVENT_OBJECT_CLOAKED`(0x8017) / `EVENT_OBJECT_UNCLOAKED`(0x8018) は
/// 既存の IME 範囲 `0x8027..=0x8029` と**連続していない**。
/// ⚠️ 広げて `0x8017..=0x8029` にすると、間の
/// `EVENT_OBJECT_TEXTSELECTIONCHANGED`(0x8020) など**高頻度イベントが全部届く**。
/// → ★ **2 本目なら購読するイベント ID は 2 個だけ**で済む。
///
/// ## ⚠️ Win-1 (`hook-constraints`)
///
/// ★ 判定にはウィンドウクラス名が要るが、**ここでは `GetClassNameW` を呼べない**。
/// → ★ **`try_send` で HWND を resolver スレッドへ渡すだけ**にする。
/// ⚠️ `HWND` は `Send` でないので `isize` に落として運ぶ。
unsafe extern "system" fn cloak_event_callback(
    _hook: HWINEVENTHOOK,
    event: u32,
    hwnd: HWND,
    id_object: i32,
    id_child: i32,
    _id_event_thread: u32,
    _dwms_event_time: u32,
) {
    // ⚠️ **ウィンドウ本体のイベントだけ**に絞る (`OBJID_WINDOW`=0 / `CHILDID_SELF`=0)。
    // ★ 付けないとキャレットやリストアイテムの子オブジェクトで水増しされる
    //   (`examples/ime_winevent_probe.rs` の診断 B と同じ絞り)。
    if id_object != 0 || id_child != 0 || hwnd.0.is_null() {
        return;
    }
    // ★ 文書化された経路が**現に駆動している**なら、そちらに任せて何も送らない。
    //   ⚠️ ここでは時刻比較のみ (`hook-constraints` Win-1)。★ resolver 側でも再確認する。
    let last_legacy = LEGACY_IME_EVENT_MS.load(Ordering::Acquire);
    if last_legacy != 0 {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as u64;
        if super::legacy_path_is_driving(last_legacy, now) {
            return;
        }
    }
    let cloaked = event == EVENT_OBJECT_CLOAKED;
    if let Some(tx) = CLOAK_EVENT_TX.get() {
        // ⚠️ ノンブロッキング。★ 溢れたら捨てる (フックを絶対に詰まらせない)。
        let _ = tx.try_send(CloakEvent {
            hwnd: hwnd.0 as isize,
            cloaked,
        });
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
                        // ⚠️★★★ 範囲は [eventMin, eventMax] の**単一連続区間**である。
                        // 正しい値では SHOW(0x8027) < HIDE(0x8028) < CHANGE(0x8029) なので、
                        // **SHOW を min・CHANGE を max** に置く。
                        // ⚠️ 旧コードの (IME_CHANGE, IME_HIDE) をそのまま正しい値へ差し替えると
                        //    0x8029 > 0x8028 の**空レンジ**になり、1 件も届かなくなる。
                        let ime_hook = SetWinEventHook(
                            EVENT_OBJECT_IME_SHOW,
                            EVENT_OBJECT_IME_CHANGE,
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

                        // --- Step 2b: cloak/uncloak 用の 2 本目 ---
                        // ⚠️★★★ この Windows 11 では IME 候補 UI が `ShowWindow` ではなく
                        //   **DWM の cloak/uncloak** で表示制御されており、上の 0x8027-29 は
                        //   60 秒 × 8 回の実測で **1 件も飛ばない**。
                        //   詳細は `cloak_event_callback` の doc と
                        //   `.steering/20260823-ime-active-cloak-rewiring/design.md`。
                        // ★ 範囲は 0x8017..=0x8018 の **2 個だけ**。
                        //
                        // ⚠️★★★ **`WINEVENT_SKIPOWNPROCESS` を付けない** (★ 1 本目とは違う)。
                        //   ★ 理由: IMM32 は **GUI スレッドごとに `IME` クラスの窓を作る**ので、
                        //   **GSE 自身の窓に日本語を打つと、cloak するのは GSE 自身の窓**である。
                        //   ⚠️★★★ G1 統制タスクは**被験者が GSE の入力画面に打つ**設計なので、
                        //   自プロセスを飛ばすと **G1 でだけ `ime_shadow` が構造的に 0 行**になる。
                        //   → ⚠️ それを「変換しなかった」と読む事故は `capabilities.rs` が
                        //   繰り返し警告している型そのもの。
                        //   ★ privacy 上の増分は無い —— **クラス名しか見ず**、
                        //   タイトルも PID も取らない (`cloak_event_callback` / `class_name_of`)。
                        let cloak_hook = SetWinEventHook(
                            EVENT_OBJECT_CLOAKED,
                            EVENT_OBJECT_UNCLOAKED,
                            HMODULE::default(),
                            Some(cloak_event_callback),
                            0,
                            0,
                            WINEVENT_OUTOFCONTEXT,
                        );
                        if cloak_hook.is_invalid() {
                            // ⚠️ 致命ではない (★ 文書化された経路が生きている端末もある)。
                            tracing::warn!("Failed to install cloak WinEvent hook");
                        } else {
                            tracing::info!(
                                "Cloak WinEvent hook installed (IME candidate UI detection active)"
                            );
                            let mut handle = (*CLOAK_HOOK_HANDLE)
                                .lock()
                                .unwrap_or_else(|p| p.into_inner());
                            *handle = Some(ThreadSafeWinEventHook(cloak_hook));
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
                match ime_open_after_press(vk_code) {
                    ImeOpenTransition::Set(v) => {
                        IME_OPEN.store(v, Ordering::Release);
                        IME_STATE_DIRTY.store(true, Ordering::Release);
                    }
                    ImeOpenTransition::Toggle => {
                        // ⚠️★ load→store ではなく fetch_xor でアトミックにトグルする
                        // (ImeOpenTransition::Toggle の doc 参照)。
                        IME_OPEN.fetch_xor(true, Ordering::AcqRel);
                        IME_STATE_DIRTY.store(true, Ordering::Release);
                    }
                    ImeOpenTransition::None => {}
                }
            }

            // Phase 2b: IME 変換中のナビゲーション・放棄をカウント
            // 既知の制約: WH_KEYBOARD_LL はシステムグローバルなため、IME_ACTIVE 中に
            // 別ウィンドウで押された矢印/ESC もカウントされる。
            // ⚠️★★★ **2026-08-23: 緩和の窓が 8 秒 → 20 秒に広がった** (security-checker MEDIUM)。
            //   ★ 旧文は「8s stale valve で緩和」と書いていたが、`IME_ACTIVE` を下ろすのは
            //   いま `CloakFold::MAX_SESSION_MS` (20 秒) が先で、`lib.rs` の valve は 25 秒である。
            //   → ⚠️ **他ウィンドウの混入が最大 20 秒ぶんまで載りうる。**
            //   ★ `nav` / `abandon` は ADR-011 D4 により **記録専用 (Tier 0)** で推論へは流れないため
            //   影響は記録の質に限られるが、⚠️ **解析時にこの上限を知っている必要がある。**
            // WinEvent IME_SHOW と hook_callback のタイミングずれにより、変換セッション
            // 最初の 1-2 キーが拾えない場合がある。Phase 2b は shadow-only なので許容。
            if is_press && IME_ACTIVE.load(Ordering::Relaxed) {
                match classify_ime_nav_key(vk_code) {
                    ImeNavAction::Navigate => {
                        IME_CANDIDATE_NAV_COUNT.fetch_add(1, Ordering::Relaxed);
                    }
                    ImeNavAction::Abandon => {
                        IME_SHADOW_ABANDON.store(true, Ordering::Relaxed);
                    }
                    ImeNavAction::Other => {}
                }
            }

            // Surface Type Cover: VK_DBE_HIRAGANA fires ONLY as key-UP.
            if is_release {
                if let Some(new_ime_open) = ime_open_after_release(vk_code) {
                    IME_OPEN.store(new_ime_open, Ordering::Release);
                    IME_STATE_DIRTY.store(true, Ordering::Release);
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
            if is_press || (is_release && is_ime_mode_key(vk_code)) {
                if let Some(tx) = POLL_WAKE_TX.get() {
                    let _ = tx.try_send(());
                }
            }
        }
    }

    CallNextHookEx(None, code, wparam, lparam)
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------
//
// ⚠️ WH_KEYBOARD_LL / WinEvent は実機でしか動かない。ここでテストするのは **判断だけ**である。
// ★ hook_macos.rs (4 テスト) と対称な水準で、コールバックから切り出した純関数を固定する。

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn typing_key_covers_letters_digits_and_control_keys() {
        assert!(is_typing_key(0x41), "A");
        assert!(is_typing_key(0x5A), "Z");
        assert!(is_typing_key(0x30), "0");
        assert!(is_typing_key(0x39), "9");
        assert!(is_typing_key(0x08), "Backspace");
        assert!(is_typing_key(0x0D), "Enter");
        assert!(is_typing_key(0x20), "Space");
        assert!(is_typing_key(0x09), "Tab");
        assert!(is_typing_key(0x2E), "Delete");
        assert!(is_typing_key(0x60), "Numpad 0 (範囲下端)");
        assert!(is_typing_key(0x6F), "Numpad Divide (範囲上端)");
        assert!(is_typing_key(0xBA), "OEM 記号 (範囲下端)");
        assert!(is_typing_key(0xC0), "OEM 記号 (範囲上端)");
        assert!(is_typing_key(0xDB), "OEM 記号 2群目 (範囲下端)");
        assert!(is_typing_key(0xDF), "OEM 記号 2群目 (範囲上端)");
    }

    #[test]
    fn typing_key_excludes_non_typing_keys() {
        assert!(!is_typing_key(0x25), "VK_LEFT はタイピングキーではない");
        assert!(!is_typing_key(0x1B), "VK_ESCAPE はタイピングキーではない");
        assert!(
            !is_typing_key(VK_KANJI),
            "IME モードキー自体はタイピングキーではない"
        );
    }

    /// ★ 範囲判定の off-by-one を捕まえる (境界の 1 つ外側)。
    #[test]
    fn typing_key_range_boundaries_are_exclusive_outside() {
        assert!(!is_typing_key(0x40), "A-Z 範囲の直前");
        assert!(!is_typing_key(0x5B), "A-Z 範囲の直後");
        assert!(!is_typing_key(0x2F), "0-9 範囲の直前");
        assert!(!is_typing_key(0x3A), "0-9 範囲の直後");
        assert!(!is_typing_key(0x5F), "Numpad 範囲の直前");
        assert!(!is_typing_key(0x70), "Numpad 範囲の直後 (F1 = VK_F1)");
        assert!(!is_typing_key(0xB9), "OEM 記号 1群目の直前");
        assert!(!is_typing_key(0xC1), "OEM 記号 1群目の直後");
        assert!(!is_typing_key(0xDA), "OEM 記号 2群目の直前");
        assert!(!is_typing_key(0xE0), "OEM 記号 2群目の直後");
    }

    #[test]
    fn press_of_alphanumeric_key_closes_ime() {
        // ★ Set(false) は current の値に関係なく常に false にする (Toggle との縮退を避けるため
        //   意図的に「変化なし」になるケースも確認する)。
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
    fn press_of_kana_key_opens_ime() {
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

    /// ★ VK_KANJI はモード切り替えキーなので Set ではなく Toggle を返す。
    /// `Set`/`Toggle` を型で分けたことで、「current を無視して固定値にする」テストと
    /// 「current に応じて変わる」テストが構造的に混同できなくなっている
    /// (旧 `Option<bool>` 表現では両者が同じ戻り値になる縮退ケースがあった)。
    #[test]
    fn press_of_kanji_key_returns_toggle() {
        assert_eq!(ime_open_after_press(VK_KANJI), ImeOpenTransition::Toggle);
    }

    #[test]
    fn press_of_unrelated_key_does_not_change_ime_state() {
        assert_eq!(
            ime_open_after_press(0x41),
            ImeOpenTransition::None,
            "A キーは IME モードに無関係"
        );
    }

    /// ⚠️★ Surface Type Cover は VK_DBE_HIRAGANA を key-up でしか発火しない。
    /// press 側の遷移表と非対称 (VK_KANJI が無い) であることをここで固定する。
    #[test]
    fn release_of_kana_key_opens_ime() {
        assert_eq!(ime_open_after_release(VK_DBE_HIRAGANA), Some(true));
        assert_eq!(ime_open_after_release(VK_DBE_KATAKANA), Some(true));
        assert_eq!(ime_open_after_release(VK_DBE_DBCSCHAR), Some(true));
    }

    #[test]
    fn release_of_alphanumeric_key_closes_ime() {
        assert_eq!(ime_open_after_release(VK_DBE_ALPHANUMERIC), Some(false));
        assert_eq!(ime_open_after_release(VK_DBE_SBCSCHAR), Some(false));
    }

    #[test]
    fn release_of_kanji_key_does_not_change_ime_state() {
        assert_eq!(
            ime_open_after_release(VK_KANJI),
            None,
            "★ press 側と違い release 側の遷移表に VK_KANJI は無い"
        );
    }

    #[test]
    fn nav_keys_classified_as_navigate() {
        for vk in [0x25, 0x26, 0x27, 0x28] {
            assert_eq!(classify_ime_nav_key(vk), ImeNavAction::Navigate);
        }
    }

    #[test]
    fn escape_classified_as_abandon() {
        assert_eq!(classify_ime_nav_key(0x1B), ImeNavAction::Abandon);
    }

    #[test]
    fn typing_key_classified_as_other() {
        assert_eq!(classify_ime_nav_key(0x41), ImeNavAction::Other);
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

    /// ⚠️★★★ **IME WinEvent 定数を固定する**（2026-08-22 の回帰テスト）。
    ///
    /// ★ 旧実装は自前 `const` で `0x8016 / 0x8017 / 0x8018` と書いており、
    /// **3 つとも別のイベント**（ARRANGMENTPREVIEW / CLOAKED / UNCLOAKED）を指していた。
    /// → 背景ウィンドウの cloak で `IME_ACTIVE` / `IME_OPEN` が立つ事故になった。
    /// ⚠️ **自前 const を復活させないために値を直接固定する。**
    #[test]
    fn ime_winevent_constants_are_the_real_ime_events() {
        assert_eq!(EVENT_OBJECT_IME_SHOW, 0x8027, "IME_SHOW は 0x8027");
        assert_eq!(EVENT_OBJECT_IME_HIDE, 0x8028, "IME_HIDE は 0x8028");
        assert_eq!(EVENT_OBJECT_IME_CHANGE, 0x8029, "IME_CHANGE は 0x8029");

        // ⚠️ 旧実装が誤って購読していた 3 つと衝突しないことを明示する。
        for wrong in [0x8016u32, 0x8017, 0x8018] {
            assert!(
                ![
                    EVENT_OBJECT_IME_SHOW,
                    EVENT_OBJECT_IME_HIDE,
                    EVENT_OBJECT_IME_CHANGE
                ]
                .contains(&wrong),
                "0x{wrong:04X} は IME イベントではない (cloak / arrangement preview)"
            );
        }
    }

    /// ⚠️★★ `SetWinEventHook` の範囲は **単一の連続区間**である。
    ///
    /// ★ SHOW を min、CHANGE を max に置くと 3 つとも入る。
    /// ⚠️ 旧コードの (CHANGE, HIDE) を正しい値へ差し替えると **空レンジ**になる。
    #[test]
    fn ime_winevent_range_covers_all_three() {
        let (min, max) = (EVENT_OBJECT_IME_SHOW, EVENT_OBJECT_IME_CHANGE);
        assert!(min <= max, "eventMin <= eventMax でないと 1 件も届かない");
        for e in [
            EVENT_OBJECT_IME_SHOW,
            EVENT_OBJECT_IME_HIDE,
            EVENT_OBJECT_IME_CHANGE,
        ] {
            assert!(min <= e && e <= max, "0x{e:04X} が範囲外");
        }
        // ⚠️ 旧コードの組合せをそのまま使うと空になることを固定する。
        assert!(
            EVENT_OBJECT_IME_CHANGE > EVENT_OBJECT_IME_HIDE,
            "(CHANGE, HIDE) を min/max にすると空レンジになる"
        );
    }
}
