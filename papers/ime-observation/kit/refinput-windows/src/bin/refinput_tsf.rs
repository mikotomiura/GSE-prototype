//! 参照入力欄 Windows (b) TSF 直受け: 自スレッドの TSF の composition と候補一覧を content-free な `gt/1`（`src: "win_tsf"`）で記録する。
//!
//! 使い方（結果は終了コードだけで知らせる。コンソールには何も出さない）:
//!   refinput_tsf --out <path>              窓（RichEdit）を 1 つ作り、閉じるまで記録する（既にある <path> は上書きしない）
//!   refinput_tsf --selftest [--out <path>] TSF を起こさず、核と状態遷移を通した代表的な列を書いて読み戻して検査する
//!
//! Exit: 0 = 正常 / 1 = 実行時の失敗（窓・TSF・書き込み・selftest の不一致）/ 2 = 使い方の誤り・Windows 以外
//!
//! ⚠️★★★ 文字列を一切取得しない（長さは `ITfRangeACP::GetExtent` の `cch` だけ）。他プロセスの TSF は見ない。
//! ★ TSF の道: 道 1（詳細は `tsf.rs` と README）。⚠️ 解釈しない: 届いた通知を届いた順に書く。

use std::process::ExitCode;

#[cfg(windows)]
#[path = "../tsf.rs"]
mod tsf;

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
    use std::cell::{Cell, RefCell};
    use std::ffi::OsString;
    use std::fs::{File, OpenOptions};
    use std::io::{Read, Write};
    use std::path::{Path, PathBuf};
    use std::process::ExitCode;
    use std::rc::Rc;
    use std::time::{SystemTime, UNIX_EPOCH};

    use refinput_windows::{check_line, header, line, ticks_to_ns, Ev, Src, UiKind};
    use windows::core::{w, PCWSTR};
    use windows::Win32::Foundation::{HINSTANCE, HWND, LPARAM, LRESULT, WPARAM};
    use windows::Win32::Graphics::Gdi::{GetSysColorBrush, UpdateWindow, COLOR_WINDOW};
    use windows::Win32::System::LibraryLoader::{
        GetModuleHandleW, LoadLibraryExW, LOAD_LIBRARY_SEARCH_SYSTEM32,
    };
    use windows::Win32::System::Performance::{QueryPerformanceCounter, QueryPerformanceFrequency};
    use windows::Win32::UI::Controls::RichEdit::{EM_SETEDITSTYLE, MSFTEDIT_CLASS, SES_USECTF};
    use windows::Win32::UI::Input::KeyboardAndMouse::SetFocus;
    use windows::Win32::UI::WindowsAndMessaging::{
        CreateWindowExW, DefWindowProcW, DestroyWindow, DispatchMessageW, GetMessageW, GetWindow,
        LoadCursorW, PostQuitMessage, RegisterClassExW, SendMessageW, ShowWindow, TranslateMessage,
        CS_HREDRAW, CS_VREDRAW, CW_USEDEFAULT, ES_AUTOVSCROLL, ES_MULTILINE, GW_CHILD, IDC_ARROW,
        MSG, SW_SHOW, WINDOW_STYLE, WM_DESTROY, WM_KEYDOWN, WM_SETFOCUS, WNDCLASSEXW, WS_CAPTION,
        WS_CHILD, WS_EX_CLIENTEDGE, WS_OVERLAPPED, WS_SYSMENU, WS_VISIBLE, WS_VSCROLL,
    };

    use super::tsf::{self, CompTracker};

    const APP_VERSION: &str = env!("CARGO_PKG_VERSION");

    // ---- 記録（時計・出力）---------------------------------------------------------------------

    /// 出力ファイルと単調時計の周波数。
    struct Out {
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

    /// 事象 1 件を、届いた時刻つきで書く出口を作る。書き込みに失敗したら旗を立ててメッセージループを止める
    /// （シンクは戻り値で失敗を返せないので、旗で持ち、終了コードにする）。
    fn make_recorder(file: File, failed: Rc<Cell<bool>>) -> tsf::Recorder {
        let out = RefCell::new(Out {
            file,
            qpc_freq: qpc_freq(),
        });
        Rc::new(move |ev: Ev| {
            let Ok(mut o) = out.try_borrow_mut() else {
                // A reentrant call while an event is already being written would otherwise be
                // silently dropped; treat it as a recording failure instead of losing the event.
                failed.set(true);
                // SAFETY: 引数なしの単純な呼び出し（この窓のスレッドで呼ぶ）。
                unsafe { PostQuitMessage(1) };
                return;
            };
            let text = line(ev, wall_ms(), mono_ns(o.qpc_freq));
            if append(&mut o.file, &text).is_err() {
                failed.set(true);
                // SAFETY: 引数なしの単純な呼び出し（この窓のスレッドで呼ぶ）。
                unsafe { PostQuitMessage(1) };
            }
        })
    }

    // ---- 窓 ------------------------------------------------------------------------------------

    /// 親窓: フォーカスを RichEdit（子）に渡し、閉じられたらループを止める。
    unsafe extern "system" fn wnd_proc(
        hwnd: HWND,
        msg: u32,
        wparam: WPARAM,
        lparam: LPARAM,
    ) -> LRESULT {
        match msg {
            WM_SETFOCUS => {
                // SAFETY: 自分の子窓（RichEdit）を引いてフォーカスを渡す。
                if let Ok(edit) = unsafe { GetWindow(hwnd, GW_CHILD) } {
                    let _ = unsafe { SetFocus(edit) };
                }
                return LRESULT(0);
            }
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

    /// 親窓と RichEdit を作り、TSF を起こしてメッセージを回し、閉じられたら TSF を止める。
    fn run_window(rec: tsf::Recorder) -> windows::core::Result<i32> {
        // ★ 窓（RichEdit）を作る前にシンクを登録する（フォーカスの通知を取りこぼさない）。
        let tsf = tsf::Tsf::start(rec.clone())?;
        // SAFETY: Win32 の窓の作成とメッセージループ。この関数の中（1 スレッド）で完結する。
        let result = unsafe {
            (|| -> windows::core::Result<i32> {
                let hinstance: HINSTANCE = GetModuleHandleW(PCWSTR::null())?.into();
                // Load only from the system directory, not the working directory or the
                // executable's own folder, so a same-named file placed there cannot be loaded
                // instead of the intended system library.
                LoadLibraryExW(w!("Msftedit.dll"), None, LOAD_LIBRARY_SEARCH_SYSTEM32)?;
                let class_name = w!("GseRefInputTsf");
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
                    w!("refinput_tsf (gt/1 win_tsf)"),
                    WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU,
                    CW_USEDEFAULT,
                    CW_USEDEFAULT,
                    640,
                    240,
                    None,
                    None,
                    hinstance,
                    None,
                )?;
                // ★ 道 1: TSF 対応のコントロール（RichEdit）を載せる。TSF の文書はこのコントロールが持つ。
                let edit = match CreateWindowExW(
                    WS_EX_CLIENTEDGE,
                    MSFTEDIT_CLASS,
                    PCWSTR::null(),
                    WS_CHILD
                        | WS_VISIBLE
                        | WS_VSCROLL
                        | WINDOW_STYLE((ES_MULTILINE | ES_AUTOVSCROLL) as u32),
                    10,
                    10,
                    600,
                    150,
                    hwnd,
                    None,
                    hinstance,
                    None,
                ) {
                    Ok(edit) => edit,
                    Err(err) => {
                        // Clean up the parent window created above instead of leaking it.
                        // SAFETY: `hwnd` was just created by this function and is not used
                        // again on this path.
                        let _ = DestroyWindow(hwnd);
                        return Err(err);
                    }
                };
                // TSF を使う指定（既定でも使うが、はっきりさせる）
                SendMessageW(
                    edit,
                    EM_SETEDITSTYLE,
                    WPARAM(SES_USECTF as usize),
                    LPARAM(SES_USECTF as isize),
                );
                let _ = ShowWindow(hwnd, SW_SHOW);
                let _ = UpdateWindow(hwnd);
                let _ = SetFocus(edit);

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
                    // ★ キーの種類（`vk`）だけを、コントロールに渡す前に書く（文字は取らない）。
                    if msg.message == WM_KEYDOWN {
                        rec(Ev::KeyDown {
                            vk: msg.wParam.0 as u32,
                        });
                    }
                    let _ = TranslateMessage(&msg);
                    DispatchMessageW(&msg);
                }
            })()
        };
        tsf.stop();
        result
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

    /// selftest が書く代表的な列。TSF を起こさず、状態遷移（`CompTracker`）に観測を流して事象を得る。
    /// 変換 1 回（開始 → 更新 → 候補窓 → 確定）と、取消 1 回。時刻は決め打ち。
    fn selftest_events() -> Vec<Ev> {
        let cand = UiKind::Candidate;
        let mut t = CompTracker::default();
        let mut evs = vec![Ev::FocusIn, Ev::KeyDown { vk: 0xE5 }];
        evs.extend(t.observe(Some((1, 0, 1)), Some(1)));
        evs.extend(t.observe(Some((2, 0, 1)), Some(2)));
        evs.push(Ev::UiBegin { kind: cand });
        evs.push(Ev::UiUpdate { kind: cand });
        evs.extend(t.observe(Some((2, 0, 1)), Some(2)));
        evs.push(Ev::UiEnd { kind: cand });
        // 確定: composition が消え、文字は文書に残る（文書末は 2 のまま）
        evs.extend(t.observe(None, Some(2)));
        evs.push(Ev::KeyDown { vk: 0xE5 });
        evs.extend(t.observe(Some((3, 2, 1)), Some(5)));
        // 取消: composition の文字も文書から消える（5 → 2）
        evs.extend(t.observe(None, Some(2)));
        evs.push(Ev::UiBegin {
            kind: UiKind::Reading,
        });
        evs.push(Ev::UiEnd {
            kind: UiKind::Reading,
        });
        evs.push(Ev::UiBegin {
            kind: UiKind::Other,
        });
        evs.push(Ev::UiEnd {
            kind: UiKind::Other,
        });
        evs.push(Ev::FocusOut);
        evs
    }

    /// 核を通して書き、読み戻して検査する。⚠️ 通ったこと ≠ 実 IME で通知が届くこと（M5 で確かめる）。
    fn selftest(path: &Path) -> bool {
        let events = selftest_events();
        // 状態遷移が確定と取消を区別できている（`tsf_end` が 2 回・長さが 2 と 0）
        let ends: Vec<Option<u32>> = events
            .iter()
            .filter_map(|e| match e {
                Ev::TsfEnd { result_len } => Some(*result_len),
                _ => None,
            })
            .collect();
        if ends != vec![Some(2), Some(0)] {
            return false;
        }
        let mut lines = vec![header(Src::WinTsf, APP_VERSION)];
        for (i, ev) in events.into_iter().enumerate() {
            let i = i as u64;
            lines.push(line(
                ev,
                1_700_000_000_000 + i * 10,
                1_000_000_000 + i * 10_000_000,
            ));
        }
        // ★ 生ログと同じく、selftest も既にある出力先を上書きしない。
        let written = OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(path)
            .and_then(|mut f| {
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
        let head_ok = it.next().is_some_and(|h| {
            h.contains("\"kind\":\"header\"")
                && h.contains("\"src\":\"win_tsf\"")
                && check_line(h).is_ok()
        });
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
                        "refinput_tsf_selftest_{}.jsonl",
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
        if append(&mut file, &header(Src::WinTsf, APP_VERSION)).is_err() {
            return ExitCode::from(1);
        }
        let failed = Rc::new(Cell::new(false));
        let rec = make_recorder(file, failed.clone());
        match run_window(rec) {
            Ok(_) if !failed.get() => ExitCode::SUCCESS,
            _ => ExitCode::from(1),
        }
    }
}
