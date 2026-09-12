use std::sync::atomic::{AtomicBool, AtomicU32, AtomicU64, Ordering};
use std::sync::OnceLock;

use crossbeam_channel::Sender;

use crate::analysis::features::InputEvent;

// ---------------------------------------------------------------------------
// Japanese IME mode VK codes — shared between platforms.
// Windows: captured by WH_KEYBOARD_LL before IME engine.
// macOS: detected via JIS HID keycodes in CGEventTap callback.
// ---------------------------------------------------------------------------
pub const VK_DBE_ALPHANUMERIC: u32 = 0xF0; // 英数: Switch to alphanumeric (A mode)
pub const VK_DBE_KATAKANA: u32 = 0xF1; // カタカナ: Switch to katakana
pub const VK_DBE_HIRAGANA: u32 = 0xF2; // ひらがな: Switch to hiragana (あ mode)
pub const VK_DBE_SBCSCHAR: u32 = 0xF3; // 半角: Single-byte character mode
pub const VK_DBE_DBCSCHAR: u32 = 0xF4; // 全角: Double-byte character mode
pub const VK_KANJI: u32 = 0x19; // 半角/全角: Half-width / full-width toggle

// ---------------------------------------------------------------------------
// Shared atomic state — accessed by both platform implementations and
// the analysis/IME polling threads.
// ---------------------------------------------------------------------------

/// Cross-process IME composition state.
/// Windows: updated by WinEvent hook (EVENT_OBJECT_IME_SHOW/HIDE).
/// macOS: updated by CGEventTap keystroke state machine.
pub static IME_ACTIVE: AtomicBool = AtomicBool::new(false);

/// Returns true if an IME is currently composing text in the foreground application.
///
/// ⚠️ `Acquire` で読む —— `hook-constraints` 共通-2 が **`IME_OPEN` と並べて**
/// store = `Release` / load = `Acquire` と**対で**定めているため。
/// ★ 片側だけ強めても happens-before は成立しないので、対を崩さないこと
/// (⚠️ `is_ime_open()` と同じ理由。★ 規則違反は本ファイル末尾の
/// `ordering_invariant_tests` が機械で止める)。
///
/// ⚠️ x86-64 では `Acquire` load は `Relaxed` と**同一命令** (フェンス無し) だが、
/// ★ aarch64 では `ldar` になる —— **1 命令・フェンス無しなので結論は変わらない**
/// (⚠️ Windows on ARM を入れるときに再検証させないためにここに書いておく)。
pub fn is_ime_active() -> bool {
    IME_ACTIVE.load(Ordering::Acquire)
}

/// Japanese IME input mode: true = あ/カ (Japanese), false = A (alphanumeric/coding).
/// The analysis thread reads this for HMM β-selection (writing vs coding baselines).
pub static IME_OPEN: AtomicBool = AtomicBool::new(false);

/// Returns true if the Japanese IME is currently in Japanese-input mode.
///
/// ⚠️ `Acquire` で読む —— `hook-constraints` 共通-2 が `IME_OPEN` の
/// store = `Release` / load = `Acquire` と**対で**定めているため。
/// ★ 片側だけ強めても happens-before は成立しないので、対を崩さないこと。
pub fn is_ime_open() -> bool {
    IME_OPEN.load(Ordering::Acquire)
}

/// Dirty flag: set by hook callback when a VK_DBE_* / VK_KANJI key is pressed.
/// The IME open polling thread reads this to emit LogEntry::ImeState with a fresh timestamp.
pub static IME_STATE_DIRTY: AtomicBool = AtomicBool::new(false);

/// Unix epoch millisecond timestamp of the most recent keypress.
/// Windows: updated by WH_KEYBOARD_LL callback.
/// macOS: updated by CGEventTap callback.
pub static LAST_KEY_MS: AtomicU64 = AtomicU64::new(0);

/// Returns the Unix epoch millisecond timestamp of the last keypress.
pub fn last_key_ms() -> u64 {
    LAST_KEY_MS.load(Ordering::Relaxed)
}

// ---------------------------------------------------------------------------
// IME Shadow Features (Phase 2b) — ★ 両 OS
// ---------------------------------------------------------------------------
//
// ⚠️★★★ **2026-09-11: `#[cfg(target_os = "windows")]` を外した** (issue 008)。
//   ★ macOS 側も同じ Atomic を駆動して `ime_shadow` を送出する。
//
// ⚠️ **駆動源は OS で違う** (★ 解析時にこの差を知っている必要がある):
//
// | | Windows | macOS |
// |---|---|---|
// | セッション境界 | WinEvent `EVENT_OBJECT_IME_SHOW/HIDE` または DWM cloak/uncloak | ★ **打鍵**の状態機械 (`ime_compose::step`) |
// | `nav` / `abandon` | 打鍵 (`classify_ime_nav_key`) | 打鍵 (`ime_compose::step`) —— **同型** |
//
// → ★ 由来の非対称は `capabilities` (ADR-013) と `meta` 行の OS で判別する
//   (2026-09-11 研究者判断: 行型は両 OS 共通のまま・由来フィールドは足さない)。

/// IME 変換セッションの開始時刻 (epoch ms)。⚠️ `0` = セッション中でない。
///
/// - Windows: WinEvent `IME_SHOW` で store。
/// - macOS: ★ 最初の英数字キーで store (`ime_compose::ComposeState::session_start_ms`)。
pub static IME_COMPOSITION_START_MS: AtomicU64 = AtomicU64::new(0);

/// 計算済み IME 変換滞在時間 (ms)。
///
/// - Windows: WinEvent `IME_HIDE` で store。
/// - macOS: ★ 終端キー (Enter / Escape / その他) で store。
pub static IME_SHADOW_DWELL_MS: AtomicU64 = AtomicU64::new(0);

/// IME 変換中の候補ナビゲーション回数 (矢印キー)。★ 両 OS ともフックコールバックで更新。
pub static IME_CANDIDATE_NAV_COUNT: AtomicU32 = AtomicU32::new(0);

/// ⚠️★★★ IME 変換を **ESC で放棄**したかどうか。★ 両 OS ともフックコールバックで更新。
///
/// ★ `false` = 確定 (Enter / その他キーによる自動確定 / IME モード離脱)。
pub static IME_SHADOW_ABANDON: AtomicBool = AtomicBool::new(false);

// ---------------------------------------------------------------------------
// Windows-specific atomics — ⚠️ 2 つの WinEvent 経路の排他制御
// ---------------------------------------------------------------------------
//
// ⚠️ ここから下 (`IME_SHADOW_READY` の手前まで) は **Windows 限定**である。
//   ★ macOS には「文書化された経路」と「cloak 経路」の二重化そのものが無い
//     (打鍵の状態機械 1 本だけ)。

/// ⚠️★★★ **文書化された IME WinEvent (0x8027-0x8029) が最後に届いた時刻 (epoch ms)。**
///
/// ★ **なぜ要るか** (2026-08-23): この端末の Windows 11 は IME 候補 UI の表示/非表示を
/// `EVENT_OBJECT_IME_*` ではなく **DWM の cloak/uncloak** で行っており、0x8027-29 は
/// 60 秒 × 8 回の実測で **1 件も飛ばない**
/// (`.steering/20260822-ime-active-rewiring/findings-enumwindows-probe.md` §15-16)。
/// → ★ そこで cloak/uncloak を第 2 の駆動源として足したが、
/// ⚠️ **両方飛ぶ端末では `IME_COMPOSITION_START_MS` などに書き手が 2 人できる。**
/// ★ この repo が過去に踏んだ事故 (無関係な窓の cloak で `IME_ACTIVE` が立つ) の型そのもの。
///
/// → ★ **優先順位を固定する**: 文書化された経路が**現に駆動している間**は、
/// cloak 経路は一切手を出さない。壊れる方向ではなく正しい方が勝つ。
///
/// # ⚠️★★★ なぜ「1 度でも飛んだか」の `bool` ではないのか
///
/// ★ 初版は `AtomicBool` の**不可逆ラッチ**だった。⚠️ しかしそれだと
/// **無関係なアプリが 0x8027 を 1 件上げただけで、プロセス寿命の残り全部で
/// cloak 経路が無言で停止する。** ⚠️ その端末で `ime_shadow` が 0 行に戻っても、
/// 解析側は「変換しなかった」と「ラッチで黙った」を**区別できない**
/// (★ この repo が繰り返してきた「計器が黙っていたのに 0 を信号と読む」事故)。
///
/// → ★ **時刻にして recency で判定する** ([`legacy_path_is_driving`])。
/// ★ 本当に legacy が生きている端末ではイベントが来続けるので恒久的に勝ち、
/// ⚠️ 単発の混入なら [`LEGACY_PATH_RECENCY_MS`] 後に cloak 経路が復帰する。
///
/// ⚠️ `0` = **一度も届いていない**。
#[cfg(target_os = "windows")]
pub static LEGACY_IME_EVENT_MS: AtomicU64 = AtomicU64::new(0);

/// ★ 「文書化された経路が現に駆動している」とみなす窓 (ms)。
///
/// ⚠️ 実測の IME 変換間隔 (60 秒で 9〜17 回) より十分長く、
/// ★ かつ「さっき 1 件混ざっただけ」を恒久化しない長さにする。
///
/// # ⚠️ トレードオフ (2026-08-23・cross-review 中)
///
/// ★ `LEGACY_IME_EVENT_MS` は **SHOW / HIDE / CHANGE の 3 つすべて**で更新する。
/// ⚠️ 「`HIDE` 単発でも 60 秒 cloak 経路が止まる」という指摘はそのとおりである。
/// ★ それでも 3 つ全部にしているのは、**どれか 1 つでも飛ぶなら文書化された経路は
/// 生きている**とみなす方が安全だからである
/// (⚠️ SHOW/CHANGE だけに絞ると、`HIDE` しか上げない IME で書き手が 2 人になる)。
/// ★ 損失は**最大 60 秒ぶんの `ime_shadow`** に有界で、切替は `tracing::warn!` に残る。
#[cfg(target_os = "windows")]
pub const LEGACY_PATH_RECENCY_MS: u64 = 60_000;

/// ★ 文書化された経路が**現に駆動しているか**。
///
/// ⚠️ 純関数にしてあるのはテストのため (★ 時刻を注入する)。
#[cfg(target_os = "windows")]
pub fn legacy_path_is_driving(last_legacy_ms: u64, now_ms: u64) -> bool {
    if last_legacy_ms == 0 {
        // ★ 一度も届いていない = cloak 経路に任せる。
        return false;
    }
    now_ms.saturating_sub(last_legacy_ms) <= LEGACY_PATH_RECENCY_MS
}

/// IME Shadow データの emit 準備完了フラグ。★ **両 OS** (2026-09-11・issue 008)。
///
/// - Windows: WinEvent `IME_HIDE` (または cloak resolver) で store(true, Release)。
/// - macOS: ★ 終端キーの検出時に `input/ime_compose.rs::drive` が store(true, Release)。
///
/// IME Monitor スレッドが swap(false, AcqRel) で読み取り、LogEntry::ImeShadow を送出。
///
/// **Ordering 設計**: READY の Release store は、先行する DWELL_MS / NAV_COUNT /
/// ABANDON への Relaxed store をすべて可視にするフェンスとして機能する。
/// Monitor 側の AcqRel swap の Acquire 部分がこの Release と対になり、
/// READY=true が見えた時点で他の shadow atomics も最新値が保証される。
/// 100ms ポーリング間隔のため、高速な連続 IME セッションではデータロスの
/// 可能性があるが、Phase 2b は shadow-only データ収集段階のため許容する。
pub static IME_SHADOW_READY: AtomicBool = AtomicBool::new(false);

// ---------------------------------------------------------------------------
// macOS が駆動する atomics
// ---------------------------------------------------------------------------
//
// ⚠️★★★ **「macOS でしかコンパイルされない」ではなく「macOS でしか書かれない」。**
//   ★ `IME_COMPOSING` は 2026-09-11 に `#[cfg]` を外した (下の doc を参照)。

/// IME inline composition state: true when the user is actively typing
/// romaji that the IME is converting to kana (marked/underlined text).
///
/// ⚠️★★★ **2026-09-11 (issue 008): `#[cfg(target_os = "macos")]` を外した。**
///
/// ★ production で**書くのは macOS だけ**である (`ime_compose::drive`)。
/// ⚠️ それでも両 OS でコンパイルするのは、**Windows の CI でドライバを検証するため**である。
/// ★ このフラグを macOS 限定にしておくと `ime_compose::drive` も macOS 限定になり、
/// ⚠️ 「確定 / 放棄を Atomic へ書き戻す層」が **どちらの OS の CI でも 1 行も走らない**。
/// ★ 実機でしか確かめられないのは「CGEventTap がそのキーを届けるか」だけにしておく。
pub static IME_COMPOSING: AtomicBool = AtomicBool::new(false);

/// ⚠️★★★ **変換セッション「進行中」の矢印キー押下回数** (macOS が駆動)。
///
/// ★ [`IME_CANDIDATE_NAV_COUNT`] と**別に持つ理由**がこの doc の全部である。
///
/// ⚠️ 初版は進行中のカウントも `IME_CANDIDATE_NAV_COUNT` に直接書いていた。
/// → ★ するとセッション開始時のリセットが、**IME Monitor がまだ回収していない
/// 前セッションの要約を上書きする**。⚠️ しかも `IME_SHADOW_DWELL_MS` は据え置かれるので、
/// **「前セッションの dwell」＋「0 の nav」＋「false の abandon」という
/// *存在しない変換* が 1 行出る** —— ★ 行が消えるより悪い (値が偽装される)。
///
/// ⚠️ 具体的な再現: ESC で放棄 → 100ms 以内に次の変換を打ち始める
/// → **`abandon` が `true` から `false` に化ける**。
/// ★ `ime_shadow` は「放棄したか」を残すための行なので、これは目的そのものを壊す。
///
/// → ★ **進行中の値と、回収待ちの要約を、別の置き場に分ける。**
/// ⚠️ セッション開始でリセットするのは**こちらだけ**である。
///
/// ★ 残る競合は「100ms 以内に **2 つの変換が終わる**」場合で、そのときは
/// 後の要約が前を丸ごと置き換える (**1 行の欠落**。値の偽装は起きない)。
/// ⚠️ これは Windows 側と同じ既知の挙動である ([`IME_SHADOW_READY`] の doc)。
pub static IME_COMPOSE_NAV: AtomicU32 = AtomicU32::new(0);

/// Set to true once any JIS IME key has been observed (macOS only).
/// Disables TIS polling to avoid per-app input source interference.
#[cfg(target_os = "macos")]
pub static JIS_KEYBOARD_SEEN: AtomicBool = AtomicBool::new(false);

/// true when the keyboard hook is successfully installed.
/// Read by `get_hook_status` Tauri command to report hook state.
/// Windows: SetWindowsHookExW 成功時に true、フック無効化時に false。
/// macOS: CGEventTap インストール成功時に true。
///
/// ⚠️★★ **これは「設置できた」しか意味しない。**「イベントが届いている」ではない。
/// 2026-08-09 の Windows 実機で、OS が低レベルフックを黙って外したあとも本フラグは
/// `true` のままで、5 分間 0 打のブロックが「正常」として提出された
/// (`windows-verification.md` §5-7)。★ 届いているかどうかは `HOOK_STARVED` を見ること。
pub static HOOK_ACTIVE: AtomicBool = AtomicBool::new(false);

/// ⚠️★★ true = 「設置済みなのにイベントが届いていない」と監視スレッドが判断した状態。
///
/// `input::liveness` の純関数が `HookHealth::Down` を返したときに立つ。
/// ★ `HOOK_ACTIVE` とは**別概念**なので同じフラグに混ぜない
/// (混ぜるとフックスレッドと監視スレッドが同じ Atomic を奪い合う)。
/// トレイはこの 2 つの AND を「計測中」として表示する。
pub static HOOK_STARVED: AtomicBool = AtomicBool::new(false);

/// ⚠️★★ **研究者向けの「生の」判定** (2026-08-28)。
///
/// ★ 上の `HOOK_STARVED` は 2026-08-28 から「**被験者に見せるか**」を持つ旗になった
/// (O1 ではトレイ警告を 30 分まで遅らせる —— `liveness::participant_visible_starved`)。
/// ⚠️ そのままだと `get_diagnostics` の `hook_starved` が **O1 のあいだだけ意味を変える**。
/// ★ 2026-08-09 の判断 **D-6** は逐語で
/// 「`hook_starved` / `callback_count` は `get_diagnostics`（研究者向け）に出し、
/// 被験者側はトレイ表示までに留める」と決めており、
/// → ★ **研究者の診断は「届いていない」を指し続けなければならない。**
///
/// ★ したがってこちらは **常に `liveness::health() == Down` と同義**である
/// (⚠️ モードに依らない)。★ 被験者の画面・トレイはこちらを見ない。
pub static HOOK_NOT_DELIVERING: AtomicBool = AtomicBool::new(false);

/// キーボードフックのコールバックが呼ばれた回数（診断 + 生存監視）。
///
/// 0 のままなら「フックは作成されたがイベントが届いていない」ことを示す。
/// ★ 2026-08-09 以降は Windows でも加算する (`input::liveness` の生存判定が読む)。
/// ⚠️ ★ `LAST_KEY_MS` を生存判定に使わない理由: あちらは**再設置時に 0 へリセットされる**ので
/// 「沈黙の長さ」の基準にできない (memory `macos-tap-idle-away-probe-bug` と同型の罠)。
pub static CALLBACK_COUNT: AtomicU64 = AtomicU64::new(0);

/// ⚠️★★ 分析スレッドへ渡せずに**捨てた**打鍵イベントの累計。
///
/// ★ `CALLBACK_COUNT` は「OS がフックを呼んだ回数」であって
/// **「記録できた回数」ではない**。channel が詰まれば呼ばれても記録は失われる
/// (security-checker MEDIUM: それを数えないと、本機能が目的とする
/// 「打っているのに記録されていない」の一部を素通りさせる)。
///
/// ⚠️ ★ コールバック内でログを書けないので (`hook-constraints` 共通-1: ログ禁止)、
/// **カウンタだけ上げて、監視スレッドが統計的に 1 回だけ報告する** (共通-3 のパターン)。
pub static EVENTS_DROPPED: AtomicU64 = AtomicU64::new(0);

/// macOS: CGEventTap 作成の連続失敗回数（診断用）。
/// TCC 権限が付与されていない、またはコード署名の問題を示す。
#[cfg(target_os = "macos")]
pub static CONSECUTIVE_TAP_FAILURES: AtomicU32 = AtomicU32::new(0);

/// macOS: Input Monitoring 失敗時に Accessibility 権限へフォールバックしたかどうか。
/// ad-hoc 署名では Input Monitoring の TCC CDHash 認証が不安定なため、
/// 10回連続失敗後に CGEventTapOptions::Default（Accessibility 権限）へ切り替える。
#[cfg(target_os = "macos")]
pub static USING_ACCESSIBILITY_FALLBACK: AtomicBool = AtomicBool::new(false);

// ---------------------------------------------------------------------------
// Lock-free channels — shared between platforms
// ---------------------------------------------------------------------------

/// Lock-free sender for keystroke events → analysis thread.
pub static EVENT_SENDER: OnceLock<Sender<InputEvent>> = OnceLock::new();

/// Lock-free wake signal sender for the IME open polling thread.
pub static POLL_WAKE_TX: OnceLock<Sender<()>> = OnceLock::new();

/// Store the polling thread's wake channel sender.
/// Must be called before `init_hook` so the sender is ready when the hook fires.
pub fn set_poll_wake_sender(tx: Sender<()>) {
    let _ = POLL_WAKE_TX.set(tx);
}

/// ⚠️★★★ **cloak/uncloak イベントを resolver スレッドへ渡すチャネル。**
///
/// ★ **なぜチャネルなのか**: 判定にはウィンドウクラス名が要るが、
/// ⚠️ `hook-constraints` Win-1 により **WinEvent コールバック内で `GetClassNameW` は呼べない**
/// (Atomic 操作と `try_send` のみ)。→ ★ **HWND を送り、別スレッドで解決する。**
///
/// ⚠️ `HWND` は `Send` ではないので **`isize` で運ぶ** (★ `ThreadSafeHook` と同じ発想)。
/// ⚠️★ resolver は hwnd を**クラス解決と cloak 状態の問い合わせにしか使わず、
/// 保存も送出もしない** (`data-privacy`: ウィンドウタイトルも PID も取らない)。
#[cfg(target_os = "windows")]
pub static CLOAK_EVENT_TX: OnceLock<Sender<CloakEvent>> = OnceLock::new();

/// ★ cloak/uncloak の生イベント。⚠️ **窓の識別子以外は何も運ばない** (content-free)。
#[cfg(target_os = "windows")]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct CloakEvent {
    /// ⚠️ `HWND` の生値。★ resolver がクラス解決に使うだけで、ログにも NDJSON にも出ない。
    pub hwnd: isize,
    /// ★ 届いた辺 (`EVENT_OBJECT_CLOAKED` なら true)。
    ///
    /// ⚠️★ **これは参考でしかない。** 配送は `WINEVENT_OUTOFCONTEXT` の非同期配送なので、
    /// resolver に届いた時点の実状態と食い違いうる。
    /// → ★ resolver は `DwmGetWindowAttribute(DWMWA_CLOAKED)` で **OS に聞き直す**。
    pub cloaked: bool,
}

#[cfg(all(test, target_os = "windows"))]
mod legacy_path_tests {
    use super::{legacy_path_is_driving, LEGACY_PATH_RECENCY_MS};

    #[test]
    fn never_seen_means_cloak_path_drives() {
        assert!(
            !legacy_path_is_driving(0, 1_000_000),
            "★ 0 = 一度も届いていない → cloak 経路に任せる"
        );
    }

    #[test]
    fn recent_legacy_event_wins() {
        let now = 1_000_000;
        assert!(legacy_path_is_driving(now, now));
        assert!(legacy_path_is_driving(now - LEGACY_PATH_RECENCY_MS, now));
    }

    /// ⚠️★★★ **単発の混入で cloak 経路が永久に黙らないこと。**
    ///
    /// ★ 初版は不可逆ラッチで、無関係なアプリの 0x8027 が 1 件飛べば
    /// プロセス寿命の残り全部で cloak 経路が停止していた。
    /// ⚠️ その端末で `ime_shadow` が 0 行に戻っても
    /// 「変換しなかった」と「黙った」を解析側が区別できない。
    #[test]
    fn stale_legacy_event_releases_the_cloak_path() {
        let now = 1_000_000;
        assert!(
            !legacy_path_is_driving(now - LEGACY_PATH_RECENCY_MS - 1, now),
            "★ 窓を過ぎたら cloak 経路が復帰しなければならない"
        );
    }

    /// ⚠️ 時計が巻き戻っても panic しないこと (`saturating_sub`)。
    #[test]
    fn clock_going_backwards_is_not_a_panic() {
        assert!(legacy_path_is_driving(2_000_000, 1_000_000));
    }
}

/// resolver スレッドの受信端を作り、送信端を登録する。
///
/// ⚠️ **`init_hook` より前に呼ぶこと** (★ フックが飛び始めたときに sender が居るように)。
#[cfg(target_os = "windows")]
pub fn set_cloak_event_sender(tx: Sender<CloakEvent>) {
    let _ = CLOAK_EVENT_TX.set(tx);
}

// ---------------------------------------------------------------------------
// Platform-specific hook implementations
// ---------------------------------------------------------------------------

#[cfg(target_os = "windows")]
#[path = "hook_windows.rs"]
mod hook_windows;

#[cfg(target_os = "macos")]
#[path = "hook_macos.rs"]
mod hook_macos;

/// フックが既に起動しているか。⚠️★★★ **2 本目を立てさせないための門**である。
static HOOK_STARTED: std::sync::atomic::AtomicBool = std::sync::atomic::AtomicBool::new(false);

/// Install the platform-specific keyboard hook and begin delivering InputEvents to `sender`.
/// Spawns a dedicated background thread; returns immediately.
///
/// ⚠️★★★ **2 回目以降は何もしない。** ★ 2026-09-06 に CI (self-hosted mac) が
/// **SIGSEGV** で落ちて分かった: `hook_macos::start()` は無条件に `thread::spawn` するので、
/// 2 回呼ぶと **hook スレッドが 2 本**立つ。
/// ⚠️ すると `TAP_PORT` の安全性の根拠 —— 「書き込み (本体) と読み出し (callback) は
/// **同一 hook スレッド**上で起き、**時間的に排他**」(`hook_macos.rs` の doc) —— が**破れる**。
/// ★ 2 本目が `TAP_PORT` を上書きし、1 本目が `run_current` を抜けて null クリアする、
/// といった順序が起きうるので、⚠️ **解放済みの port を触りうる** (UAF)。
///
/// ★ 本番の呼び出しは `lib.rs` の 1 か所だけ（★ grep で確認）なので実害は無かったが、
/// ⚠️ **不変条件が「呼び出し規約」でしか守られていなかった**。→ ★ 門にした。
///
/// 戻り値: 実際に起動したら `true`。⚠️ 既に起動済みなら `false`（★ 何もしていない）。
pub fn init_hook(sender: Sender<InputEvent>) -> bool {
    use std::sync::atomic::Ordering;
    if HOOK_STARTED
        .compare_exchange(false, true, Ordering::AcqRel, Ordering::Acquire)
        .is_err()
    {
        // ⚠️ 黙って無視しない（★ 「呼んだのに動いていない」を見えるようにする）。
        tracing::warn!(
            "init_hook called twice; the second call does nothing (hook already running)"
        );
        return false;
    }
    let _ = EVENT_SENDER.set(sender);

    #[cfg(target_os = "windows")]
    hook_windows::start();

    #[cfg(target_os = "macos")]
    hook_macos::start();

    true
}

/// フックの再設置を要求する (silent death からの復帰・`decisions.md` D-3)。
///
/// ⚠️★★ **新しい復帰経路は書かない。** 既存の「メッセージループ / run loop を抜けて
/// ループ先頭で再設置する」経路 (Windows: `Keyboard hook message loop exited` /
/// macOS: `CGEventTap CFRunLoop exited`) を**起こすだけ**である。
/// ★ 経路を増やすと、どれか 1 つが静かに壊れる。
///
/// ⚠️★★★ **2026-09-05 に macOS を実装した。** ★ それまで macOS は**定数 `false`** で、
/// 「タップ失効の再作成を自前で持つので不要」と書いてあったが、⚠️ **その自前の再作成は
/// OS が `TapDisabled*` を届けたときにしか動かない**。
/// ★ 2026-09-04 の 8 時間実測で、打鍵していた 31 分のうち `starve_window` 8 窓 (合計 114 s)
/// ＋ 120 s 級の欠測ブロック 2 回が出たのに **1 度も再設置されなかった**
/// (`experiments/20260903-o1-runtime-cost/notes.md`)。
///
/// 戻り値: 要求を送れたら `true`。⚠️ フック起動前は `false` (★ 嘘をつかない)。
pub fn request_reinstall() -> bool {
    #[cfg(target_os = "windows")]
    {
        hook_windows::request_reinstall()
    }
    #[cfg(target_os = "macos")]
    {
        hook_macos::request_reinstall()
    }
    #[cfg(not(any(target_os = "windows", target_os = "macos")))]
    {
        false
    }
}

/// OS のフックが「有効」と答えるか。★ **診断専用** (⚠️ 判定に使わない)。
///
/// ⚠️★★ 目的は「**飢えの機序を 1 回で決着させる**」ことである。★ 2026-09-04 の実測では
/// 120 s 級の欠測が「tap が disable されていた」のか「イベントが来なかっただけ」なのかを
/// **区別する記録が無く**、直す対象の機序が決められなかった。
///
/// 戻り値: `None` = その OS では答えられない / フックがまだ無い。
pub fn hook_reports_enabled() -> Option<bool> {
    #[cfg(target_os = "macos")]
    {
        hook_macos::tap_is_enabled()
    }
    #[cfg(not(target_os = "macos"))]
    {
        // ⚠️ Windows の `WH_KEYBOARD_LL` には「有効か」を聞く API が無い
        //   (★ `UnhookWindowsHookEx` するまで有効という以上のことは分からない)。
        //   → ★ **答えられないことを `None` で表す** (⚠️ `Some(true)` と偽らない)。
        None
    }
}

/// フック監視スレッド (層 2) が自力で復帰させた累計回数。★ **診断専用**。
///
/// ⚠️ macOS 以外は層 2 を持たないので常に 0 (★ 「0 回起きた」ではなく「機構が無い」)。
pub fn watchdog_recoveries() -> u32 {
    #[cfg(target_os = "macos")]
    {
        hook_macos::watchdog_reenables()
    }
    #[cfg(not(target_os = "macos"))]
    {
        0
    }
}

// ---------------------------------------------------------------------------
// 共通-2 (Ordering) の回帰テスト
// ---------------------------------------------------------------------------

#[cfg(test)]
mod ordering_invariant_tests {
    use std::collections::BTreeSet;
    use std::path::{Path, PathBuf};

    /// `src/` 配下の `*.rs` を再帰で集める。
    ///
    /// ⚠️★★★ **ハードコードの列挙にしない** (code-reviewer / security-checker MEDIUM)。
    /// ★ 列挙だと**新しいファイルが黙って検査の外に出る** —— それは本テストが
    /// 批判している「実測はその時点の写像にすぎない」と**同じ弱点を 1 段上に残す**だけである。
    fn collect_sources(dir: &Path, out: &mut Vec<PathBuf>) {
        let Ok(entries) = std::fs::read_dir(dir) else {
            return;
        };
        for e in entries.flatten() {
            let p = e.path();
            if p.is_dir() {
                collect_sources(&p, out);
            } else if p.extension().is_some_and(|x| x == "rs") {
                out.push(p);
            }
        }
    }

    /// ⚠️★★★ `IME_OPEN` / `IME_ACTIVE` に弱い Ordering が混ざったら落とす。
    ///
    /// # ★ なぜ型で表せないのか
    ///
    /// ★ `hook-constraints` 共通-2 は「**この 2 つの static だけ** store = `Release` /
    /// load = `Acquire`」と定めている (⚠️ `LAST_KEY_MS` / `CONSECUTIVE_TAP_FAILURES` は
    /// `Relaxed` で**正しい**)。→ 規則は「**どの変数か**」に依存するので、
    /// `AtomicBool` という型は両者を区別できない。
    /// ⚠️ したがって [`crate::capabilities`] と同じ様式で **ソースの実物**を検査する。
    ///
    /// # ⚠️★★★ なぜ「実測して 0 件」では足りないのか
    ///
    /// ★ 2026-09-12 に mac 側 (PR #190) が `IME_OPEN` を閉じ、⚠️ **同じ日に
    /// `IME_ACTIVE` が 7 箇所 `Relaxed` のまま**であることが判明した。
    /// → ★ 実測は**その時点の写像**にすぎず、**次に書く人を止めない**。
    ///
    /// # ⚠️ なぜ **`#[cfg]` を付けないのか**
    ///
    /// ★ 本テストは**ソースを文字列として読む**ので、`hook_windows.rs` が
    /// 1 行もコンパイルされない macOS でも**中身を検査できる**。
    /// ⚠️ 逆に `#[cfg]` を付けると**相手側 OS の CI が素通り**し、
    /// 今回まさに起きた「片 OS でしか見ていない」状態に戻る。
    ///
    /// # ★ 針の設計 (⚠️ レビューで塞いだ 3 つの穴)
    ///
    /// | 穴 | ⚠️ 何が素通りしたか | ★ 対処 |
    /// |---|---|---|
    /// | 針が `Ordering::Relaxed` 固定 | `use ...Ordering::Relaxed;` + **裸の `Relaxed`**。★ `lib.rs` の `emit_ime_shadow` が**実際にこの書き方**をしている | ★ 針を **`Relaxed`** に緩める (⚠️ 名前との AND なので誤検出は増えない) |
    /// | 1 行 `contains` | ⚠️ rustfmt が引数を折ると**すり抜ける** (★ 同ファイルに 7 行に割れた `store` が実在) | ★ **`;` 区切りのステートメント単位**で見る |
    /// | ファイルのハードコード列挙 | ⚠️ 新規ファイルが**黙って外に出る** | ★ `read_dir` で `src/` を再帰走査 |
    ///
    /// # ★ 既知の限界
    ///
    /// - ⚠️ **行コメントは落とす** (`//` 以降)。★ 規則を説明する文章が自分に引っかかるため。
    ///   ⚠️ 副作用として `"http://..."` のような**文字列中の `//`** も切るが、
    ///   ★ そこに保護対象の名前と `Relaxed` が同居することは無い。
    /// - ★ 見るのは **名前の直後の `( .. )` の中だけ**なので、
    ///   ⚠️ 名前を**経由しない**書き方 (一度ローカル変数に束ねてから `load` する等) は拾えない。
    ///   ★ 現在そのような書き方は repo に無い (⚠️ 増やさないこと)。
    #[test]
    fn guarded_atomics_never_use_weak_ordering() {
        // ★ 針を `concat!` で割る —— ⚠️ **本ファイル自身も走査対象**なので、
        //   予防的に自己ヒットの目を潰しておく (★ 将来 1 行の述語に書き直されても効く)。
        let names = [concat!("IME_", "OPEN"), concat!("IME_", "ACTIVE")];
        let weak = concat!("Rela", "xed");

        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("src");
        let mut files = Vec::new();
        collect_sources(&root, &mut files);

        // ⚠️★★★ **走査が空振りしていないことを先に確かめる。**
        //   ★ 0 件でも `assert!(violations.is_empty())` は緑になる —— それは
        //   **「検査したが無かった」ではなく「検査していない」**であり、最も危険な緑である。
        assert!(
            files.len() >= 20,
            "ソース走査が空振りしている (found {} files under {}). \
             ★ 検査していないのに緑になる状態なので落とす。",
            files.len(),
            root.display()
        );

        let mut seen_names: BTreeSet<&str> = BTreeSet::new();
        let mut violations = Vec::new();

        for path in &files {
            let Ok(src) = std::fs::read_to_string(path) else {
                continue;
            };
            let rel = path
                .strip_prefix(&root)
                .unwrap_or(path)
                .to_string_lossy()
                .replace(std::path::MAIN_SEPARATOR, "/");

            // ★ 行コメントを落としてから 1 本につなぐ。
            //   ⚠️ これで rustfmt が折った複数行の呼び出しも 1 本の文字列に戻る。
            let stripped: String = src
                .lines()
                .map(|l| match l.find("//") {
                    Some(i) => &l[..i],
                    None => l,
                })
                .collect::<Vec<_>>()
                .join(" ");

            // ★ **名前のすぐ後ろの呼び出し式 `( .. )` の中だけ**を見る。
            //   ⚠️ 当初は `;` でステートメントに割ったが、**`if cond { .. }` のブロック本体まで
            //     1 断片に入ってしまい**、正しい `Acquire` の行が無関係な
            //     `NAV_COUNT.fetch_add(.., Relaxed)` と同居して**過検出した** (実測 2 件)。
            //   ★ 常時赤の検査は**いずれ消される**ので、引数リストまで絞る。
            for name in names {
                let mut from = 0usize;
                while let Some(rel_i) = stripped[from..].find(name) {
                    let i = from + rel_i;
                    from = i + name.len();
                    seen_names.insert(name);

                    // ★ 直後の `(` から対応する `)` までを引数リストとみなす。
                    let Some(open_rel) = stripped[from..].find('(') else {
                        break;
                    };
                    let open = from + open_rel;
                    let mut depth = 0usize;
                    let mut close = None;
                    for (k, c) in stripped[open..].char_indices() {
                        match c {
                            '(' => depth += 1,
                            ')' => {
                                depth -= 1;
                                if depth == 0 {
                                    close = Some(open + k);
                                    break;
                                }
                            }
                            _ => {}
                        }
                    }
                    let Some(close) = close else { break };
                    let args = &stripped[open + 1..close];
                    if args.contains(weak) {
                        violations.push(format!(
                            "{rel} | {name}(…{}…)",
                            args.split_whitespace().collect::<Vec<_>>().join(" ")
                        ));
                    }
                }
            }
        }

        // ⚠️ 名前を 1 つも見つけられないなら、走査経路か針が壊れている (★ これも「検査していない」)。
        for n in names {
            assert!(
                seen_names.contains(n),
                "{n} をソースから 1 件も見つけられなかった。★ 走査経路か針が壊れている。"
            );
        }

        assert!(
            violations.is_empty(),
            "hook-constraints 共通-2 違反: 保護対象の static に弱い Ordering が使われている。\n\
             ★ store は Release / load は Acquire で **対**にすること \
             (⚠️ 片側だけ強めても happens-before は成立しない)。\n\
             ⚠️ 近似値で十分な LAST_KEY_MS 等とは別扱いである。\n{}",
            violations.join("\n")
        );
    }
}
