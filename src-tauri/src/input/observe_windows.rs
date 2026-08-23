// O1 (R3-a) の非打鍵チャネル — Windows 実装。
//
// ★ 2 つを 1 本の専用スレッドで受ける:
//   - **L-c フォーカス遷移**: `SetWinEventHook(EVENT_SYSTEM_FOREGROUND)`（★ **3 本目**のフック）
//   - **L-b ポインタ**: **Raw Input**（`RIDEV_INPUTSINK`・**マウスのみ**）
//
// ⚠️★★★ **キーボードフックのスレッドに相乗りさせない。**
//   ★ `WH_KEYBOARD_LL` は `LowLevelHooksTimeout` を持ち、
//   **スレッドが詰まると OS が無通知でフックを外す**。
//   → ⚠️ フォアグラウンド遷移とマウスの奔流を同じスレッドに載せると、
//   **打鍵の観測ごと落ちる**（★ O1 のためにコアの計器を壊すことになる）。

use std::sync::atomic::Ordering;
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use windows::core::PCWSTR;
use windows::Win32::Foundation::{HINSTANCE, HWND, LPARAM, LRESULT, WPARAM};
use windows::Win32::System::LibraryLoader::GetModuleHandleW;
use windows::Win32::UI::Accessibility::{SetWinEventHook, UnhookWinEvent, HWINEVENTHOOK};
use windows::Win32::UI::Input::KeyboardAndMouse::GetKeyboardLayoutNameW;
use windows::Win32::UI::Input::{
    GetRawInputBuffer, RegisterRawInputDevices, RAWINPUT, RAWINPUTDEVICE, RAWINPUTHEADER,
    RIDEV_INPUTSINK, RIM_TYPEMOUSE,
};
use windows::Win32::UI::WindowsAndMessaging::{
    CreateWindowExW, DefWindowProcW, DestroyWindow, DispatchMessageW, PeekMessageW, RegisterClassW,
    TranslateMessage, HWND_MESSAGE, MSG, PM_REMOVE, WINDOW_EX_STYLE, WINDOW_STYLE, WNDCLASSW,
};

use crate::analysis::pointer_bin::{PointerAccum, PointerBin};

use super::{FOCUS_TX, OBSERVATIONS_DROPPED, POINTER_TX};

/// ★ Windows では両方とも実装がある（ADR-013 D1 の自己刻印に使う）。
pub const FOCUS_AVAILABLE: bool = true;
pub const POINTER_AVAILABLE: bool = true;

/// `EVENT_SYSTEM_FOREGROUND`。
///
/// ⚠️★★★ **既存の WinEvent フックの範囲を広げてはならない。**
/// ★ `SetWinEventHook` の `eventMin`/`eventMax` は**単一の連続区間**しか取れず、
/// 既存の 2 本は IME 用 `0x8027..=0x8029` と cloak 用 `0x8017..=0x8018` である。
/// `0x0003` はそこから遠く離れているので、⚠️ 広げると**間の全イベントが届く**。
/// → ★ **3 本目を単独で張る**（購読するイベント ID は 1 個だけ）。
const EVENT_SYSTEM_FOREGROUND: u32 = 0x0003;

/// `WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS`。
///
/// ⚠️★★★ **`WINEVENT_OUTOFCONTEXT` が本質である** —— ★ **DLL 注入をしない**ので
/// UIPI の禁止リスト第 5 項（DLL injection）に触れず、
/// ★ **コールバック引数に文字列が 1 つも無い**ため content-free が構造的に保証される。
const WINEVENT_OUTOFCONTEXT: u32 = 0x0000;
const WINEVENT_SKIPOWNPROCESS: u32 = 0x0002;

/// マウスの HID usage（`usUsagePage=0x01` / `usUsage=0x02`）。
const HID_USAGE_PAGE_GENERIC: u16 = 0x01;
const HID_USAGE_GENERIC_MOUSE: u16 = 0x02;

/// `RAWMOUSE.usButtonFlags` のうち **押下** を表すビット。
///
/// ⚠️ **離上は数えない**（★ 1 クリックを 2 回に数えないため）。
/// ⚠️ **どのボタンかは残さない** —— ★ 押下の「回数」だけを足す。
const RI_MOUSE_BUTTON_DOWN_MASK: u16 = 0x0001 // 左
    | 0x0004 // 右
    | 0x0010 // 中
    | 0x0040 // X1
    | 0x0100; // X2
/// ホイール（縦 / 横）。⚠️ **向きは捨てる**。
const RI_MOUSE_WHEEL: u16 = 0x0400;
const RI_MOUSE_HWHEEL: u16 = 0x0800;

/// `RAWMOUSE.usFlags` の `MOUSE_MOVE_ABSOLUTE`。
///
/// ## ⚠️★★★ ADR-014 D4 の「構造的に安全」には**例外がある**（★ 2026-08-23 に自己レビューで発見）
///
/// ★ D4 は Raw Input を選んだ理由を逐語「**`RAWMOUSE` に絶対座標フィールドがそもそも
/// 存在しない**（構造的に安全）」と書いている。⚠️ **これは相対モードの device に限って正しい。**
///
/// ★ `usFlags` に `MOUSE_MOVE_ABSOLUTE`(0x01) が立つ device（RDP セッション / 一部の VM /
/// 一部のタブレット）では、**`lLastX`/`lLastY` は相対移動量ではなく正規化された絶対座標**である。
/// → ⚠️★★★ そのまま `|x|+|y|` を足すと **(a) 位置由来の値になり (b) 常に最大バケットへ張り付く**。
///
/// ★ **決定**: 絶対モードの record は **移動量として数えない**（⚠️ ボタン / ホイールは数える）。
/// - ⚠️ **前回位置との差を取る形にはしない** —— ★ それは「座標を持たない」という
///   段 1 の性質を*方針*に格下げする（D4 は**構造**で守ることを選んでいる）。
/// - ⚠️ **代償**: 絶対モードの端末では `moved` が常に 0 になる（★ ボタン / ホイールでしか
///   活動が見えない）。→ ★ **研究者へ返す**（`decisions.md` D-M）。
const MOUSE_MOVE_ABSOLUTE: u16 = 0x0001;

/// ビンの長さ。★ ADR-014 D4 の L-b 仕様（**1 秒固定ビン**）。
const BIN_MS: u64 = 1000;

/// 1 回の `GetRawInputBuffer` で受け取るバッファのバイト数。
///
/// ★ 高ポーリングレートのマウス（1000 Hz）でも 1 回の呼び出しで捌けるだけ取る。
/// ⚠️ 足りなければ次のループで続きを取るだけなので、取りこぼしにはならない。
const RAW_BUFFER_BYTES: usize = 16 * 1024;

fn now_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64
}

/// ★★★ フォアグラウンド遷移のコールバック。
///
/// ## ⚠️★★★ ここで **HWND を外へ出さない**
///
/// ★ 引数の `hwnd` は**読みさえしない**（`_hwnd` で捨てる）。
/// ⚠️ ウィンドウ通し番号や distinct 数も**擬似識別子**になるので数えない（ADR-012 D4 L-c）。
/// → ★ 送るのは **`u64` の時刻 1 個だけ**である。
///
/// ## ⚠️ `hook-constraints`
///
/// ★ Atomic と `try_send` のみ。⚠️ ログを書かない・ロックを取らない。
unsafe extern "system" fn foreground_event_callback(
    _hook: HWINEVENTHOOK,
    event: u32,
    _hwnd: HWND,
    id_object: i32,
    id_child: i32,
    _id_event_thread: u32,
    _dwms_event_time: u32,
) {
    // ⚠️ ウィンドウ本体のイベントだけに絞る (`OBJID_WINDOW`=0 / `CHILDID_SELF`=0)。
    //   ★ 付けないと子オブジェクトで水増しされる (`hook_windows.rs` の cloak 経路と同じ絞り)。
    if event != EVENT_SYSTEM_FOREGROUND || id_object != 0 || id_child != 0 {
        return;
    }
    if let Some(tx) = FOCUS_TX.get() {
        if tx.try_send(now_ms()).is_err() {
            // ⚠️★ コールバック内でログを書かない (`hook-constraints` 共通-1)。
            OBSERVATIONS_DROPPED.fetch_add(1, Ordering::Relaxed);
        }
    }
}

/// メッセージ専用ウィンドウの WndProc。
///
/// ⚠️ `WM_INPUT` はここでは処理しない —— ★ 実際の読み出しは
/// [`drain_raw_input`] が `GetRawInputBuffer` でまとめて行う（★ 1 件ずつ
/// `GetRawInputData` を呼ぶより OS 側のオーバーヘッドが小さい）。
unsafe extern "system" fn wnd_proc(
    hwnd: HWND,
    msg: u32,
    wparam: WPARAM,
    lparam: LPARAM,
) -> LRESULT {
    // SAFETY: `DefWindowProcW` は任意のメッセージに対して安全に呼べる既定処理である。
    DefWindowProcW(hwnd, msg, wparam, lparam)
}

/// メッセージ専用ウィンドウを作る。
///
/// ★ `RIDEV_INPUTSINK` は `hwndTarget` が必須なので、⚠️ **表示されない窓が 1 つ要る**。
/// `HWND_MESSAGE` の子にすると、タスクバーにも Alt+Tab にも現れない。
fn create_message_window() -> Option<HWND> {
    // ⚠️ クラス名は静的な UTF-16 文字列にする (★ 一時変数のポインタを渡さない)。
    let class_name: Vec<u16> = "GseO1RawInputSink\0".encode_utf16().collect();
    // SAFETY: `GetModuleHandleW(None)` は自プロセスのモジュールハンドルを返す。失敗時は Err。
    let hinstance = match unsafe { GetModuleHandleW(None) } {
        Ok(h) => h,
        Err(e) => {
            tracing::warn!("O1: GetModuleHandleW failed: {e:?}");
            return None;
        }
    };
    let wc = WNDCLASSW {
        lpfnWndProc: Some(wnd_proc),
        hInstance: hinstance.into(),
        lpszClassName: PCWSTR(class_name.as_ptr()),
        ..Default::default()
    };
    // SAFETY: `wc` のポインタは呼び出しの間だけ有効であればよく、`class_name` は
    // 本関数のスコープで生存している。クラスの二重登録は 0 を返すだけで無害
    // (★ 既に登録済みなら続けて `CreateWindowExW` してよい)。
    let _atom = unsafe { RegisterClassW(&wc) };
    // SAFETY: `HWND_MESSAGE` を親に渡すとメッセージ専用ウィンドウになる (Win32 の規定)。
    //   ★ 生成に失敗すると `Err` / 無効ハンドルが返るので下で判定する。
    let hwnd = unsafe {
        CreateWindowExW(
            WINDOW_EX_STYLE(0),
            PCWSTR(class_name.as_ptr()),
            PCWSTR(class_name.as_ptr()),
            WINDOW_STYLE(0),
            0,
            0,
            0,
            0,
            HWND_MESSAGE,
            None,
            HINSTANCE(hinstance.0),
            None,
        )
    };
    match hwnd {
        Ok(h) if !h.0.is_null() => Some(h),
        Ok(_) => None,
        Err(e) => {
            tracing::warn!("O1: CreateWindowExW (message-only) failed: {e:?}");
            None
        }
    }
}

/// Raw Input（**マウスのみ**）を登録する。
///
/// ## ⚠️★★★ `WH_MOUSE_LL` を使わない理由（★ ADR-014 D4 の逐語）
///
/// 「⚠️ **`WH_MOUSE_LL` は採らない**（システム全体のマウス入力を直列化・
/// `LowLevelHooksTimeout` で**通知なく外される**）」。
///
/// ★ Raw Input は **`RAWMOUSE` に絶対座標フィールドがそもそも存在しない**ので、
/// 「座標を持たない」が**構造的に**保証される（＝ 方針ではなく型で守られる）。
fn register_raw_mouse(hwnd: HWND) -> bool {
    let rid = RAWINPUTDEVICE {
        usUsagePage: HID_USAGE_PAGE_GENERIC,
        usUsage: HID_USAGE_GENERIC_MOUSE,
        // ⚠️ **キーボードは登録しない。** ★ 打鍵は既存の `WH_KEYBOARD_LL` が見ており、
        //   二重に取る必要が無い (`data-privacy`: 取らなくてよいものは取らない)。
        dwFlags: RIDEV_INPUTSINK,
        hwndTarget: hwnd,
    };
    // SAFETY: `rid` は本関数のスコープで生存する有効な構造体で、`cbSize` も対の型から取る。
    let ok = unsafe {
        RegisterRawInputDevices(&[rid], std::mem::size_of::<RAWINPUTDEVICE>() as u32).is_ok()
    };
    if !ok {
        tracing::warn!("O1: RegisterRawInputDevices (mouse, INPUTSINK) failed");
    }
    ok
}

/// 溜まっている Raw Input をまとめて読み、[`PointerAccum`] へ足す。
///
/// ## ⚠️★★★ ここで捨てているもの
///
/// - **`RAWINPUTHEADER.hDevice`** …… ★ ハードウェア識別子（ADR-014 D4 の禁止表）
/// - **`ulExtraInformation`** …… ★ 任意アプリが書ける自由フィールド（同上）
/// - **`lLastX` / `lLastY` の符号** …… ★ 足す前に絶対値へ落とす（`PointerAccum::add_move`）
/// - **どのボタンか** …… ★ 押下の**回数**だけ
/// - **ホイールの向き** …… ★ 刻みの**回数**だけ
fn drain_raw_input(buf: &mut [u8], accum: &mut PointerAccum) {
    loop {
        let mut size = buf.len() as u32;
        // SAFETY: `buf` は呼び出し側が確保した可変バッファで、`size` にその容量を渡す。
        //   `GetRawInputBuffer` は書き込んだバイト数ぶんだけ `RAWINPUT` を並べる。
        //   戻り値が 0 なら「もう無い」、`u32::MAX` (=-1) ならエラーである。
        let count = unsafe {
            GetRawInputBuffer(
                Some(buf.as_mut_ptr() as *mut RAWINPUT),
                &mut size,
                std::mem::size_of::<RAWINPUTHEADER>() as u32,
            )
        };
        if count == 0 || count == u32::MAX {
            return;
        }

        // SAFETY: `buf` の先頭から `count` 件の `RAWINPUT` が並んでいることを
        //   `GetRawInputBuffer` が保証する。
        unsafe { accumulate_from_buffer(buf.as_ptr() as *const RAWINPUT, count, accum) };
    }
}

/// `RAWINPUT` の並びを歩いて [`PointerAccum`] へ足す。
///
/// ## ⚠️★★★ なぜ別関数に切り出したのか
///
/// ★ **`NEXTRAWINPUTBLOCK` の桁合わせ（8 バイト境界への切り上げ）を間違えると
/// 領域外を読む**。⚠️ 実機のマウス操作でしか踏めない形にしておくと、
/// **検証できない `unsafe`** が残る。
/// → ★ ここを取り出したので、[`tests::accumulate_walks_the_buffer_with_qword_alignment`] が
/// **手で組んだバッファ**で歩き方を固定できる。
///
/// # Safety
///
/// `ptr` から始まる領域に、`count` 件の妥当な `RAWINPUT`（各要素の長さは
/// `header.dwSize`・要素間は 8 バイト境界へ切り上げ）が並んでいること。
unsafe fn accumulate_from_buffer(ptr: *const RAWINPUT, count: u32, accum: &mut PointerAccum) {
    let mut ptr = ptr;
    for _ in 0..count {
        // SAFETY: 呼び出し側の契約により `ptr` は妥当な `RAWINPUT` を指す。
        let ri = &*ptr;
        if ri.header.dwType == RIM_TYPEMOUSE.0 {
            // SAFETY: `dwType == RIM_TYPEMOUSE` のとき union の `mouse` が有効である。
            let mouse = &ri.data.mouse;
            // ⚠️★★★ **絶対モードの record は移動量として数えない**
            //   (`MOUSE_MOVE_ABSOLUTE` の doc を参照 —— ★ `lLastX`/`lLastY` が
            //   相対移動量ではなく**正規化された絶対座標**になるため)。
            if mouse.usFlags.0 & MOUSE_MOVE_ABSOLUTE == 0 {
                // ⚠️ **符号は `add_move` の中で落ちる**(★ ここで方向を持たない)。
                accum.add_move(mouse.lLastX, mouse.lLastY);
            }
            // SAFETY: `RAWMOUSE.Anonymous` は union だが、`usButtonFlags` を読む形は
            //   Win32 が公開している通常の読み方である。
            let flags = mouse.Anonymous.Anonymous.usButtonFlags;
            if flags & RI_MOUSE_BUTTON_DOWN_MASK != 0 {
                accum.add_button_press();
            }
            if flags & (RI_MOUSE_WHEEL | RI_MOUSE_HWHEEL) != 0 {
                // ★ 向きは見ない (⚠️ `usButtonData` は符号付きだが読まない)。
                accum.add_wheel(1);
            }
        }
        // ★ Win32 の `NEXTRAWINPUTBLOCK` と同じ規則 (QWORD 境界へ切り上げ)。
        let step = ((ri.header.dwSize as usize) + 7) & !7usize;
        // SAFETY: `step` は当該要素の長さを 8 バイト境界へ丸めた値で、
        //   `count` 件目までは領域内に留まる (呼び出し側の契約)。
        ptr = (ptr as *const u8).add(step) as *const RAWINPUT;
    }
}

/// O1 観測スレッドを起こす。
pub fn start() {
    thread::spawn(|| {
        // ── ★ 3 本目の WinEvent フック（フォーカス遷移） ─────────────────
        // SAFETY: `SetWinEventHook` は本スレッドにフックを設置する。コールバックは
        //   `extern "system"` で ABI が一致しており、`WINEVENT_OUTOFCONTEXT` なので
        //   DLL 注入を伴わない。解放は本スレッド終了時の `UnhookWinEvent`。
        let focus_hook = unsafe {
            SetWinEventHook(
                EVENT_SYSTEM_FOREGROUND,
                EVENT_SYSTEM_FOREGROUND,
                None,
                Some(foreground_event_callback),
                0,
                0,
                WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS,
            )
        };
        if focus_hook.0.is_null() {
            tracing::warn!("O1: SetWinEventHook(EVENT_SYSTEM_FOREGROUND) failed");
        } else {
            tracing::info!("O1: foreground transition hook installed");
        }

        // ── ★ Raw Input（ポインタ） ──────────────────────────────────
        let hwnd = create_message_window();
        let raw_ok = match hwnd {
            Some(h) => register_raw_mouse(h),
            None => false,
        };
        if raw_ok {
            tracing::info!("O1: raw mouse input registered (INPUTSINK)");
        }

        let mut buf = vec![0u8; RAW_BUFFER_BYTES];
        let mut accum = PointerAccum::default();
        let mut bin_started = Instant::now();

        loop {
            // ★ メッセージを回す (WinEvent のコールバックはここで駆動される)。
            let mut msg = MSG::default();
            // SAFETY: `PeekMessageW` は本スレッドのキューを読むだけで、`msg` は有効。
            while unsafe { PeekMessageW(&mut msg, None, 0, 0, PM_REMOVE) }.as_bool() {
                // SAFETY: `msg` は直前に `PeekMessageW` が埋めた有効な構造体である。
                unsafe {
                    let _ = TranslateMessage(&msg);
                    DispatchMessageW(&msg);
                }
            }

            if raw_ok {
                drain_raw_input(&mut buf, &mut accum);
            }

            // ── ★ 1 秒ビンを閉じる ───────────────────────────────────
            if bin_started.elapsed() >= Duration::from_millis(BIN_MS) {
                let bin: PointerBin = accum.close(now_ms());
                accum = PointerAccum::default();
                bin_started = Instant::now();
                // ⚠️★★★ **ゼロ抑制** (ADR-014 D5): 何も起きていない秒は行にしない。
                if !bin.is_empty() {
                    if let Some(tx) = POINTER_TX.get() {
                        if tx.try_send(bin).is_err() {
                            OBSERVATIONS_DROPPED.fetch_add(1, Ordering::Relaxed);
                        }
                    }
                }
            }

            thread::sleep(Duration::from_millis(5));
        }

        // ⚠️ ループは無限なのでここへは到達しない。★ 到達する形に変えるなら
        //   `UnhookWinEvent(focus_hook)` と `DestroyWindow(hwnd)` を必ず呼ぶこと。
        #[allow(unreachable_code)]
        {
            // SAFETY: 設置したのと同じスレッドで解放する (Win32 の要件)。
            unsafe {
                let _ = UnhookWinEvent(focus_hook);
                if let Some(h) = hwnd {
                    let _ = DestroyWindow(h);
                }
            }
        }
    });
}

/// キーボードレイアウトの識別子（例 `00000411` = 日本語）。
///
/// ⚠️★★★ **`ToUnicodeEx` を呼ばない。** ★ 呼んだ瞬間に**入力文字そのものが
/// プロセス内に出現する**（`data-privacy` ルール 1 の一線）。
/// ★ `GetKeyboardLayoutNameW` が返すのは **配列の識別子だけ**である。
pub fn keyboard_layout_id() -> Option<String> {
    // ★ Win32 の規定で `KL_NAMELENGTH` = 9 (終端含む)。
    let mut buf = [0u16; 9];
    // SAFETY: `buf` は Win32 が要求する長さ (KL_NAMELENGTH) の可変バッファである。
    let ok = unsafe { GetKeyboardLayoutNameW(&mut buf) }.is_ok();
    if !ok {
        return None;
    }
    let len = buf.iter().position(|&c| c == 0).unwrap_or(buf.len());
    let s = String::from_utf16_lossy(&buf[..len]);
    if s.is_empty() {
        None
    } else {
        Some(s)
    }
}

/// ⚠️ Windows に `EnableSecureEventInput` に相当するものは無い。
///
/// ★ **`None` は「計器が無い」であって「secure ではない」ではない**（ADR-013 D1）。
pub fn secure_input_enabled() -> Option<bool> {
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    /// ⚠️★★★ **押下マスクに離上が 1 ビットも入っていない**こと。
    ///
    /// ★ 入れると 1 クリックが 2 回に数えられ、⚠️ ボタン回数が systematically 2 倍になる。
    #[test]
    fn button_mask_contains_only_down_transitions() {
        // Win32 の定義: DOWN は奇数ビット、UP はその 1 つ上のビットである。
        for up_bit in [
            0x0002u16, // 左 UP
            0x0008,    // 右 UP
            0x0020,    // 中 UP
            0x0080,    // X1 UP
            0x0200,    // X2 UP
        ] {
            assert_eq!(
                RI_MOUSE_BUTTON_DOWN_MASK & up_bit,
                0,
                "離上ビット {up_bit:#06X} がマスクに入っている"
            );
        }
        for down_bit in [0x0001u16, 0x0004, 0x0010, 0x0040, 0x0100] {
            assert_ne!(
                RI_MOUSE_BUTTON_DOWN_MASK & down_bit,
                0,
                "押下ビット {down_bit:#06X} がマスクから漏れている"
            );
        }
    }

    /// ⚠️ ホイールのマスクがボタン押下と重なっていないこと。
    #[test]
    fn wheel_bits_do_not_overlap_button_bits() {
        assert_eq!(
            RI_MOUSE_BUTTON_DOWN_MASK & (RI_MOUSE_WHEEL | RI_MOUSE_HWHEEL),
            0
        );
    }

    /// ⚠️★★★ **既存の WinEvent 2 本と範囲が重ならない**こと。
    ///
    /// ★ 重なっていたら「3 本目を張る」判断そのものが崩れる（★ 範囲を広げれば済む話になる）。
    #[test]
    fn foreground_event_is_far_from_the_existing_winevent_ranges() {
        // IME 用 0x8027..=0x8029 ／ cloak 用 0x8017..=0x8018 (`hook_windows.rs`)。
        assert!(
            EVENT_SYSTEM_FOREGROUND < 0x8017,
            "既存の範囲と連続していない"
        );
        assert_eq!(EVENT_SYSTEM_FOREGROUND, 0x0003);
    }

    /// ★ ビンの長さは 1 秒である (ADR-014 D4 の L-b 仕様)。
    #[test]
    fn pointer_bin_is_one_second() {
        assert_eq!(BIN_MS, 1000);
    }

    /// ⚠️★ テスト用に 1 件の `RAWINPUT`(マウス) を組む。
    fn mouse_record(dx: i32, dy: i32, button_flags: u16) -> RAWINPUT {
        let mut ri: RAWINPUT = unsafe { std::mem::zeroed() };
        ri.header.dwType = RIM_TYPEMOUSE.0;
        ri.header.dwSize = std::mem::size_of::<RAWINPUT>() as u32;
        // SAFETY: `dwType` を `RIM_TYPEMOUSE` にしたので `mouse` を書いてよい。
        unsafe {
            ri.data.mouse.lLastX = dx;
            ri.data.mouse.lLastY = dy;
            ri.data.mouse.Anonymous.Anonymous.usButtonFlags = button_flags;
        }
        ri
    }

    /// ⚠️★★★ **`NEXTRAWINPUTBLOCK` の桁合わせが正しいこと**（★ 領域外読みの防波堤）。
    ///
    /// ★ 手で組んだバッファを歩かせて、**2 件目以降を正しい位置から読む**ことを固定する。
    /// ⚠️ ここが 1 バイトずれると、実機でしか踏めない未定義動作になる。
    #[test]
    fn accumulate_walks_the_buffer_with_qword_alignment() {
        let size = std::mem::size_of::<RAWINPUT>();
        let step = (size + 7) & !7usize;
        let mut buf = vec![0u8; step * 3];
        let records = [
            mouse_record(10, 0, 0),
            mouse_record(-4, 3, 0x0001), // ★ 左ボタン押下
            mouse_record(0, 0, RI_MOUSE_WHEEL),
        ];
        for (i, r) in records.iter().enumerate() {
            // SAFETY: `buf` は `step * 3` バイトあり、各要素は `step` 境界に収まる。
            unsafe {
                std::ptr::copy_nonoverlapping(
                    r as *const RAWINPUT as *const u8,
                    buf.as_mut_ptr().add(i * step),
                    size,
                );
            }
        }

        let mut accum = PointerAccum::default();
        // SAFETY: 直前に 3 件ぶんを `step` 間隔で並べた。
        unsafe { accumulate_from_buffer(buf.as_ptr() as *const RAWINPUT, 3, &mut accum) };

        // ★ 10 + (4 + 3) + 0 = 17 (⚠️ 符号は落ちている)。
        assert_eq!(accum.abs_delta_sum, 17, "3 件目まで正しく歩けていない");
        assert_eq!(accum.button_presses, 1);
        assert_eq!(accum.wheel_ticks, 1);
    }

    /// ⚠️★★★ **絶対モードの record を移動量として数えない**こと。
    ///
    /// ★ RDP / 一部の VM では `lLastX`/`lLastY` が **正規化された絶対座標**になるので、
    /// そのまま足すと ⚠️ **(a) 位置由来の値になり (b) 常に最大バケットへ張り付く**。
    /// ⚠️ ボタン / ホイールは**数える**（★ 活動が完全に見えなくなるのを避ける）。
    #[test]
    fn absolute_mode_records_do_not_contribute_movement() {
        let mut ri = mouse_record(32767, 32767, 0x0001);
        // SAFETY: `dwType` が `RIM_TYPEMOUSE` なので `mouse` を書いてよい。
        unsafe {
            ri.data.mouse.usFlags.0 |= MOUSE_MOVE_ABSOLUTE;
        }
        let mut accum = PointerAccum::default();
        // SAFETY: 1 件だけの妥当なバッファである。
        unsafe { accumulate_from_buffer(&ri as *const RAWINPUT, 1, &mut accum) };
        assert_eq!(
            accum.abs_delta_sum, 0,
            "絶対座標が移動量として足されている (⚠️ 位置由来の値になる)"
        );
        assert_eq!(accum.button_presses, 1, "ボタンは数える");
    }

    /// ⚠️ マウス以外の `dwType` は数えない（★ キーボードは登録していないが、防御的に固定する）。
    #[test]
    fn non_mouse_records_are_ignored() {
        let mut ri = mouse_record(100, 100, 0x0001);
        ri.header.dwType = 1; // RIM_TYPEKEYBOARD
        let mut accum = PointerAccum::default();
        // SAFETY: 1 件だけの妥当なバッファである。
        unsafe { accumulate_from_buffer(&ri as *const RAWINPUT, 1, &mut accum) };
        assert_eq!(accum, PointerAccum::default(), "マウス以外を数えている");
    }
}
