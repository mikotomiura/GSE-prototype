//! IME WinEvent の到達を実機で確かめる診断ツール（★ 配布ビルドには入らない）。
//!
//! ⚠️★★★ **これは計器ではない。** `cargo run --example` でしか動かず、
//! `cargo build --release` にも tauri のバンドルにも含まれない。
//!
//! ## 何を答えるためのものか（★ 2 つの問いを 1 回で閉じる）
//!
//! | # | 問い | ★ どう答えるか |
//! |---|---|---|
//! | 1 | ⚠️ `WINEVENT_SKIPOWNPROCESS` が **GSE 自身の画面での入力**を落としてしまわないか | ★ **SKIP 有り / 無しの 2 本**を同時に張り、到達数を比べる |
//! | 2 | ★ `EVENT_OBJECT_TEXTEDIT_CONVERSIONTARGETCHANGED`(0x8030) が**実際に飛ぶか** | ★ 範囲を `0x8027..=0x8030` にして**イベント別に数える** |
//!
//! ⚠️ 2 は「どの IME か」ではなく「**どのアプリの入力欄か**」に依存する
//! （★ 発火主体はアプリ側の UIA プロバイダ）。→ **アプリごとに測る必要がある。**
//!
//! ## 使い方
//!
//! ```text
//! cd src-tauri
//! cargo run --example ime_winevent_probe
//! ```
//!
//! 起動したら **60 秒のあいだ、確かめたいアプリで日本語を入力する**
//! （★ 変換もする。⚠️ **←→ で文節を移動させる**と 0x8030 が出るなら出る）。
//! 終了時に集計が stdout に出る。
//!
//! ## ⚠️ privacy
//!
//! ★ **記録するのはイベント ID と件数だけ。** ⚠️ ウィンドウタイトルもプロセス名も
//! **取得しない**。⚠️ PID は「自分と同じか」の **bool 判定にだけ**使い、値は出力しない。
//!
//! ★ 出力は `gse-replay` と同じく `std::io::stdout()` へ直接書く
//! （⚠️ マクロ経由の標準出力は CLAUDE.md 制約 8 で禁止されている）。

fn main() -> std::io::Result<()> {
    #[cfg(not(windows))]
    {
        use std::io::Write;
        let stderr = std::io::stderr();
        let mut lock = stderr.lock();
        writeln!(lock, "このツールは Windows 専用です。")?;
        Ok(())
    }
    #[cfg(windows)]
    {
        windows_probe::run()
    }
}

#[cfg(windows)]
mod windows_probe {
    use std::io::Write;
    use std::sync::atomic::{AtomicU32, Ordering};
    use std::time::{Duration, Instant};

    use windows::Win32::Foundation::HWND;
    use windows::Win32::System::Threading::GetCurrentProcessId;
    use windows::Win32::UI::Accessibility::{SetWinEventHook, UnhookWinEvent, HWINEVENTHOOK};
    use windows::Win32::UI::WindowsAndMessaging::{
        DispatchMessageW, GetWindowThreadProcessId, PeekMessageW, EVENT_OBJECT_IME_CHANGE,
        EVENT_OBJECT_IME_HIDE, EVENT_OBJECT_IME_SHOW,
        EVENT_OBJECT_TEXTEDIT_CONVERSIONTARGETCHANGED, MSG, PM_REMOVE,
    };

    const WINEVENT_OUTOFCONTEXT: u32 = 0x0000;
    const WINEVENT_SKIPOWNPROCESS: u32 = 0x0002;

    /// slot 0 = SKIPOWNPROCESS 有り / slot 1 = 無し。
    const SLOTS: usize = 2;

    static N_SHOW: [AtomicU32; SLOTS] = [AtomicU32::new(0), AtomicU32::new(0)];
    static N_HIDE: [AtomicU32; SLOTS] = [AtomicU32::new(0), AtomicU32::new(0)];
    static N_CHANGE: [AtomicU32; SLOTS] = [AtomicU32::new(0), AtomicU32::new(0)];
    static N_CONV: [AtomicU32; SLOTS] = [AtomicU32::new(0), AtomicU32::new(0)];
    static N_OTHER: [AtomicU32; SLOTS] = [AtomicU32::new(0), AtomicU32::new(0)];
    /// ⚠️ 「自プロセス由来だった」件数（★ PID そのものは保存も出力もしない）。
    static N_OWN: [AtomicU32; SLOTS] = [AtomicU32::new(0), AtomicU32::new(0)];

    static OUR_PID: AtomicU32 = AtomicU32::new(0);

    fn tally(slot: usize, event: u32, hwnd: HWND) {
        let bucket = if event == EVENT_OBJECT_IME_SHOW {
            &N_SHOW
        } else if event == EVENT_OBJECT_IME_HIDE {
            &N_HIDE
        } else if event == EVENT_OBJECT_IME_CHANGE {
            &N_CHANGE
        } else if event == EVENT_OBJECT_TEXTEDIT_CONVERSIONTARGETCHANGED {
            &N_CONV
        } else {
            &N_OTHER
        };
        bucket[slot].fetch_add(1, Ordering::Relaxed);

        // ⚠️ 自プロセス由来かどうかだけを数える。★ PID は出力しない。
        if !hwnd.0.is_null() {
            let mut pid = 0u32;
            // SAFETY: hwnd は OS がコールバックへ渡したもの。出力引数は自前のスタック変数。
            unsafe { GetWindowThreadProcessId(hwnd, Some(&mut pid)) };
            if pid != 0 && pid == OUR_PID.load(Ordering::Relaxed) {
                N_OWN[slot].fetch_add(1, Ordering::Relaxed);
            }
        }
    }

    unsafe extern "system" fn cb_skip(
        _h: HWINEVENTHOOK,
        event: u32,
        hwnd: HWND,
        _o: i32,
        _c: i32,
        _t: u32,
        _ms: u32,
    ) {
        tally(0, event, hwnd);
    }

    unsafe extern "system" fn cb_all(
        _h: HWINEVENTHOOK,
        event: u32,
        hwnd: HWND,
        _o: i32,
        _c: i32,
        _t: u32,
        _ms: u32,
    ) {
        tally(1, event, hwnd);
    }

    pub fn run() -> std::io::Result<()> {
        // SAFETY: 引数を取らない純粋な状態取得。
        OUR_PID.store(unsafe { GetCurrentProcessId() }, Ordering::Relaxed);

        let stdout = std::io::stdout();
        let mut out = stdout.lock();

        // ⚠️ 範囲は 0x8027..=0x8030。★ 間の 0x802A-0x802F も届くので tally で弾いている。
        let min = EVENT_OBJECT_IME_SHOW;
        let max = EVENT_OBJECT_TEXTEDIT_CONVERSIONTARGETCHANGED;

        writeln!(out, "== IME WinEvent probe ==")?;
        writeln!(
            out,
            "range 0x{min:04X}..=0x{max:04X}  SHOW=0x{:04X} HIDE=0x{:04X} CHANGE=0x{:04X} CONV=0x{:04X}",
            EVENT_OBJECT_IME_SHOW,
            EVENT_OBJECT_IME_HIDE,
            EVENT_OBJECT_IME_CHANGE,
            EVENT_OBJECT_TEXTEDIT_CONVERSIONTARGETCHANGED
        )?;
        writeln!(out)?;
        writeln!(
            out,
            "★ これから 60 秒、確かめたいアプリで日本語を入力してください。"
        )?;
        writeln!(out, "  - 変換もしてください (スペースキー)")?;
        writeln!(
            out,
            "  - ⚠️ ←→ で文節を移動させてください (0x8030 が出るならここ)"
        )?;
        writeln!(
            out,
            "  - ★ GSE 本体の G1 入力画面でも同じことをすると slot 差が見えます"
        )?;
        writeln!(out)?;
        out.flush()?;

        // SAFETY: 同一スレッドで張り、同一スレッドで外す (Win32 の要件)。
        let h_skip = unsafe {
            SetWinEventHook(
                min,
                max,
                None,
                Some(cb_skip),
                0,
                0,
                WINEVENT_OUTOFCONTEXT | WINEVENT_SKIPOWNPROCESS,
            )
        };
        let h_all =
            unsafe { SetWinEventHook(min, max, None, Some(cb_all), 0, 0, WINEVENT_OUTOFCONTEXT) };

        if h_skip.is_invalid() || h_all.is_invalid() {
            writeln!(out, "⚠️ SetWinEventHook に失敗しました。")?;
            return Ok(());
        }

        let deadline = Instant::now() + Duration::from_secs(60);
        let mut msg = MSG::default();
        while Instant::now() < deadline {
            // SAFETY: 自スレッドのメッセージキューを読むだけ。
            while unsafe { PeekMessageW(&mut msg, None, 0, 0, PM_REMOVE) }.as_bool() {
                unsafe { DispatchMessageW(&msg) };
            }
            std::thread::sleep(Duration::from_millis(10));
        }

        // SAFETY: 張ったスレッドと同じスレッドで外す。
        unsafe {
            let _ = UnhookWinEvent(h_skip);
            let _ = UnhookWinEvent(h_all);
        }

        let g = |a: &[AtomicU32; SLOTS], i: usize| a[i].load(Ordering::Relaxed);
        writeln!(out)?;
        writeln!(out, "== 結果 (60 秒) ==")?;
        writeln!(out, "                          SKIP有   SKIP無")?;
        writeln!(
            out,
            "IME_SHOW    (0x8027)   {:>8} {:>8}",
            g(&N_SHOW, 0),
            g(&N_SHOW, 1)
        )?;
        writeln!(
            out,
            "IME_HIDE    (0x8028)   {:>8} {:>8}",
            g(&N_HIDE, 0),
            g(&N_HIDE, 1)
        )?;
        writeln!(
            out,
            "IME_CHANGE  (0x8029)   {:>8} {:>8}",
            g(&N_CHANGE, 0),
            g(&N_CHANGE, 1)
        )?;
        writeln!(
            out,
            "CONV_TARGET (0x8030) ★ {:>8} {:>8}",
            g(&N_CONV, 0),
            g(&N_CONV, 1)
        )?;
        writeln!(
            out,
            "その他 (0x802A-2F)     {:>8} {:>8}",
            g(&N_OTHER, 0),
            g(&N_OTHER, 1)
        )?;
        writeln!(
            out,
            "うち自プロセス由来     {:>8} {:>8}",
            g(&N_OWN, 0),
            g(&N_OWN, 1)
        )?;
        writeln!(out)?;
        writeln!(out, "== 読み方 ==")?;
        writeln!(
            out,
            "★ 問い1: SKIP有 と SKIP無 の SHOW/HIDE が同数 → SKIPOWNPROCESS は取りこぼしていない"
        )?;
        writeln!(
            out,
            "   (＝今回の IME 定数修正は G1 で効く)。⚠️ SKIP有 だけ 0 なら落ちている。"
        )?;
        writeln!(
            out,
            "★ 問い2: CONV_TARGET が 1 件以上なら 0x8030 は使える。"
        )?;
        writeln!(
            out,
            "   ⚠️ 0 なら、そのアプリの UIA プロバイダが上げていない (採用しない根拠)。"
        )?;
        out.flush()?;
        Ok(())
    }
}
