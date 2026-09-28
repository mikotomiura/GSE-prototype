//! 参照入力欄 Windows (a) IMM 互換: 自窓の IME メッセージを content-free な `gt/1`（`src: "win_imm"`）で記録する。
//!
//! 使い方（結果は終了コードだけで知らせる。コンソールには何も出さない）:
//!   refinput_imm --out <path>              窓を 1 つ作り、閉じるまで記録する（既にある <path> は上書きしない）
//!   refinput_imm --selftest [--out <path>] 窓を作らず、核を通した代表的な列を書いて読み戻して検査する
//!
//! Exit: 0 = 正常 / 1 = 実行時の失敗（窓・書き込み・selftest の不一致）/ 2 = 使い方の誤り・Windows 以外
//!
//! ⚠️★★★ 文字列を一切取得しない。長さは `ImmGetCompositionStringW` にバッファ NULL・長さ 0 を渡して
//! **バイト数だけ**を得る。文字を運ぶメッセージ（`WM_IME_CHAR` など）は記録しない。
//! ⚠️ 解釈しない: 届いたメッセージを届いた順に書く（どのメッセージが届くかは M5 のパイロットで確かめる）。

use std::process::ExitCode;

#[cfg(windows)]
fn main() -> ExitCode {
    imp::run()
}

#[cfg(not(windows))]
fn main() -> ExitCode {
    // 参照入力欄の窓は Windows でしか動かない（`cargo test` が他の OS でも通るように、bin は空の入口を持つ）。
    ExitCode::from(2)
}

#[cfg(windows)]
mod imp {
    use std::ffi::OsString;
    use std::fs::{File, OpenOptions};
    use std::io::{Read, Write};
    use std::path::{Path, PathBuf};
    use std::process::ExitCode;
    use std::sync::atomic::{AtomicBool, Ordering};
    use std::sync::{Mutex, OnceLock};
    use std::time::{SystemTime, UNIX_EPOCH};

    use refinput_windows::{check_line, header, line, ticks_to_ns, units_from_bytes, Ev, Src};
    use windows::core::{w, PCWSTR};
    use windows::Win32::Foundation::{HINSTANCE, HWND, LPARAM, LRESULT, WPARAM};
    use windows::Win32::Graphics::Gdi::{GetSysColorBrush, UpdateWindow, COLOR_WINDOW};
    use windows::Win32::System::LibraryLoader::GetModuleHandleW;
    use windows::Win32::System::Performance::{QueryPerformanceCounter, QueryPerformanceFrequency};
    use windows::Win32::UI::Input::Ime::{
        ImmGetCompositionStringW, ImmGetContext, ImmReleaseContext, GCS_COMPSTR, GCS_RESULTSTR,
        IME_COMPOSITION_STRING,
    };
    use windows::Win32::UI::Input::KeyboardAndMouse::SetFocus;
    use windows::Win32::UI::WindowsAndMessaging::{
        CreateWindowExW, DefWindowProcW, DispatchMessageW, GetMessageW, LoadCursorW,
        PostQuitMessage, RegisterClassExW, ShowWindow, TranslateMessage, CS_HREDRAW, CS_VREDRAW,
        CW_USEDEFAULT, IDC_ARROW, MSG, SW_SHOW, WM_DESTROY, WM_IME_COMPOSITION,
        WM_IME_ENDCOMPOSITION, WM_IME_NOTIFY, WM_IME_STARTCOMPOSITION, WM_KEYDOWN, WM_KILLFOCUS,
        WM_SETFOCUS, WNDCLASSEXW, WS_OVERLAPPEDWINDOW,
    };

    const APP_VERSION: &str = env!("CARGO_PKG_VERSION");

    /// 書き込みの失敗（窓プロシージャは戻り値で返せないので旗で持ち、終了コードにする）。
    static WRITE_FAILED: AtomicBool = AtomicBool::new(false);
    static RECORDER: OnceLock<Mutex<Recorder>> = OnceLock::new();

    // ---- 記録（時計・出力）---------------------------------------------------------------------

    /// 出力ファイルと単調時計の周波数。
    struct Recorder {
        file: File,
        qpc_freq: i64,
    }

    fn qpc_freq() -> i64 {
        let mut f = 0i64;
        // SAFETY: 出力先は有効な i64 へのポインタ。
        match unsafe { QueryPerformanceFrequency(&mut f) } {
            Ok(()) => f,
            Err(_) => 0,
        }
    }

    /// 単調時計（QueryPerformanceCounter）を ns にしたもの。
    fn mono_ns(freq: i64) -> u64 {
        let mut t = 0i64;
        // SAFETY: 出力先は有効な i64 へのポインタ。
        match unsafe { QueryPerformanceCounter(&mut t) } {
            Ok(()) => ticks_to_ns(t, freq),
            Err(_) => 0,
        }
    }

    /// 壁時計（Unix ms）。
    fn wall_ms() -> u64 {
        match SystemTime::now().duration_since(UNIX_EPOCH) {
            Ok(d) => u64::try_from(d.as_millis()).unwrap_or(u64::MAX),
            Err(_) => 0,
        }
    }

    fn append(file: &mut File, text: &str) -> std::io::Result<()> {
        // ★ 1 行ずつ LF で書く（BOM なし・CRLF なし）。書いた時点で OS に渡す（プロセスが落ちても残す）。
        let mut buf = String::with_capacity(text.len() + 1);
        buf.push_str(text);
        buf.push('\n');
        file.write_all(buf.as_bytes())
    }

    /// 事象 1 件を、届いた時刻つきで書く。
    fn record(ev: Ev) {
        let Some(cell) = RECORDER.get() else { return };
        let mut rec = match cell.lock() {
            Ok(g) => g,
            Err(poisoned) => poisoned.into_inner(),
        };
        let text = line(ev, wall_ms(), mono_ns(rec.qpc_freq));
        if append(&mut rec.file, &text).is_err() {
            WRITE_FAILED.store(true, Ordering::SeqCst);
            // SAFETY: 引数なしの単純な呼び出し（この窓のスレッドで、窓プロシージャの中から呼ぶ）。
            unsafe { PostQuitMessage(1) };
        }
    }

    // ---- IMM の呼び出し（unsafe はここに閉じる）-------------------------------------------------

    /// 窓の入力コンテキスト（取得と解放を対にする）。
    struct ImeContext {
        hwnd: HWND,
        himc: windows::Win32::UI::Input::Ime::HIMC,
    }

    impl ImeContext {
        fn of(hwnd: HWND) -> Option<ImeContext> {
            // SAFETY: hwnd はこの窓プロシージャに渡された自分の窓。
            let himc = unsafe { ImmGetContext(hwnd) };
            if himc.is_invalid() {
                None
            } else {
                Some(ImeContext { hwnd, himc })
            }
        }

        /// 指定した種類の文字列の**長さだけ**（UTF-16 のコード単位数）。
        /// ⚠️★★★ バッファは NULL・長さ 0 なので、文字列そのものは取得されない。
        fn len_of(&self, kind: IME_COMPOSITION_STRING) -> u32 {
            // SAFETY: himc は取得済みで、解放前。バッファ NULL・長さ 0 ではバイト数だけが返る。
            units_from_bytes(unsafe { ImmGetCompositionStringW(self.himc, kind, None, 0) })
        }
    }

    impl Drop for ImeContext {
        fn drop(&mut self) {
            // SAFETY: `of` で取得した組を、同じ窓に返す。
            let _ = unsafe { ImmReleaseContext(self.hwnd, self.himc) };
        }
    }

    /// `WM_IME_COMPOSITION` の記録。`lParam` のフラグを書き、立っている種類の長さだけを得る。
    /// ⚠️ `wParam` はこのメッセージでは直近の 1 文字（DBCS）を運ぶので、**読まない**。
    fn record_composition(hwnd: HWND, lparam: LPARAM) {
        let flags = lparam.0 as u32;
        let ctx = ImeContext::of(hwnd);
        let len_if = |bit: IME_COMPOSITION_STRING| -> u32 {
            match &ctx {
                Some(c) if flags & bit.0 != 0 => c.len_of(bit),
                _ => 0,
            }
        };
        record(Ev::Comp {
            flags,
            comp_len: len_if(GCS_COMPSTR),
            result_len: len_if(GCS_RESULTSTR),
        });
    }

    // ---- 窓 ------------------------------------------------------------------------------------

    /// 記録したうえで **`DefWindowProcW` に渡す**（IME の既定の表示を壊さない）。
    /// ⚠️ 文字を運ぶメッセージ（`WM_IME_CHAR` など）は扱わない（既定の処理に任せる）。
    unsafe extern "system" fn wnd_proc(
        hwnd: HWND,
        msg: u32,
        wparam: WPARAM,
        lparam: LPARAM,
    ) -> LRESULT {
        match msg {
            WM_IME_STARTCOMPOSITION => record(Ev::StartComp),
            WM_IME_COMPOSITION => record_composition(hwnd, lparam),
            WM_IME_ENDCOMPOSITION => record(Ev::EndComp),
            WM_IME_NOTIFY => record(Ev::Notify {
                imn: wparam.0 as u32,
            }),
            WM_KEYDOWN => record(Ev::KeyDown {
                vk: wparam.0 as u32,
            }),
            WM_SETFOCUS => record(Ev::FocusIn),
            WM_KILLFOCUS => record(Ev::FocusOut),
            WM_DESTROY => {
                // SAFETY: 引数なしの単純な呼び出し。
                unsafe { PostQuitMessage(0) };
                return LRESULT(0);
            }
            _ => {}
        }
        // SAFETY: 受け取った引数をそのまま既定の処理へ渡す。
        unsafe { DefWindowProcW(hwnd, msg, wparam, lparam) }
    }

    /// 窓を 1 つ作って、閉じられるまでメッセージを回す。
    fn run_window() -> windows::core::Result<i32> {
        // SAFETY: Win32 の窓の作成とメッセージループ。この関数の中（1 スレッド）で完結する。
        unsafe {
            let hinstance: HINSTANCE = GetModuleHandleW(PCWSTR::null())?.into();
            let class_name = w!("GseRefInputImm");
            let class = WNDCLASSEXW {
                cbSize: std::mem::size_of::<WNDCLASSEXW>() as u32,
                style: CS_HREDRAW | CS_VREDRAW,
                lpfnWndProc: Some(wnd_proc),
                hInstance: hinstance,
                hCursor: LoadCursorW(None, IDC_ARROW)?,
                hbrBackground: GetSysColorBrush(COLOR_WINDOW),
                lpszClassName: class_name,
                ..Default::default()
            };
            if RegisterClassExW(&class) == 0 {
                return Err(windows::core::Error::from_win32());
            }
            let hwnd = CreateWindowExW(
                Default::default(),
                class_name,
                w!("refinput_imm (gt/1 win_imm)"),
                WS_OVERLAPPEDWINDOW,
                CW_USEDEFAULT,
                CW_USEDEFAULT,
                640,
                240,
                None,
                None,
                hinstance,
                None,
            )?;
            let _ = ShowWindow(hwnd, SW_SHOW);
            let _ = UpdateWindow(hwnd);
            let _ = SetFocus(hwnd);

            let mut msg = MSG::default();
            loop {
                let got = GetMessageW(&mut msg, None, 0, 0);
                if got.0 <= 0 {
                    // 0 = WM_QUIT / −1 = エラー
                    return if got.0 == 0 {
                        Ok(msg.wParam.0 as i32)
                    } else {
                        Err(windows::core::Error::from_win32())
                    };
                }
                // ★ IME は TranslateMessage 経由でキーを受ける（文字の記録には使わない）。
                let _ = TranslateMessage(&msg);
                DispatchMessageW(&msg);
            }
        }
    }

    // ---- 引数・selftest ------------------------------------------------------------------------

    struct Args {
        selftest: bool,
        out: Option<PathBuf>,
    }

    /// `--out <path>` / `--selftest`。未知の引数・値の欠け・重複は使い方の誤り。
    fn parse_args<I: Iterator<Item = OsString>>(mut it: I) -> Result<Args, ()> {
        let mut args = Args {
            selftest: false,
            out: None,
        };
        while let Some(a) = it.next() {
            match a.to_str() {
                Some("--selftest") if !args.selftest => args.selftest = true,
                Some("--out") if args.out.is_none() => match it.next() {
                    Some(p) if !p.is_empty() => args.out = Some(PathBuf::from(p)),
                    _ => return Err(()),
                },
                _ => return Err(()),
            }
        }
        Ok(args)
    }

    /// selftest が書く代表的な列（窓を作らず、核だけを通す）。時刻は決め打ち。
    fn selftest_events() -> Vec<Ev> {
        vec![
            Ev::FocusIn,
            Ev::KeyDown { vk: 0xE5 },
            Ev::StartComp,
            Ev::Notify { imn: 5 },
            Ev::Comp {
                flags: GCS_COMPSTR.0,
                comp_len: 1,
                result_len: 0,
            },
            Ev::Comp {
                flags: GCS_COMPSTR.0,
                comp_len: 2,
                result_len: 0,
            },
            Ev::Notify { imn: 4 },
            Ev::Comp {
                flags: GCS_RESULTSTR.0,
                comp_len: 0,
                result_len: 2,
            },
            Ev::EndComp,
            Ev::KeyDown { vk: 13 },
            Ev::FocusOut,
        ]
    }

    /// 核を通して書き、読み戻して検査する。⚠️ 通ったこと ≠ 実 IME で届くこと（M5 で確かめる）。
    fn selftest(path: &Path) -> bool {
        let mut lines = vec![header(Src::WinImm, APP_VERSION)];
        for (i, ev) in selftest_events().into_iter().enumerate() {
            let i = i as u64;
            lines.push(line(
                ev,
                1_700_000_000_000 + i * 10,
                1_000_000_000 + i * 10_000_000,
            ));
        }
        let written = File::create(path).and_then(|mut f| {
            for l in &lines {
                append(&mut f, l)?;
            }
            f.flush()
        });
        if written.is_err() {
            return false;
        }
        let mut text = String::new();
        if File::open(path)
            .and_then(|mut f| f.read_to_string(&mut text))
            .is_err()
        {
            return false;
        }
        // 書いたとおりに読み戻せる（BOM・CRLF・欠けが無い）
        let mut expected = lines.join("\n");
        expected.push('\n');
        if text != expected {
            return false;
        }
        // 全行が content-free な gt/1 の形（ヘッダは 1 行目だけ・2 行目以降は ev）
        let mut it = text.lines();
        let head_ok = it
            .next()
            .is_some_and(|h| h.contains("\"kind\":\"header\"") && check_line(h).is_ok());
        head_ok && it.all(|l| l.contains("\"kind\":\"ev\"") && check_line(l).is_ok())
    }

    pub fn run() -> ExitCode {
        let Ok(args) = parse_args(std::env::args_os().skip(1)) else {
            return ExitCode::from(2);
        };
        if args.selftest {
            // --out が無ければ一時ファイルに書いて消す
            let (path, temp) = match args.out {
                Some(p) => (p, false),
                None => (
                    std::env::temp_dir().join(format!(
                        "refinput_imm_selftest_{}.jsonl",
                        std::process::id()
                    )),
                    true,
                ),
            };
            let ok = selftest(&path);
            if temp {
                let _ = std::fs::remove_file(&path);
            }
            return if ok {
                ExitCode::SUCCESS
            } else {
                ExitCode::from(1)
            };
        }
        let Some(path) = args.out else {
            return ExitCode::from(2);
        };
        // ★ 生ログを上書きしない（既にあれば失敗）
        let Ok(mut file) = OpenOptions::new().write(true).create_new(true).open(&path) else {
            return ExitCode::from(1);
        };
        if append(&mut file, &header(Src::WinImm, APP_VERSION)).is_err() {
            return ExitCode::from(1);
        }
        let _ = RECORDER.set(Mutex::new(Recorder {
            file,
            qpc_freq: qpc_freq(),
        }));
        match run_window() {
            Ok(_) if !WRITE_FAILED.load(Ordering::SeqCst) => ExitCode::SUCCESS,
            _ => ExitCode::from(1),
        }
    }
}
