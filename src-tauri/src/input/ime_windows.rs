use std::sync::atomic::Ordering;
use std::time::{SystemTime, UNIX_EPOCH};

use crossbeam_channel::Sender;
use windows::{
    core::*,
    Win32::Foundation::{BOOL, HWND, LPARAM},
    Win32::Graphics::Dwm::{DwmGetWindowAttribute, DWMWA_CLOAKED},
    Win32::System::Com::*,
    Win32::UI::Accessibility::*,
    Win32::UI::Input::Ime::{ImmGetContext, ImmGetOpenStatus, ImmReleaseContext},
    Win32::UI::WindowsAndMessaging::{
        EnumWindows, GetClassNameW, GetForegroundWindow, IsWindowVisible,
    },
};

use crate::input::ime_cloak::{
    candidate_shown_from_cloak, is_ime_cloak_class, CloakFold, FoldAction, FOLD_GAP_MS,
};
use crate::logger::LogEntry;

pub struct ImeMonitor {
    automation: Option<IUIAutomation>,
}

impl ImeMonitor {
    pub fn new() -> Self {
        unsafe {
            // COM is initialized here for the UIAutomation fallback.
            let _ = CoInitializeEx(None, COINIT_MULTITHREADED);

            let automation: Result<IUIAutomation> =
                CoCreateInstance(&CUIAutomation, None, CLSCTX_INPROC_SERVER);

            if let Ok(auto) = automation {
                Self {
                    automation: Some(auto),
                }
            } else {
                Self { automation: None }
            }
        }
    }

    /// Returns true if IME (Japanese input method, etc.) is currently composing text.
    ///
    /// Detection strategy (in priority order):
    ///
    /// 1. **WinEvent (PRIMARY)**: The WinEvent hook in hook.rs monitors
    ///    EVENT_OBJECT_IME_CHANGE/SHOW/HIDE across all processes via WINEVENT_OUTOFCONTEXT.
    ///    This is the only method that reliably detects the romaji→hiragana composition
    ///    phase (before the candidate list appears). Works for any foreground application.
    ///
    ///    WHY the old ImmGetContext approach failed:
    ///    ImmGetContext() returns NULL for windows owned by a different process.
    ///    Since we never type in our own app, it ALWAYS returned NULL.
    ///
    /// 2. **EnumWindows (SECONDARY)**: Scans all top-level windows for visible IME
    ///    candidate windows by class name. Covers the candidate-selection phase as a
    ///    belt-and-suspenders fallback if the WinEvent hasn't fired yet.
    ///
    /// 3. **UIAutomation (TERTIARY)**: Original approach retained as last resort.
    ///    Limited: only fires when the focused element is the IME window itself,
    ///    which doesn't happen during normal composition.
    pub fn is_candidate_window_open(&self) -> bool {
        let winevent_active = crate::input::hook::is_ime_active();

        // --- SECONDARY: EnumWindows scan for visible IME candidate windows ---
        // NOTE: "MSCTFIME UI" is intentionally excluded here.
        // That class belongs to the language bar (A/あ button on taskbar) which is
        // ALWAYS visible when Japanese IME is loaded, even when NOT composing.
        // Including it caused a permanent false-positive that paused all analysis.
        let enumwindows_active = is_ime_candidate_window_visible();

        // --- TERTIARY: UIAutomation focused-element check ---
        let uia_active = if let Some(auto) = &self.automation {
            let mut found = false;
            unsafe {
                if let Ok(element) = auto.GetFocusedElement() {
                    if let Ok(class_name) = element.CurrentClassName() {
                        let name = class_name.to_string();
                        // Check for "Candidate" only; do NOT include "Ime" — WebView2
                        // accessibility elements may expose class names containing "Ime"
                        // (e.g. ImeMode, ImeInputMode), which would cause a false-positive
                        // that permanently pauses analysis when the Tauri window has focus.
                        if name.contains("Candidate") {
                            found = true;
                        }
                    }
                    if !found {
                        if let Ok(name_bstr) = element.CurrentName() {
                            let name = name_bstr.to_string();
                            if name.contains("候補") {
                                found = true;
                            }
                        }
                    }
                }
            }
            found
        } else {
            false
        };

        // Safety: if WinEvent says IME is active but neither EnumWindows nor UIAutomation
        // confirms a visible candidate window, the IME_ACTIVE flag is stale.
        // This happens when EVENT_OBJECT_IME_HIDE was missed (e.g. focus change, crash).
        // Reset it here to prevent permanently pausing all keystroke analysis.
        //
        // ⚠️★★★ **2026-08-23: cloak 経路が駆動している端末では*この判定を使わない*。**
        //   ★ 理由は `is_stale_winevent_active` の doc を参照 (前提が実測で崩れている)。
        let legacy_path = crate::input::hook::LEGACY_IME_EVENT_SEEN.load(Ordering::Acquire);
        if is_stale_winevent_active(winevent_active, enumwindows_active, uia_active, legacy_path) {
            crate::input::hook::IME_ACTIVE.store(false, Ordering::Relaxed);
            return false;
        }

        winevent_active || enumwindows_active || uia_active
    }
}

/// Scan all top-level windows for visible IME candidate windows using EnumWindows.
///
/// マッチ判定そのもの (どのクラス名を候補ウィンドウとみなすか、"MSCTFIME UI" や
/// 完全一致 "IME" をなぜ除外するか) は `is_ime_candidate_class_name` の doc を参照。
///
/// ⚠️★★★ **2026-08-22 に `pub` へ上げた (収集開始前)。**
/// ★ 理由: `examples/ime_winevent_probe.rs` から**この関数そのもの**を叩いて
/// 実機での検出率を測るため。⚠️ プローブ側にロジックを**複製すると
/// 「複製の方が動いた」という無意味な計測**になり、本番経路の可否を答えられない。
/// ★ 公開したのは可視性だけで、シグネチャも中身も変えていない。
pub fn is_ime_candidate_window_visible() -> bool {
    // The callback sets *lparam to true and stops enumeration when an IME window is found.
    unsafe extern "system" fn callback(hwnd: HWND, lparam: LPARAM) -> BOOL {
        // Skip invisible windows
        if !IsWindowVisible(hwnd).as_bool() {
            return BOOL(1); // Continue enumeration
        }

        let mut buf = [0u16; 256];
        let len = GetClassNameW(hwnd, &mut buf);
        if len > 0 {
            let class = String::from_utf16_lossy(&buf[..len as usize]);

            if is_ime_candidate_class_name(&class) {
                // Signal found via lparam (pointer to bool on caller's stack)
                *(lparam.0 as *mut bool) = true;
                return BOOL(0); // Stop enumeration
            }
        }

        BOOL(1) // Continue enumeration
    }

    let mut found = false;
    unsafe {
        // Ignore the Result: BOOL(0) from our callback is interpreted as "error"
        // by EnumWindows, but it just means we stopped early after finding a match.
        let _ = EnumWindows(Some(callback), LPARAM(&mut found as *mut bool as isize));
    }
    found
}

// Kept for API compatibility (unused)
pub fn is_ime_active_check() -> bool {
    false
}

// ---------------------------------------------------------------------------
// IME candidate window decisions (pure — テストできる形に切り出す)
// ---------------------------------------------------------------------------

/// WinEvent (`IME_ACTIVE`) が立っているのに EnumWindows / UIAutomation のどちらも
/// 候補ウィンドウを確認できないとき、`IME_ACTIVE` は stale (EVENT_OBJECT_IME_HIDE 取りこぼし)。
///
/// ⚠️★ stale のまま放置すると、二度と `EVENT_OBJECT_IME_HIDE` が来ない限り
/// 分析が永久に一時停止する (fail-open ではなく fail-stuck になる)。
///
/// # ⚠️★★★ 2026-08-23: `legacy_path` で必ず絞ること
///
/// ★ この判定の**前提**は「本当に候補が出ているなら EnumWindows か UIA が裏を取れるはずだ」
/// である。⚠️ **その前提は cloak 経路では成り立たない**:
///
/// | 裏取り手段 | 実測 |
/// |---|---|
/// | `EnumWindows` (`is_ime_candidate_window_visible`) | ⚠️ **0/2400** (立ち上がり 0) |
/// | UI Automation のフォーカス要素 | ⚠️ **0** |
///
/// → ⚠️★★★ **裏取りが構造的に 0 の世界では、この式は「常に stale」に退化する。**
/// ★ つまり cloak 経路が `IME_ACTIVE=true` を立てた 100ms 後に必ず折られ、
/// **`ime_shadow` は 1 行も出ない。**
///
/// ★ そこで **文書化された経路 (0x8027-29) が実際に飛んだ端末に限って**この判定を使う。
/// ⚠️ 時間切れ判定 (fail-stuck の防止) は失われない:
/// `lib.rs` の 8 秒 safety valve と
/// [`crate::input::ime_cloak::MAX_SESSION_MS`] が別々に効いている。
fn is_stale_winevent_active(
    winevent_active: bool,
    enumwindows_active: bool,
    uia_active: bool,
    legacy_path: bool,
) -> bool {
    legacy_path && winevent_active && !enumwindows_active && !uia_active
}

/// IME 候補ウィンドウのクラス名判定。
///
/// ⚠️★★ **"MSCTFIME UI" (言語バーの A/あ 表示) と、完全一致の "IME" (IMM32 の常駐
/// システムウィンドウ) を含めてはならない。** どちらも日本語 IME 読み込み時は常時
/// 可視なため、含めると変換していないときも false positive になり、
/// 分析が永久に一時停止する事故になる (実際に起きた不具合)。
/// ★ 部分一致 "CandidateUI" / "Candidate" のみで判定することでこれらを自然に除外する。
fn is_ime_candidate_class_name(class: &str) -> bool {
    class.contains("CandidateUI") || class.contains("Candidate")
}

/// Spawn a dedicated background thread for IME open/close state tracking.
///
/// # Detection strategy (layered, in priority order)
///
/// **Primary — `ImmGetOpenStatus` polling:**
/// When `ImmGetContext(foreground_hwnd)` returns a non-null HIMC, `ImmGetOpenStatus`
/// gives the authoritative IME mode. This works when the foreground window is owned
/// by a process whose IME context is accessible (rare on Windows 10/11 for cross-process
/// windows, but used as a supplement when available).
///
/// **Fallback — `IME_STATE_DIRTY` flag from VK_DBE_* keys:**
/// `hook_callback` detects VK_DBE_* / VK_KANJI key presses and atomically updates
/// `IME_OPEN` + sets `IME_STATE_DIRTY`. When `ImmGetContext` returns NULL (typical for
/// cross-process windows), this thread reads the dirty flag and emits `LogEntry::ImeState`
/// at its own timestamp — ensuring the log entry is always temporally separated from
/// the triggering keystroke (no same-millisecond flapping).
///
/// # Lag reduction (ADVICE.md v2 requirement)
///
/// Instead of a fixed 100ms sleep, the thread waits on `wake_rx` with a 100ms timeout.
/// `hook_callback` sends a wake signal on every keypress (non-blocking `try_send`).
/// On wake, we sleep 5ms to let the OS route the key through the IME engine, then poll.
/// Maximum lag during active typing: ~5ms (down from 100ms).
///
/// # No flapping guarantee
///
/// `LogEntry::ImeState` is emitted only from THIS thread, never from the analysis thread
/// processing the key event. The timestamp is `SystemTime::now()` at the moment of
/// emission — always ≥5ms after the triggering keystroke.
pub fn spawn_ime_open_polling_thread(
    log_tx: Sender<LogEntry>,
    wake_rx: crossbeam_channel::Receiver<()>,
) {
    std::thread::spawn(move || {
        // Option<bool>: None = まだ一度も検出していない初期状態。
        // Some(v) = 前回 emit した状態。
        // None の場合は current_state が false でも必ず emit する
        // (起動直後に IME が A モードのまま VK 240 を押した場合を捕捉する)。
        let mut last_state: Option<bool> = None;

        loop {
            // Wait for a keystroke wake signal, or fall back to 100ms idle poll.
            let woke_by_key = wake_rx
                .recv_timeout(std::time::Duration::from_millis(100))
                .is_ok();

            if woke_by_key {
                // Brief delay: gives the OS time to route the key through the IME
                // engine so that ImmGetOpenStatus / IME_OPEN reflect the new mode.
                std::thread::sleep(std::time::Duration::from_millis(5));
            }

            // --- PRIMARY: ImmGetContext-based detection ---
            // May return NULL for cross-process windows on Windows 10/11.
            let mut imm_succeeded = false;
            unsafe {
                let hwnd = GetForegroundWindow();
                if !hwnd.0.is_null() {
                    let himc = ImmGetContext(hwnd);
                    if !himc.0.is_null() {
                        let current_state = ImmGetOpenStatus(himc).as_bool();
                        let _ = ImmReleaseContext(hwnd, himc);
                        imm_succeeded = true;

                        // last_state が None (初回) か、前回と異なる場合のみ emit
                        if last_state.map_or(true, |prev| prev != current_state) {
                            last_state = Some(current_state);
                            crate::input::hook::IME_OPEN.store(current_state, Ordering::Relaxed);
                            emit_ime_state(&log_tx, current_state);
                        }
                    }
                }
            }

            // --- FALLBACK: VK_DBE_* dirty flag from hook_callback ---
            // Used when ImmGetContext returns NULL (typical cross-process case).
            // IME_OPEN was already updated by the hook; we just need to detect the
            // change and emit the log entry with a fresh timestamp.
            if !imm_succeeded {
                if crate::input::hook::IME_STATE_DIRTY.swap(false, Ordering::AcqRel) {
                    let current_state = crate::input::hook::IME_OPEN.load(Ordering::Acquire);
                    // last_state が None (初回) か、前回と異なる場合のみ emit
                    if last_state.map_or(true, |prev| prev != current_state) {
                        last_state = Some(current_state);
                        emit_ime_state(&log_tx, current_state);
                    }
                }
            }
        }
    });
}

// ---------------------------------------------------------------------------
// ⚠️★★★ cloak resolver — cloak/uncloak から `IME_ACTIVE` を駆動する (2026-08-23)
// ---------------------------------------------------------------------------

/// ★ 窓のクラス名を取る。⚠️ 取れなければ `None` (★ 失敗を空文字に丸めない)。
///
/// ⚠️ **privacy**: ★ クラス名は判定に使うだけで、**ログにも NDJSON にも出さない**。
/// ⚠️ ウィンドウタイトル (`GetWindowTextW`) も PID も取得しない。
fn class_name_of(hwnd: HWND) -> Option<String> {
    let mut buf = [0u16; 256];
    // SAFETY: hwnd は WinEvent が渡したもの。buf は自前のスタック配列で、
    //   `GetClassNameW` は書き込んだ長さを返す (失敗時 0)。
    let len = unsafe { GetClassNameW(hwnd, &mut buf) };
    if len <= 0 {
        // ⚠️ WINEVENT_OUTOFCONTEXT の配送は非同期なので、到達時に窓が消えていればここ。
        return None;
    }
    Some(String::from_utf16_lossy(&buf[..len as usize]))
}

/// ⚠️★★★ **DWM に「その窓はいま cloak されているか」を聞く。**
///
/// ★ **なぜイベントの種類 (`CLOAKED`/`UNCLOAKED`) をそのまま信じないか**:
/// `WINEVENT_OUTOFCONTEXT` の配送は**非同期**で、resolver に届くまでに
/// 状態がさらに変わっていることがある。★ **OS に聞いた現在値が唯一の真実。**
///
/// ⚠️ 取得に失敗したら `None`。★ 「cloak されていない」に丸めない (判定を汚す)。
fn dwm_is_cloaked(hwnd: HWND) -> Option<bool> {
    let mut v: u32 = 0;
    // SAFETY: hwnd は WinEvent が渡したもの。出力先は自前の u32 で、サイズも一致させている。
    let hr = unsafe {
        DwmGetWindowAttribute(
            hwnd,
            DWMWA_CLOAKED,
            (&mut v as *mut u32).cast(),
            std::mem::size_of::<u32>() as u32,
        )
    };
    if hr.is_ok() {
        Some(v != 0)
    } else {
        None
    }
}

/// ⚠️★★★ **cloak/uncloak を受け取り、`IME_ACTIVE` と IME Shadow の atomics を駆動する。**
///
/// # なぜ専用スレッドなのか
///
/// ★ 判定にはウィンドウクラス名が要るが、⚠️ `hook-constraints` **Win-1** により
/// **WinEvent コールバック内で `GetClassNameW` は呼べない** (Atomic ＋ `try_send` のみ)。
/// → ★ コールバックは HWND を `try_send` するだけにして、**解決はここでやる**。
///
/// # ⚠️ このスレッドが唯一の書き手であること
///
/// ★ `IME_COMPOSITION_START_MS` / `IME_SHADOW_DWELL_MS` / `IME_SHADOW_READY` /
/// `IME_ACTIVE` を cloak 経路から書くのは**ここだけ**である。
/// ⚠️ 文書化された経路 (`hook_windows.rs` の `win_event_callback`) が 1 度でも飛んだ端末では、
/// コールバック側が `try_send` しなくなるので**このスレッドは何も受け取らない**
/// (`hook.rs::LEGACY_IME_EVENT_SEEN` を参照)。
///
/// # ⚠️ `IME_OPEN` は**触らない**
///
/// ★ `IME_OPEN` (日本語モードか英数か) には別の正しい持ち主が居る
/// (`VK_DBE_*` キー ＋ `ImmGetOpenStatus` ポーリング)。
/// ⚠️★★★ 旧実装が「無関係な窓の cloak で `IME_OPEN` まで立てていた」のが
/// 2026-08-21 に見つかった計器不良そのものである。★ 同じ誤りを繰り返さない。
pub fn spawn_cloak_resolver_thread() {
    // ⚠️ 有界チャネル。★ 溢れたらコールバック側が捨てる (フックを絶対に詰まらせない)。
    let (tx, rx) = crossbeam_channel::bounded::<crate::input::hook::CloakEvent>(256);
    crate::input::hook::set_cloak_event_sender(tx);

    std::thread::spawn(move || {
        tracing::info!("IME cloak resolver thread started");
        let mut fold = CloakFold::new();
        // ★ debounce の満了を見逃さない程度に細かく起こす。
        let tick = std::time::Duration::from_millis(FOLD_GAP_MS.max(1) / 4 + 1);
        loop {
            match rx.recv_timeout(tick) {
                Ok(ev) => {
                    let hwnd = HWND(ev.hwnd as *mut std::ffi::c_void);
                    // ★ 1) クラスで絞る。⚠️ 取れなければ捨てる (短命な窓)。
                    let Some(class) = class_name_of(hwnd) else {
                        continue;
                    };
                    if !is_ime_cloak_class(&class) {
                        continue;
                    }
                    // ★ 2) 辺の名前ではなく **OS に現在状態を聞く**。
                    //   ⚠️ 聞けなかったときだけ、届いた辺を保険で使う。
                    let cloaked = dwm_is_cloaked(hwnd).unwrap_or(ev.cloaked);
                    let shown = candidate_shown_from_cloak(cloaked);
                    let now = now_ms();
                    if let Some(action) = fold.on_event(ev.hwnd, shown, now) {
                        apply_fold_action(action);
                    }
                }
                Err(crossbeam_channel::RecvTimeoutError::Timeout) => {}
                Err(crossbeam_channel::RecvTimeoutError::Disconnected) => {
                    // ⚠️ 送信端は `OnceLock` に置かれ落ちないので、実際にはここへ来ない。
                    tracing::warn!("cloak resolver channel disconnected — thread exits");
                    return;
                }
            }
            // ★ 受信の有無に関わらず**必ず**時間側を進める
            //   (⚠️ 呼ばないと最後の uncloak のあとセッションが閉じない)。
            if let Some(action) = fold.on_tick(now_ms()) {
                apply_fold_action(action);
            }
        }
    });
}

/// ★ [`FoldAction`] を atomics へ反映する。⚠️ **書き手はここだけ。**
///
/// ★ 更新順は既存の `win_event_callback` (IME_SHOW / IME_HIDE) と**同じ形**にしてある
/// —— `IME_SHADOW_READY` の `Release` store が先行する Relaxed store 群を可視化する
/// フェンスになる (`hook.rs::IME_SHADOW_READY` の Ordering 設計を参照)。
fn apply_fold_action(action: FoldAction) {
    use crate::input::hook;
    match action {
        FoldAction::Begin(start_ms) => {
            hook::IME_COMPOSITION_START_MS.store(start_ms, Ordering::Relaxed);
            // ★ 前セッションのカウンターを畳む (既存 IME_SHOW 経路と同じ)。
            hook::IME_CANDIDATE_NAV_COUNT.store(0, Ordering::Relaxed);
            hook::IME_SHADOW_ABANDON.store(false, Ordering::Relaxed);
            hook::IME_ACTIVE.store(true, Ordering::Relaxed);
        }
        FoldAction::End(dwell_ms) => {
            hook::IME_SHADOW_DWELL_MS.store(dwell_ms, Ordering::Relaxed);
            hook::IME_COMPOSITION_START_MS.store(0, Ordering::Relaxed);
            hook::IME_SHADOW_READY.store(true, Ordering::Release);
            hook::IME_ACTIVE.store(false, Ordering::Relaxed);
        }
    }
}

fn now_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64
}

/// Emit a `LogEntry::ImeState` to the logger channel with the current wall-clock time.
fn emit_ime_state(log_tx: &Sender<LogEntry>, on: bool) {
    let ts = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64;
    let active = crate::input::hook::IME_ACTIVE.load(Ordering::Relaxed);
    let _ = log_tx.try_send(LogEntry::ImeState {
        timestamp: ts,
        on,
        active,
    });
    tracing::debug!(
        "IME open: {} (polling)",
        if on { "ON (あ)" } else { "OFF (A)" }
    );
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    /// ⚠️ 以下 4 件は 2026-08-23 に `legacy_path` 引数が増えたが、**判定内容は変えていない**。
    /// ★ 文書化された経路 (0x8027-29) が飛ぶ端末＝従来の世界を `true` で表している。
    #[test]
    fn stale_when_only_winevent_signals_active() {
        assert!(
            is_stale_winevent_active(true, false, false, true),
            "★ WinEvent だけが active なら stale とみなし、放置せずリセットする"
        );
    }

    #[test]
    fn not_stale_when_enumwindows_confirms() {
        assert!(!is_stale_winevent_active(true, true, false, true));
    }

    #[test]
    fn not_stale_when_uia_confirms() {
        assert!(!is_stale_winevent_active(true, false, true, true));
    }

    #[test]
    fn not_stale_when_winevent_itself_is_false() {
        // WinEvent が false のときは「stale」という概念自体が当てはまらない。
        assert!(!is_stale_winevent_active(false, false, false, true));
    }

    /// ⚠️★★★ **本タスクの中核の回帰テスト。**
    ///
    /// ★ cloak 経路が駆動している端末 (`legacy_path=false`) では、
    /// EnumWindows も UIA も**構造的に 0** なので、この判定を効かせると
    /// `IME_ACTIVE` が立った 100ms 後に必ず折られ **`ime_shadow` が 1 行も出ない**。
    #[test]
    fn never_stale_on_cloak_driven_machines() {
        assert!(
            !is_stale_winevent_active(true, false, false, false),
            "★ 裏取りが構造的に 0 の世界では『常に stale』に退化する → 効かせない"
        );
    }

    #[test]
    fn matches_known_candidate_class_names() {
        assert!(is_ime_candidate_class_name("CandidateUI_UIElement"));
        assert!(is_ime_candidate_class_name("SomeCandidateWindow"));
    }

    /// ★★ 回帰テストの本体。この 2 クラス名を含めると分析が永久停止する不具合が実際に起きた。
    #[test]
    fn excludes_language_bar_and_imm32_system_window() {
        assert!(
            !is_ime_candidate_class_name("MSCTFIME UI"),
            "言語バー (A/あ 表示) は変換中でなくても常時可視 → 含めると誤検知が固定化する"
        );
        assert!(
            !is_ime_candidate_class_name("IME"),
            "IMM32 の常駐システムウィンドウは常時可視 → 完全一致 'IME' は含めない"
        );
    }

    #[test]
    fn does_not_match_unrelated_class_names() {
        assert!(!is_ime_candidate_class_name("Chrome_WidgetWin_1"));
        assert!(!is_ime_candidate_class_name(""));
    }
}
