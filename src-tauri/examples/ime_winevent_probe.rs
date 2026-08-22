//! IME WinEvent の到達を実機で確かめる診断ツール（★ 配布ビルドには入らない）。
//!
//! ⚠️★★★ **これは計器ではない。** `cargo run --example` でしか動かず、
//! `cargo build --release` にも tauri のバンドルにも含まれない。
//!
//! ## 何を答えるためのものか（★ 3 つの問いを 1 回で閉じる）
//!
//! | # | 問い | ★ どう答えるか |
//! |---|---|---|
//! | 1 | ⚠️ `WINEVENT_SKIPOWNPROCESS` が **GSE 自身の画面での入力**を落としてしまわないか | ★ **SKIP 有り / 無しの 2 本**を同時に張り、到達数を比べる |
//! | 2 | ★ `EVENT_OBJECT_TEXTEDIT_CONVERSIONTARGETCHANGED`(0x8030) が**実際に飛ぶか** | ★ 範囲を `0x8027..=0x8030` にして**イベント別に数える** |
//! | **3** | ⭐★★★ **`is_ime_candidate_window_visible()` (EnumWindows 経路) は効くか** | ★ **本番の関数そのもの**を 25ms で叩き、検出率と遷移回数を数える |
//!
//! ⚠️★★★ **問い 3 が本命** (2026-08-22 の実測で IME WinEvent は 0 件だったため)。
//! ★ `IME_ACTIVE` の駆動源を WinEvent から EnumWindows へ移せるかどうかは、**この数字だけ**で決める。
//! ⚠️ プローブ側に検出ロジックを**複製しない** —— 複製を測っても本番経路の可否は答えられない。
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
//! ★ 記録するのは **イベント ID・件数・ウィンドウクラス名**だけ。
//! ⚠️ **ウィンドウタイトル (`GetWindowTextW`) は取得しない。** PID は「自分と同じか」の
//! **bool 判定にだけ**使い、値は出力しない。
//!
//! ⚠️★★★ **クラス名は「プロセス名を含まない」とは言い切れない** (2026-08-22・security review)。
//! ★ **WPF** はトップレベル窓を `HwndWrapper[<AppDomain 名>;;<GUID>]` で登録し、
//! **AppDomain 名は通常 実行ファイル名** (例 `devenv.exe`) である。
//! ★ **WinForms** も `WindowsForms10.Window.8.app.0.<hash>` の形でアプリ固有の識別子を含む。
//! → ★ そこで **出力前に [`normalize_class_name`] で正規化する** (角括弧以降を落とし、
//! WinForms は先頭 2 セグメントに切る)。⚠️ **生のクラス名は保存も出力もしない。**
//!
//! ⚠️★★★ **正規化は万能ではない** (2026-08-22・cross-review 中)。
//! ★ WPF/WinForms 以外にも、任意のアプリが**アプリ名・ユーザー名・拡張機能名・社内識別子**を
//! クラス名に入れうる。⚠️ **allowlist 化もハッシュ化もしていない。**
//! → ★★★ **本ツールの出力は「ローカルで研究者が読むもの」である。**
//! ⚠️ **repo / gse-dataset / 外部 LLM へ貼る前に、必ず目で見てレビューすること。**
//! ★ 出力は可視ウィンドウクラスの一覧を含み、**利用中アプリの指紋になりうる**。
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
    use std::collections::{BTreeMap, BTreeSet};
    use std::io::Write;
    use std::sync::atomic::AtomicU64;
    use std::sync::atomic::{AtomicU32, Ordering};
    use std::sync::{Mutex, OnceLock};
    use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

    use windows::Win32::Foundation::{BOOL, HWND, LPARAM, LRESULT, WPARAM};
    use windows::Win32::System::Com::{
        CoCreateInstance, CoInitializeEx, CLSCTX_INPROC_SERVER, COINIT_MULTITHREADED,
    };
    use windows::Win32::System::Threading::GetCurrentProcessId;
    use windows::Win32::UI::Accessibility::{
        CUIAutomation, IUIAutomation, SetWinEventHook, UIA_TextChildPatternId,
        UIA_TextEditPatternId, UIA_TextPatternId, UnhookWinEvent, HWINEVENTHOOK,
    };
    use windows::Win32::UI::Input::Ime::{ImmGetContext, ImmGetOpenStatus, ImmReleaseContext};
    use windows::Win32::UI::WindowsAndMessaging::{
        CallNextHookEx, DispatchMessageW, EnumWindows, GetClassNameW, GetForegroundWindow,
        GetWindowThreadProcessId, IsWindowVisible, PeekMessageW, SetWindowsHookExW,
        UnhookWindowsHookEx, EVENT_OBJECT_CLOAKED, EVENT_OBJECT_CREATE, EVENT_OBJECT_HIDE,
        EVENT_OBJECT_IME_CHANGE, EVENT_OBJECT_IME_HIDE, EVENT_OBJECT_IME_SHOW, EVENT_OBJECT_SHOW,
        EVENT_OBJECT_TEXTEDIT_CONVERSIONTARGETCHANGED, EVENT_OBJECT_UNCLOAKED, HHOOK, MSG,
        PM_REMOVE, WH_KEYBOARD_LL, WM_KEYDOWN, WM_SYSKEYDOWN,
    };

    /// ⚠️★★★ **CREATE / SHOW / HIDE したウィンドウのクラス名**（★ 2026-08-22 追加）。
    ///
    /// ★ なぜ足したか: 初回計測で `CREATE 583 = DESTROY 583` と**確かに何かが出入りしている**のに、
    /// クラス名センサスには**常時可視の 2 クラスしか写らなかった**。
    /// ⚠️ センサスが `looks_ime_like` で**絞ってから**数えていたため、
    /// 候補ウィンドウのクラス名がその語に当たらなければ**構造的に見えない**。
    /// → ★ **絞らずに、イベントで捕まえた瞬間のクラス名をそのまま数える。**
    ///
    /// ★ これはポーリングより**取りこぼしにくい**: 候補ウィンドウが 100ms 未満で
    /// 生成・破棄されても、CREATE/SHOW はイベントとして届きうる。
    ///
    /// ⚠️★★★ **ただし「必ず捕まる」とは言えない** (2026-08-22・cross-review 高)。
    /// ★ `WINEVENT_OUTOFCONTEXT` の配送は**非同期**で、到達時に窓が消えていれば
    /// `GetClassNameW` が失敗する ([`N_EVENT_CLASS_UNAVAIL`] で数える)。
    /// ⚠️ さらに本ツールはメッセージポンプと `EnumWindows` が**同じスレッド**なので、
    /// 負荷次第で配送が遅れうる。→ ★ **0 件を主張する前に `N_EVENT_CLASS_UNAVAIL` を見ること。**
    ///
    /// ⚠️ **privacy**: ★ クラス名のみ ([`normalize_class_name`] で正規化)。
    /// ⚠️ ウィンドウタイトルは取得しない。
    ///
    /// ⚠️★★★ **この形を本番 (`src/input/`) へ持ち込んではならない。**
    /// ★ WinEvent コールバック内で `format!` (ヒープ確保) と `Mutex::lock()` を行っており、
    /// `hook-constraints` **Win-1** (コールバック内は Atomic ＋ `try_send` のみ) に反する。
    /// ★ ここで許されるのは **プローブ専用**だからである
    /// (⚠️ 本番へ配線するなら HWND を `try_send` し、別スレッドでクラス名を解決すること)。
    #[allow(clippy::type_complexity)]
    fn event_classes() -> &'static Mutex<BTreeMap<(&'static str, String), u32>> {
        static MAP: OnceLock<Mutex<BTreeMap<(&'static str, String), u32>>> = OnceLock::new();
        MAP.get_or_init(|| Mutex::new(BTreeMap::new()))
    }

    /// ★ EnumWindows 経路を叩く間隔。⚠️ **本番 (`lib.rs` の IME Monitor) は 100ms** だが、
    /// ★ ここでは 25ms で取って「**本番の 100ms では取りこぼすか**」を別途換算する。
    const ENUM_PERIOD_MS: u32 = 25;
    /// ★ 本番相当の間引き (25ms × 4 = 100ms)。
    const ENUM_PROD_DIVISOR: u32 = 4;

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

    /// ⚠️★★★ **生存確認チャネル**（`0x8000..=0x8030` の全オブジェクトイベント）。
    ///
    /// ★ キャレットの点滅やウィンドウ移動で**常時発火する**ので、
    /// **「フックは生きているのに IME イベントだけ来ない」**と
    /// **「そもそもフックが 1 件も配送していない」**を区別できる。
    /// ⚠️ これが 0 なら測定は**不成立**であり、「0x8030 が出ない」とは言えない。
    static N_ALIVE: AtomicU32 = AtomicU32::new(0);

    /// ⚠️★★★ **オブジェクトイベントのヒストグラム**（`0x8000..=0x8030`）。
    ///
    /// ★ 「IME イベントが 0」のとき、**その IME が代わりに何を出しているか**を見る。
    /// ⚠️ 現代の Windows 11 IME は候補 UI を別プロセス（Windows Input Experience）で
    /// 描画するため、**MSAA の `EVENT_OBJECT_IME_*` を上げない可能性がある**。
    const HIST_MIN: u32 = 0x8000;
    const HIST_MAX: u32 = 0x8030;
    const HIST_LEN: usize = (HIST_MAX - HIST_MIN + 1) as usize;
    #[allow(clippy::declare_interior_mutable_const)]
    const ZERO: AtomicU32 = AtomicU32::new(0);
    static HIST: [AtomicU32; HIST_LEN] = [ZERO; HIST_LEN];

    /// ★ `ImmGetOpenStatus` のポーリング結果。
    /// ⚠️ 「日本語モードだったか」を独立に確かめる（★ 打っていなかった可能性を潰す）。
    static N_IMM_POLL: AtomicU32 = AtomicU32::new(0);
    static N_IMM_OK: AtomicU32 = AtomicU32::new(0);
    static N_IMM_OPEN: AtomicU32 = AtomicU32::new(0);

    static OUR_PID: AtomicU32 = AtomicU32::new(0);

    /// ⚠️★★★ **UIA プロバイダの「起こし」統計** (2026-08-22 追加)。
    ///
    /// ★ **なぜ要るか**: `EVENT_OBJECT_TEXTEDIT_CONVERSIONTARGETCHANGED`(0x8030) の
    /// 発火主体は IME ではなく **アプリ側の UIA プロバイダ**である
    /// (逐語「required to be raised by Microsoft UI Automation elements supporting
    /// the TextEdit pattern」)。
    /// ⚠️ **Chromium 系 (Chrome / WebView2) はアクセシビリティツリーを遅延生成する**ので、
    /// WinEvent フックを張っただけでは **プロバイダが起きず、0 件が「出ない」なのか
    /// 「起こしていない」なのか区別できない**。
    /// → ★ `accevent.exe` が本物の UIA クライアントとして行っていることを、ここで再現する。
    static N_UIA_POKE: AtomicU32 = AtomicU32::new(0);
    /// ★ `ElementFromHandle` が要素を返した回数 (＝ プロバイダが応答した)。
    static N_UIA_ELEMENT_OK: AtomicU32 = AtomicU32::new(0);
    /// ★★★ **テキスト系パターンが取れた回数** —— ⚠️ これが 0 なら、
    /// そのアプリには **テキストプロバイダが無い**ので 0x8030 は原理的に出ない。
    static N_UIA_TEXT_OK: AtomicU32 = AtomicU32::new(0);
    /// ★ `TextEdit` パターンが取れた回数 (⚠️ 0x8030 を上げる資格そのもの)。
    static N_UIA_TEXTEDIT_OK: AtomicU32 = AtomicU32::new(0);

    /// ⚠️★★★ **フォーカス要素側**のパターン統計 (2026-08-22 訂正で追加)。
    ///
    /// ⚠️ **初版は トップレベル窓の要素にだけパターンを要求して数えていた。これは誤り。**
    /// ★ `ElementFromHandle(hwnd)` が返すのは **ブラウザのフレーム**であり、
    /// `TextPattern` は**その内側の入力欄**に付く。
    /// → ⚠️ **フレームに Text が無いのは正常**で、「アプリにテキストプロバイダが無い」証拠にならない。
    /// ★ 判定に使えるのは **フォーカス要素側**である。
    static N_UIA_FOCUS_OK: AtomicU32 = AtomicU32::new(0);
    static N_UIA_FOCUS_TEXT_OK: AtomicU32 = AtomicU32::new(0);
    static N_UIA_FOCUS_TEXTEDIT_OK: AtomicU32 = AtomicU32::new(0);

    /// ⚠️★★★ **打鍵数** —— ★ 「入力が実際に行われたか」の**唯一信頼できる指標** (2026-08-22 訂正)。
    ///
    /// ⚠️ **初版は `TEXTSELECTIONCHANGED`/`VALUECHANGE` を入力の証拠に使ったが、これは誤り。**
    /// ★ どちらも**アプリ依存**で、Notepad のような RichEdit 系は打鍵ごとには上げない。
    /// → ⚠️ **実際に日本語を打った 60 秒が「入力なし」と判定される**事故が起きた
    ///    (★ `VALUECHANGE=2` で 60 秒間不動)。
    ///
    /// ★ **打鍵は `WH_KEYBOARD_LL` で直接数える。** アプリに依存しない。
    ///
    /// ⚠️ **privacy**: ★ **数えるだけ。** ⚠️ `KBDLLHOOKSTRUCT` を**一切参照しない**ので、
    /// ★★★ **どのキーを押したかはプロセス内に一度も現れない** (content-free が構造的)。
    static N_KEYS: AtomicU32 = AtomicU32::new(0);

    /// ⚠️★★★ **v0.1.27 以前の `IME_ACTIVE` 駆動をそのまま再現する状態**。
    ///
    /// ★ 旧コードは `IME_SHOW=0x8017`(=`CLOAKED`) で **単一のグローバル**
    /// `IME_COMPOSITION_START_MS` を刻み、`IME_HIDE=0x8018`(=`UNCLOAKED`) で
    /// `dwell = now - start` を計算していた (⚠️ **HWND 別ではない。last-writer-wins**)。
    /// → ★★★ **ここで同じことをすれば、当時 `ime_dwell_med` に何が入っていたかが直接見える。**
    static LEGACY_START_MS: AtomicU64 = AtomicU64::new(0);

    /// ⚠️★★★ **直近の打鍵時刻 (epoch ms)**。★ cloak が「変換中」に起きたか「無操作中」に起きたかを分ける。
    static LAST_KEY_MS: AtomicU64 = AtomicU64::new(0);

    /// ★ 「打鍵の近く」とみなす閾値。⚠️ 変換は打鍵の直後に起きるので、
    /// これを超えて離れた cloak は **変換とは無関係** = false positive 候補である。
    const NEAR_KEY_MS: u64 = 2000;

    /// ⚠️★★★ **クラス別 cloak 統計** —— ★ C の 2 つの問いに答えるためのもの。
    ///
    /// 問い 1: ⚠️ **変換していないときに `IME` が cloak されないか** (false positive の確認)
    /// 問い 2: ★ 34 = 17 × 2 の内訳 (dwell の分布に 2 山が出るか)
    #[derive(Default, Clone)]
    struct CloakStat {
        cloaks: u32,
        uncloaks: u32,
        /// ★ 直近打鍵から `NEAR_KEY_MS` 以内に起きた cloak
        near_key: u32,
        /// ⚠️ 打鍵から離れて起きた cloak (★ **これが false positive 候補**)
        far_key: u32,
        /// ★ 未確定の cloak 開始時刻 (クラス単位の近似)
        pending: u64,
        /// ★ cloak → uncloak の滞在時間
        dwells: Vec<u64>,
    }

    #[allow(clippy::type_complexity)]
    fn cloak_stats() -> &'static Mutex<BTreeMap<String, CloakStat>> {
        static M: OnceLock<Mutex<BTreeMap<String, CloakStat>>> = OnceLock::new();
        M.get_or_init(|| Mutex::new(BTreeMap::new()))
    }

    /// ★ 再現した「旧 `ime_shadow`」の dwell 列 (ms)。
    fn legacy_dwells() -> &'static Mutex<Vec<u64>> {
        static V: OnceLock<Mutex<Vec<u64>>> = OnceLock::new();
        V.get_or_init(|| Mutex::new(Vec::new()))
    }

    fn now_ms() -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as u64
    }

    /// ⚠️ `WH_KEYBOARD_LL` コールバック。★ Atomic の加算と `CallNextHookEx` のみ
    /// (`hook-constraints` Win-1 準拠)。
    unsafe extern "system" fn keyboard_hook(code: i32, wparam: WPARAM, lparam: LPARAM) -> LRESULT {
        if code >= 0 {
            let msg = wparam.0 as u32;
            if msg == WM_KEYDOWN || msg == WM_SYSKEYDOWN {
                // ⚠️★ lparam (KBDLLHOOKSTRUCT) には**触れない**。★ 数えるだけ。
                N_KEYS.fetch_add(1, Ordering::Relaxed);
                LAST_KEY_MS.store(now_ms(), Ordering::Relaxed);
            }
        }
        // ★ Win-2: どの経路でも必ず呼ぶ。
        CallNextHookEx(None, code, wparam, lparam)
    }

    /// ⚠️ **診断B 側**で `GetClassNameW` がクラス名を返せなかった回数。
    ///
    /// ★ **なぜ数えるか**: WinEvent の `WINEVENT_OUTOFCONTEXT` 配送は**非同期**なので、
    /// コールバック到達時に窓が既に破棄されていると必ずここに落ちる。
    /// ⚠️★★★ ＝ **短命な窓ほど系統的に取りこぼす**。★ 0 でない限り「診断B は全数だ」と言えない。
    static N_EVENT_CLASS_UNAVAIL: AtomicU32 = AtomicU32::new(0);

    /// ⚠️ **診断A (センサス) 側**で `GetClassNameW` が失敗した回数。
    ///
    /// ⚠️★★★ **診断B と混ぜてはならない** (2026-08-22・cross-review 高)。
    /// ★ こちらは列挙中に窓が消えた等であり、**「短命な窓の取りこぼし」の根拠にはならない**。
    /// ⚠️ 1 つのカウンタで両方を数えると、出力の意味が混ざって結論を誤らせる。
    static N_CENSUS_CLASS_UNAVAIL: AtomicU32 = AtomicU32::new(0);

    /// ⚠️★★★ **クラス名からアプリ固有の識別子を落とす** (2026-08-22・security review)。
    ///
    /// ★ **WPF**: `HwndWrapper[<AppDomain 名>;;<GUID>]` —— **AppDomain 名は通常 実行ファイル名**。
    /// ★ **WinForms**: `WindowsForms10.Window.8.app.0.<hash>` —— アプリ固有の hash を含む。
    /// → ⚠️ **生値をそのまま出すと「プロセス名を記録しない」という前提が崩れる。**
    ///
    /// ★ 落とし方は保守的に 2 手だけ: (i) 最初の `[` 以降を捨てる /
    /// (ii) `WindowsForms` 始まりは先頭 2 セグメントに切る。
    fn normalize_class_name(class: &str) -> String {
        let head = class.split('[').next().unwrap_or(class);
        if head.starts_with("WindowsForms") {
            return head.split('.').take(2).collect::<Vec<_>>().join(".");
        }
        head.to_string()
    }

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

    /// ★ 生存確認 ＋ イベント ID のヒストグラム ＋ **CREATE/SHOW/HIDE のクラス名**。
    unsafe extern "system" fn cb_alive(
        _h: HWINEVENTHOOK,
        event: u32,
        hwnd: HWND,
        id_object: i32,
        id_child: i32,
        _t: u32,
        _ms: u32,
    ) {
        N_ALIVE.fetch_add(1, Ordering::Relaxed);
        if (HIST_MIN..=HIST_MAX).contains(&event) {
            HIST[(event - HIST_MIN) as usize].fetch_add(1, Ordering::Relaxed);
        }

        // ⚠️ **ウィンドウ本体のイベントだけ**に絞る (OBJID_WINDOW=0 / CHILDID_SELF=0)。
        // ★ これを付けないとキャレットやリストアイテムの子オブジェクトで水増しされる。
        // ⚠️★★★ **旧 v0.1.27 の駆動をそのまま再現する。**
        // ★ 旧コードは HWND を見ずグローバル 1 個で start/dwell を回していた (last-writer-wins)。
        if event == EVENT_OBJECT_CLOAKED {
            LEGACY_START_MS.store(now_ms(), Ordering::Relaxed);
        } else if event == EVENT_OBJECT_UNCLOAKED {
            let start = LEGACY_START_MS.swap(0, Ordering::Relaxed);
            if start > 0 {
                let d = now_ms().saturating_sub(start);
                if let Ok(mut v) = legacy_dwells().lock() {
                    v.push(d);
                }
            }
        }

        let is_window_level = id_object == 0 && id_child == 0;
        let is_lifecycle = event == EVENT_OBJECT_CREATE
            || event == EVENT_OBJECT_SHOW
            || event == EVENT_OBJECT_HIDE
            || event == EVENT_OBJECT_CLOAKED
            || event == EVENT_OBJECT_UNCLOAKED;
        if !is_window_level || !is_lifecycle || hwnd.0.is_null() {
            return;
        }

        let mut buf = [0u16; 256];
        // SAFETY: hwnd は OS がコールバックへ渡したもの。buf は自前のスタック配列。
        let len = GetClassNameW(hwnd, &mut buf);
        if len <= 0 {
            // ⚠️ 配送が非同期なので、到達時に窓が消えているとここに来る。★ 黙って捨てない。
            N_EVENT_CLASS_UNAVAIL.fetch_add(1, Ordering::Relaxed);
            return;
        }
        let class = normalize_class_name(&String::from_utf16_lossy(&buf[..len as usize]));
        let tag = if event == EVENT_OBJECT_CREATE {
            "CREATE"
        } else if event == EVENT_OBJECT_SHOW {
            "SHOW"
        } else if event == EVENT_OBJECT_HIDE {
            "HIDE"
        } else if event == EVENT_OBJECT_CLOAKED {
            "CLOAK"
        } else {
            "UNCLOAK"
        };
        // ⚠️★★★ クラス別 cloak 統計 (★ C の実測)。
        if event == EVENT_OBJECT_CLOAKED || event == EVENT_OBJECT_UNCLOAKED {
            let t = now_ms();
            let since_key = t.saturating_sub(LAST_KEY_MS.load(Ordering::Relaxed));
            if let Ok(mut m) = cloak_stats().lock() {
                let e = m.entry(class.clone()).or_default();
                if event == EVENT_OBJECT_CLOAKED {
                    e.cloaks += 1;
                    if since_key <= NEAR_KEY_MS {
                        e.near_key += 1;
                    } else {
                        e.far_key += 1;
                    }
                    e.pending = t;
                } else {
                    e.uncloaks += 1;
                    if e.pending > 0 {
                        e.dwells.push(t.saturating_sub(e.pending));
                        e.pending = 0;
                    }
                }
            }
        }

        // ⚠️ ロックはこの中で完結させる (★ DispatchMessageW を跨いで保持しない)。
        if let Ok(mut map) = event_classes().lock() {
            *map.entry((tag, class)).or_insert(0) += 1;
        }
    }

    /// ⚠️ 前面ウィンドウの IME モードを 1 回ポーリングする。
    ///
    /// ★ `ime_windows.rs` と同じ手（`ImmGetContext` → `ImmGetOpenStatus`）。
    /// ⚠️ 他プロセスのウィンドウでは NULL が返ることが分かっているので、
    /// **成功回数と open 回数を別々に数える**（★ 「取れなかった」と「閉じていた」を混ぜない）。
    fn poll_imm() {
        N_IMM_POLL.fetch_add(1, Ordering::Relaxed);
        // SAFETY: いずれも読み取り専用。himc は同じ hwnd で必ず release する。
        unsafe {
            let hwnd = GetForegroundWindow();
            if hwnd.0.is_null() {
                return;
            }
            let himc = ImmGetContext(hwnd);
            if himc.0.is_null() {
                return;
            }
            N_IMM_OK.fetch_add(1, Ordering::Relaxed);
            if ImmGetOpenStatus(himc).as_bool() {
                N_IMM_OPEN.fetch_add(1, Ordering::Relaxed);
            }
            let _ = ImmReleaseContext(hwnd, himc);
        }
    }

    /// ⚠️★★★ **入力が実際に行われたかの独立確認** (2026-08-22 追加)。
    ///
    /// ★ `alive` は「フックが生きているか」しか答えない。
    /// ⚠️★★★ **「被験者が本当に文字を入力したか」は別の問い**であり、初版は出していなかった。
    /// → ⚠️ **入力が無かった 60 秒の 0 件を「0x8030 は出ない」と読む事故**が実際に起きた。
    ///
    /// ★ 使うのは `EVENT_OBJECT_TEXTSELECTIONCHANGED`(0x8014) と
    /// `EVENT_OBJECT_VALUECHANGE`(0x800E)。★ どちらも**文字が入力欄に入ると飛ぶ**。
    /// ⚠️ 引数に文字列は無く content-free である。
    fn typing_evidence() -> (u32, u32) {
        let sel = HIST[(0x8014 - HIST_MIN) as usize].load(Ordering::Relaxed);
        let val = HIST[(0x800E - HIST_MIN) as usize].load(Ordering::Relaxed);
        (sel, val)
    }

    /// ⚠️★★★ **AccEvent 相当 — UIA プロバイダを起こす。**
    ///
    /// ★ 前面ウィンドウに対して `ElementFromHandle` を呼ぶと `WM_GETOBJECT` が飛び、
    /// **Chromium はその時点でアクセシビリティを有効化する**。
    /// ★ さらに **Text / TextEdit / TextChild パターンを要求**してテキスト系まで上げる
    /// (⚠️ Chromium の AXMode は段階的に上がるため、要素を取るだけでは足りない)。
    ///
    /// ⚠️ **privacy**: ★ パターンを **要求するだけ**で、
    /// ⚠️ `TextPattern::DocumentRange` も `GetText()` も **呼ばない** ——
    /// ★★★ **本文を 1 文字も読まない。** 数えるのは「取れたか」の bool だけである。
    fn poke_uia_provider(automation: &IUIAutomation) {
        N_UIA_POKE.fetch_add(1, Ordering::Relaxed);
        // SAFETY: いずれも読み取り専用の COM 呼び出し。返る interface は Drop で解放される。
        unsafe {
            let hwnd = GetForegroundWindow();
            if hwnd.0.is_null() {
                return;
            }
            if let Ok(element) = automation.ElementFromHandle(hwnd) {
                N_UIA_ELEMENT_OK.fetch_add(1, Ordering::Relaxed);
                if element.GetCurrentPattern(UIA_TextPatternId).is_ok() {
                    N_UIA_TEXT_OK.fetch_add(1, Ordering::Relaxed);
                }
                if element.GetCurrentPattern(UIA_TextEditPatternId).is_ok() {
                    N_UIA_TEXTEDIT_OK.fetch_add(1, Ordering::Relaxed);
                }
            }
            // ⚠️★★★ **判定に使うのはこちら。** ★ フォーカス要素が実際の入力欄である。
            if let Ok(focused) = automation.GetFocusedElement() {
                N_UIA_FOCUS_OK.fetch_add(1, Ordering::Relaxed);
                if focused.GetCurrentPattern(UIA_TextPatternId).is_ok() {
                    N_UIA_FOCUS_TEXT_OK.fetch_add(1, Ordering::Relaxed);
                }
                if focused.GetCurrentPattern(UIA_TextEditPatternId).is_ok() {
                    N_UIA_FOCUS_TEXTEDIT_OK.fetch_add(1, Ordering::Relaxed);
                }
                // ★ TextChild は「テキストの子孫である」ことを示す。要求のみ (数えない)。
                let _ = focused.GetCurrentPattern(UIA_TextChildPatternId);
            }
        }
    }

    /// ⚠️★★★ **絞らずに**、可視トップレベルウィンドウのクラス名を**全部**数える。
    ///
    /// ⚠️ ★ 2026-08-22 の初回計測では `looks_ime_like` で**絞ってから**数えていた。
    /// → **候補ウィンドウのクラス名がその語に当たらなければ最初から見えない**という
    /// 構造的な盲点があり、「0 件」を「候補ウィンドウが無い」の根拠にできなかった。
    /// ★ いまは全件数え、`looks_ime_like` は**印を付けるだけ**に降格した。
    ///
    /// ★ これがある理由: 問い 3 が **0 件だったとき**に
    /// 「**候補ウィンドウがそもそも無い**」のか
    /// 「**候補ウィンドウはあるが `is_ime_candidate_class_name` の網 (`Candidate` 部分一致)
    /// が細すぎて漏れている**」のかを区別するため。
    /// ⚠️ 前者なら B は不成立だが、後者なら**網を広げれば成立する**——結論が正反対になる。
    ///
    /// ⚠️ **privacy**: ★ `GetClassNameW` の**クラス名のみ**を、
    /// [`normalize_class_name`] で**正規化してから**数える (⚠️ WPF/WinForms はクラス名に
    /// 実行ファイル名を埋め込むため・モジュール doc 参照)。
    /// ⚠️ ウィンドウタイトルは取得しない。
    fn census_visible_classes(map: &mut BTreeMap<String, u32>) {
        unsafe extern "system" fn cb(hwnd: HWND, lparam: LPARAM) -> BOOL {
            if !IsWindowVisible(hwnd).as_bool() {
                return BOOL(1);
            }
            let mut buf = [0u16; 256];
            let len = GetClassNameW(hwnd, &mut buf);
            if len > 0 {
                // SAFETY: lparam は直下の EnumWindows 呼び出しで渡した `&mut BTreeSet`
                // そのもの。列挙は呼び出しスレッドで同期的に走るので借用は生きており、
                // 他スレッドからの同時アクセスも無い。
                let seen = &mut *(lparam.0 as *mut BTreeSet<String>);
                seen.insert(normalize_class_name(&String::from_utf16_lossy(
                    &buf[..len as usize],
                )));
            } else {
                N_CENSUS_CLASS_UNAVAIL.fetch_add(1, Ordering::Relaxed);
            }
            BOOL(1)
        }

        // ⚠️★ **1 ポーリング内で重複排除する。** ★ 同じクラスの窓が N 個あっても 1 と数える。
        // ⚠️ そうしないと `Chrome_WidgetWin_1 4800/600` のように分母を超え、
        // 「600/600 は常時可視」という凡例と矛盾して読者を誤らせる。
        let mut seen: BTreeSet<String> = BTreeSet::new();
        // SAFETY: `seen` はこの呼び出しの間だけ生きている有効な参照。
        unsafe {
            let _ = EnumWindows(
                Some(cb),
                LPARAM(&mut seen as *mut BTreeSet<String> as isize),
            );
        }
        for class in seen {
            *map.entry(class).or_insert(0) += 1;
        }
    }

    #[cfg(test)]
    mod tests {
        use super::normalize_class_name;

        /// ★ 実行: `cargo test --example ime_winevent_probe`
        /// (⚠️ 既定の `cargo test` は example 内の `#[test]` を **実行しない**。コンパイルのみ)
        #[test]
        fn wpf_class_drops_appdomain_and_guid() {
            // ⚠️★★★ AppDomain 名は通常 **実行ファイル名**。★ 落とせていないと privacy 前提が崩れる。
            assert_eq!(
                normalize_class_name(
                    "HwndWrapper[devenv.exe;;a1b2c3d4-0000-1111-2222-333344445555]"
                ),
                "HwndWrapper"
            );
        }

        #[test]
        fn winforms_class_keeps_only_two_segments() {
            assert_eq!(
                normalize_class_name("WindowsForms10.Window.8.app.0.141b42a_r6_ad1"),
                "WindowsForms10.Window"
            );
        }

        #[test]
        fn ordinary_class_is_unchanged() {
            assert_eq!(
                normalize_class_name("Chrome_WidgetWin_1"),
                "Chrome_WidgetWin_1"
            );
            assert_eq!(normalize_class_name("Notepad"), "Notepad");
            // ★ ドットを含むが WinForms ではないものは切らない。
            assert_eq!(
                normalize_class_name("Windows.UI.Core.CoreWindow"),
                "Windows.UI.Core.CoreWindow"
            );
        }

        #[test]
        fn degenerate_inputs_do_not_panic() {
            assert_eq!(normalize_class_name(""), "");
            // ⚠️ 先頭が `[` = 角括弧より前が空。★ panic せず空を返す。
            assert_eq!(normalize_class_name("[whatever]"), "");
            // ⚠️ 閉じ括弧が無い壊れた形でも切る。
            assert_eq!(
                normalize_class_name("HwndWrapper[unterminated"),
                "HwndWrapper"
            );
            // ⚠️ WinForms 始まりでセグメントが 2 未満。
            assert_eq!(normalize_class_name("WindowsForms10"), "WindowsForms10");
        }
    }

    /// ⚠️ **意図的に本番 (`is_ime_candidate_class_name`) より広い。**
    /// ★ 本番は `Candidate` 部分一致のみ。ここは「IME っぽい」を広く拾って**診断**に使う。
    /// ⚠️ この関数を本番へ持ち込んではならない —— `MSCTFIME UI` (言語バー) を拾うため、
    /// そのまま使うと分析が永久停止する既知の事故を再発させる。
    fn looks_ime_like(class: &str) -> bool {
        let lower = class.to_ascii_lowercase();
        const NEEDLES: [&str; 8] = [
            "cand",             // CandidateUI / ...Candidate...  (★ 本番が見ているもの)
            "ime",              // MSCTFIME UI / IME / ...
            "msctf",            // TSF 系
            "tsf",              //
            "inputexperience",  // Windows Input Experience
            "textinput",        // TextInputHost
            "windows.ui.core",  // CoreWindow (UWP 候補 UI の実体)
            "applicationframe", // UWP のホストフレーム
        ];
        NEEDLES.iter().any(|needle| lower.contains(needle))
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
        // ⚠️★★★ 生存確認: これが 0 なら「IME が出ない」ではなく「測定不成立」である。
        let h_alive = unsafe {
            SetWinEventHook(
                HIST_MIN,
                HIST_MAX,
                None,
                Some(cb_alive),
                0,
                0,
                WINEVENT_OUTOFCONTEXT,
            )
        };

        if h_skip.is_invalid() || h_all.is_invalid() || h_alive.is_invalid() {
            // ⚠️★★★ 成功した分だけ外してから抜ける (★ 張りっぱなしにしない)。
            // SAFETY: 張ったスレッドと同じスレッドで外す。無効ハンドルは外さない。
            unsafe {
                for h in [h_skip, h_all, h_alive] {
                    if !h.is_invalid() {
                        let _ = UnhookWinEvent(h);
                    }
                }
            }
            // ⚠️★★★ `Ok(())` で返してはならない。
            // ★ 本ツールは **null 結果 (0 件) を根拠にする**ので、
            // 「測って 0 だった」と「そもそも測れなかった」が
            // **終了コードで区別できなければならない**。
            // ⚠️★ `anyhow` は使わない —— **このリポジトリは anyhow を依存に持たない**
            // (`overlay_panel.rs` 逐語「このリポジトリは anyhow を依存に持たず
            // Result<_,String>/tauri::Result」・`bin/replay.rs` も同旨)。
            return Err(std::io::Error::other(
                "SetWinEventHook に失敗した (★ 測定は不成立。0 件を根拠にしないこと)",
            ));
        }

        // ⚠️★★★ 打鍵カウント用の低レベルフック。★ 数えるだけで内容は見ない。
        // SAFETY: 同一スレッドで張り、同一スレッドで外す。メッセージループは下の PeekMessageW。
        let h_keys: HHOOK =
            unsafe { SetWindowsHookExW(WH_KEYBOARD_LL, Some(keyboard_hook), None, 0) }
                .unwrap_or_default();

        let started = Instant::now();
        let deadline = started + Duration::from_secs(60);
        let mut next_tick = started + Duration::from_secs(5);
        let mut next_imm = started;
        let mut next_enum = started;
        let mut next_census = started;
        let mut next_poke = started;
        let mut msg = MSG::default();

        // ---- 問い 3: EnumWindows 経路 (★ 本番の関数をそのまま叩く) ----
        // ★ 25ms 実測ぶん
        let mut enum_poll = 0u32;
        let mut enum_hit = 0u32;
        let mut enum_rise = 0u32;
        let mut enum_prev = false;
        let mut enum_tick = 0u32;
        // ★ 本番相当 (100ms) へ間引いたぶん。⚠️ 「25ms なら見えるが本番では見えない」を検出する。
        let mut prod_poll = 0u32;
        let mut prod_hit = 0u32;
        let mut prod_rise = 0u32;
        let mut prod_prev = false;
        // ★ 候補ウィンドウが開いていた時間 (25ms 刻みの近似)。
        let mut dwell_cur_ms = 0u32;
        let mut dwell_max_ms = 0u32;
        let mut dwell_total_ms = 0u32;
        // ★ 診断用クラス名センサス。
        let mut census: BTreeMap<String, u32> = BTreeMap::new();
        let mut census_polls = 0u32;

        // ⚠️★★★ **本番の完全な述語** `is_candidate_window_open()` (2026-08-22 追加)。
        //
        // ★ なぜ要るか: `is_ime_candidate_window_visible()` は **EnumWindows 経路だけ**であり、
        //   本番が実際に使うのは `WinEvent || EnumWindows || **UIAutomation**` の OR である。
        // ⚠️★★★ **UIA 経路だけ一度も測っていなかった** —— ★ EnumWindows が 0 でも
        //   UIA が拾っていれば `IME_ACTIVE` の配線は成立しうる。
        // → ★ **両方を同時に取り、差分を UIA の寄与として読む。**
        let monitor = gse_next_lib::input::ime::ImeMonitor::new();
        // ⚠️★★★ **AccEvent 相当の UIA クライアント**を自前で持つ。
        // ★ `ImeMonitor` も内部で IUIAutomation を作るが、⚠️ それは `GetFocusedElement()` を
        //   呼ぶだけで **テキストパターンを要求しない** ため、Chromium の AXMode が
        //   テキスト系まで上がらない可能性がある。→ ★ ここで明示的に起こす。
        // SAFETY: COM の初期化と生成。★ `ImeMonitor::new()` が既に CoInitializeEx 済みでも
        //   多重呼び出しは S_FALSE を返すだけで問題ない。
        let uia: Option<IUIAutomation> = unsafe {
            let _ = CoInitializeEx(None, COINIT_MULTITHREADED);
            CoCreateInstance(&CUIAutomation, None, CLSCTX_INPROC_SERVER).ok()
        };
        let mut full_poll = 0u32;
        let mut full_hit = 0u32;
        let mut full_rise = 0u32;
        let mut full_prev = false;
        // ★ 「本番の述語は true だが EnumWindows は false」＝ **UIA (または WinEvent) の寄与**。
        let mut uia_only_hit = 0u32;
        while Instant::now() < deadline {
            // SAFETY: 自スレッドのメッセージキューを読むだけ。
            while unsafe { PeekMessageW(&mut msg, None, 0, 0, PM_REMOVE) }.as_bool() {
                unsafe { DispatchMessageW(&msg) };
            }
            // ★ 5 秒ごとに途中経過を出す（★ 打ちながら効いているか分かるように）。
            if Instant::now() >= next_tick {
                let left = deadline.saturating_duration_since(Instant::now()).as_secs();
                writeln!(
                    out,
                    "  [残り {left:>2}s] alive={} imm(ok/open)={}/{} SHOW={}/{} HIDE={}/{} CHANGE={}/{} CONV={}/{}",
                    N_ALIVE.load(Ordering::Relaxed),
                    N_IMM_OK.load(Ordering::Relaxed),
                    N_IMM_OPEN.load(Ordering::Relaxed),
                    N_SHOW[0].load(Ordering::Relaxed),
                    N_SHOW[1].load(Ordering::Relaxed),
                    N_HIDE[0].load(Ordering::Relaxed),
                    N_HIDE[1].load(Ordering::Relaxed),
                    N_CHANGE[0].load(Ordering::Relaxed),
                    N_CHANGE[1].load(Ordering::Relaxed),
                    N_CONV[0].load(Ordering::Relaxed),
                    N_CONV[1].load(Ordering::Relaxed),
                )?;
                // ⚠️★★★ 問い 3 は打ちながら見えたほうがよい (★ 反応が無いなら入力方法を変える)。
                writeln!(
                    out,
                    "            enum(25ms) hit={}/{} 立ち上がり={}  ★ ここが 0 のままなら EnumWindows は効いていない",
                    enum_hit, enum_poll, enum_rise
                )?;
                // ⚠️★★★ **入力が届いているかを打ちながら見せる。**
                // ★ ここが 0 のまま進むと、その 60 秒は 0x8030 の判定に使えない。
                let (sel, val) = typing_evidence();
                writeln!(
                    out,
                    "            ⚠️ 打鍵={}  (参考 textsel={} valuechange={})  ★ 打鍵が伸びなければ入力先が違う",
                    N_KEYS.load(Ordering::Relaxed),
                    sel,
                    val
                )?;
                out.flush()?;
                next_tick += Duration::from_secs(5);
            }
            if Instant::now() >= next_imm {
                poll_imm();
                next_imm += Duration::from_millis(500);
            }
            // ⚠️★★★ 問い 3。★ **本番の `is_ime_candidate_window_visible()` を直接呼ぶ。**
            if Instant::now() >= next_enum {
                let hit = gse_next_lib::input::ime::is_ime_candidate_window_visible();
                enum_poll += 1;
                if hit {
                    enum_hit += 1;
                    dwell_cur_ms += ENUM_PERIOD_MS;
                    dwell_total_ms += ENUM_PERIOD_MS;
                    if !enum_prev {
                        enum_rise += 1;
                    }
                } else {
                    if dwell_cur_ms > dwell_max_ms {
                        dwell_max_ms = dwell_cur_ms;
                    }
                    dwell_cur_ms = 0;
                }
                enum_prev = hit;

                // ★ 本番 (100ms) 相当へ間引く。
                enum_tick += 1;
                if enum_tick.is_multiple_of(ENUM_PROD_DIVISOR) {
                    prod_poll += 1;
                    if hit {
                        prod_hit += 1;
                        if !prod_prev {
                            prod_rise += 1;
                        }
                    }
                    prod_prev = hit;
                }
                // ⚠️★★★ 同じ tick で **本番の完全な述語**も取る (★ 時刻をずらさない)。
                let full = monitor.is_candidate_window_open();
                full_poll += 1;
                if full {
                    full_hit += 1;
                    if !full_prev {
                        full_rise += 1;
                    }
                    if !hit {
                        // ★ EnumWindows が false なのに本番が true → UIA / WinEvent の寄与。
                        uia_only_hit += 1;
                    }
                }
                full_prev = full;

                next_enum += Duration::from_millis(ENUM_PERIOD_MS as u64);
            }
            if Instant::now() >= next_census {
                census_visible_classes(&mut census);
                census_polls += 1;
                next_census += Duration::from_millis(100);
            }
            // ⚠️★★★ UIA プロバイダを定期的に起こす (★ COM 呼び出しなので 250ms 間隔)。
            if Instant::now() >= next_poke {
                if let Some(a) = uia.as_ref() {
                    poke_uia_provider(a);
                }
                next_poke += Duration::from_millis(250);
            }
            std::thread::sleep(Duration::from_millis(5));
        }

        // SAFETY: 張ったスレッドと同じスレッドで外す。
        unsafe {
            let _ = UnhookWinEvent(h_skip);
            let _ = UnhookWinEvent(h_all);
            let _ = UnhookWinEvent(h_alive);
            if !h_keys.is_invalid() {
                let _ = UnhookWindowsHookEx(h_keys);
            }
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
        writeln!(
            out,
            "生存確認 alive (0x800B)  {:>8}   ★ これが 0 なら測定不成立",
            N_ALIVE.load(Ordering::Relaxed)
        )?;
        let (n_sel, n_val) = typing_evidence();
        let n_keys = N_KEYS.load(Ordering::Relaxed);
        // ⚠️★★★ **有効性の閾値。** ★ 日本語を変換しながら 60 秒打てば軽く超える数。
        // ⚠️ 初版は「textsel/valuechange のどちらかが 1 以上」で、
        //   **2 件で「入力は届いている」と誤判定した** (★ 実際に起きた)。
        const MIN_KEYS_FOR_VALID_RUN: u32 = 30;
        writeln!(
            out,
            "⚠️★★★ 入力の証拠  **打鍵={}**  (参考 textsel={} valuechange={})",
            n_keys, n_sel, n_val
        )?;
        if h_keys.is_invalid() {
            writeln!(
                out,
                "   ⚠️★★★ **打鍵フックの設置に失敗した。この回の有効性は判定できない。**"
            )?;
        } else if n_keys < MIN_KEYS_FOR_VALID_RUN {
            writeln!(
                out,
                "   ⚠️★★★ **打鍵が {MIN_KEYS_FOR_VALID_RUN} 未満 = 実質入力していない。この 60 秒は判定に使えない。**"
            )?;
        } else {
            writeln!(
                out,
                "   ★ 入力は確かに行われた。→ **下の CONV_TARGET の 0 は「出なかった」と読んでよい。**"
            )?;
        }
        writeln!(out)?;
        writeln!(
            out,
            "== ⚠️★★★ UIA プロバイダの起こし (★ accevent.exe 相当・0x8030 の前提) =="
        )?;
        writeln!(
            out,
            "  起こし試行={}  窓要素の取得成功={}",
            N_UIA_POKE.load(Ordering::Relaxed),
            N_UIA_ELEMENT_OK.load(Ordering::Relaxed)
        )?;
        writeln!(
            out,
            "  ⚠️ 窓(フレーム)側  Text={} TextEdit={}   ★ ここが 0 なのは**正常**",
            N_UIA_TEXT_OK.load(Ordering::Relaxed),
            N_UIA_TEXTEDIT_OK.load(Ordering::Relaxed)
        )?;
        writeln!(
            out,
            "     (★ ElementFromHandle が返すのはブラウザのフレーム。TextPattern は内側の入力欄に付く)"
        )?;
        writeln!(
            out,
            "  ⚠️★★★ フォーカス要素側  取得={} Text={} TextEdit={}   ★ **判定に使うのはこちら**",
            N_UIA_FOCUS_OK.load(Ordering::Relaxed),
            N_UIA_FOCUS_TEXT_OK.load(Ordering::Relaxed),
            N_UIA_FOCUS_TEXTEDIT_OK.load(Ordering::Relaxed)
        )?;
        writeln!(out)?;
        writeln!(
            out,
            "IMM ポーリング  試行={} 取得成功={} うち日本語モード={}",
            N_IMM_POLL.load(Ordering::Relaxed),
            N_IMM_OK.load(Ordering::Relaxed),
            N_IMM_OPEN.load(Ordering::Relaxed)
        )?;
        writeln!(out)?;
        // ★ 打ち終わった瞬間に候補が開いたままなら、最後の滞在を取りこぼさないよう畳む。
        if dwell_cur_ms > dwell_max_ms {
            dwell_max_ms = dwell_cur_ms;
        }
        writeln!(
            out,
            "== ⚠️★★★ 問い3: EnumWindows 経路 (is_ime_candidate_window_visible) =="
        )?;
        let pct = |hit: u32, poll: u32| -> f64 {
            if poll == 0 {
                0.0
            } else {
                100.0 * f64::from(hit) / f64::from(poll)
            }
        };
        writeln!(
            out,
            "  25ms 実測    ポーリング={:>5} 検出={:>5} ({:>5.1}%) 立ち上がり={:>4}",
            enum_poll,
            enum_hit,
            pct(enum_hit, enum_poll),
            enum_rise
        )?;
        writeln!(
            out,
            "  100ms 本番相当 ポーリング={:>5} 検出={:>5} ({:>5.1}%) 立ち上がり={:>4}  ★ 本番はこちら",
            prod_poll,
            prod_hit,
            pct(prod_hit, prod_poll),
            prod_rise
        )?;
        writeln!(
            out,
            "  候補ウィンドウ滞在  合計={} ms  最長={} ms  (25ms 刻みの近似)",
            dwell_total_ms, dwell_max_ms
        )?;
        // ⚠️★ 滞在は「回数 × 25ms」なので、ループが滑ると**過小**になる。
        // ★ 期待ポーリング数と突き合わせて、滑っていないことを言えるようにする。
        let expected_polls = 60_000 / ENUM_PERIOD_MS;
        writeln!(
            out,
            "  ⚠️ ポーリング実測={} / 期待={}  ★ 一致していれば滑りなし (滞在 ms が信頼できる)",
            enum_poll, expected_polls
        )?;
        writeln!(
            out,
            "  ★ 本番の完全な述語 is_candidate_window_open()  検出={}/{} ({:>5.1}%) 立ち上がり={}",
            full_hit,
            full_poll,
            pct(full_hit, full_poll),
            full_rise
        )?;
        writeln!(
            out,
            "  ⚠️★★★ うち EnumWindows が false だった回数={}  ★ これが UIA 経路の寄与",
            uia_only_hit
        )?;
        writeln!(
            out,
            "  ⚠️ クラス名取得の失敗  診断B={} / 診断A={}  ★ 診断B が 0 でなければ短命な窓を取りこぼしている",
            N_EVENT_CLASS_UNAVAIL.load(Ordering::Relaxed),
            N_CENSUS_CLASS_UNAVAIL.load(Ordering::Relaxed)
        )?;
        writeln!(out)?;
        writeln!(
            out,
            "== 診断A: 可視だったトップレベルウィンドウのクラス (全件・センサス {census_polls} 回) =="
        )?;
        writeln!(
            out,
            "  ★ **出現の少ない順**。⚠️ 一過性のもの (= 変換中だけ出た可能性) が上に来る。"
        )?;
        writeln!(
            out,
            "     {census_polls}/{census_polls} は常時可視 (デスクトップの常駐窓) なので候補 UI ではない。"
        )?;
        if census.is_empty() {
            writeln!(out, "  (なし)")?;
        } else {
            let mut rows: Vec<(&String, &u32)> = census.iter().collect();
            rows.sort_by(|a, b| a.1.cmp(b.1).then(a.0.cmp(b.0)));
            for (class, count) in rows.iter().take(60) {
                let mut mark = String::new();
                if class.contains("Candidate") {
                    mark.push_str(" ★本番の網に掛かる");
                } else if looks_ime_like(class) {
                    mark.push_str(" ☆IMEらしい");
                }
                writeln!(out, "  {count:>5}/{census_polls:<5} {class}{mark}")?;
            }
            if rows.len() > 60 {
                writeln!(out, "  ... 他 {} 件", rows.len() - 60)?;
            }
        }
        writeln!(out)?;
        writeln!(
            out,
            "== ⚠️★★★ 診断B: CREATE / SHOW / HIDE したウィンドウのクラス (イベント駆動) =="
        )?;
        writeln!(
            out,
            "  ★ ポーリングより取りこぼしにくい (100ms 未満で消える窓も届きうる)。★ 出現の多い順。"
        )?;
        writeln!(
            out,
            "  ⚠️ ここに候補 UI が居なければ、候補ウィンドウは**トップレベル窓として存在しない**。"
        )?;
        match event_classes().lock() {
            Ok(map) if map.is_empty() => {
                writeln!(out, "  (なし)")?;
            }
            Ok(map) => {
                #[allow(clippy::type_complexity)]
                let mut rows: Vec<(&(&'static str, String), &u32)> = map.iter().collect();
                rows.sort_by(|a, b| b.1.cmp(a.1).then(a.0.cmp(b.0)));
                for ((tag, class), count) in rows.iter().take(40) {
                    // ⚠️★ 判定は **クラス側だけ**に掛ける。
                    // ★ タグ付き文字列に掛けると、将来 `MINIMIZE` 等を足したときに
                    //   タグの "ime" に当たって全行が誤マークされる。
                    let mark = if class.contains("Candidate") {
                        " ★本番の網に掛かる"
                    } else if looks_ime_like(class) {
                        " ☆IMEらしい"
                    } else {
                        ""
                    };
                    writeln!(out, "  {count:>5}  {tag:<6} {class}{mark}")?;
                }
                if rows.len() > 40 {
                    writeln!(out, "  ... 他 {} 件", rows.len() - 40)?;
                }
            }
            Err(_) => {
                // ⚠️★ 「中毒」と「空」を出し分ける (★ 黙って (なし) にしない)。
                writeln!(
                    out,
                    "  ⚠️ 集計が取得できません (Mutex poisoned) — ★ 測定は不成立"
                )?;
            }
        }
        writeln!(out)?;
        writeln!(
            out,
            "== ⚠️★★★ 実測C: クラス別 cloak と「打鍵からの距離」 (★ false positive の確認) =="
        )?;
        writeln!(
            out,
            "  ★ 近い = 直近打鍵から {NEAR_KEY_MS}ms 以内 / ⚠️ 遠い = それ以上 (= 変換と無関係の疑い)"
        )?;
        writeln!(
            out,
            "  ⚠️★★★ 『遠い』が多いクラスは絞り込みに使えない (無操作中にも cloak する)"
        )?;
        match cloak_stats().lock() {
            Ok(m) if m.is_empty() => {
                writeln!(out, "  (なし)")?;
            }
            Ok(m) => {
                let mut rows: Vec<(&String, &CloakStat)> = m.iter().collect();
                rows.sort_by(|a, b| b.1.cloaks.cmp(&a.1.cloaks).then(a.0.cmp(b.0)));
                writeln!(
                    out,
                    "  {:<28} {:>6} {:>8} {:>6} {:>6}  {:>10}",
                    "クラス", "cloak", "uncloak", "近い", "遠い", "dwell中央"
                )?;
                for (class, st) in rows.iter().take(20) {
                    let med = if st.dwells.is_empty() {
                        0
                    } else {
                        let mut d = st.dwells.clone();
                        d.sort_unstable();
                        d[d.len() / 2]
                    };
                    let far_mark = if st.far_key > st.near_key {
                        " ⚠️遠いが優勢"
                    } else {
                        ""
                    };
                    writeln!(
                        out,
                        "  {:<28} {:>6} {:>8} {:>6} {:>6}  {:>8} ms{}",
                        class, st.cloaks, st.uncloaks, st.near_key, st.far_key, med, far_mark
                    )?;
                }
                writeln!(out)?;
                // ⚠️★★★ 問い 2: `IME` クラスの dwell 分布 (34 = 17 x 2 の内訳)
                if let Some(st) = m.get("IME") {
                    if !st.dwells.is_empty() {
                        let mut d = st.dwells.clone();
                        d.sort_unstable();
                        writeln!(out, "  ★ `IME` クラスの dwell 分布 (n={}):", d.len())?;
                        for p in [0.0_f64, 0.25, 0.5, 0.75, 0.9, 1.0] {
                            let k = ((d.len() - 1) as f64 * p).round() as usize;
                            writeln!(out, "     p{:>3.0} = {:>8} ms", p * 100.0, d[k])?;
                        }
                        writeln!(
                            out,
                            "     ⚠️ 分布が 2 山なら 34 = 17 x 2 の内訳が見える (候補表示 / 別周期)"
                        )?;
                    }
                }
            }
            Err(_) => {
                writeln!(out, "  ⚠️ 集計が取得できません (Mutex poisoned)")?;
            }
        }
        writeln!(out)?;
        writeln!(
            out,
            "== ⚠️★★★ 旧 v0.1.27 の駆動を再現した「ime_shadow」 (★ CLOAK→UNCLOAK) =="
        )?;
        writeln!(
            out,
            "  ★ 当時 ime_dwell_med に何が入っていたかを直接見る。★ 比較対象 (実データの中央値):"
        )?;
        writeln!(out, "     P010=100ms / P011=183ms / P013=838ms")?;
        match legacy_dwells().lock() {
            Ok(v) if v.is_empty() => {
                writeln!(out, "  (なし) ★ cloak/uncloak の対が 1 度も成立しなかった")?;
            }
            Ok(v) => {
                let mut d: Vec<u64> = v.clone();
                d.sort_unstable();
                let pick = |p: f64| -> u64 {
                    let k = ((d.len() - 1) as f64 * p).round() as usize;
                    d[k]
                };
                writeln!(
                    out,
                    "  ★ 再現された行数={}  dwell 中央値={} ms  p90={} ms  最大={} ms",
                    d.len(),
                    pick(0.5),
                    pick(0.9),
                    d[d.len() - 1]
                )?;
                writeln!(
                    out,
                    "  ⚠️ 打鍵={} に対する比  = {:.3} 行/打鍵",
                    n_keys,
                    if n_keys > 0 {
                        d.len() as f64 / f64::from(n_keys)
                    } else {
                        0.0
                    }
                )?;
            }
            Err(_) => {
                writeln!(out, "  ⚠️ 集計が取得できません (Mutex poisoned)")?;
            }
        }
        writeln!(out)?;
        writeln!(
            out,
            "== 実際に飛んだオブジェクトイベント (0x8000-0x8030) =="
        )?;
        let mut any = false;
        for (i, c) in HIST.iter().enumerate() {
            let n = c.load(Ordering::Relaxed);
            if n > 0 {
                any = true;
                let id = HIST_MIN + i as u32;
                let name = match id {
                    0x8000 => "CREATE",
                    0x8001 => "DESTROY",
                    0x8002 => "SHOW",
                    0x8003 => "HIDE",
                    0x8004 => "REORDER",
                    0x8005 => "FOCUS",
                    0x8006 => "SELECTION",
                    0x8008 => "SELECTIONADD",
                    0x800A => "STATECHANGE",
                    0x800B => "LOCATIONCHANGE",
                    0x800C => "NAMECHANGE",
                    0x800E => "VALUECHANGE",
                    0x8014 => "TEXTSELECTIONCHANGED",
                    0x8015 => "CONTENTSCROLLED",
                    0x8017 => "CLOAKED",
                    0x8018 => "UNCLOAKED",
                    0x8027 => "IME_SHOW ★",
                    0x8028 => "IME_HIDE ★",
                    0x8029 => "IME_CHANGE ★",
                    0x8030 => "CONV_TARGET ★",
                    _ => "",
                };
                writeln!(out, "  0x{id:04X} {name:<24} {n:>8}")?;
            }
        }
        if !any {
            writeln!(out, "  (なし)")?;
        }
        writeln!(out)?;
        writeln!(out, "== 読み方 ==")?;
        writeln!(
            out,
            "⚠️★★★ 問い0: alive が 0 → フックが 1 件も配送していない。"
        )?;
        writeln!(
            out,
            "   この場合、下の 0 は「出ない」ではなく「測れていない」である。"
        )?;
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
        writeln!(
            out,
            "⚠️★★★ 問い3: 100ms 本番相当の「立ち上がり」が 1 以上 → EnumWindows は効く (B は成立)。"
        )?;
        writeln!(
            out,
            "   ★ 0 のとき: 上のクラス名センサスに候補 UI らしきものが居れば「網が細い」、"
        )?;
        writeln!(
            out,
            "     居なければ「候補ウィンドウを別プロセスが所有していて EnumWindows に出ない」。"
        )?;
        writeln!(
            out,
            "   ⚠️ 後者なら IME_ACTIVE は取れないと結論し、capabilities は config_gated 据え置き。"
        )?;
        writeln!(out)?;
        writeln!(
            out,
            "== ⚠️ 本ツールの限界 (★ null 結果を主張する前に読む) =="
        )?;
        writeln!(
            out,
            "1. ⚠️ メッセージポンプと EnumWindows が**同じスレッド**を共有している。"
        )?;
        writeln!(
            out,
            "   ★ alive は「フックが生きている」ことしか示さず、**OS 側の欠落は検出できない**。"
        )?;
        writeln!(
            out,
            "2. ⚠️ 診断A は 100ms ポーリングなので、**それより短命な窓は写らない** (診断B は写る)。"
        )?;
        writeln!(
            out,
            "3. ⚠️ クラス名は正規化して出している (WPF/WinForms が実行ファイル名を埋めるため)。"
        )?;
        out.flush()?;
        Ok(())
    }
}
